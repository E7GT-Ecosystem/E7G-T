"""Check the live unspecialized _graph bytecode and emit its Lean program.

Instruction decoding and modeled execution are not CPython dispatch adequacy.
Caches are retained in the manifest but not executed in this selected model.
The preceding observer's exact source/code/binding checks are required.
"""
import dis
import hashlib
import json
from dataclasses import dataclass

from e7c_joint_serializer_observer import ROOT, freeze_manifest, lean_string, source

EDITION = "E7C-graph-bytecode/0.1-provisional"
GENERATED = ROOT / "proof-packages/lean-core/E7CJointGraphBytecodeGenerated.lean"


def decode_instructions(instructions):
    """No generic Python language, method dispatch, jumps or exception table."""
    program = []
    for instruction in instructions:
        op, arg, value = instruction.opname, instruction.arg, instruction.argval
        if instruction.is_jump_target:
            raise ValueError("jump targets are outside the selected straight-line grammar")
        if op == "RESUME" and arg == 0:
            program.append(("resume", 0))
        elif op == "LOAD_GLOBAL" and value == "list" and arg == 1:
            program.append(("loadGlobal", "list", True))
        elif op == "LOAD_FAST" and arg == 0 and value == "g":
            program.append(("loadFast", 0))
        elif op == "LOAD_ATTR" and (value, arg) in {("edges", 2), ("tag", 4)}:
            program.append(("loadAttr", value))
        elif op == "CALL" and arg == 1:
            program.append(("call", 1))
        elif (op == "LOAD_CONST" and type(value) is tuple and len(value) == 2
              and all(type(k) is str for k in value) and len(set(value)) == 2):
            program.append(("loadKeys", value))
        elif op == "BUILD_CONST_KEY_MAP" and arg == 2:
            program.append(("buildConstKeyMap", 2))
        elif op == "RETURN_VALUE" and arg is None:
            program.append(("returnValue",))
        else:
            raise ValueError("unsupported opcode/operand: " + op)
    return program


def current_program():
    manifest = freeze_manifest()
    code = source._graph.__code__
    if (code.co_argcount != 1 or code.co_posonlyargcount or code.co_kwonlyargcount
            or code.co_varnames != ("g",) or code.co_exceptiontable
            or code.co_flags != 0x1000003 or code.co_stacksize != 3
            or code.co_freevars or code.co_cellvars
            or code.co_names != ("list", "edges", "tag")
            or code.co_consts != (None, ("edges", "tag"))):
        raise ValueError("unsupported graph frame layout or exception table")
    instructions = list(dis.get_instructions(code, show_caches=False, adaptive=False))
    program = decode_instructions(instructions)
    # Fixed source/code validation above authenticates neither native execution
    # nor this decoder. Each complete decoded image must match the generated file.
    all_instructions = list(dis.get_instructions(code, show_caches=True, adaptive=False))
    if [i for i in all_instructions if i.opname != "CACHE"] != instructions:
        raise ValueError("cache elision changed the instruction image")
    manifest = {"edition": EDITION, "runtime": manifest,
                "co_code_sha256": hashlib.sha256(code.co_code).hexdigest(),
                "stacksize": code.co_stacksize, "flags": code.co_flags,
                "exception_table_hex": code.co_exceptiontable.hex(),
                "instructions_with_caches": [{"offset": i.offset, "opname": i.opname,
                    "arg": i.arg, "argval": i.argval} for i in all_instructions],
                "program": program,
                "execution_adequacy": "unproved; unspecialized instruction model only"}
    return program, manifest


