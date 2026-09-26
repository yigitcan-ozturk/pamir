#!/usr/bin/env python3
"""One-shot independent holdout: immutable pinset + conservative gate + frozen-vs-v1.
No tuning or relabelling. Exit nonzero on integrity/determinism/advancement failure.
"""
import hashlib,json
from collections import Counter
from pathlib import Path
from pamir.engine import detect_deviations,_select_material_root_index,_signal_family
from pamir.ingest import load
from candidate_selector_v1 import select_material_root_index_v1
from field_validation_holdout_telemetry_gate import main as telemetry_gate
BASE=Path("field-validation/runtime/holdout-telemetry-gate")
OUT=Path("field-validation/runtime/holdout-v1-evaluation")
SELECTOR_SHA="5fc5db552b47701c30a33b7fd252ee6f14f3a502254869cd8762926e82410244"
def digest(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
 return h.hexdigest()
def root(dev,i):
 if i is None:return None
 d=dev[i]
 return dict(signal=d.signal,family=_signal_family(d.signal),timestamp_us=d.timestamp_us,score=d.score)
def main():
 if digest(Path("scripts/candidate_selector_v1.py"))!=SELECTOR_SHA:raise RuntimeError("Frozen selector SHA changed")
 telemetry_gate()
 gate=json.loads((BASE/"telemetry-gate-results.json").read_text())
 accepted=[x for x in gate["results"] if x["status"]=="accepted_pre_pamir"]
 labels=Counter(x["classification"] for x in accepted)
 if len(accepted)!=20 or labels!=Counter({"healthy_control":12,"incident":8}):
  raise RuntimeError(f"Predeclared holdout gate mismatch: {len(accepted)}, {labels}")
 if gate["summary"]["rejected"]!=0:raise RuntimeError("Cross-holdout duplicate or rejection")
 rows=[]
 for c in accepted:
  path=BASE/(c["flight_review_uuid"]+".ulg")
  if digest(path)!=c["sha256"]:raise RuntimeError(c["case_id"]+": input hash mismatch")
  samples=load(path)
  d1=detect_deviations(samples,threshold=7.0)
  d2=detect_deviations(samples,threshold=7.0)
  def signature(ds):return [(x.timestamp_us,x.signal,x.value,x.baseline,x.score,x.confidence,x.reason) for x in ds]
  if signature(d1)!=signature(d2):raise RuntimeError(c["case_id"]+": frozen replay mismatch")
  f1=_select_material_root_index(d1);f2=_select_material_root_index(d2)
  v1=select_material_root_index_v1(d1);v2=select_material_root_index_v1(d2)
  if f1!=f2 or v1!=v2:raise RuntimeError(c["case_id"]+": root replay mismatch")
  rows.append(dict(case_id=c["case_id"],label=c["classification"],input_sha256=c["sha256"],
    frozen=root(d1,f1),candidate_v1=root(d1,v1),changed=f1!=v1,
    timestamp_shift_us=(d1[v1].timestamp_us-d1[f1].timestamp_us if f1 is not None and v1 is not None else None),
    deterministic=True))
 def count(label,key):return sum(r["label"]==label and r[key] is not None for r in rows)
 lost=[r["case_id"] for r in rows if r["label"]=="incident" and r["frozen"] is not None and r["candidate_v1"] is None]
 summary=dict(accepted=len(rows),labels=dict(labels),frozen=dict(healthy_roots=count("healthy_control","frozen"),incident_roots=count("incident","frozen")),
  candidate_v1=dict(healthy_roots=count("healthy_control","candidate_v1"),incident_roots=count("incident","candidate_v1")),
  root_changes=sum(r["changed"] for r in rows),incident_root_losses=lost,deterministic=True,
  advancement_gate_passed=(count("healthy_control","candidate_v1")<count("healthy_control","frozen") and not lost
    and count("incident","candidate_v1")>=count("incident","frozen")))
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/"holdout-results.json").write_text(json.dumps(dict(summary=summary,cases=rows,gate_summary=gate["summary"],selector_sha256=SELECTOR_SHA),indent=2)+"\n")
 print(json.dumps(summary,indent=2))
 if lost:raise RuntimeError("STOP: candidate lost a frozen incident root")
 if not summary["advancement_gate_passed"]:print("NO PROMOTION: predeclared advancement criteria not met")
if __name__=="__main__":main()
