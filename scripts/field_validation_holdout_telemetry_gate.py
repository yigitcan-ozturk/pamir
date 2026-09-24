#!/usr/bin/env python3
"""Pre-PAMIR holdout telemetry/real-flight sufficiency gate. Never imports PAMIR."""
import hashlib,json,urllib.request
from pathlib import Path
from pyulog import ULog
PIN=Path("field-validation/HOLDOUT_ACQUISITION_PINSET.json")
OUT=Path("field-validation/runtime/holdout-telemetry-gate")
CORE={"vehicle_attitude","vehicle_local_position","vehicle_global_position","vehicle_rates_setpoint","actuator_motors","actuator_outputs","battery_status","estimator_status"}
def sha256(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""): h.update(b)
 return h.hexdigest()
def get(ds,name):
 for d in ds:
  if d.name==name: return d
 return None
def main():
 pin=json.loads(PIN.read_text()); OUT.mkdir(parents=True,exist_ok=True); results=[]; seen={}
 for c in pin["cases"]:
  uid=c["flight_review_uuid"]; p=OUT/f"{uid}.ulg"; r=dict(c,pamir_scored=False)
  try:
   req=urllib.request.Request(f"https://cdn.logs.px4.io/{uid}.ulg",headers={"User-Agent":"PAMIR-holdout-telemetry-gate/1"})
   with urllib.request.urlopen(req,timeout=180) as resp,p.open("wb") as f:
    while True:
     b=resp.read(1<<20)
     if not b: break
     f.write(b)
   dig=sha256(p); r["redownload_sha256"]=dig; r["sha256_match"]=dig==c["sha256"]
   if not r["sha256_match"]: r["status"]="quarantined_sha_mismatch"; results.append(r); continue
   if dig in seen: r.update(status="rejected_cross_holdout_sha_duplicate",duplicate_of=seen[dig]); results.append(r); continue
   seen[dig]=c["case_id"]
   u=ULog(str(p)); ds=u.data_list
   ts=[int(x) for d in ds for x in ([d.data["timestamp"][0],d.data["timestamp"][-1]] if "timestamp" in d.data and len(d.data["timestamp"]) else [])]
   duration=(max(ts)-min(ts))/1e6 if ts else 0.0
   vs=get(ds,"vehicle_status"); ld=get(ds,"vehicle_land_detected")
   armed=bool(vs and "arming_state" in vs.data and any(int(x)==2 for x in vs.data["arming_state"]))
   airborne=bool(ld and "landed" in ld.data and any(int(x)==0 for x in ld.data["landed"]))
   core=sorted({d.name for d in ds if d.name in CORE})
   r.update(duration_s=round(duration,3),armed_evidence=armed,airborne_evidence=airborne,core_datasets=core,core_dataset_count=len(core),parseable=True)
   reasons=[]
   if duration<10: reasons.append("duration_lt_10s")
   if not armed: reasons.append("no_armed_evidence")
   if not airborne: reasons.append("no_airborne_evidence")
   if len(core)<2: reasons.append("insufficient_core_datasets")
   r["status"]="accepted_pre_pamir" if not reasons else "quarantined_telemetry_insufficient"; r["reasons"]=reasons; results.append(r)
  except Exception as e:
   r.update(status="quarantined_parse_or_download_error",error=type(e).__name__+": "+str(e)); results.append(r)
 out={"pamir_executed":False,"gate":{"min_duration_s":10,"requires_armed":True,"requires_airborne":True,"min_core_datasets":2},"results":results}
 out["summary"]={"cases":len(results),"accepted":sum(x["status"]=="accepted_pre_pamir" for x in results),"quarantined":sum(x["status"].startswith("quarantined") for x in results),"rejected":sum(x["status"].startswith("rejected") for x in results)}
 (OUT/"telemetry-gate-results.json").write_text(json.dumps(out,indent=2)+"\n")
 print(json.dumps(out["summary"],indent=2))
if __name__=="__main__": main()
