#!/usr/bin/env python3
"""Availability + neutral telemetry-shape probe. Never imports PAMIR and never assigns outcome labels."""
import json,re,urllib.request,hashlib
from pathlib import Path
from pyulog import ULog
SRC=Path("field-validation/HOLDOUT_H11_STRUCTURAL_PROBE.md"); OUT=Path("field-validation/runtime/holdout-h11-probe")
CORE={"vehicle_attitude","vehicle_local_position","vehicle_global_position","vehicle_rates_setpoint","actuator_motors","actuator_outputs","battery_status","estimator_status"}
def get(ds,n):
 for d in ds:
  if d.name==n:return d
def main():
 rows=re.findall(r"\| (H11P-\d+) \| ([0-9a-f-]{36}) \|",SRC.read_text()); OUT.mkdir(parents=True,exist_ok=True); out=[]
 for cid,uid in rows:
  r={"candidate_id":cid,"flight_review_uuid":uid,"pamir_scored":False,"label_assigned":False}
  p=OUT/(uid+".ulg")
  try:
   req=urllib.request.Request("https://cdn.logs.px4.io/"+uid+".ulg",headers={"User-Agent":"PAMIR-h11-structural/1"})
   with urllib.request.urlopen(req,timeout=180) as resp,p.open("wb") as f:
    while True:
     b=resp.read(1<<20)
     if not b:break
     f.write(b)
   h=hashlib.sha256(p.read_bytes()).hexdigest(); u=ULog(str(p)); ds=u.data_list
   ts=[int(x) for d in ds for x in ([d.data["timestamp"][0],d.data["timestamp"][-1]] if "timestamp" in d.data and len(d.data["timestamp"]) else [])]
   dur=(max(ts)-min(ts))/1e6 if ts else 0; vs=get(ds,"vehicle_status"); ld=get(ds,"vehicle_land_detected")
   armed=bool(vs and "arming_state" in vs.data and any(int(x)==2 for x in vs.data["arming_state"])); airborne=bool(ld and "landed" in ld.data and any(int(x)==0 for x in ld.data["landed"]))
   core=sorted({d.name for d in ds if d.name in CORE}); reasons=[]
   if dur<10:reasons.append("duration_lt_10s")
   if not armed:reasons.append("no_armed_evidence")
   if not airborne:reasons.append("no_airborne_evidence")
   if len(core)<2:reasons.append("insufficient_core_datasets")
   r.update(available=True,parseable=True,sha256=h,size_bytes=p.stat().st_size,duration_s=round(dur,3),armed_evidence=armed,airborne_evidence=airborne,core_datasets=core,structurally_admissible=not reasons,reasons=reasons)
  except Exception as e:r.update(available=False,parseable=False,structurally_admissible=False,error=type(e).__name__+": "+str(e))
  out.append(r)
 doc={"pamir_executed":False,"labels_assigned":False,"results":out,"summary":{"cases":len(out),"structurally_admissible":sum(x["structurally_admissible"] for x in out),"not_admissible":sum(not x["structurally_admissible"] for x in out)}}
 (OUT/"structural-probe.json").write_text(json.dumps(doc,indent=2)+"\n");print(json.dumps(doc["summary"],indent=2))
if __name__=="__main__":main()
