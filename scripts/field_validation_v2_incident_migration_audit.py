#!/usr/bin/env python3
"""Corpus-v1-only incident migration evidence export; not causal adjudication."""
import json
from pathlib import Path
from pamir.engine import detect_deviations,_select_material_root_index,_signal_family
from pamir.ingest import load
from field_validation_batch import download,resolve,sha256
from field_validation_v2_reselection_comparison import select
TARGETS={"FV-E003","FV-I001"}
RULES=("tracking_error_downstream_control_or_actuation","estimation_downstream_control_or_actuation")
def record(d):
 if d is None:return None
 return {"signal":d.signal,"timestamp_us":d.timestamp_us,"family":_signal_family(d.signal),"score":d.score,"reason":d.reason}
def main():
 manifest=json.loads(Path("field-validation/corpus/manifest.json").read_text())
 cases=[c for c in manifest["cases"] if c["case_id"] in TARGETS]
 if len(cases)!=2:raise RuntimeError("Expected two specified Corpus cases")
 rows=[]
 for c in cases:
  p=Path("field-validation/runtime/migration-audit-cache")/c["case_id"]/"input.ulg"
  p.parent.mkdir(parents=True,exist_ok=True)
  if not p.exists() or sha256(p).lower()!=c["sha256"].lower():
   download(resolve(c["flight_review_uuid"]),p)
  if sha256(p).lower()!=c["sha256"].lower():raise RuntimeError("SHA mismatch: "+c["case_id"])
  deviations=detect_deviations(load(p),threshold=7.0)
  frozen_idx=_select_material_root_index(deviations)
  variants={}
  for name in RULES:
   idx=select(deviations,name)
   root=deviations[idx] if idx is not None else None
   context=[record(d) for d in deviations if root and root.timestamp_us-2_000_000<=d.timestamp_us<=root.timestamp_us+3_000_000]
   variants[name]={"root":record(root),"changed":idx!=frozen_idx,"context":context}
  frozen=deviations[frozen_idx] if frozen_idx is not None else None
  rows.append({"case_id":c["case_id"],"source_url":c["source_url"],"source_narrative":c["narrative_basis"],
   "frozen_root":record(frozen),"variants":variants,
   "warning":"Deviation topic names and timing alone do not establish physical sensor independence or causal truth."})
 out=Path("field-validation/runtime/v2-incident-migration-audit.json")
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps({"cases":rows,"status":"evidence export only; manual source-lineage adjudication pending"},indent=2)+"\n")
 for r in rows:
  print(json.dumps({"case_id":r["case_id"],"frozen":r["frozen_root"],"variants":{k:v["root"] for k,v in r["variants"].items()}},indent=2))
if __name__=="__main__":main()
