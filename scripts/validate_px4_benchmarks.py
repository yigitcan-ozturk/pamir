#!/usr/bin/env python3
import json
import argparse
from math import isfinite
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


def validate_report(report: dict, samples: list) -> list[str]:
    """Check actual observations, not only serializable report shape."""
    errors = []
    chain = report["failure_chain"]
    if report["root_event"] != (chain[0] if chain else None):
        errors.append("root does not match first chain event")
    previous = None
    for event in chain:
        t = event["timestamp_us"]
        start, end = event["evidence_start_us"], event["evidence_end_us"]
        points = [p for p in samples if p.signal == event["signal"] and isfinite(p.value)]
        if not points or not min(p.timestamp_us for p in points) <= start <= t <= end <= max(p.timestamp_us for p in points):
            errors.append(f"{event['signal']}: evidence outside observed signal")
        if not any(p.timestamp_us == t and p.value == event["value"] for p in points):
            errors.append(f"{event['signal']}: missing event observation")
        if not isfinite(event["confidence"]) or not 0.5 <= event["confidence"] <= 0.999:
            errors.append("invalid confidence")
        if previous is None:
            if event["parent_signal"] is not None or event["relation"] is not None:
                errors.append("root has a parent")
        else:
            if t < previous["timestamp_us"] or event["parent_signal"] != previous["signal"]:
                errors.append("invalid parent/order")
            if event["relation"] not in {"likely_caused", "followed_by"}:
                errors.append("invalid relationship")
            if event["relation"] == "likely_caused" and not 0 < t - previous["timestamp_us"] <= 3_000_000:
                errors.append("causal link lacks strictly preceding nearby parent")
        previous = event
    return errors


def compare_pair(crash: dict, control: dict) -> list[str]:
    errors = []
    if crash["root_event"] is None:
        errors.append("incident has no material root")
    # Predeclared conservative gate: a non-crash flight must not receive a
    # material failure chain. Do not tune this threshold to observed outputs.
    if control["root_event"] is not None:
        errors.append("non-crash control has a material failure chain")
    return errors


def analyze(path: Path, metadata: dict) -> dict:
    samples = load(path)
    if not samples:
        raise RuntimeError(f"{path.name}: parsed zero telemetry samples")
    report = build_report(samples, str(path))
    report.update(metadata)
    report["validation_errors"] = validate_report(report, samples)
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--portable-only", action="store_true", help="Explicitly limit source coverage; does not certify v0.1 completion")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    summary = []
    missing_incidents = []
    errors = []

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
        errors.extend(report["validation_errors"])
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
        errors.extend(report["validation_errors"])
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

    errors.extend(report["validation_errors"])
    errors.extend(compare_pair(crash, control))
    if missing_incidents and not args.portable_only:
        errors.append("required Flight Review cases missing: " + ", ".join(missing_incidents))
    # Public descriptions do not provide timestamped event-order annotations.
    # Passing transport/schema checks cannot certify narrative agreement.
    narrative_status = "unverified_missing_timestamped_annotations"
    if not args.portable_only:
        errors.append("incident narrative ordering has no reviewed timestamped annotations")
    payload = {
        "narrative_validation": narrative_status,
        "v0_1_complete": False,
        "validation_errors": errors,
        "validation_passed": not errors,
        "validated": summary,
        "portable_incident_control_complete": False,
        "portable_control_gate_passed": not compare_pair(crash, control),
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
    if errors:
        raise SystemExit("VALIDATION FAILED: " + "; ".join(errors))
    if missing_incidents:
        print("FLIGHT REVIEW SOURCE GATE OPEN (external 403): " + ", ".join(missing_incidents))


if __name__ == "__main__":
    main()
