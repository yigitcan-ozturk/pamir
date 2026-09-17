from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .engine import build_report, detect_deviations
from .model import Sample


@dataclass(frozen=True)
class DetectorVariant:
    name: str
    threshold: float = 7.0
    min_baseline_points: int = 30
    baseline_window_us: int = 10_000_000
    evidence_before_us: int = 500_000
    evidence_after_us: int = 750_000

    def detector_kwargs(self) -> dict[str, int | float]:
        return {
            "threshold": self.threshold,
            "min_baseline_points": self.min_baseline_points,
            "baseline_window_us": self.baseline_window_us,
            "evidence_before_us": self.evidence_before_us,
            "evidence_after_us": self.evidence_after_us,
        }


DEFAULT_VARIANTS: tuple[DetectorVariant, ...] = (
    DetectorVariant("baseline"),
    DetectorVariant("threshold_low", threshold=6.5),
    DetectorVariant("threshold_high", threshold=7.5),
    DetectorVariant("history_short", baseline_window_us=8_000_000),
    DetectorVariant("history_long", baseline_window_us=12_000_000),
    DetectorVariant("prior_points_low", min_baseline_points=25),
    DetectorVariant("prior_points_high", min_baseline_points=35),
    DetectorVariant("evidence_narrow", evidence_before_us=400_000, evidence_after_us=600_000),
    DetectorVariant("evidence_wide", evidence_before_us=750_000, evidence_after_us=1_000_000),
)


def _root_identity(root: dict[str, Any] | None) -> tuple[str, str] | None:
    if root is None:
        return None
    return str(root["signal"]), str(root["reason"])


def measure_root_stability(
    samples: list[Sample],
    source: str,
    *,
    variants: tuple[DetectorVariant, ...] = DEFAULT_VARIANTS,
    timestamp_tolerance_us: int = 250_000,
) -> dict[str, Any]:
    """Measure root-selection stability under bounded detector perturbations.

    This utility is intentionally outside the v0.1 detector. It does not tune or
    mutate detector defaults; it replays the same samples through explicitly named
    variants and reports whether the selected forensic root is preserved.

    v0.2 distinguishes a raw candidate root from a qualified material root. A root
    is qualified only when the frozen baseline selects it and every bounded replay
    preserves the same signal/reason within the timestamp tolerance. Candidate
    emergence is retained in the report as instability; it is never silently
    promoted to a causal/material claim merely because one perturbation selected it.
    """
    if not variants:
        raise ValueError("at least one detector variant is required")
    if timestamp_tolerance_us < 0:
        raise ValueError("timestamp_tolerance_us must be non-negative")

    runs: list[dict[str, Any]] = []
    for variant in variants:
        deviations = detect_deviations(samples, **variant.detector_kwargs())
        report = build_report(samples, source, deviations=deviations)
        root = report["root_event"]
        runs.append({
            "variant": variant.name,
            "parameters": variant.detector_kwargs(),
            "root_event": root,
            "root_identity": list(_root_identity(root)) if root is not None else None,
            "failure_chain": report["failure_chain"],
        })

    baseline = runs[0]["root_event"]
    baseline_identity = _root_identity(baseline)
    matching = 0
    for run in runs:
        root = run["root_event"]
        same_identity = _root_identity(root) == baseline_identity
        if baseline is None and root is None:
            timestamp_stable = True
        elif baseline is None or root is None:
            timestamp_stable = False
        else:
            timestamp_stable = abs(int(root["timestamp_us"]) - int(baseline["timestamp_us"])) <= timestamp_tolerance_us
        stable = same_identity and timestamp_stable
        run["matches_baseline_root"] = stable
        if stable:
            matching += 1

    ratio = matching / len(runs)
    candidate_root_variants = [run["variant"] for run in runs if run["root_event"] is not None]
    qualified_material_root = baseline if baseline is not None and matching == len(runs) else None

    if baseline is None:
        status = "stable_no_root" if matching == len(runs) else "unstable_root_emergence"
    else:
        status = "stable" if matching == len(runs) else "unstable"

    return {
        "schema_version": "0.2-root-stability-v2",
        "source": source,
        "variant_count": len(runs),
        "timestamp_tolerance_us": timestamp_tolerance_us,
        "baseline_root": baseline,
        "qualified_material_root": qualified_material_root,
        "qualification_policy": "baseline root must be preserved by every bounded detector variant",
        "candidate_root_variants": candidate_root_variants,
        "matching_variant_count": matching,
        "stability_ratio": round(ratio, 3),
        "status": status,
        "runs": runs,
    }
