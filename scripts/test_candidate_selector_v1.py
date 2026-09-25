#!/usr/bin/env python3
"""Semantic/determinism checks for Candidate Selector v1, without holdout scoring."""
from pamir.model import Deviation
from scripts.candidate_selector_v1 import select_material_root_index_v1
def d(t,s,reason="robust_baseline_deviation",confidence=.95): return Deviation(timestamp_us=t,signal=s,value=2,baseline=0,score=12,confidence=confidence,evidence_start_us=t,evidence_end_us=t,reason=reason)
cases=[
 ([d(0,"estimator_status.output_tracking_error"),d(1,"vehicle_local_position.x"),d(2,"vehicle_attitude.roll")],0),
 ([d(0,"estimator_status.output_tracking_error"),d(1,"vehicle_local_position.x")],None),
 ([d(0,"battery_status.voltage_v"),d(1,"vehicle_local_position.x"),d(2,"vehicle_attitude.roll")],0),
]
for ds,want in cases:
 a=select_material_root_index_v1(ds); b=select_material_root_index_v1(ds)
 assert a==b==want,(a,b,want)
print("candidate_selector_v1 semantic/determinism checks: PASS")
