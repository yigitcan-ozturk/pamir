# PAMIR

**Post-Mission Autonomous Incident Reconstruction**

> **PAMIR reconstructs autonomous-system failures from mission telemetry and identifies what failed first, what happened next, and the evidence behind it.**

PAMIR is an offline-first flight/mission black-box investigator for autonomous systems.

Its first goal is simple:

> **Tell me what failed first — and prove it.**

PAMIR ingests mission logs, normalizes telemetry, identifies the first meaningful deviation, reconstructs the downstream failure chain, and produces an evidence-backed incident report.

## v0.1 scope

- PX4 ULog ingestion
- normalized event timeline
- adaptive rolling median/MAD baseline
- first-deviation analysis
- confidence per deviation
- evidence windows around each deviation
- conservative causal relationship labels
- evidence-backed JSON incident report
- local/offline operation
- reproducible validation against public PX4 incident and healthy/control logs

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
pytest -q
pamir analyze examples/demo.json -o pamir-report.json
```

For a real PX4 log:

```bash
pamir analyze path/to/flight.ulg -o pamir-report.json
```

## Public PX4 benchmark

The v0.1 hard gate uses five directly accessible public incident ULogs and three public healthy/control ULogs. Binary logs are not committed to this repository; the downloader fetches them from public GitHub sources and verifies pinned SHA-256 digests before analysis.

```bash
python scripts/download_px4_benchmarks.py
python scripts/validate_px4_benchmarks.py
```

Required cases are listed in `benchmarks/px4_reproducible_incidents.json`. The corpus includes an indoor estimation-degradation crash, a Follow Me controller-command crash, a position-mode crash, an altitude-hold crash, an uncontrolled-yaw incident, and three labeled healthy/control flights.

The older `benchmarks/px4_public_incidents.json` Flight Review corpus remains an optional extended set because `logs.px4.io` currently returns HTTP 403 to hosted CI runners. Those optional sources do not determine v0.1 completion.

## v0.1 forensic method

The original fixed first-20-samples baseline has been removed. Each eligible signal is evaluated against recent telemetry history using a rolling robust median/MAD baseline. The history is limited to 10 seconds and 250 samples, with at least 30 prior observations.

Root selection is deliberately more conservative than anomaly detection. Normal battery demand/SOC depletion, estimator state/covariance/reset fields, ordinary actuator commands, healthy estimator-accuracy changes, and sub-threshold estimator test ratios are not accepted as failure roots. Vibration metrics remain evidence-only. Control setpoints remain excluded from the generic detector; a control-family root is permitted only for a narrow multi-axis rate-command discontinuity followed by attitude and motion anomalies.

Each detected deviation can contain:

```text
ROOT EVENT
signal deviation
confidence: anomaly-strength score
evidence: t-0.50s .. t+0.75s

    -> likely_caused / followed_by

next telemetry deviation
```

`likely_caused` in v0.1 is intentionally conservative: it requires strict timestamp order, temporal proximity, and a plausible signal-family transition. Other ordered events are labeled `followed_by`. This is evidence organization, not a claim of mathematically proven causation.

`confidence` is an **uncalibrated anomaly-strength heuristic**, not a probability that the proposed cause is correct.

## Current implementation

```text
PX4 .ulg / normalized .json
          |
          v
      ingestion
          |
          v
 normalized samples
          |
          v
 rolling robust detector
          |
          +----> root event + confidence + evidence window
          |
          +----> timestamp-ordered causal/follow-up chain
          |
          v
 evidence-backed JSON report
```

## v0.1 completion gate

v0.1 requires all of the following:

1. five public incident ULogs and the healthy/control corpus download reproducibly,
2. required binaries pass SHA-256 verification,
3. PAMIR parses and analyzes every required ULog without crashing,
4. every incident produces a material root with required downstream telemetry strictly after the root timestamp,
5. every healthy/control ULog produces no material failure root,
6. evidence windows replay the exact reported observations,
7. causal links satisfy strict temporal-order invariants,
8. unit/regression tests and the GitHub Actions benchmark both pass.

## Validation status — 2026-09-12

**v0.1 reproducible validation gate: PASSED.**

Final validated head: `18c0553affe2a508f686d2285770bb4172b8b859`.
GitHub Actions benchmark run `34664700248` completed successfully and printed:

```text
PAMIR v0.1 REPRODUCIBLE VALIDATION GATE PASSED
```

The generated summary reports:

```text
v0_1_complete: true
validation_passed: true
validation_errors: []
required_incident_count: 5
required_control_count: 3
```

All five required incidents produced material roots with zero timestamp-causal validation errors. All three healthy/control logs produced `no_deviation_detected` with no material root. The pinned public PX4/pyulog binary sample also parses through the full pipeline.

During benchmark hardening, a candidate “single motor output zero” case was removed after the upstream PX4 issue discussion established that the observed zero motor command could be intended yaw-control behavior rather than a fault. PAMIR was not tuned to force that mislabeled case to pass.

Detailed measured results are recorded in `benchmarks/VALIDATION.md` and `benchmarks/validation_snapshot.json`.

## Safety boundary

PAMIR focuses on reliability, telemetry analysis, test/measurement, incident reconstruction, and mission assurance. It is not intended for weapon control, targeting, engagement, or autonomous attack functions.
