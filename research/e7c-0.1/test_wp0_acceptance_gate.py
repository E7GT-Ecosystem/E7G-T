from hashlib import sha256
from pathlib import Path
import re
import subprocess
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[2]
RESEARCH = Path(__file__).resolve().parent
COVERAGE_PATH = RESEARCH / "E7C_0.1_SUCCESSOR_SOURCE_COVERAGE.yaml"
REGISTER_PATH = RESEARCH / "E7C_0.1_POST_V0121_GAP_AND_PROPOSAL_REGISTER.md"
DISPOSITIONS_PATH = RESEARCH / "E7C_0.1_COMPONENT_DISPOSITIONS.md"
ALLOWED_DECISIONS = {"retain", "adapt", "replace", "retire"}


class WP0AcceptanceGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.coverage = yaml.safe_load(COVERAGE_PATH.read_text(encoding="utf-8"))

    def test_every_pr_through_cutoff_is_accounted_for_exactly_once(self):
        ledger = self.coverage["pull_request_ledger"]
        numbers = [entry["pull_request"] for entry in ledger["entries"]]
        expected = list(range(ledger["interval"]["first"], ledger["interval"]["last"] + 1))

        self.assertEqual(numbers, expected)
        self.assertEqual(len(numbers), len(set(numbers)))
        self.assertTrue(ledger["exactly_once"])
        allowed = set(ledger["statuses"])
        self.assertTrue(all(entry["status"] in allowed for entry in ledger["entries"]))

    def test_all_gap_register_entries_are_mapped(self):
        declared = set(re.findall(r"\| (GPR-\d{3}) \|", REGISTER_PATH.read_text(encoding="utf-8")))
        mapped = set(self.coverage["canonical_baseline"].get("register_entries", []))
        for artifact in self.coverage["artifacts"]:
            mapped.update(artifact.get("register_entries", []))

        self.assertEqual(declared, {f"GPR-{number:03d}" for number in range(1, 19)})
        self.assertEqual(mapped, declared)

    def test_baseline_paths_blob_pins_and_canonical_digest_resolve(self):
        baseline = self.coverage["baseline_commit"]
        canonical = self.coverage["canonical_baseline"]
        pinned = [(canonical["path"], canonical["blob_sha"])]
        for artifact in self.coverage["artifacts"]:
            for item in artifact.get("paths", []):
                pinned.append((item["path"], item["blob_sha"]))
            for item in artifact.get("anchor_blobs", []):
                pinned.append((item["path"], item["blob_sha"]))

        for path, expected_blob in pinned:
            with self.subTest(path=path):
                actual_blob = subprocess.check_output(
                    ["git", "rev-parse", f"{baseline}:{path}"], cwd=ROOT, text=True
                ).strip()
                self.assertEqual(actual_blob, expected_blob)

        canonical_bytes = subprocess.check_output(
            ["git", "show", f"{baseline}:{canonical['path']}"], cwd=ROOT
        )
        self.assertEqual(sha256(canonical_bytes).hexdigest(), canonical["sha256"])

    def test_component_decisions_use_only_closed_vocabulary(self):
        decisions = set(
            re.findall(
                r"^\|[^\n]*\| `([^`]+)` \|",
                DISPOSITIONS_PATH.read_text(encoding="utf-8"),
                flags=re.MULTILINE,
            )
        )
        self.assertTrue(decisions)
        self.assertLessEqual(decisions, ALLOWED_DECISIONS)

    def test_wpc_0_2_retains_wpc_0_1_predecessor_contract(self):
        artifacts = {item["id"]: item for item in self.coverage["artifacts"]}
        self.assertEqual(
            artifacts["successor-wpc-package"]["predecessor_contract"],
            {
                "identity": "WPC/0.1",
                "relation": "explicit_successor_extension",
                "register_entry": "GPR-014",
            },
        )


if __name__ == "__main__":
    unittest.main()
