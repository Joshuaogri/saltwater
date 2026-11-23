# Saltwater 52→44 Requirement Crosswalk

**Version:** 1.3 — division-by-division semantic audit register  
**Date:** 2026-11-22  
**Source:** `docs/governance/SALTWATER_MASTER_BLUEPRINT.json` (52 divisions; unchanged)  
**Target:** `docs/blueprint/SALTWATER-MASTER-BLUEPRINT.md` (BP-01–BP-44; fixed structure)  
**Purpose:** Lossless traceability from every source requirement and test to its destination specification.  
**Status:** Source-array IDs and source-wide metadata are mapped; semantic audit amendments recorded. Full specification incorporation and evidence remain pending.

## 1. Rules

1. The 52-division JSON remains the authoritative source for the original wording. It is not deleted, rewritten or silently superseded.
2. Source IDs below are stable logical IDs: `Snn.Rnn` = source division `nn`, requirement array item `nn` (1-based); `Snn.Tnn` = test array item `nn` (1-based). Cross-cutting rules use `Xnn`.
3. Source JSON pointers identify the exact original text: `/divisions/(nn-1)/req/(nn-1)` and `/divisions/(nn-1)/tests/(nn-1)`. This avoids duplicating or paraphrasing source requirements and keeps their wording intact.
4. Every source requirement and test is mapped to one or more BP destinations. Multiple destinations mean the requirement must be specified across those divisions, with one designated owner where stated; it does not permit duplicate or conflicting authorities.
5. The target BP structure remains exactly 44 divisions. This crosswalk does not approve new divisions or alter the target titles.
6. A mapped requirement is **not** thereby designed, implemented, tested or verified. Each target division must incorporate the mapped requirements into its complete specification and acceptance suite.
7. Where a source requirement spans multiple domains, preserve the complete requirement and define interfaces, ownership, event flow and shared invariants in the destination specifications.
8. No Neon schema, migration, seed, import or other database write is authorised by this document.

## 2. Source-to-target crosswalk

Notation: `R: Snn.Rnn→BP-xx` maps every requirement; `T: Snn.Tnn→BP-xx` maps every source test. All requirement and test text remains verbatim in the source JSON at the pointers defined above.

