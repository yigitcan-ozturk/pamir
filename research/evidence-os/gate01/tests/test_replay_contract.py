"""Contract-level deterministic serialization tests; NOT PX4 telemetry replay."""
import copy
import unittest
from evidence_contract import validate_evidence
from test_contract import fixture

class ReplayContractTests(unittest.TestCase):
    def test_identical_documents_same_digest(self):
        first = fixture()
        self.assertEqual(validate_evidence(first), validate_evidence(copy.deepcopy(first)))

    def test_order_of_keys_does_not_change_digest(self):
        first = fixture()
        reordered = dict(reversed(list(first.items())))
        self.assertEqual(validate_evidence(first), validate_evidence(reordered))

    def test_changed_observation_changes_digest(self):
        first = fixture()
        changed = copy.deepcopy(first)
        changed["observations"][1]["timestamp_s"] = 2.5
        self.assertNotEqual(validate_evidence(first), validate_evidence(changed))

    def test_missing_observations_rejected(self):
        doc = fixture()
        doc["observations"] = []
        with self.assertRaises(ValueError):
            validate_evidence(doc)

if __name__ == "__main__":
    unittest.main()
