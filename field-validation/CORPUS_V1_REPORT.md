# PAMIR Field Validation Corpus v1 — Aggregate Evidence Report

Status: COMPLETE  
Frozen engine under test: PAMIR v0.1.0  
Corpus size: 50 accepted real public PX4 flights  
Synthetic data: none

## Result

All 50 accepted cases have pinned provenance and passed exact deterministic replay. The frozen v0.1 detection policy, thresholds, benchmark corpus, Evidence Pack, and required CI semantics were not modified by this programme.

| Measure | Result |
|---|---:|
| Accepted real flights | 50 / 50 |
| Exact deterministic replay | 50 / 50 |
| Incident | 6 |
| Healthy control | 33 |
| Unknown | 11 |
| deviation_detected | 24 |
| no_deviation_detected | 21 |
| Legacy/null conclusion field | 5 |
| Healthy controls with a PAMIR root | 16 / 33 (48.48%) |

## Family coverage

| Primary family | Accepted cases |
|---|---:|
| sensor_anomaly | 9 |
| attitude_control | 5 |
| failsafe | 12 |
| propulsion_motor | 1 |
| ekf_gps | 3 |
| power_battery | 2 |
| other / general flight validation | 18 |

## Interpretation boundaries

A deterministic replay PASS means the same pinned input produced byte-identical PAMIR reports across the required replay pair. It does not mean the inferred root is ground-truth causation.

Healthy/incident/unknown classification is derived independently from source narrative and predeclared acceptance criteria; PAMIR output does not manufacture the label.

The healthy-control root rate is reported without tuning it away: 16 of 33 accepted healthy controls produced a PAMIR root (48.48%). This is a field-validation finding and a calibration/generalisation target, not evidence that those source-labelled healthy flights failed.

PAMIR v0.1 confidence remains an uncalibrated anomaly-strength heuristic and must not be interpreted as probability of causation.

Unknown/no-conclusion behaviour is retained rather than converted into artificial PASS/failure labels.

## Reproducibility and provenance

Each accepted case follows the programme chain:

source -> license -> original file -> SHA256 -> provenance -> independent classification -> predeclared acceptance criteria -> PAMIR result -> reproducibility result

Source-unavailable/quarantined candidates are excluded from the 50 accepted cases and are not silently substituted under an existing case identity.

## Corpus composition limitation

Corpus v1 is intentionally real-world and provenance-first, but it is not balanced across failure families. In particular, propulsion/motor and power/battery coverage is smaller than failsafe/general validation coverage. Corpus v1 therefore establishes reproducible field evidence, not population-level prevalence or calibrated causal accuracy.

## Next validation lane

Threshold sensitivity and error analysis must run in a separate field-validation harness against the frozen v0.1 engine. The frozen v0.1 thresholds/configuration, validated benchmark corpus, Evidence Pack, and CI semantics remain unchanged.
