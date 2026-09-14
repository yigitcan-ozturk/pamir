# PAMIR-CUAS — Forensics Engine Prototype v0.1

Status: research prototype

## Mission

PAMIR-CUAS is a vendor-neutral, post-test validation and incident-reconstruction layer for Counter-UAS systems. It does not perform weapon control, targeting, engagement, guidance, or interception.

The prototype answers one question:

> Why did a detection, classification, or track outcome become wrong?

## Prototype hypothesis

Given normalized sensor/C2 observations plus ground truth, PAMIR-CUAS reconstructs an evidence lineage and tests whether timing, stale data, sensor disagreement, association, or confidence transformation materially contributed to a false positive or missed detection.

## v0.1 demonstrator

Input:
- synthetic radar observations
- synthetic RF observations
- synthetic EO/IR observations
- C2/fusion output
- independent ground truth
- timestamps and confidence values

Core analysis:
1. build an evidence graph for one incident;
2. detect temporal-integrity anomalies (clock offset, stale/out-of-order observations);
3. identify sensor disagreement;
4. compare final outcome with ground truth;
5. run safe offline counterfactual replays by excluding/correcting evidence;
6. generate a causal-attribution report explaining which upstream factor changed the outcome.

Output example:

`FALSE_POSITIVE -> temporal anomaly detected -> RF evidence stale by 420 ms -> stale RF evidence materially increased fused confidence -> timestamp-corrected replay removes false positive.`

This statement must be supported by replay evidence, not inferred from correlation alone.

## Evidence graph

Minimum node types:
- GroundTruth
- SensorObservation
- TrackAssociation
- ConfidenceTransformation
- FusionDecision
- CounterfactualRun

Minimum edge types:
- OBSERVED_BY
- ASSOCIATED_WITH
- CONTRIBUTED_TO
- TRANSFORMED_INTO
- COMPARED_WITH
- REPLAYED_AS

Each evidence record carries:
- source_id
- event_time
- ingest_time
- observation_id
- track_id (when available)
- confidence
- payload hash
- provenance metadata

## Initial failure taxonomy

- TEMPORAL_CLOCK_OFFSET
- TEMPORAL_STALE_EVIDENCE
- TEMPORAL_OUT_OF_ORDER
- SENSOR_DISAGREEMENT
- ASSOCIATION_MISMATCH
- CONFIDENCE_DOMINANCE
- FALSE_POSITIVE
- MISSED_DETECTION
- INSUFFICIENT_EVIDENCE

## Acceptance gate for prototype v0.1

The first demonstrator passes only if a synthetic incident can be reproduced deterministically and the engine can:

- identify the known injected fault;
- trace the affected decision back to contributing evidence;
- run at least one counterfactual replay;
- show that correcting/removing the injected fault changes or does not change the outcome;
- distinguish causal evidence from merely correlated anomalies;
- produce a machine-readable incident report.

## Safety boundary

Explicitly out of scope:
- target selection
- weapon control
- engagement decisions
- interceptor guidance
- firing solutions
- effector optimization

## Next implementation steps

- freeze normalized event schema
- create synthetic incident Case CUAS-001
- implement deterministic timeline normalizer
- implement evidence graph builder
- implement temporal anomaly detector
- implement counterfactual replay harness
- create regression tests and evidence report
