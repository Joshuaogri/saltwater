# Saltwater Master Blueprint

**Baseline:** Kingswell Master Blueprint BP-01–BP-44, approved 2026-11-20; adopted and adapted for Saltwater by user instruction 2026-11-22.  
**Status:** Adopted design framework; Saltwater-specific division specifications and acceptance evidence remain to be completed.  
**Source:** [Kingswell Master Blueprint](https://github.com/Joshuaogri/Kingswell-Police-Simulation/blob/main/docs/blueprint/MASTER-BLUEPRINT.md) and [Division Register](https://github.com/Joshuaogri/Kingswell-Police-Simulation/blob/main/docs/blueprint/DIVISION-REGISTER.md).

## Binding Saltwater canon
- Fictional sovereign **city-state** named Saltwater; one city, one sovereign jurisdiction; no second playable city, territory or world expansion.
- Population ceiling **10,000 living people total**, police included. Initial design: 9,000 residents + 500 police = 9,500; 500 capacity reserve. Entries/deaths/permanent exits reconcile atomically.
- At least **10,000 businesses**; all entities have stable IDs and coherent premises, people, schedules and records.
- Police is the deepest simulation; all other systems function sufficiently to support and affect policing, without equal simulation depth.
- One individual officer is played; text-first is permanent and complete. Maps/graphics are optional.
- No simulation time advances while the player is absent.
- Neon PostgreSQL = persistence; GitHub = versioned source/specifications; ChatGPT = AI partner/interface.
- Extreme storage efficiency. Measure baseline and projected/actual bytes before and after every proposed database write; no Neon migration, seed, import or bulk write without explicit user approval.
- Preserve player agency, hidden information, causal continuity, provenance and historical records. Never reveal hidden case perpetrators unless the player types exactly **“bingo”**.

## Master divisions — adopted 44-part structure
| ID | Saltwater division | Scope |
|---|---|---|
| BP-01 | Game Identity, Foundations and Governing Rules | Canon, experience, agency, boundaries, authority and change control |
| BP-02 | Sovereign City-State and Geographical Architecture | Jurisdiction, districts, parcels, addresses, terrain, roads and spatial IDs |
| BP-03 | Population and Individual Simulation | 10k cap, identity, lifecycle, demographics, persistent NPCs and processing tiers |
| BP-04 | Built World, Property, Businesses and Organisations | Buildings, premises, ownership, tenancy, 10k+ businesses, public bodies, infrastructure and supporting city services |
| BP-05 | Police Architecture | Mandate, hierarchy, ranks, divisions, units, authority and command |
| BP-06 | Police Personnel | Individual employee records, recruitment, service, status and history |
| BP-07 | Career System | Recruit entry, training gates, promotion, transfer, discipline and retirement |
| BP-08 | Units and Deployment | Unit structure, staffing, qualifications, assignment and deployment lifecycle |
| BP-09 | Police Resources | Fleet, equipment, facilities, budgets, availability and maintenance |
| BP-10 | Patrol Operations | Beats, patrol, response, traffic, field activity and supervision |
| BP-11 | Emergency Communications | 911, call-taking, radio, CAD, triage and dispatch |
| BP-12 | Incident Management | Incident creation, attendance, command, reports, resources and closure |
| BP-13 | Crime Architecture | Complete offence/non-offence taxonomy, elements and classification |
| BP-14 | Crime Generation | Causal, varied crime and incident occurrence; no arbitrary outcomes |
| BP-15 | Case Management | Case lifecycle, ownership, objectives, links, reviews and closure |
| BP-16 | Investigation | Investigative actions, plans, leads, decisions and case progression |
| BP-17 | Victims and Witnesses | Identity, roles, welfare, vulnerability, statements and contact |
| BP-18 | Suspects and Offenders | Person status, links, risk, history and legal-status distinctions |
| BP-19 | Interviews and Interrogations | Planning, participants, records, statements, versions and safeguards |
| BP-20 | Surveillance | CCTV, observation, technical monitoring, coverage, retrieval and continuity |
| BP-21 | Intelligence | Sources, reliability, confidence, analysis, dissemination and review |
| BP-22 | Crime Scenes | Control, boundaries, access, searches, examination and release |
| BP-23 | Evidence Management | Recovery, exhibits, packaging, seals, custody, transfer and disclosure |
| BP-24 | Forensics | Disciplines, submissions, methods, results, limitations and review |
| BP-25 | Arrests and Warrants | Grounds, authority, applications, execution, search and seizure |
| BP-26 | Custody Management | Booking, detention, welfare, property, review, release and continuity |
| BP-27 | Legal Processes | Charging, disclosure, prosecution and procedural workflow |
| BP-28 | Courts and Outcomes | Hearings, evidence, rulings, verdicts, sentencing and appeals |
| BP-29 | Corrections | Sentence execution, supervision, rehabilitation, release and recall |
| BP-30 | Department Governance | Policy, command, delegation, oversight and institutional decisions |
| BP-31 | Professional Standards | Complaints, misconduct, investigations, hearings and accountability |
| BP-32 | Training and Development | Training catalogue, qualifications, competency and progression |
| BP-33 | Human Resources | Employment, contracts, attendance, leave, pay, welfare and workforce |
| BP-34 | Finance and Procurement | Public/police finance, budgets, revenue, purchasing, assets and accounting |
| BP-35 | Simulation Engine | Authoritative state, event processing, causality, NPC activity and time controls |
| BP-36 | Relationships and Social Context | Households, relationships, social networks and community context |
| BP-37 | Time and Scheduling | One clock, calendar, shifts, routines, deadlines and no offline time advance |
| BP-38 | Records and Databases | Neon schemas, IDs, constraints, provenance, migrations and data ownership |
| BP-39 | Persistence and Recovery | Save state, backups, restore, recovery and continuity |
| BP-40 | Interface | Laptop-style text interface, commands, records and complete text gameplay |
| BP-41 | Notifications and Reporting | Alerts, reports, briefings, summaries and delivery rules |
| BP-42 | Security and Permissions | Roles, access, clearances, secrets and hidden-information boundaries |
| BP-43 | Testing and Quality Assurance | Unit, integration, replay, edge, population, storage and acceptance tests |
| BP-44 | Configuration and Change Control | Canon versions, settings, traceability, controlled amendments; no world expansion |

## Division specification contract
Every BP division must define: purpose; scope/exclusions; entities and fields; lifecycle/state transitions; rules and invariants; inputs/outputs; dependencies and ownership; permissions; exceptions/edge cases; cross-system effects; acceptance tests; evidence. No placeholder coverage or implied implementation.

## Governance and delivery
- BP-01–BP-44 are the fixed top-level structure. Do not add, remove, reorder, split, merge or rename divisions without explicit user approval.
- The existing Saltwater 52-division draft is source material only. Crosswalk every requirement into these 44 divisions; preserve requirements, not the old division count. Record unresolved conflicts; do not silently discard requirements.
- Blueprint approval, implementation, testing and verification are separate states. Documentation alone never proves implementation.
- Keep the Kingswell master unchanged. Saltwater adaptations belong only in the Saltwater repository.
- No Neon writes are authorised by this blueprint adoption.
