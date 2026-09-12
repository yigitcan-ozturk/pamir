from bisect import bisect_right
from collections import defaultdict, deque
from math import exp, isfinite
from statistics import median
from .model import Sample, Deviation


def _mad(values: list[float], center: float) -> float:
    return median([abs(v - center) for v in values]) if values else 0.0


def _confidence(score: float, threshold: float) -> float:
    x = max(0.0, score - threshold)
    return round(min(0.999, 0.5 + 0.5 * (1.0 - exp(-x / 3.0))), 3)


def _signal_family(signal: str) -> str:
    s = signal.lower()
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


def _is_root_candidate(signal: str) -> bool:
    s = signal.lower()
    excluded = (
        "setpoint", "timestamp", "_integral_dt", ".device_id", ".noutputs",
        ".nav_state", ".arming_state", ".hil_state", ".failsafe", "_counter",
        "reset_count", "_flags", ".failure_detector_status", ".rc_signal_lost",
        ".data_link_lost", ".is_rotary_wing", ".is_vtol", ".in_transition",
        "states[", "covariances[", "_valid", ".valid",
    )
    return not any(term in s for term in excluded)


def _direction_is_material(signal: str, value: float, baseline: float) -> bool:
    s = signal.lower()
    if "test_ratio" in s:
        return value > 1.0
    if "pos_horiz_accuracy" in s or "pos_vert_accuracy" in s:
        return value > baseline
    if "tracking_error" in s:
        return abs(value) > abs(baseline)
    if "voltage" in s:
        return value < baseline
    return True


def _magnitude_floor(signal: str, center: float) -> float:
    s = signal.lower()
    base = max(1e-6, abs(center) * 0.005)
    if "actuator_motors" in s and ".control" in s:
        return max(base, 0.005)
    if "actuator_outputs" in s and ".output" in s:
        return max(base, abs(center) * 0.05, 5.0)
    return base


def _is_measured_actuation_root(deviation: Deviation) -> bool:
    if deviation.reason == "armed_actuator_output_collapse":
        return True
    s = deviation.signal.lower()
    if "actuator_motors" in s and ".control" in s:
        return False
    if "actuator_outputs" in s and ".output" in s:
        return False
    return True


def _is_power_root(signal: str) -> bool:
    return "voltage" in signal.lower()


def _is_material_estimation_root(deviation: Deviation) -> bool:
    s = deviation.signal.lower()
    if ".vibe[" in s or s.endswith(".vibe"):
        return False
    if "pos_horiz_accuracy" in s:
        return deviation.value > 1.0
    if "pos_vert_accuracy" in s:
        return deviation.value > 2.0
    return True


def _relation(parent: Deviation, child: Deviation, causal_window_us: int) -> tuple[str, str | None]:
    dt = child.timestamp_us - parent.timestamp_us
    if dt <= 0 or dt > causal_window_us:
        return "followed_by", parent.signal
    transitions = {
        ("power", "actuation"), ("actuation", "attitude"),
        ("attitude", "motion"), ("estimation", "attitude"),
        ("estimation", "motion"),
    }
    if (_signal_family(parent.signal), _signal_family(child.signal)) in transitions:
        return "likely_caused", parent.signal
    return "followed_by", parent.signal


def _select_material_root_index(deviations: list[Deviation], cluster_window_us: int = 3_000_000) -> int | None:
    core = {"power", "actuation", "attitude", "motion", "estimation"}
    for i, deviation in enumerate(deviations):
        family = _signal_family(deviation.signal)
        if family not in {"power", "actuation", "estimation"}:
            continue
        if family == "power" and not _is_power_root(deviation.signal):
            continue
        if family == "actuation":
            if not _is_measured_actuation_root(deviation) or deviation.confidence < 0.8:
                continue
        if family == "estimation":
            if not _is_material_estimation_root(deviation):
                continue
            recent_actuation = any(
                _signal_family(previous.signal) == "actuation"
                and 0 <= deviation.timestamp_us - previous.timestamp_us <= 2_000_000
                for previous in deviations[:i]
            )
            if recent_actuation:
                continue
        end = deviation.timestamp_us + cluster_window_us
        families = {
            _signal_family(item.signal)
            for item in deviations[i:]
            if item.timestamp_us <= end
        } & core
        required_families = 2 if deviation.reason == "armed_actuator_output_collapse" else 3
        if "motion" in families and len(families) >= required_families:
            return i
    if deviations:
        first = deviations[0]
        if _signal_family(first.signal) == "power" and _is_power_root(first.signal) and first.confidence >= 0.9:
            return 0
    return None


