# BP03 integrated opening world and population acceptance

**Date:** 2026-11-27  
**Blueprint:** BP03 — Population and Individual Simulation  
**Workflow:** [SW-DB-001 disposable world provisioning and capacity proof](https://github.com/Joshuaogri/saltwater/actions/runs/46041993980)  
**Result:** PASS  
**PostgreSQL:** Disposable PostgreSQL 16.16  
**Main commit under test:** a321f99591065fd7f7adbc16c483abdeeb051804

## BP03 integration

The workflow applied the BP03 population qualification union, BP02-linked residence service, and individual simulation proposals 0036–0039 alongside the existing disposable platform and world schema. The BP03 residence acceptance passed with canonical BP02 address links. The opening world fixture then created and reconciled:

- 9,500 canonical people
- 9,000 usual residents
- 500 physically present police-subset cohort members
- 9,500 counted living people at opening
- 10,000 canonical businesses and 10,000 business-name reservations
- World tick remained 0; simulation time did not advance during provisioning

The police-subset fixture members were counted through physical presence. It deliberately created no BP06 personnel dossiers or active-police-service flags; those remain a separate personnel-domain integration.

## Population lifecycle and capacity

The SW-DB-001 acceptance passed opening arithmetic, identity, lifecycle exit/re-entry, qualification history and rollback checks. The workflow then filled the shared population to 9,999 and passed the concurrent final-slot test. Exactly one competing admission succeeded and the other was rejected. Final world reconciliation:

- 10,000 canonical people
- 10,000 counted living people
- 10,000 canonical businesses
- 10,000 business-name reservations
- Population counter exactly 10,000
- World tick 0

The workflow also passed BP04 disposable property/premises and physical-profile acceptance, idempotent provisioning, query-latency measurement and backup/restore.

## Storage measurements

- Full disposable database after the 9,500-person / 10,000-business opening fixture: **57,506,839 bytes**
- Fixture growth over the schema-only baseline: **43,573,248 bytes**
- BP03 population + residence schema-only growth: **212,992 bytes**
- BP03 individual simulation schema-only growth (proposals 0036–0039): **532,480 bytes**
- BP03 proposal 0036 alone in the focused workflow: **139,264 bytes**
- BP04-01 schema growth: **696,320 bytes**
- BP04-02 schema growth: **933,888 bytes**

All figures are disposable PostgreSQL 16.16 measurements, not Neon estimates.

## Scope boundary

This proves the integrated population union, 9,500-person opening arithmetic, residence interface, lifecycle history and shared 10,000-person cap in a disposable world. It does not seed production Neon. The 9,000-person candidate-to-dwelling allocation remains a separate candidate package; this world fixture does not materialise 9,000 actual residence/household rows. Household membership has its own focused acceptance against the canonical BP04 property stack. The 500 police cohort is not yet linked to production BP06 personnel dossiers, BP07 careers or BP08 unit memberships.
