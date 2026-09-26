# Candidate v2 — Corpus v1 Discovery Audit Result

GitHub Actions run: https://github.com/yigitcan-ozturk/pamir/actions/runs/36240212698
Artifact: pamir-v2-discovery-audit (ID 10905289924)

## Verified execution
- 50/50 Corpus v1 real-flight cases processed successfully.
- Source labels: 33 healthy_control, 6 incident, 11 unknown.
- Frozen PAMIR 7.0: 16/33 healthy material roots, 3/6 incident material roots.
- Across all rooted cases: estimation 27, power 2.
- The generated case-level JSON contains forward 3-second family counts, distinct signal counts, same-signal event/timestamp counts and span. These are observational support diagnostics, **not** independently proven physical sensor corroboration.

## Decision boundary
Do not claim Candidate v2 efficacy or select a rule from aggregate results alone. The audit generated diagnostics; it did not implement or test a selector. Candidate v1 is rejected for promotion. Spent Holdout v1 must not be used to design Candidate v2. Frozen PAMIR v0.1 and all baseline evidence remain unchanged.

## Next experiment
Evaluate predeclared temporal-support and distinct-signal support hypotheses **on Corpus v1 only**, preserving frozen non-estimation roots. Produce full case-level root migration and incident-retention tables, including no-conclusion cases, before selecting a single versioned v2 implementation. Distinct signals do not establish independent channels; any physical-channel claim requires explicit provenance mapping.
