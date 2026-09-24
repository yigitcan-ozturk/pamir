# Holdout H1 Acquisition Results

Run: 35973204242
Artifact: 10796564432
Artifact digest: sha256:906a4ddac708e6f8908f4421eb3519fc94e71fba2070909a564dde6cd43ac34f
PAMIR executed: **false**

## Result

Eight blind-labelled H1 candidates were subjected only to source acquisition and Corpus v1 leakage checks.

- H1-006 / PX4 #24830 / UUID 493454d6-f936-4068-b3cd-53738a62e02e: **acquired_unscored**.
  - SHA256: 5d7476d8b1b9375eb67015ec9e25b38d4c8ecf70b830921e3931df059c6e0ddc
  - size: 2,680,565 bytes
  - Corpus v1 UUID duplicate: false
  - Corpus v1 SHA256 duplicate: false
  - pre-score class remains incident.
- H1-001, H1-002, H1-003, H1-004, H1-005, H1-007 and H1-008: **quarantined_source_unavailable** under the current Flight Review index. They are not substituted and are not scored.

## Holdout accounting

Accepted for the next telemetry/replay gate: 1 incident candidate.
Quarantined before scoring: 7.
Healthy controls acquired: 0.

This does not satisfy Independent Holdout v1. Continue acquisition from independent, narrative-bearing real/public sources. Frozen PAMIR v0.1.0 remains unchanged.
