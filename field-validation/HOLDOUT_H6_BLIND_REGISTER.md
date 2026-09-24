# Holdout H6 Blind Incident Candidate Register

Status: source-labelled candidates; PAMIR not scored. Acquisition availability is tested before acceptance.

| Case | Flight Review UUID | Label | Source narrative |
|---|---|---|---|
| H6-001 | 5c3b168c-9a6d-461b-9a78-c81855c53f61 | incident | Real VTOL test; erroneous angular-rate setpoints/motor output after Offboard-to-Mission transition. |
| H6-002 | 4fb99f3a-2c14-4fea-a653-5f9d2f47c675 | incident | FMUv6XRT hardfault occurred mid-air during mission and resulted in crash/loss of test vehicle. |
| H6-003 | f7e9a824-e8bb-419d-a084-36574ce042f5 | incident | Fixed-wing airspeed-sensor failure during takeoff; source reports crash in manual mode. |
| H6-004 | fab2c889-e3c8-4ff6-a6cf-6b5af31cd0ba | incident | Public PX4 issue documents software/Pixhawk restart behavior during flight. |
| H6-005 | 54757cef-3b2c-4803-9cbe-737a17e9b37d | incident | Public PX4 issue documents flight crash associated with I2C malfunction. |
| H6-006 | 101ed7b8-2a88-4bd0-8faf-8a197772bd72 | incident | Real VTOL quadchute/RTL failure report: vehicle flies away instead of returning home. |

Labels are locked from public source narratives before PAMIR execution. All UUIDs were checked absent from Corpus v1 at registration. Acquisition failure means quarantine, not substitution. PAMIR must not execute in acquisition.
