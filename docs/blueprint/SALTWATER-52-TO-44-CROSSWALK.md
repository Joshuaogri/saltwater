# Saltwater 52→44 Requirement Crosswalk

**Version:** 1.0  
**Date:** 2026-11-22  
**Source:** `docs/governance/SALTWATER_MASTER_BLUEPRINT.json` (52 divisions; unchanged)  
**Target:** `docs/blueprint/SALTWATER-MASTER-BLUEPRINT.md` (BP-01–BP-44; fixed structure)  
**Purpose:** Lossless traceability from every source requirement and test to its destination specification.  
**Status:** Crosswalk baseline; detailed BP specifications and verification evidence are still pending.

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
| S04 | Person identity and life records | R: S04.R01→BP-03,BP-33,BP-36,BP-37; S04.R02→BP-03,BP-35,BP-38; S04.R03→BP-03,BP-15,BP-16,BP-17,BP-18,BP-35 | T: S04.T01→BP-03,BP-38; S04.T02→BP-03,BP-35,BP-38 | BP-03 owns person identity/lifecycle; domain records hold specialised attributes; relevance promotion is permanent and cannot erase history. |
| S05 | Households, relationships and social networks | R: S05.R01→BP-03,BP-36; S05.R02→BP-03,BP-36,BP-37,BP-38; S05.R03→BP-14,BP-17,BP-18,BP-21,BP-35,BP-36 | T: S05.T01→BP-03,BP-36,BP-38 | BP-36 owns relationship semantics; BP-03 owns identity and lifecycle; case roles remain distinct from guilt or proof. |
| S06 | Housing, property and tenancy | R: S06.R01→BP-04; S06.R02→BP-04,BP-33,BP-38; S06.R03→BP-04,BP-20,BP-22,BP-35,BP-37 | T: S06.T01→BP-04,BP-35,BP-37 | BP-04 owns property, ownership, occupancy and access rights; time-valid occupancy/access is shared with BP-20/BP-22 evidence timelines. |
| S07 | Businesses and commercial economy | R: S07.R01→BP-04,BP-38; S07.R02→BP-04,BP-09,BP-34,BP-35,BP-36; S07.R03→BP-04,BP-10,BP-11,BP-12,BP-15,BP-16,BP-21; S07.R04→BP-04,BP-35,BP-43 | T: S07.T01→BP-04,BP-38; S07.T02→BP-04,BP-33,BP-35 | BP-04 owns the business registry and minimum 10,000 businesses; finance, staffing, premises and police consumers reference business IDs. |
| S08 | Employment, labour and professional life | R: S08.R01→BP-04,BP-06,BP-07,BP-33,BP-34; S08.R02→BP-03,BP-04,BP-35,BP-36,BP-37; S08.R03→BP-04,BP-06,BP-33 | T: S08.T01→BP-03,BP-04,BP-33,BP-35,BP-37 | BP-33 owns general employment lifecycle; BP-06/BP-07 own police-specific employment and career rules. |
| S09 | Markets, trade, supply chains and logistics | R: S09.R01→BP-02,BP-04,BP-09,BP-34; S09.R02→BP-04,BP-09,BP-34,BP-35; S09.R03→BP-01,BP-02,BP-04,BP-34 | T: S09.T01→BP-04,BP-09,BP-34,BP-35 | BP-04 owns commercial actors; BP-09 police logistics/resources; BP-34 accounting/procurement; off-map dependencies do not create playable territory. |
| S10 | Public finance, taxation and economic accounts | R: S10.R01→BP-30,BP-33,BP-34; S10.R02→BP-03,BP-04,BP-34; S10.R03→BP-34,BP-38,BP-43 | T: S10.T01→BP-34,BP-38,BP-43 | BP-34 owns accounting model, transaction rules and public/police budgets; all posted amounts must reconcile. |
| S11 | Government and public administration | R: S11.R01→BP-01,BP-30,BP-42; S11.R02→BP-04,BP-30,BP-31,BP-34; S11.R03→BP-30,BP-38,BP-42 | T: S11.T01→BP-30,BP-38,BP-42 | BP-30 owns public institutional structure and decision authority; BP-04 represents operational bodies and premises. |
| S12 | Civil registry and public records | R: S12.R01→BP-03,BP-04,BP-30,BP-38; S12.R02→BP-38,BP-42,BP-44; S12.R03→BP-16,BP-27,BP-38,BP-42 | T: S12.T01→BP-38,BP-42,BP-44 | BP-38 owns authoritative record/version/provenance rules; domain owners remain responsible for their source records. |
| S13 | Healthcare and public health | R: S13.R01→BP-04,BP-09,BP-12,BP-17,BP-26,BP-35; S13.R02→BP-03,BP-12,BP-17,BP-22,BP-23,BP-24,BP-28; S13.R03→BP-38,BP-42 | T: S13.T01→BP-04,BP-09,BP-12,BP-35 | BP-04 represents providers and facilities; BP-12/BP-17/BP-24 handle operational interfaces; BP-42 controls restricted access. Healthcare remains proportionate, not a second deep simulation. |
| S14 | Education, training and research | R: S14.R01→BP-04,BP-07,BP-32,BP-33,BP-37; S14.R02→BP-07,BP-09,BP-32; S14.R03→BP-03,BP-07,BP-32,BP-33,BP-38 | T: S14.T01→BP-07,BP-32,BP-38 | BP-04 represents providers; BP-32 owns general training/qualifications; BP-07 owns police career gates. |
| S15 | Social care, welfare and community support | R: S15.R01→BP-04,BP-17,BP-30,BP-36; S15.R02→BP-04,BP-17,BP-30,BP-38; S15.R03→BP-03,BP-14,BP-17,BP-18,BP-35,BP-36 | T: S15.T01→BP-04,BP-17,BP-30,BP-38 | BP-04 represents services/providers; BP-17 owns victim/witness support interfaces; BP-30 owns public-service governance. |
| S16 | Utilities, energy and communications infrastructure | R: S16.R01→BP-04,BP-09,BP-35; S16.R02→BP-04,BP-09,BP-10,BP-11,BP-12,BP-35; S16.R03→BP-04,BP-09,BP-12,BP-41 | T: S16.T01→BP-04,BP-09,BP-35 | BP-04 owns infrastructure assets/operators; BP-09 owns police resource dependencies; BP-35 propagates geographically bounded outage/restoration effects. |
| S17 | Roads, transport and mobility | R: S17.R01→BP-02,BP-04,BP-09,BP-10,BP-11; S17.R02→BP-03,BP-09,BP-10,BP-11,BP-12,BP-35,BP-37; S17.R03→BP-10,BP-11,BP-12,BP-16,BP-20,BP-22 | T: S17.T01→BP-02,BP-10,BP-11,BP-35 | BP-02 owns road geometry; BP-04 owns transport operators/facilities; BP-10/BP-11 consume routes and travel constraints. |
| S18 | Buildings, facilities and physical assets | R: S18.R01→BP-02,BP-04,BP-09,BP-22; S18.R02→BP-04,BP-09,BP-20,BP-22,BP-23; S18.R03→BP-20,BP-22,BP-23,BP-35,BP-37 | T: S18.T01→BP-04,BP-20,BP-22,BP-35 | BP-04 owns building/facility topology and access points; BP-20/BP-22 consume time-valid access facts. |
| S19 | Environment, weather and natural hazards | R: S19.R01→BP-02,BP-04,BP-09,BP-35,BP-37; S19.R02→BP-02,BP-09,BP-10,BP-12,BP-17,BP-20,BP-22,BP-24,BP-35; S19.R03→BP-35,BP-37,BP-38 | T: S19.T01→BP-02,BP-35,BP-37 | BP-35 owns environmental event effects and chronology; BP-02 provides geographic context. |
| S20 | Food systems and essential services | R: S20.R01→BP-04,BP-09,BP-34; S20.R02→BP-04,BP-09,BP-12,BP-35; S20.R03→BP-04,BP-09,BP-34,BP-35 | T: S20.T01→BP-04,BP-09,BP-34,BP-35 | BP-04 represents providers and supply actors; BP-09 handles police dependencies; BP-35 coordinates disruption/recovery. |
| S21 | Culture, media, recreation and civic life | R: S21.R01→BP-04,BP-30,BP-36; S21.R02→BP-04,BP-14,BP-17,BP-21,BP-35,BP-36,BP-37,BP-41; S21.R03→BP-04,BP-30,BP-36 | T: S21.T01→BP-04,BP-35,BP-36,BP-37 | BP-04 owns organisations/venues; BP-36 social context; BP-35/BP-37 event scheduling and causal effects. |
| S22 | Emergency services and civil protection | R: S22.R01→BP-04,BP-09,BP-11,BP-12,BP-30; S22.R02→BP-04,BP-09,BP-11,BP-12,BP-35; S22.R03→BP-01,BP-11,BP-12,BP-35 | T: S22.T01→BP-09,BP-11,BP-12,BP-35 | BP-11/BP-12 own dispatch and incident coordination; BP-04 represents agencies; BP-09 tracks police resources. |
| S23 | Police service governance and structure | R: S23.R01→BP-05,BP-06,BP-08,BP-30,BP-42; S23.R02→BP-01,BP-03,BP-05,BP-06; S23.R03→BP-05,BP-06,BP-07,BP-30,BP-31,BP-33; S23.R04→BP-05,BP-06,BP-08,BP-10,BP-30,BP-35 | T: S23.T01→BP-05,BP-06,BP-08,BP-42 | BP-05 owns organisational architecture and authority distinctions; BP-06 individual personnel; BP-30 governance. |
| S24 | Police personnel and career simulation | R: S24.R01→BP-06,BP-07,BP-09,BP-32,BP-33; S24.R02→BP-06,BP-07,BP-08,BP-32,BP-33; S24.R03→BP-07,BP-08,BP-10,BP-32 | T: S24.T01→BP-06,BP-07,BP-08,BP-32 | BP-06 owns personnel record; BP-07 career rules; BP-08 assignment eligibility; BP-32 training qualification. |
| S25 | Police duty rosters, staffing and deployment | R: S25.R01→BP-06,BP-08,BP-10,BP-11,BP-33,BP-37; S25.R02→BP-08,BP-09,BP-10,BP-11,BP-35,BP-37; S25.R03→BP-08,BP-33,BP-37,BP-38 | T: S25.T01→BP-08,BP-10,BP-11,BP-37 | BP-08 owns authoritative duty assignment; BP-33 owns leave/attendance employment records; actual attendance differs from planned roster. |
| S26 | Police command, policy and internal governance | R: S26.R01→BP-05,BP-08,BP-12,BP-30,BP-31,BP-41; S26.R02→BP-05,BP-08,BP-12,BP-30,BP-38; S26.R03→BP-30,BP-31,BP-38,BP-42 | T: S26.T01→BP-05,BP-30,BP-38 | BP-30 owns policy, command decisions and delegation; operational commands are consumed by BP-08/BP-12. |
| S27 | 911, call-taking, CAD and dispatch | R: S27.R01→BP-11,BP-12,BP-17,BP-35; S27.R02→BP-11,BP-12,BP-38,BP-42; S27.R03→BP-08,BP-09,BP-11,BP-12,BP-35 | T: S27.T01→BP-08,BP-11,BP-12,BP-35 | BP-11 owns intake/CAD/radio/dispatch; BP-12 owns incident record; original caller claims remain distinct from verified facts. |
| S28 | Patrol, response and field operations | R: S28.R01→BP-08,BP-10,BP-12,BP-22,BP-30; S28.R02→BP-08,BP-09,BP-10,BP-35,BP-37; S28.R03→BP-10,BP-12,BP-14,BP-35 | T: S28.T01→BP-08,BP-09,BP-10,BP-35 | BP-10 owns field/patrol activity; BP-08 owns deployment and eligibility; BP-35 enforces time, distance and resource constraints. |
| S29 | Incidents, crime taxonomy and occurrence generation | R: S29.R01→BP-12,BP-13,BP-14,BP-15; S29.R02→BP-03,BP-04,BP-13,BP-14,BP-35,BP-36; S29.R03→BP-12,BP-13,BP-15,BP-16,BP-21,BP-27,BP-28 | T: S29.T01→BP-12,BP-13,BP-14,BP-35 | BP-13 owns taxonomy/classification; BP-14 occurrence generation; BP-12 incident/report lifecycle. |
| S30 | Case management and investigative command | R: S30.R01→BP-15,BP-16,BP-30,BP-38,BP-41; S30.R02→BP-15,BP-16,BP-21,BP-27,BP-28; S30.R03→BP-15,BP-16,BP-23,BP-38 | T: S30.T01→BP-15,BP-16,BP-38 | BP-15 owns case identity/lifecycle; BP-16 investigative action/decision; all state changes are attributable and historically preserved. |
| S31 | Victims, witnesses, suspects and persons of interest | R: S31.R01→BP-03,BP-15,BP-17,BP-18,BP-42; S31.R02→BP-13,BP-15,BP-17,BP-18,BP-27,BP-28; S31.R03→BP-03,BP-15,BP-17,BP-18,BP-35 | T: S31.T01→BP-03,BP-15,BP-17,BP-18 | BP-17 owns victim/witness case role; BP-18 suspect/offender status; BP-03 identity; no role or suspicion equals guilt. |
| S32 | Scene management and evidence collection | R: S32.R01→BP-22,BP-23; S32.R02→BP-22,BP-23,BP-24; S32.R03→BP-22,BP-23,BP-24,BP-38 | T: S32.T01→BP-22,BP-23,BP-24,BP-38 | BP-22 owns scene control/search; BP-23 exhibit lifecycle/continuity; BP-24 examination. |
| S33 | Forensics and specialist examination | R: S33.R01→BP-09,BP-23,BP-24; S33.R02→BP-16,BP-21,BP-23,BP-24; S33.R03→BP-09,BP-23,BP-24,BP-35 | T: S33.T01→BP-23,BP-24 | BP-24 owns forensic method/results/limitations; raw results, interpretation and investigative inference remain separate. |
| S34 | Interviews, interrogations and statements | R: S34.R01→BP-17,BP-18,BP-19,BP-27; S34.R02→BP-17,BP-19,BP-23,BP-38; S34.R03→BP-01,BP-16,BP-19,BP-42 | T: S34.T01→BP-17,BP-19,BP-38 | BP-19 owns interview process and source records; BP-17/BP-18 own participant case roles; no unsolicited solution prompts. |
| S35 | Intelligence, analysis and information handling | R: S35.R01→BP-16,BP-18,BP-21,BP-42; S35.R02→BP-16,BP-21,BP-23,BP-27; S35.R03→BP-21,BP-38,BP-42 | T: S35.T01→BP-16,BP-21,BP-38 | BP-21 owns intelligence lifecycle, confidence and dissemination; intelligence is not evidence or established fact. |
| S36 | Surveillance, observation and technical monitoring | R: S36.R01→BP-09,BP-20,BP-22,BP-35; S36.R02→BP-16,BP-20,BP-23,BP-38,BP-42; S36.R03→BP-20,BP-21,BP-23 | T: S36.T01→BP-20,BP-23,BP-38 | BP-20 owns surveillance sources/coverage/retrieval; BP-23 owns evidential continuity after collection. |
| S37 | Arrest, search, warrants and custody | R: S37.R01→BP-18,BP-25,BP-26,BP-27; S37.R02→BP-23,BP-25,BP-26,BP-38; S37.R03→BP-12,BP-25,BP-26,BP-27 | T: S37.T01→BP-25,BP-26,BP-27,BP-38 | BP-25 owns arrest/warrant/search authority and execution; BP-26 custody lifecycle; BP-23 seized-evidence continuity. |
| S38 | Prosecution, courts and legal outcomes | R: S38.R01→BP-15,BP-23,BP-27,BP-28; S38.R02→BP-18,BP-27,BP-28,BP-29; S38.R03→BP-15,BP-27,BP-28,BP-38 | T: S38.T01→BP-15,BP-27,BP-28,BP-38 | BP-27 owns prosecution/disclosure workflow; BP-28 courts/outcomes; historical investigative records are never rewritten by outcomes. |
| S39 | Corrections, rehabilitation and post-sentence status | R: S39.R01→BP-03,BP-18,BP-28,BP-29; S39.R02→BP-03,BP-26,BP-28,BP-29,BP-38 | T: S39.T01→BP-03,BP-28,BP-29,BP-38 | BP-29 owns sentence execution/supervision/release; BP-03 owns person lifecycle; BP-28 is source of sentence authority. |
| S40 | Complaints, oversight and public accountability | R: S40.R01→BP-30,BP-31,BP-41; S40.R02→BP-30,BP-31,BP-38,BP-42; S40.R03→BP-14,BP-30,BP-31,BP-35,BP-36,BP-41 | T: S40.T01→BP-30,BP-31,BP-38 | BP-31 owns complaint/misconduct case lifecycle; BP-30 institutional oversight; trust effects are causally generated, not arbitrary. |
| S41 | Time, calendar, schedules and simulation clock | R: S41.R01→BP-07,BP-08,BP-11,BP-35,BP-37; S41.R02→BP-01,BP-35,BP-37; S41.R03→BP-35,BP-37,BP-38 | T: S41.T01→BP-35,BP-37,BP-38 | BP-37 owns canonical clock/calendar/schedules; BP-35 owns event execution and pause/resume semantics. |
| S42 | Simulation engine, causality and world activity | R: S42.R01→BP-03,BP-04,BP-14,BP-35,BP-36,BP-37; S42.R02→BP-03,BP-35,BP-38; S42.R03→BP-03,BP-04,BP-35,BP-37,BP-43; S42.R04→BP-01,BP-35,BP-37 | T: S42.T01→BP-35,BP-38,BP-43 | BP-35 owns event/state processing and causality; domain divisions own domain rules; deterministic replay applies where specified. |
| S43 | AI generation, narrative and player agency | R: S43.R01→BP-01,BP-14,BP-16,BP-19,BP-35,BP-40; S43.R02→BP-01,BP-16,BP-21,BP-35,BP-42; S43.R03→BP-01,BP-16,BP-18,BP-21,BP-35,BP-42; S43.R04→BP-01,BP-16,BP-40; S43.R05→BP-35,BP-38,BP-42 | T: S43.T01→BP-01,BP-16,BP-18,BP-35,BP-42; S43.T02→BP-03,BP-16,BP-21,BP-35,BP-42 | BP-01 owns player-agency/hidden-truth invariants; BP-35 generation and event persistence; BP-42 information boundaries. Exact `bingo` trigger and no unsolicited investigative hints remain binding. |
| S44 | Text interface, commands and player workflow | R: S44.R01→BP-40; S44.R02→BP-01,BP-06,BP-07,BP-40; S44.R03→BP-38,BP-40; S44.R04→BP-40,BP-43 | T: S44.T01→BP-40,BP-43 | BP-40 owns the laptop-style text interface and complete text workflows; visual presentation is never required. |
| S45 | Maps, diagrams and visual evidence | R: S45.R01→BP-02,BP-20,BP-22,BP-23,BP-24,BP-40; S45.R02→BP-02,BP-20,BP-22,BP-23,BP-24,BP-38; S45.R03→BP-01,BP-38,BP-40 | T: S45.T01→BP-02,BP-23,BP-24,BP-38 | BP-40 presents optional views; domain records remain authoritative; visuals must be traceable to canonical data. |
| S46 | Database, schemas and persistence | R: S46.R01→BP-38,BP-39,BP-44; S46.R02→BP-03,BP-04,BP-38,BP-43; S46.R03→BP-03,BP-15,BP-23,BP-38,BP-39; S46.R04→BP-35,BP-38,BP-39; S46.R05→BP-38,BP-43 | T: S46.T01→BP-03,BP-38,BP-43 | BP-38 owns schemas/constraints/transactions; BP-39 recovery; immutable source events and derived views remain distinct. |
| S47 | Storage efficiency and capacity governance | R: S47.R01→BP-38,BP-39,BP-43; S47.R02→BP-38,BP-39,BP-43; S47.R03→BP-38,BP-39,BP-43; S47.R04→BP-01,BP-38,BP-43,BP-44; S47.R05→BP-38,BP-39,BP-43,BP-44 | T: S47.T01→BP-01,BP-38,BP-43,BP-44; S47.T02→BP-38,BP-39,BP-43,BP-44 | BP-38 owns data/storage design; BP-43 benchmarks/tests; BP-44 governs approval/change. Mandatory measured baseline, estimate, explicit approval and post-write measurement are preserved. |
| S48 | Security, permissions and information boundaries | R: S48.R01→BP-05,BP-30,BP-38,BP-42; S48.R02→BP-01,BP-16,BP-18,BP-21,BP-42; S48.R03→BP-38,BP-42,BP-44 | T: S48.T01→BP-38,BP-42 | BP-42 owns access/secret/hidden-information policy; domain divisions define their permissions; credentials never enter source or game records. |
| S49 | Backups, recovery and data integrity | R: S49.R01→BP-38,BP-39,BP-43; S49.R02→BP-01,BP-38,BP-39,BP-44; S49.R03→BP-38,BP-39 | T: S49.T01→BP-38,BP-39,BP-43 | BP-39 owns backup/restore and recovery objectives; BP-38 owns data integrity; restore evidence is mandatory. |
| S50 | Testing, validation and simulation quality | R: S50.R01→BP-38,BP-43; S50.R02→BP-03,BP-14,BP-35,BP-38,BP-43; S50.R03→BP-01,BP-38,BP-43,BP-44 | T: S50.T01→BP-01,BP-43,BP-44 | BP-43 owns test strategy and evidence; every division must have traceable acceptance tests, including edge, race, scale and continuity cases. |
| S51 | Operations, observability and maintenance | R: S51.R01→BP-09,BP-35,BP-38,BP-39,BP-41,BP-43; S51.R02→BP-38,BP-39,BP-43,BP-44; S51.R03→BP-38,BP-39,BP-43,BP-44 | T: S51.T01→BP-35,BP-38,BP-39,BP-43 | Operational monitoring, safe maintenance, rollback and environment separation are explicit responsibilities, not optional implementation details. |
| S52 | Canon, versioning and change control | R: S52.R01→BP-01,BP-38,BP-44; S52.R02→BP-01,BP-44; S52.R03→BP-01,BP-38,BP-43,BP-44; S52.R04→BP-01,BP-38,BP-43,BP-44 | T: S52.T01→BP-01,BP-38,BP-43,BP-44 | BP-44 owns canon/version/change control; BP-01 owns governing rules; statuses remain distinct and evidence-linked. |

