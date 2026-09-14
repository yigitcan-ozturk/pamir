from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CalibrationBin:
    lower: float
    upper: float
    empirical_pass_rate: float
    sample_count: int

    def contains(self, raw_confidence: float) -> bool:
        return self.lower <= raw_confidence <= self.upper


@dataclass(frozen=True)
class CalibrationProfile:
    version: str
    dataset_id: str
    dataset_sha256: str
    bins: tuple[CalibrationBin, ...]


def calibrate_forensic_confidence(
    raw_confidence: float,
    profile: CalibrationProfile,
    *,
    min_bin_samples: int = 2,
) -> dict[str, Any]:
    """Map a raw v0.1 anomaly-strength heuristic to benchmark evidence.

    The returned empirical score is not a probability of causation. If the
    applicable benchmark bin has insufficient support, PAMIR reports an explicit
    uncalibrated fallback instead of fabricating precision.
    """
    if not 0.0 <= raw_confidence <= 1.0:
        raise ValueError("raw_confidence must be between 0 and 1")
    if min_bin_samples < 1:
        raise ValueError("min_bin_samples must be at least 1")

    matched = next((item for item in profile.bins if item.contains(raw_confidence)), None)
    provenance = {
        "profile_version": profile.version,
        "dataset_id": profile.dataset_id,
        "dataset_sha256": profile.dataset_sha256,
        "min_bin_samples": min_bin_samples,
    }
    if matched is None:
        return {
            "status": "uncalibrated",
            "raw_confidence": raw_confidence,
            "empirical_score": None,
            "support_count": 0,
            "reason": "no_matching_calibration_bin",
            "provenance": provenance,
        }
    if matched.sample_count < min_bin_samples:
        return {
            "status": "uncalibrated",
            "raw_confidence": raw_confidence,
            "empirical_score": None,
            "support_count": matched.sample_count,
            "reason": "insufficient_calibration_support",
            "provenance": provenance,
        }
    if not 0.0 <= matched.empirical_pass_rate <= 1.0:
        raise ValueError("empirical_pass_rate must be between 0 and 1")

    return {
        "status": "calibrated",
        "raw_confidence": raw_confidence,
        "empirical_score": round(matched.empirical_pass_rate, 3),
        "support_count": matched.sample_count,
        "reason": "benchmark_empirical_bin",
        "bin": {"lower": matched.lower, "upper": matched.upper},
        "provenance": provenance,
        "interpretation": "empirical benchmark support; not probability of causation",
    }
