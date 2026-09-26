# Candidate v2 Corpus v1 true reselection results

Status: discovery-only, not independent validation and not frozen Candidate v2. Run: https://github.com/yigitcan-ozturk/pamir/actions/runs/36245034546 (success). Artifact: https://github.com/yigitcan-ozturk/pamir/actions/runs/36245034546/artifacts/10907820054

## Cohort and baseline
50 SHA-verified Corpus v1 PX4 ULogs; source-labelled 33 healthy controls, 6 incidents, 11 unknown. Frozen threshold 7.0 yielded 16/33 healthy roots, 3/6 incident roots, 10/11 unknown roots.

## External selector variants (actual chronological reselection with frozen non-estimation eligibility and power fallback)
| Rule | Healthy roots | Incident roots | Unknown roots | Incident losses | Incident root migrations |
| --- | ---: | ---: | ---: | ---: | --- |
| Frozen | 16 | 3 | 10 | — | — |
| All estimation candidates require >=4 distinct forward signals | 16 | 3 | 10 | 0 | 0 |
| output_tracking_error candidates require >=4 distinct forward signals | 16 | 3 | 10 | 0 | 0 |
| output_tracking_error candidates require forward control or actuation family | 7 | 3 | 8 | 0 | 2 (FV-E003, FV-I001) |
| All estimation candidates require forward control or actuation family | 5 | 3 | 2 | 0 | 2 (FV-E003, FV-I001) |

All-estimation forward-control/actuation rule suppressed frozen healthy roots in FV-F003, FV-F004, FV-F005, FV-G003, FV-G008, FV-H002, FV-H003, FV-J001, FV-M002, FV-N001, FV-N002. Tracking-error-only version suppressed nine frozen healthy roots. Distinct-signal variants did not suppress any healthy root after reselection; FV-H002 migrated instead.

## Limitations and research gate
Source labels are not independently adjudicated root-cause ground truth. Incident-root retention is **not** incident causal correctness, particularly because two incident roots migrated. Forward family presence is not evidence of independent physical channels or causal ordering. These exploratory results are in-sample Corpus v1 and must not be described as independent performance or a validated candidate. Frozen PAMIR v0.1.0 and threshold 7.0 remain unchanged; spent Holdout v1 must not be used to develop v2.

Before freezing a candidate: review the two incident migrations and all suppressed healthy cases using Corpus v1 provenance and raw channel lineage, verify no label leakage, and predeclare the exact algorithm plus minimum acceptable gates. A **new** source-labelled, SHA/UUID-deduplicated independent holdout must be acquired only after candidate freeze.
