#!/usr/bin/env python3
"""Validate frozen Candidate Selector v1 on Corpus v1 only. Holdout is not read."""
import json
from collections import Counter
from pathlib import Path
from pamir.engine import _select_material_root_index,_signal_family,detect_deviations
from pamir.ingest import load
from field_validation_batch import download,resolve,sha256
from candidate_selector_v1 import select_material_root_index_v1
def label(c):
 s=json.dumps(c).lower()
 if "healthy_control" in s:return "healthy_control"
 if '"incident"' in s:return "incident"
 return "unknown"
def main():
 m=json.loads(Path("field-validation/corpus/manifest.json").read_text())
 cases=[c for c in m["cases"] if c.get("acceptance_status")!="quarantined" and c.get("sha256")]
 if len(cases)!=50:raise RuntimeError("expected 50 Corpus v1 cases")
 out=[]; cache=Path("field-validation/runtime/candidate-selector-v1-corpus")
 for c in cases:
  p=cache/c["case_id"]/ "input.ulg";p.parent.mkdir(parents=True,exist_ok=True)
  if not p.exists() or sha256(p).lower()!=c["sha256"].lower():download(resolve(c["flight_review_uuid"]),p)
  if sha256(p).lower()!=c["sha256"].lower():raise RuntimeError(c["case_id"]+": sha mismatch")
  dev=detect_deviations(load(p),threshold=7.0)
  f=_select_material_root_index(dev); a=select_material_root_index_v1(dev); b=select_material_root_index_v1(dev)
  if a!=b:raise RuntimeError(c["case_id"]+": nondeterministic")
  def root(i):
   if i is None:return None
   d=dev[i];return {"signal":d.signal,"family":_signal_family(d.signal),"timestamp_us":d.timestamp_us,"score":d.score}
  out.append({"case_id":c["case_id"],"label":label(c),"frozen":root(f),"candidate":root(a),"changed":f!=a})
 cnt=Counter(x["label"] for x in out)
 def rooted(k,l):return sum(x["label"]==l and x[k] is not None for x in out)
 summary={"cases":len(out),"labels":dict(cnt),"frozen":{"healthy_roots":rooted("frozen","healthy_control"),"incident_roots":rooted("frozen","incident"),"unknown_roots":rooted("frozen","unknown")},"candidate_v1":{"healthy_roots":rooted("candidate","healthy_control"),"incident_roots":rooted("candidate","incident"),"unknown_roots":rooted("candidate","unknown")},"root_changes":sum(x["changed"] for x in out),"deterministic":True}
 Path("field-validation/runtime/candidate-selector-v1-corpus-results.json").write_text(json.dumps({"summary":summary,"cases":out},indent=2)+"\n")
 print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
