# Field Validation metrics

## Root-event stability
For repeated deterministic runs of the same pinned input, compare root family, signal and timestamp. Report exact-match rate and timestamp delta.

## False-root rate
On independently labelled healthy controls:
false-root rate = controls with material root / accepted healthy controls.

## Threshold sensitivity
Run a predeclared threshold sweep in the field-validation harness without changing the frozen v0.1.0 baseline configuration. Report root-family changes, root timestamp shifts, false-root changes, and no-conclusion changes.

## Unknown / no-conclusion behaviour
Report the fraction and characteristics of accepted cases where evidence is insufficient for a defensible root. Do not score these automatically as failures unless predeclared criteria require a root.

## Cross-platform generalisation
Stratify outcomes by vehicle type, PX4 version, board/hardware where available, and incident family. Do not claim generalisation for strata with inadequate sample counts.

## Required corpus report
Report total candidates, accepted/rejected, incident/control/unknown balance, family coverage, deterministic replay rate, root stability, false-root rate, threshold sensitivity, and no-conclusion rate.
