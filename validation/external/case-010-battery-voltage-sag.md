# External Validation Case #010 — Battery Voltage Sag

## Status

**PASS**

PAMIR v0.1 detected a material battery-voltage deviation and selected the physical power/voltage signal as the root event. This matches the independently described incident family: battery voltage sag associated with aged/degraded batteries.

## Source

- Public PX4/Dronecode community flight log
- Log ID: `d4f2b663-9343-4375-b358-f62c495d4227`
- Source discussion: `Current sensor issue` (Dronecode/PX4 community)

## Ground truth / external diagnosis

The community analysis described a substantial battery voltage drop under load and indicated aged/degraded batteries rather than a current-sensor-only explanation. The operator reported the batteries were approximately 4–5 years old and decided to replace them.

Expected root family for this validation case: **physical battery / voltage sag**.

## Frozen PAMIR v0.1 result

PAMIR was run without tuning or modifying the frozen v0.1 baseline.

```text
FIRST DEVIATION: battery_status.voltage_v @ 56258536 us (score=9.361)
```

Root event:

```json
{
  "timestamp_us": 56258536,
  "signal": "battery_status.voltage_v",
  "value": 22.186479568481445,
  "baseline": 23.908119201660156,
  "score": 9.361,
  "confidence": 0.772,
  "evidence_start_us": 55758536,
  "evidence_end_us": 57008536,
  "reason": "rolling_robust_baseline_deviation",
  "relation": null,
  "parent_signal": null
}
```

## Assessment

- Incident/deviation detection: **PASS**
- Root family: **PASS — battery voltage / power**
- Ground-truth alignment: **PASS**
- Baseline modification: **none**

### Final classification

**PASS — external physical power/voltage case correctly rooted by frozen PAMIR v0.1.**

This case is evidence that v0.1 can correctly identify the root-cause family for at least one external real-world incident. It does not by itself establish a calibrated probability of causation or broad generalization across all incident classes.
