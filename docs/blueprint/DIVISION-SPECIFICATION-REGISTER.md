# Saltwater Division Specification Register

**Version:** 1.0  
**Date:** 2026-11-22  
**Structure:** Fixed BP-01–BP-44; no structural change.  
**Purpose:** Track design specification separately from implementation, testing and verification.

| ID | Division | Specification status | Implementation | Test | Verification | Specification |
|---|---|---|---|---|---|---|
| BP-01 | Game Identity, Foundations and Governing Rules | DESIGNED_DRAFT | NOT_STARTED | NOT_STARTED | NOT_STARTED | [BP-01](divisions/BP-01-GAME-IDENTITY-FOUNDATIONS-GOVERNING-RULES.md) |
| BP-02 | Sovereign City-State and Geographical Architecture | DESIGNED_DRAFT | NOT_STARTED | NOT_STARTED | NOT_STARTED | [BP-02](divisions/BP-02-SOVEREIGN-CITY-STATE-GEOGRAPHY.md) |
| BP-03 | Population and Individual Simulation | DESIGNED_DRAFT | NOT_STARTED | NOT_STARTED | NOT_STARTED | [BP-03](divisions/BP-03-POPULATION-AND-INDIVIDUAL-SIMULATION.md) |
| BP-04 | Built World, Property, Businesses and Organisations | DESIGNED_DRAFT | NOT_STARTED | NOT_STARTED | NOT_STARTED | [BP-04](divisions/BP-04-BUILT-WORLD-PROPERTY-BUSINESSES-ORGANISATIONS.md) |
| BP-05 | Police Architecture | DESIGNED_DRAFT | NOT_STARTED | NOT_STARTED | NOT_STARTED | [BP-05](divisions/BP-05-POLICE-ARCHITECTURE.md) |
| BP-06 | Police Personnel | DESIGNED_DRAFT | NOT_STARTED | NOT_STARTED | NOT_STARTED | [BP-06](divisions/BP-06-POLICE-PERSONNEL.md) |
| BP-07 | Career System | DESIGNED_DRAFT | NOT_STARTED | NOT_STARTED | NOT_STARTED | [BP-07](divisions/BP-07-CAREER-SYSTEM.md) |
| BP-08 | Units and Deployment | DESIGNED_DRAFT | NOT_STARTED | NOT_STARTED | NOT_STARTED | [BP-08](divisions/BP-08-UNITS-AND-DEPLOYMENT.md) |
| BP-09 | Police Resources | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-10 | Patrol Operations | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-11 | Emergency Communications | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-12 | Incident Management | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-13 | Crime Architecture | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-14 | Crime Generation | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-15 | Case Management | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-16 | Investigation | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-17 | Victims and Witnesses | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-18 | Suspects and Offenders | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-19 | Interviews and Interrogations | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-20 | Surveillance | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-21 | Intelligence | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-22 | Crime Scenes | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-23 | Evidence Management | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-24 | Forensics | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-25 | Arrests and Warrants | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-26 | Custody Management | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-27 | Legal Processes | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-28 | Courts and Outcomes | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-29 | Corrections | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-30 | Department Governance | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-31 | Professional Standards | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-32 | Training and Development | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-33 | Human Resources | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-34 | Finance and Procurement | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-35 | Simulation Engine | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-36 | Relationships and Social Context | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-37 | Time and Scheduling | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-38 | Records and Databases | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-39 | Persistence and Recovery | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-40 | Interface | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-41 | Notifications and Reporting | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-42 | Security and Permissions | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-43 | Testing and Quality Assurance | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |
| BP-44 | Configuration and Change Control | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED | — |

## Governing status rules

- `NOT_STARTED`: no full division specification exists.
- `DESIGNED_DRAFT`: specification draft exists; not user-approved.
- `DESIGNED`: complete specification reviewed and approved, with source traceability.
- `IMPLEMENTED`: corresponding implementation artefacts exist and are linked.
- `TESTED`: required tests executed and results recorded.
- `VERIFIED`: implementation/tests pass, dependencies reconcile and reproducible evidence is linked.
- `BLOCKED`: documented conflict/dependency/failure prevents progression.
- `RETIRED`: formally retired by approved change; history retained.

Statuses are independent across specification, implementation, testing and verification. No status is inferred from a commit or document alone.

## Current sequence

1. Crosswalk structural coverage: all 52 source divisions, 168 requirement IDs and 60 test IDs are mapped; semantic completeness/ownership audit remains to be completed. See [52→44 crosswalk](SALTWATER-52-TO-44-CROSSWALK.md).
2. BP-01: full specification draft created; user review/approval pending.
3. BP-02: full architecture draft created; exact map canon decisions remain open.
4. BP-03: full population architecture draft created; population-scope countability decisions remain open.
5. BP-04: full built-world/property/business/organisation specification draft created; business baseline and distribution decisions remain open.
6. BP-05: full police institutional architecture specification draft created; command titles, unit structure and staffing allocation remain open.
7. BP-06: full police personnel specification draft created; category taxonomy, service-number format, probation and restricted-record policy decisions remain open.
8. BP-07: full career system specification draft created; rank ladder, promotion thresholds, service-credit rules and several Chief-tenure implementation details remain open.
9. BP-08: full units and deployment specification draft created; exact unit hierarchy, establishment, staffing, geographic coverage and readiness policies remain open.\n10. Continue BP-09 through BP-44 in numeric order, preserving the same specification contract and traceability.

**No Neon write has been made or authorised by these documents.**
