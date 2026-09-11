#!/usr/bin/env python3
import json
from pathlib import Path

from pamir.engine import build_report
from pamir.ingest import load

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "benchmarks" / "px4_public_incidents.json"
DATA = ROOT / "benchmarks" / "data"
OUT = ROOT / "benchmarks" / "reports"


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    summary = []

    for case in manifest["cases"]:
        path = DATA / f"{case['id']}.ulg"
        if not path.exists():
            raise FileNotFoundError(f"missing benchmark log: {path}")

        samples = load(path)
        report = build_report(samples, str(path))
        report["benchmark_case"] = case["id"]
        report["benchmark_kind"] = case["kind"]
        report["known_narrative"] = case["known_narrative"]
        report["validation_goal"] = case["validation_goal"]

        output = OUT / f"{case['id']}.json"
        output.write_text(json.dumps(report, indent=2), encoding="utf-8")
        summary.append({
            "id": case["id"],
            "kind": case["kind"],
            "samples": report["sample_count"],
            "signals": report["signals_analyzed"],
            "conclusion": report["conclusion"],
            "root_event": report["root_event"],
        })
        print(
            f"{case['id']}: samples={report['sample_count']} "
            f"signals={report['signals_analyzed']} conclusion={report['conclusion']}"
        )

    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"validated {len(summary)} public PX4 benchmark logs")


if __name__ == "__main__":
    main()
