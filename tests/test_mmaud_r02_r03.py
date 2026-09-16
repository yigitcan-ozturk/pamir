from pamir_cuas.adapters.mmaud import associate_nearest_frames, temporal_gate_passes


# Timestamp-only fixtures derived from the user-supplied complete MMAUD Mavic3
# ground_truth (833 frames) and radar_enhance_pcl (2548 frames) archives.
# Raw arrays are not committed. These are original recording timestamps; no
# anomaly or fault is claimed to exist in the source recording.


def _assert_gate(ground_truth, radar, expected_max_ms):
    associations = associate_nearest_frames(ground_truth, radar, max_delta_ms=50.0)
    assert len(associations) == len(ground_truth)
    assert temporal_gate_passes(associations) is True
    assert all(item["within_gate"] for item in associations)
    assert max(item["delta_ms"] for item in associations) <= expected_max_ms
    return associations


def test_r02_mmaud_real_recording_temporal_gate():
    ground_truth = [
        "1692846939.281240.npy", "1692846939.482445.npy",
        "1692846939.681642.npy", "1692846939.881245.npy",
        "1692846940.082311.npy", "1692846940.280320.npy",
        "1692846940.481608.npy", "1692846940.681762.npy",
        "1692846940.880504.npy", "1692846941.079664.npy",
    ]
    radar = [
        "1692846939.311745.npy", "1692846939.511687.npy",
        "1692846939.711789.npy", "1692846939.911382.npy",
        "1692846940.113389.npy", "1692846940.311502.npy",
        "1692846940.513495.npy", "1692846940.711926.npy",
        "1692846940.913286.npy", "1692846941.111634.npy",
    ]
    associations = _assert_gate(ground_truth, radar, 33.0)
    assert associations[0]["radar_file"] == "1692846939.311745.npy"


def test_r03_mmaud_real_recording_temporal_gate():
    ground_truth = [
        "1692847010.684085.npy", "1692847010.885809.npy",
        "1692847011.083508.npy", "1692847011.284606.npy",
        "1692847011.486377.npy", "1692847011.684933.npy",
        "1692847011.885036.npy", "1692847012.087140.npy",
        "1692847012.285310.npy", "1692847012.490042.npy",
    ]
    radar = [
        "1692847010.713194.npy", "1692847010.913249.npy",
        "1692847011.113157.npy", "1692847011.313192.npy",
        "1692847011.513357.npy", "1692847011.712341.npy",
        "1692847011.913285.npy", "1692847012.113379.npy",
        "1692847012.312067.npy", "1692847012.512457.npy",
    ]
    associations = _assert_gate(ground_truth, radar, 30.0)
    assert associations[-1]["radar_file"] == "1692847012.512457.npy"
