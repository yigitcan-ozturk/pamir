from copy import deepcopy
from types import SimpleNamespace

import pytest

from pamir.engine import build_report, _confidence
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