| Source | Source division | Requirement mapping | Test mapping | Coverage / ownership notes |
|---|---|---|---|---|
| S01 | Sovereignty, jurisdiction and constitutional order | R: S01.R01→BP-01,BP-02,BP-30,BP-44; S01.R02→BP-01,BP-27,BP-30,BP-42; S01.R03→BP-01,BP-02,BP-44 | T: S01.T01→BP-02,BP-44; S01.T02→BP-01,BP-30,BP-42 | BP-01 owns canon; BP-02 owns the single bounded territory; BP-30 owns institutions and authority; BP-27 covers legal hierarchy/process; BP-44 controls change and forbids expansion. |
| S02 | Geography, land and spatial reference | R: S02.R01→BP-02; S02.R02→BP-02,BP-04,BP-10,BP-12,BP-22,BP-35; S02.R03→BP-02,BP-40 | T: S02.T01→BP-02; S02.T02→BP-02,BP-04,BP-35 | BP-02 owns canonical spatial IDs and geometry; consumers reference, never redefine, locations. |
| S03 | Population accounting and demographic model | R: S03.R01→BP-01,BP-03,BP-06; S03.R02→BP-03,BP-38; S03.R03→BP-03,BP-36,BP-37; S03.R04→BP-03,BP-35,BP-38; S03.R05→BP-03,BP-06,BP-33 | T: S03.T01→BP-03,BP-38; S03.T02→BP-03,BP-35; S03.T03→BP-03,BP-06 | BP-03 owns the single population ledger and atomic cap enforcement; police/personnel systems are subsets, not parallel population counts. |
| S04 | Person identity and life records | R: S04.R01→BP-03,BP-04,BP-33,BP-36,BP-37; S04.R02→BP-03,BP-35,BP-38; S04.R03→BP-03,BP-15,BP-16,BP-17,BP-18,BP-35 | T: S04.T01→BP-03,BP-38; S04.T02→BP-03,BP-35,BP-38 | BP-03 owns person identity/lifecycle; domain records hold specialised attributes; relevance promotion is permanent and cannot erase history. |
| S05 | Households, relationships and social networks | R: S05.R01→BP-03,BP-36; S05.R02→BP-03,BP-36,BP-37,BP-38; S05.R03→BP-14,BP-17,BP-18,BP-21,BP-35,BP-36 | T: S05.T01→BP-03,BP-36,BP-38 | BP-36 owns relationship semantics; BP-03 owns identity and lifecycle; case roles remain distinct from guilt or proof. |
| S06 | Housing, property and tenancy | R: S06.R01→BP-04,BP-34; S06.R02→BP-04,BP-33,BP-34,BP-38; S06.R03→BP-04,BP-20,BP-22,BP-35,BP-37 | T: S06.T01→BP-04,BP-35,BP-37 | BP-04 owns property, ownership, occupancy and access rights; time-valid occupancy/access is shared with BP-20/BP-22 evidence timelines. |
| S07 | Businesses and commercial economy | R: S07.R01→BP-04,BP-38; S07.R02→BP-04,BP-09,BP-34,BP-35,BP-36; S07.R03→BP-04,BP-10,BP-11,BP-12,BP-15,BP-16,BP-21; S07.R04→BP-04,BP-35,BP-43 | T: S07.T01→BP-04,BP-38; S07.T02→BP-04,BP-33,BP-35 | BP-04 owns the business registry and minimum 10,000 businesses; finance, staffing, premises and police consumers reference business IDs. |
| S08 | Employment, labour and professional life | R: S08.R01→BP-04,BP-06,BP-07,BP-33,BP-34; S08.R02→BP-03,BP-04,BP-35,BP-36,BP-37; S08.R03→BP-04,BP-06,BP-33 | T: S08.T01→BP-03,BP-04,BP-33,BP-35,BP-37 | BP-33 owns general employment lifecycle; BP-06/BP-07 own police-specific employment and career rules. |
| S09 | Markets, trade, supply chains and logistics | R: S09.R01→BP-02,BP-04,BP-09,BP-34; S09.R02→BP-02,BP-04,BP-09,BP-34,BP-35; S09.R03→BP-01,BP-02,BP-04,BP-34 | T: S09.T01→BP-04,BP-09,BP-34,BP-35 | BP-04 owns commercial actors; BP-09 police logistics/resources; BP-34 accounting/procurement; off-map dependencies do not create playable territory. |
| S10 | Public finance, taxation and economic accounts | R: S10.R01→BP-30,BP-33,BP-34; S10.R02→BP-03,BP-04,BP-34; S10.R03→BP-34,BP-38,BP-43 | T: S10.T01→BP-34,BP-38,BP-43 | BP-34 owns accounting model, transaction rules and public/police budgets; all posted amounts must reconcile. |
| S11 | Government and public administration | R: S11.R01→BP-01,BP-30,BP-42; S11.R02→BP-04,BP-30,BP-31,BP-34; S11.R03→BP-30,BP-38,BP-42 | T: S11.T01→BP-30,BP-38,BP-42 | BP-30 owns public institutional structure and decision authority; BP-04 represents operational bodies and premises. |
| S12 | Civil registry and public records | R: S12.R01→BP-03,BP-04,BP-30,BP-38; S12.R02→BP-38,BP-42,BP-44; S12.R03→BP-16,BP-27,BP-38,BP-42 | T: S12.T01→BP-38,BP-42,BP-44 | BP-38 owns authoritative record/version/provenance rules; domain owners remain responsible for their source records. |
| S13 | Healthcare and public health | R: S13.R01→BP-04,BP-09,BP-12,BP-17,BP-26,BP-35; S13.R02→BP-03,BP-12,BP-17,BP-22,BP-23,BP-24,BP-28; S13.R03→BP-38,BP-42 | T: S13.T01→BP-04,BP-09,BP-12,BP-35 | BP-04 represents providers and facilities; BP-12/BP-17/BP-24 handle operational interfaces; BP-42 controls restricted access. Healthcare remains proportionate, not a second deep simulation. |
| S14 | Education, training and research | R: S14.R01→BP-03,BP-04,BP-07,BP-32,BP-33,BP-37; S14.R02→BP-07,BP-09,BP-32; S14.R03→BP-03,BP-07,BP-32,BP-33,BP-38 | T: S14.T01→BP-03,BP-07,BP-32,BP-38 | BP-03 owns individual education participation/history; BP-04 provider/programme/facility/capacity; BP-32 police training; BP-07 police career gates; BP-33 staff employment; BP-37 schedules. |
| S15 | Social care, welfare and community support | R: S15.R01→BP-04,BP-17,BP-30,BP-36; S15.R02→BP-04,BP-17,BP-30,BP-38; S15.R03→BP-03,BP-14,BP-17,BP-18,BP-35,BP-36 | T: S15.T01→BP-04,BP-17,BP-30,BP-38 | BP-04 represents services/providers; BP-17 owns victim/witness support interfaces; BP-30 owns public-service governance. |
| S16 | Utilities, energy and communications infrastructure | R: S16.R01→BP-04,BP-09,BP-35; S16.R02→BP-04,BP-09,BP-10,BP-11,BP-12,BP-35; S16.R03→BP-04,BP-09,BP-12,BP-41 | T: S16.T01→BP-04,BP-09,BP-35 | BP-04 owns infrastructure assets/operators; BP-09 owns police resource dependencies; BP-35 propagates geographically bounded outage/restoration effects. |
| S17 | Roads, transport and mobility | R: S17.R01→BP-02,BP-04,BP-09,BP-10,BP-11; S17.R02→BP-03,BP-09,BP-10,BP-11,BP-12,BP-35,BP-37; S17.R03→BP-10,BP-11,BP-12,BP-16,BP-20,BP-22 | T: S17.T01→BP-02,BP-10,BP-11,BP-35 | BP-02 owns road geometry; BP-04 owns transport operators/facilities; BP-10/BP-11 consume routes and travel constraints. |
| S18 | Buildings, facilities and physical assets | R: S18.R01→BP-02,BP-04,BP-09,BP-22; S18.R02→BP-04,BP-09,BP-20,BP-22,BP-23; S18.R03→BP-20,BP-22,BP-23,BP-35,BP-37 | T: S18.T01→BP-04,BP-20,BP-22,BP-35 | BP-04 owns building/facility topology and access points; BP-20/BP-22 consume time-valid access facts. |
| S19 | Environment, weather and natural hazards | R: S19.R01→BP-02,BP-04,BP-09,BP-35,BP-37; S19.R02→BP-02,BP-09,BP-10,BP-12,BP-17,BP-20,BP-22,BP-24,BP-35; S19.R03→BP-35,BP-37,BP-38 | T: S19.T01→BP-02,BP-35,BP-37 | BP-35 owns environmental event effects and chronology; BP-02 provides geographic context. |
| S20 | Food systems and essential services | R: S20.R01→BP-04,BP-09,BP-34; S20.R02→BP-04,BP-09,BP-12,BP-35; S20.R03→BP-04,BP-09,BP-34,BP-35 | T: S20.T01→BP-04,BP-09,BP-34,BP-35 | BP-04 represents providers and supply actors; BP-09 handles police dependencies; BP-35 coordinates disruption/recovery. |
| S21 | Culture, media, recreation and civic life | R: S21.R01→BP-04,BP-30,BP-36; S21.R02→BP-04,BP-14,BP-17,BP-21,BP-35,BP-36,BP-37,BP-41; S21.R03→BP-04,BP-30,BP-36 | T: S21.T01→BP-04,BP-35,BP-36,BP-37 | BP-04 owns organisations/venues; BP-36 social context; BP-35/BP-37 event scheduling and causal effects. |
| S22 | Emergency services and civil protection | R: S22.R01→BP-04,BP-09,BP-11,BP-12,BP-30; S22.R02→BP-04,BP-09,BP-11,BP-12,BP-35; S22.R03→BP-01,BP-11,BP-12,BP-35 | T: S22.T01→BP-09,BP-11,BP-12,BP-35 | BP-11/BP-12 own dispatch and incident coordination; BP-04 represents agencies; BP-09 tracks police resources. |
| S23 | Police service governance and structure | R: S23.R01→BP-05,BP-06,BP-07,BP-08,BP-30,BP-31,BP-32,BP-33,BP-42; S23.R02→BP-01,BP-03,BP-05,BP-06; S23.R03→BP-05,BP-06,BP-07,BP-30,BP-31,BP-32,BP-33; S23.R04→BP-05,BP-06,BP-08,BP-10,BP-30,BP-35 | T: S23.T01→BP-05,BP-06,BP-08,BP-42 | BP-05 owns organisational architecture and authority distinctions; BP-06 individual personnel; BP-30 governance. |
| S24 | Police personnel and career simulation | R: S24.R01→BP-06,BP-07,BP-09,BP-32,BP-33; S24.R02→BP-06,BP-07,BP-08,BP-32,BP-33; S24.R03→BP-07,BP-08,BP-10,BP-32 | T: S24.T01→BP-06,BP-07,BP-08,BP-32 | BP-06 owns personnel record; BP-07 career rules; BP-08 assignment eligibility; BP-32 training qualification. |
| S25 | Police duty rosters, staffing and deployment | R: S25.R01→BP-06,BP-08,BP-09,BP-10,BP-11,BP-33,BP-37; S25.R02→BP-08,BP-09,BP-10,BP-11,BP-35,BP-37; S25.R03→BP-08,BP-33,BP-37,BP-38 | T: S25.T01→BP-08,BP-10,BP-11,BP-37 | BP-08 owns authoritative duty assignment; BP-33 owns leave/attendance employment records; actual attendance differs from planned roster. |
| S26 | Police command, policy and internal governance | R: S26.R01→BP-05,BP-08,BP-12,BP-30,BP-31,BP-41; S26.R02→BP-05,BP-08,BP-12,BP-30,BP-38; S26.R03→BP-30,BP-31,BP-38,BP-42 | T: S26.T01→BP-05,BP-30,BP-38 | BP-30 owns policy, command decisions and delegation; operational commands are consumed by BP-08/BP-12. |
| S27 | 911, call-taking, CAD and dispatch | R: S27.R01→BP-11,BP-12,BP-17,BP-35; S27.R02→BP-11,BP-12,BP-38,BP-42; S27.R03→BP-08,BP-09,BP-11,BP-12,BP-35 | T: S27.T01→BP-08,BP-11,BP-12,BP-35 | BP-11 owns intake/CAD/radio/dispatch; BP-12 owns incident record; original caller claims remain distinct from verified facts. |
| S28 | Patrol, response and field operations | R: S28.R01→BP-08,BP-10,BP-12,BP-22,BP-30; S28.R02→BP-08,BP-09,BP-10,BP-35,BP-37; S28.R03→BP-10,BP-12,BP-14,BP-35 | T: S28.T01→BP-08,BP-09,BP-10,BP-35 | BP-10 owns field/patrol activity; BP-08 owns deployment and eligibility; BP-35 enforces time, distance and resource constraints. |
| S29 | Incidents, crime taxonomy and occurrence generation | R: S29.R01→BP-02,BP-11,BP-12,BP-13,BP-14,BP-15,BP-17,BP-18; S29.R02→BP-02,BP-03,BP-04,BP-13,BP-14,BP-35,BP-36,BP-37; S29.R03→BP-12,BP-13,BP-15,BP-16,BP-18,BP-21,BP-27,BP-28 | T: S29.T01→BP-12,BP-13,BP-14,BP-35 | BP-13 owns taxonomy/classification; BP-14 occurrence generation; BP-12 incident/report lifecycle. |
| S30 | Case management and investigative command | R: S30.R01→BP-15,BP-16,BP-30,BP-38,BP-41; S30.R02→BP-15,BP-16,BP-21,BP-27,BP-28; S30.R03→BP-15,BP-16,BP-23,BP-38 | T: S30.T01→BP-15,BP-16,BP-38 | BP-15 owns case identity/lifecycle; BP-16 investigative action/decision; all state changes are attributable and historically preserved. |
| S31 | Victims, witnesses, suspects and persons of interest | R: S31.R01→BP-03,BP-15,BP-17,BP-18,BP-42; S31.R02→BP-13,BP-15,BP-17,BP-18,BP-27,BP-28; S31.R03→BP-03,BP-15,BP-17,BP-18,BP-35 | T: S31.T01→BP-03,BP-15,BP-17,BP-18 | BP-17 owns victim/witness case role; BP-18 suspect/offender status; BP-03 identity; no role or suspicion equals guilt. |
| S32 | Scene management and evidence collection | R: S32.R01→BP-09,BP-22,BP-23; S32.R02→BP-22,BP-23,BP-24; S32.R03→BP-19,BP-20,BP-21,BP-22,BP-23,BP-24,BP-38 | T: S32.T01→BP-22,BP-23,BP-24,BP-38 | BP-22 owns scene control/search; BP-23 exhibit lifecycle/continuity; BP-24 examination. |
| S33 | Forensics and specialist examination | R: S33.R01→BP-09,BP-23,BP-24; S33.R02→BP-16,BP-21,BP-23,BP-24; S33.R03→BP-09,BP-23,BP-24,BP-35 | T: S33.T01→BP-23,BP-24 | BP-24 owns forensic method/results/limitations; raw results, interpretation and investigative inference remain separate. |
| S34 | Interviews, interrogations and statements | R: S34.R01→BP-17,BP-18,BP-19,BP-27; S34.R02→BP-17,BP-19,BP-23,BP-38; S34.R03→BP-01,BP-16,BP-19,BP-42 | T: S34.T01→BP-17,BP-19,BP-38 | BP-19 owns interview process and source records; BP-17/BP-18 own participant case roles; no unsolicited solution prompts. |
| S35 | Intelligence, analysis and information handling | R: S35.R01→BP-16,BP-18,BP-21,BP-42; S35.R02→BP-16,BP-21,BP-23,BP-27; S35.R03→BP-21,BP-38,BP-42 | T: S35.T01→BP-16,BP-21,BP-38 | BP-21 owns intelligence lifecycle, confidence and dissemination; intelligence is not evidence or established fact. |
| S36 | Surveillance, observation and technical monitoring | R: S36.R01→BP-09,BP-20,BP-22,BP-35; S36.R02→BP-16,BP-20,BP-23,BP-38,BP-42; S36.R03→BP-20,BP-21,BP-23 | T: S36.T01→BP-20,BP-23,BP-38 | BP-20 owns surveillance sources/coverage/retrieval; BP-23 owns evidential continuity after collection. |
| S37 | Arrest, search, warrants and custody | R: S37.R01→BP-18,BP-25,BP-26,BP-27; S37.R02→BP-23,BP-25,BP-26,BP-38; S37.R03→BP-12,BP-25,BP-26,BP-27 | T: S37.T01→BP-25,BP-26,BP-27,BP-38 | BP-25 owns arrest/warrant/search authority and execution; BP-26 custody lifecycle; BP-23 seized-evidence continuity. |
| S38 | Prosecution, courts and legal outcomes | R: S38.R01→BP-15,BP-23,BP-27,BP-28; S38.R02→BP-18,BP-27,BP-28,BP-29; S38.R03→BP-15,BP-27,BP-28,BP-38 | T: S38.T01→BP-15,BP-27,BP-28,BP-38 | BP-27 owns prosecution/disclosure workflow; BP-28 courts/outcomes; historical investigative records are never rewritten by outcomes. |
| S39 | Corrections, rehabilitation and post-sentence status | R: S39.R01→BP-03,BP-18,BP-28,BP-29; S39.R02→BP-03,BP-26,BP-28,BP-29,BP-38 | T: S39.T01→BP-03,BP-28,BP-29,BP-38 | BP-29 owns sentence execution/supervision/release; BP-03 owns person lifecycle; BP-28 is source of sentence authority. |
| S40 | Complaints, oversight and public accountability | R: S40.R01→BP-30,BP-31,BP-41; S40.R02→BP-30,BP-31,BP-38,BP-42; S40.R03→BP-14,BP-30,BP-31,BP-35,BP-36,BP-41 | T: S40.T01→BP-30,BP-31,BP-38 | BP-31 owns complaint/misconduct case lifecycle; BP-30 institutional oversight; trust effects are causally generated, not arbitrary. |
| S41 | Time, calendar, schedules and simulation clock | R: S41.R01→BP-04,BP-07,BP-08,BP-11,BP-35,BP-37; S41.R02→BP-01,BP-35,BP-37; S41.R03→BP-35,BP-37,BP-38 | T: S41.T01→BP-35,BP-37,BP-38 | BP-37 owns canonical clock/calendar/schedules; BP-35 owns event execution and pause/resume semantics. |
| S42 | Simulation engine, causality and world activity | R: S42.R01→BP-03,BP-04,BP-14,BP-35,BP-36,BP-37; S42.R02→BP-03,BP-35,BP-38; S42.R03→BP-03,BP-04,BP-35,BP-37,BP-38,BP-43; S42.R04→BP-01,BP-35,BP-37 | T: S42.T01→BP-35,BP-38,BP-43 | BP-35 owns event/state processing and causality; domain divisions own domain rules; deterministic replay applies where specified. |
| S43 | AI generation, narrative and player agency | R: S43.R01→BP-01,BP-14,BP-16,BP-19,BP-35,BP-40; S43.R02→BP-01,BP-16,BP-21,BP-35,BP-42; S43.R03→BP-01,BP-16,BP-18,BP-21,BP-35,BP-42; S43.R04→BP-01,BP-16,BP-40; S43.R05→BP-35,BP-38,BP-42 | T: S43.T01→BP-01,BP-16,BP-18,BP-35,BP-42; S43.T02→BP-03,BP-16,BP-21,BP-35,BP-42 | BP-01 owns player-agency/hidden-truth invariants; BP-35 generation and event persistence; BP-42 information boundaries. Exact `bingo` trigger and no unsolicited investigative hints remain binding. |
| S44 | Text interface, commands and player workflow | R: S44.R01→BP-40; S44.R02→BP-01,BP-06,BP-07,BP-40; S44.R03→BP-38,BP-40; S44.R04→BP-40,BP-43 | T: S44.T01→BP-40,BP-43 | BP-40 owns the laptop-style text interface and complete text workflows; visual presentation is never required. |
| S45 | Maps, diagrams and visual evidence | R: S45.R01→BP-02,BP-12,BP-15,BP-16,BP-20,BP-22,BP-23,BP-24,BP-35,BP-40,BP-41; S45.R02→BP-02,BP-20,BP-22,BP-23,BP-24,BP-38; S45.R03→BP-01,BP-38,BP-40 | T: S45.T01→BP-02,BP-23,BP-24,BP-38 | BP-40 presents optional views; domain records remain authoritative; visuals must be traceable to canonical data. |
| S46 | Database, schemas and persistence | R: S46.R01→BP-38,BP-39,BP-40,BP-43,BP-44; S46.R02→BP-03,BP-04,BP-38,BP-43; S46.R03→BP-03,BP-15,BP-23,BP-38,BP-39; S46.R04→BP-35,BP-38,BP-39; S46.R05→BP-38,BP-43 | T: S46.T01→BP-03,BP-38,BP-43 | BP-38 owns schemas/constraints/transactions; BP-39 recovery; immutable source events and derived views remain distinct. |
| S47 | Storage efficiency and capacity governance | R: S47.R01→BP-38,BP-39,BP-43; S47.R02→BP-38,BP-39,BP-43; S47.R03→BP-38,BP-39,BP-43; S47.R04→BP-01,BP-38,BP-43,BP-44; S47.R05→BP-38,BP-39,BP-43,BP-44 | T: S47.T01→BP-01,BP-38,BP-43,BP-44; S47.T02→BP-38,BP-39,BP-43,BP-44 | BP-38 owns data/storage design; BP-43 benchmarks/tests; BP-44 governs approval/change. Mandatory measured baseline, estimate, explicit approval and post-write measurement are preserved. |
| S48 | Security, permissions and information boundaries | R: S48.R01→BP-05,BP-30,BP-38,BP-40,BP-42,BP-43; S48.R02→BP-01,BP-16,BP-17,BP-18,BP-19,BP-20,BP-21,BP-23,BP-42; S48.R03→BP-38,BP-42,BP-43,BP-44 | T: S48.T01→BP-38,BP-42 | BP-42 owns access/secret/hidden-information policy; domain divisions define their permissions; credentials never enter source or game records. |
| S49 | Backups, recovery and data integrity | R: S49.R01→BP-38,BP-39,BP-43; S49.R02→BP-01,BP-38,BP-39,BP-44; S49.R03→BP-38,BP-39 | T: S49.T01→BP-38,BP-39,BP-43 | BP-39 owns backup/restore and recovery objectives; BP-38 owns data integrity; restore evidence is mandatory. |
| S50 | Testing, validation and simulation quality | R: S50.R01→BP-38,BP-43; S50.R02→BP-03,BP-14,BP-35,BP-38,BP-43; S50.R03→BP-01,BP-38,BP-43,BP-44 | T: S50.T01→BP-01,BP-43,BP-44 | BP-43 owns test strategy and evidence; every division must have traceable acceptance tests, including edge, race, scale and continuity cases. |
| S51 | Operations, observability and maintenance | R: S51.R01→BP-09,BP-35,BP-38,BP-39,BP-40,BP-41,BP-43; S51.R02→BP-38,BP-39,BP-43,BP-44; S51.R03→BP-38,BP-39,BP-43,BP-44 | T: S51.T01→BP-35,BP-38,BP-39,BP-43 | Operational monitoring, safe maintenance, rollback and environment separation are explicit responsibilities, not optional implementation details. |
| S52 | Canon, versioning and change control | R: S52.R01→BP-01,BP-38,BP-44; S52.R02→BP-01,BP-44; S52.R03→BP-01,BP-38,BP-43,BP-44; S52.R04→BP-01,BP-38,BP-43,BP-44 | T: S52.T01→BP-01,BP-38,BP-43,BP-44 | BP-44 owns canon/version/change control; BP-01 owns governing rules; statuses remain distinct and evidence-linked. |

