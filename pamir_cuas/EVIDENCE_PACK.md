# PAMIR-CUAS Demonstrator Evidence Pack

**Track:** `feat/cuas-forensics-prototype`  
**Purpose:** reproducible technical demonstrator acceptance  
**Boundary:** mission assurance, incident reconstruction, validation, and resilience evidence only. No targeting, engagement, guidance, interception, firing solution, or effector control.

## Verified evidence chain

Source / controlled fixture -> deterministic processing -> causal analysis -> counterfactual result -> machine-readable evidence report -> DRE bounded recovery decision -> CI validation.

## Validation cases

- CUAS-001: controlled stale-evidence false-positive regression gate — CI PASS.
- CUAS-002: controlled sensor-disagreement/confidence-dominance regression gate — CI PASS.
- CUAS-003: controlled temporal out-of-order causal-attribution gate — CI PASS.
- R01: MMAUD V1 DJI Mavic3 real-recording temporal association — CI PASS.
- R02: independent MMAUD V1 DJI Mavic3 real-recording temporal window — CI PASS.
- R03: independent MMAUD V1 DJI Mavic3 real-recording temporal window — CI PASS.
- Evidence Report: deterministic canonical JSON + SHA-256 evidence hash — CI PASS.
- DRE/ARC: bounded detect/alert/isolate/validate/promote-or-rollback state machine — CI PASS.
- Demonstrator Acceptance: end-to-end forensic report + resilience audit gate — pending/verified by the branch CI associated with this pack.

## Real-data provenance

R01/R02/R03 use timestamp-derived windows from the user-supplied MMAUD V1 Mavic3 ground-truth and enhanced-radar archives. The original recording is treated as real sensor data. Controlled faults used elsewhere in the demonstrator are explicitly labelled controlled injections and are **not** represented as incidents present in the MMAUD source recording.

Full archive inspection used 833 ground-truth `.npy` files and 2,548 enhanced-radar `.npy` files. All 833 ground-truth timestamps had a nearest radar timestamp within 50 ms in the inspected recording.

## Reproducibility

From a clean checkout of this branch:

```bash
python -m pip install -e '.[dev]'
pytest -q
```

The GitHub Actions workflow `.github/workflows/test.yml` is the acceptance authority for repository-level PASS/FAIL.

## Acceptance criteria

The demonstrator is acceptance-ready only when all branch tests complete successfully in GitHub Actions. The end-to-end gate must produce deterministic evidence, preserve provenance, record source isolation, and terminate in a bounded validated state (`RECOVERED` or `ROLLBACK`).

## Limitations

This evidence pack demonstrates software-level deterministic reconstruction, temporal association, causal attribution, counterfactual analysis, evidence generation, and bounded resilience behavior. It does not establish field qualification, operational C-UAS effectiveness, safety certification, military certification, or weapon-system capability. A subsequent blind validation should use unseen controlled data supplied by an authorized system integrator or test authority with acceptance criteria declared before execution.
