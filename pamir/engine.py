from collections import defaultdict
from math import exp
from statistics import median
from .model import Sample, Deviation


def _mad(values: list[float], center: float) -> float:
    return median([abs(v - center) for v in values]) if values else 0.0


def _confidence(score: float, threshold: float) -> float:
    # Smoothly saturates toward 1.0 as a deviation exceeds the threshold.
    x = max(0.0, score - threshold)
    return round(min(0.999, 0.5 + 0.5 * (1.0 - exp(-x / 3.0))), 3)


def _signal_family(signal: str) -> str:
    s = signal.lower()
    if "battery" in s or "voltage" in s or "current" in s:
        return "power"
    if "actuator" in s or "motor" in s or "output" in s or "thrust" in s:
        return "actuation"
    if "attitude" in s or "angular" in s or "gyro" in s:
        return "attitude"
    if "position" in s or "alt" in s or "velocity" in s or "gps" in s:
        return "motion"
    if "estimator" in s or "innovation" in s or "mag" in s:
        return "estimation"
    return "other"


def _relation(parent: Deviation, child: Deviation, causal_window_us: int) -> tuple[str, str | None]:
    dt = child.timestamp_us - parent.timestamp_us
    if dt < 0 or dt > causal_window_us:
        return "followed_by", parent.signal

    transitions = {
        ("power", "actuation"),
        ("actuation", "attitude"),
        ("attitude", "motion"),
        ("estimation", "attitude"),
        ("estimation", "motion"),
    }
    if (_signal_family(parent.signal), _signal_family(child.signal)) in transitions:
        return "likely_caused", parent.signal
    return "followed_by", parent.signal


def detect_deviations(
    samples: list[Sample],
    *,
    threshold: float = 6.0,
    min_baseline_points: int = 30,
    baseline_window_us: int = 10_000_000,
    evidence_before_us: int = 500_000,
    evidence_after_us: int = 750_000,
    causal_window_us: int = 3_000_000,
) -> list[Deviation]:
    """Detect each signal's first meaningful deviation using a rolling robust baseline.

    Unlike the original fixed first-N-samples baseline, the baseline is built from
    recent history immediately preceding each candidate point. This makes the
    detector usable across ULog topics with different sampling rates and flight phases.
    """
    series: dict[str, list[Sample]] = defaultdict(list)
    for sample in sorted(samples, key=lambda s: s.timestamp_us):
        series[sample.signal].append(sample)

    raw: list[Deviation] = []
    for signal, points in series.items():
        history: list[Sample] = []
        for point in points:
            cutoff = point.timestamp_us - baseline_window_us
            history = [h for h in history if h.timestamp_us >= cutoff]

            if len(history) >= min_baseline_points:
                values = [h.value for h in history]
                center = median(values)
                mad = _mad(values, center)
                robust_scale = 1.4826 * mad
                magnitude_floor = max(1e-6, abs(center) * 0.005)
                scale = max(robust_scale, magnitude_floor)
                score = abs(point.value - center) / scale

                if score >= threshold:
                    raw.append(
                        Deviation(
                            timestamp_us=point.timestamp_us,
                            signal=signal,
                            value=point.value,
                            baseline=center,
                            score=round(score, 3),
                            confidence=_confidence(score, threshold),
                            evidence_start_us=max(0, point.timestamp_us - evidence_before_us),
                            evidence_end_us=point.timestamp_us + evidence_after_us,
                            reason="rolling_robust_baseline_deviation",
                        )
                    )
                    break

            history.append(point)

    ordered = sorted(raw, key=lambda d: d.timestamp_us)
    linked: list[Deviation] = []
    for i, deviation in enumerate(ordered):
        if i == 0:
            linked.append(deviation)
            continue
        relation, parent = _relation(linked[-1], deviation, causal_window_us)
        linked.append(
            Deviation(
                timestamp_us=deviation.timestamp_us,
                signal=deviation.signal,
                value=deviation.value,
                baseline=deviation.baseline,
                score=deviation.score,
                confidence=deviation.confidence,
                evidence_start_us=deviation.evidence_start_us,
                evidence_end_us=deviation.evidence_end_us,
                reason=deviation.reason,
                relation=relation,
                parent_signal=parent,
            )
        )
    return linked


def build_report(samples: list[Sample], source: str) -> dict:
    deviations = detect_deviations(samples)
    first = deviations[0].to_dict() if deviations else None
    chain = [d.to_dict() for d in deviations[:10]]
    return {
        "pamir_version": "0.1.0",
        "source": source,
        "sample_count": len(samples),
        "signals_analyzed": len({s.signal for s in samples}),
        "root_event": first,
        "first_deviation": first,
        "failure_chain": chain,
        "method": {
            "baseline": "rolling median/MAD",
            "evidence_window": "-0.5s/+0.75s",
            "causal_links": "conservative temporal + signal-family heuristic",
        },
        "conclusion": "deviation_detected" if first else "no_deviation_detected",
    }