## 3. Cross-cutting requirements

| Source ID | Binding rule | Required target divisions |
|---|---|---|
| X01 | Stable identity and provenance across every domain; domain owners create records while shared registries enforce canonical identity. | BP-01,BP-03,BP-04,BP-05,BP-06,BP-12,BP-15,BP-23,BP-35,BP-38,BP-39,BP-44 |
| X02 | Single source of truth; no contradictory duplicate authority, including spatial, person, business, time, case, evidence and finance records. | BP-01,BP-02,BP-03,BP-04,BP-05,BP-12,BP-15,BP-23,BP-34,BP-35,BP-37,BP-38,BP-44 |
| X03 | All time-dependent facts are effective-dated and historically queryable; all domain divisions must comply with the shared clock contract. | BP-01,BP-02,BP-03,BP-04,BP-05,BP-08,BP-10,BP-11,BP-12,BP-15,BP-16,BP-19,BP-20,BP-22,BP-23,BP-25,BP-26,BP-27,BP-28,BP-29,BP-33,BP-35,BP-37,BP-38,BP-39,BP-43 |
| X04 | All financial, population, inventory, staffing, resource and capacity changes reconcile atomically. | BP-03,BP-04,BP-06,BP-08,BP-09,BP-11,BP-12,BP-26,BP-29,BP-33,BP-34,BP-35,BP-38,BP-43 |
| X05 | Distinguish fact, allegation, estimate, inference, intelligence, opinion, source statement, analytical conclusion and adjudicated finding. | BP-01,BP-12,BP-13,BP-15,BP-16,BP-17,BP-18,BP-19,BP-20,BP-21,BP-22,BP-23,BP-24,BP-27,BP-28,BP-31,BP-38,BP-42 |
| X06 | Preserve originals; derived summaries never replace source records; corrections are additive, attributed and historically traceable. | BP-01,BP-12,BP-15,BP-16,BP-19,BP-20,BP-21,BP-22,BP-23,BP-24,BP-27,BP-28,BP-31,BP-38,BP-39,BP-43 |
| X07 | No hidden simulation time while player is out; pause/resume and deliberate time advancement are explicit. | BP-01,BP-35,BP-37,BP-38,BP-39,BP-40,BP-43 |
| X08 | Text-first operation; optional maps/graphics cannot be required and cannot contradict authoritative text/records. | BP-01,BP-02,BP-20,BP-22,BP-23,BP-24,BP-38,BP-40,BP-43 |
| X09 | Police receives deepest simulation; supporting city systems remain operationally coherent, proportionate and causally connected. | BP-01,BP-02,BP-03,BP-04,BP-05,BP-09,BP-11,BP-12,BP-14,BP-35,BP-36,BP-44 |
| X10 | No design/implementation/test/verification status is asserted without the corresponding approval, artefact, passing test and reproducible evidence. | BP-01,BP-38,BP-39,BP-43,BP-44 |



