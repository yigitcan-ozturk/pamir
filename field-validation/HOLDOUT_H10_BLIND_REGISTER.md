# Holdout H10 Blind Register

Availability was checked before registration without PAMIR execution or telemetry outcome scoring. Labels below are assigned solely from the public PX4 source narrative and locked before PAMIR.

| Case | Flight Review UUID | Label | Source rationale |
|---|---|---|---|
| H10-001 | e64738dc-70fc-4459-9bac-5cdb3820f927 | incident | PX4 report describes an armed multicopter takeoff followed by Orbit-mode stall/hover and route deviation when NAV_MC_ALT_RAD=0. |
| H10-002 | eed65553-b985-4340-bb81-f30bc0cb8e80 | incident | PX4 VTOL RTL report documents a reproduced in-flight No Valid Mission Available failure. |
| H10-003 | 104de51f-29a2-40af-b896-f0c498574fb5 | incident | Same PX4 VTOL RTL report documents a reproducible fixed-wing transition failure leaving the vehicle stuck in the air. |

Excluded after source review:
- 548ce3e2-acb2-4098-bfe4-224e28afa05f: source explicitly identifies this UUID as simulation; the separate real-flight UUID was not the probed record.

Acquisition failure or telemetry insufficiency means quarantine. No PAMIR-derived relabelling, substitution, or gate weakening.
