from pamir_cuas.adapters.mmaud import associate_nearest_frames, temporal_gate_passes


def test_r01_mmaud_temporal_association_gate():
    # Timestamp-only fixture derived from the independently recorded MMAUD
    # Mavic3 sample inspected during R01. Raw dataset arrays are intentionally
    # not committed; this regression gate validates deterministic association.
    ground_truth = [
        "1692846887.830421.npy",
        "1692846888.030307.npy",
        "1692846888.230252.npy",
    ]
    radar = [
        "1692846887.846020.npy",
        "1692846887.911313.npy",
        "1692846887.978641.npy",
        "1692846888.045315.npy",
        "1692846888.111982.npy",
        "1692846888.178650.npy",
        "1692846888.245318.npy",
    ]

    associations = associate_nearest_frames(
        ground_truth, radar, max_delta_ms=40.0
    )

    assert len(associations) == len(ground_truth)
    assert associations[0]["radar_file"] == "1692846887.846020.npy"
    assert associations[0]["delta_ms"] < 20.0
    assert max(item["delta_ms"] for item in associations) < 40.0
    assert temporal_gate_passes(associations) is True
    assert all(item["within_gate"] for item in associations)
