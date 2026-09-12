#!/usr/bin/env python3
import json
from pathlib import Path

from pamir.ingest import load
from pamir.stability import measure_root_stability

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "benchmarks" / "px4_reproducible_incidents.json"
DATA = ROOT / "benchmarks" / "data"
OUT = ROOT / "benchmarks" / "reports"


def summarize_case(case: dict, stability: dict) -> dict:
    baseline_root = stability.get("baseline_root")
    qualified_root = stability.get("qualified_material_root")
    return {
        "id": case["id"],
        "kind": case["kind"],
        "status": stability["status"],
        "stability_ratio": stability["stability_ratio"],
        "variant_count": stability["variant_count"],
        "matching_variant_count": stability["matching_variant_count"],
        "baseline_root_signal": baseline_root["signal"] if baseline_root else None,
        "baseline_root_reason": baseline_root["reason"] if baseline_root else None,
        "baseline_root_timestamp_us": baseline_root["timestamp_us"] if baseline_root else None,
        "qualified_material_root_signal": qualified_root["signal"] if qualified_root else None,
        "candidate_root_variants": stability.get("candidate_root_variants", []),
    }


def validate_case(case: dict, stability: dict) -> list[str]:
    errors: list[str] = []
    runs = stability.get("runs", [])
    if not runs:
        return ["root-stability analysis produced no variant runs"]

    if case["kind"] == "incident":
        if stability.get("baseline_root") is None:
            errors.append("incident baseline lost its v0.1 material root")
    elif case["kind"] == "control":
        if stability.get("qualified_material_root") is not None:
            errors.append("healthy/control produced a perturbation-qualified material root")
    else:
        errors.append(f"unknown benchmark kind: {case['kind']}")
    return errors


def build_payload(rows: list[dict], errors: list[str]) -> dict:
    incidents = [row for row in rows if row["kind"] == "incident"]
    controls = [row for row in rows if row["kind"] == "control"]
    return {
        "schema_version": "0.2-public-root-stability-v2",
        "v0_1_gate_unchanged": True,
        "qualification_policy": "material root requires baseline selection and preservation across every bounded variant",
        "required_incident_count": len(incidents),
        "required_control_count": len(controls),
        "incident_stability_generated": len(incidents),
        "controls_without_qualified_material_root": all(
            row["qualified_material_root_signal"] is None for row in controls
        ),
        "control_candidate_instability_count": sum(
            1 for row in controls if row["status"] == "unstable_root_emergence"
        ),
        "validation_passed": not errors,
        "validation_errors": errors,
        "cases": rows,
    }


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    errors: list[str] = []

    for case in manifest["cases"]:
        path = DATA / f"{case['id']}.ulg"
        if not path.exists():
            errors.append(f"{case['id']}: required benchmark ULog missing")
            continue
        samples = load(path)
        if not samples:
            errors.append(f"{case['id']}: parsed zero telemetry samples")
            continue
        stability = measure_root_stability(samples, case["id"])
        case_errors = validate_case(case, stability)
        errors.extend(f"{case['id']}: {error}" for error in case_errors)
        row = summarize_case(case, stability)
        rows.append(row)
        (OUT / f"{case['id']}.stability.json").write_text(
            json.dumps(stability, indent=2), encoding="utf-8"
        )
        print(
            f"{case['id']}: kind={case['kind']} status={row['status']} "
            f"stability={row['stability_ratio']} root={row['baseline_root_signal'] or 'none'} "
            f"qualified={row['qualified_material_root_signal'] or 'none'}"
        )

    payload = build_payload(rows, errors)
    (OUT / "v0_2_stability_summary.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )

    if errors:
        raise SystemExit("V0.2 ROOT-STABILITY VALIDATION FAILED: " + "; ".join(errors))
    print("PAMIR v0.2 PUBLIC ROOT-STABILITY GATE PASSED")


if __name__ == "__main__":
    main()
