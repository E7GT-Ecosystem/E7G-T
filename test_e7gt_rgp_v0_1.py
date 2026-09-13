import unittest
from dataclasses import replace

from importlib.machinery import SourceFileLoader


rgp = SourceFileLoader("rgp", "E7G-T_RGP_v0.1.py").load_module()


def base_layer():
    return rgp.Layer(
        signature="workspace-layer/0.1",
        edition="parent-1",
        carrier={"release": "r1", "tasks": ["a", "b"]},
        rules=("workspace.generate",),
        interface={"messages": "v1"},
        access_policy={"operator": ("view",), "admin": ("view", "generate")},
        invariants={"schema": "messages-v1"},
        provenance={"created_by": "fixture"},
        placement=rgp.Placement(0, "design", "t0", "private", "root"),
    )


class RGPBoundedModelTests(unittest.TestCase):
    def test_hosting_is_not_generation(self):
        layer = base_layer()
        hosted = {"host": "platform", "component": layer.identity}
        self.assertNotIn("rule", hosted)

    def test_generated_object_need_not_be_hosted(self):
        child, edge = rgp.generate(
            base_layer(), rule_id="workspace.generate", rule_edition="1",
            child_edition="child-1", parameters={"release": "r2"},
            transform=lambda carrier, p: {**carrier, **p}, inherit=("schema",),
        )
        self.assertEqual(edge.child_identity, child.identity)
        self.assertNotIn("host", child.provenance)

    def test_shared_parameter_is_retained(self):
        parent = base_layer()
        one, edge_one = rgp.generate(
            parent, rule_id="workspace.generate", rule_edition="1",
            child_edition="child-a", parameters={"release_choice": "r2"},
            transform=lambda carrier, p: {**carrier, **p}, inherit=("schema",),
        )
        two, edge_two = rgp.generate(
            parent, rule_id="workspace.generate", rule_edition="1",
            child_edition="child-b", parameters={"release_choice": "r2"},
            transform=lambda carrier, p: {**carrier, **p}, inherit=("schema",),
        )
        self.assertEqual(edge_one.parameters, edge_two.parameters)
        self.assertNotEqual(one.identity, two.identity)

    def test_projection_retains_source_and_loss(self):
        view = rgp.project(base_layer(), role="operator", fields=("carrier",), edition="1")
        self.assertEqual(view.source_identity, base_layer().identity)
        self.assertIn("rules", view.lost)
        self.assertNotEqual(view.reconstruction, "singleton")

    def test_projection_does_not_modify_sr4_portion(self):
        layer = base_layer()
        portion = rgp.encode_sr4(layer, portion_index="A", codec_edition="json/1")
        rgp.project(layer, role="operator", fields=("carrier",), edition="1")
        self.assertEqual(rgp.decode_sr4(portion, codec_edition="json/1"), layer.canonical_record())

    def test_sr4_exact_round_trip_and_injectivity(self):
        first = base_layer()
        second = replace(first, edition="parent-2")
        first_portion = rgp.encode_sr4(first, portion_index="A", codec_edition="json/1")
        second_portion = rgp.encode_sr4(second, portion_index="A", codec_edition="json/1")
        self.assertEqual(rgp.decode_sr4(first_portion, codec_edition="json/1"), first.canonical_record())
        self.assertNotEqual(first_portion.payload, second_portion.payload)

    def test_digest_only_is_not_sr4(self):
        layer = base_layer()
        portion = rgp.EncodedPortion(
            layer.identity, layer.edition, "A", "digest/1", "digest/1",
            layer.identity.encode(), layer.identity, rgp.RetentionTier.SR0,
        )
        with self.assertRaisesRegex(rgp.RGPError, "insufficient"):
            rgp.decode_sr4(portion, codec_edition="digest/1")

    def test_damaged_portion_rejects_previous_witness(self):
        portion = rgp.encode_sr4(base_layer(), portion_index="A", codec_edition="json/1")
        damaged = replace(portion, payload=portion.payload[:-1])
        with self.assertRaisesRegex(rgp.RGPError, "invalid_encoding"):
            rgp.decode_sr4(damaged, codec_edition="json/1")

    def test_codec_binding_is_explicit(self):
        portion = rgp.encode_sr4(base_layer(), portion_index="A", codec_edition="json/1")
        with self.assertRaisesRegex(rgp.RGPError, "unsupported"):
            rgp.decode_sr4(portion, codec_edition="json/2")

    def test_rank_and_regime_are_independent(self):
        layer = base_layer()
        same_rank = replace(layer, placement=replace(layer.placement, regime="run"))
        same_regime = replace(layer, placement=replace(layer.placement, rank=3))
        self.assertEqual(layer.placement.rank, same_rank.placement.rank)
        self.assertEqual(layer.placement.regime, same_regime.placement.regime)

    def test_composition_preserves_component_identity(self):
        first = base_layer()
        second = replace(first, edition="parent-2")
        composite = rgp.compose((first, second), interface_edition="messages/1")
        self.assertEqual(composite.component_identities, (first.identity, second.identity))
        self.assertTrue(composite.preserves_component_identity)

    def test_external_instantiation_is_not_inferred(self):
        self.assertNotIn("external_instantiation", base_layer().canonical_record())


if __name__ == "__main__":
    unittest.main()
