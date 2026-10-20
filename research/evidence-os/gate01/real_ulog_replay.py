"""Run frozen PAMIR v0.1 CLI twice on a pinned real PX4 ULog and compare stable forensic fields.

This is a separate research script; it does not modify the frozen engine.
Usage: python research/evidence-os/gate01/real_ulog_replay.py --ulog benchmarks/data/CASE.ulg --sha256 PINNED_SHA
"""
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

STABLE_FIELDS = ("root_event", "failure_chain", "first_deviation", "conclusion", "sample_count", "signals_analyzed")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ulog", required=True, type=Path)
    parser.add_argument("--sha256", required=True)
    args = parser.parse_args()
    if not args.ulog.is_file() or args.ulog.is_symlink():
        parser.error("missing or symlink input")
    if len(args.sha256) != 64 or any(c not in "0123456789abcdef" for c in args.sha256):
        parser.error("expected lowercase SHA-256")
    actual = hashlib.sha256(args.ulog.read_bytes()).hexdigest()
    if actual != args.sha256:
        parser.error("input SHA-256 mismatch")
    with tempfile.TemporaryDirectory() as td:
        outputs = []
        for i in range(2):
            output = Path(td) / f"run-{i}.json"
            subprocess.run([sys.executable, "-m", "pamir.cli", "analyze", str(args.ulog.resolve()), "-o", str(output)], check=True)
            report = json.loads(output.read_text(encoding="utf-8"))
            projection = {key: report.get(key) for key in STABLE_FIELDS}
            outputs.append(json.dumps(projection, sort_keys=True, separators=(",", ":"), allow_nan=False).encode())
        if outputs[0] != outputs[1]:
            raise SystemExit("REPLAY FAIL: stable forensic fields differ")
        print(json.dumps({"result": "PASS", "input_sha256": actual, "stable_fields_sha256": hashlib.sha256(outputs[0]).hexdigest(), "runs": 2}, sort_keys=True))

if __name__ == "__main__":
    main()
