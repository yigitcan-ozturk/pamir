# PAMIR — Evidence Operating System for Autonomous Machines

> PAMIR turns autonomous-system behaviour into evidence.

## Boundary

PAMIR v0.1.0 is a frozen compatibility baseline. Its incident/control corpus, validation expectations, replay semantics, external-validation artefacts, and report contract are not retuned by this lane.

This lane is additive and begins at the output boundary of the existing deterministic reconstruction engine.

## Gap analysis

The current core already provides ULog ingestion, robust deviation detection, a selected material root, ordered failure-chain output, evidence windows, calibration provenance, root-stability analysis, and causal-order validation. Those capabilities answer a bounded form of **what happened first and what followed**.

The missing category-level primitives are:

1. an immutable, canonical evidence unit with provenance and integrity identity;
2. a graph that represents support, contradiction, temporal order, claims and unknowns without flattening them into one heuristic chain;
3. evidence-sufficiency semantics that explicitly distinguish proved, supported, contradicted and unknown;
4. first-divergence semantics that can compare observed behaviour with an expected/required trace, not merely find the first anomaly;
5. causal hypotheses separated from deterministic facts;
6. counterfactual replay with explicit intervention/model/version provenance;
7. accountability mappings from machine decisions to requirements, states, commands and evidence;
8. cross-incident pattern discovery over comparable evidence graphs.

## Architecture

```text
Frozen PAMIR v0.1.0
  ULog -> normalized samples -> deviations -> deterministic reconstruction
                         |
                         v
Evidence OS lane
  PAMIR Evidence Object
        -> Evidence Graph
        -> Evidence Sufficiency
        -> First-Divergence Comparator
        -> Causal Hypothesis Layer
        -> Counterfactual Replay
        -> Machine Accountability
        -> Multi-Incident Pattern Discovery
        -> Live Demonstrator
```

## PAMIR Evidence Object (PEO)

Every evidence-bearing fact becomes a canonical object with:

- stable object id;
- evidence kind;
- timestamp;
- subject;
- payload;
- source;
- provenance;
- explicit support/contradiction/unknown references;
- deterministic SHA-256 digest.

The initial adapter converts existing v0.1 deviations into PEOs without changing v0.1 detection or root selection.

## Evidence Graph

Nodes are PEOs. Edges are typed and must reference existing nodes. The graph serialisation is deterministic. The initial edge basis preserves the existing v0.1 temporal/signal-family reconstruction and labels that basis rather than overstating it as proof of causality.

## Evidence Sufficiency

Sufficiency is a first-class result, not an afterthought. The first implementation is intentionally conservative: it records what is known and what remains unknown. Later gates will make sufficiency requirement-specific and machine-checkable.

## First Divergence

Phase 1 exposes the earliest represented deviation. Phase 2 introduces an expected-trace/requirement comparator:

```text
observed state/command/response
            vs
expected state/command/response
            |
            v
first timestamp where the evidence-backed contract no longer holds
```

This distinction is critical: anomaly detection is not equivalent to requirement divergence.

## Counterfactual replay contract

Counterfactuals are never emitted as free-form causal claims. A replay must identify:

- original evidence graph digest;
- intervention;
- intervention timestamp;
- replay/model version;
- assumptions;
- changed downstream states;
- unchanged downstream states;
- unresolved outputs.

Until that model exists, the report says `not_run`.

## Next acceptance gates

1. PEO/graph deterministic serialisation and integrity tests.
2. Adapter over existing v0.1 reports with byte-stable output.
3. Expected-trace contract + first-divergence comparator.
4. Evidence-sufficiency rules with explicit unknown propagation.
5. Counterfactual replay interface and deterministic fixture.
6. Real ULog demonstration on an existing external case.
7. Live demonstrator rendering the graph, first divergence, known/unknown evidence, and counterfactual delta.
8. Cross-case graph signature prototype.

No gate may weaken the frozen v0.1 validation contract.
