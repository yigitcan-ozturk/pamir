# External Validation Case #013 — Hexacopter Sudden Crash

## Status

**FAIL — detection miss**

Frozen PAMIR v0.1 completed the blind analysis before the independent community discussion was revealed and returned `NO DEVIATION DETECTED`.

After the result was locked, the PX4 community discussion was revealed. An independent reviewer reported an observable motor-level anomaly: while throttle was being increased before the descent, motor 6 reduced its speed.

The discussion did not establish a definitive root cause. Therefore this case is classified narrowly as a **detection miss**, not as a proven root-cause disagreement.

## Source

- Public PX4/Dronecode community incident log
- Discussion: `Hexacopter sudden crash`
- Log ID: `acee7ab5-5f65-452d-890f-a57b12b6d4db`
- Recorded SHA-256: `78535f531b1311818ef4ac16c9ce51a97331b2361f7bacd73ac065cefdcedaba`
- Vehicle: PX4 hexarotor
- Flight mode reported by operator: Position mode

## Blind-validation protocol

1. The real incident ULog was acquired from the public PX4 discussion.
2. Source identity/fingerprint was recorded.
3. PAMIR v0.1 remained frozen; no threshold or detector changes were made for this case.
4. PAMIR was run before reading the community replies/diagnosis.
5. The PAMIR result was locked.
6. Only then was the external discussion revealed and compared with the locked result.

## Frozen PAMIR v0.1 result

```text
NO DEVIATION DETECTED
```

Generated report:

```text
case-013-result.json
```

## Independent external observation

After the blind result was locked, the community analysis reported that when throttle was increased before the descent, **motor 6 reduced its speed**. The reviewer asked about propeller rotation direction and flight-controller orientation. The operator replied that propeller directions had been checked, the controller had no yaw orientation offset, and the aircraft had previously completed several flights.

The operator also asked whether a low thrust-to-weight ratio might explain the event. The reviewer stated that low thrust-to-weight can be problematic but, unless extremely low, would not normally explain a crash like this.

No definitive root cause was established in the discussion.

## Assessment

- Blind protocol: **PASS**
- Frozen baseline preserved: **PASS**
- Incident/deviation detection: **FAIL**
- Observable external anomaly: **motor 6 speed decreased while throttle was increased**
- Definitive root-cause comparison: **INCONCLUSIVE — external discussion did not establish one**
- Baseline modification: **none**

### Final classification

**FAIL — detection miss.**

The frozen PAMIR v0.1 baseline reported no deviation despite an independently observed motor-level anomaly in the incident log. This is retained as negative evidence and a documented limitation of v0.1 rather than being tuned away after the fact.

## Capability gap / next research lane

Case #013 motivates a separate post-v0.1 research lane for actuator/motor disagreement detection, including temporal comparison of commanded versus observed actuator/motor behavior where the telemetry supports it.

Any future improvement evaluated on this already-revealed case must be labelled a **retrospective regression result**, not a blind validation result. Generalization must be tested on a previously unseen external case (for example #014) before claiming new external validation evidence.
