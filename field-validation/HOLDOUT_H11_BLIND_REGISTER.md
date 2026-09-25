# Holdout H11 Blind Register

H11 candidates were first screened only for source availability and neutral ULog structural sufficiency. No PAMIR output and no outcome label was used in that screen. Labels below are now assigned solely from public PX4 source narratives and locked before PAMIR.

| Case | Flight Review UUID | Label | Source rationale |
|---|---|---|---|
| H11-001 | bc2fa493-8cc7-4404-8695-d4e9775f5c0f | incident | PX4 issue explicitly identifies this UUID as a real flight test exhibiting aggressive jerking and velocity/acceleration setpoint jumps during external flight-mode switching. |
| H11-002 | 52331f5e-7ca7-4b2d-8864-5c65dfca7509 | incident | PX4 issue documents an outdoor GPS RTL flight where near-zero range data caused EKF2 terrain/HAGL reset and eventual maximum-thrust command. |
| H11-003 | 50e611ef-f73f-483a-aed3-b59703442ee8 | incident | PX4 Orbit-mode bug report documents inverted roll-stick direction behavior and links this flight log as reproduction evidence. |

Structurally admissible but excluded from the real-flight holdout:
- 247fac13-73ef-4efd-ab56-2b69385fe75c
- 2055ba6c-ecfe-4466-a8e4-1f2eb525c861
The source narrative identifies these as SITL/CI mission-sequence reproduction logs rather than independent real-flight evidence.

Acquisition/identity is pinned from the pre-registration structural probe. Any later SHA mismatch is quarantine. No PAMIR-derived relabelling, substitution, or gate weakening.