## 3A. Source-wide material beyond division req[] and tests[]

The first crosswalk's 168 requirement and 60 test IDs covered the division arrays only. This section closes the remaining source-level traceability gap. Source JSON remains unchanged; pointers below are exact.

### Canon and authority fields

| Source ID | Exact source field / content | Target ownership |
|---|---|---|
| C01 | `/canon/setting`: fictional sovereign city-state Saltwater; one city/jurisdiction | BP-01 owns canon; BP-02 owns spatial/jurisdiction implementation; BP-44 controls amendments |
| C02 | `/canon/world`: no external playable city/territory; off-map references only | BP-01,BP-02,BP-44 |
| C03 | `/canon/population/initial`: 9,000 residents + 500 police = 9,500 | BP-01 owns binding baseline; BP-03 owns authoritative count; BP-06 owns police subset |
| C04 | `/canon/population/reserve`: 500 headroom, not extra population | BP-01,BP-03 |
| C05 | `/canon/population/hard_cap`: 10,000 living people maximum | BP-01,BP-03,BP-38,BP-43 |
| C06 | `/canon/population/counting` and `/canon/population/rule`: count every qualifying living person once; atomic entries/exits/deaths; never exceed cap | BP-01,BP-03,BP-35,BP-38,BP-43 |
| C07 | `/canon/police/approx_strength` and `/scope`: approx. 500 individually persistent police; police is within population cap | BP-01,BP-05,BP-06,BP-08,BP-30 |
| C08 | `/canon/interface`: permanent text-first; detailed narrative/records/dialogue/evidence/chronology; visuals optional | BP-01,BP-40,BP-43 |
| C09 | `/canon/priority`: canon/player agency → fidelity → continuity/integrity → minimum lossless storage → performance | BP-01,BP-38,BP-43,BP-44 |

