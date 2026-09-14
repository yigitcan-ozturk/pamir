\# PAMIR v0.2 Evidence Calibration Plan



\## Objective



PAMIR v0.2 will improve evidence calibration without changing the frozen v0.1 baseline.



v0.1 remains the reference implementation and validation gate.



\## Baseline



Frozen baseline:

\- PAMIR v0.1.0

\- 5 required incident ULogs

\- 3 required control ULogs

\- 3 / 3 external clean-log PASS

\- no change to v0.1 detection semantics



\## v0.2 Calibration Goals



1\. Measure false-positive behaviour on clean telemetry.

2\. Characterize raw deviation density before material-root selection.

3\. Measure confidence-score distributions across:

&#x20;  - clean logs

&#x20;  - degraded / ambiguous logs

&#x20;  - confirmed incident logs

4\. Separate anomaly strength from causal confidence.

5\. Expose calibration metrics without changing v0.1 pass/fail behaviour.

6\. Preserve evidence provenance for every calibration result.



\## Initial Metrics



For every analyzed ULog record:



\- sample\_count

\- signals\_analyzed

\- raw\_deviation\_count

\- raw\_deviation\_rate

\- material\_root\_present

\- root\_signal

\- root\_confidence

\- first\_deviation\_timestamp

\- evidence\_window\_size

\- failure\_chain\_length



Derived calibration metrics:



\- deviations per 10,000 samples

\- deviations per analyzed signal

\- material-root conversion rate

\- confidence distribution

\- clean-log false-positive rate



\## Phase 1 — Measurement Only



No threshold changes.



The first v0.2 implementation will only expose measurements from the existing v0.1 engine.



Success condition:



\- v0.1 outputs remain unchanged

\- calibration metrics can be generated reproducibly

\- clean and incident telemetry can be compared quantitatively



\## Phase 2 — Calibration Dataset



Dataset groups:



\### Clean

\- External Case #010

\- External Case #011

\- External Case #012



\### Required controls

\- github-indoor-control-2025

\- follow-me-control-2020

\- stabilized-control-2022



\### Confirmed incidents

\- existing five required incident benchmark ULogs



\## Guardrails



\- Do not modify frozen v0.1 semantics.

\- Do not tune thresholds to individual logs.

\- Do not label raw deviations as causal failures.

\- Do not interpret confidence as probability of causation.

\- Every calibration result must retain source provenance.



\## First implementation task



Create a calibration-report layer that consumes PAMIR v0.1 analysis output and produces additional measurement fields without affecting the original report or conclusion.



