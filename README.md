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
- validation against public PX4 incident logs

No new feature families are added until this validation milestone is complete.

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

The v0.1 benchmark manifest contains public incident logs with an accompanying public incident narrative. The binary ULog files are not committed to this repository; they are downloaded reproducibly from PX4 Flight Review.

```bash
python scripts/download_px4_benchmarks.py
pamir analyze benchmarks/data/motor-stop-fatal-crash-2020.ulg -o pamir-report.json
```

Benchmark cases are listed in `benchmarks/px4_public_incidents.json` and currently cover motor-stop/crash, mission flight termination, VTOL return-mode crash, magnetometer-switch/spin crash, plus a successful mission control case.

## v0.1 forensic method

The original fixed first-20-samples baseline has been removed. Each signal is now evaluated against recent telemetry history using a rolling robust median/MAD baseline. This avoids coupling anomaly detection to a particular topic sampling rate and follows changing flight phases more safely than a fixed startup baseline.

Each detected deviation contains:

```text
ROOT EVENT
battery.voltage down
confidence: 0.91
evidence: t-0.50s .. t+0.75s

    -> likely_caused

motor.output instability
confidence: 0.84

    -> likely_caused

attitude deviation
confidence: 0.78

    -> likely_caused

position / altitude deviation
```

`likely_caused` in v0.1 is intentionally conservative: it requires temporal proximity plus a plausible signal-family transition (for example power -> actuation -> attitude -> motion). Other ordered events are labeled `followed_by`. This is evidence organization, not a claim of mathematically proven causation.

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
          +----> ordered causal/follow-up chain
          |
          v
 evidence-backed JSON report
```

## v0.1 completion gate

v0.1 is considered complete when:

1. the public PX4 benchmark logs download reproducibly,
2. PAMIR parses and analyzes all benchmark logs without crashing,
3. root-event ordering is consistent with the published incident narrative on the incident set,
4. the successful control case has materially fewer/less-severe false positives,
5. tests and GitHub Actions pass on the final validation branch.

## Safety boundary

PAMIR focuses on reliability, telemetry analysis, test/measurement, incident reconstruction, and mission assurance. It is not intended for weapon control, targeting, engagement, or autonomous attack functions.