### Governing principles

| Source ID | Source pointer | Destination |
|---|---|---|
| P01 | `/principles/0`: requirements binding after blueprint approval | BP-01,BP-44 |
| P02 | `/principles/1`: coherent high-functioning city; no decorative placeholders where operation affects play | BP-01,BP-04,BP-35,BP-43 |
| P03 | `/principles/2`: police deepest; other systems support/create/constrain/respond without equal depth | BP-01,BP-04,BP-05,BP-35,BP-44 |
| P04 | `/principles/3`: preserve detail; compress structure, never meaning | BP-01,BP-38,BP-43 |
| P05 | `/principles/4`: stable unique IDs, lifecycle, provenance and explicit relationships | BP-01,BP-03,BP-04,BP-38 |
| P06 | `/principles/5`: reconcile time, population, money, stock, capacity, authority and location | BP-01,BP-02,BP-03,BP-04,BP-05,BP-34,BP-35,BP-37,BP-38,BP-43 |
| P07 | `/principles/6`: generated facts obey canon, causality, schedules, geography, resources and prior records | BP-01,BP-02,BP-14,BP-35,BP-37,BP-43 |
| P08 | `/principles/7`: player actions authoritative; no auto-solving or hidden-truth disclosure | BP-01,BP-16,BP-35,BP-40,BP-42 |
| P09 | `/principles/8`: no simulation time while player is out | BP-01,BP-35,BP-37,BP-43 |
| P10 | `/principles/9`: no completion without implementation and test evidence | BP-01,BP-38,BP-43,BP-44 |

