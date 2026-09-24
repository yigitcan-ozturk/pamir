# Independent Holdout Validation Protocol — v1

Status: PREDECLARED. This protocol defines the next PAMIR Field Validation gate before any holdout outcome is observed.

Frozen PAMIR v0.1.0, Corpus v1, its labels, Evidence Pack, and validated artefacts remain unchanged.

## Purpose

Test whether the calibration hypothesis derived from Corpus v1 generalises to previously unused real PX4 flights. Corpus v1 is discovery/tuning evidence and is not counted as independent validation.

## Holdout target

Minimum 20 previously unused, real, public PX4 ULogs:
- target >= 10 independently defensible healthy controls;
- target >= 6 incident flights;
- remaining cases may be unknown and stay unknown;
- seek more than one PX4 release, airframe/platform and uploader/source context where public evidence permits;
- no flight already present in Corpus v1 is admissible.

This is a minimum gate, not a claim of representativeness.

## Provenance gate

For every case preserve:
source URL/UUID -> public evidence/description -> original ULog -> SHA256 -> acquisition timestamp -> independent label -> label rationale -> acceptance/rejection reason.

Labels are assigned from source evidence before PAMIR/calibration output is inspected. PAMIR output must never relabel a source case.

## Predeclared comparisons

1. Frozen PAMIR v0.1.0 reference, unchanged.
2. Candidate family-aware selector derived from Corpus v1 mechanism findings.
3. No post-hoc threshold selection on holdout.

## Primary metrics

- healthy-control material-root rate;
- incident material-root retention relative to frozen reference;
- no-conclusion rate;
- root-family and root-signal migration;
- root timestamp shift;
- deterministic replay equality;
- per-platform/release descriptive breakdown when sample count permits.

Unknown cases are reported separately and excluded from false-root claims.

## Advancement gate

The candidate can advance beyond experimental status only if:
- deterministic replay is exact for every accepted holdout case;
- healthy-control false-root rate is lower than frozen reference on holdout;
- incident-root retention is not lower than frozen reference on holdout;
- no severe root-family/timestamp instability is hidden by aggregate metrics.

With small samples, results remain evidence for further validation, not production-performance guarantees.

## Stop conditions

Stop and document rather than tune on holdout if:
- candidate loses an incident root retained by frozen reference;
- provenance/label independence is compromised;
- duplicate/leaked Corpus v1 flight is found;
- deterministic replay fails.

Any redesign after inspecting holdout results creates a new candidate version and requires a fresh holdout set.
