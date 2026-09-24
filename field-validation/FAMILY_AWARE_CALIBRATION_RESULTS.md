# Family-Aware Calibration Proxy Results — Corpus v1

Run: 35968806191  
Artifact: pamir-corpus-v1-family-aware-calibration  
Artifact SHA256: 70acacab6b7878cb01397a89d17ddff532be81dd2d3550f8e2e35c6ee999607e

Frozen PAMIR v0.1.0 remains unchanged.

| candidate | healthy false roots | false-root rate | incident roots | unknown roots | roots changed vs frozen |
|---|---:|---:|---:|---:|---:|
| frozen_7 | 16/33 | 48.48% | 3/6 | 10/11 | 0 |
| estimation_survival_8 | 11/33 | 33.33% | 3/6 | 10/11 | 14 |
| estimation_survival_9 | 9/33 | 27.27% | 3/6 | 10/11 | 18 |
| estimation_survival_10 | 9/33 | 27.27% | 3/6 | 10/11 | 20 |

## Interpretation

The bounded estimation-family threshold-survival proxy suppresses observed healthy-control false roots from 16 to 9 at the 9/10 candidates while retaining the same 3/6 incident roots observed by frozen v0.1 in this corpus. That is a 43.75% reduction in observed healthy false roots relative to the frozen reference.

This is not evidence that threshold 9 or 10 should replace the frozen threshold. Root migration remains substantial: 18 roots change at the 9 candidate and 20 at the 10 candidate. The experiment is a sensitivity proxy, not a replacement root selector, and the incident set is small and unbalanced.

The next admissible step is an independently specified family-aware root selector evaluated on a holdout corpus. Corpus v1 must not be used both to tune and to claim independent validation.

## Decision

- Keep frozen v0.1.0 unchanged at its existing semantics.
- Do not promote any proxy candidate.
- Use Corpus v1 findings to define, not validate, a candidate family-aware selector.
- Build an independent holdout validation set before making calibration claims.
