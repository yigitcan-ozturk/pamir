# PAMIR-CUAS Demonstrator Acceptance

The demonstrator acceptance gate is intentionally narrow and deterministic.

## Acceptance flow

1. Ingest a provenance-labelled controlled incident fixture.
2. Run deterministic incident analysis and causal/counterfactual evaluation.
3. Build the canonical machine-readable evidence report and SHA-256 evidence hash.
4. Feed detected degradation to the bounded Deterministic Resilience Engine (DRE/ARC).
5. Alert and isolate the degraded evidence source.
6. Validate the candidate recovery using the forensic validation result.
7. Terminate in a bounded `RECOVERED` or `ROLLBACK` state.
8. Re-run the complete flow and require byte-equivalent evidence serialization and identical resilience audit state.

## Acceptance command

```bash
pytest -q tests/test_cuas_demonstrator_acceptance.py
```

Repository acceptance additionally requires the complete test suite to pass in GitHub Actions.

## Scope

This gate validates mission-assurance software behavior only. It contains no target engagement, weapon control, terminal guidance, interception logic, firing solution, or effector command.
