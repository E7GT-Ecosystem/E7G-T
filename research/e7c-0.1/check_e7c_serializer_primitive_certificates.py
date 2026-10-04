"""Kernel-check fresh native primitive receipts and adversarial modifications."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile

from e7c_joint_serializer_primitive_capture import capture
from e7c_joint_serializer_primitive_certificates import certificate_text
from test_e7c_joint_serializer_primitive_capture import fixture_values


def main():
    package = Path(__file__).resolve().parent / "proof-packages/lean-core"
    packets = [capture(value) for value in fixture_values()]
    with tempfile.TemporaryDirectory(prefix="e7c-native-primitives-") as directory:
        directory = Path(directory)

        def check(name, observations):
            path = directory / (name + ".lean")
            path.write_text(certificate_text(observations))
            return subprocess.run(["lake", "env", "lean", str(path)], cwd=package,
                                  capture_output=True, text=True, timeout=120)

        good = check("LiveNativePrimitives", packets)
        if good.returncode:
            raise RuntimeError("fresh native primitive receipts failed: " + good.stdout + good.stderr)
        forged = []
        changed = copy.deepcopy(packets[1])
        changed["output"][0]["coefficient"] = {"numerator": 2, "denominator": 4}
        forged.append(("RawFractionChanged", changed))
        changed = copy.deepcopy(packets[1])
        next(e for e in changed["events"] if e["site"] == "_row.numerator")["payload"] = 99
        forged.append(("PrimitiveReadChanged", changed))
        changed = copy.deepcopy(packets[1])
        next(e for e in changed["events"] if e["site"] == "_graph.tag")["payload"] = ""
        forged.append(("NullReadChanged", changed))
        changed = copy.deepcopy(packets[1])
        del changed["events"][1]
        forged.append(("MissingActualRead", changed))
        changed = copy.deepcopy(packets[1])
        changed["events"].append(copy.deepcopy(changed["events"][-1]))
        forged.append(("RepeatedReturn", changed))
        changed = copy.deepcopy(packets[1])
        changed["copies"][0]["output_refs"][0] += 100
        forged.append(("ReboundCopyCell", changed))
        changed = copy.deepcopy(packets[1])
        del changed["copies"][0]
        forged.append(("MissingCopyOperation", changed))
        changed = copy.deepcopy(packets[1])
        changed["output"].reverse()
        forged.append(("NativeRowsReordered", changed))
        for name, observation in forged:
            result = check(name, [observation])
            if result.returncode != 1 or "error:" not in result.stdout or "rfl" not in result.stdout:
                raise RuntimeError("forged receipt accepted or verification failed: " + name +
                                   "\n" + result.stdout + result.stderr)
        print(json.dumps({"fresh_native_serializer_captures": len(packets),
                          "primitive_events": sum(len(p["events"]) for p in packets),
                          "copy_operations": sum(len(p["copies"]) for p in packets),
                          "kernel_rejections": len(forged),
                          "native_dispatch_capture_and_denotation": "trusted/open",
                          "all_input_cpython_adequacy": "unproved"}))


if __name__ == "__main__":
    main()
