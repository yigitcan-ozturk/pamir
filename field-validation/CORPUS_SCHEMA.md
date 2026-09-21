# Corpus record schema

Each flight is represented by one immutable provenance record.

Required fields:

- case_id
- source_project
- source_url
- download_url
- license
- retrieved_at_utc
- original_filename
- sha256
- vehicle_type
- px4_version
- board
- flight_mode
- classification: incident | healthy_control | unknown
- primary_family: ekf_gps | attitude_control | propulsion_motor | power_battery | failsafe | sensor_anomaly | other
- narrative_basis
- acceptance_status: candidate | accepted | rejected
- acceptance_reason
- predeclared_acceptance_criteria
- pamir_version
- pamir_root_event
- pamir_root_timestamp
- pamir_conclusion
- reproducibility_status
- notes

## Separation rule

Source/narrative classification and acceptance criteria must be recorded before interpreting PAMIR output. PAMIR output must never be used to retroactively manufacture ground truth.
