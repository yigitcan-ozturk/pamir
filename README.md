# PAMIR

**Post-Mission Autonomous Incident Reconstruction**

PAMIR is an offline-first incident forensics engine for autonomous systems.

Its first goal is simple:

> **Tell me what failed first — and prove it.**

PAMIR ingests mission logs, normalizes telemetry, identifies the first meaningful deviation, reconstructs the downstream failure chain, and produces an evidence-backed incident report.

## v0.1 scope

- PX4 ULog ingestion
- normalized event timeline
- robust baseline anomaly detection
- first-deviation analysis
- failure-chain reconstruction
- evidence-backed JSON incident report
- local/offline operation

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

The first v0.1 detector uses a robust median/MAD baseline per signal, then reports the earliest signal whose deviation crosses the configured threshold. The report includes the first deviation and the first ordered set of downstream deviations as an initial failure chain.

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
 robust deviation detector
          |
          +----> first deviation
          |
          +----> ordered failure chain
          |
          v
 evidence-backed JSON report
```

## Project status

v0.1 core is now implemented on `feat/v0.1-core`. The next validation step is to run the pipeline against public PX4 flight logs and tune signal selection / anomaly scoring from real incidents.

## Safety boundary

PAMIR focuses on reliability, telemetry analysis, test/measurement, incident reconstruction, and mission assurance. It is not intended for weapon control, targeting, engagement, or autonomous attack functions.
