from __future__ import annotations

from .evidence_graph import EvidenceEdge, EvidenceGraph
from .evidence_object import EvidenceObject, evidence_id
from .model import Deviation

def graph_from_deviations(deviations: list[Deviation], source: str) -> EvidenceGraph:
    graph = EvidenceGraph()
    previous_id: str | None = None
    for deviation in sorted(deviations, key=lambda d: (d.timestamp_us, d.signal, d.reason)):
        payload = {
            "signal": deviation.signal,
            "value": deviation.value,
            "baseline": deviation.baseline,
            "score": deviation.score,
            "confidence": deviation.confidence,
            "reason": deviation.reason,
            "evidence_window_us": [deviation.evidence_start_us, deviation.evidence_end_us],
        }
        oid = evidence_id("deviation", deviation.signal, deviation.timestamp_us, payload)
        obj = EvidenceObject(
            object_id=oid,
            kind="deviation",
            timestamp_us=deviation.timestamp_us,
            subject=deviation.signal,
            payload=payload,
            source=source,
            provenance={"producer": "pamir", "baseline_contract": "v0.1.0-frozen"},
        )
        graph.add_object(obj)
        if previous_id is not None:
            graph.add_edge(EvidenceEdge(
                source_id=previous_id,
                target_id=oid,
                relation=deviation.relation or "followed_by",
                basis="v0.1 temporal/signal-family reconstruction",
            ))
        previous_id = oid
    return graph

def evidence_sufficiency(graph: EvidenceGraph) -> dict:
    first = graph.first_divergence()
    if first is None:
        return {
            "status": "insufficient",
            "score": 0.0,
            "known": [],
            "unknown": ["no material deviation represented"],
        }
    known = ["timestamped first divergence", "source provenance", "deterministic object digest"]
    if graph.edges:
        known.append("ordered downstream evidence")
    unknown = [
        "causal attribution beyond supported evidence",
        "counterfactual outcome until an intervention model is supplied",
    ]
    score = 0.75 if graph.edges else 0.6
    return {"status": "partial", "score": score, "known": known, "unknown": unknown}

def build_evidence_os_report(deviations: list[Deviation], source: str) -> dict:
    graph = graph_from_deviations(deviations, source)
    first = graph.first_divergence()
    return {
        "schema": "pamir-evidence-os/v0.1",
        "baseline": "PAMIR v0.1.0 frozen; unchanged",
        "question_chain": [
            "What happened?",
            "Why?",
            "What evidence proves it?",
            "What remains unknown?",
            "What would have changed the outcome?",
        ],
        "first_divergence": first.to_dict() if first else None,
        "evidence_sufficiency": evidence_sufficiency(graph),
        "evidence_graph": graph.to_dict(),
        "counterfactual_replay": {
            "status": "not_run",
            "reason": "requires an explicit, versioned intervention and replay model",
        },
    }
