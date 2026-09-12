#!/usr/bin/env python3
import json
from math import isfinite
from pathlib import Path

from pamir.engine import build_report, detect_deviations
from pamir.ingest import load

ROOT = Path(__file__).resolve().parents[1]
REPRO_MANIFEST = ROOT / "benchmarks" / "px4_reproducible_incidents.json"
LEGACY_MANIFEST = ROOT / "benchmarks" / "px4_public_incidents.json"
DATA = ROOT / "benchmarks" / "data"
OUT = ROOT / "benchmarks" / "reports"


def validate_report(report: dict, samples: list) -> list[str]:
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


def _event_signal(event) -> str:
    return event["signal"] if isinstance(event, dict) else event.signal


def _event_time(event) -> int:
    return event["timestamp_us"] if isinstance(event, dict) else event.timestamp_us


def compare_pair(crash: dict, control: dict) -> list[str]:
    errors = []
    if crash.get("root_event") is None:
        errors.append("incident has no material root")
    if control.get("root_event") is not None:
        errors.append("non-crash control has a material failure chain")
    return errors


def validate_causal_timestamps(report: dict, metadata: dict, deviations: list | None = None) -> list[str]:
    errors = []
    root = report.get("root_event")
    if root is None:
        return ["incident has no timestamped root event"]

    expected_root = metadata.get("expected_root_family")
    root_family = _family(root["signal"])
    if expected_root and root_family != expected_root:
        errors.append(f"root family {root_family} does not match expected {expected_root}")

    root_t = root["timestamp_us"]
    causal_window_us = int(metadata.get("causal_window_us", 3_000_000))
    source_events = deviations if deviations is not None else report.get("failure_chain", [])[1:]
    downstream = [event for event in source_events if root_t < _event_time(event) <= root_t + causal_window_us]
    downstream_families = {_family(_event_signal(event)) for event in downstream}
    for required in metadata.get("required_downstream_families", []):
        if required not in downstream_families:
            errors.append(f"missing strictly downstream {required} evidence within {causal_window_us}us")

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


def analyze(path: Path, metadata: dict) -> tuple[dict, list]:
    samples = load(path)
    if not samples:
        raise RuntimeError(f"{path.name}: parsed zero telemetry samples")
    deviations = detect_deviations(samples)
    report = build_report(samples, str(path), deviations=deviations)
    report.update(metadata)
    report["validation_errors"] = validate_report(report, samples)
    output = OUT / f"{path.stem}.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    root = report["root_event"]
    root_label = root["signal"] if root else "none"
    root_conf = root["confidence"] if root else 0.0
    print(
        f"{path.stem}: samples={report['sample_count']} signals={report['signals_analyzed']} "
        f"raw_deviations={len(deviations)} conclusion={report['conclusion']} "
        f"root={root_label} confidence={root_conf} chain={len(report['failure_chain'])}"
    )
    return report, deviations


def summary_row(case: dict, report: dict, causal_errors: list[str]) -> dict:
    root = report["root_event"]
    return {
        "id": case["id"], "kind": case["kind"], "source_url": case.get("source_url"),
        "samples": report["sample_count"], "signals": report["signals_analyzed"],
        "conclusion": report["conclusion"], "root_event": root,
        "root_confidence": root["confidence"] if root else 0.0,
        "root_score": root["score"] if root else 0.0,
        "chain_length": len(report["failure_chain"]),
        "timestamp_causal_errors": causal_errors,
    }


def main() -> None:
    manifest = json.loads(REPRO_MANIFEST.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    errors = []
    summary = []
    reports = {}

    incidents = [case for case in manifest["cases"] if case["kind"] == "incident"]
    controls = [case for case in manifest["cases"] if case["kind"] == "control"]
    if len(incidents) < 5:
        errors.append(f"benchmark corpus has only {len(incidents)} incidents; five required")
    if not controls:
        errors.append("benchmark corpus has no healthy/control cases")

    for case in manifest["cases"]:
        path = DATA / f"{case['id']}.ulg"
        if not path.exists():
            errors.append(f"required benchmark ULog missing: {case['id']}")
            continue
        report, deviations = analyze(path, case)
        reports[case["id"]] = report
        case_errors = list(report["validation_errors"])
        if case["kind"] == "incident":
            if report["root_event"] is None:
                case_errors.append("incident has no material root")
            else:
                case_errors.extend(validate_causal_timestamps(report, case, deviations))
        elif case["kind"] == "control":
            if report["root_event"] is not None:
                case_errors.append("healthy/control log has a material failure chain")
        else:
            case_errors.append(f"unknown benchmark kind: {case['kind']}")
        errors.extend(f"{case['id']}: {error}" for error in case_errors)
        summary.append(summary_row(case, report, case_errors))

    if "github-indoor-crash-2025" in reports and "github-indoor-control-2025" in reports:
        errors.extend(
            "github-indoor-pair: " + error
            for error in compare_pair(reports["github-indoor-crash-2025"], reports["github-indoor-control-2025"])
        )

    fallback = DATA / "px4-pyulog-sample.ulg"
    if not fallback.exists():
        errors.append("missing pinned public PX4/pyulog parser sample")
    else:
        parser_case = {
            "id": "px4-pyulog-sample", "kind": "parser-control",
            "validation_goal": "Prove real binary PX4 ULog ingestion and forensic pipeline execution.",
        }
        parser_report, _ = analyze(fallback, parser_case)
        errors.extend(f"px4-pyulog-sample: {error}" for error in parser_report["validation_errors"])

    legacy = json.loads(LEGACY_MANIFEST.read_text(encoding="utf-8"))
    unavailable_legacy = [case["id"] for case in legacy["cases"] if not (DATA / f"{case['id']}.ulg").exists()]

    passed = not errors
    payload = {
        "v0_1_complete": passed, "validation_passed": passed,
        "validation_errors": errors, "required_incident_count": len(incidents),
        "required_control_count": len(controls), "validated": summary,
        "legacy_flight_review_sources_unavailable": unavailable_legacy,
        "legacy_flight_review_note": "Extended corpus only; the v0.1 gate uses directly accessible public GitHub ULogs.",
    }
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"required corpus: {len(incidents)} incident(s), {len(controls)} control(s), validated={len(summary)}")
    if unavailable_legacy:
        print("OPTIONAL Flight Review corpus unavailable: " + ", ".join(unavailable_legacy))
    if errors:
        raise SystemExit("VALIDATION FAILED: " + "; ".join(errors))
    print("PAMIR v0.1 REPRODUCIBLE VALIDATION GATE PASSED")


if __name__ == "__main__":
    main()
