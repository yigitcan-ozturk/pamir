"""MMAUD validation adapter for PAMIR-CUAS.

Maps MMAUD-derived evidence into the deterministic incident schema and provides
vendor-neutral timestamp association for independently recorded ground-truth
and radar frames. It does not perform targeting or engagement.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable


def timestamp_seconds(path_or_name: str | Path) -> float:
    """Parse the MMAUD epoch timestamp encoded in a .npy filename."""
    name = Path(path_or_name).name
    if not name.endswith(".npy"):
        raise ValueError(f"expected .npy evidence file: {name}")
    try:
        return float(name[:-4])
    except ValueError as exc:
        raise ValueError(f"invalid MMAUD timestamp filename: {name}") from exc


def associate_nearest_frames(
    ground_truth_files: Iterable[str | Path],
    radar_files: Iterable[str | Path],
    *,
    max_delta_ms: float = 50.0,
) -> list[dict[str, Any]]:
    """Associate each GT frame with the nearest radar frame deterministically.

    The function intentionally uses filenames only, so CI can validate temporal
    integrity without redistributing the original dataset payloads.
    """
    gt = sorted((timestamp_seconds(p), str(p)) for p in ground_truth_files)
    radar = sorted((timestamp_seconds(p), str(p)) for p in radar_files)
    if not radar:
        raise ValueError("radar evidence set is empty")

    result: list[dict[str, Any]] = []
    for gt_time, gt_path in gt:
        radar_time, radar_path = min(
            radar,
            key=lambda item: (abs(item[0] - gt_time), item[0], item[1]),
        )
        delta_ms = abs(radar_time - gt_time) * 1000.0
        result.append(
            {
                "ground_truth_file": Path(gt_path).name,
                "radar_file": Path(radar_path).name,
                "ground_truth_time_ms": round(gt_time * 1000),
                "radar_time_ms": round(radar_time * 1000),
                "delta_ms": delta_ms,
                "within_gate": delta_ms <= max_delta_ms,
            }
        )
    return result


def temporal_gate_passes(associations: Iterable[dict[str, Any]]) -> bool:
    rows = list(associations)
    return bool(rows) and all(bool(row["within_gate"]) for row in rows)


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
