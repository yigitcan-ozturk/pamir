from pamir.engine import build_report, detect_deviations
from pamir.model import Sample


def test_first_deviation_is_identified():
    samples = [Sample(i, "x", 10 + (0.01 if i % 2 else 0)) for i in range(20)]
    samples += [Sample(20, "x", 14.0), Sample(21, "x", 14.2)]
    deviations = detect_deviations(samples)
    assert deviations
    assert deviations[0].timestamp_us == 20
    assert deviations[0].signal == "x"


def test_report_no_deviation():
    samples = [Sample(i, "x", 10.0) for i in range(25)]
    report = build_report(samples, "fixture")
    assert report["conclusion"] == "no_deviation_detected"
    assert report["first_deviation"] is None
