# BP03 Opening Civilian Resident Identity Candidate Seed — Build 0001

**Dataset:** `SW-OPENING-CIVILIAN-RESIDENT-SEED-V1`  
**Build workflow:** [46016834874 — success](https://github.com/Joshuaogri/saltwater/actions/runs/46016834874)  
**Source commit:** `6feb2becb68fca921d1b17b7ec822ec64ea6eb73`  
**Generated data commit:** `e6422fb04ea4d40d6ef33bb973a6375b057f541f`  
**Branch:** `main` only  
**Date:** 2026-11-27

## Result

- Exactly 9,000 deterministic three-part civilian resident name candidates.
- Five resident cohort regression tests passed; five existing police cohort tests also passed.
- Exact normalized names are unique within the resident cohort.
- Zero exact normalized-name overlap with the 500-person opening police candidate cohort.
- Candidate references are stable: `SWCIV-000001` through `SWCIV-009000`.
- Readable JSON: 4,603,381 bytes.
- Deterministic gzip: 253,572 bytes.
- Manifest SHA-256: `e8dcfca02f7a3f2d80d53a90a79eae1b572be135d68653f57a3c451f014dbe43`.

## Opening reconciliation

| Cohort | Candidates |
|---|---:|
| Civilian usual residents | 9,000 |
| Active police-service people | 500 |
| Distinct opening target | 9,500 |
| Hard population ceiling | 10,000 |
| Unused headroom | 500 |

The two candidate cohorts are deliberately disjoint. The opening police people are not added on top of the 10,000 ceiling.

## Data boundary

The dataset contains names and stable candidate/source references only. It does not infer age, date of birth, sex, gender, ethnicity, nationality, citizenship, occupation, household, address or personal history. Residence assignment to BP02 parcel/address identities is not yet performed. Candidate names remain pending authoritative SW-UNS exact/near-duplicate reservation.

No canonical BP03 person rows or BP06 personnel appointments were created. No production Neon write or import was performed. The manifest records `production_import_authorized=false`.

## Next BP03 implementation

Implement the canonical person and population service against the approved SW-CANON-001 counting rule: one distinct living-person count over the union of usual residence, physical presence and active police-service membership. The existing single inclusion-flag proposal is insufficient. Admissions must be atomic under concurrency, lifecycle changes must be append-only/auditable, and resident identities must link to valid BP02 address/parcel identities before the opening world is provisioned.