## 3. Cross-cutting requirements

| Source ID | Binding rule | Required target divisions |
|---|---|---|
| X01 | Stable identity and provenance across every domain. | BP-03,BP-38 |
| X02 | Single source of truth; no contradictory duplicate authority. | BP-01,BP-03,BP-04,BP-35,BP-38,BP-44 |
| X03 | All time-dependent facts are effective-dated and historically queryable. | BP-35,BP-37,BP-38,BP-39 |
| X04 | All financial, population, inventory, staffing and capacity changes reconcile. | BP-03,BP-04,BP-08,BP-09,BP-33,BP-34,BP-35,BP-38 |
| X05 | Distinguish fact, allegation, estimate, inference, intelligence and opinion. | BP-12,BP-13,BP-15,BP-16,BP-18,BP-19,BP-21,BP-23,BP-24,BP-27,BP-28 |
| X06 | Preserve originals; derived summaries never replace source records. | BP-19,BP-20,BP-21,BP-23,BP-24,BP-38,BP-39 |
| X07 | No hidden simulation time while player is out. | BP-01,BP-35,BP-37,BP-43 |
| X08 | Text-first operation; optional visuals cannot be required. | BP-01,BP-40,BP-43 |
| X09 | Police receives deepest simulation; all other domains remain operationally coherent and connected. | BP-01,BP-04,BP-05,BP-35,BP-44 |
| X10 | No implementation marked complete without reproducible evidence. | BP-01,BP-38,BP-43,BP-44 |

## 4. Coverage controls and audit checklist

- [ ] All 52 source divisions are present exactly once in Section 2.
- [ ] Every `req[]` item in the source JSON has one stable `Snn.Rnn` ID and at least one BP destination.
- [ ] Every `tests[]` item in the source JSON has one stable `Snn.Tnn` ID and at least one BP destination.
- [ ] All 10 cross-cutting rules X01–X10 are mapped.
- [ ] Original source wording and array order remain unchanged in the source JSON.
- [ ] All mappings are incorporated into the target division specifications; no mapping is treated as completed merely because it appears here.
- [ ] Each multi-target requirement has a primary owner, explicit interfaces and no competing source of truth.
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