### Governance metadata and delivery rules

| Source ID | Source pointer / value | Destination |
|---|---|---|
| M01 | `/authority`: proposed permanent specification; approval required; amendments versioned | BP-01,BP-44 |
| M02 | `/status`: source document is `DRAFT_FOR_USER_REVIEW`; not automatically approved by adoption of the 44-division structure | BP-01,BP-44 |
| M03 | `/dependency_order`: `01-02,03-05,06-10,11-22,23-28,29-40,41-45,46-49,50-52` | BP-01,BP-35,BP-43,BP-44; retain as source-order dependency evidence, then reconcile to BP-01–BP-44 sequencing |
| M04 | `/completion_states`: NOT_STARTED, DESIGNED, IMPLEMENTED, TESTED, VERIFIED, BLOCKED, RETIRED | BP-01,BP-38,BP-43,BP-44 |
| M05 | `/completion_rule`: VERIFIED requires implementation, passing acceptance tests, reconciled dependencies and linked GitHub evidence; documentation alone is insufficient | BP-01,BP-38,BP-43,BP-44 |
| M06 | `/change_control`: user owns canon/final approval; no structural or material reinterpretation without explicit approval; versioned traceability | BP-01,BP-44 |
| M07 | `/out_of_scope/0..5`: second playable city; equal-depth non-police simulation; graphics prerequisite; unbounded population; unapproved Neon writes; invented completion status | BP-01,BP-02,BP-03,BP-04,BP-38,BP-40,BP-43,BP-44 |
| M08 | `/traceability`: every requirement stable ID; implementation, test, schema object and evidence link to it | BP-01,BP-38,BP-43,BP-44 |
| M09 | `/v`, `/project`, `/kind`: source version 1, project Saltwater, master-blueprint type | BP-01,BP-44 |

**Dependency-order resolution:** The source's 52-division sequence is historical source metadata, not a replacement for the adopted BP-01–BP-44 structure. Its dependency intent must be translated into explicit target-to-target dependencies during each full division specification. It must not be used to renumber or reorder the 44 divisions.


## 4. Coverage controls and audit checklist

- [ ] All 52 source divisions are present exactly once in Section 2.
- [ ] Every `req[]` item in the source JSON has one stable `Snn.Rnn` ID and at least one BP destination.
- [ ] Every `tests[]` item in the source JSON has one stable `Snn.Tnn` ID and at least one BP destination.
- [x] All 10 cross-cutting rules X01–X10 are mapped with expanded destination coverage.\n- [x] Canon C01–C09, principles P01–P10 and governance metadata M01–M09 are explicitly traced.
- [ ] Original source wording and array order remain unchanged in the source JSON.
- [ ] All mappings are incorporated into the target division specifications; no mapping is treated as completed merely because it appears here.
- [ ] Each multi-target requirement has a primary owner, explicit interfaces and no competing source of truth; verify this during BP-specific design.
- [ ] No target division has silently absorbed an incompatible requirement; conflicts are logged and resolved explicitly.
- [ ] The fixed BP-01–BP-44 structure and Saltwater canon remain unchanged.
- [ ] No Neon write has been made or authorised.

## 5. Target development sequence

After this crosswalk passes its audit, develop BP-01 through BP-44 in the fixed order. Each division must be a complete specification, not a summary. Minimum specification contract:

1. Purpose, outcomes, scope, exclusions and governing principles.
2. Complete functional requirements, with source IDs retained.
3. Entities, attributes, types, constraints, identifiers and relationships.
4. Lifecycle, states, transitions, triggers, actors and permitted operations.
5. Business rules, invariants, formulas, limits and reconciliation rules.
6. Inputs, outputs, events, commands, reports and user-visible behaviour.
7. Dependencies, interfaces, ownership and cross-division contracts.
8. Roles, authority, permissions, confidentiality and information boundaries.
9. Normal, exceptional, invalid, adversarial, failure and recovery paths.
10. Time, scheduling, concurrency, causality and historical/effective dating.
11. Persistence, provenance, audit, retention, performance and storage design.
12. NPC/AI behaviour, knowledge boundaries and player-agency constraints where relevant.
13. UI/text workflows and optional visual outputs where relevant.
14. Acceptance criteria with positive, negative, boundary, integration, replay, load and regression tests.
15. Traceability from each requirement to implementation artefact, test and reproducible evidence.
16. Open decisions, assumptions, risks and unresolved conflicts—never silently guessed.

**Completion rule:** A division is design-complete only when every applicable item above is specified and all source requirements/tests are allocated. It is implemented, tested or verified only with corresponding code/schema and reproducible evidence. A document alone cannot establish those states.

## 6. Known design constraints to carry through all 44 divisions

