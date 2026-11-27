# BP03 Population Qualification Union — Disposable Acceptance 0001

Proposal: db/proposals/0010_bp03_population_qualification_union.sql  
Acceptance: tests/pkg001/population_union_acceptance.sql  
Blueprint: BP03 — Population and Individual Simulation  
Canon: SW-CANON-001, distinct living-person union  
Environment: disposable PostgreSQL only  
Production Neon: not applied

## Implemented
- Three explicit qualifications on one canonical person state: usual residence, physical presence, active police-service membership.
- One person counts once regardless of whether one, two or all three qualifications are active.
- A serialized counter-row lock enforces the 10,000 cap on admissions and lifecycle transitions.
- Qualification changes and death transitions use committed events and append-only history.
- Canonical person creation reserves the canonical name through SW-UNS and creates an initially unqualified living identity.
- Idempotent source references and a read-only population summary.

## Acceptance
The SQL test covers one qualification, two-way overlap, three-way overlap, removal of residence while other qualifications remain, physical exit while police membership remains, removal of the final qualification, nonresident arrival, death preserving identity, and refusal to requalify a deceased person. The 9,999-to-10,000 concurrency fixture now explicitly qualifies its test people as usual residents.

## Boundaries
The proposal refuses to migrate existing population rows because the prior single inclusion flag does not identify the qualifying category. Residence-to-BP02-address linkage and automatic activation/deactivation from BP06 service-engagement events remain subsequent integration work. No production data has been changed.