def _armed_state_index(series: dict[str, list[Sample]]) -> tuple[list[int], list[float]]:
    points = series.get("vehicle_status.arming_state", [])
    return [point.timestamp_us for point in points], [point.value for point in points]


def _armed_at(timestamp_us: int, arm_times: list[int], arm_values: list[float]) -> bool:
    index = bisect_right(arm_times, timestamp_us) - 1
    return index >= 0 and arm_values[index] == 2.0


def _critical_actuator_collapses(
    series: dict[str, list[Sample]],
    *,
    evidence_before_us: int,
    evidence_after_us: int,
) -> list[Deviation]:
    """Find persistent PWM collapses while PX4 still reports the vehicle armed.

    This path is intentionally narrow: it does not treat ordinary actuator commands as
    root proof. It only records a later critical event when a previously active PWM
    channel falls to its minimum region while the vehicle remains armed.
    """
    arm_times, arm_values = _armed_state_index(series)
    if not arm_times:
        return []

    found = []
    for signal, points in series.items():
        s = signal.lower()
        if "actuator_outputs" not in s or ".output[" not in s or len(points) < 13:
            continue
        history: deque[float] = deque(maxlen=20)
        for index, point in enumerate(points):
            if len(history) >= 10:
                center = median(history)
                drop = center - point.value
                persistent = (
                    index + 2 < len(points)
                    and points[index + 1].value <= 1100.0
                    and points[index + 2].value <= 1100.0
                    and points[index + 2].timestamp_us - point.timestamp_us <= 500_000
                )
                if (
                    center >= 1300.0
                    and point.value <= 1100.0
                    and drop >= 400.0
                    and persistent
                    and _armed_at(point.timestamp_us, arm_times, arm_values)
                ):
                    score = max(7.0, drop / 50.0)
                    found.append(Deviation(
                        timestamp_us=point.timestamp_us,
                        signal=signal,
                        value=point.value,
                        baseline=center,
                        score=round(score, 3),
                        confidence=_confidence(score, 7.0),
                        evidence_start_us=max(points[0].timestamp_us, point.timestamp_us - evidence_before_us),
                        evidence_end_us=min(points[-1].timestamp_us, point.timestamp_us + evidence_after_us),
                        reason="armed_actuator_output_collapse",
                    ))
                    break
            history.append(point.value)
    return found