- One sovereign city-state and one city only; external references are off-map context, never expansion.
- Maximum 10,000 living people in total, including police; initial target 9,000 residents + 500 police, with 500 headroom.
- At least 10,000 distinct, coherent businesses.
- Police is the deepest simulation; supporting city systems must still be operationally credible and causally connected.
- Text is the complete primary interface; maps/graphics are optional.
- No simulation time passes while the player is absent.
- Every person/entity has stable identity, lifecycle, relationships and provenance.
- Relevant persons promoted to persistent full detail are never downgraded.
- Preserve player agency and hidden truth. Never reveal a perpetrator/accomplice/culprit until the exact player input `bingo`; never volunteer solution hints or next-investigation instructions.
- Compress storage representation, never detail or meaning. No Neon write without a measured baseline, credible incremental estimate, explicit approval and post-write measurement.
- The user retains final authority over canon and design amendments.

## 7. Semantic audit findings and resolutions

| Audit ID | Finding in v1.0 | Resolution in v1.1 | Remaining control |
|---|---|---|---|
| A01 | Source-level canon, principles, authority, completion states, exclusions, dependency order and traceability were not explicitly mapped. | Added C01–C09, P01–P10 and M01–M09. | Confirm each is incorporated in BP-01 and relevant owner divisions. |
| A02 | Person life records and property/tenancy links omitted business and finance ownership interfaces. | Expanded S04.R01 and S06.R01 destinations. | BP-03/BP-04/BP-33/BP-34 define authoritative fields and effective-dated links. |
| A03 | Trade/logistics lacked explicit geographic routing dependency. | Added BP-02 to S09.R02. | BP-02 owns network; BP-04/BP-09/BP-34 own their domain records. |
| A04 | Police structure and career mapping underrepresented training, professional standards and HR. | Expanded S23.R01 and S23.R03 to BP-07/BP-31/BP-32/BP-33. | BP-05 owns structure; BP-06 personnel; BP-07 career; BP-31 standards; BP-32 training; BP-33 HR. |
| A05 | Rostering omitted police resource availability. | Added BP-09 to S25.R01. | BP-08 owns deployment assignment; BP-09 resource readiness; BP-33 attendance. |
| A06 | Crime taxonomy/generation lacked explicit geography, dispatch and victim/suspect ownership. | Expanded S29.R01/R02/R03. | BP-13 owns taxonomy; BP-14 generation; BP-02 geography; BP-11 reporting/dispatch; BP-17/BP-18 case roles. |
| A07 | Evidence collection's supported evidence types lacked interview, surveillance and intelligence source interfaces. | Expanded S32.R01/R03 and mapped BP-19/BP-20/BP-21. | BP-23 owns exhibit continuity; source divisions retain original records. |
| A08 | Time rules omitted business opening-hour ownership. | Added BP-04 to S41.R01. | BP-37 owns clock; BP-04 owns business schedules; all domains consume canonical time. |
| A09 | Visuals/timelines omitted case, incident, engine and reporting interfaces. | Expanded S45.R01. | BP-40 presents views; domain data remains authoritative. |
| A10 | Database architecture requirement omitted ChatGPT interface and connectivity/quality verification. | Expanded S46.R01. | BP-38 owns data; BP-39 persistence; BP-40 interface; BP-43 tests; BP-44 source/version governance. |
| A11 | Security roles and secret protection omitted player-facing enforcement and test coverage. | Expanded S48.R01–R03. | BP-42 owns policy; domain owners enforce; BP-40 applies presentation boundary; BP-43 verifies. |
| A12 | Operations/observability lacked operator-facing visibility. | Added BP-40 to S51.R01. | BP-41 reports/alerts; BP-40 displays; BP-43 tests. |
| A13 | Some broad cross-cutting mappings were too narrow to ensure universal application. | Expanded X01–X10 destinations. | Each BP specification must state which global invariants it implements and how. |
| A14 | S14 education/research mapping did not clearly assign individual non-police learner enrolment, attendance and education history; BP-32 scope was police training. | Added BP-03 for person-level education participation/history; clarified BP-04 provider-level programmes/capacity/facilities; constrained BP-32 to police training/credentials; retained BP-07/BP-33/BP-37 ownership. | BP-03/BP-04/BP-32 specifications, S14.R01/S14.T01 mapping and acceptance tests must preserve this boundary. |

**Audit conclusion:** v1.1 resolves identified omissions in traceability and clarifies ownership interfaces without changing BP-01–BP-44. This is a documentary semantic audit, not proof that the full target specifications are complete. Requirements with multi-domain destinations remain subject to division-level interface and acceptance-test design. No Neon changes are authorised.

## 8. Division-by-division semantic audit register

Each source division was reviewed against its complete requirement and test text, its mapped BP destinations, and the target ownership boundaries. “Reviewed” means no further mapping change was identified in this pass; it does not mean target design or implementation is complete.

