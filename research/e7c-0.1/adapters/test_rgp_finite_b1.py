"""Differential and negative tests for the pinned RGP-B1/0.1 companion."""

from dataclasses import replace
from importlib.machinery import SourceFileLoader
from pathlib import Path
import unittest

from rgp_finite_b1 import (AdmissionError, Encoded, Layer, Placement, compose,
                           decode_sr4, encode_sr4, generate, host, project,
                           reconstruct)

SOURCE = Path(__file__).resolve().parents[3] / "E7G-T_RGP_v0.1.py"
reference = SourceFileLoader("rgp_source_for_adapter", str(SOURCE)).load_module()


def layers():
    fields = dict(signature="workspace-layer/0.1", edition="parent-1",
                  carrier={"release": "r1", "tasks": ["a", "b"]},
                  rules=("workspace.generate",), interface={"messages": "v1"},
                  access_policy={"operator": ("view",), "admin": ("view", "generate")},
                  invariants={"schema": "messages-v1"},
                  provenance={"created_by": "fixture"})
    args = (0, "design", "t0", "private", "root")
    return Layer(**fields, placement=Placement(*args)), reference.Layer(
        **fields, placement=reference.Placement(*args))


class RGPFiniteDifferential(unittest.TestCase):
    def test_generation_inheritance_rank_and_host_separation(self):
        layer, old = layers()
        arguments = dict(rule_id="workspace.generate", rule_edition="1",
                         child_edition="child-1", parameters={"release": "r2"},
                         inherit=("schema",))
        child, edge = generate(layer, **arguments)
        old_child, old_edge = reference.generate(
            old, **arguments, transform=lambda carrier, params: {**carrier, **params})
        self.assertEqual(child.record(), old_child.canonical_record())
        self.assertEqual(child.identity, old_child.identity)
        self.assertEqual(edge.__dict__, old_edge.__dict__)
        self.assertEqual(host(layer, "platform").component_identity, layer.identity)
        self.assertNotIn("host", child.provenance)
        self.assertEqual(child.placement.temporal_scope, layer.placement.temporal_scope)
        self.assertEqual(child.placement.access_scope, layer.placement.access_scope)
        self.assertEqual(child.placement.composition_scope, layer.placement.composition_scope)
        with self.assertRaises(AdmissionError):
            generate(layer, **{**arguments, "inherit": ("missing",)})
        with self.assertRaises(AdmissionError):
            generate(layer, **{**arguments, "rule_id": "unknown"})

    def test_projection_differential_and_retained_reconstruction(self):
        layer, old = layers()
        view = project(layer, role="operator", fields=("carrier",), edition="1")
        old_view = reference.project(old, role="operator", fields=("carrier",), edition="1")
        self.assertEqual((view.source_identity, view.fields, view.preserved, view.lost),
                         (old_view.source_identity, old_view.view,
                          old_view.preserved, old_view.lost))
        with self.assertRaisesRegex(AdmissionError, "lossy"):
            reconstruct(view)
        self.assertEqual(reconstruct(view, encode_sr4(layer, portion_index="A",
                                                     codec_edition="json/1")), layer.record())
        with self.assertRaises(AdmissionError):
            project(layer, role="guest", fields=("carrier",), edition="1")
        with self.assertRaises(AdmissionError):
            project(layer, role="operator", fields=("unknown",), edition="1")
        full = project(layer, role="operator", fields=tuple(layer.record()), edition="1")
        self.assertEqual(reconstruct(full), layer.record())
        with self.assertRaises(AdmissionError):
            reconstruct(replace(view, preserved=("carrier", "unknown")),
                        encode_sr4(layer, portion_index="A", codec_edition="json/1"))

    def test_sr4_round_trip_and_invalid_claims(self):
        layer, old = layers()
        portion = encode_sr4(layer, portion_index="A", codec_edition="json/1")
        old_portion = reference.encode_sr4(old, portion_index="A", codec_edition="json/1")
        self.assertEqual(portion.payload, old_portion.payload)
        self.assertEqual(portion.payload_digest, old_portion.payload_digest)
        self.assertEqual(decode_sr4(portion, codec_edition="json/1"),
                         reference.decode_sr4(old_portion, codec_edition="json/1"))
        second = replace(layer, edition="parent-2")
        self.assertNotEqual(portion.payload,
                            encode_sr4(second, portion_index="A", codec_edition="json/1").payload)
        for damaged in (replace(portion, retention_tier=0),
                        replace(portion, payload=portion.payload[:-1]),
                        replace(portion, source_edition="wrong"),
                        replace(portion, source_identity="0" * 64)):
            with self.subTest(damaged=damaged):
                with self.assertRaises(AdmissionError):
                    decode_sr4(damaged, codec_edition="json/1")
        with self.assertRaisesRegex(AdmissionError, "unsupported"):
            decode_sr4(portion, codec_edition="json/2")
        with self.assertRaises(AdmissionError):
            reconstruct(project(second, role="operator", fields=("carrier",), edition="1"),
                        portion)

    def test_composition_and_independent_coordinates(self):
        layer, old = layers()
        second, old_second = replace(layer, edition="parent-2"), replace(old, edition="parent-2")
        composite = compose((layer, second), interface_edition="messages/1")
        old_composite = reference.compose((old, old_second), interface_edition="messages/1")
        self.assertEqual(composite.component_identities, old_composite.component_identities)
        with self.assertRaises(AdmissionError):
            compose((layer, layer), interface_edition="messages/1")
        self.assertEqual(replace(layer.placement, regime="run").rank, layer.placement.rank)
        self.assertEqual(replace(layer.placement, rank=3).regime, layer.placement.regime)
        with self.assertRaises(AdmissionError):
            replace(layer, placement=replace(layer.placement, rank=True))
        with self.assertRaises(AdmissionError):
            replace(layer, carrier={"value": float("nan")})


if __name__ == "__main__":
    unittest.main()