def detect_deviations(
    samples: list[Sample], *, threshold: float = 7.0, min_baseline_points: int = 30,
    baseline_window_us: int = 10_000_000, max_baseline_points: int = 250,
    evidence_before_us: int = 500_000, evidence_after_us: int = 750_000,
    causal_window_us: int = 3_000_000,
) -> list[Deviation]:
    """Detect meaningful deviations plus narrowly-defined later critical collapses."""
    series: dict[str, list[Sample]] = defaultdict(list)
    for sample in sorted(samples, key=lambda s: s.timestamp_us):
        if sample.timestamp_us >= 0 and isfinite(sample.value):
            series[sample.signal].append(sample)

    raw: list[Deviation] = []
    for signal, points in series.items():
        if not _is_root_candidate(signal):
            continue
        history: deque[Sample] = deque()
        for point in points:
            cutoff = point.timestamp_us - baseline_window_us
            while history and history[0].timestamp_us < cutoff:
                history.popleft()
            if len(history) >= min_baseline_points:
                values = [h.value for h in history]
                center = median(values)
                mad = _mad(values, center)
                scale = max(1.4826 * mad, _magnitude_floor(signal, center))
                score = abs(point.value - center) / scale
                if score >= threshold and _direction_is_material(signal, point.value, center):
                    raw.append(Deviation(
                        timestamp_us=point.timestamp_us, signal=signal, value=point.value,
                        baseline=center, score=round(score, 3),
                        confidence=_confidence(score, threshold),
                        evidence_start_us=max(points[0].timestamp_us, point.timestamp_us - evidence_before_us),
                        evidence_end_us=min(points[-1].timestamp_us, point.timestamp_us + evidence_after_us),
                        reason="rolling_robust_baseline_deviation",
                    ))
                    break
            history.append(point)
            while len(history) > max_baseline_points:
                history.popleft()

    raw.extend(_critical_actuator_collapses(
        series,
        evidence_before_us=evidence_before_us,
        evidence_after_us=evidence_after_us,
    ))

    ordered = sorted(raw, key=lambda d: (d.timestamp_us, d.signal, d.reason))
    linked: list[Deviation] = []
    for i, deviation in enumerate(ordered):
        if i == 0:
            linked.append(deviation)
            continue
        relation, parent = _relation(linked[-1], deviation, causal_window_us)
        linked.append(Deviation(
            timestamp_us=deviation.timestamp_us, signal=deviation.signal,
            value=deviation.value, baseline=deviation.baseline, score=deviation.score,
            confidence=deviation.confidence, evidence_start_us=deviation.evidence_start_us,
            evidence_end_us=deviation.evidence_end_us, reason=deviation.reason,
            relation=relation, parent_signal=parent,
        ))
    return linked


def build_report(samples: list[Sample], source: str, *, deviations: list[Deviation] | None = None) -> dict:
    if deviations is None:
        deviations = detect_deviations(samples)
    root_index = _select_material_root_index(deviations)
    selected = deviations[root_index:] if root_index is not None else []
    first = selected[0].to_dict() if selected else None
    if first is not None:
        first["relation"] = None
        first["parent_signal"] = None

    chain = [d.to_dict() for d in selected[:10]]
    if chain:
        chain[0]["relation"] = None
        chain[0]["parent_signal"] = None

    evidence = {}
    for event in chain:
        points = [
            s for s in samples
            if s.signal == event["signal"]
            and event["evidence_start_us"] <= s.timestamp_us <= event["evidence_end_us"]
            and isfinite(s.value)
        ]
        points.sort(key=lambda s: s.timestamp_us)
        evidence[event["signal"]] = [
            {"timestamp_us": s.timestamp_us, "value": s.value} for s in points
        ]

    return {
        "evidence": evidence,
        "pamir_version": "0.1.0",
        "source": source,
        "sample_count": len(samples),
        "signals_analyzed": len({s.signal for s in samples}),
        "raw_deviation_count": len(deviations),
        "root_event": first,
        "first_deviation": first,
        "failure_chain": chain,
        "method": {
            "baseline": "rolling median/MAD (10s, capped at 250 prior samples per signal; threshold 7.0; actuator noise floors)",
            "root_candidate_policy": "continuous measured telemetry only; estimator state/covariance arrays, validity/reset fields, ordinary actuator commands, raw current demand and normal SOC depletion are evidence rather than root proof; estimator test ratios require >1.0; accuracy anomalies cannot root while horizontal/vertical accuracy remains <1 m/<2 m; vibration metrics remain evidence only; a later actuator output may root only for a persistent armed PWM collapse from >=1300 to <=1100 with >=400 drop and downstream motion evidence",
            "evidence_window": "-0.5s/+0.75s",
            "confidence": "uncalibrated anomaly-strength heuristic; not probability of causation",
            "causal_links": "conservative temporal + signal-family heuristic",
        },
        "conclusion": "deviation_detected" if first else "no_deviation_detected",
    }
