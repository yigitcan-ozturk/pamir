# Holdout H7 Telemetry Gate Findings

Run: 36014778350
Artifact digest: sha256:e23e642f933e22bcc1ce94fa69b27931a63f5f258b3e6808518fc2ca0a77f484

The 18-case pinned pool produced 14 accepted_pre_pamir, 4 quarantined, 0 rejected. All 14 previously accepted cases remained accepted.

H7 acquisition candidates were quarantined at the pre-PAMIR telemetry gate because the conservative real-flight evidence requirements were not satisfied by the logged topic set. They remain excluded from the accepted holdout. No PAMIR scoring was used to make this decision.

Current accepted_pre_pamir holdout: 14 cases = 12 healthy_control + 2 incident.
Protocol gap: 6 additional accepted cases total, including at least 4 additional incident cases.

Decision: do not weaken the predeclared telemetry gate. Source new cases instead.
