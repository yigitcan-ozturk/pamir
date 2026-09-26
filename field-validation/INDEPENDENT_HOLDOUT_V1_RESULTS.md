# Independent Holdout v1 — Locked Evaluation Findings

Evaluation run: https://github.com/yigitcan-ozturk/pamir/actions/runs/36227739563
Workflow branch head: `7b813485560923e0414f02c453233c6edd70cd38`
Selector frozen SHA256: `5fc5db552b47701c30a33b7fd252ee6f14f3a502254869cd8762926e82410244`

## Predeclared cohort
20 accepted_pre_pamir real public ULogs: 12 independently source-labelled healthy controls, 8 independently source-labelled incidents. No quarantined cases were scored.

## Results
| Metric | Frozen PAMIR v0.1 | Candidate Selector v1 |
|---|---:|---:|
| Healthy controls with material root | 6/12 (50%) | 6/12 (50%) |
| Incident cases with material root | 6/8 (75%) | 6/8 (75%) |
| Changed roots | — | 0 |

- Deterministic replay: true
- Incident roots lost relative to frozen: none
- Advancement gate: **FAILED** (healthy false-root rate was not lower)
- Workflow: SUCCESS denotes successful execution, **not** successful candidate advancement.

## Decision
**Do not promote Candidate Selector v1.** Its actual implementation was identical to frozen behavior on all 50 discovery cases and all 20 independent holdout cases. The earlier threshold-survival proxy reduction was not demonstrated by Candidate v1 and is not a valid product claim.

The 20-case holdout has now been exposed to candidate results. It is **spent for any future redesigned selector**. A future Candidate v2 must be designed and frozen using discovery-only evidence and then evaluated on a newly acquired, independently source-labelled, previously unseen holdout. No post-hoc tuning on this holdout.

Frozen PAMIR v0.1.0, frozen threshold 7.0, existing Evidence Pack and prior validation artefacts remain unchanged.

## Interpretation limitations
The labels establish source-reported healthy/incident status, not independently proven causal root correctness. A material root in an incident is a detection proxy, not proof of correct causal attribution. This holdout is small and has a concentrated healthy test source; report 6/12 and 6/8 as cohort measurements, not population performance estimates.
