# PAMIR-CUAS Validation Matrix

| Gate | Evidence type | Expected result |
|---|---|---|
| CUAS-001 | Controlled stale evidence | causal attribution + counterfactual correction |
| CUAS-002 | Controlled sensor disagreement | disagreement/confidence attribution |
| CUAS-003 | Controlled out-of-order timing | temporal causal attribution |
| R01 | MMAUD real recording | temporal association within declared gate |
| R02 | MMAUD real recording, independent window | temporal association within declared gate |
| R03 | MMAUD real recording, independent window | temporal association within declared gate |
| Evidence report | Deterministic software gate | stable canonical report + SHA-256 |
| DRE/ARC | Deterministic software gate | alert/isolate/validate + promote-or-rollback |
| DEMO-ACCEPT-001 | End-to-end controlled demonstrator | deterministic evidence + bounded recovery audit |

Controlled fixtures and controlled fault injections are never represented as faults observed in the original MMAUD recording.
