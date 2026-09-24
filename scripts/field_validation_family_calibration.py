#!/usr/bin/env python3
"""Counterfactual family-aware root calibration over Corpus v1.
External field-validation experiment only; frozen PAMIR v0.1 is unchanged.
"""
from __future__ import annotations
import argparse, json
from collections import Counter
from pathlib import Path
from pamir.engine import _signal_family

CORE={"power","actuation","attitude","motion","estimation","control"}

def eligible_estimation(root, chain, mode):
    sig=root["signal"].lower()
    if mode=="output_tracking_only" and "output_tracking_error" not in sig:
        return True
    if mode=="estimation_score10" and float(root["score"]) < 10.0:
        return False
    t=int(root["timestamp_us"]); end=t+3_000_000
    fam={_signal_family(x["signal"]) for x in chain if t <= int(x["timestamp_us"]) <= end} & CORE
    return len(fam)>=3 and any(x!="estimation" for x in fam)

def candidate_root(case, threshold_key, mode):
    # The threshold artifact stores selected root metadata, not the full deviation chain.
    # This harness therefore uses root migration across the predeclared threshold sweep
    # as reproducible counterfactual evidence and never claims to re-run frozen selection.
    r=case["thresholds"][threshold_key]
    return r["root_signal"], r["root_family"], r["root_timestamp_us"], r["root_score"]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",default="field-validation/runtime/threshold-sensitivity-results.json")
    ap.add_argument("--out",default="field-validation/runtime/family-aware-calibration.json")
    ap.add_argument("--md",default="field-validation/runtime/family-aware-calibration.md")
    a=ap.parse_args(); d=json.loads(Path(a.input).read_text())
    # Artifact lacks full chains, so use an explicitly bounded proxy:
    # family-aware candidate = require an estimation root to survive at threshold 8;
    # score-floor candidate = survive at threshold 10. This is sensitivity evidence,
    # not an implementation of a new root selector.
    configs={"frozen_7":"7.0","estimation_survival_8":"8.0","estimation_survival_9":"9.0","estimation_survival_10":"10.0"}
    rows={}
    for name,t in configs.items():
        healthy=incident=unknown=0; fam=Counter(); changed=0
        for c in d["cases"]:
            ref=c["thresholds"]["7.0"]; x=c["thresholds"][t]
            # Non-estimation frozen roots are preserved. Estimation roots must survive
            # at the candidate threshold to remain eligible.
            if ref["root_signal"] and ref["root_family"]!="estimation":
                root=ref
            elif ref["root_family"]=="estimation":
                root=x if x["root_signal"] else {"root_signal":None,"root_family":None,"root_timestamp_us":None}
            else:
                root={"root_signal":None,"root_family":None,"root_timestamp_us":None}
            if root["root_signal"]:
                fam[root["root_family"]]+=1
                if c["label"]=="healthy_control": healthy+=1
                elif c["label"]=="incident": incident+=1
                else: unknown+=1
            if root["root_signal"]!=ref["root_signal"] or root["root_timestamp_us"]!=ref["root_timestamp_us"]: changed+=1
        rows[name]={"healthy_false_roots":healthy,"incident_roots":incident,"unknown_roots":unknown,"root_families":dict(fam),"roots_changed_vs_frozen":changed}
    out={"experiment":"family-aware-calibration-proxy","warning":"Threshold-survival proxy only; not a replacement root selector.","results":rows}
    Path(a.out).parent.mkdir(parents=True,exist_ok=True); Path(a.out).write_text(json.dumps(out,indent=2)+"\n")
    lines=["# Family-Aware Calibration Proxy","",
           "This is a bounded threshold-survival proxy over the existing artifact; frozen PAMIR v0.1 is unchanged.","",
           "| candidate | healthy false roots | incident roots | unknown roots | roots changed |",
           "|---|---:|---:|---:|---:|"]
    for n,x in rows.items(): lines.append(f"| {n} | {x['healthy_false_roots']}/33 | {x['incident_roots']}/6 | {x['unknown_roots']}/11 | {x['roots_changed_vs_frozen']} |")
    lines += ["","No candidate is eligible for promotion without independent holdout validation."]
    Path(a.md).write_text("\n".join(lines)+"\n"); print("\n".join(lines))
if __name__=="__main__": main()
