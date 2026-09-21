# PAMIR Evidence Object Specification v0.1-draft

Status: EXPERIMENTAL / NOT PART OF PAMIR v0.1

## 1. EvidenceObject

An EvidenceObject is an immutable description of an observed execution event and the material needed to verify its recorded identity.

Required fields:

- evidence_id
- run_id
- event_type
- event_time
- observed_time
- source
- source_version
- subject_identity
- input_hash
- output_hash
- parent_evidence_ids
- content_reference
- integrity_status
- capture_policy

The object must not claim causation merely because one event precedes another.

## 2. EvidenceManifest

The manifest inventories EvidenceObjects belonging to a run and records integrity material sufficient to detect mutation, omission when detectable, or substitution of captured evidence.

Initial integrity primitive: SHA-256 content hashes. A later version may define chained or signed manifests; this draft does not claim cryptographic non-repudiation.

## 3. DecisionSnapshot

A DecisionSnapshot records the evidence set known to be available to the system at a specific decision boundary.

Minimum fields:

- decision_id
- run_id
- decision_time
- available_evidence_ids
- unavailable_expected_evidence_ids
- conflicting_evidence_ids
- model_identity
- model_version
- context_identity / context_hash
- policy_identity / policy_version where applicable

Historical availability must be distinguished from data retrieved after the decision.

## 4. ReconstructionReport

Allowed top-level evidence states:

- VERIFIED: required captured evidence is present and integrity checks pass.
- PARTIAL: reconstruction is possible but expected evidence is missing.
- INSUFFICIENT: available evidence cannot support the requested conclusion.
- CONFLICTED: material captured evidence disagrees and the conflict is unresolved.

A report must separate:

1. observed facts;
2. derived temporal/dependency relationships;
3. causal hypotheses;
4. missing evidence;
5. counterfactual results.

## 5. First divergence

First divergence is the earliest evidence-supported point at which an observed trajectory differs from a declared reference trajectory or invariant.

It is not automatically the root cause.

## 6. Replay semantics

PAMIR distinguishes:

- evidence reconstruction: deterministic reconstruction from preserved evidence;
- recorded-output replay: reuse of preserved historical outputs;
- live re-execution: a new execution against a model/tool/environment.

Live re-execution is not assumed deterministic. Any model, tool, policy, context, or environment difference must be recorded in replay provenance.

## 7. Evidence sufficiency

Sufficiency is evaluated against an explicit question or claim and its required evidence classes. It must never be presented as a probability of causation.

Example:

Decision D17 reconstructed.
Required evidence classes: 8.
Verified/present: 7.
Missing: tool result T8.
Result: PARTIAL.
Causal claim dependent on T8: unsupported.

## 8. Controlled validation scenarios

- stale context: prove which context version existed at decision time.
- conflicting evidence: preserve both observations and expose unresolved disagreement.
- tool timeout: distinguish unavailable-at-decision evidence from later data.
- mutated tool output: detect mismatch between preserved historical identity and later output.
- model/context change: distinguish historical reconstruction from live re-execution.

## 9. Compatibility direction

Prefer ingestion/adaptation of standard telemetry such as OpenTelemetry GenAI conventions rather than inventing a competing tracing protocol.

## 10. Baseline isolation

Nothing in this specification changes PAMIR v0.1 algorithms, benchmark corpus, validation gates, Evidence Pack, or external-validation artefacts.
