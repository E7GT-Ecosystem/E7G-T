"""Export retained native observations verbatim for Lean kernel receipts.

Admission here checks literal types and evidence limits, not expected helper
results, primitive plans or a source/IR semantic oracle. Kernel receipts do
not establish the claimed native origin of a caller-supplied packet.
"""
import json
from e7c_joint_serializer_native_values import (
    graph_term, lean_string, raw_snapshot, raw_term, validate_input_literals,
)
from e7c_joint_serializer_primitive_capture import EDITION


def validate_literals(packet):
    fields = {"edition", "input", "output", "events", "copies", "manifest", "limits",
              "native_dispatch_and_capture_adequacy"}
    if type(packet) is not dict or set(packet) != fields or packet["edition"] != EDITION:
        raise ValueError("native primitive packet fields required")
    # Reuse the selected scalar/canonical input-domain validator without the
    # legacy observer or its frame-only limits.
    validate_input_literals(packet["input"])
    raw_snapshot(packet["output"])
    if type(packet["events"]) is not list or len(packet["events"]) > 1200:
        raise ValueError("primitive event array required")
    for event in packet["events"]:
        if (type(event) is not dict or set(event) != {"site", "payload"}
                or type(event["site"]) is not str):
            raise ValueError("primitive event literals required")
        lean_string(event["site"])
        raw_snapshot(event["payload"])
    if type(packet["copies"]) is not list or len(packet["copies"]) > 128:
        raise ValueError("copy observation array required")
    for copy in packet["copies"]:
        if type(copy) is not dict or set(copy) != {"input_refs", "output_refs"}:
            raise ValueError("copy observation fields required")
        for field in ("input_refs", "output_refs"):
            if (type(copy[field]) is not list or len(copy[field]) > 3
                    or any(type(ref) is not int or ref <= 0 for ref in copy[field])):
                raise ValueError("positive native object tokens required")
    limits = packet["limits"]
    if (type(limits) is not dict or set(limits) != {"rows", "events", "bytes"}
            or any(type(n) is not int or n < 0 for n in limits.values())
            or limits["rows"] > 64 or limits["events"] > 1200 or limits["bytes"] > 262144
            or len(packet["input"]) > limits["rows"]
            or len(packet["events"]) > limits["events"]):
        raise ValueError("primitive evidence limits required")
    if len(json.dumps(packet, ensure_ascii=False).encode()) > limits["bytes"]:
        raise ValueError("primitive packet byte limit")


def certificate_text(packets):
    lines = ["import E7CJointNativeSerializerCapture", "",
             "namespace E7CJointNativeSerializerFixtures",
             "open E7CEECQTwoStageExactCodec E7CJointRawJsonAdmission",
             "open E7CJointNativeSerializerCapture", ""]
    for index, packet in enumerate(packets):
        validate_literals(packet)
        rows = []
        for row in packet["input"]:
            left, right = row["atoms"]
            fraction = row["coefficient"]
            rows.append("⟨" + graph_term(left) + ", " + graph_term(right) + ", " +
                        "({ num := (" + str(fraction["numerator"]) + "), den := " +
                        str(fraction["denominator"]) +
                        ", den_nz := by decide, reduced := by decide } : Rat)⟩")
        events = ", ".join("(" + lean_string(e["site"]) + ", (" + raw_term(e["payload"]) + "))"
                           for e in packet["events"])
        copies = ", ".join("⟨" + str(c["input_refs"]) + ", " + str(c["output_refs"]) + "⟩"
                           for c in packet["copies"])
        lines.extend([f"def rows{index} : List WireRow := [" + ", ".join(rows) + "]",
                      f"def capture{index} : Capture :=",
                      "  ⟨(" + raw_term(packet["output"]) + "), [" + events + "], [" + copies + "]⟩",
                      f"theorem checked{index} : Certificate rows{index} capture{index} := by",
                      "  refine ⟨?_, ?_, ?_, ?_⟩ <;> rfl", ""])
    return "\n".join(lines + ["end E7CJointNativeSerializerFixtures", ""])
