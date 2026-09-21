# PAMIR Agent Evidence Layer — Experimental

Status: experimental research lane. This directory does not modify the PAMIR v0.1 validated baseline.

## Hypothesis

Standard agent observability can show execution traces. PAMIR tests whether an additional evidence layer can preserve and reconstruct the evidence state available to an autonomous system at decision time.

The experiment asks:

> Can an independent examiner reconstruct what evidence was available at decision time, verify its integrity, identify what is missing or conflicting, and distinguish observed facts from causal hypotheses?

## Pipeline

Execution -> Evidence Capture -> Integrity -> Decision Snapshot -> Evidence Graph -> Reconstruction -> Evidence Sufficiency -> First Divergence -> Causal Hypothesis -> Counterfactual / Replay Provenance

## Non-goals

This lane is not a replacement for OpenTelemetry, an LLM tracing platform, a prompt evaluator, or a generic agent monitoring UI. Existing telemetry should be accepted as input where practical.

## Initial controlled incidents

1. stale context
2. conflicting evidence
3. tool timeout / missing result
4. mutated tool output
5. model or context change

## Validation rule

Features survive only if they produce independently verifiable evidence beyond what a conventional execution trace already provides. The experiment may end in GO, MODIFY, or STOP.

See [SPEC.md](SPEC.md) for the first evidence-object contract.
