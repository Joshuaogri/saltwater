# BP06 opening police cohort provisioning

**Purpose:** connect the canon's opening police cohort to existing canonical BP03 people without duplicating person identities.

## What this adds

- Migration proposal `db/proposals/0033_bp06_opening_personnel_cohort.sql`.
- A stable opening-cohort register and one-to-one member crosswalk.
- A transactionally idempotent `sw_police.provision_opening_personnel_cohort(jsonb,text)` function.
- Explicit employee category on personnel dossiers and correct BP06 appointment-type mapping.
- Optional supervisor reference for established appointments; recruits still require the existing authorised-supervisor path.
- Bootstrap permission for `PERSONNEL_APPOINTED` events at tick zero only, while bootstrap is open.

## Input contract

The function accepts exactly 500 entries, each containing an existing `person_id` and one of:
`sworn_officer`, `civilian_employee`, or `technical_professional`.

Every person must already exist in BP03 and have living/included population state. The human-player identity is excluded. Duplicate identities, missing people, unsupported categories, prior personnel dossiers, or a different replay manifest are rejected.

It does not create people, alter population state/counters, allocate ranks, fill posts, create BP07 career episodes, or create BP08 unit memberships. Those are separate domain operations. Service numbers are issued once and retained in the member crosswalk.

## Verification

The first disposable acceptance passed in [PKG-001 run 45868150806](../test-evidence/BP06-opening-personnel-cohort-run-0001.md). The successful schema-application step includes migration 0033 and the opening-cohort acceptance script. This is step-level evidence; the wider PKG-001 workflow was still running when recorded.

`tests/pkg001/opening_personnel_cohort_acceptance.sql` creates 500 disposable canonical people inside a transaction, provisions them, checks one-to-one personnel/service records, idempotency, category preservation, unchanged population count and unchanged vacant posts, then rolls back.

This is a proposal and disposable acceptance test only. The live Neon database currently has no BP03/BP06 tables or person rows, and no production write has been made. The eventual 500-person input manifest must be generated from the approved BP03 opening population seed, not from authorised-post vacancies.
