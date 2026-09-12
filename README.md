# PAMIR

### Post-Mission Autonomous Incident Reconstruction

> **Tell me what failed first — and prove it.**

PAMIR is an offline forensic analysis engine for autonomous-system telemetry. It reconstructs an incident timeline, identifies the **earliest material root event**, and preserves the timestamped evidence showing what happened next.

```text
PX4 ULog
   │
   ▼
Normalize telemetry
   │
   ▼
Detect material deviations
   │
   ▼
Identify earliest root event
   │
   ├──────────────► Evidence window
   │
   ▼
Validate timestamp ordering
   │
   ▼
Reconstruct causal / follow-up chain
   │
   ▼
Evidence-backed JSON incident report
```

## v0.1 — validated baseline

**PAMIR v0.1 has passed its reproducible public validation gate.**

| Validation | Result |
| --- | ---: |
| Public PX4 incident ULogs | **5 / 5 material roots identified** |
| Healthy / control ULogs | **3 / 3 with no material root** |
| Timestamp causal validation | **PASS** |
| Benchmark inputs | **SHA256 pinned** |
| Operation | **Local / offline** |

The benchmark is a hard CI gate: public logs are downloaded, cryptographically verified, analyzed, and checked for root-event and timestamp invariants. Detailed measured results are in [`benchmarks/VALIDATION.md`](benchmarks/VALIDATION.md).

## What PAMIR returns

PAMIR is designed to answer four questions:

1. **What failed first?** — the earliest material root event.
2. **When did it happen?** — the source telemetry timestamp.
3. **What happened next?** — a strictly timestamp-ordered incident chain.
4. **What evidence supports it?** — replayable telemetry observations around each deviation.

Conceptually, a report looks like this:

```text
ROOT EVENT
└─ signal:      vehicle_rates_setpoint.pitch
   confidence:  0.999
   evidence:    [t-0.50s ... t+0.75s]

   ├─ likely_caused ─► attitude deviation
   └─ followed_by   ─► motion deviation
```

The example above illustrates the report structure. Exact benchmark measurements and detected roots are recorded in the validation snapshot rather than hard-coded into the analyzer.

## Why this is different from anomaly detection

An anomaly detector can tell you that a signal looks unusual. PAMIR's v0.1 objective is narrower and harder: determine the **first defensible material event**, then organize downstream evidence without pretending that temporal correlation proves causation.

Root selection is deliberately conservative. Normal battery demand/SOC depletion, estimator state/covariance/reset fields, ordinary actuator commands, healthy estimator-accuracy changes, and sub-threshold estimator test ratios are not accepted as failure roots. Vibration metrics remain evidence-only.

Control setpoints are excluded from the generic detector. A control-family root is permitted only for a narrow multi-axis rate-command discontinuity followed by attitude and motion anomalies.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
pytest -q
```

Analyze a real PX4 ULog:

```bash
pamir analyze path/to/flight.ulg -o pamir-report.json
```

Or run the bundled normalized demo:

```bash
pamir analyze examples/demo.json -o pamir-report.json
```

## Reproduce the public PX4 benchmark

```bash
python scripts/download_px4_benchmarks.py
python scripts/validate_px4_benchmarks.py
```

The hard v0.1 corpus contains five directly accessible public incident ULogs and three healthy/control ULogs. Required cases and SHA-256 digests are pinned in [`benchmarks/px4_reproducible_incidents.json`](benchmarks/px4_reproducible_incidents.json).

The corpus covers an indoor estimation-degradation crash, a Follow Me controller-command crash, a position-mode crash, an altitude-hold crash, an uncontrolled-yaw incident, and three labeled healthy/control flights.

The older `benchmarks/px4_public_incidents.json` Flight Review corpus remains optional because `logs.px4.io` currently returns HTTP 403 to hosted CI runners. It does not determine v0.1 completion.

## Forensic method

Each eligible signal is evaluated against recent telemetry history using a rolling robust median/MAD baseline. History is limited to 10 seconds and 250 samples, with at least 30 prior observations.

Each detected deviation can carry:

- source signal and timestamp;
- anomaly-strength confidence;
- evidence window;
- signal family;
- conservative `likely_caused` or `followed_by` relationship.

`likely_caused` requires strict timestamp order, temporal proximity, and a plausible signal-family transition. It is an evidence-organizing relationship, **not a claim of mathematically proven causation**.

`confidence` is an **uncalibrated anomaly-strength heuristic**, not a probability that the proposed cause is correct.

## v0.1 completion gate

v0.1 requires all of the following:

1. five public incident ULogs and the healthy/control corpus download reproducibly;
2. required binaries pass SHA-256 verification;
3. every required ULog parses and analyzes without crashing;
4. every incident produces a material root with required downstream telemetry strictly after the root timestamp;
5. every healthy/control ULog produces no material failure root;
6. evidence windows replay the exact reported observations;
7. causal links satisfy strict temporal-order invariants;
8. unit/regression tests and the GitHub Actions benchmark both pass.

## Validation status — 2026-09-12

**v0.1 reproducible validation gate: PASSED.**

Validated benchmark head: `18c0553affe2a508f686d2285770bb4172b8b859`  
Final documentation head before merge: `c6d0660b85a12a00af4b7445d5a5605ff8953a2d`  
PR #2 squash-merged to `main`: `0427a6ef30c7a7a50cf71a491d9cbe41fd3f9dd3`

The validated workflow printed:

```text
PAMIR v0.1 REPRODUCIBLE VALIDATION GATE PASSED
```

and generated:

```text
v0_1_complete: true
validation_passed: true
validation_errors: []
required_incident_count: 5
required_control_count: 3
```

All five required incidents produced material roots with zero timestamp-causal validation errors. All three healthy/control logs produced `no_deviation_detected` with no material root.

During benchmark hardening, a candidate "single motor output zero" case was deliberately removed after the upstream PX4 discussion established that the observed output could be intended yaw-control behavior rather than a true failure. PAMIR was **not tuned to force a mislabeled benchmark case to pass**.

See [`benchmarks/VALIDATION.md`](benchmarks/VALIDATION.md) and [`benchmarks/validation_snapshot.json`](benchmarks/validation_snapshot.json) for the measured evidence.

## v0.1 scope

- PX4 ULog ingestion
- normalized telemetry
- adaptive rolling median/MAD baseline
- first material root-event analysis
- confidence / anomaly-strength scoring
- evidence windows
- conservative causal/follow-up relations
- evidence-backed JSON incident report
- reproducible public benchmark
- healthy/control false-positive gate
- timestamp causal validation
- local/offline operation

## Current direction

v0.1 is intentionally frozen as a validated baseline. The immediate priority is **external validation**: additional public ULogs, real flight-test telemetry, methodology review, and evidence-backed incident cases. New feature families should not weaken the existing validation gate.

Technical criticism and additional public PX4 ULogs are welcome.

## Safety boundary

PAMIR focuses on reliability, telemetry analysis, test/measurement, incident reconstruction, and mission assurance. It is not intended for weapon control, targeting, engagement, or autonomous attack functions.
