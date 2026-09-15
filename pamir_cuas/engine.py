"""Minimal deterministic forensics engine for PAMIR-CUAS prototype v0.1."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Iterable


STALE_THRESHOLD_MS = 300
DISAGREEMENT_THRESHOLD = 0.45
DECISION_THRESHOLD = 0.60


@dataclass(frozen=True)
class Observation:
    source_id: str
    observation_id: str
    event_time_ms: int
    ingest_time_ms: int
    confidence: float
    supports_threat: bool
    track_id: str | None = None

    @property
    def age_ms(self) -> int:
        return self.ingest_time_ms - self.event_time_ms


@dataclass(frozen=True)
class GroundTruth:
    threat_present: bool


def _normalize_observations(rows: Iterable[dict[str, Any]]) -> list[Observation]:
    result: list[Observation] = []
    for row in rows:
        result.append(Observation(source_id=str(row["source_id"]), observation_id=str(row["observation_id"]), event_time_ms=int(row["event_time_ms"]), ingest_time_ms=int(row["ingest_time_ms"]), confidence=float(row["confidence"]), supports_threat=bool(row["supports_threat"]), track_id=row.get("track_id")))
    return sorted(result, key=lambda x: (x.ingest_time_ms, x.source_id, x.observation_id))


def _fuse(observations: list[Observation]) -> float:
    """Repeatable validation surface, not an operational C-UAS fusion algorithm."""
    if not observations:
        return 0.0
    signed = [o.confidence if o.supports_threat else -o.confidence for o in observations]
    return max(0.0, min(1.0, round(0.5 + sum(signed) / (2 * len(observations)), 6)))


def _decision(score: float) -> bool:
    return score >= DECISION_THRESHOLD


def analyze_incident(incident: dict[str, Any]) -> dict[str, Any]:
    observations = _normalize_observations(incident["observations"])
    truth = GroundTruth(threat_present=bool(incident["ground_truth"]["threat_present"]))
    baseline_score = _fuse(observations)
    baseline_decision = _decision(baseline_score)
    anomalies: list[dict[str, Any]] = []

    for obs in observations:
        if obs.age_ms > STALE_THRESHOLD_MS:
            anomalies.append({"type": "TEMPORAL_STALE_EVIDENCE", "observation_id": obs.observation_id, "source_id": obs.source_id, "age_ms": obs.age_ms})

    threat_obs = [o for o in observations if o.supports_threat]
    non_threat_obs = [o for o in observations if not o.supports_threat]
    if threat_obs and non_threat_obs:
        max_threat = max(o.confidence for o in threat_obs)
        max_non_threat = max(o.confidence for o in non_threat_obs)
        if abs(max_threat - max_non_threat) <= DISAGREEMENT_THRESHOLD:
            anomalies.append({"type": "SENSOR_DISAGREEMENT", "max_threat_confidence": max_threat, "max_non_threat_confidence": max_non_threat})

    outcome = "CORRECT"
    if baseline_decision and not truth.threat_present:
        outcome = "FALSE_POSITIVE"
    elif not baseline_decision and truth.threat_present:
        outcome = "MISSED_DETECTION"

    counterfactuals: list[dict[str, Any]] = []
    causal_findings: list[dict[str, Any]] = []

    stale_ids = {a["observation_id"] for a in anomalies if a["type"] == "TEMPORAL_STALE_EVIDENCE"}
    for obs_id in sorted(stale_ids):
        replay_obs = [o for o in observations if o.observation_id != obs_id]
        replay_score = _fuse(replay_obs)
        replay_decision = _decision(replay_score)
        changed = replay_decision != baseline_decision
        counterfactuals.append({"kind": "EXCLUDE_STALE_EVIDENCE", "excluded_observation_id": obs_id, "score": replay_score, "decision": replay_decision, "changed_outcome": changed})
        if changed:
            source = next(o.source_id for o in observations if o.observation_id == obs_id)
            causal_findings.append({"cause": "TEMPORAL_STALE_EVIDENCE", "observation_id": obs_id, "source_id": source, "evidence": "removing the stale observation changes the fused decision"})

    # CUAS-002: when sensors disagree, test each observation rather than merely
    # reporting correlation. A finding is causal only if exclusion flips the decision.
    if any(a["type"] == "SENSOR_DISAGREEMENT" for a in anomalies):
        for obs in observations:
            if obs.observation_id in stale_ids:
                continue
            replay_obs = [o for o in observations if o.observation_id != obs.observation_id]
            replay_score = _fuse(replay_obs)
            replay_decision = _decision(replay_score)
            changed = replay_decision != baseline_decision
            counterfactuals.append({"kind": "EXCLUDE_DISAGREEING_EVIDENCE", "excluded_observation_id": obs.observation_id, "score": replay_score, "decision": replay_decision, "changed_outcome": changed})
            if changed:
                causal_findings.append({"cause": "SENSOR_DISAGREEMENT", "observation_id": obs.observation_id, "source_id": obs.source_id, "evidence": "excluding the disagreeing observation changes the fused decision"})

    evidence_graph = {
        "nodes": [*[{"id": o.observation_id, "type": "SensorObservation", **asdict(o), "age_ms": o.age_ms} for o in observations], {"id": "fusion:baseline", "type": "FusionDecision", "score": baseline_score}, {"id": "ground_truth", "type": "GroundTruth", "threat_present": truth.threat_present}],
        "edges": [*[{"from": o.observation_id, "to": "fusion:baseline", "type": "CONTRIBUTED_TO"} for o in observations], {"from": "fusion:baseline", "to": "ground_truth", "type": "COMPARED_WITH"}],
    }
    return {"incident_id": incident.get("incident_id", "unknown"), "baseline": {"score": baseline_score, "decision": baseline_decision, "ground_truth": truth.threat_present, "outcome": outcome}, "anomalies": anomalies, "counterfactuals": counterfactuals, "causal_findings": causal_findings, "evidence_graph": evidence_graph, "pass": bool(causal_findings) and outcome in {"FALSE_POSITIVE", "MISSED_DETECTION"}}
