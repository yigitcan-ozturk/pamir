# PAMIR-CUAS Reproducibility

## Environment

The repository CI uses the Python version and dependency installation declared in `.github/workflows/test.yml`.

## Clean verification

```bash
git checkout feat/cuas-forensics-prototype
python -m pip install -e '.[dev]'
pytest -q
```

## Determinism requirements

- identical controlled input produces identical analysis output;
- canonical evidence serialization is stable;
- the evidence SHA-256 is stable for the same report body;
- resilience audit ordering and isolated-source output are stable;
- real-recording temporal gates use fixed timestamp fixtures derived from the documented MMAUD recording windows.

## Authority

A local PASS is useful for development. GitHub Actions on the branch head is the recorded demonstrator acceptance authority.
