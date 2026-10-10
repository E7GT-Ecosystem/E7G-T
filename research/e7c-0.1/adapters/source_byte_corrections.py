"""Exact current-byte alternatives for the recorded attribution-only correction.

Historical source IDs remain unchanged in existing receipts. This allowlist
admits only the explicitly reviewed current bytes, not arbitrary source drift.
"""

from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RECORD = ROOT / "docs/AUTHORSHIP_BYTES.json"


def matches_source_bytes(content: bytes, historical_digest: str) -> bool:
    actual = sha256(content).hexdigest()
    if actual == historical_digest:
        return True
    return any(
        row["historical_sha256"] == historical_digest
        and row["current_sha256"] == actual
        for row in json.loads(RECORD.read_text())["artifacts"]
    )


def current_blob_sha(path: str, historical_blob: str) -> str:
    for row in json.loads(RECORD.read_text())["artifacts"]:
        if row["path"] == path and row["historical_git_blob_sha"] == historical_blob:
            return row["current_git_blob_sha"]
    return historical_blob
