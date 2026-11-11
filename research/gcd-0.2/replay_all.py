#!/usr/bin/env python3
"""Deterministically recompute the delivered GCD/0.2 receipts."""
import json
from pathlib import Path
import sys
import gcd02 as g

HERE = Path(__file__).resolve().parent
DATA = HERE / "evidence"


def replay_example(path):
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    good = {}
    for name, receipt in obj["stages"].items():
        good[name] = {"valid": g.verify_receipt(receipt), "status": receipt["outcome"]["status"],
                      "digest": receipt["digest_sha256"]}
    return good


def replay_negative(path):
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    good = {}
    for item in obj["negative_cases"]:
        r = item["receipt"]
        good[item["case"]] = {"valid": g.verify_receipt(r),
                              "expected_status": item["expected_status"],
                              "actual_status": r["outcome"]["status"],
                              "status_matches": item["expected_status"] == r["outcome"]["status"]}
    return good


def main():
    example = replay_example(sys.argv[1] if len(sys.argv) > 1 else DATA / "end_to_end_receipts.json")
    negative = replay_negative(sys.argv[2] if len(sys.argv) > 2 else DATA / "negative_receipts.json")
    passed = all(v["valid"] for v in example.values()) and all(v["valid"] and v["status_matches"]
                                                          for v in negative.values())
    result = {"profile": g.PROFILE, "model": g.MODEL, "passed": passed,
              "end_to_end_receipts_checked": len(example),
              "expected_negative_receipts_checked": len(negative),
              "end_to_end": example, "negative": negative,
              "scope": "first-party deterministic interpreter replay; not independent implementation or authenticated history"}
    print(json.dumps(result, indent=2, sort_keys=True))
    (DATA / "replay_report.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                                               encoding="utf-8")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
