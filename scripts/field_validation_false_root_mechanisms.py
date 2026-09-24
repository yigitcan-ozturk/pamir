#!/usr/bin/env python3
"""Analyse Corpus v1 healthy-control false-root mechanisms.

External analysis only. Frozen PAMIR v0.1 is not modified.
Consumes the machine-readable threshold-sensitivity artifact.
"""
from __future__ import annotations
import argparse, json
from collections import Counter
from pathlib import Path

REF = "7.0"
CANDIDATES = ("8.0", "9.0", "10.0")

def norm_signal(signal):
    if not signal:
        return None
    s = signal
    # Collapse estimator instance and vector index notation for mechanism grouping.
    import re
    s = re.sub(r"estimator_status\[\d+\]", "estimator_status[*]", s)
    s = re.sub(r"estimator_innovations\[\d+\]", "estimator_innovations[*]", s)
    s = re.sub(r"\[\d+\]$", "[*]", s)
    return s

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",default="field-validation/runtime/threshold-sensitivity-results.json")
    ap.add_argument("--json-out",default="field-validation/runtime/false-root-mechanisms.json")
    ap.add_argument("--md-out",default="field-validation/runtime/false-root-mechanisms.md")
    a=ap.parse_args()
    data=json.loads(Path(a.input).read_text())
    healthy=[c for c in data["cases"] if c["label"]=="healthy_control"]
    false=[c for c in healthy if c["thresholds"][REF]["root_signal"]]
    no_root=[c for c in healthy if not c["thresholds"][REF]["root_signal"]]

    mechanisms=Counter(norm_signal(c["thresholds"][REF]["root_signal"]) for c in false)
    families=Counter(c["thresholds"][REF]["root_family"] for c in false)
    rows=[]
    for c in false:
        ref=c["thresholds"][REF]
        row={"case_id":c["case_id"],"root_signal_7":ref["root_signal"],
             "mechanism":norm_signal(ref["root_signal"]),"family_7":ref["root_family"],
             "root_score_7":ref["root_score"],"raw_deviation_count_7":ref["raw_deviation_count"]}
        for t in CANDIDATES:
            x=c["thresholds"][t]
            row[f"root_{t}"]=x["root_signal"]
            row[f"suppressed_{t}"]=x["root_signal"] is None
            row[f"changed_{t}"]=x["root_changed_vs_7"]
            row[f"timestamp_shift_us_{t}"]=x["root_timestamp_shift_us_vs_7"]
        rows.append(row)

    # Also flag non-monotonic roots among all healthy controls.
    nonmono=[]
    for c in healthy:
        present=[bool(c["thresholds"][t]["root_signal"]) for t in ("5.0","6.0","7.0","8.0","9.0","10.0")]
        if any((not present[i]) and present[j] for i in range(len(present)) for j in range(i+1,len(present))):
            nonmono.append({"case_id":c["case_id"],"root_presence":present,
                            "signals":[c["thresholds"][t]["root_signal"] for t in ("5.0","6.0","7.0","8.0","9.0","10.0")]})

    out={"reference_threshold":7.0,"healthy_controls":len(healthy),
         "false_roots_at_7":len(false),"no_root_at_7":len(no_root),
         "families":dict(families),"mechanisms":dict(mechanisms),
         "false_root_cases":rows,"non_monotonic_healthy_cases":nonmono}
    Path(a.json_out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.json_out).write_text(json.dumps(out,indent=2)+"\n")

    lines=["# Corpus v1 False-Root Mechanism Analysis","",
           "External field-validation analysis; frozen PAMIR v0.1 is unchanged.","",
           f"- Healthy controls: {len(healthy)}",
           f"- Material roots at frozen 7.0: {len(false)}",
           f"- No root at frozen 7.0: {len(no_root)}","",
           "## Reference-root families",""]
    for k,v in families.most_common(): lines.append(f"- {k}: {v}")
    lines += ["","## Normalised mechanisms",""]
    for k,v in mechanisms.most_common(): lines.append(f"- {k}: {v}")
    lines += ["","## Case matrix","",
              "| case | root @7 | family | score @7 | root @8 | root @9 | root @10 |",
              "|---|---|---|---:|---|---|---|"]
    for x in rows:
        lines.append(f"| {x['case_id']} | {x['root_signal_7']} | {x['family_7']} | {x['root_score_7']} | {x['root_8.0'] or '—'} | {x['root_9.0'] or '—'} | {x['root_10.0'] or '—'} |")
    lines += ["","## Non-monotonic healthy cases","",
              "Cases where a root disappears at a lower tested threshold and reappears at a higher one:"]
    for x in nonmono: lines.append(f"- {x['case_id']}: {x['root_presence']}")
    Path(a.md_out).write_text("\n".join(lines)+"\n")
    print("\n".join(lines))
if __name__=="__main__": main()
