from pamir.engine import build_report, detect_deviations
from pamir.model import Sample


def test_first_deviation_is_identified_with_rolling_baseline():
    samples = [Sample(i * 100_000, "battery.voltage", 12.0 + (0.01 if i % 2 else 0)) for i in range(40)]
    samples += [
        Sample(4_000_000, "battery.voltage", 9.0),
        Sample(4_100_000, "battery.voltage", 8.9),
    ]
    deviations = detect_deviations(samples)
    assert deviations
    assert deviations[0].timestamp_us == 4_000_000
    assert deviations[0].signal == "battery.voltage"
    assert deviations[0].confidence >= 0.5
    assert deviations[0].evidence_start_us == 3_500_000
    assert deviations[0].evidence_end_us == 4_100_000


def test_report_no_deviation():
    samples = [Sample(i * 100_000, "x", 10.0) for i in range(50)]
    report = build_report(samples, "fixture")
    assert report["conclusion"] == "no_deviation_detected"
    assert report["first_deviation"] is None


def test_accuracy_improvement_is_not_treated_as_failure():
    samples = [Sample(i * 100_000, "estimator_status.pos_horiz_accuracy", 0.05) for i in range(40)]
    samples += [Sample(4_000_000, "estimator_status.pos_horiz_accuracy", 0.02)]
    deviations = detect_deviations(samples)
    assert not deviations


def test_accuracy_degradation_is_detected():
    samples = [Sample(i * 100_000, "estimator_status.pos_vert_accuracy", 0.10) for i in range(40)]
    samples += [Sample(4_000_000, "estimator_status.pos_vert_accuracy", 0.30)]
    deviations = detect_deviations(samples)
    assert deviations
    assert deviations[0].signal == "estimator_status.pos_vert_accuracy"


def test_failure_chain_marks_likely_causal_transition():
    samples = []
    for i in range(40):
        ts = i * 100_000
        samples.extend([
            Sample(ts, "battery.voltage", 12.0),
            Sample(ts, "motor.output", 0.50),
            Sample(ts, "vehicle.attitude.roll", 0.0),
            Sample(ts, "vehicle.position.altitude", 100.0),
        ])

    samples.extend([
        Sample(4_000_000, "battery.voltage", 8.0),
        Sample(4_200_000, "motor.output", 0.95),
        Sample(4_400_000, "vehicle.attitude.roll", 0.7),
        Sample(4_600_000, "vehicle.position.altitude", 85.0),
    ])

    report = build_report(samples, "causal-fixture")
    chain = report["failure_chain"]
    assert [item["signal"] for item in chain[:4]] == [
        "battery.voltage",
        "motor.output",
        "vehicle.attitude.roll",
        "vehicle.position.altitude",
    ]
    assert chain[1]["relation"] == "likely_caused"
    assert chain[1]["parent_signal"] == "battery.voltage"
    assert chain[2]["relation"] == "likely_caused"
    assert chain[3]["relation"] == "likely_caused"


def test_multi_axis_rate_command_discontinuity_can_root_before_attitude_and_motion():
    samples = []
    for i in range(40):
        ts = i * 100_000
        samples.extend([
            Sample(ts, "vehicle_rates_setpoint.roll", 0.0),
            Sample(ts, "vehicle_rates_setpoint.pitch", 0.0),
            Sample(ts, "vehicle_rates_setpoint.yaw", 0.0),
            Sample(ts, "vehicle_attitude.q[1]", 0.0),
            Sample(ts, "vehicle_local_position.vx", 0.0),
        ])
    samples.extend([
        Sample(4_000_000, "vehicle_rates_setpoint.roll", 1.4),
        Sample(4_050_000, "vehicle_rates_setpoint.pitch", -1.2),
        Sample(4_100_000, "vehicle_rates_setpoint.yaw", 0.1),
        Sample(4_300_000, "vehicle_attitude.q[1]", 0.6),
        Sample(4_500_000, "vehicle_local_position.vx", 8.0),
    ])
    report = build_report(samples, "control-discontinuity")
    assert report["root_event"] is not None
    assert report["root_event"]["reason"] == "multi_axis_rate_command_discontinuity"
    assert report["root_event"]["signal"] in {
        "vehicle_rates_setpoint.roll", "vehicle_rates_setpoint.pitch"
    }


def test_single_axis_rate_command_change_is_not_root_proof():
    samples = []
    for i in range(40):
        ts = i * 100_000
        samples.extend([
            Sample(ts, "vehicle_rates_setpoint.roll", 0.0),
            Sample(ts, "vehicle_rates_setpoint.pitch", 0.0),
            Sample(ts, "vehicle_attitude.q[1]", 0.0),
            Sample(ts, "vehicle_local_position.vx", 0.0),
        ])
    samples.extend([
        Sample(4_000_000, "vehicle_rates_setpoint.roll", 1.5),
        Sample(4_300_000, "vehicle_attitude.q[1]", 0.6),
        Sample(4_500_000, "vehicle_local_position.vx", 8.0),
    ])
    assert build_report(samples, "single-axis-command")["root_event"] is None


def test_simultaneous_events_are_not_causal():
    from pamir.engine import _relation
    from pamir.model import Deviation
    a = Deviation(10, "battery.voltage", 8, 12, 10, .8, 0, 10, "test")
    b = Deviation(10, "motor.output", 0, 1, 10, .8, 0, 10, "test")
    assert _relation(a, b, 100)[0] == "followed_by"


def test_nonfinite_samples_do_not_poison_baseline():
    points = [Sample(i * 100000, "battery.voltage", 12) for i in range(40)]
    points += [Sample(3900001, "battery.voltage", float("nan")), Sample(4000000, "battery.voltage", 8)]
    assert detect_deviations(points)[0].baseline == 12


def test_timing_metadata_is_not_a_root_candidate():
    points = [Sample(i * 100000, "sensor_combined.gyro_integral_dt", 1000) for i in range(40)]
    points.append(Sample(4000000, "sensor_combined.gyro_integral_dt", 5000))
    assert detect_deviations(points) == []


def test_estimator_position_accuracy_is_estimation_family():
    from pamir.engine import _signal_family
    assert _signal_family("estimator_status.pos_vert_accuracy") == "estimation"
    assert _signal_family("vehicle_rates_setpoint.roll") == "control"
