#!/usr/bin/env python3
import json,re,urllib.request,gzip
from pathlib import Path
SRC=Path("field-validation/HOLDOUT_H10_AVAILABILITY_PROBE.md"); OUT=Path("field-validation/runtime/holdout-h10-probe")
def main():
 ids=re.findall(r"\| (H10P-\d+) \| ([0-9a-f-]{36}) \|",SRC.read_text())
 req=urllib.request.Request("https://review.px4.io/dbinfo",headers={"User-Agent":"PAMIR-h10-probe/1","Accept-Encoding":"gzip"})
 with urllib.request.urlopen(req,timeout=90) as r:
  b=r.read()
  if r.headers.get("Content-Encoding","").lower()=="gzip" or b[:2]==b"\x1f\x8b": b=gzip.decompress(b)
 idx={str(x.get("log_id")):x for x in json.loads(b.decode()) if x.get("log_id")}
 rows=[{"candidate_id":c,"flight_review_uuid":u,"available":bool(idx.get(u,{}).get("download_url"))} for c,u in ids]
 OUT.mkdir(parents=True,exist_ok=True); (OUT/"availability.json").write_text(json.dumps({"pamir_scored":False,"candidates":rows},indent=2)+"\n")
 print(json.dumps({"cases":len(rows),"available":sum(x["available"] for x in rows),"unavailable":sum(not x["available"] for x in rows)},indent=2))
if __name__=="__main__": main()
