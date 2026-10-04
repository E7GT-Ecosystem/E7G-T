"""Transport observed raw operands and native returns without repairing them.

Literal safety/domain checks are separate from the local equations checked by
Lean. No expected parse, constructor output or host-exit theorem is generated.
"""
import json
import math

from e7c_joint_admission_capture import EDITION
from e7c_joint_serializer_native_values import (
    graph_term, lean_string, raw_snapshot, raw_term, validate_input_literals,
)


def ratio_term(pair):
    if type(pair) is not dict or set(pair) != {"numerator", "denominator"}:
        raise ValueError("native Fraction fields required")
    n, d = pair["numerator"], pair["denominator"]
    if (type(n) is not int or type(d) is not int or n == 0 or d <= 0
            or math.gcd(n, d) != 1 or max(n.bit_length(), d.bit_length()) > 256):
        raise ValueError("canonical native Fraction literals required")
    return ("({ num := (" + str(n) + "), den := " + str(d) +
            ", den_nz := by decide, reduced := by decide } : Rat)")


def fields_term(raw):
    return "[" + ", ".join("(" + lean_string(k) + ", (" + raw_term(v) + "))"
                              for k, v in raw.items()) + "]" if type(raw) is dict else "[]"


def wire_rows_term(rows):
    validate_input_literals(rows)
    return "[" + ", ".join("⟨" + graph_term(row["atoms"][0]) + ", " +
                              graph_term(row["atoms"][1]) + ", " +
                              ratio_term(row["coefficient"]) + "⟩" for row in rows) + "]"


def validate_literals(packet):
    fields = {"edition", "input_rows", "row_calls", "parsed_rows", "constructor",
              "observed_admit_exit", "manifest", "calls", "limits", "native_dispatch_and_denotation"}
    if type(packet) is not dict or set(packet) != fields or packet["edition"] != EDITION:
        raise ValueError("admission packet fields required")
    raw_snapshot(packet["input_rows"])
    if type(packet["row_calls"]) is not list or len(packet["row_calls"]) > 64:
        raise ValueError("bounded row-call array required")
    for row in packet["row_calls"]:
        if type(row) is not dict or set(row) != {"input", "configs", "fraction"}:
            raise ValueError("row call fields required")
        raw_snapshot(row["input"])
        if type(row["configs"]) is not list or len(row["configs"]) != 2:
            raise ValueError("two Config call records required")
        for config in row["configs"]:
            if type(config) is not dict or set(config) != {"input", "edges_operand", "tag_operand", "output"}:
                raise ValueError("Config call fields required")
            raw_snapshot(config["input"])
            if (type(config["edges_operand"]) is not list
                    or any(type(e) is not str for e in config["edges_operand"])
                    or (config["tag_operand"] is not None and type(config["tag_operand"]) is not str)):
                raise ValueError("Config operand literal types required")
            # Validate the output graph shape through the existing typed row
            # domain, without comparing it with a reconstructed expectation.
            validate_input_literals([{"atoms": [config["output"], config["output"]],
                                      "coefficient": {"numerator": 1, "denominator": 1}}])
        fraction = row["fraction"]
        if type(fraction) is not dict or set(fraction) != {"input", "numerator", "denominator", "output"}:
            raise ValueError("Fraction call fields required")
        raw_snapshot(fraction["input"])
        if any(type(fraction[k]) is not int or fraction[k].bit_length() > 256
               for k in ("numerator", "denominator")):
            raise ValueError("exact integer Fraction operands required")
        ratio_term(fraction["output"])
    validate_input_literals(packet["parsed_rows"])
    constructor = packet["constructor"]
    if (type(constructor) is not dict or set(constructor) != {
            "arity", "stored_arity", "input_terms", "output_terms", "input_tuple_ref",
            "output_tuple_ref", "input_refs", "output_refs"}):
        raise ValueError("Joint constructor fields required")
    for key in ("arity", "stored_arity", "input_tuple_ref", "output_tuple_ref"):
        if type(constructor[key]) is not int or constructor[key] < 0:
            raise ValueError("natural constructor scalar required")
    for key in ("input_refs", "output_refs"):
        if (type(constructor[key]) is not list or len(constructor[key]) > 64
                or any(type(ref) is not int or ref <= 0 for ref in constructor[key])):
            raise ValueError("bounded positive constructor tokens required")
    validate_input_literals(constructor["input_terms"])
    validate_input_literals(constructor["output_terms"])
    limits = packet["limits"]
    if (type(limits) is not dict or set(limits) != {"rows", "calls", "bytes"}
            or any(type(n) is not int or n < 0 for n in limits.values())
            or limits["rows"] > 64 or limits["calls"] > 200 or limits["bytes"] > 262144
            or len(packet["row_calls"]) > limits["rows"]
            or type(packet["calls"]) is not int or not 0 <= packet["calls"] <= limits["calls"]
            or len(json.dumps(packet, ensure_ascii=False).encode()) > limits["bytes"]):
        raise ValueError("admission evidence limits required")


