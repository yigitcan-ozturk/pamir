#!/usr/bin/env python3
"""Corpus-only exploratory support gates; not a deployable candidate selector."""
import json
from collections import Counter
from pathlib import Path
from pamir.engine import detect_deviations,_select_material_root_index,_signal_family
from pamir.ingest import load
from field_validation_batch import download,resolve,sha256
GATES={"persistence_2_events":lambda w,r:len({x.timestamp_us for x in w if x.signal==r.signal})>=2,
"persistence_250ms":lambda w,r:len({x.timestamp_us for x in w if x.signal==r.signal})>=2 and max([x.timestamp_us for x in w if x.signal==r.signal])-min([x.timestamp_us for x in w if x.signal==r.signal])>=250_000,
"distinct_signals_4":lambda w,r:len({x.signal for x in w})>=4,
"persistence_and_distinct":lambda w,r:len({x.timestamp_us for x in w if x.signal==r.signal})>=2 and len({x.signal for x in w})>=4}
def label(c):
 for k in ("classification","independent_classification","label"):
  s=str(c.get(k,"")).lower()
  if "healthy" in s or "control" in s:return "healthy_control"
  if "incident" in s:return "incident"
 return "unknown"
def main():
 m=json.loads(Path("field-validation/corpus/manifest.json").read_text())
 cases=[c for c in m["cases"] if c.get("acceptance_status")!="quarantined" and c.get("sha256")]
 if len(cases)!=50:raise RuntimeError("Expected exactly 50 Corpus v1 cases")
 rows=[]
 for c in cases:
  p=Path("field-validation/runtime/v2-experiment-cache")/c["case_id"]/"input.ulg"
  p.parent.mkdir(parents=True,exist_ok=True)
  if not p.exists() or sha256(p).lower()!=c["sha256"].lower():download(resolve(c["flight_review_uuid"]),p)
  if sha256(p).lower()!=c["sha256"].lower():raise RuntimeError(c["case_id"]+": SHA mismatch")
  dev=detect_deviations(load(p),threshold=7.0); idx=_select_material_root_index(dev)
  root=dev[idx] if idx is not None else None
  window=[d for d in dev[idx:] if d.timestamp_us<=root.timestamp_us+3_000_000] if root else []
  decisions={}
  for name,gate in GATES.items():
   # Diagnostic suppression only: no reselection or fallback. Non-estimation frozen roots preserved.
   keep=(root is not None and (_signal_family(root.signal)!="estimation" or gate(window,root)))
   decisions[name]=dict(root_present=keep,root_signal=root.signal if keep else None,
      suppressed_estimation=bool(root and not keep))
  rows.append(dict(case_id=c["case_id"],label=label(c),frozen_root=root.signal if root else None,
   frozen_family=_signal_family(root.signal) if root else None,diagnostics=decisions))
 def n(label,key=None):
  return sum(1 for x in rows if x["label"]==label and (x["frozen_root"] is not None if key is None else x["diagnostics"][key]["root_present"]))
 summary={"cohort":dict(Counter(x["label"] for x in rows)),
  "frozen":dict(healthy=n("healthy_control"),incident=n("incident"),unknown=n("unknown")),"gates":{}}
 for name in GATES:
  summary["gates"][name]=dict(healthy=n("healthy_control",name),incident=n("incident",name),
   unknown=n("unknown",name),incident_losses=[x["case_id"] for x in rows if x["label"]=="incident" and x["frozen_root"] and not x["diagnostics"][name]["root_present"]],
   healthy_suppressed=[x["case_id"] for x in rows if x["label"]=="healthy_control" and x["diagnostics"][name]["suppressed_estimation"]])
 out=Path("field-validation/runtime/v2-exploratory-gates.json");out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(dict(summary=summary,cases=rows,limitations="Exploratory frozen-root suppression proxies, not actual reselecting Candidate v2; distinct signals not independent sensors."),indent=2)+"\n")
 print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
