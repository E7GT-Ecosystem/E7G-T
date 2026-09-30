"""Selected source/loop check, not a C parser or a native memory verifier."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

FIXTURE = Path(__file__).with_name("fixtures") / "tuple-cell-copy-source.json"
LOOP = """        for (i = 0; i < n; i++) {
            PyObject *o = src[i];
            dest[i] = Py_NewRef(o);
        }"""
PINS = {
    "3.12.3": "f59abe2e644f14c599410cbb8316d548c9bfd6b6",
    "3.12.14": "d017f34b94f0dfd2c28c283db58f64d763170bf4",
}

FAST_PATH_SHA256 = '5c80d1daaea6845cd4aefc5e38b3f1c2d81aa0cb71475292b3a92940c2843ec5'

def check_source_packet(packet: dict) -> None:
    if packet.get("edition") != "E7C-tuple-cell-copy/0.1-provisional":
        raise ValueError("wrong selected edition")
    if packet.get("repository") != "python/cpython" or packet.get("path") != "Objects/listobject.c":
        raise ValueError("wrong source")
    sources = packet.get("sources")
    if not isinstance(sources, list) or len(sources) != 2:
        raise ValueError("two source pins required")
    if [entry.get("version") for entry in sources] != list(PINS):
        raise ValueError("source order or versions changed")
    for entry in sources:
        if entry.get("git_blob") != PINS[entry["version"]]:
            raise ValueError("source blob changed")
        if entry.get("copy_loop") != LOOP:
            raise ValueError("copy loop changed")
        path = entry.get("selected_fast_path")
        if not isinstance(path, str) or path.count(LOOP) != 1:
            raise ValueError("selected path must contain the complete loop once")
        if hashlib.sha256(path.encode()).hexdigest() != FAST_PATH_SHA256:
            raise ValueError("selected fast path changed")


def copy_cells(cells: tuple, new_ref=lambda pointer: pointer) -> tuple[list, list]:
    if type(cells) is not tuple:
        raise ValueError("exact tuple required")
    output, events = [], []
    for index, pointer in enumerate(cells):
        events.append(("read", index, pointer))
        result = new_ref(pointer)
        events.append(("newRef", pointer, result))
        output.append(result)
        events.append(("write", index, result))
    return output, events


if __name__ == "__main__":
    check_source_packet(json.loads(FIXTURE.read_text()))
    print("Both selected CPython source paths and copy loops match their pins.")
