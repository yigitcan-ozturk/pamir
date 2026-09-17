import pytest

from pamir.causal_validation import validate_causal_chain


def _event(timestamp_us, signal, relation=None, parent_signal=None):
    return {
        "timestamp_us": timestamp_us,
        "signal": signal,
        "relation": relation,
        "parent_signal": parent_signal,
    }


def test_accepts_supported_strictly_forward_causal_chain():
    chain = [
        _event(1_000_000, "battery_status.voltage_v"),
        _event(1_100_000, "motor_failure.output", "likely_caused", "battery_status.voltage_v"),
        _event(1_200_000, "vehicle_attitude.roll", "likely_caused", "motor_failure.output"),
        _event(1_300_000, "vehicle_local_position.z", "likely_caused", "vehicle_attitude.roll"),
    ]
    result = validate_causal_chain(chain)
    assert result["valid"] is True
    assert result["error_count"] == 0
    assert result["rule_version"] == "v0.2-causal-rules-v1"


def test_rejects_backward_or_equal_timestamp():
    chain = [
        _event(2_000_000, "estimator_status.test_ratio"),
        _event(2_000_000, "vehicle_attitude.pitch", "likely_caused", "estimator_status.test_ratio"),
    ]
    result = validate_causal_chain(chain)
    assert result["valid"] is False
    assert any(error["code"] == "non_forward_timestamp" for error in result["errors"])


def test_rejects_unsupported_likely_caused_transition():
    chain = [
        _event(1_000_000, "vehicle_local_position.z"),
        _event(1_100_000, "battery_status.voltage_v", "likely_caused", "vehicle_local_position.z"),
    ]
    result = validate_causal_chain(chain)
    assert result["valid"] is False
    assert any(error["code"] == "unsupported_likely_caused_transition" for error in result["errors"])
    assert result["fallback_policy"] == "unsupported causal claims must downgrade to followed_by"


def test_rejects_parent_signal_mismatch():
    chain = [
        _event(1_000_000, "estimator_status.test_ratio"),
        _event(1_100_000, "vehicle_attitude.pitch", "likely_caused", "wrong.signal"),
    ]
    result = validate_causal_chain(chain)
    assert any(error["code"] == "parent_signal_mismatch" for error in result["errors"])


def test_unknown_rule_version_is_rejected():
    with pytest.raises(ValueError, match="unsupported causal rule version"):
        validate_causal_chain([], rule_version="future-version")
