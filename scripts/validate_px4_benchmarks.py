#!/usr/bin/env python3
import json
from pathlib import Path

from pamir.engine import build_report
from pamir.ingest import load

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "benchmarks" / "px4_public_incidents.json"
DATA = ROOT / "benchmarks" / "data"
OUT = ROOT / "benchmarks" / "reports"


def analyze(path: Path, metadata: dict) -> dict:
    samples = load(path)
    if not samples:
        raise RuntimeError(f"{path.name}: parsed zero telemetry samples")
    report = build_report(samples, str(path))
    report.update(metadata)
    output = OUT / f"{path.stem}.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        f"{path.stem}: samples={report['sample_count']} "
        f"signals={report['signals_analyzed']} conclusion={report['conclusion']}"
    )
    return report


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    summary = []
    missing_incidents = []

    for case in manifest["cases"]:
        path = DATA / f"{case['id']}.ulg"
        if not path.exists():
            missing_incidents.append(case["id"])
            print(f"SKIP source-unavailable: {case['id']}")
            continue
        report = analyze(path, {
            "benchmark_case": case["id"],
            "benchmark_kind": case["kind"],
            "known_narrative": case["known_narrative"],
            "validation_goal": case["validation_goal"],
        })
        summary.append({
            "id": case["id"], "kind": case["kind"],
            "samples": report["sample_count"], "signals": report["signals_analyzed"],
            "conclusion": report["conclusion"], "root_event": report["root_event"],
        })

    fallback = DATA / "px4-pyulog-sample.ulg"
    if not fallback.exists():
        raise FileNotFoundError("missing pinned public PX4/pyulog ULog fallback")
    report = analyze(fallback, {
        "benchmark_case": "px4-pyulog-sample",
        "benchmark_kind": "parser-control",
        "validation_goal": "Prove real binary PX4 ULog ingestion and forensic pipeline execution.",
    })
    summary.append({
        "id": "px4-pyulog-sample", "kind": "parser-control",
        "samples": report["sample_count"], "signals": report["signals_analyzed"],
        "conclusion": report["conclusion"], "root_event": report["root_event"],
    })

    payload = {
        "validated": summary,
        "incident_sources_unavailable": missing_incidents,
        "incident_validation_complete": len(missing_incidents) == 0,
    }
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"validated {len(summary)} available public PX4 ULog(s)")
    if missing_incidents:
        print("INCIDENT VALIDATION GATE OPEN: source access unavailable for " + ", ".join(missing_incidents))


if __name__ == "__main__":
    main()
