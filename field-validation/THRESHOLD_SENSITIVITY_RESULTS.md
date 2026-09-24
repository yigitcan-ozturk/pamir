# Corpus v1 Threshold Sensitivity Results

Frozen PAMIR v0.1 remains unchanged. Threshold 7.0 is the frozen reference.

| threshold | healthy false roots | false-root rate | incident roots | incident root-detection | unknown roots | roots changed vs 7 |
|---:|---:|---:|---:|---:|---:|---:|
| 5.0 | 26/33 | 78.79% | 3/6 | 50.00% | 10/11 | 29 |
| 6.0 | 21/33 | 63.64% | 3/6 | 50.00% | 11/11 | 16 |
| 7.0 | 16/33 | 48.48% | 3/6 | 50.00% | 10/11 | 0 |
| 8.0 | 11/33 | 33.33% | 3/6 | 50.00% | 10/11 | 16 |
| 9.0 | 11/33 | 33.33% | 3/6 | 50.00% | 10/11 | 22 |
| 10.0 | 13/33 | 39.39% | 3/6 | 50.00% | 10/11 | 27 |

## Interpretation boundary

These are sensitivity diagnostics, not calibrated causal-accuracy estimates. Healthy labels remain independent source labels; unknown cases remain unknown. No candidate threshold is promoted into frozen v0.1 by this report.

## Post-run observations

- Raising the generic threshold from 7.0 to 8.0 reduces observed healthy-control material roots from 16/33 to 11/33 while the descriptive incident-root count remains 3/6 on this corpus.
- Threshold 9.0 retains the same 11/33 healthy-control rate but changes 22 roots relative to the frozen reference, so equal aggregate rate does not imply root stability.
- Threshold 10.0 is non-monotonic: healthy-control roots increase to 13/33. FV-H002, FV-J001, FV-J002, FV-J003 and FV-J004 show roots at 10.0 after having no root at 8.0/9.0. This confirms that a single global threshold cannot be interpreted as a simple monotonic false-root control under the frozen multi-detector/root-selection semantics.
- At the frozen 7.0 reference, 15/16 healthy false roots are in the estimation family and 1/16 is power. The dominant repeated signal is estimator output-tracking error, but innovations and magnetic-strength signals also appear.
- Unknown cases remain root-heavy (10/11 at the frozen reference), and remain excluded from false-root claims.

No threshold change is recommended from this experiment alone. The next lane is false-root mechanism analysis and candidate calibration outside frozen v0.1.
