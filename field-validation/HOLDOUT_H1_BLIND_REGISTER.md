# Holdout v1 — Batch H1 Blind Candidate Register

Status: source-labelled, NOT PAMIR-scored.

This register was created before PAMIR scoring. Corpus v1 UUIDs were checked first. Two recent software-crash logs from PX4 issue #27879 were rejected for holdout leakage because their UUIDs already occur in Corpus v1.

| Case | PX4 issue | Flight Review UUID | Pre-score class | Narrative basis | Gate |
|---|---:|---|---|---|---|
| H1-001 | #22193 | 2bcae38b-6a3d-4439-94ec-7d697b06838e | healthy_control | Reporter states the autotune flight went well and parameters saved successfully. | acquire/verify |
| H1-002 | #22193 | df00d3ed-5412-454b-a4d8-58bafdddc556 | incident | Reporter states mission flight crashed 5–8 s after takeoff. | acquire/verify |
| H1-003 | #21895 | 8b05047d-cc5b-4b7c-ba2e-c84877f04a19 | incident | Mission/Position flight; sudden yaw-estimate jump, instability, crash. | acquire/verify |
| H1-004 | #21895 | d6b953ae-1128-4e75-b663-4468ddb8d614 | incident | Position/hover flight; sudden yaw-estimate jump causing crash. | acquire/verify |
| H1-005 | #21895 | d96c98a6-f429-429d-9219-94173580b73f | incident | Offboard flight; ~50° yaw jump, instability, takeover and landing. | acquire/verify |
| H1-006 | #24830 | 493454d6-f936-4068-b3cd-53738a62e02e | incident | Reporter states aircraft suddenly fell from sky and software errors were present in log. | acquire/verify |
| H1-007 | #25415 | 0a3c1eac-bae4-4214-a54c-791d303c05fe | incident | Reporter states normal flight transitioned to violent oscillation and crash. | acquire/verify |
| H1-008 | #22193 | 0d3d9e8a-6f76-4586-84c8-07d19e397de4 | unknown | Pre-crash migration flight; narrative does not justify healthy label. | acquire/verify |

Excluded before scoring:
- PX4 #27879 / 02a49fdc-6e69-4aba-8439-e18259c65ebb — Corpus v1 UUID leakage.
- PX4 #27879 / f2cdb24d-3d6d-44de-8912-ea618e465811 — Corpus v1 UUID leakage.
- PX4 #17688 / 7b8ce0d1-52c8-4c32-ad14-55b48b99d5d7 — source narrative may describe a ground/QGC reproduction rather than a qualifying real flight; held out of H1 pending evidence.

Rules:
- Labels above are immutable for H1 unless source evidence itself is corrected before PAMIR scoring.
- ULog retrieval, SHA256 pinning, real-flight/telemetry sufficiency and duplicate checks happen next.
- Failed acquisition is quarantine, never substitution.
- PAMIR output cannot strengthen or change source labels.
