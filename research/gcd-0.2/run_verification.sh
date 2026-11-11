#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 test_gcd02.py --json-report evidence/conformance_run.json
python3 make_evidence.py
python3 replay_all.py evidence/end_to_end_receipts.json evidence/negative_receipts.json
printf '\nFirst-party verification complete. Check SHA256SUMS.txt against the exact delivered snapshot if needed.\n'
