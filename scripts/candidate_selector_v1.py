#!/usr/bin/env python3
"""Candidate Selector v1. External field-validation code; frozen PAMIR engine is not modified."""
from __future__ import annotations
from pamir.engine import (_signal_family,_is_power_root,_is_measured_actuation_root,_is_material_estimation_root)
CORE={"power","actuation","attitude","motion","estimation","control"}
def select_material_root_index_v1(deviations,cluster_window_us=3_000_000):
 for i,d in enumerate(deviations):
  family=_signal_family(d.signal)
  if family not in {"power","actuation","estimation","control"}: continue
  if family=="power" and not _is_power_root(d.signal): continue
  if family=="actuation" and (not _is_measured_actuation_root(d) or d.confidence<0.8): continue
  if family=="estimation":
   if not _is_material_estimation_root(d): continue
   recent=any(_signal_family(p.signal)=="actuation" and 0<=d.timestamp_us-p.timestamp_us<=2_000_000 for p in deviations[:i])
   if recent: continue
  if family=="control" and (d.reason!="multi_axis_rate_command_discontinuity" or d.confidence<0.8): continue
  end=d.timestamp_us+cluster_window_us
  families={_signal_family(x.signal) for x in deviations[i:] if x.timestamp_us<=end}&CORE
  if family=="control":
   if {"attitude","motion"}.issubset(families): return i
   continue
  if family=="estimation":
   if not (len(families)>=3 and any(x!="estimation" for x in families)): continue
  if "motion" in families and len(families)>=3:return i
 if deviations:
  first=deviations[0]
  if _signal_family(first.signal)=="power" and _is_power_root(first.signal) and first.confidence>=0.9:return 0
 return None
