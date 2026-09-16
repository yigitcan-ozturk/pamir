"""End-to-end PAMIR-CUAS demonstrator acceptance gate.

This gate exercises mission-assurance and forensic evidence only. It does not
perform targeting, engagement, guidance, interception, or effector control.
"""

from pamir_cuas.arc import ResilienceController, ResilienceState
from pamir_cuas.engine import analyze_incident
from pamir_cuas.report import build_evidence_report, dumps_evidence_report


def _incident():
    return {
        "incident_id": "DEMO-ACCEPT-001",
        "ground_truth": {"is_threat": False},
        "observations": [
            {
                "source_id": "radar",
                "observation_id": "radar-1",
                "track_id": "T-DEMO",
                "event_time": 1000.0,
                "ingest_time": 1000.03,
                "confidence": 0.10,
                "is_threat": False,
            },
            {
                "source_id": "eo",
                "observation_id": "eo-1",
                "track_id": "T-DEMO",
                "event_time": 1000.04,
                "ingest_time": 1000.07,
                "confidence": 0.10,
                "is_threat": False,
            },
            {
                "source_id": "rf",
                "observation_id": "rf-1",
                "track_id": "T-DEMO",
                "event_time": 999.0,
                "ingest_time": 1000.09,
                "confidence": 0.99,
                "is_threat": True,
            },
        ],
        "provenance": {
            "source": "CONTROLLED_DEMONSTRATOR_FIXTURE",
            "fault": "controlled temporal degradation",
        },
    }


def _run():
    incident = _incident()
    analysis = analyze_incident(incident)
    report = build_evidence_report(incident, analysis)

    controller = ResilienceController()
    actions = controller.detect_degradation("rf", "temporal evidence degradation")
    recovery = controller.validation_result(
        passed=bool(report["validation_pass"]),
        candidate_id="demo-counterfactual-001",
    )
    return report, controller.snapshot(), actions, recovery


def test_end_to_end_demonstrator_is_deterministic_and_auditable():
    first = _run()
    second = _run()

    assert first == second
    report, snapshot, actions, recovery = first

    assert report["incident_id"] == "DEMO-ACCEPT-001"
    assert len(report["evidence_hash"]) == 64
    assert dumps_evidence_report(report) == dumps_evidence_report(second[0])
    assert actions == [
        "ALERT",
        "ISOLATE_SOURCE",
        "ENTER_DEGRADED_MODE",
        "VALIDATE_CANDIDATE",
    ]
    assert "rf" in snapshot["isolated_sources"]
    assert recovery in {"PROMOTE", "ROLLBACK"}
    assert snapshot["state"] in {
        ResilienceState.RECOVERED.value,
        ResilienceState.ROLLBACK.value,
    }
