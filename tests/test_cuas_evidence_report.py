from pamir_cuas import analyze_incident
from pamir_cuas.report import SCHEMA_VERSION, build_evidence_report, dumps_evidence_report


def test_evidence_report_is_deterministic_and_hashed():
    incident = {
        "incident_id": "REPORT-001",
        "ground_truth": {"threat_present": False},
        "provenance": {"dataset": "controlled-regression", "fault_injection": "declared"},
        "observations": [
            {"source_id": "radar-A", "observation_id": "radar-r1", "event_time_ms": 1000, "ingest_time_ms": 1020, "confidence": 0.10, "supports_threat": False, "track_id": "T-R1"},
            {"source_id": "rf-A", "observation_id": "rf-r1", "event_time_ms": 500, "ingest_time_ms": 1100, "confidence": 0.99, "supports_threat": True, "track_id": "T-R1"},
        ],
    }
    analysis = analyze_incident(incident)
    first = build_evidence_report(incident, analysis)
    second = build_evidence_report(incident, analysis)

    assert first == second
    assert first["schema_version"] == SCHEMA_VERSION
    assert first["incident_id"] == "REPORT-001"
    assert first["provenance"]["fault_injection"] == "declared"
    assert len(first["sha256"]) == 64
    assert dumps_evidence_report(first) == dumps_evidence_report(second)
