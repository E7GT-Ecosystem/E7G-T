"""Kernel-check live reported-run certificates and reject forged reports.

Invoke after the pinned Lean package build. Successful checks establish the
reported literals' mathematical relation, not CPython origin or all-input host
adequacy. No generated file imports an arbitrary user-supplied Lean program.
"""
import copy
import json
import subprocess
import tempfile
from pathlib import Path

from e7c_joint_serializer_observer import certificate_text, freeze_manifest, observe
from test_e7c_joint_serializer_observer import fixture_values


def main():
    root = Path(__file__).resolve().parent
    package = root / "proof-packages/lean-core"
    manifest = freeze_manifest()
    packets = [observe(value, manifest) for value in fixture_values()]
    if any(packet["tag"] != "observed_normal" for packet in packets):
        raise RuntimeError("live observation did not return normally in the selected host domain")
    with tempfile.TemporaryDirectory(prefix="e7c-observed-certificates-") as directory:
        directory = Path(directory)
        positive = directory / "Live.lean"
        positive.write_text(certificate_text(packets))
        result = subprocess.run(["lake", "env", "lean", str(positive)], cwd=package,
                                capture_output=True, text=True, timeout=120)
        if result.returncode:
            raise RuntimeError("live mathematical certificate failed: " + result.stdout + result.stderr)
        forged = []
        wrong_pair = copy.deepcopy(packets[1])
        wrong_pair["output"][0]["coefficient"] = {"numerator": 2, "denominator": 4}
        forged.append(("UnreducedOutput", wrong_pair))
        wrong_tag = copy.deepcopy(packets[1])
        wrong_tag["output"][0]["atoms"][0]["tag"] = ""
        forged.append(("NullChanged", wrong_tag))
        missing_event = copy.deepcopy(packets[1])
        del missing_event["events"][2]
        forged.append(("MissingFrame", missing_event))
        reversed_rows = copy.deepcopy(packets[1])
        reversed_rows["output"].reverse()
        forged.append(("ReorderedRows", reversed_rows))
        for name, packet in forged:
            path = directory / (name + ".lean")
            path.write_text(certificate_text([packet]))
            result = subprocess.run(["lake", "env", "lean", str(path)], cwd=package,
                                    capture_output=True, text=True, timeout=120)
            if result.returncode != 1 or "error:" not in result.stdout or "rfl" not in result.stdout:
                raise RuntimeError("forgery was accepted or Lean could not check it: " + name +
                                   "\n" + result.stdout + result.stderr)
        report = {"tag": "checked_reported_observations", "runtime_manifest": manifest,
                  "normal_captures_checked": len(packets), "forged_captures_rejected": len(forged),
                  "all_input_cpython_adequacy": "unproved",
                  "capture_origin_and_native_denotation": "trusted, not kernel-proved"}
        print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
