from copy import deepcopy
from types import SimpleNamespace

import pytest

from pamir.engine import build_report, detect_deviations, _confidence
from pamir.ingest import load_ulog
from pamir.model import Sample
from scripts.download_px4_benchmarks import validate_ulog
from scripts.validate_px4_benchmarks import (
    validate_report,
    compare_pair,
    validate_causal_timestamps,
)


def fixture_report():
    samples = [Sample(i * 100000, 'battery.voltage', 12) for i in range(40)]
    samples.append(Sample(4000000, 'battery.voltage', 8))
    return samples, build_report(samples, 'fixture')


def test_evidence_can_be_replayed_and_validates():
    samples, report = fixture_report()
    assert validate_report(report, samples) == []
    assert report['evidence']['battery.voltage'][-1] == {'timestamp_us': 4000000, 'value': 8}


@pytest.mark.parametrize('key,value', [('confidence', float('nan')), ('evidence_end_us', 99999999), ('value', 999)])
def test_validator_rejects_corrupt_evidence(key, value):
    samples, report = fixture_report()
    report['failure_chain'][0][key] = value
    assert validate_report(report, samples)


def test_control_false_positive_fails_gate():
    _, report = fixture_report()
    assert compare_pair(report, deepcopy(report))
    assert compare_pair(report, {'root_event': None}) == []


def test_timestamp_causal_validation_requires_strict_downstream_order():
    root = {
        'timestamp_us': 1_000_000,
        'signal': 'estimator_status.pos_vert_accuracy',
        'relation': None,
        'parent_signal': None,
    }
    attitude = {
        'timestamp_us': 1_500_000,
        'signal': 'vehicle_attitude.q[0]',
        'relation': 'likely_caused',
        'parent_signal': root['signal'],
    }
    motion = {
        'timestamp_us': 2_000_000,
        'signal': 'vehicle_local_position.z',
        'relation': 'likely_caused',
        'parent_signal': attitude['signal'],
    }
    report = {'root_event': root, 'failure_chain': [root, attitude, motion]}
    metadata = {
        'expected_root_family': 'estimation',
        'required_downstream_families': ['attitude', 'motion'],
    }
    assert validate_causal_timestamps(report, metadata) == []

    reversed_report = deepcopy(report)
    reversed_report['failure_chain'][1]['timestamp_us'] = 900_000
    assert validate_causal_timestamps(reversed_report, metadata)


def test_healthy_battery_demand_and_soc_depletion_are_not_failure_roots():
    samples = []
    for i in range(40):
        t = i * 100_000
        samples.extend([
            Sample(t, 'battery_status.current_a', 2.0),
            Sample(t, 'battery_status.remaining', 0.90),
        ])
    samples.extend([
        Sample(4_000_000, 'battery_status.current_a', 20.0),
        Sample(4_000_000, 'battery_status.remaining', 0.82),
    ])
    report = build_report(samples, 'healthy-battery')
    assert report['root_event'] is None
    assert report['conclusion'] == 'no_deviation_detected'


def test_voltage_collapse_remains_eligible_power_root():
    samples = [Sample(i * 100_000, 'battery.voltage', 12.0) for i in range(40)]
    samples.append(Sample(4_000_000, 'battery.voltage', 8.0))
    report = build_report(samples, 'voltage-collapse')
    assert report['root_event']['signal'] == 'battery.voltage'


def test_subthreshold_px4_test_ratio_is_not_material_anomaly():
    samples = [Sample(i * 100_000, 'estimator_status.pos_test_ratio', 0.006) for i in range(40)]
    samples.append(Sample(4_000_000, 'estimator_status.pos_test_ratio', 0.04))
    assert detect_deviations(samples) == []
    assert build_report(samples, 'healthy-estimator')['root_event'] is None


def test_healthy_estimator_accuracy_change_is_visible_but_cannot_root_failure():
    horizontal = [Sample(i * 100_000, 'estimator_status.pos_horiz_accuracy', 0.33) for i in range(40)]
    horizontal.append(Sample(4_000_000, 'estimator_status.pos_horiz_accuracy', 0.80))
    vertical = [Sample(i * 100_000, 'estimator_status.pos_vert_accuracy', 0.40) for i in range(40)]
    vertical.append(Sample(4_000_000, 'estimator_status.pos_vert_accuracy', 1.80))
    samples = horizontal + vertical
    deviations = detect_deviations(samples)
    assert {deviation.signal for deviation in deviations} == {
        'estimator_status.pos_horiz_accuracy',
        'estimator_status.pos_vert_accuracy',
    }
    assert build_report(samples, 'healthy-accuracy', deviations=deviations)['root_event'] is None


def test_estimator_state_covariance_validity_and_reset_fields_are_not_anomalies():
    excluded_signals = (
        'estimator_status.states[20]',
        'estimator_status.covariances[3]',
        'vehicle_local_position.xy_valid',
        'vehicle_local_position.reset_count',
    )
    samples = []
    for i in range(40):
        for signal in excluded_signals:
            samples.append(Sample(i * 100_000, signal, 0.0))
    for signal in excluded_signals:
        samples.append(Sample(4_000_000, signal, 100.0))
    assert detect_deviations(samples) == []


def test_multi_instance_actuator_commands_cannot_be_root_proof():
    samples = []
    for i in range(40):
        t = i * 100_000
        samples.extend([
            Sample(t, 'actuator_outputs[2].output[3]', 1000.0),
            Sample(t, 'vehicle_attitude.q[0]', 1.0),
            Sample(t, 'vehicle_local_position.z', 0.0),
        ])
    samples.extend([
        Sample(4_000_000, 'actuator_outputs[2].output[3]', 1800.0),
        Sample(4_100_000, 'vehicle_attitude.q[0]', 0.5),
        Sample(4_200_000, 'vehicle_local_position.z', -10.0),
    ])
    report = build_report(samples, 'command-transition')
    assert report['root_event'] is None


def test_confidence_is_monotonic_bounded_heuristic():
    values = [_confidence(score, 7) for score in (7, 8, 10, 20, 1000)]
    assert values == sorted(values)
    assert values[0] == .5 and values[-1] == .999


def test_ulog_instances_and_nonfinite_values(monkeypatch):
    import pyulog
    datasets = [SimpleNamespace(name='battery_status', multi_id=i,
        data={'timestamp': [1, 2, 3], 'voltage_v': [12 + i, float('nan'), float('inf')]}) for i in (0, 1)]
    monkeypatch.setattr(pyulog, 'ULog', lambda _: SimpleNamespace(data_list=datasets))
    samples = load_ulog('unused.ulg')
    assert [(s.signal, s.value) for s in samples] == [('battery_status.voltage_v', 12), ('battery_status[1].voltage_v', 13)]


def test_truncated_and_changed_downloads_rejected():
    with pytest.raises(RuntimeError):
        validate_ulog(b'ULog', 'test')
    with pytest.raises(RuntimeError, match='SHA-256'):
        validate_ulog(b'ULog\x01\x12\x35' + bytes(20), 'github-indoor-crash-2025')
