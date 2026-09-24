"""Finite cross-slice WP6 conformance record, not a general IR validator."""

import hashlib
import json
from pathlib import Path

from e7_ir_var_b1 import execute as execute_var, parse as parse_var, serialize as serialize_var
from e7_ir_strict_map_b1 import compare_replay as compare_strict
from e7_ir_named_maps_b1 import compare_replay as compare_named
from e7_ir_views_b1 import compare_replay as compare_view
from e7c_b1_canonical import canonical_key, digest
from e7c_b1_evaluator import Evaluator
from e7c_b1_replay_checker import check_witness

HERE = Path(__file__).resolve().parent / "fixtures" / "wp5_ir"
SLICES = (
    ("var", "finite_graph_var.json", None),
    ("strict_map", "strict_graph_map.json", compare_strict),
    ("named_total", "total_graph_map.json", compare_named),
    ("source_view", "source_graph_view.json", compare_view),
    ("lossy_projection", "lossy_graph_projection.json", compare_view),
)
EDITION = "E7-IR-CROSS-SLICE-CONFORMANCE/0.1-provisional"


def build_manifest():
    rows = []
    for label, filename, compare in SLICES:
        raw = (HERE / filename).read_bytes()
        package = json.loads(raw)
        if label == "var":
            source = package["source_document"]
            witness = package["source_result"]["witness"]
            ir = package["ir"]
            result = execute_var(parse_var(serialize_var(ir)))
            assert result == package["ir_result"]
        else:
            source = package["source_document"]
            witness = package["source_witness"]
            ir = package
            result = compare(ir)["ir_result"]
        replay = check_witness(witness)
        assert replay["status"] == "accepted"
        static = Evaluator(source).static
        dimensions = [entry["static_atom"]["dimension"] for entry in result["ordered_ledger"]]
        effects = [effect["dimension"] for effect in static["effects"]]
        assert set(dimensions) <= set(effects)
        assert all(entry["static_atom"] in static["effects"] for entry in result["ordered_ledger"])
        assert witness["evaluation_claim"]["resource_progress"] == result["resource_progress"]
        source_terminal = witness["evaluation_claim"]["terminal_outcome"]
        if source_terminal["tag"] == "success":
            assert result["terminal_outcome"]["tag"] == "success"
            assert result["terminal_outcome"]["value"] == source_terminal["value"]
            assert result["terminal_outcome"]["optional_witness"] is None
        else:
            assert result["terminal_outcome"] == source_terminal
        rows.append({"slice": label, "fixture": filename,
                     "fixture_sha256": hashlib.sha256(raw).hexdigest(),
                     "source_document_digest": digest(source),
                     "ir_edition": ir["ir_edition"],
                     "witness_identifier": witness["identity"]["witness_identifier"],
                     "static_type": static["type"],
                     "static_effects": [canonical_key(effect) for effect in static["effects"]],
                     "ledger_dimensions": dimensions,
                     "terminal_tag": result["terminal_outcome"]["tag"],
                     "completed_steps": result["resource_progress"]["completed_steps"]})
    return {"edition": EDITION, "scope": "five finite first-party replay fixtures",
            "source_authority": "E7G-T-v0.12.1/RGP2-experimental",
            "no_profile_or_product_promotion": True,
            "cases": rows}
