from pathlib import Path
import unittest

import yaml


MANIFEST = Path(__file__).with_name("E7C_0.1_SUCCESSOR_SOURCE_COVERAGE.yaml")


class SuccessorSourceCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.coverage = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))

    def test_package_predecessor_contract_is_closed(self):
        """Every declared package predecessor has a mapped differential."""
        for artifact in self.coverage["artifacts"]:
            contract = artifact.get("predecessor_contract")
            if contract is None:
                continue

            component_mappings = {
                (component["identity"], component["register_entry"])
                for component in artifact.get("components", [])
            }
            expected_mapping = (
                contract["identity"],
                contract["register_entry"],
            )

            with self.subTest(artifact=artifact["id"]):
                self.assertIn(
                    expected_mapping,
                    component_mappings,
                    "declared predecessor must be mapped as a package component",
                )
                self.assertIn(
                    contract["register_entry"],
                    artifact.get("register_entries", []),
                    "predecessor differential must be in package register coverage",
                )


if __name__ == "__main__":
    unittest.main()
