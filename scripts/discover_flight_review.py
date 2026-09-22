#!/usr/bin/env python3
"""Discover currently indexed PX4 Flight Review logs for PAMIR corpus triage.

This is acquisition only: it never labels a flight incident/control and never
uses PAMIR output as ground truth. It emits source metadata for independent
narrative review before a case can enter the validation manifest.
"""
from __future__ import annotations
import argparse, gzip, json, urllib.request
from pathlib import Path

DBINFO="https://review.px4.io/dbinfo"

def load_rows():
    req=urllib.request.Request(DBINFO,headers={"User-Agent":"PAMIR-field-validation/1","Accept-Encoding":"gzip"})
    with urllib.request.urlopen(req,timeout=90) as r:
        payload=r.read()
        if r.headers.get("Content-Encoding","").lower()=="gzip" or payload[:2]==b"\\x1f\\x8b":
            payload=gzip.decompress(payload)
    return json.loads(payload.decode("utf-8"))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--limit",type=int,default=25)
    ap.add_argument("--require-narrative",action="store_true")
    ap.add_argument("--output",default="field-validation/runtime/discovery/current-index.json")
    args=ap.parse_args()
    rows=load_rows()
    usable=[]
    for row in rows:
        if not row.get("log_id") or not row.get("download_url"):
            continue
        if args.require_narrative:
            desc=str(row.get("description") or "").strip()
            feedback=str(row.get("feedback") or "").strip()
            feedback_missing=(not feedback or feedback.lower()=="none given")
            generic_descriptions={"qgroundcontrol session",""}
            low_information=feedback_missing and (
                desc.lower() in generic_descriptions
                or len(desc) < 12
                or desc.lower() in {"one","godess","proto 3","stationarytest","11"}
            )
            synthetic_hint=any(token in (desc+" "+feedback).lower() for token in ("sitl","simulation","sim ","gazebo"))
            desk_hint="desk test" in (desc+" "+feedback).lower()
            if low_information or synthetic_hint or desk_hint:
                continue
        usable.append({k:row.get(k) for k in (
            "log_id","download_url","description","feedback","type","airframe",
            "hardware","software","version","upload_date","date","duration"
        ) if k in row})
        if len(usable)>=args.limit:
            break
    out=Path(args.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({"source":DBINFO,"indexed_rows":len(rows),
                               "selected_for_manual_triage":len(usable),
                               "classification":"unassigned",
                               "logs":usable},indent=2)+"\\n")
    print(f"indexed={len(rows)} selected={len(usable)} output={out}")

if __name__=="__main__":
    main()
