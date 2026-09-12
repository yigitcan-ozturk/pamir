#!/usr/bin/env python3
import argparse
import json
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
        "validation_goal": "Surface an upstream estimation degradation before downstream vehicle-motion consequences.",
        "expected_root_family": "estimation",
        "required_downstream_families": ["attitude", "motion"],
    },
    {
        "id": "github-indoor-control-2025",
        "kind": "control",
        "known_narrative": "Companion public ULog from the same hardware/testing context that did not crash.",
        "validation_goal": "The control must not receive a material failure root/chain.",
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


def _family(signal: str) -> str:
    s = signal.lower()
    if "estimator" in s or "innovation" in s or "mag" in s:
        return "estimation"
    if "battery" in s or "voltage" in s or "current" in s:
        return "power"
    if "actuator" in s or "motor" in s or "output" in s or "thrust" in s:
        return "actuation"
    if "attitude" in s or "angular" in s or "gyro" in s:
        return "attitude"
    if "position" in s or "alt" in s or "velocity" in s or "gps" in s:
        return "motion"
    return "other"


def compare_pair(crash: dict, control: dict) -> list[str]:
    """Hard incident/control discrimination gate only."""
    errors = []
    if crash.get("root_event") is None:
        errors.append("incident has no material root")
    if control.get("root_event") is not None:
        errors.append("non-crash control has a material failure chain")
    return errors


def validate_causal_timestamps(report: dict, metadata: dict) -> list[str]:
    """Validate predeclared narrative semantics against telemetry timestamps.

    This does not claim calibrated causation. It requires the inferred root to be in the
    expected family and strictly precede the requested downstream consequences in the
    actual ULog clock. Any `likely_caused` edge must also be strictly ordered and inside
    the engine's three-second causal window.
    """
    errors = []
    root = report.get("root_event")
    if root is None:
        return ["incident has no timestamped root event"]

    expected_root = metadata.get("expected_root_family")
    if expected_root and _family(root["signal"]) != expected_root:
        errors.append(
            f"root family {_family(root['signal'])} does not match expected {expected_root}"
        )

    root_t = root["timestamp_us"]
    downstream = [event for event in report.get("failure_chain", [])[1:] if event["timestamp_us"] > root_t]
    downstream_families = {_family(event["signal"]) for event in downstream}
    for required in metadata.get("required_downstream_families", []):
        if required not in downstream_families:
            errors.append(f"missing strictly downstream {required} evidence")

    previous = root
    for event in report.get("failure_chain", [])[1:]:
        if event["timestamp_us"] < previous["timestamp_us"]:
            errors.append("failure chain timestamps are not monotonic")
        if event.get("relation") == "likely_caused":
            dt = event["timestamp_us"] - previous["timestamp_us"]
            if not 0 < dt <= 3_000_000:
                errors.append("likely_caused edge violates strict temporal window")
        previous = event
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
    parser.add_argument(
        "--require-flight-review",
        action="store_true",
        help="Also require the legacy logs.px4.io cases; cloud CI commonly receives HTTP 403 from that external service.",
    )
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    summary = []
    missing_flight_review = []
    errors = []

    for case in manifest["cases"]:
        path = DATA / f"{case['id']}.ulg"
        if not path.exists():
            missing_flight_review.append(case["id"])
            print(f"SKIP external-source-unavailable: {case['id']}")
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
    portable_metadata = {case["id"]: case for case in PORTABLE_CASES}
    for case in PORTABLE_CASES:
        path = DATA / f"{case['id']}.ulg"
        if not path.exists():
            raise FileNotFoundError(f"missing portable benchmark ULog: {case['id']}")
        report = analyze(path, case)
        portable_reports[case["id"]] = report
        errors.extend(report["validation_errors"])
        summary.append(summary_row(case["id"], case["kind"], report))

    fallback = DATA / "px4-pyulog-sample.ulg"
    if not fallback.exists():
        raise FileNotFoundError("missing pinned public PX4/pyulog ULog fallback")
    parser_report = analyze(fallback, {
        "benchmark_case": "px4-pyulog-sample",
        "benchmark_kind": "parser-control",
        "validation_goal": "Prove real binary PX4 ULog ingestion and forensic pipeline execution.",
    })
    errors.extend(parser_report["validation_errors"])
    summary.append(summary_row("px4-pyulog-sample", "parser-control", parser_report))

    crash = portable_reports["github-indoor-crash-2025"]
    control = portable_reports["github-indoor-control-2025"]
    pair_errors = compare_pair(crash, control)
    causal_errors = validate_causal_timestamps(
        crash, portable_metadata["github-indoor-crash-2025"]
    )
    errors.extend(pair_errors)
    errors.extend(causal_errors)

    if args.require_flight_review and missing_flight_review:
        errors.append("required Flight Review cases missing: " + ", ".join(missing_flight_review))

    portable_comparison = {
        "crash_root": crash["root_event"],
        "control_root": control["root_event"],
        "crash_chain_length": len(crash["failure_chain"]),
        "control_chain_length": len(control["failure_chain"]),
        "crash_root_score": crash["root_event"]["score"] if crash["root_event"] else 0.0,
        "control_root_score": control["root_event"]["score"] if control["root_event"] else 0.0,
    }

    passed = not errors
    payload = {
        "v0_1_complete": passed,
        "validation_passed": passed,
        "validation_errors": errors,
        "timestamp_causal_validation": "passed" if not causal_errors else "failed",
        "timestamp_causal_errors": causal_errors,
        "validated": summary,
        "portable_incident_control_complete": not pair_errors and not causal_errors,
        "portable_control_gate_passed": control["root_event"] is None,
        "portable_comparison": portable_comparison,
        "flight_review_sources_unavailable": missing_flight_review,
        "flight_review_validation_complete": len(missing_flight_review) == 0,
        "flight_review_note": "Legacy Flight Review cases remain an extended corpus; v0.1 merge gate is moving to five reproducible public incident ULogs hosted on accessible sources.",
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
    if missing_flight_review:
        print("OPTIONAL FLIGHT REVIEW CORPUS UNAVAILABLE FROM RUNNER (external 403): " + ", ".join(missing_flight_review))
    if errors:
        raise SystemExit("VALIDATION FAILED: " + "; ".join(errors))
    print("PAMIR v0.1 REPRODUCIBLE VALIDATION GATE PASSED")


if __name__ == "__main__":
    main()