def generated_text(program):
    def term(instruction):
        op, *args = instruction
        if op in {"resume", "loadFast", "call", "buildConstKeyMap"}:
            return f"(.{op} {args[0]})"
        if op == "loadGlobal":
            return "(.loadGlobal " + lean_string(args[0]) + " " + str(args[1]).lower() + ")"
        if op == "loadAttr":
            return "(.loadAttr " + lean_string(args[0]) + ")"
        if op == "loadKeys":
            return "(.loadKeys [" + ", ".join(lean_string(k) for k in args[0]) + "])"
        if op == "returnValue":
            return ".returnValue"
        raise ValueError("unsupported generated instruction")
    return ("import E7CJointGraphBytecodeSyntax\n\n"
            "/- Generated from the checked live unspecialized CPython-3.12 _graph\n"
            "image. CACHE entries are recorded separately. Dispatch adequacy is\n"
            "not established by this program or its all-input theorem. -/\n"
            "namespace E7CJointGraphBytecodeGenerated\n"
            "open E7CJointGraphBytecodeSyntax\n\n"
            "def graphProgram : List Instruction :=\n  [" +
            ",\n   ".join(term(i) for i in program) + "]\n\n"
            "end E7CJointGraphBytecodeGenerated\n")


def check():
    program, manifest = current_program()
    if generated_text(program) != GENERATED.read_text():
        raise ValueError("generated Lean program does not match the live bytecode image")
    return manifest


@dataclass(frozen=True)
class ModelValue:
    kind: str
    payload: object


def raw(value):
    if value.kind == "raw":
        return value.payload
    if value.kind == "sequence":
        return [raw(child) for child in value.payload]
    raise ValueError("modeled value has no selected raw conversion")


def run_model(program, graph, *, read=None):
    """Independent Python realization of the declared stack model, not CPython.

    A malformed model state is rejected with ValueError. This function neither
    classifies actual host outcomes nor enforces product resource budgets.
    """
    def default_read(value, name):
        if value.kind != "graph" or name not in {"edges", "tag"}:
            raise ValueError("unsupported modeled attribute")
        if name == "edges":
            return ModelValue("sequence", [ModelValue("raw", edge) for edge in value.payload[name]])
        return ModelValue("raw", value.payload[name])
    read = default_read if read is None else read
    locals_ = [ModelValue("graph", graph)]
    stack = []  # top first, as in Lean
    for pc, instruction in enumerate(program):
        op, *args = instruction
        if op == "resume" and args == [0]:
            continue
        if op == "loadGlobal" and args == ["list", True]:
            stack[:0] = [("listConstructor", None), ("nullSentinel", None)]
        elif op == "loadFast" and args == [0]:
            stack.insert(0, ("value", locals_[0]))
        elif op == "loadAttr" and stack and stack[0][0] == "value":
            stack[0] = ("value", read(stack[0][1], args[0]))
        elif (op == "call" and args == [1] and len(stack) >= 3
              and stack[0][0] == "value" and stack[0][1].kind == "sequence"
              and stack[1:3] == [("listConstructor", None), ("nullSentinel", None)]):
            allocated = []
            for cell in stack[0][1].payload:
                allocated.append(cell)
            stack[:3] = [("value", ModelValue("sequence", allocated))]
        elif op == "loadKeys":
            stack.insert(0, ("keys", args[0]))
        elif (op == "buildConstKeyMap" and args == [2] and len(stack) >= 3
              and stack[0][0] == "keys" and len(stack[0][1]) == 2
              and len(set(stack[0][1])) == 2 and stack[1][0] == stack[2][0] == "value"):
            keys = stack[0][1]
            output = dict(zip(keys, [raw(stack[2][1]), raw(stack[1][1])]))
            stack[:3] = [("value", ModelValue("raw", output))]
        elif op == "returnValue" and not args and len(stack) == 1 and stack[0][0] == "value":
            if pc != len(program) - 1:
                raise ValueError("return is not the final modeled instruction")
            return raw(stack[0][1])
        else:
            raise ValueError("unsupported modeled instruction/stack shape")
    raise ValueError("modeled execution has no return")


if __name__ == "__main__":
    print(json.dumps(check(), ensure_ascii=False))
