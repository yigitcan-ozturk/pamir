# R01 — MMAUD Independent Real-World Validation

## Purpose

Establish the first PAMIR-CUAS validation case whose source evidence originates
from an independent, publicly documented real-world anti-UAV dataset.

## Source

- Dataset: MMAUD — A Comprehensive Multi-Modal Anti-UAV Dataset for Modern Miniature Drone Threats
- Maintainer: NTU ARIS
- Publication: ICRA 2024, DOI 10.1109/ICRA57147.2024.10610957
- Modalities documented by the dataset: two 3D LiDARs, two time-synchronized cameras, one mmWave radar, four audio-array nodes, plus ground truth.

## Evidence policy

PAMIR-CUAS must never represent a controlled mutation as an event that occurred
in the original MMAUD recording.

For every R01 execution retain:

1. dataset sequence identifier;
2. original source-file hash where redistribution/licensing permits;
3. extraction code/version;
4. immutable extracted evidence rows;
5. a separate fault-injection manifest, if a controlled temporal or evidence fault is introduced;
6. expected result declared before analysis;
7. PAMIR-CUAS report and evidence graph;
8. final PASS/FAIL.

## R01 acceptance gate

R01 is PASS only when all of the following are available in CI or a retained
validation artifact:

- independently sourced MMAUD evidence has actually been ingested;
- provenance identifies the exact dataset sequence;
- original evidence and any controlled mutation are distinguishable;
- PAMIR-CUAS produces deterministic analysis from the extracted evidence;
- the expected anomaly/root cause, when intentionally injected, is identified;
- counterfactual replay demonstrates materiality where a causal claim is made;
- evidence lineage is retained;
- the run is reproducible.

Creating the adapter or this manifest alone does **not** constitute R01 PASS.

## Licensing note

The MMAUD repository states that the dataset is intended for non-commercial
academic use under CC BY-NC-SA 4.0 and asks commercial users to contact the
maintainers. Do not redistribute raw dataset files inside this repository.
Before commercial deployment or redistribution, confirm permission with the
dataset owner.
