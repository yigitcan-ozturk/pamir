# PAMIR

**Post-Mission Autonomous Incident Reconstruction**

PAMIR is an offline-first incident forensics engine for autonomous systems.

Its first goal is simple:

> **Tell me what failed first — and prove it.**

PAMIR will ingest mission logs, normalize telemetry, identify the first meaningful deviation, reconstruct the downstream failure chain, and produce an evidence-backed incident report.

## v0.1 scope

- PX4 ULog ingestion
- normalized event timeline
- anomaly detection
- first-deviation analysis
- failure-chain reconstruction
- evidence-backed incident report
- local/offline operation

## Project status

PAMIR is in active development. The first milestone is a reproducible analysis pipeline over public PX4 flight logs.

## Safety boundary

PAMIR focuses on reliability, telemetry analysis, test/measurement, incident reconstruction, and mission assurance. It is not intended for weapon control, targeting, engagement, or autonomous attack functions.
