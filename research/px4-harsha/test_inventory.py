"""Run: python -m unittest discover -s research/px4-harsha -p 'test_*.py'"""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import inventory

class FakeDataset:
    def __init__(self, name, multi_id, data):
        self.name, self.multi_id, self.data = name, multi_id, data

class FakeLog:
    def __init__(self, include_selector=True):
        self.data_list = [
            FakeDataset("estimator_innovation_test_ratios", 1,
                {"timestamp": np.array([1000000, 2000000, 3000000]),
                 "mag_field[2]": np.array([1.2, 0.2, 12.4])}),
            FakeDataset("estimator_innovation_test_ratios", 0,
                {"timestamp": np.array([1000000, 2000000]),
                 "mag_field[2]": np.array([0.1, 9.0])}),
        ]
        if include_selector:
            self.data_list.append(FakeDataset("estimator_selector_status", 0,
                {"timestamp": np.array([1000000, 2500000, 3000000]),
                 "primary_instance": np.array([0, 0, 1])}))

class TestConservativeEvidence(unittest.TestCase):
    def run_inventory(self, selector):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "synthetic.ulg"
            path.write_bytes(b"synthetic test only")
            with patch.object(inventory, "ULog", return_value=FakeLog(selector)):
                return inventory.summarize(path)

    def test_early_anomaly_never_becomes_cause(self):
        result = self.run_inventory(True)
        self.assertTrue(all(h["status"] == "UNRESOLVED" and not h["causal_edge_confirmed"]
                            for h in result["causal_hypotheses"]))

    def test_missing_selector_stays_unknown(self):
        self.assertEqual(self.run_inventory(False)["selector_changes"], [])

    def test_nonselected_instance_remains_separate(self):
        result = self.run_inventory(True)
        peaks = {(r["instance"], r["field"]): r["max_value"]
                 for r in result["mag_candidate_screens"]}
        self.assertEqual(peaks[(0, "mag_field[2]")], 9.0)
        self.assertEqual(peaks[(1, "mag_field[2]")], 12.4)
        self.assertEqual(result["selector_changes"][-1]["selected_instance"], 1)

if __name__ == "__main__":
    unittest.main()
