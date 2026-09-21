#!/usr/bin/env python3
"""PAMIR field-validation batch harness.

Runs outside the frozen v0.1 policy. It resolves public PX4 Flight Review
ULogs, verifies a pinned SHA256 when present, and executes frozen PAMIR twice.
A missing hash is discovery-only and never becomes accepted evidence.
"""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys, urllib.request
from pathlib import Path

DBINFO="https://review.px4.io/dbinfo"

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def resolve(uuid: str) -> str:
    with urllib.request.urlopen(DBINFO, timeout=60) as r:
        rows=json.load(r)
    for row in rows:
        if row.get("log_id")==uuid and row.get("download_url"):
            return row["download_url"]
    raise RuntimeError(f"{uuid} not present in current Flight Review dbinfo")

def download(url: str, dest: Path) -> None:
    req=urllib.request.Request(url,headers={"User-Agent":"PAMIR-field-validation/1"})
    with urllib.request.urlopen(req,timeout=120) as r, dest.open("wb") as f:
        while True:
            b=r.read(1024*1024)
            if not b: break
            f.write(b)

def run_case(case: dict, root: Path) -> dict:
    cid=case["case_id"]; out=root/cid; out.mkdir(parents=True,exist_ok=True)
    result={"case_id":cid,"status":"started","accepted_for_scoring":False}
    try:
        url=resolve(case["flight_review_uuid"]); result["download_url"]=url
        ulg=out/"input.ulg"; download(url,ulg)
        digest=sha256(ulg); result["sha256"]=digest; result["size_bytes"]=ulg.stat().st_size
        expected=case.get("sha256")
        if not expected:
            result["status"]="discovery_sha_required"
            return result
        if digest.lower()!=expected.lower():
            result["status"]="sha256_mismatch"; return result
        reports=[]
        for n in (1,2):
            p=out/f"report-{n}.json"
            subprocess.run([sys.executable,"-m","pamir.cli","analyze",str(ulg),"-o",str(p)],check=True)
            reports.append(p)
        if reports[0].read_bytes()!=reports[1].read_bytes():
            result["status"]="determinism_failure"; return result
        report=json.loads(reports[0].read_text())
        result.update({"status":"pass_exact","accepted_for_scoring":True,
                       "report_sha256":sha256(reports[0]),"pamir_report":report})
        return result
    except Exception as e:
        result.update({"status":"source_or_runtime_error","error":f"{type(e).__name__}: {e}"})
        return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",default="field-validation/corpus/manifest.json")
    ap.add_argument("--case",action="append",dest="cases")
    ap.add_argument("--output",default="field-validation/runtime/batch")
    args=ap.parse_args()
    manifest=json.loads(Path(args.manifest).read_text())
    selected=[c for c in manifest["cases"] if not args.cases or c["case_id"] in args.cases]
    root=Path(args.output); root.mkdir(parents=True,exist_ok=True)
    results=[run_case(c,root) for c in selected if c.get("acceptance_status")!="quarantined"]
    (root/"batch-results.json").write_text(json.dumps(results,indent=2)+"\n")
    print(json.dumps(results,indent=2))
    if any(r["status"] in {"sha256_mismatch","determinism_failure"} for r in results): return 2
    return 0

if __name__=="__main__": raise SystemExit(main())
