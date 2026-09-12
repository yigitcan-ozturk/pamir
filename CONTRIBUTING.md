# Contributing to PAMIR

PAMIR is being developed as an evidence-first forensic tool for autonomous-system telemetry. Contributions are welcome when they improve reproducibility, validation quality, incident reconstruction, or the clarity of technical evidence.

## Highest-value contributions

The current priority is **external validation without changing the frozen v0.1 baseline semantics**.

Useful contributions include:

- additional public PX4 ULog incident cases with a defensible expected event sequence;
- healthy/control PX4 ULogs for false-positive evaluation;
- independently reproduced benchmark results;
- methodology criticism with a reproducible counterexample;
- parser or compatibility fixes supported by tests;
- documentation that makes evidence and assumptions clearer;
- bounded performance or reliability improvements that preserve existing behavior.

## External validation submission

When submitting a telemetry case, please include:

1. **Source** — public URL or a sanitized file you are authorized to share.
2. **Vehicle / stack context** — PX4 version and relevant platform information when known.
3. **Observed incident** — concise description of what is known to have happened.
4. **Expected earliest material event** — only if independently known.
5. **PAMIR output** — root event, timestamp, confidence heuristic, and relevant evidence window.
6. **Assessment** — match, partial match, false positive, false negative, or unclear.
7. **Reproduction steps** — exact command and environment details.

Do not submit private, export-controlled, safety-sensitive, or personally identifying telemetry unless you have explicit authorization to publish it.

## Reproduce the public baseline

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
pytest -q
python scripts/download_px4_benchmarks.py
python scripts/validate_px4_benchmarks.py
```

The v0.1 benchmark inputs and digests are pinned in:

- `benchmarks/px4_reproducible_incidents.json`
- `benchmarks/VALIDATION.md`

## Development expectations

A contribution should:

- preserve deterministic behavior where possible;
- include tests for behavioral changes;
- keep evidence provenance explicit;
- avoid presenting heuristic confidence as causal probability;
- preserve timestamp ordering and bounded finite outputs;
- fail safely when telemetry is unsupported or ambiguous;
- document any new assumption or scope boundary.

## Pull requests

Keep pull requests focused. Include:

- the problem being solved;
- why the change is needed;
- test or benchmark evidence;
- compatibility or scope implications;
- any known limitation that remains after the change.

Changes that alter root-event semantics or benchmark interpretation should be proposed separately from documentation, compatibility, or tooling changes so they can be reviewed as methodology changes.

## Technical criticism is welcome

A reproducible failure case is a valuable contribution. If PAMIR identifies the wrong earliest material event, misses a material event, or produces an unsafe interpretation, open an issue with the smallest shareable reproduction and the evidence supporting the criticism.
