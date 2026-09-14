from __future__ import annotations

from typing import Any


TRANSITION_RULES_V1 = {
    ("power", "actuation"),
    ("actuation", "attitude"),
    ("attitude", "motion"),
    ("estimation", "attitude"),
    ("estimation", "motion"),
    ("control", "attitude"),
    ("control", "motion"),
}


def signal_family(signal: str) -> str:
    s = signal.lower()
    if "vehicle_rates_setpoint" in s or "vehicle_attitude_setpoint" in s:
        return "control"
    if "estimator" in s or "innovation" in s or "mag" in s:
        return "estimation"
    if "battery" in s or "voltage" in s or "current" in s:
        return "power"
    if "actuator" in s or "motor" in s or "output" in s or "thrust" in s:
        return "actuation"
    if "attitude" in s or "angular" in s or "gyro" in s:
        return "attitude"
    if "position" in s or "alt" in s or "velocity" in s or "gps" in s:
        return "motion"
    return "other"


def validate_causal_chain(
    chain: list[dict[str, Any]], *, rule_version: str = "v0.2-causal-rules-v1"
) -> dict[str, Any]:
    """Validate v0.2 causal claims without changing the frozen v0.1 detector.

    `likely_caused` is accepted only for strictly forward-in-time adjacent events,
    with the declared parent matching the previous signal and a transition allowed
    by the versioned rule table. Unsupported claims are reported as errors so the
    v0.2 reporting layer can downgrade them to `followed_by`.
    """
    if rule_version != "v0.2-causal-rules-v1":
        raise ValueError("unsupported causal rule version")

    errors: list[dict[str, Any]] = []
    for index, event in enumerate(chain):
        timestamp = event.get("timestamp_us")
        if not isinstance(timestamp, int) or timestamp < 0:
            errors.append({"index": index, "code": "invalid_timestamp"})
            continue

        if index == 0:
            if event.get("relation") not in (None, "followed_by"):
                errors.append({"index": index, "code": "root_has_causal_relation"})
            continue

        previous = chain[index - 1]
        previous_ts = previous.get("timestamp_us")
        if isinstance(previous_ts, int) and timestamp <= previous_ts:
            errors.append({"index": index, "code": "non_forward_timestamp"})

        relation = event.get("relation")
        parent_signal = event.get("parent_signal")
        expected_parent = previous.get("signal")
        if parent_signal != expected_parent:
            errors.append({"index": index, "code": "parent_signal_mismatch"})

        if relation == "likely_caused":
            transition = (signal_family(str(expected_parent or "")), signal_family(str(event.get("signal") or "")))
            if transition not in TRANSITION_RULES_V1:
                errors.append({
                    "index": index,
                    "code": "unsupported_likely_caused_transition",
                    "transition": list(transition),
                })
        elif relation != "followed_by":
            errors.append({"index": index, "code": "unsupported_relation"})

    return {
        "rule_version": rule_version,
        "event_count": len(chain),
        "error_count": len(errors),
        "errors": errors,
        "valid": not errors,
        "fallback_policy": "unsupported causal claims must downgrade to followed_by",
    }
