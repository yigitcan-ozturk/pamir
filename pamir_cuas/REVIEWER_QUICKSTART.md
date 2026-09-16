# Reviewer Quickstart

For technical review:

```bash
python -m pip install -e '.[dev]'
pytest -q
```

Then inspect:

- `PROTOTYPE_SPEC.md` — technical contract
- `VALIDATION_MATRIX.md` — evidence map
- `EVIDENCE_PACK.md` — provenance, evidence and limitations
- `DEMONSTRATOR_ACCEPTANCE.md` — end-to-end acceptance flow
- `BLIND_VALIDATION_PROTOCOL.md` — proposed next external validation gate

The repository CI result on the reviewed branch head is the machine-verifiable acceptance record.
