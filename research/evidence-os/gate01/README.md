# Evidence OS Gate 01 — isolated contract smoke tests

Research branch only. Frozen PAMIR v0.1 is unchanged.

Run: `python -m unittest discover -s tests -v`

This small GitHub smoke suite is **separate from the 31-test local v3 ZIP**. It checks evidence references, ordered timestamps, canonical JSON and byte-level SHA-256 input integrity with synthetic fixtures.

**NO-GO** until full v3 suite is ported and independently run in CI, real pinned PX4 ULogs are replayed twice, and causal/sufficiency claims are externally reviewed. Passing these tests does not establish causal inference or deterministic telemetry replay.
