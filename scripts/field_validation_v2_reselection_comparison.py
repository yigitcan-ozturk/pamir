#!/usr/bin/env python3
"""Corpus-only true reselection experiment; never modify PAMIR frozen engine."""
import json
from collections import Counter
from pathlib import Path
from pamir.engine import (detect_deviations,_select_material_root_index,_signal_family,
 _is_power_root,_is_measured_actuation_root,_is_material_estimation_root)
from pamir.ingest import load
from field_validation_batch import download,resolve,sha256
CORE={"power","actuation","attitude","motion","estimation","control"}
RULES={
 "estimation_4_distinct_signals":lambda d,w:len({x.signal for x in w})>=4,
 "tracking_error_4_signals":lambda d,w:"output_tracking_error" not in d.signal.lower() or len({x.signal for x in w})>=4,
 "tracking_error_downstream_control_or_actuation":lambda d,w:"output_tracking_error" not in d.signal.lower() or bool({_signal_family(x.signal) for x in w}&{"control","actuation"}),
 "estimation_downstream_control_or_actuation":lambda d,w:bool({_signal_family(x.signal) for x in w}&{"control","actuation"})
}
def select(ds,rule):
 for i,d in enumerate(ds):
  family=_signal_family(d.signal)
  if family not in {"power","actuation","estimation","control"}:continue
  if family=="power" and not _is_power_root(d.signal):continue
  if family=="actuation" and (not _is_measured_actuation_root(d) or d.confidence<0.8):continue
  if family=="estimation":
   if not _is_material_estimation_root(d):continue
   if any(_signal_family(p.signal)=="actuation" and 0<=d.timestamp_us-p.timestamp_us<=2_000_000 for p in ds[:i]):continue
  if family=="control" and (d.reason!="multi_axis_rate_command_discontinuity" or d.confidence<0.8):continue
  w=[x for x in ds[i:] if x.timestamp_us<=d.timestamp_us+3_000_000]
  families={_signal_family(x.signal) for x in w}&CORE
  if family=="control":
   if {"attitude","motion"}.issubset(families):return i
   continue
  if "motion" in families and len(families)>=3:
   if family!="estimation" or RULES[rule](d,w):return i
 if ds and _signal_family(ds[0].signal)=="power" and _is_power_root(ds[0].signal) and ds[0].confidence>=0.9:return 0
 return None
def label(c):
 for k in ("classification","independent_classification","label"):
  s=str(c.get(k,"")).lower()
  if "healthy" in s or "control" in s:return "healthy_control"
  if "incident" in s:return "incident"
 return "unknown"
def root(ds,idx):
 if idx is None:return None
 d=ds[idx]
 return dict(signal=d.signal,timestamp_us=d.timestamp_us,family=_signal_family(d.signal))
def main():
 m=json.loads(Path("field-validation/corpus/manifest.json").read_text())
 cases=[c for c in m["cases"] if c.get("acceptance_status")!="quarantined" and c.get("sha256")]
 if len(cases)!=50:raise RuntimeError("Expected 50 Corpus v1 cases")
 rows=[]
 for c in cases:
  p=Path("field-validation/runtime/v2-reselection-cache")/c["case_id"]/"input.ulg"
  p.parent.mkdir(parents=True,exist_ok=True)
  if not p.exists() or sha256(p).lower()!=c["sha256"].lower():download(resolve(c["flight_review_uuid"]),p)
  if sha256(p).lower()!=c["sha256"].lower():raise RuntimeError(c["case_id"]+": SHA mismatch")
  ds=detect_deviations(load(p),threshold=7.0)
  frozen=root(ds,_select_material_root_index(ds))
  variants={name:root(ds,select(ds,name)) for name in RULES}
  rows.append(dict(case_id=c["case_id"],label=label(c),frozen=frozen,variants=variants))
 summary=dict(cohort=dict(Counter(x["label"] for x in rows)),
 frozen={l:sum(x["label"]==l and x["frozen"] is not None for x in rows) for l in ("healthy_control","incident","unknown")},variants={})
 for name in RULES:
  summary["variants"][name]=dict(
   counts={l:sum(x["label"]==l and x["variants"][name] is not None for x in rows) for l in ("healthy_control","incident","unknown")},
   incident_losses=[x["case_id"] for x in rows if x["label"]=="incident" and x["frozen"] and not x["variants"][name]],
   incident_migrations=[x["case_id"] for x in rows if x["label"]=="incident" and x["frozen"] and x["variants"][name] and x["frozen"]!=x["variants"][name]],
   healthy_suppressed=[x["case_id"] for x in rows if x["label"]=="healthy_control" and x["frozen"] and not x["variants"][name]],
   healthy_migrations=[x["case_id"] for x in rows if x["label"]=="healthy_control" and x["frozen"] and x["variants"][name] and x["frozen"]!=x["variants"][name]])
 out=Path("field-validation/runtime/v2-reselection-comparison.json");out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(dict(summary=summary,cases=rows,limitations="Corpus v1 exploratory reselection; signal families are not independent sensors; no independent v2 validation."),indent=2)+"\n")
 print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
