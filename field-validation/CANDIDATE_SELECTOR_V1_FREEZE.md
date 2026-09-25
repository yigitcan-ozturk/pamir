# Candidate Selector v1 — Freeze Record

Candidate Selector v1 was frozen **before any PAMIR scoring of the independent holdout**.

- Specification commit: `53a320a18e65159e420424b8769bc38e5b00f2a1`
- Selector implementation commit: `a54d0bb2c4d26f4bbbdc211a124c07978e4169f1`
- Semantic test commit: `f806804162a1163a438987b17e1474479001c153`
- Freeze workflow run: `36096921225`
- Validation result: PASS
- Frozen selector SHA256: `5fc5db552b47701c30a33b7fd252ee6f14f3a502254869cd8762926e82410244`

The selector is external field-validation code. `pamir/engine.py` and PAMIR v0.1.0 remain unchanged.

Any selector change after this record creates a new candidate version and cannot use the current independent holdout for tuning.
