# Holdout H2 Acquisition Results

Run: 35983961207
Artifact: 10801651178
Artifact digest: sha256:a7b746cb776cc870859bdf4719fcd16751cb112e07ebe25e8c385814f8500d05
PAMIR executed: **false**

All 12 blind-labelled H2 healthy controls were acquired successfully from the current PX4 Flight Review index.

- acquired_unscored: 12/12
- Corpus v1 UUID duplicates: 0
- Corpus v1 SHA256 duplicates: 0
- quarantined/rejected: 0
- source labels remain locked healthy_control.

Pinned SHA256 values are preserved in workflow artifact 10801651178. H2 now satisfies the protocol's healthy-control acquisition target (>=10), subject to the next telemetry-sufficiency and deterministic-replay acceptance gate.

Combined acquisition pool before scoring:
- H1: 1 acquired incident, 7 quarantined
- H2: 12 acquired healthy controls
- total acquired and unscored: 13
- healthy: 12
- incident: 1

The overall holdout minimum of 20 accepted cases and incident target >=6 are not yet met. No calibration or PAMIR scoring has been performed on H2.
