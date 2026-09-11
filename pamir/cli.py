import argparse
import json
from pathlib import Path
from .engine import build_report
from .ingest import load


def main() -> None:
    parser = argparse.ArgumentParser(prog="pamir", description="Post-Mission Autonomous Incident Reconstruction")
    sub = parser.add_subparsers(dest="command", required=True)
    analyze = sub.add_parser("analyze", help="Analyze a PX4 .ulg or normalized .json log")
    analyze.add_argument("input")
    analyze.add_argument("--output", "-o", default="pamir-report.json")
    args = parser.parse_args()

    samples = load(args.input)
    report = build_report(samples, source=str(args.input))
    Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    first = report["first_deviation"]
    if first:
        print(f"FIRST DEVIATION: {first['signal']} @ {first['timestamp_us']} us (score={first['score']})")
    else:
        print("NO DEVIATION DETECTED")
    print(f"Report: {args.output}")

if __name__ == "__main__":
    main()
