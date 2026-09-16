"""Machine-readable evidence reports for PAMIR-CUAS validation."""

from __future__ import annotations

import hashlib
import json
from typing import Any

SCHEMA_VERSION = "pamir-cuas-evidence/v0.1"


def build_evidence_report(incident: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
    """Build a deterministic, audit-friendly report from an incident analysis."""
    body = {
        "schema_version": SCHEMA_VERSION,
        "incident_id": analysis["incident_id"],
        "provenance": incident.get("provenance", {}),
        "baseline": analysis["baseline"],
        "anomalies": analysis["anomalies"],
        "causal_findings": analysis["causal_findings"],
        "counterfactuals": analysis["counterfactuals"],
        "evidence_graph": analysis["evidence_graph"],
        "validation_pass": bool(analysis["pass"]),
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return {**body, "sha256": hashlib.sha256(canonical).hexdigest()}


def dumps_evidence_report(report: dict[str, Any]) -> str:
    """Serialize a report deterministically for storage, replay, or exchange."""
    return json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
