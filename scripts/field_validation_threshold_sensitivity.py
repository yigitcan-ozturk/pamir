#!/usr/bin/env python3
"""Corpus-v1 threshold sensitivity and false-root error analysis.

External field-validation harness only. Frozen PAMIR v0.1 source/configuration
is not modified. Candidate thresholds are passed to detect_deviations().
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from pamir.engine import _signal_family, build_report, detect_deviations
from pamir.ingest import load
from field_validation_batch import download, resolve, sha256

THRESHOLDS = (5.0, 6.0, 7.0, 8.0, 9.0, 10.0)
REFERENCE = 7.0


def label_of(case: dict) -> str:
    for key in ("classification", "independent_classification", "label"):
        value = case.get(key)
        if isinstance(value, str):
            v = value.lower().strip()
            if "healthy" in v or "control" in v:
                return "healthy_control"
            if "incident" in v:
                return "incident"
            if "unknown" in v:
                return "unknown"
    blob = json.dumps(case, sort_keys=True).lower()
    if "healthy_control" in blob:
        return "healthy_control"
    if '"incident"' in blob:
        return "incident"
    return "unknown"


def score_case(case: dict, cache: Path) -> dict:
    cid = case["case_id"]
    case_dir = cache / cid
    case_dir.mkdir(parents=True, exist_ok=True)
    ulg = case_dir / "input.ulg"
    expected = case.get("sha256")
    if not expected:
        raise RuntimeError(f"{cid}: accepted case has no pinned sha256")
    if not ulg.exists() or sha256(ulg).lower() != expected.lower():
        download(resolve(case["flight_review_uuid"]), ulg)
    actual = sha256(ulg)
    if actual.lower() != expected.lower():
        raise RuntimeError(f"{cid}: sha256 mismatch {actual} != {expected}")

    samples = load(ulg)
    runs = {}
    for threshold in THRESHOLDS:
        deviations = detect_deviations(samples, threshold=threshold)
        report = build_report(samples, source=cid, deviations=deviations)
        root = report["root_event"]
        runs[str(threshold)] = {
            "conclusion": report["conclusion"],
            "raw_deviation_count": report["raw_deviation_count"],
            "root_signal": root["signal"] if root else None,
            "root_family": _signal_family(root["signal"]) if root else None,
            "root_timestamp_us": root["timestamp_us"] if root else None,
            "root_score": root["score"] if root else None,
        }

    ref = runs[str(REFERENCE)]
    for threshold in THRESHOLDS:
        row = runs[str(threshold)]
        row["root_changed_vs_7"] = (
            row["root_signal"] != ref["root_signal"]
            or row["root_timestamp_us"] != ref["root_timestamp_us"]
        )
        row["root_timestamp_shift_us_vs_7"] = (
            row["root_timestamp_us"] - ref["root_timestamp_us"]
            if row["root_timestamp_us"] is not None
            and ref["root_timestamp_us"] is not None
            else None
        )

    return {
        "case_id": cid,
        "label": label_of(case),
        "sha256": actual,
        "thresholds": runs,
    }


def aggregate(results: list[dict]) -> dict:
    out = {}
    for threshold in THRESHOLDS:
        key = str(threshold)
        labelled = Counter(r["label"] for r in results)
        rooted = Counter(
            r["label"] for r in results
            if r["thresholds"][key]["root_signal"] is not None
        )
        healthy_n = labelled["healthy_control"]
        incident_n = labelled["incident"]
        unknown_n = labelled["unknown"]
        false_roots = rooted["healthy_control"]
        incident_roots = rooted["incident"]
        unknown_roots = rooted["unknown"]

        false_signals = Counter(
            r["thresholds"][key]["root_signal"] for r in results
            if r["label"] == "healthy_control"
            and r["thresholds"][key]["root_signal"] is not None
        )
        false_families = Counter(
            r["thresholds"][key]["root_family"] for r in results
            if r["label"] == "healthy_control"
            and r["thresholds"][key]["root_family"] is not None
        )
        out[key] = {
            "healthy_controls": healthy_n,
            "healthy_false_roots": false_roots,
            "healthy_false_root_rate": false_roots / healthy_n if healthy_n else None,
            "incidents": incident_n,
            "incident_roots": incident_roots,
            "incident_root_detection_rate": incident_roots / incident_n if incident_n else None,
            "unknown": unknown_n,
            "unknown_roots": unknown_roots,
            "unknown_root_rate": unknown_roots / unknown_n if unknown_n else None,
            "healthy_false_root_signals": dict(false_signals.most_common()),
            "healthy_false_root_families": dict(false_families.most_common()),
            "roots_changed_vs_7": sum(
                bool(r["thresholds"][key]["root_changed_vs_7"]) for r in results
            ),
        }
    return out


def markdown(summary: dict) -> str:
    lines = [
        "# Corpus v1 Threshold Sensitivity Results", "",
        "Frozen PAMIR v0.1 remains unchanged. Threshold 7.0 is the frozen reference.", "",
        "| threshold | healthy false roots | false-root rate | incident roots | incident root-detection | unknown roots | roots changed vs 7 |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for threshold in THRESHOLDS:
        row = summary[str(threshold)]
        lines.append(
            f"| {threshold:.1f} | {row['healthy_false_roots']}/{row['healthy_controls']} "
            f"| {row['healthy_false_root_rate']:.2%} "
            f"| {row['incident_roots']}/{row['incidents']} "
            f"| {row['incident_root_detection_rate']:.2%} "
            f"| {row['unknown_roots']}/{row['unknown']} "
            f"| {row['roots_changed_vs_7']} |"
        )
    lines += [
        "", "## Interpretation boundary", "",
        "These are sensitivity diagnostics, not calibrated causal-accuracy estimates. "
        "Healthy labels remain independent source labels; unknown cases remain unknown. "
        "No candidate threshold is promoted into frozen v0.1 by this report.", "",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="field-validation/corpus/manifest.json")
    ap.add_argument("--cache", default="field-validation/runtime/threshold-sensitivity")
    ap.add_argument("--output", default="field-validation/runtime/threshold-sensitivity-results.json")
    ap.add_argument("--summary", default="field-validation/runtime/threshold-sensitivity-summary.md")
    args = ap.parse_args()

    manifest = json.loads(Path(args.manifest).read_text())
    cases = [
        c for c in manifest["cases"]
        if c.get("acceptance_status") != "quarantined" and c.get("sha256")
    ]
    if len(cases) != 50:
        raise RuntimeError(f"Corpus v1 gate: expected 50 accepted pinned cases, found {len(cases)}")

    results = [score_case(case, Path(args.cache)) for case in cases]
    summary = aggregate(results)
    payload = {
        "experiment": "corpus-v1-threshold-sensitivity",
        "frozen_reference_threshold": REFERENCE,
        "candidate_thresholds": list(THRESHOLDS),
        "case_count": len(results),
        "cases": results,
        "aggregate": summary,
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(payload, indent=2) + "\n")
    Path(args.summary).write_text(markdown(summary) + "\n")
    print(markdown(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
