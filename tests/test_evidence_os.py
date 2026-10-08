from pamir.evidence_graph import EvidenceEdge, EvidenceGraph
from pamir.evidence_object import EvidenceObject
from pamir.evidence_os import build_evidence_os_report
from pamir.model import Deviation

def _d(ts: int, signal: str, relation=None, parent=None):
    return Deviation(
        timestamp_us=ts, signal=signal, value=2.0, baseline=1.0, score=9.0,
        confidence=0.9, evidence_start_us=ts-10, evidence_end_us=ts+10,
        reason="test", relation=relation, parent_signal=parent,
    )

def test_evidence_object_digest_is_deterministic():
    obj = EvidenceObject("x", "claim", 1, "s", {"b": 2, "a": 1}, "fixture")
    assert obj.digest == EvidenceObject("x", "claim", 1, "s", {"a": 1, "b": 2}, "fixture").digest

def test_graph_rejects_dangling_edges():
    graph = EvidenceGraph()
    try:
        graph.add_edge(EvidenceEdge("missing", "also-missing", "supports", "test"))
    except ValueError:
        pass
    else:
        raise AssertionError("dangling edge accepted")

def test_first_divergence_is_earliest_deviation():
    report = build_evidence_os_report(
        [_d(200, "vehicle_attitude.roll"), _d(100, "battery_status.voltage_v")],
        "fixture",
    )
    assert report["first_divergence"]["timestamp_us"] == 100
    assert report["baseline"] == "PAMIR v0.1.0 frozen; unchanged"
    assert report["counterfactual_replay"]["status"] == "not_run"
