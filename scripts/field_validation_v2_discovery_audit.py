#!/usr/bin/env python3
"""Corpus-v1-only support audit; observational diagnostics, not Candidate v2."""
import json
from collections import Counter
from pathlib import Path
from pamir.engine import detect_deviations,_select_material_root_index,_signal_family
from pamir.ingest import load
from field_validation_batch import download,resolve,sha256
def label(c):
 for k in ("classification","independent_classification","label"):
  v=c.get(k)
  if isinstance(v,str):
   if "healthy" in v.lower() or "control" in v.lower():return "healthy_control"
   if "incident" in v.lower():return "incident"
 return "unknown"
def main():
 manifest=json.loads(Path("field-validation/corpus/manifest.json").read_text())
 cases=[c for c in manifest["cases"] if c.get("acceptance_status")!="quarantined" and c.get("sha256")]
 if len(cases)!=50:raise RuntimeError("Corpus v1 must have 50 accepted cases")
 rows=[]
 for c in cases:
  p=Path("field-validation/runtime/v2-discovery-cache")/c["case_id"]/"input.ulg"
  p.parent.mkdir(parents=True,exist_ok=True)
  if not p.exists() or sha256(p).lower()!=c["sha256"].lower():download(resolve(c["flight_review_uuid"]),p)
  if sha256(p).lower()!=c["sha256"].lower():raise RuntimeError(c["case_id"]+": SHA mismatch")
  ds=detect_deviations(load(p),threshold=7.0)
  idx=_select_material_root_index(ds)
  root=ds[idx] if idx is not None else None
  r=dict(case_id=c["case_id"],label=label(c),root_signal=root.signal if root else None,root_family=_signal_family(root.signal) if root else None)
  if root:
   window=[d for d in ds if root.timestamp_us<=d.timestamp_us<=root.timestamp_us+3_000_000]
   same=[d for d in window if d.signal==root.signal]
   r.update(root_score=root.score,root_timestamp_us=root.timestamp_us,
    forward_deviation_count=len(window),forward_families=sorted({_signal_family(d.signal) for d in window}),
    distinct_forward_signals=len({d.signal for d in window}),
    same_signal_event_count=len(same),same_signal_distinct_timestamps=len({d.timestamp_us for d in same}),
    same_signal_span_us=(max(d.timestamp_us for d in same)-min(d.timestamp_us for d in same)))
  rows.append(r)
 summary=dict(cases=len(rows),labels=dict(Counter(x["label"] for x in rows)),
  healthy_roots=sum(x["label"]=="healthy_control" and x["root_signal"] is not None for x in rows),
  incident_roots=sum(x["label"]=="incident" and x["root_signal"] is not None for x in rows),
  rooted_family_counts=dict(Counter(x["root_family"] for x in rows if x["root_family"])),
  note="Counts of deviation events/signals are NOT independent sensor corroboration; source independence requires separate channel lineage.")
 out=Path("field-validation/runtime/v2-discovery-support-audit.json")
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(dict(summary=summary,cases=rows),indent=2)+"\n")
 print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
