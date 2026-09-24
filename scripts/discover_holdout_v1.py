#!/usr/bin/env python3
"""Discover independent PX4 Flight Review holdout candidates.
Acquisition/triage only. Never runs PAMIR and never assigns incident/control labels.
"""
from __future__ import annotations
import argparse, gzip, json, urllib.request
from pathlib import Path

DBINFO="https://review.px4.io/dbinfo"
MANIFEST=Path("field-validation/corpus/manifest.json")

def rows():
    req=urllib.request.Request(DBINFO,headers={"User-Agent":"PAMIR-holdout-v1/1","Accept-Encoding":"gzip"})
    with urllib.request.urlopen(req,timeout=90) as r:
        b=r.read()
        if r.headers.get("Content-Encoding","").lower()=="gzip" or b[:2]==b"\x1f\x8b": b=gzip.decompress(b)
    return json.loads(b.decode())

def corpus_ids():
    d=json.loads(MANIFEST.read_text())
    return {str(c.get("flight_review_uuid")) for c in d["cases"] if c.get("flight_review_uuid")}

def useful(r):
    text=" ".join(str(r.get(k) or "") for k in ("description","feedback")).strip()
    low=text.lower()
    if len(text)<12: return False
    if any(x in low for x in ("sitl","simulation","gazebo","desk test")): return False
    return True

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--limit",type=int,default=60); a=ap.parse_args()
    used=corpus_ids(); selected=[]; seen=set()
    for r in rows():
        uid=str(r.get("log_id") or "")
        if not uid or uid in used or uid in seen or not r.get("download_url") or not useful(r): continue
        seen.add(uid)
        selected.append({k:r.get(k) for k in ("log_id","download_url","description","feedback","type","airframe","hardware","software","version","upload_date","date","duration")})
        if len(selected)>=a.limit: break
    out={"source":DBINFO,"corpus_v1_uuid_exclusions":len(used),"selected":len(selected),
         "classification":"UNASSIGNED — independent narrative review required before PAMIR scoring",
         "candidates":selected}
    p=Path("field-validation/runtime/holdout-v1-discovery.json"); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(out,indent=2)+"\n"); print(f"excluded={len(used)} selected={len(selected)}")
if __name__=="__main__": main()
