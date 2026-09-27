#!/usr/bin/env python3
"""Harsha EOA/FRD inventory. Requires: pip install pyulog numpy. No causal inference."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from pyulog import ULog

LOG_URL = "https://review.px4.io/plot_app?log=452d7328-c961-49d4-b608-33ee82d99133"
EVENTS = [
    ("mag_field[2] reported peak", 455.242),
    ("mag_field[0] reported peak", 456.740),
    ("first identified attitude divergence", 462.123),
    ("tilt 46.3 vs setpoint 4.8", 462.532),
    ("actuator [1999,109,1999,109]", 462.586),
    ("tilt 82.6 vs setpoint 5.3", 462.862),
    ("fd_roll", 467.388),
    ("flight termination", 468.015),
]

def summarize(log_path):
    path = Path(log_path)
    ul = ULog(str(path))
    topics = []
    ratios = []
    selector = []
    for d in ul.data_list:
        data = d.data
        times = np.asarray(data.get("timestamp", []), dtype=np.float64) / 1e6
        fields = sorted(data)
        topics.append({"name": d.name, "multi_id": d.multi_id, "fields": fields,
                       "samples": len(times),
                       "start_s": float(times[0]) if len(times) else None,
                       "end_s": float(times[-1]) if len(times) else None})
        if d.name in ("estimator_innovations", "estimator_innovation_test_ratios", "estimator_status"):
            for field in fields:
                if ("mag" not in field.lower() or
                    not any(k in field.lower() for k in ("ratio", "test", "mag_field"))):
                    continue
                values = np.asarray(data[field])
                if not np.issubdtype(values.dtype, np.number): continue
                finite = np.isfinite(values)
                exceed = finite & (values > 1)
                # This is a candidate screen, NOT validated PX4-specific fault logic.
                ratios.append({"topic": d.name, "instance": d.multi_id, "field": field,
                               "first_sample_s": float(times[0]) if len(times) else None,
                               "first_ratio_gt_1_s": float(times[np.flatnonzero(exceed)[0]]) if np.any(exceed) else None,
                               "ratio_gt_1_count": int(exceed.sum()),
                               "max_value": float(np.max(values[finite])) if np.any(finite) else None})
        if d.name == "estimator_selector_status":
            key = next((k for k in ("primary_instance", "selected_instance") if k in data), None)
            if key:
                vals = np.asarray(data[key])
                changes = np.r_[True, vals[1:] != vals[:-1]]
                selector.extend({"time_s": float(t), "selected_instance": int(v)}
                                for t,v in zip(times[changes], vals[changes]))
    return {
        "schema": "pamir.harsha.eoa_frd.inventory.v0.1",
        "source_url": LOG_URL, "raw_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "parser": "pyulog", "timebase": "ULog timestamp / 1e6; alignment not validated",
        "supplied_events_not_reproduced": [{"label": x, "time_s": t} for x,t in EVENTS],
        "topic_inventory": topics, "mag_candidate_screens": ratios,
        "selector_changes": selector,
        "causal_hypotheses": [
            {"id": h, "status": "UNRESOLVED", "causal_edge_confirmed": False}
            for h in ("H1_MAG_SELECTED_EKF_CONTROL", "H2_ESTIMATOR_SWITCH",
                      "H3_INDEPENDENT_CONTROL_ACTUATOR", "H4_BACKGROUND_MAG_ANOMALY")],
        "limitations": [
            "ratio >1 is exploratory only; validate PX4 firmware-specific semantics",
            "peak times do not prove onset",
            "selector absent means selected instance unknown",
            "this inventory does not establish FRD or causality",
        ],
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("ulog")
    p.add_argument("--out", default="harsha_inventory.json")
    args=p.parse_args()
    result=summarize(args.ulog)
    Path(args.out).write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    print(f"wrote {args.out}; topics={len(result['topic_inventory'])}; causal status=UNRESOLVED")

if __name__=="__main__": main()
