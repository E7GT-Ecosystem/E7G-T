"""Check events emitted at actual charge/append sites in both Python paths.

This checks concrete execution transcripts. Lean proves the corresponding
conditional Trace relation; this Python checker is not a proof of Python code.
"""

from __future__ import annotations

from e7c_eecq_two_stage_exact_codec import (
    CodecAdmission, LeanEvent, budget, events, observation, policy, rows,
    staged_spec,
)


class TransitionAdmission(ValueError):
    pass


def expected_events(source):
    encoded = rows(source)
    first, second = policy(source)
    result = [LeanEvent("first")]
    if first != "ready":
        return tuple(result)
    retained = []
    for index, current in enumerate(encoded):
        result.append(LeanEvent("first", index, current, current.left.ab))
        if not current.left.ab:
            retained.append(current)
    result.append(LeanEvent("second"))
    if second == "ready":
        result.extend(LeanEvent("second", index, current, current.right.bc)
                      for index, current in enumerate(retained))
    return tuple(result)


def check(source, result, transcript):
    """Check every emitted step against the selected transition constructors."""
    try:
        encoded = rows(source)
        projected = observation(source, result)
        # A transcript and its terminal claim can be internally consistent
        # while falsely asserting that stage one finished. Require the entire
        # typed observation to match the separately traversed rule, including
        # the cursor, three exact portions, and second-attempt start bit.
        if projected != staged_spec(source):
            raise TransitionAdmission("observation does not refine staged rule")
        ledger = events(result, encoded)
        full = expected_events(source)
        step_bound, ledger_bound = budget(source)
        if type(transcript) is not list:
            raise TransitionAdmission("transition transcript must be a list")
        steps = 0
        appended = 0
        started = False
        pending = None
        failed_append = False
        terminal_seen = False
        for item in transcript:
            if type(item) is not dict or item.get("action") not in (
                    "charge", "append", "terminal"):
                raise TransitionAdmission("invalid transition action")
            if terminal_seen:
                raise TransitionAdmission("transition after terminal outcome")
            if item["action"] == "terminal":
                if (item.get("stage") != (
                        "second" if projected["firstExcluded"] is not None else "first")
                        or item.get("row_index", "missing") is not None
                        or item.get("steps") != steps
                        or item.get("ledger_entries") != appended
                        or item.get("second_started") is not started
                        or item.get("event", "missing") is not None
                        or item.get("terminal_outcome") != result["terminal_outcome"]
                        or item.get("progress") != result["resource_progress"]):
                    raise TransitionAdmission("terminal step or progress differs from result")
                terminal_seen = True
                continue
            if failed_append:
                raise TransitionAdmission("transition after failed append")
            if item["action"] == "charge":
                if pending is not None or steps >= step_bound or appended >= len(full):
                    raise TransitionAdmission("step charged outside active cursor or bound")
                pending = full[appended]
                steps += 1
                if pending.stage == "second" and pending.index is None:
                    started = True
            else:
                if (pending is None or appended >= ledger_bound or appended >= len(ledger)
                        or ledger[appended] != pending or item.get("event") !=
                        result["ordered_ledger"][appended]):
                    raise TransitionAdmission("append differs from charged event or full ledger")
                appended += 1
                pending = None
            if (item.get("stage") != (pending.stage if pending is not None
                                      else ledger[appended - 1].stage)
                    or item.get("row_index") != (pending.index if pending is not None
                                                 else ledger[appended - 1].index)
                    or item.get("steps") != steps or item.get("ledger_entries") != appended
                    or (item["action"] == "charge" and item.get("event") is not None)
                    or (item["stage"] == "second" and
                        (type(item.get("second_started")) is not bool or
                         item["second_started"] != started))
                    or (item["stage"] == "first" and "second_started" in item)):
                raise TransitionAdmission("incorrect transition state or event cursor")
            if pending is not None and appended == ledger_bound:
                failed_append = True
        if steps != projected["completedSteps"] or appended != len(ledger):
            raise TransitionAdmission("transcript does not account for all progress")
        if not terminal_seen:
            raise TransitionAdmission("missing terminal transition")
        if started != projected["secondStarted"]:
            raise TransitionAdmission("second attempt charge not preserved")
        if pending is not None and not failed_append:
            raise TransitionAdmission("charged step lacks required append")
        if projected["terminal"] == "resource_limit":
            if not (failed_append or steps == step_bound and appended < len(full)):
                raise TransitionAdmission("resource stop without exhausted bound")
        elif failed_append or appended != len(full):
            raise TransitionAdmission("nonresource terminal before all selected events")
        return projected
    except (CodecAdmission, KeyError, IndexError, TypeError) as exc:
        raise TransitionAdmission("invalid external transition certificate") from exc


def certify_both(source):
    """Build a replayable *instance* certificate for both actual Python paths.

    This executes source and IR separately and preserves each complete
    transcript. It is not a universal proof about Python control flow or a
    Lean proof-term checker: those links remain explicit obligations.
    """
    from e7c_b1_canonical import digest
    from e7c_eecq_two_stage_b1 import evaluate
    from e7_ir_eecq_two_stage_b1 import compare_replay, execute, lower

    source_trace, ir_trace = [], []
    source_result = evaluate(source, _transition_sink=source_trace.append)
    package = lower(source)
    ir_result = execute(package, _transition_sink=ir_trace.append)
    replayed = compare_replay(package)["ir_result"]
    source_projection = check(source, source_result, source_trace)
    ir_projection = check(source, ir_result, ir_trace)
    if (source_projection != ir_projection or source_trace != ir_trace
            or source_result["witness"]["claim"] != ir_result
            or replayed != ir_result):
        raise TransitionAdmission("source, IR and independent replay disagree")
    return {"source_digest": digest(source), "source": source,
            "ir_package": package, "source_result": source_result,
            "ir_result": ir_result, "source_transcript": source_trace,
            "ir_transcript": ir_trace, "exact_observation": source_projection}
