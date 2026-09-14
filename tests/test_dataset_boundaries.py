import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CALIBRATION = ROOT / "benchmarks" / "v0_2_calibration.json"
HOLDOUT = ROOT / "benchmarks" / "v0_2_holdout.json"


def test_calibration_and_holdout_case_ids_are_disjoint():
    calibration = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    holdout = json.loads(HOLDOUT.read_text(encoding="utf-8"))

    calibration_ids = set(calibration["case_ids"])
    holdout_ids = {case["id"] for case in holdout["cases"]}

    assert calibration_ids
    assert calibration_ids.isdisjoint(holdout_ids)


def test_holdout_cases_require_pinned_inputs_before_scoring():
    holdout = json.loads(HOLDOUT.read_text(encoding="utf-8"))

    for case in holdout["cases"]:
        assert case["kind"] in {"incident", "control", "review_only"}
        assert case["download_url"]
        assert len(case["sha256"]) == 64
        int(case["sha256"], 16)
        assert case["source_url"]
        assert case["label_rationale"]


def test_holdout_policy_forbids_tuning_reuse():
    holdout = json.loads(HOLDOUT.read_text(encoding="utf-8"))
    policy = holdout["policy"].lower()
    assert "must not be used" in policy
    assert "threshold tuning" in policy
    assert "confidence calibration" in policy
