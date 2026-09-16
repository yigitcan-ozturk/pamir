from pamir_cuas.arc import ResilienceController, ResilienceState


def test_degradation_alerts_isolates_and_enters_validation():
    controller = ResilienceController()

    actions = controller.detect_degradation("rf-01", "TEMPORAL_STALE_EVIDENCE")

    assert actions == [
        "ALERT",
        "ISOLATE_SOURCE",
        "ENTER_DEGRADED_MODE",
        "VALIDATE_CANDIDATE",
    ]
    assert controller.state is ResilienceState.VALIDATING
    assert controller.isolated_sources == {"rf-01"}
    assert [row["event"] for row in controller.audit] == [
        "ALERT",
        "ISOLATE_SOURCE",
        "VALIDATE_CANDIDATE",
    ]


def test_validation_pass_promotes_recovery():
    controller = ResilienceController()
    controller.detect_degradation("radar-02", "SENSOR_DISAGREEMENT")

    action = controller.validation_result(True, "safe-config-001")

    assert action == "PROMOTE"
    assert controller.state is ResilienceState.RECOVERED
    assert controller.audit[-1]["validation_pass"] is True


def test_validation_failure_rolls_back():
    controller = ResilienceController()
    controller.detect_degradation("eo-03", "TEMPORAL_OUT_OF_ORDER")

    action = controller.validation_result(False, "candidate-unsafe")

    assert action == "ROLLBACK"
    assert controller.state is ResilienceState.ROLLBACK
    assert controller.audit[-1]["validation_pass"] is False


def test_audit_snapshot_is_deterministic():
    first = ResilienceController()
    second = ResilienceController()
    for controller in (first, second):
        controller.detect_degradation("rf-04", "TEMPORAL_STALE_EVIDENCE")
        controller.validation_result(True, "candidate-safe")

    assert first.snapshot() == second.snapshot()