| Source | Domain | Audit result | Ownership / resolution |
|---|---|---|---|
| S01 | Sovereignty | Revised | Clarified canon/jurisdiction, authority and change ownership. |
| S02 | Geography | Reviewed | BP-02 owns canonical spatial IDs; operational divisions consume them. |
| S03 | Population accounting | Reviewed | BP-03 owns unique-person ledger and atomic capacity; BP-06 is a subset. |
| S04 | Person identity | Revised | Added BP-04 for business/employer relationships; BP-03 remains identity owner. |
| S05 | Households/relationships | Reviewed | BP-36 owns relationship semantics; BP-03 owns person identity. |
| S06 | Housing/property/tenancy | Revised | Added BP-34 for rent/payment records; BP-04 owns tenancy and occupancy. |
| S07 | Businesses/economy | Reviewed | BP-04 owns business registry; other divisions consume stable business references. |
| S08 | Employment/labour | Reviewed | BP-33 owns employment; BP-04, BP-06/BP-07 and BP-34 own business/police/finance interfaces. |
| S09 | Markets/trade/logistics | Revised | Added BP-02 to route/logistics mapping; off-map dependencies remain non-playable. |
| S10 | Public finance | Reviewed | BP-34 owns accounting and transaction reconciliation. |
| S11 | Government/public administration | Reviewed | BP-30 owns public institutions and authority; BP-04 represents entities; BP-31/BP-34 handle oversight/procurement. |
| S12 | Civil registry/public records | Reviewed | BP-38 owns record standards; source-domain owners retain authoritative facts. |
| S13 | Healthcare/public health | Reviewed | BP-04 represents providers; BP-17/BP-24/BP-26/BP-42 own police/medical interfaces and access. |
| S14 | Education/training/research | Revised | BP-03 owns person-level education participation/history; BP-04 provider/facility/capacity; BP-32 police training; BP-07 career gates; BP-33 staff; BP-37 schedules. |
| S15 | Social care/welfare | Reviewed | BP-04 represents services; BP-17 and BP-30 own victim-support and public-service interfaces. |
| S16 | Utilities/infrastructure | Reviewed | BP-04 owns operators/assets; BP-35 propagates outages; BP-09/BP-12 consume effects. |
| S17 | Roads/transport/mobility | Reviewed | BP-02 owns topology; BP-04 transport actors; BP-10/BP-11/BP-12 consume routes. |
| S18 | Buildings/facilities/assets | Reviewed | BP-04 owns buildings/access points; BP-20/BP-22/BP-23 consume access and scene facts. |
| S19 | Environment/weather/hazards | Reviewed | BP-35 owns event causality; BP-02 supplies spatial context; domain divisions consume effects. |
| S20 | Food/essential services | Reviewed | BP-04 represents suppliers; BP-09/BP-34/BP-35 own police dependencies, finance and disruption. |
| S21 | Culture/media/recreation | Reviewed | BP-04 owns organisations/venues; BP-35/BP-36/BP-37 own event/social/time effects. |
| S22 | Emergency services/civil protection | Reviewed | BP-04 represents agencies; BP-11/BP-12 coordinate dispatch/incident handoffs; BP-09 tracks police resources. |
| S23 | Police governance/structure | Revised | Added BP-07/BP-31/BP-32/BP-33 for career, standards, training and HR ownership. |
| S24 | Police personnel/career | Reviewed | BP-06 personnel, BP-07 career, BP-08 deployment eligibility, BP-32 qualifications. |
| S25 | Police rosters/staffing | Revised | Added BP-09 resource readiness; BP-08 remains assignment owner and BP-33 attendance owner. |
| S26 | Police command/policy | Reviewed | BP-30 owns policy/command decisions; BP-31 owns standards/discipline; operations consume orders. |
| S27 | 911/CAD/dispatch | Reviewed | BP-11 owns intake/CAD/radio/dispatch; BP-12 owns incident; claims remain distinct from facts. |
| S28 | Patrol/field operations | Reviewed | BP-10 owns patrol actions; BP-08 deployment; BP-35 time/distance/resource constraints. |
| S29 | Incident/crime taxonomy/generation | Revised | Added geography, dispatch and victim/suspect ownership; clarified classification vs generation. |
| S30 | Case management/investigative command | Reviewed | BP-15 owns case lifecycle; BP-16 actions/decisions; chronology remains immutable. |
| S31 | Victims/witnesses/suspects | Reviewed | BP-17/BP-18 own distinct case roles; BP-03 identity; suspicion is not guilt. |
| S32 | Scene/evidence collection | Revised | Added BP-09 resources and BP-19/BP-20/BP-21 source interfaces for testimonial, surveillance and intelligence material. |
| S33 | Forensics/specialist examination | Reviewed | BP-24 owns methods/results/limitations; raw result, interpretation and inference remain separate. |
| S34 | Interviews/statements | Reviewed | BP-19 owns interview process/source records; BP-27 procedural interface; no solution leakage. |
| S35 | Intelligence/analysis | Reviewed | BP-21 owns source grading/confidence/dissemination; intelligence is not evidence. |
| S36 | Surveillance/monitoring | Reviewed | BP-20 owns collection/coverage/retrieval; BP-23 owns evidential continuity. |
| S37 | Arrest/search/warrants/custody | Reviewed | BP-25 owns arrest/warrant/search; BP-26 custody; BP-23 seized-evidence continuity. |
| S38 | Prosecution/courts/outcomes | Reviewed | BP-27 prosecution/disclosure; BP-28 courts; BP-29 sentence execution; history is preserved. |
| S39 | Corrections/post-sentence | Reviewed | BP-29 owns sentence/supervision/release; BP-28 sentence authority; BP-03 person lifecycle. |
| S40 | Complaints/oversight | Reviewed | BP-31 owns complaint/misconduct lifecycle; BP-30 institutional oversight; BP-41 reporting. |
| S41 | Time/calendar/schedules | Revised | Added BP-04 business opening hours; BP-37 clock ownership and BP-35 execution remain distinct. |
| S42 | Simulation engine/causality | Revised | Added BP-38 integrity constraints to impossible-state/state-mutation mapping. |
| S43 | AI generation/player agency | Reviewed | BP-01 owns agency/reveal invariants; BP-35 generation; BP-42 information boundaries. |
| S44 | Text interface/workflow | Reviewed | BP-40 owns complete text workflows; BP-43 verifies essential actions. |
| S45 | Maps/diagrams/visual evidence | Revised | Added BP-12/BP-15/BP-16/BP-35/BP-41 for incident/case/investigation timelines and reporting. |
| S46 | Database/schemas/persistence | Revised | Added BP-40 interface and BP-43 connectivity/quality tests; BP-38/BP-39 remain data/persistence owners. |
| S47 | Storage/capacity governance | Reviewed | BP-38 data/storage; BP-43 benchmarks; BP-44 change approval; no write without user approval. |
| S48 | Security/permissions | Revised | Added BP-40 presentation enforcement, BP-43 tests and source-domain permission interfaces. |
| S49 | Backups/recovery/integrity | Reviewed | BP-39 recovery owner; BP-38 data integrity; BP-43 restore evidence. |
| S50 | Testing/validation/quality | Reviewed | BP-43 owns test strategy/evidence; every division supplies traceable acceptance criteria. |
| S51 | Operations/observability | Revised | Added BP-40 operator-facing visibility; BP-41 alerts/reports; BP-43 tests. |
| S52 | Canon/version/change control | Reviewed | BP-44 owns controlled amendments; BP-01 global rules; status/evidence remain distinct. |

**Coverage result:** 52/52 source divisions reviewed; 168/168 requirement IDs mapped; 60/60 test IDs mapped; 10/10 principles, 10/10 cross-cutting rules, 9/9 canon elements and 9/9 governance metadata groups mapped; all 44 target divisions referenced. The crosswalk is semantically audited at the design-mapping level. Each division specification must still resolve field-level ownership, event contracts, exceptions and tests before design completion.
