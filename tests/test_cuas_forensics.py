from pamir_cuas import analyze_incident


def test_cuas_001_stale_rf_causes_false_positive():
    incident = {
        "incident_id": "CUAS-001",
        "ground_truth": {"threat_present": False},
        "observations": [
            {"source_id": "radar-A", "observation_id": "radar-001", "event_time_ms": 1000, "ingest_time_ms": 1040, "confidence": 0.20, "supports_threat": False, "track_id": "T-17"},
            {"source_id": "eo-A", "observation_id": "eo-001", "event_time_ms": 1010, "ingest_time_ms": 1060, "confidence": 0.10, "supports_threat": False, "track_id": "T-17"},
            {"source_id": "rf-A", "observation_id": "rf-001", "event_time_ms": 500, "ingest_time_ms": 1100, "confidence": 0.95, "supports_threat": True, "track_id": "T-17"},
        ],
    }
    report = analyze_incident(incident)
    assert report["baseline"]["outcome"] == "FALSE_POSITIVE"
    assert any(item["type"] == "TEMPORAL_STALE_EVIDENCE" and item["observation_id"] == "rf-001" for item in report["anomalies"])
    assert any(item["excluded_observation_id"] == "rf-001" and item["changed_outcome"] is True for item in report["counterfactuals"])
    assert any(item["cause"] == "TEMPORAL_STALE_EVIDENCE" and item["observation_id"] == "rf-001" for item in report["causal_findings"])
    assert report["pass"] is True
    assert any(edge["type"] == "CONTRIBUTED_TO" for edge in report["evidence_graph"]["edges"])


def test_cuas_002_disagreeing_sensor_materially_causes_false_positive():
    incident = {
        "incident_id": "CUAS-002",
        "ground_truth": {"threat_present": False},
        "observations": [
            {"source_id": "radar-A", "observation_id": "radar-002", "event_time_ms": 2000, "ingest_time_ms": 2040, "confidence": 0.20, "supports_threat": False, "track_id": "T-22"},
            {"source_id": "eo-A", "observation_id": "eo-002", "event_time_ms": 2010, "ingest_time_ms": 2050, "confidence": 0.10, "supports_threat": False, "track_id": "T-22"},
            {"source_id": "rf-A", "observation_id": "rf-002", "event_time_ms": 2020, "ingest_time_ms": 2060, "confidence": 0.99, "supports_threat": True, "track_id": "T-22"},
        ],
    }
    report = analyze_incident(incident)
    assert report["baseline"]["outcome"] == "FALSE_POSITIVE"
    assert any(item["type"] == "SENSOR_DISAGREEMENT" for item in report["anomalies"])
    assert any(item["kind"] == "EXCLUDE_DISAGREEING_EVIDENCE" and item["excluded_observation_id"] == "rf-002" and item["changed_outcome"] is True for item in report["counterfactuals"])
    assert any(item["cause"] == "SENSOR_DISAGREEMENT" and item["observation_id"] == "rf-002" for item in report["causal_findings"])
    assert report["pass"] is True


def test_cuas_003_out_of_order_evidence_materially_causes_false_positive():
    incident = {
        "incident_id": "CUAS-003",
        "ground_truth": {"threat_present": False},
        "observations": [
            {"source_id": "radar-A", "observation_id": "radar-003", "event_time_ms": 3000, "ingest_time_ms": 3030, "confidence": 0.10, "supports_threat": False, "track_id": "T-31"},
            {"source_id": "eo-A", "observation_id": "eo-003", "event_time_ms": 3040, "ingest_time_ms": 3070, "confidence": 0.10, "supports_threat": False, "track_id": "T-31"},
            {"source_id": "rf-A", "observation_id": "rf-003", "event_time_ms": 3020, "ingest_time_ms": 3090, "confidence": 0.99, "supports_threat": True, "track_id": "T-31"},
        ],
    }
    report = analyze_incident(incident)
    assert report["baseline"]["outcome"] == "FALSE_POSITIVE"
    assert any(item["type"] == "TEMPORAL_OUT_OF_ORDER" and item["observation_id"] == "rf-003" for item in report["anomalies"])
    assert any(item["kind"] == "EXCLUDE_OUT_OF_ORDER_EVIDENCE" and item["excluded_observation_id"] == "rf-003" and item["changed_outcome"] is True for item in report["counterfactuals"])
    assert any(item["cause"] == "TEMPORAL_OUT_OF_ORDER" and item["observation_id"] == "rf-003" for item in report["causal_findings"])
    assert report["pass"] is True
    assert any(node["id"] == "rf-003" and node["type"] == "SensorObservation" for node in report["evidence_graph"]["nodes"])
