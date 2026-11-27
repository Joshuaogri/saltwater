# BP03–BP06 Personnel Population Integration

## Contract
Each BP06 personnel service event for appointment, service-state change, category change or rescission recalculates the active-police-service qualification on the same canonical BP03 person. It does not create a new person or add a second population contribution.

The integration preserves existing usual-resident and physically-present flags. It counts primary sworn, civilian, technical-professional and auxiliary service appointments in active, leave, suspended, secondment-out, secondment-in or notice states. Contractors and terminal/non-service states are excluded.

## Acceptance
The BP06 personnel-service disposable acceptance now asserts that every personnel dossier has a corresponding living canonical person with active-police-service qualification and that the BP03 summary's active police subset equals the number of personnel dossiers.

## Limits
The acceptance validates initial appointment propagation. Detailed service-state transition tests and BP02 address/residence linkage remain follow-up work. No production Neon write or opening cohort seed was performed.
