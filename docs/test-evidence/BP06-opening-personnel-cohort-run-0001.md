# BP06 Opening Police Cohort Provisioning — Acceptance Run 0001

**Workflow:** [PKG-001 disposable PostgreSQL validation, run 45868150806](https://github.com/Joshuaogri/saltwater/actions/runs/45868150806)  
**Source commit:** `2dc113c257fdb68066938b42b070a34af25d7c81`  
**Branch:** `main`  
**Date:** 2026-11-26  
**Result:** **BP06 opening-cohort acceptance step passed**  
**Production Neon:** unchanged

## What was executed

The workflow applied `db/proposals/0033_bp06_opening_personnel_cohort.sql` to disposable PostgreSQL and then ran `tests/pkg001/opening_personnel_cohort_acceptance.sql` inside the same successful schema-application step.

The acceptance fixture:
- created 500 canonical BP03 person records inside a transaction;
- set all 500 to living/included population state;
- supplied 400 sworn-officer, 75 civilian-employee and 25 technical-professional categories;
- provisioned 500 BP06 personnel dossiers against those existing person IDs;
- verified 500 active primary service engagements, 500 appointment events and 500 issued service numbers;
- verified category and appointment-type mapping;
- replayed the same manifest and confirmed idempotent result;
- rejected a 499-person input, duplicate identity input and a missing canonical person;
- verified personnel provisioning caused zero additional population count;
- verified all 500 authorised posts remained vacant and no BP07 post appointments or BP08 unit memberships were created;
- rolled back the fixture transaction.

The successful GitHub Actions step is `Apply foundation and PKG-001 to disposable PostgreSQL`. This is step-level evidence only; the wider PKG-001 workflow had not yet completed when this record was written.

## Remaining work

The actual BP03 opening 500-person identity manifest is not yet present. The live Neon database currently has no `sw_people` or `sw_police` tables/person records, and no production migration or seed was run. The next integration is to generate the canonical BP03 identities and category mapping, then connect BP07 career/post assignments and BP08 unit memberships.
