"""Fresh operation-local raw admission receipts and kernel negative controls."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile

from e7c_joint_admission_capture import capture
from e7c_joint_admission_certificates import certificate_text
from test_e7c_joint_admission_capture import fixture_documents


def main():
    package = Path(__file__).resolve().parent / "proof-packages/lean-core"
    packets = [capture(document) for document in fixture_documents()]
    with tempfile.TemporaryDirectory(prefix="e7c-native-admission-") as directory:
        directory = Path(directory)

        def check(name, observations):
            path = directory / (name + ".lean")
            path.write_text(certificate_text(observations))
            return subprocess.run(["lake", "env", "lean", str(path)], cwd=package,
                                  capture_output=True, text=True, timeout=120)

        good = check("FreshAdmissionPrefix", packets)
        if good.returncode:
            raise RuntimeError("fresh native admission receipts failed:\n" + good.stdout + good.stderr)
        forged = []

        def changed(name, mutate):
            packet = copy.deepcopy(packets[1])
            mutate(packet)
            forged.append((name, packet))

        changed("ReboundFractionOperand", lambda p: p["row_calls"][0]["fraction"].__setitem__("numerator", 99))
        changed("WrongFractionReturn", lambda p: p["row_calls"][0]["fraction"].__setitem__(
            "output", {"numerator": 7, "denominator": 13}))
        changed("BooleanRawInteger", lambda p: p["row_calls"][0]["fraction"]["input"].__setitem__("numerator", True))
        changed("NullConfigTagChanged", lambda p: p["row_calls"][0]["configs"][0]["output"].__setitem__("tag", ""))
        changed("ConfigEdgesOperandChanged", lambda p: p["row_calls"][0]["configs"][0].__setitem__("edges_operand", []))
        changed("ParserOrderChanged", lambda p: p["parsed_rows"].reverse())
        changed("MissingRowCalls", lambda p: p["row_calls"].pop())
        changed("ReboundConstructorTuple", lambda p: p["constructor"].__setitem__("output_tuple_ref", 999))
        changed("ConstructorCoefficientChanged", lambda p: p["constructor"]["output_terms"][0].__setitem__(
            "coefficient", {"numerator": 7, "denominator": 13}))
        changed("MissingConstructorCell", lambda p: p["constructor"]["output_refs"].pop())
        for name, observation in forged:
            result = check(name, [observation])
            if result.returncode != 1 or "error:" not in result.stdout:
                raise RuntimeError("forgery accepted or kernel verification failed: " + name +
                                   "\n" + result.stdout + result.stderr)
        print(json.dumps({"fresh_admission_prefixes": len(packets),
                          "raw_rows": sum(len(p["row_calls"]) for p in packets),
                          "observed_call_boundaries": sum(p["calls"] for p in packets),
                          "kernel_rejections": len(forged),
                          "observed_later_admission_exceptions": sum(
                              not p["observed_admit_exit"]["returned"] for p in packets),
                          "native_dispatch_denotation_and_host_exit": "trusted/open",
                          "joint_aggregation_and_final_equality_adequacy": "unproved"}))


if __name__ == "__main__":
    main()
