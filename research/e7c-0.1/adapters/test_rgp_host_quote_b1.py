"""Canonical §R.2/R.4 anti-collapse cases beyond executable companion coverage."""

from dataclasses import replace
import unittest

from rgp_finite_b1 import (AdmissionError, HostBoundary, canonical, sha, contextual_view,
                           hosts, quote, reconstruct, unquote)
from test_rgp_finite_b1 import layers


class RGPHostQuotation(unittest.TestCase):
    def test_host_requires_quote_position_and_contract(self):
        layer, _ = layers()
        quoted = quote(layer)
        boundary = HostBoundary("messages", "v1", layer.signature)
        relation = hosts(layer, quoted, boundary)
        self.assertEqual((relation.host_identity, relation.quoted_source_identity),
                         (layer.identity, layer.identity))
        self.assertEqual(relation.interface_position, "messages")
        self.assertEqual(unquote(quoted), layer.record())
        self.assertEqual(quoted.quotation_rank, layer.placement.rank + 1)
        self.assertEqual(layer.placement.rank, 0)  # host rank does not order the quote
        for wrong in (HostBoundary("unknown", "v1", layer.signature),
                      HostBoundary("messages", "v2", layer.signature),
                      HostBoundary("messages", "v1", "other")):
            with self.subTest(boundary=wrong):
                with self.assertRaises(AdmissionError):
                    hosts(layer, quoted, wrong)

    def test_quote_tampering_and_local_view_do_not_expand_role_access(self):
        layer, _ = layers()
        quoted = quote(layer)
        with self.assertRaises(AdmissionError):
            unquote(replace(quoted, payload=quoted.payload[:-1]))
        with self.assertRaises(AdmissionError):
            unquote(replace(quoted, quotation_rank=quoted.source_rank))
        forged = canonical({"placement": {"rank": quoted.source_rank},
                            "kernel": "0.12.1-experimental", "profile": "RGP/0.1",
                            "model": "RGP-B1/0.1"})
        with self.assertRaises(AdmissionError):
            hosts(layer, replace(quoted, payload=forged, source_identity=sha(forged)),
                  HostBoundary("messages", "v1", layer.signature))
        local = contextual_view(layer, role="operator", temporal_locality="t0",
                                fields=("carrier",), edition="project/1")
        self.assertEqual(local.source.source_identity, local.view.source_identity)
        self.assertEqual(local.temporal_locality, "t0")
        self.assertNotIn("rules", local.view.fields)
        self.assertIn("rules", unquote(local.source))
        with self.assertRaises(AdmissionError):
            reconstruct(local.view)
        with self.assertRaises(AdmissionError):
            contextual_view(layer, role="guest", temporal_locality="t0",
                            fields=("carrier",), edition="project/1")
        with self.assertRaises(AdmissionError):
            contextual_view(layer, role="operator", temporal_locality="",
                            fields=("carrier",), edition="project/1")


if __name__ == "__main__":
    unittest.main()
