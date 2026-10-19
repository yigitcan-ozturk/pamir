import hashlib
import tempfile
import unittest
from pathlib import Path
from evidence_contract import canonical_bytes, validate_evidence, verify_input

def fixture():
    return {"schema_version": "gate01.1", "observations": [{"id": "a", "timestamp_s": 1.0}, {"id": "b", "timestamp_s": 2.0}], "earliest_anomaly": "a", "first_relevant_divergence": "b", "causal_proof": False}

class ContractTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(len(validate_evidence(fixture())), 64)
    def test_canonical_order(self):
        self.assertEqual(canonical_bytes({"b": 2, "a": 1}), canonical_bytes({"a": 1, "b": 2}))
    def test_duplicate_ids(self):
        x=fixture(); x["observations"][1]["id"]="a"
        with self.assertRaises(ValueError): validate_evidence(x)
    def test_reversed_time(self):
        x=fixture(); x["observations"][1]["timestamp_s"]=0
        with self.assertRaises(ValueError): validate_evidence(x)
    def test_nonfinite_time(self):
        x=fixture(); x["observations"][0]["timestamp_s"]=float("nan")
        with self.assertRaises(ValueError): validate_evidence(x)
    def test_unsupported_ref(self):
        x=fixture(); x["first_relevant_divergence"]="missing"
        with self.assertRaises(ValueError): validate_evidence(x)
    def test_reject_causal_proof(self):
        x=fixture(); x["causal_proof"]=True
        with self.assertRaises(ValueError): validate_evidence(x)
    def test_input_integrity(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"input.bin"; p.write_bytes(b"PX4 synthetic fixture")
            h=hashlib.sha256(p.read_bytes()).hexdigest()
            self.assertEqual(verify_input(p,h),h)
            p.write_bytes(b"changed")
            with self.assertRaises(ValueError): verify_input(p,h)
    def test_bad_digest(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"input.bin"; p.write_bytes(b"x")
            with self.assertRaises(ValueError): verify_input(p,"not-a-sha")
if __name__ == "__main__": unittest.main()
