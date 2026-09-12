import pytest

from pamir.model import Sample
from pamir.stability import DetectorVariant, measure_root_stability


def _battery_drop_fixture() -> list[Sample]:
    samples = [Sample(i * 100_000, "battery.voltage", 12.0) for i in range(40)]
    samples.append(Sample(4_000_000, "battery.voltage", 8.0))
    return samples


def test_material_root_is_stable_across_default_bounded_variants():
    result = measure_root_stability(_battery_drop_fixture(), "battery-drop")

    assert result["schema_version"] == "0.2-root-stability-v1"
    assert result["baseline_root"] is not None
    assert result["baseline_root"]["signal"] == "battery.voltage"
    assert result["status"] == "stable"
    assert result["stability_ratio"] == 1.0
    assert result["matching_variant_count"] == result["variant_count"]
    assert all(run["matches_baseline_root"] for run in result["runs"])


def test_healthy_control_reports_stable_no_root():
    samples = [Sample(i * 100_000, "battery.voltage", 12.0) for i in range(60)]
    result = measure_root_stability(samples, "healthy-control")

    assert result["baseline_root"] is None
    assert result["status"] == "stable_no_root"
    assert result["stability_ratio"] == 1.0


def test_sensitivity_analysis_exposes_root_instability_instead_of_hiding_it():
    samples = []
    for i in range(40):
        ts = i * 100_000
        samples.extend([
            Sample(ts, "battery.voltage", 12.0),
            Sample(ts, "vehicle.attitude.roll", 0.0),
            Sample(ts, "vehicle.position.altitude", 100.0),
        ])
    samples.extend([
        Sample(4_000_000, "battery.voltage", 11.5),
        Sample(4_200_000, "vehicle.attitude.roll", 0.7),
        Sample(4_400_000, "vehicle.position.altitude", 85.0),
    ])
    variants = (
        DetectorVariant("baseline", threshold=7.0),
        DetectorVariant("strict", threshold=10.0),
    )

    result = measure_root_stability(samples, "borderline", variants=variants)

    assert result["baseline_root"] is not None
    assert result["baseline_root"]["signal"] == "battery.voltage"
    assert result["runs"][1]["root_event"] is None
    assert result["status"] == "unstable"
    assert result["stability_ratio"] == 0.5


def test_stability_requires_at_least_one_variant():
    with pytest.raises(ValueError, match="at least one detector variant"):
        measure_root_stability([], "empty", variants=())


def test_negative_timestamp_tolerance_is_rejected():
    with pytest.raises(ValueError, match="timestamp_tolerance_us"):
        measure_root_stability([], "empty", timestamp_tolerance_us=-1)
