from collections import defaultdict
from statistics import median
from .model import Sample, Deviation


def _mad(values: list[float], center: float) -> float:
    return median([abs(v - center) for v in values]) if values else 0.0


def detect_deviations(samples: list[Sample], baseline_points: int = 20, threshold: float = 6.0) -> list[Deviation]:
    series: dict[str, list[Sample]] = defaultdict(list)
    for sample in sorted(samples, key=lambda s: s.timestamp_us):
        series[sample.signal].append(sample)

    deviations: list[Deviation] = []
    for signal, points in series.items():
        if len(points) <= baseline_points:
            continue
        baseline_values = [p.value for p in points[:baseline_points]]
        center = median(baseline_values)
        mad = _mad(baseline_values, center)
        scale = max(1e-9, 1.4826 * mad)
        floor = max(1e-6, abs(center) * 0.01)
        scale = max(scale, floor)

        for point in points[baseline_points:]:
            score = abs(point.value - center) / scale
            if score >= threshold:
                deviations.append(Deviation(
                    timestamp_us=point.timestamp_us,
                    signal=signal,
                    value=point.value,
                    baseline=center,
                    score=round(score, 3),
                    reason="robust_baseline_deviation",
                ))
                break

    return sorted(deviations, key=lambda d: d.timestamp_us)


def build_report(samples: list[Sample], source: str) -> dict:
    deviations = detect_deviations(samples)
    first = deviations[0].to_dict() if deviations else None
    chain = [d.to_dict() for d in deviations[:10]]
    return {
        "pamir_version": "0.1.0",
        "source": source,
        "sample_count": len(samples),
        "signals_analyzed": len({s.signal for s in samples}),
        "first_deviation": first,
        "failure_chain": chain,
        "conclusion": "deviation_detected" if first else "no_deviation_detected",
    }
