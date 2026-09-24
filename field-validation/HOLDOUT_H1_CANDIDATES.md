# Holdout v1 — Blind Candidate Register H1

Status: PRE-SCORING. PAMIR output has not been used to assign these labels.

Corpus v1 UUID leakage check performed before registration. Any UUID already used in Corpus v1 is excluded.

## Incident candidates

| Case | UUID | Source | Independent basis |
|---|---|---|---|
| HO-H1-I01 | df00d3ed-5412-454b-a4d8-58bafdddc556 | PX4 issue #22193 | Reporter states mission flight crashed 5–8 s after takeoff. |
| HO-H1-I02 | 5d49c71f-0608-4677-b551-70dfcfe7701d | PX4 issue #13452 | Reporter states offboard takeoff without valid local position led to EKF instability and crash. |
| HO-H1-I03 | e79ca622-a5d7-4b76-9d08-26e8b75273e6 | PX4 issue #22465 | Reporter states unexpected yaw rotations, building strike and near-crash. |
| HO-H1-I04 | 44fcd17a-694d-431e-a02f-74c51f8d3cda | PX4 issue #15289 | Reporter states motors stopped in mission and vehicle fell from 120 m. |

These are incident labels only. The source narrative does not establish PAMIR root causation.

## Healthy-control candidates

PX4 v1.16 release-test issue #24188 marks the referenced test submissions PASS/green or the individual test explicitly Result: Pass. Only UUIDs not found in Corpus v1 are registered.

| Case | UUID | Source basis |
|---|---|---|
| HO-H1-H01 | 7c61581e-3022-4e9f-83f6-646ffa803d89 | v1.16 RC3 release-test submission; mission + automatic landing; parent result green; findings none |
| HO-H1-H02 | eea50903-059c-4512-8aa9-90b4edd1e264 | same independent PASS submission |
| HO-H1-H03 | 616c9b4f-0f48-4b6e-97f1-5ceef3be31e9 | same independent PASS submission |
| HO-H1-H04 | 502970dc-a4a8-414e-8da6-4c7e1a6a51e7 | same independent PASS submission |

## Excluded for leakage

The following otherwise useful issue/release-test UUIDs were already present in Corpus v1 and are not admissible to holdout: issue #27879 crash logs; issue #26910 VOXL2 logs; v1.16 release-test PASS logs 07e64eb7, 9f9d4ed9, 67332627, 4ecae679, 7bdac691, 5c8ce834, e689fe73, ba880f55.

## Gate

H1 contains 8 blind-labelled, leakage-free candidates: 4 incident + 4 healthy_control. They are candidates, not accepted holdout cases, until original ULog retrieval, SHA256 pinning, telemetry sufficiency, and exact deterministic replay pass.

No PAMIR scoring may be used to alter these source labels.
