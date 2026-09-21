# Field Validation acceptance protocol

A case is accepted only when:

1. It is a real public PX4 ULog.
2. The original binary is retrievable and SHA256-pinned.
3. Public-use licensing/provenance is recorded.
4. The log parses deterministically with the pinned PAMIR environment.
5. It contains enough telemetry for the declared validation question.
6. Incident/control/unknown classification is supported independently of PAMIR output.
7. Acceptance criteria are declared before aggregate scoring.

Reject or quarantine cases with missing provenance, inaccessible originals, corrupted/truncated telemetry that defeats the validation question, unclear usage rights, or labels that depend only on PAMIR's own result.

Unknown/no-conclusion is a valid outcome and must not be converted to a PASS or incident root merely to increase coverage.
