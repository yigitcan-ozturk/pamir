# CI Gate

Required workflow: `.github/workflows/test.yml`

Required state for final demonstrator acceptance:

- status: `completed`
- conclusion: `success`
- head branch: `feat/cuas-forensics-prototype`
- head contains `tests/test_cuas_demonstrator_acceptance.py`

Any failing test keeps demonstrator readiness open until corrected and reverified.
