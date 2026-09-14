import pytest

from pamir.calibration import CalibrationBin, CalibrationProfile, calibrate_forensic_confidence


def _profile(*bins: CalibrationBin) -> CalibrationProfile:
    return CalibrationProfile(
        version="test-v1",
        dataset_id="calibration-fixture",
        dataset_sha256="a" * 64,
        bins=tuple(bins),
    )


def test_supported_bin_returns_empirical_score_with_provenance():
    result = calibrate_forensic_confidence(
        0.82,
        _profile(CalibrationBin(0.8, 0.9, 0.75, 4)),
    )

    assert result["status"] == "calibrated"
    assert result["empirical_score"] == 0.75
    assert result["support_count"] == 4
    assert result["provenance"]["dataset_id"] == "calibration-fixture"
    assert "not probability of causation" in result["interpretation"]


def test_insufficient_bin_support_falls_back_to_uncalibrated():
    result = calibrate_forensic_confidence(
        0.82,
        _profile(CalibrationBin(0.8, 0.9, 1.0, 1)),
        min_bin_samples=2,
    )

    assert result["status"] == "uncalibrated"
    assert result["empirical_score"] is None
    assert result["reason"] == "insufficient_calibration_support"


def test_missing_bin_falls_back_to_uncalibrated():
    result = calibrate_forensic_confidence(
        0.42,
        _profile(CalibrationBin(0.8, 0.9, 0.75, 4)),
    )

    assert result["status"] == "uncalibrated"
    assert result["reason"] == "no_matching_calibration_bin"


def test_invalid_raw_confidence_is_rejected():
    with pytest.raises(ValueError, match="raw_confidence"):
        calibrate_forensic_confidence(1.2, _profile())


def test_invalid_minimum_support_is_rejected():
    with pytest.raises(ValueError, match="min_bin_samples"):
        calibrate_forensic_confidence(0.8, _profile(), min_bin_samples=0)
