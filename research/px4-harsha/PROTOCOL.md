# Harsha PX4: EOA vs FRD causal-evidence protocol

Research lane only. PAMIR v0.1 frozen baseline must remain unchanged.

Source log: https://review.px4.io/plot_app?log=452d7328-c961-49d4-b608-33ee82d99133

## Supplied observations (not independently reproduced in this lane)
- Attitude/setpoint divergence: 462.123 s
- 462.532 s: tilt actual 46.3°, setpoint 4.8°
- 462.862 s: tilt actual 82.6°, setpoint 5.3°
- 462.586 s: actuator outputs [1999,109,1999,109]
- 467.388 s: fd_roll; 468.015 s: flight termination
- Primary EKF instance 1: mag_field[0] ratio 3.241 at 456.740 s; mag_field[2] ratio 12.411 at 455.242 s
- Elevated magnetometer innovation test ratios reported on both EKF instances.
- Earlier anomalies reported at least 20 s before visible attitude divergence; actual onset unverified.

## Definitions
EOA: earliest observed anomaly *under an explicitly stated detector, topic coverage, and valid time interval*. Not necessarily earliest physical fault.
FRD: first relevant departure from a defined reference with quantified detection rule, temporal uncertainty and relevance evidence. The currently supplied 462.123 s is first *identified* attitude divergence, not proven globally earliest relevant divergence.
CH: falsifiable causal hypothesis with mechanism, supporting/contradicting observations, missing evidence and status. Temporal precedence alone never establishes causality.

## Mandatory evidence gates
1. Preserve raw ULog hash, source URL, retrieval date, parser version, PX4 firmware metadata, topic inventory and timestamp domain.
2. Inspect *entire* EKF innovation and test-ratio history per estimator instance, including quiet baseline intervals. Detect threshold exceedance intervals, gaps, recurrence and duration. Do not use isolated peak values as onset.
3. Reconstruct selector history (e.g. estimator_selector_status primary_instance and changes) and estimator_status/flags per instance. Distinguish selected estimator from non-selected instance at each timestamp; check topic availability and field naming for this firmware.
4. Align innovation, attitude, attitude setpoint, rates, control allocation, actuator outputs, failures and vehicle status using ULog timestamps. Report interpolation policy and maximum tolerable gap; do not interpolate through dropouts.
5. Compare hypotheses H1 magnetometer -> selected EKF attitude -> controller; H2 estimator selection/switching; H3 independent control/actuator problem; H4 recurrent background magnetic anomaly unrelated to loss. Add alternatives from actual data.
6. For each proposed causal edge demand temporal consistency, intermediate mechanism evidence, alternatives/contradictions and coverage. Missing intermediate observations => UNRESOLVED, not CONFIRMED.
7. Record negative findings and data-coverage limits. Counterfactuals remain simulations/hypotheses, never observed effects.

## Outputs / acceptance criteria
- Machine-readable Evidence Object: immutable source metadata, EOA candidates, FRD candidates, selector timeline, hypotheses, evidence links, contradictions, unknowns, reproducibility.
- Plots and CSV: full-flight per-instance mag ratios; pre-event vs nominal baseline; selector and flags; synchronized event timeline.
- Automated tests: pre-existing anomalies do not automatically become causal; missing selector data stays unknown; nonselected instance peak cannot be assigned to selected estimator; gaps prevent false onset claims.
- Outcome labels: SUPPORTED / CONTRADICTED / UNRESOLVED for each *hypothesis*, not a root-cause label by timestamp.
- Do not merge into frozen baseline without independent reproduction and review.

## Current evidence status
Supplied event timestamps are recorded as USER_REPORTED_VERIFIED; independent full-flight reconstruction PENDING_RAW_ULOG. No causal edge confirmed.
