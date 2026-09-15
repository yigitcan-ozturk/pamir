"""MMAUD validation adapter for PAMIR-CUAS.

This module maps extracted MMAUD-derived validation rows into the deterministic
PAMIR-CUAS incident schema. It does not perform detection, targeting, or
engagement. Original dataset evidence and controlled fault injection must be
kept distinguishable in validation manifests.
"""

from __future__ import annotations

from typing import Any, Iterable


def build_incident(
    *,
    incident_id: str,
    rows: Iterable[dict[str, Any]],
    threat_present: bool,
    dataset_sequence: str,
) -> dict[str, Any]:
    observations: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        observations.append(
            {
                "source_id": str(row["source_id"]),
                "observation_id": str(row.get("observation_id", f"mmaud-{index:04d}")),
                "event_time_ms": int(row["event_time_ms"]),
                "ingest_time_ms": int(row["ingest_time_ms"]),
                "confidence": float(row["confidence"]),
                "supports_threat": bool(row["supports_threat"]),
                "track_id": row.get("track_id"),
            }
        )

    return {
        "incident_id": incident_id,
        "ground_truth": {"threat_present": bool(threat_present)},
        "observations": observations,
        "provenance": {
            "dataset": "MMAUD",
            "dataset_sequence": dataset_sequence,
            "source_kind": "independent-real-world-dataset",
            "fault_injection": "must-be-declared-by-validation-manifest",
        },
    }
