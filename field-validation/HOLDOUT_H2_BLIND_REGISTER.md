# Holdout v1 — Batch H2 Blind Candidate Register

Status: source-labelled, NOT PAMIR-scored.

Source: PX4/PX4-Autopilot issue #27470, v1.18 release-candidate flight-testing archive, comment 4848654358 (2026-06-30). The contributor explicitly marks the test-card rows below PASS and identifies a Holybro X500 V2, Pixhawk 6XRT/NXP, PX4 1.18.0-alpha1. Labels are locked before PAMIR execution.

| Case | PX4 issue | Flight Review UUID | Pre-score class | Source PASS basis |
|---|---:|---|---|---|
| H2-001 | #27470 | 2e1ea627-608c-41bb-9ad3-8686562eed61 | healthy_control | MC_04 RC Loss — PASS |
| H2-002 | #27470 | 824f1a9b-572a-447f-a816-3c6e484fde13 | healthy_control | MC_04 RC Loss — PASS |
| H2-003 | #27470 | 6e3d7215-b65a-4343-8c53-af956e6b5c01 | healthy_control | MC_04 RC Loss — PASS |
| H2-004 | #27470 | 1f5dfb99-2953-421e-97a6-51665f902450 | healthy_control | MC_04 Datalink Loss — PASS |
| H2-005 | #27470 | 3727071f-a231-4099-be86-03ad771bc0fb | healthy_control | MC_04 Datalink Loss — PASS |
| H2-006 | #27470 | de5c8a0a-a96a-48b1-9ab6-b371d9fc182b | healthy_control | MC_04 Datalink Loss — PASS |
| H2-007 | #27470 | ea91f3d5-ca6d-46d6-8bc2-5f9345a1573f | healthy_control | MC_04 Battery Tests — PASS |
| H2-008 | #27470 | b783c327-3215-42f1-8815-e3812351e9cd | healthy_control | MC_04 Battery Tests — PASS |
| H2-009 | #27470 | 9ef3519a-deab-4b55-add2-fc6cf7c46528 | healthy_control | MC_04 Battery Tests — PASS |
| H2-010 | #27470 | 9e406ea0-d62a-4891-bd27-ff9eff0c84ee | healthy_control | MC_04 Battery Tests — PASS |
| H2-011 | #27470 | c96f694b-0147-4d83-bd7c-1353c66dcecf | healthy_control | MC_08 DSHOT Stabilized — PASS |
| H2-012 | #27470 | 64f7c9f0-d951-48cb-9668-298fac1077db | healthy_control | MC_08 DSHOT Stabilized — PASS |

Corpus v1 UUID leakage check before registration: all 12 UUIDs absent from field-validation/corpus/manifest.json.

Rules:
- These source labels are locked before PAMIR scoring.
- PASS means the declared PX4 test objective passed; it is used as the independent healthy-control label and does not imply every telemetry channel is anomaly-free.
- Acquisition must pin original ULog SHA256 and repeat Corpus v1 UUID/SHA duplicate checks.
- Missing/unavailable sources are quarantined, not replaced after seeing PAMIR output.
- PAMIR output cannot change these labels.