def certificate_text(packets):
    lines = ["import E7CJointNativeAdmissionCapture", "",
             "namespace E7CJointNativeAdmissionFixtures",
             "open E7CEECQTwoStageExactCodec E7CJointRawJsonAdmission",
             "open E7CJointNativeAdmissionComposition", ""]
    for index, packet in enumerate(packets):
        validate_literals(packet)
        names = []
        for ordinal, row in enumerate(packet["row_calls"]):
            prefix = f"p{index}r{ordinal}"
            for side, config in zip(("left", "right"), row["configs"]):
                name = prefix + side
                tag = "none" if config["tag_operand"] is None else "some " + lean_string(config["tag_operand"])
                edges = "[" + ", ".join(lean_string(e) for e in config["edges_operand"]) + "]"
                lines.extend([f"def {name} : ConfigCapture :=",
                              "  ⟨(" + raw_term(config["input"]) + "), " + fields_term(config["input"]) +
                              ", " + edges + ", " + tag + ", " + graph_term(config["output"]) + "⟩",
                              f"theorem {name}Checked : ConfigReceipt {name} := by",
                              "  constructor <;> first | rfl | decide", ""])
            fraction = row["fraction"]
            fname = prefix + "fraction"
            lines.extend([f"def {fname} : FractionCapture :=",
                          "  ⟨(" + raw_term(fraction["input"]) + "), " + fields_term(fraction["input"]) +
                          ", (" + str(fraction["numerator"]) + "), (" + str(fraction["denominator"]) +
                          "), " + ratio_term(fraction["output"]) + "⟩",
                          f"theorem {fname}Checked : FractionReceipt {fname} := by",
                          "  constructor <;> first | rfl | decide | (simp [Rat.div, Rat.inv_def] <;> decide)", "",
                          f"def {prefix} : RowCapture :=",
                          "  ⟨(" + raw_term(row["input"]) + "), " + fields_term(row["input"]) +
                          f", {prefix}left, {prefix}right, {fname}⟩",
                          f"theorem {prefix}Checked : RowReceipt {prefix} := by",
                          "  refine ⟨?_, ?_, ?_, ?_, " + prefix + "leftChecked, " + prefix +
                          "rightChecked, " + fname + "Checked⟩ <;> first | rfl | decide", ""])
            names.append(prefix)
        lines.extend([f"def captures{index} : List RowCapture := [" + ", ".join(names) + "]",
                      f"def parsed{index} : List WireRow := " + wire_rows_term(packet["parsed_rows"]),
                      f"theorem prefix{index} : PrefixReceipt (" + raw_term(packet["input_rows"]) +
                      f") captures{index} parsed{index} := by",
                      "  refine ⟨?_, ?_, ?_, ?_⟩",
                      "  · rfl", "  · decide",
                      "  · " + ("exact True.intro" if not names else
                                   "exact ⟨" + ", ⟨".join(name + "Checked" for name in names) +
                                   ", True.intro" + "⟩" * len(names)),
                      "  · rfl", ""])
        c = packet["constructor"]
        lines.extend([f"def constructor{index} : ConstructorCapture :=",
                      "  ⟨" + str(c["arity"]) + ", " + str(c["stored_arity"]) + ", " +
                      wire_rows_term(c["input_terms"]) + ", " + wire_rows_term(c["output_terms"]) +
                      ", " + str(c["input_tuple_ref"]) + ", " + str(c["output_tuple_ref"]) +
                      ", ⟨" + str(c["input_refs"]) + ", " + str(c["output_refs"]) + "⟩⟩",
                      f"theorem constructor{index}Checked : ConstructorReceipt constructor{index} := by",
                      "  constructor <;> first | rfl | decide", ""])
    return "\n".join(lines + ["end E7CJointNativeAdmissionFixtures", ""])
