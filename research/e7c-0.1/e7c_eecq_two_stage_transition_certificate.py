"""Check events emitted at actual charge/append sites in both Python paths.

This checks concrete execution transcripts. Lean proves the corresponding
conditional Trace relation; this Python checker is not a proof of Python code.
"""

from __future__ import annotations

from e7c_eecq_two_stage_exact_codec import (
    CodecAdmission, LeanEvent, budget, events, observation, policy, rows,
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
        for item in transcript:
            if type(item) is not dict or item.get("action") not in ("charge", "append"):
                raise TransitionAdmission("invalid transition action")
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
