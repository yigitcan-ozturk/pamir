#!/usr/bin/env python3
import json
from pathlib import Path

from pamir.engine import build_report
from pamir.ingest import load

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "benchmarks" / "px4_public_incidents.json"
DATA = ROOT / "benchmarks" / "data"
OUT = ROOT / "benchmarks" / "reports"

PORTABLE_CASES = (
    {
        "id": "github-indoor-crash-2025",
        "kind": "incident",
        "known_narrative": "Indoor offboard takeoff attempt drifted diagonally and crashed into a wall; the public issue reports rapidly degrading position/attitude estimates.",
        "validation_goal": "Surface the earliest material telemetry deviation before downstream attitude/position consequences.",
    },
    {
        "id": "github-indoor-control-2025",
        "kind": "control",
        "known_narrative": "Companion public ULog from the same hardware/testing context that did not crash.",
        "validation_goal": "Provide a directly downloadable control for comparing false-positive severity against the crash flight.",
    },
)


def analyze(path: Path, metadata: dict) -> dict:
    samples = load(path)
    if not samples:
        raise RuntimeError(f"{path.name}: parsed zero telemetry samples")
    report = build_report(samples, str(path))
    report.update(metadata)
    output = OUT / f"{path.stem}.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    root = report["root_event"]
    root_label = root["signal"] if root else "none"
    root_conf = root["confidence"] if root else 0.0
    print(
        f"{path.stem}: samples={report['sample_count']} "
        f"signals={report['signals_analyzed']} conclusion={report['conclusion']} "
        f"root={root_label} confidence={root_conf} chain={len(report['failure_chain'])}"
    )
    return report


def summary_row(case_id: str, kind: str, report: dict) -> dict:
    root = report["root_event"]
    return {
        "id": case_id,
        "kind": kind,
        "samples": report["sample_count"],
        "signals": report["signals_analyzed"],
        "conclusion": report["conclusion"],
        "root_event": root,
        "root_confidence": root["confidence"] if root else 0.0,
        "root_score": root["score"] if root else 0.0,
        "chain_length": len(report["failure_chain"]),
    }


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
        summary.append(summary_row(case["id"], case["kind"], report))

    portable_reports = {}
    for case in PORTABLE_CASES:
        path = DATA / f"{case['id']}.ulg"
        if not path.exists():
            raise FileNotFoundError(f"missing portable benchmark ULog: {case['id']}")
        report = analyze(path, {
            "benchmark_case": case["id"],
            "benchmark_kind": case["kind"],
            "known_narrative": case["known_narrative"],
            "validation_goal": case["validation_goal"],
        })
        portable_reports[case["id"]] = report
        summary.append(summary_row(case["id"], case["kind"], report))

    fallback = DATA / "px4-pyulog-sample.ulg"
    if not fallback.exists():
        raise FileNotFoundError("missing pinned public PX4/pyulog ULog fallback")
    report = analyze(fallback, {
        "benchmark_case": "px4-pyulog-sample",
        "benchmark_kind": "parser-control",
        "validation_goal": "Prove real binary PX4 ULog ingestion and forensic pipeline execution.",
    })
    summary.append(summary_row("px4-pyulog-sample", "parser-control", report))

    crash = portable_reports["github-indoor-crash-2025"]
    control = portable_reports["github-indoor-control-2025"]
    portable_comparison = {
        "crash_root": crash["root_event"],
        "control_root": control["root_event"],
        "crash_chain_length": len(crash["failure_chain"]),
        "control_chain_length": len(control["failure_chain"]),
        "crash_root_score": crash["root_event"]["score"] if crash["root_event"] else 0.0,
        "control_root_score": control["root_event"]["score"] if control["root_event"] else 0.0,
    }

    payload = {
        "validated": summary,
        "portable_incident_control_complete": True,
        "portable_comparison": portable_comparison,
        "flight_review_sources_unavailable": missing_incidents,
        "flight_review_validation_complete": len(missing_incidents) == 0,
    }
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"validated {len(summary)} public PX4 ULog(s)")
    print(
        "PORTABLE INCIDENT/CONTROL: "
        f"crash_root_score={portable_comparison['crash_root_score']} "
        f"control_root_score={portable_comparison['control_root_score']} "
        f"crash_chain={portable_comparison['crash_chain_length']} "
        f"control_chain={portable_comparison['control_chain_length']}"
    )
    if missing_incidents:
        print("FLIGHT REVIEW SOURCE GATE OPEN (external 403): " + ", ".join(missing_incidents))


if __name__ == "__main__":
    main()
