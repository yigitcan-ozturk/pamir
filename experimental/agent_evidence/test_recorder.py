from experimental.agent_evidence.recorder import EvidenceRecorder


def test_stale_context_preserves_decision_time_state():
    recorder = EvidenceRecorder(run_id="AE-001")

    old_context = {"policy": "v1", "limit": 10}
    new_context = {"policy": "v2", "limit": 5}

    recorder.capture(
        evidence_id="CTX-OLD",
        event_type="context",
        source="policy-store",
        source_version="1",
        subject_identity="agent-1",
        input_value={"request": "limit"},
        output_value=old_context,
        event_time="2026-09-21T08:00:00Z",
        observed_time="2026-09-21T08:00:00Z",
    )

    snapshot = recorder.snapshot(
        decision_id="D-001",
        decision_time="2026-09-21T08:00:01Z",
        available_evidence_ids=("CTX-OLD",),
        expected_evidence_ids=("CTX-OLD",),
        model_identity="test-agent",
        model_version="1",
        context_value=old_context,
    )

    recorder.capture(
        evidence_id="CTX-NEW",
        event_type="context",
        source="policy-store",
        source_version="2",
        subject_identity="agent-1",
        input_value={"request": "limit"},
        output_value=new_context,
        event_time="2026-09-21T08:05:00Z",
        observed_time="2026-09-21T08:05:00Z",
    )

    report = recorder.reconstruct(snapshot)

    assert report.status == "VERIFIED"
    assert snapshot.available_evidence_ids == ("CTX-OLD",)
    assert "CTX-NEW" not in snapshot.available_evidence_ids


def test_mutation_is_detected():
    recorder = EvidenceRecorder(run_id="AE-002")
    recorder.capture(
        evidence_id="T-1",
        event_type="tool_result",
        source="tool",
        source_version="1",
        subject_identity="agent-1",
        input_value={"q": "x"},
        output_value={"answer": 1},
        event_time="2026-09-21T08:00:00Z",
    )
    recorder.payloads["T-1"]["output"]["answer"] = 2

    snapshot = recorder.snapshot(
        decision_id="D-002",
        decision_time="2026-09-21T08:00:01Z",
        available_evidence_ids=("T-1",),
        expected_evidence_ids=("T-1",),
    )
    report = recorder.reconstruct(snapshot)

    assert report.status == "INSUFFICIENT"
    assert "T-1" in report.missing_evidence_ids
