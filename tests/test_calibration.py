from pamir.calibration import build_calibration_report


def test_clean_log_calibration_report():
    report = {
        "sample_count": 91052,
        "signals_analyzed": 475,
        "raw_deviation_count": 35,
        "root_event": None,
        "failure_chain": [],
        "conclusion": "no_deviation_detected",
    }

    calibration = build_calibration_report(report)

    assert calibration["calibration_version"] == "0.2"
    assert calibration["sample_count"] == 91052
    assert calibration["signals_analyzed"] == 475
    assert calibration["raw_deviation_count"] == 35

    assert calibration["material_root_present"] is False
    assert calibration["root_signal"] is None
    assert calibration["root_confidence"] is None
    assert calibration["failure_chain_length"] == 0

    assert calibration["source_conclusion"] == "no_deviation_detected"

    assert calibration["raw_deviation_rate"] == 35 / 91052
    assert calibration["deviations_per_10k_samples"] == (35 / 91052) * 10000
    assert calibration["deviations_per_signal"] == 35 / 475


def test_calibration_does_not_mutate_source_report():
    report = {
        "sample_count": 100,
        "signals_analyzed": 10,
        "raw_deviation_count": 2,
        "root_event": None,
        "failure_chain": [],
        "conclusion": "no_deviation_detected",
    }

    original = dict(report)

    build_calibration_report(report)

    assert report == original


def test_zero_counts_are_safe():
    calibration = build_calibration_report(
        {
            "sample_count": 0,
            "signals_analyzed": 0,
            "raw_deviation_count": 0,
            "root_event": None,
            "failure_chain": [],
            "conclusion": "no_deviation_detected",
        }
    )

    assert calibration["raw_deviation_rate"] == 0.0
    assert calibration["deviations_per_10k_samples"] == 0.0
    assert calibration["deviations_per_signal"] == 0.0

