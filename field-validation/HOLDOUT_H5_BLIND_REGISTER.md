# Holdout H5 Blind Incident Register

Status: source-labelled; PAMIR not scored. This batch prioritizes logs.px4.io-linked real-flight incident reports and excludes Corpus v1 UUIDs.

| Case | Flight Review UUID | Label | Source narrative |
|---|---|---|---|
| H5-001 | 8846a52a-eead-4e24-a30d-72c0f22f5f7c | incident | Repeated RC-loss/failsafe transitions; reporter states hexacopter crashed. |
| H5-002 | 7743e2cd-4654-4f5f-87db-36c787df42b6 | incident | Offboard hexacopter; one motor went full power and vehicle crashed. |
| H5-003 | 36440ff4-6aaf-4dd7-9a29-9fb9bd9ad3d8 | incident | Primary EKF change/altitude jump; motors stopped and vehicle fell. |
| H5-004 | 5a129e78-ebf0-4ae1-a331-69c0af8ec51a | incident | Position-mode hexacopter began spinning uncontrollably and crashed. |
| H5-005 | 2e6046ed-5282-48cd-831e-4978e197b453 | incident | Reporter states vehicle crashed after vertical thrust failed to track ascent demand. |

Labels are locked from public source narratives before PAMIR execution. All UUIDs were absent from Corpus v1 at registration. Acquisition must repeat UUID/SHA leakage checks; unavailable logs are quarantined without substitution after PAMIR output.
