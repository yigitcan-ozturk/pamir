"""Isolated Gate 01 evidence contract. Does not import or modify frozen v0.1."""
import hashlib
import json
import math
from pathlib import Path

def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")

def verify_input(path, expected_sha256):
    p = Path(path)
    if not p.is_file() or p.is_symlink():
        raise ValueError("missing or unsafe input")
    if len(expected_sha256) != 64 or any(c not in "0123456789abcdef" for c in expected_sha256):
        raise ValueError("invalid SHA256")
    actual = hashlib.sha256(p.read_bytes()).hexdigest()
    if actual != expected_sha256:
        raise ValueError("input digest mismatch")
    return actual

def validate_evidence(doc):
    if doc.get("schema_version") != "gate01.1":
        raise ValueError("unknown schema")
    observations = doc.get("observations")
    if not isinstance(observations, list) or not observations:
        raise ValueError("missing observations")
    ids = set()
    last = -math.inf
    for o in observations:
        t = o.get("timestamp_s")
        if not isinstance(t, (int, float)) or isinstance(t, bool) or not math.isfinite(t) or t < last:
            raise ValueError("invalid timestamp order")
        if not isinstance(o.get("id"), str) or not o["id"] or o["id"] in ids:
            raise ValueError("invalid observation id")
        ids.add(o["id"])
        last = t
    for field in ("earliest_anomaly", "first_relevant_divergence"):
        ref = doc.get(field)
        if ref is not None and ref not in ids:
            raise ValueError("unsupported reference")
    if doc.get("causal_proof") is True:
        raise ValueError("causal proof not established")
    return hashlib.sha256(canonical_bytes(doc)).hexdigest()
