from __future__ import annotations

from typing import Any, Mapping


def build_calibration_report(report: Mapping[str, Any]) -> dict[str, Any]:
    """
    Derive PAMIR v0.2 calibration metrics from a frozen v0.1 report.

    This layer is measurement-only:
    - it must not mutate the input report;
    - it must not change v0.1 root selection;
    - it must not change the v0.1 conclusion.
    """

    sample_count = int(report.get("sample_count", 0) or 0)
    signals_analyzed = int(report.get("signals_analyzed", 0) or 0)
    raw_deviation_count = int(report.get("raw_deviation_count", 0) or 0)

    root_event = report.get("root_event")
    failure_chain = report.get("failure_chain") or []

    raw_deviation_rate = (
        raw_deviation_count / sample_count
        if sample_count > 0
        else 0.0
    )

    deviations_per_10k_samples = raw_deviation_rate * 10_000

    deviations_per_signal = (
        raw_deviation_count / signals_analyzed
        if signals_analyzed > 0
        else 0.0
    )

    material_root_present = root_event is not None

    root_signal = None
    root_confidence = None

    if isinstance(root_event, Mapping):
        root_signal = root_event.get("signal")
        root_confidence = root_event.get("confidence")

    return {
        "calibration_version": "0.2",
        "sample_count": sample_count,
        "signals_analyzed": signals_analyzed,
        "raw_deviation_count": raw_deviation_count,
        "raw_deviation_rate": raw_deviation_rate,
        "deviations_per_10k_samples": deviations_per_10k_samples,
        "deviations_per_signal": deviations_per_signal,
        "material_root_present": material_root_present,
        "root_signal": root_signal,
        "root_confidence": root_confidence,
        "failure_chain_length": len(failure_chain),
        "source_conclusion": report.get("conclusion"),
    }
