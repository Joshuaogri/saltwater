# BP04-03 — Stage B Schema Run 0001

**Date:** 2026-11-24  
**Branch:** `main`  
**Commit under test:** `ebf698dcc624ab4082b7fad1161a0f40e6f16a70`  
**Workflow:** [BP04-03 Stage B Disposable PostgreSQL — run 45481959712](https://github.com/Joshuaogri/saltwater/actions/runs/45481959712)  
**Result:** PASS

## Scope

Applied the BP-02-owned parcel/address candidate schema to a fresh disposable PostgreSQL 16 database after applying the existing platform and BP04 foundations. Loaded the SW-GEO-V1 identity fixture and the BP04-01 test-only parcel/address references. Ran synthetic acceptance in a transaction that was rolled back.

No Neon connection or production write occurred. No operational spatial IDs, live parcel fabric, canonical addresses or city inventory were seeded.

## Schema delivered

Proposal `0013_bp02_parcel_address_candidate.sql` adds:

- `sw_geo.parcel_profile`: version-linked parcel land use, development state, area/basis, geometry quality and provenance.
- `sw_geo.address_profile`: stable BP-02 address identity, parcel/neighbourhood/optional-road relationships, locator type/value, frontage semantics, active version and provenance.
- `sw_geo.parcel_lineage`: append-only predecessor/successor events for splits, mergers, boundary replacement and retirement.
- `sw_geo.address_alias`: append-only former/common/local/delivery locator history.
- Kind guards enforce parcel kind 6, neighbourhood kind 4, road kind 7 and address kind 11.
- Parcel geometry payload SHA-256 is checked against the stored payload on profile insertion.
- Partial unique indexes reject duplicate active locators within a road or parcel scope.
- Candidate profile/history tables reject update/delete; no record can be marked approved by this candidate schema.

## Test results

- Python Stage B contract tests: 4 passed.
- Disposable PostgreSQL 16 schema application: passed.
- Synthetic parcel and address insertion: passed.
- Duplicate active road locator rejection: passed.
- Wrong-kind road reference rejection: passed.
- Mismatched geometry checksum rejection: passed.
- Parcel predecessor/successor lineage insertion: passed.
- Append-only parcel profile mutation rejection: passed.
- Acceptance transaction: rolled back.

## Storage

- Proposal source file: 10,668 bytes.
- Disposable database schema growth: 294,912 bytes.

Schema growth is the measured database-size delta for this isolated migration step. It excludes any full-city parcel/address candidate data, which has not yet been generated.

## Status and remaining work

**Stage B schema foundation: VERIFIED.**  
**Stage B city parcel fabric and address candidate generation: NOT YET BUILT.**

Next work must generate a reproducible, topology-aware candidate parcel fabric from the committed fictional geography, validate polygon coverage/overlap/gaps and neighbourhood assignment, and only assign a road locator where frontage is supported by geometry. Campus, compound, waterfront, service and unfronted locations must remain explicit. The 100 Stage A source mappings remain unresolved and no operational geography approval is implied.
