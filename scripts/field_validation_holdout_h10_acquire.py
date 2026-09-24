#!/usr/bin/env python3
"""Acquire blind-labelled Holdout H10 ULogs without running PAMIR."""
from __future__ import annotations
import hashlib,json,re,urllib.request,gzip
from pathlib import Path
DBINFO="https://review.px4.io/dbinfo"; REGISTER=Path("field-validation/HOLDOUT_H10_BLIND_REGISTER.md"); CORPUS=Path("field-validation/corpus/manifest.json"); OUT=Path("field-validation/runtime/holdout-h10-acquisition")
def sha256(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
 return h.hexdigest()
def db():
 req=urllib.request.Request(DBINFO,headers={"User-Agent":"PAMIR-holdout-h10/1","Accept-Encoding":"gzip"})
 with urllib.request.urlopen(req,timeout=90) as r:
  b=r.read()
  if r.headers.get("Content-Encoding","").lower()=="gzip" or b[:2]==b"\x1f\x8b": b=gzip.decompress(b)
 return {str(x.get("log_id")):x for x in json.loads(b.decode()) if x.get("log_id")}
def main():
 rows=[(cid,"0",uid,label) for cid,uid,label in re.findall(r"\| (H10-\d+) \| ([0-9a-f-]{36}) \| (healthy_control|incident|unknown) \|",REGISTER.read_text())]
 corpus=json.loads(CORPUS.read_text()); used_uuid={str(c.get("flight_review_uuid")) for c in corpus["cases"] if c.get("flight_review_uuid")}; used_sha={str(c.get("sha256")).lower() for c in corpus["cases"] if c.get("sha256")}; idx=db(); OUT.mkdir(parents=True,exist_ok=True); results=[]
 for cid,issue,uid,label in rows:
  r={"case_id":cid,"issue":int(issue),"flight_review_uuid":uid,"classification":label,"pamir_scored":False,"corpus_uuid_duplicate":uid in used_uuid}
  if uid in used_uuid: r["status"]="rejected_corpus_uuid_duplicate"; results.append(r); continue
  meta=idx.get(uid)
  if not meta or not meta.get("download_url"): r["status"]="quarantined_source_unavailable"; results.append(r); continue
  p=OUT/f"{uid}.ulg"
  try:
   req=urllib.request.Request(meta["download_url"],headers={"User-Agent":"PAMIR-holdout-h10/1"})
   with urllib.request.urlopen(req,timeout=180) as resp,p.open("wb") as f:
    while True:
     b=resp.read(1024*1024)
     if not b: break
     f.write(b)
   dig=sha256(p); r.update({"status":"acquired_unscored","download_url":meta["download_url"],"sha256":dig,"size_bytes":p.stat().st_size,"corpus_sha256_duplicate":dig.lower() in used_sha})
   if r["corpus_sha256_duplicate"]: r["status"]="rejected_corpus_sha256_duplicate"
  except Exception as e: r.update({"status":"quarantined_download_error","error":f"{type(e).__name__}: {e}"})
  results.append(r)
 (OUT/"acquisition-results.json").write_text(json.dumps({"pamir_executed":False,"results":results},indent=2)+"\n")
 print(json.dumps({"cases":len(results),"acquired":sum(x["status"]=="acquired_unscored" for x in results),"quarantined":sum(x["status"].startswith("quarantined") for x in results),"rejected":sum(x["status"].startswith("rejected") for x in results)},indent=2))
if __name__=="__main__": main()
