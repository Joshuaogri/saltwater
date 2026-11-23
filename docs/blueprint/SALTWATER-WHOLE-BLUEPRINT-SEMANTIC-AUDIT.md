# Saltwater — Whole-Blueprint Semantic Audit

**Project:** Saltwater  
**Scope:** Original 52-division source, 52→44 crosswalk, fixed 44-division master blueprint, all 44 division specifications and the specification register.  
**Audit state:** IN_PROGRESS — source mapping and document-structure pass completed; requirement-to-specification semantic reconciliation remains open.  
**Authority:** The user retains final authority over canon and all material design changes.  
**Database boundary:** GitHub documentation only. No Neon read, write, migration, seed, import, upload or database operation was performed for this audit.

## 1. Audit objective

Verify that every requirement and acceptance test in the preserved 52-division source is not merely mapped to a BP division, but is fully and correctly expressed in the actual target specification(s). Identify semantic omissions, weakened wording, contradictory rules, duplicated or missing ownership, ambiguous interfaces, unsupported assumptions, missing exceptions and acceptance tests that do not prove the source intent.

The audit must preserve the fixed BP-01–BP-44 structure. It must not silently change canon, approve open policy decisions, or treat a specification draft as implemented, tested or verified.

## 2. Authoritative inputs inspected

1. `docs/governance/SALTWATER_MASTER_BLUEPRINT.json` — preserved 52-division source and governing canon.
2. `docs/blueprint/SALTWATER-52-TO-44-CROSSWALK.md` — source-to-target requirement/test mapping and prior mapping-level semantic audit.
3. `docs/blueprint/SALTWATER-MASTER-BLUEPRINT.md` — fixed 44-division structure and specification contract.
4. `docs/blueprint/DIVISION-SPECIFICATION-REGISTER.md` — design, implementation, test and verification status.
5. All 44 files in `docs/blueprint/divisions/BP-01-...` through `BP-44-...`.

## 3. Source and crosswalk integrity — passed

The preserved source contains:
- 52 source divisions;
- 168 source requirements;
- 60 source acceptance tests;
- 228 total requirement/test identifiers.

The crosswalk contains mappings for all 228 source identifiers. No source requirement or test ID was found unmapped. All 44 target divisions are represented in the fixed master structure and crosswalk.

This establishes source-ID allocation and structural traceability only. It does **not** prove that every mapped target specification contains the full semantic intent, correct ownership, interface behaviour, exceptions or adequate acceptance evidence.

The existing crosswalk v1.2 records a prior mapping-level review of 52/52 source divisions and findings A01–A13. Its own conclusion explicitly distinguishes that documentary mapping audit from completion of the 44 target specifications. This audit therefore reopens the target-specification layer without discarding the prior crosswalk findings or source history.

## 4. Binding canon checked

The source canon was inspected and its population arithmetic is internally consistent:
- opening population: 9,000 residents + 500 police = 9,500 living persons;
- additional 500 is capacity headroom, not a second population;
- hard maximum: 10,000 living persons, counting every person exactly once across roles.

The audit retains the other binding Saltwater rules: one sovereign city-state and one playable city; no territorial expansion; at least 10,000 businesses; police as the deepest simulation; text-first permanent primary interface; no simulation-time advancement while the player is absent; permanent full-detail promotion of materially relevant persons; preserved player agency; exact `bingo` reveal gate; lossless meaning/provenance; and no Neon writes without explicit, informed approval after storage measurement.

No canon change was made.

## 5. Target-document structure — passed after corrections

All 44 division specification files exist. Their numbered top-level sections were checked for sequential numbering and duplicate section numbers.

Five documents contained heading-number defects. These were corrected in GitHub without changing domain meaning or the fixed division structure:

| Division | Correction | Result |
|---|---|---|
| BP-15 Case Management | Removed two empty placeholder headings that duplicated the later full acceptance-test and edge-case sections. | 35 sequential sections |
| BP-23 Evidence Management | Renumbered the appended acceptance, traceability, open-decision and completion sections. | 32 sequential sections |
| BP-24 Forensics | Renumbered the appended acceptance, traceability, open-decision and completion sections. | 37 sequential sections |
| BP-25 Arrests and Warrants | Renumbered the appended acceptance, traceability, open-decision and completion sections. | 38 sequential sections |
| BP-26 Custody Management | Renumbered the appended acceptance, traceability, open-decision and completion sections. | 38 sequential sections |

Post-change fetch verification confirmed sequential numbering and no duplicate section numbers in all five corrected files. The remaining 39 files were also checked and had sequential numbered top-level sections at the time of audit.

### Correction commits

- BP-15: `1825bc4a7b6d1114479e7220d627ed4dec306a41`
- BP-23: `70fa9f9eaac80922fefae514ca280edf38ccbda0`
- BP-24: `ef53d1c162e86d4e68cd7b2d27282dac4d0b28bc`
- BP-25: `85dbba0193e991651f10b781cdce98b2498fea4f`
- BP-26: `9228a41c517f4d1d62dbfcdb8dec090197a46581`

## 6. Semantic reconciliation — in progress

For every source requirement and test, the audit must check each mapped target division against the actual specification text, not merely the crosswalk row. The review must verify:

1. Full meaning retained; no narrowing, weakening or omission.
2. Correct domain owner and explicit producer/consumer interface.
3. No duplicate or competing authoritative source of truth.
4. Required entities, fields, identifiers, relationships and lifecycle states.
5. Inputs, outputs, events, transaction boundaries and failure behaviour.
6. Permissions, confidentiality, provenance and information boundaries.
7. Time, pause, population, geography and business-count invariants where applicable.
8. Edge cases, exceptions, uncertainty and correction/recovery paths.
9. Acceptance tests that prove the original source requirement, including negative and boundary cases.
10. Consistency with other mapped divisions and the fixed master blueprint.

A source item is not marked semantically covered merely because its ID appears in a specification or because the specification lists the source division by name. Coverage requires a meaningful target obligation and a testable contract.

### Known reconciliation controls

- BP-06 uses grouped source-domain references and defers exact requirement/test pointers to the crosswalk; verify each mapped obligation against its personnel and lifecycle sections.
- BP-07 explicitly states that mapped source requirements/tests must be semantically reconciled before approval. This remains a required audit task, not a completed status.
- BP-08 likewise states that detailed source IDs remain in the crosswalk and require semantic reconciliation before approval.
- BP-01 uses source-ID ranges and global obligation summaries; confirm that global charter responsibilities are not mistaken for ownership of domain implementation.
- For every other BP division, inspect the exact mapped IDs in the crosswalk and verify the corresponding content and tests in that specification.

These are audit controls, not findings that the relevant requirements are necessarily absent. No semantic omission is declared resolved without examining its actual destination content.

### Initial canon and ownership scan: BP-01–BP-08

The first targeted scan of BP-01–BP-08 was performed against their mapped source domains and the binding source canon. This is a preliminary content scan, not the final item-by-item semantic sign-off.

| Division | Initial scan | Matters requiring resolution before design approval |
|---|---|---|
| BP-01 | Global canon and authority model are consistent with the source population arithmetic, one-city boundary, business minimum, police depth, text-first interface and pause rule. | Confirm that all cross-cutting obligations remain represented in domain specifications and that authority boundaries are consistent across BP-27/BP-30/BP-42/BP-44. |
| BP-02 | Single bounded jurisdiction, off-map-only external references, canonical spatial IDs, geometry/topology and text fallback are specified. | Exact boundary, coordinate system, districts, roads, addressing and natural geography remain intentionally open canon decisions. |
| BP-03 | Opening 9,000 residents + 500 police = 9,500 total; 500 headroom; 10,000 hard cap; one-person-one-ID; atomic capacity and permanent promotion are explicit. | Countability of visitors/commuters/temporary persons and whether opening identities are seeded individually or generated from aggregate targets remain open. |
| BP-04 | At least 10,000 distinct businesses, separate person-count accounting, property/tenancy/occupancy, access, time validity and employer/provider interfaces are specified. | Whether the 10,000-business floor means total registered or active businesses, sector distribution and initial property/building counts remain open. |
| BP-05 | Police remains the deepest institution; approximately 500 personnel are included in the population cap; rank/position/grade/authority/powers/clearance/qualification/appointment/assignment are distinct. | Final organisation chart, command titles, unit structure, staffing allocation and authority matrix remain open. |
| BP-06 | Personnel records link to canonical BP-03 identities; service history, categories, appointments, qualifications, supervision, personnel documents and lifecycle are represented. | Personnel category taxonomy, service-number format, applicant lifecycle and restricted personnel-record policy remain open. |
| BP-07 | Career lifecycle includes recruit/probation, progression, acting/secondment, service calculation, mandatory retirement by years of service and Chief tenure exception. | Rank ladder, promotion thresholds, probation duration, service-credit edge cases and appeal policy remain open; the 35-year service rule and Chief exception are not to be weakened. |
| BP-08 | Unit catalogue, establishment, command, membership, deployment, geographic responsibility, readiness and resource interfaces are specified. | Final unit structure, staffing allocations, beat model, readiness formula and deployment arbitration remain open. |

**Preliminary result:** no contradiction with the inspected binding Saltwater canon was identified in this first scan. This does not certify complete semantic coverage: each source requirement/test must still be checked against every mapped target division and its acceptance criteria.

### Initial source-domain scan: S09–S16

| Source | Initial ownership/content check | Audit outcome |
|---|---|---|
| S09 Markets, trade, supply chains and logistics | BP-02 spatial network; BP-04 businesses, warehouses and providers; BP-09 police logistics; BP-34 procurement/finance; BP-35 causal disruption and delivery events. | Ownership split appears coherent; verify stock/order/delivery reconciliation across sender, carrier and receiver in mapped tests. |
| S10 Public finance, taxation and economic accounts | BP-34 owns accounting, currency, budgets, revenue, debt, grants and household/business finance; BP-38 records/transactions; BP-43 tests balance. | No immediate ownership gap found in initial scan; fictional currency/accounting policies remain open. |
| S11 Government and public administration | BP-30 owns institutions, offices, authority and decisions; BP-04 organisation identity; BP-31 oversight; BP-34 procurement; BP-38 records; BP-42 access. | Ownership split appears coherent; verify permit/licence/inspection workflows and official-action authority tests. |
| S12 Civil registry and public records | BP-03 person/civil identity; BP-04 property/business; BP-30 permits and public institutions; BP-38 record/version/provenance; BP-42 access; BP-44 change governance. | Source ownership is distributed by record domain; verify no missing issuing/registry workflow or competing authority in detailed review. |
| S13 Healthcare and public health | Provider operations lacked explicit appointment/treatment/public-health-alert metadata. | Finding A15 resolved in BP-03/BP-04 and crosswalk v1.3; test execution pending. |
| S14 Education, training and research | General learner enrolment/attendance was not clearly assigned; BP-32 is police-training focused. | Finding A14 resolved in BP-03/BP-04/BP-32 and crosswalk v1.3; test execution pending. |
| S15 Social care, welfare and community support | BP-04 provider identities/capacity; BP-17 safeguarding/referrals; BP-30 public-service governance; BP-36 social context; BP-38 records. | Ownership split appears coherent at support-level depth; verify referral lifecycle, eligibility/capacity and outcome contracts. |
| S16 Utilities, energy and communications infrastructure | BP-04 operators/assets; BP-09 police resource dependencies; BP-35 outage propagation/restoration; BP-12 incident effects; BP-41 service notices. | Ownership split appears coherent; verify network-connected impact, outage scope and explicit restoration tests. |

This is an initial ownership/content scan only. The mapped target sections and acceptance tests for every source item still require detailed reconciliation.

### Semantic finding A14 — education-provider and learner-record ownership

<badge color="success">Resolved in draft specifications and crosswalk v1.3</badge>

**Source:** S14.R01 and S14.T01.

**Gap:** The source requires schools, colleges and training providers, enrolment, attendance, staff, qualifications, schedules and facilities. BP-32's actual scope is the police training/professional-development system, while BP-04 originally limited itself to provider identity and service profile and BP-03 only referenced education/qualification facts. The original mapping did not explicitly assign individual non-police learner enrolment and attendance history.

**Resolution within the existing 44 divisions:**
- **BP-03:** owns person-level school/college/vocational education participation, enrolment state, attendance/participation history, completion/withdrawal and qualification references. Six acceptance criteria AC-EDU-01–06 were added.
- **BP-04:** owns school/college/provider identity, programmes offered, term/session schedule references, enrolment capacity/availability, staff-role references, qualification-issuer profile and facilities. Individual learner records remain BP-03-owned.
- **BP-32:** remains authoritative for police training and police-training credentials; general school/college learner records are explicitly excluded. Boundary test TRN-AT-161 was added; its acceptance-test ID sequence now contains 161 unique IDs.
- **BP-07:** retains police career/qualification gate decisions; **BP-33** owns education-provider staff employment; **BP-37** owns canonical time/schedules; **BP-38** owns physical schema and constraints.

**Crosswalk v1.3:** S14.R01 now maps to BP-03/BP-04/BP-07/BP-32/BP-33/BP-37; S14.T01 maps to BP-03/BP-04/BP-07/BP-32/BP-38. The S14 division audit status changed from Reviewed to Revised. The original 52-division source wording was not changed.

**Verification:** BP-03 person education records, six new acceptance criteria and traceability; BP-04 provider-level education facts, event types and traceability; BP-32 general-education boundary and TRN-AT-161; and both S14 crosswalk rows were fetched after commit and checked. This resolves the identified ownership gap at specification level; tests have not been executed.

### Semantic finding A15 — proportionate healthcare service records

<badge color="success">Resolved in draft specifications and crosswalk v1.3</badge>

**Source:** S13.R01, S13.R02 and S13.T01.

**Gap:** The provider representation described facilities, broad capacity and referrals, but did not explicitly define healthcare appointment, treatment-encounter and public-health-alert event metadata. The source requires these service facts while explicitly avoiding a separate deep healthcare simulator.

**Resolution within existing divisions:**
- **BP-04:** now owns proportionate healthcare provider/service capability, practitioner/service roles, emergency-care capacity, appointment/referral availability, treatment-encounter metadata, public-health alert references and service disruption/restoration.
- **BP-03:** now explicitly owns proportionate person-level injury, death and care-access references, without duplicating clinical charts or making medical/forensic findings.
- **BP-17/BP-26:** retain victim/witness and custody-specific care/support workflows.
- **BP-23/BP-24:** retain exhibit continuity and forensic examination/interpretation.
- **BP-35:** coordinates time-valid capacity, alerts and disruption effects; **BP-42** controls sensitive access.

BP-04 acceptance criterion AC-D06 and BP-03 criteria AC-HLTH-01–04 were added. Crosswalk audit finding A15 and the S13 division review status were updated. No new division or deep healthcare simulator was introduced.

**Verification:** Updated BP-03/BP-04 specifications and crosswalk were fetched after commit. Test execution remains pending.

### Initial source-domain scan: S17–S24

| Source | Initial ownership/content check | Audit outcome |
|---|---|---|
| S17 Roads, transport and mobility | BP-02 topology, stops, parking and accessibility; BP-04 operators, routes and fleet profiles; BP-37 timetables; BP-09 police fleet; BP-10/BP-11/BP-12 operational consumers. | Finding A16 resolved the previously implicit service-route/stop/timetable ownership. Test execution pending. |
| S18 Buildings, facilities and physical assets | BP-02 spatial identity; BP-04 premises/building/facility and access structure; BP-09 police assets; BP-20 surveillance; BP-22 scene geometry; BP-23 exhibits. | Ownership split appears coherent; verify key/lock/alarm and authorised-access timelines against scene and surveillance records. |
| S19 Environment, weather and natural hazards | BP-02 geography; BP-35 environmental causality/effects; BP-37 canonical time; BP-09/BP-10/BP-12/BP-17/BP-20/BP-22/BP-24 consume justified impacts. | Ownership split appears coherent; verify effects are location/time-valid and do not invent evidence or health consequences. |
| S20 Food systems and essential services | BP-04 suppliers/operators/stock; BP-09 police dependencies; BP-34 financial/procurement; BP-35 supply-chain causality and recovery. | Ownership split appears proportionate; verify stock/delivery/shortage reconciliation and no conjured supply. |
| S21 Culture, media, recreation and civic life | BP-04 organisations/venues/media; BP-30 public authority; BP-36 community/social context; BP-35 generation; BP-37 schedules; BP-41 public notices/reports. | Ownership split appears coherent at support-level depth; verify events have organiser, place, time and grounded attendance. |
| S22 Emergency services and civil protection | BP-04 agency identity/facilities; BP-09 police resource interfaces; BP-11 dispatch coordination; BP-12 incident command; BP-30 institutional authority; BP-35 causal coordination. | Ownership split appears proportionate; verify other-agency capability and handoffs without creating a second deep simulation or displacing police depth. |
| S23 Police service governance and structure | BP-05 institutional architecture; BP-06 personnel; BP-07 career; BP-08 units; BP-30 governance; BP-31 standards; BP-32 training; BP-33 HR; BP-42 permissions. | Ownership split appears coherent; verify rank/position/grade/authority/powers/clearance/qualification/appointment/assignment remain distinct across interfaces. |
| S24 Police personnel and career simulation | BP-06 personnel; BP-07 career; BP-08 deployment; BP-09 resources; BP-32 qualifications; BP-33 HR. | Ownership split appears coherent; verify personnel identity, employment, career, competence, welfare, pay and discipline are linked without duplicate master records. |

This is an initial ownership/content scan only. All mapped source requirements/tests still require exact target-section and acceptance-test reconciliation.

### Initial source-domain scan: S25–S32

| Source | Initial ownership/content check | Audit outcome |
|---|---|---|
| S25 Police duty rosters, staffing and deployment | BP-06 personnel; BP-08 unit membership/assignment/coverage; BP-09 resource readiness; BP-10 patrol; BP-11 dispatch availability; BP-33 employment/attendance; BP-37 scheduling. | Ownership split appears coherent; verify minimum staffing, actual attendance and incompatible-duty tests across the roster/dispatch/patrol interfaces. |
| S26 Police command, policy and internal governance | BP-05 institutional authority; BP-08 unit command; BP-12 operational command; BP-30 governance/policy; BP-31 standards; BP-38 decision provenance; BP-41 notifications/reports. | Ownership split appears coherent; verify every material instruction has authoriser, issuer, recipient, execution status and audit trail. |
| S27 911, call-taking, CAD and dispatch | BP-11 call-taking/CAD/radio/dispatch; BP-12 incident; BP-17 caller/participant role; BP-08 deployment; BP-09 readiness; BP-35 event execution; BP-38 originals; BP-42 access. | BP-11 scope is aligned with source; verify concurrent workload, original recordings, claim/fact separation and dispatch chronology. |
| S28 Patrol, response and field operations | BP-08 deployment; BP-10 patrol/field actions; BP-12 incident; BP-22 scenes; BP-30 authority; BP-09 equipment; BP-35/BP-37 time and causality. | Ownership split appears coherent; verify location, resource, authority and task commitments are rechecked at execution. |
| S29 Incidents, crime taxonomy and occurrence generation | BP-13 taxonomy; BP-14 hidden occurrence truth/generation; BP-11 reporting/dispatch; BP-12 incident lifecycle; BP-15 case; BP-17/BP-18 roles; BP-21 intelligence. | Ownership split appears coherent; verify occurrence, report, allegation, intelligence, offence and proven finding remain separate. |
| S30 Case management and investigative command | BP-15 case identity/lifecycle; BP-16 investigative work; BP-21 intelligence; BP-27/BP-28 legal; BP-30 governance; BP-38 records; BP-41 reporting. | Ownership split appears coherent; verify concurrent/cold/linked/reopened cases and immutable chronology/decision provenance. |
| S31 Victims, witnesses, suspects and persons of interest | BP-03 identity/promotion; BP-15 case links; BP-17 victim/witness; BP-18 suspect/offender; BP-42 information security; BP-35 promotion events. | Ownership split appears coherent; verify roles are independent, suspicion is not guilt and relevant-person promotion is permanent. |
| S32 Scene management and evidence collection | BP-22 scene boundaries/search/observations; BP-23 exhibits/custody; BP-24 forensics; BP-19 interviews; BP-20 surveillance; BP-21 intelligence; BP-38 records; BP-09 resources. | Ownership split appears coherent; verify testimonial/digital/documentary/biological/trace material can enter evidence workflow without source-record or chain-of-custody loss. |

This is an initial ownership/content scan only. Detailed mapped-source acceptance-test reconciliation remains open.

### Initial source-domain scan: S33–S40

| Source | Initial ownership/content check | Audit outcome |
|---|---|---|
| S33 Forensics and specialist examination | BP-09 specialist resources; BP-23 exhibits/submissions; BP-24 methods/results/limitations/quality/interpretation; BP-16 investigative inference; BP-21 intelligence; BP-35 causal scheduling/turnaround. | Ownership split appears coherent; verify each conclusion identifies method, source material, limitations and examiner, and that turnaround uses simulation time. |
| S34 Interviews, interrogations and statements | BP-17/BP-18 participant roles; BP-19 interview lifecycle/recordings/statements; BP-27 procedural/legal interface; BP-23 evidential continuity; BP-38 originals/provenance; BP-42 access. | Ownership split appears coherent; verify verbatim/source content, statement versions, cautions and hidden-truth/no-leading-prompt safeguards. |
| S35 Intelligence, analysis and information handling | BP-21 source grading/confidence/products/dissemination; BP-16 investigative use; BP-18 suspect links; BP-23 evidence boundary; BP-27 legal; BP-38 provenance; BP-42 restrictions. | Ownership split appears coherent; verify intelligence remains distinct from evidence and established fact, with source provenance and uncertainty retained. |
| S36 Surveillance, observation and technical monitoring | BP-20 methods/coverage/authorisation/collection/time drift/retrieval; BP-22 scenes; BP-23 evidence continuity; BP-35 time; BP-38 records; BP-42 access; BP-09 resources. | Ownership split appears coherent; verify coverage limits, blind spots and source-device/time basis accompany every item and absence of coverage is not treated as proof of absence. |
| S37 Arrest, search, warrants and custody | BP-25 grounds/warrants/search/seizure; BP-26 custody/booking/welfare/release; BP-23 property/evidence; BP-27 legal process; BP-37 canonical clock; BP-38 records. | Finding A17 resolved the missing canonical-clock mapping. Verify custody/warrant events satisfy configured rules and pause/chronology constraints. |
| S38 Prosecution, courts and legal outcomes | BP-27 charging/prosecution/defence/disclosure; BP-28 adjudication/verdict/sentence/appeal; BP-29 sentence execution; BP-15 case links; BP-23 evidence versions; BP-38 records. | Ownership split appears coherent; verify legal statuses never auto-convert and court outcomes do not rewrite investigative history. |
| S39 Corrections, rehabilitation and post-sentence status | BP-29 sentence execution/supervision/release/recall; BP-28 sentence authority; BP-26 police custody; BP-03 person continuity; BP-38 records. | Ownership split appears coherent; verify sentence and release dates reconcile to court orders and person records. |
| S40 Complaints, oversight and public accountability | BP-30 institutional oversight; BP-31 complaint/standards investigation; BP-41 public reporting; BP-35 event causality; BP-36 public trust/social context; BP-38 records; BP-42 access. | Ownership split appears coherent; verify each complaint has route/owner/status/outcome and due-process/conflict safeguards. |

This is an initial ownership/content scan only. Detailed source-item and acceptance-test reconciliation remains open.

### Semantic finding A17 — canonical custody clock mapping

<badge color="success">Resolved in BP-26, BP-37 and crosswalk v1.3</badge>

**Source:** S37.R02 and S37.T01.

**Gap:** BP-26 correctly stated that BP-37 is the sole canonical clock, but the source-to-target mapping for the custody clock/property-continuity requirement did not include BP-37. This left the canonical clock and custody-specific elapsed-time/review responsibilities implicit in traceability.

**Resolution:** BP-26's S37.R02 traceability now explicitly states that BP-37 supplies canonical time while BP-26 owns custody-specific elapsed-time calculation, review decisions and personal property in custody; BP-23 owns exhibit continuity. BP-37 now traces S37.R02 and S37.T01 for canonical time and scheduled custody-review/deadline occurrences. Crosswalk S37.R02 and S37.T01 now include BP-37 and audit finding A17 records the boundary.

**Verification:** BP-26, BP-37 and crosswalk were fetched after commit. Test execution remains pending.

### Initial source-domain scan: S41–S52

| Source | Initial ownership/content check | Audit outcome |
|---|---|---|
| S41 Time, calendar, schedules and simulation clock | BP-37 owns canonical clock/calendar/timezones/schedule catalogue; BP-35 executes; BP-01 owns no-offline-time canon; BP-38 preserves event history. | Ownership split appears coherent; verify one clock basis, deterministic ordering and complete freeze/resume semantics. |
| S42 Simulation engine, causality and world activity | BP-35 orchestration; BP-03/BP-04 domain state; BP-14 occurrence generation; BP-36 social context; BP-37 time; BP-38 integrity; BP-43 tests. | Ownership split appears coherent; verify deterministic event/replay boundaries, no impossible states and relevance processing without loss of persistence. |
| S43 AI generation, narrative and player agency | BP-01 global agency/reveal rules; BP-14 hidden occurrence truth; BP-16 investigative agency; BP-18 offender roles; BP-19 interviews; BP-21 intelligence; BP-35 generation; BP-40 presentation; BP-42 access. | Exact `bingo` reveal gate and no-hint rule are present in core specifications; verify adversarial leakage through every output channel. |
| S44 Text interface, commands and player workflow | BP-40 laptop-style text interface; BP-01 permanent text-first canon; BP-06/BP-07 individual officer/recruit; BP-38 readable source records; BP-43 essential-workflow tests. | Ownership split appears coherent; verify no essential action requires graphics. |
| S45 Maps, diagrams and visual evidence | BP-02 spatial source; BP-12/BP-15/BP-16 incident/case/investigation views; BP-20 surveillance; BP-22 scenes; BP-23 evidence; BP-24 forensics; BP-35 derivation; BP-40 presentation; BP-41 reports; BP-38 records. | Ownership split appears coherent; verify every visual is derived from canonical records and cannot override text/source evidence. |
| S46 Database, schemas and persistence | BP-38 canonical records/schemas/constraints; BP-39 persistence/recovery; BP-40 interface; BP-43 tests; BP-44 change control. | Ownership split appears coherent; verify connectivity claims require a successful live test and physical schema remains BP-38-owned. |
| S47 Storage efficiency and capacity governance | BP-38 storage design/measurement; BP-39 recovery footprint; BP-43 benchmark/evidence; BP-44 change gate; BP-01 global priority/approval. | Mandatory baseline, byte/MiB estimate, uncertainty, explicit approval and post-write measurement are present; no Neon write authorised. |
| S48 Security, permissions and information boundaries | BP-42 central access/security; BP-05/BP-30 authority; BP-38 data boundary; BP-40 presentation; BP-43 adversarial tests; all domain owners supply permission scopes. | Ownership split appears coherent; verify hidden truth, restricted personal data, credentials and derived views cannot leak. |
| S49 Backups, recovery and data integrity | BP-39 backup/restore/recovery; BP-38 record integrity; BP-43 restore testing; BP-44 change governance. | Ownership split appears coherent; recovery objectives/cadence and provider capabilities remain open decisions, not approved defaults. |
| S50 Testing, validation and simulation quality | BP-43 test strategy/evidence; every domain division supplies acceptance criteria; BP-38 schema constraints; BP-44 release/change gates. | Ownership split appears coherent; no test execution or verification is claimed from authored criteria alone. |
| S51 Operations, observability and maintenance | BP-35 runtime health; BP-38 database; BP-39 recovery; BP-40 operator visibility; BP-41 notifications/reports; BP-43 quality gates; BP-44 safe change. | Ownership split appears coherent; verify all critical failures are detectable, attributable and recoverable. |
| S52 Canon, versioning and change control | BP-44 controlled change; BP-01 canon; BP-38 schemas/records; BP-43 evidence/status. | BP-44 specification and approval gates exist; verify every amendment has reason, authority, affected requirements, migration impact and test evidence. |

This is an initial ownership/content scan only. Requirement-by-requirement destination coverage and acceptance-test adequacy remain open, including adversarial and cross-channel tests.

### Semantic finding A16 — public transport and mobility ownership

<badge color="success">Resolved in draft specifications and crosswalk v1.3</badge>

**Source:** S17.R01.

**Gap:** The source explicitly requires public transport, fleet, routes, timetables, stops, parking and accessibility. The original specifications had a road graph and generic transport-operator references, plus generic scheduling, but did not clearly allocate stop/parking/accessibility spatial records, transport service routes/fleet profiles and timetable occurrences across the owning divisions.

**Resolution within existing divisions:**
- **BP-02:** owns public-transport stops/stations/terminals, parking/loading areas, accessible pedestrian connectors, spatial identity and route geometry/topology.
- **BP-04:** owns transport operators, service-route identity, ordered stop sequences, fleet/service profiles, capacity, accessibility and service disruption events.
- **BP-37:** owns timetable definitions and scheduled service-run occurrences; it does not decide route geometry or operator/service identity.
- **BP-09:** remains owner of police fleet/resource readiness only. **BP-10/BP-11/BP-12** consume route and service availability for patrol, dispatch and incidents.

Added BP-02 criterion AC-D10 and BP-04 criterion AC-D07. BP-37's schedule catalogue and source traceability now explicitly include public transport timetables/service runs. Crosswalk S17.R01 now includes BP-37; finding A16 and the S17 review status were updated.

**Verification:** Updated BP-02/BP-04/BP-37 specifications and crosswalk were fetched after commit. Test execution remains pending.

## 7. Cross-division invariants and boundaries to reconcile

The full audit must specifically test these high-risk boundaries:

- BP-01 canon vs BP-02 geography vs BP-03 population vs BP-04 property/businesses.
- BP-03 canonical person identity vs BP-06 police personnel vs BP-17/BP-18 case roles vs BP-36 relationships.
- BP-05 police architecture vs BP-06 personnel vs BP-07 career vs BP-08 deployment vs BP-30 governance vs BP-31 standards vs BP-32 training vs BP-33 HR.
- BP-09 resources vs BP-10 patrol vs BP-11 dispatch vs BP-12 incidents.
- BP-13 crime taxonomy vs BP-14 hidden occurrence truth vs BP-15 case lifecycle vs BP-16 investigation.
- BP-17 victims/witnesses vs BP-18 suspects/offenders vs BP-19 interviews vs BP-20 surveillance vs BP-21 intelligence.
- BP-22 scene control vs BP-23 exhibit identity/custody vs BP-24 examination/results.
- BP-25 arrest/warrant/search vs BP-26 police custody vs BP-27 legal process vs BP-28 adjudication vs BP-29 sentence execution.
- BP-30 governance vs BP-31 professional standards vs BP-32 training vs BP-33 employment vs BP-34 finance/procurement.
- BP-35 event execution vs BP-37 canonical time vs BP-38 authoritative records vs BP-39 recovery.
- BP-40 interface vs BP-41 notifications/reporting vs BP-42 security vs BP-43 testing vs BP-44 change control.

## 8. Audit status

| Audit layer | Status | Evidence |
|---|---|---|
| Source JSON integrity and counts | PASSED | 52 divisions; 168 requirements; 60 tests |
| Source-ID mapping completeness | PASSED | 228/228 IDs mapped |
| Fixed 44-division structure | PASSED | Master blueprint and all 44 spec files present |
| Top-level section numbering | PASSED | All 44 checked; five defects corrected and re-fetched |
| Requirement-to-specification semantic coverage | IN_PROGRESS | Detailed item-by-item reconciliation S01–S16 and S33–S52 complete (73 source requirements/tests across S01–S16); S17–S32 still require the same detailed review |
| Cross-division ownership and interface consistency | IN_PROGRESS | Ownership boundaries reviewed for S01–S16 and S33–S52; full 44-division consistency pass remains |
| Acceptance-test adequacy against source wording | IN_PROGRESS | Source tests S01–S16 and S33–S52 checked against mapped acceptance criteria; S17–S32 and full test-quality pass remain |
| Binding-canon propagation and contradiction audit | IN_PROGRESS | Canon inspected; detailed domain review S01–S16 and S33–S52 complete; full 44-division consistency pass remains |
| Design approval | NOT_APPROVED | User retains approval authority |
| Implementation / test execution / verification | NOT_STARTED | No implementation evidence asserted |

## 9. Required next sequence

1. Complete detailed source-to-specification semantic reconciliation for S17–S24, then S25–S32 in numeric order. S01–S16 and S33–S52 now have detailed item-by-item reconciliation recorded; do not repeat those reviews unless a later change affects them.
3. For each remaining source item, record every source ID, mapped destination, evidence section, result, defect and resolution. Resolve ownership conflicts and update relevant specifications/crosswalk without changing the 44-division structure.
4. After S01–S32 are reconciled, perform a whole-blueprint pass for canon propagation, cross-division ownership, acceptance-test adequacy, traceability, numbering, register accuracy and dependency consistency.
5. Keep test definitions distinct from execution results. No test is passed without reproducible evidence against the stated target.
6. Only after the full audit is complete, prepare an implementation plan. Any Neon write remains separately gated by current measured baseline, credible size estimate, explicit user approval and post-write measurement.

**Current conclusion:** Source mapping is complete and document structure has been corrected. Detailed item-by-item semantic reconciliation is complete for S01–S16 and S33–S52; S17–S32 and the final whole-blueprint consistency pass remain. No claim of full design completeness, implementation, test execution or verification is made.


## 7. Detailed semantic reconciliation: S33–S36

**Review method:** Each original source requirement and test was compared with the actual mapped destination specification sections, ownership boundaries and acceptance criteria. This is a specification-content review, not test execution.

| Source item | Required meaning checked | Destination specification evidence | Semantic result |
|---|---|---|---|
| S33.R01 | Forensic disciplines, submissions, prioritisation, methods, results, limitations, contamination, quality and expert interpretation. | BP-24 §§4–19 defines capability, request/triage/job/method/examination/contamination/quality/report lifecycles; BP-23 §13 retains exhibit identity, exact versions and custody; BP-09 supplies specialist resources. | Covered; BP-24 owns forensic work and BP-23 custody. |
| S33.R02 | Raw result, analyst interpretation and investigative inference remain distinct. | BP-24 §§3, 12–13, 21; BP-23 §§3, 13; BP-16 §8 and BP-21 §§3, 5, 16–17 preserve source/result/interpretation/inference boundaries. | Covered; no competing source authority identified. |
| S33.R03 | Specialist resources and realistic turnaround times. | BP-24 §§4–9 and 17–18 define capability, qualification, triage, resource allocation, estimates, queues, delay and pause-aware work; BP-09 owns police resource availability. | Covered at specification level. |
| S33.T01 | Every forensic conclusion identifies method, source material, limitations and examiner. | BP-24 FORENSIC-AT-103–108 and FORENSIC-AT-143 require exact exhibit/version, examiner/competence, method/version, source, limitations, uncertainty and contamination/quality details. | Acceptance criterion directly tests the source intent. |
| S34.R01 | Interview planning, procedural status, participants, recordings, notes, questions, answers, breaks, disclosure and statement versions. | BP-19 §§5–14 and 18–25; BP-17/BP-18 retain participant-role ownership; BP-27 owns legal disclosure decisions. | Covered with explicit domain boundaries. |
| S34.R02 | Preserve verbatim/detailed source content and distinguish originals from summaries. | BP-19 §§11–14 preserve immutable turns, original recordings, versioned transcripts/statements and derived summaries; BP-23 §13 handles accepted evidential copies without taking source ownership. | Covered; originals and derivatives remain distinct. |
| S34.R03 | No leading prompts and no hidden-solution disclosure. | BP-19 §§3, 15–17 and player-control provisions prohibit inserted leading prompts, next-question suggestions and hidden-truth leakage; INT-AT-049 and INT-AT-112–120 cover question integrity, player choice and direct/indirect leak paths. | Covered. |
| S34.T01 | Interview chronology, participants and recording references reconcile. | INT-AT-061–080 and INT-AT-099 cover exact recording/version, intervals, gaps, clock uncertainty, participant/turn chronology and persistence. | Acceptance criterion directly tests the source intent. |
| S35.R01 | Source grading, reliability, confidence, dissemination, restrictions, products, links and review dates. | BP-21 §§6–15 and 20 define source and content assessment, analytical products, handling restrictions, dissemination, review and audit. | Covered by BP-21 as sole intelligence lifecycle owner. |
| S35.R02 | Intelligence remains separate from evidence and established fact. | BP-21 §§3, 5 and 16–17; BP-23 §3; BP-16 §8; explicit class boundaries and acceptance tests prevent intelligence from becoming evidence or proof by copying/linkage. | Covered. |
| S35.R03 | Preserve provenance and uncertainty. | BP-21 §§7–9 and 11–15 preserve source/version, uncertainty, caveats, assumptions, confidence, correction and dissemination lineage; BP-38 owns global record/provenance rules. | Covered. |
| S35.T01 | Every intelligence item has source, confidence and handling status. | BP-21 INTEL-AT-001–015, 021–050, 091–110 and 126–160 test source linkage, assessment, restrictions, dissemination and access. | Acceptance suite covers the source test's required fields and controls. |
| S36.R01 | Physical observation, CCTV/ANPR, authorised monitoring, coverage, blind spots, clock drift, retention and retrieval. | BP-20 §§5–7 and 11–13 define source/device, coverage and blind-spot intervals, observation/capture, clock calibration, retention and retrieval. | Covered. |
| S36.R02 | Requests, authorisations, collection windows, operators, exports and evidential continuity. | BP-20 §§8–9, 11, 14–15 and 18; BP-23 §§13–14 and 20 separate source capture/retrieval from accepted exhibit custody and derivative lineage. | Covered; handover does not transfer source ownership. |
| S36.R03 | Absence of coverage is never proof of absence. | BP-20 §§3, 7, 10 and 17; SUR-AT-018, 077 and 115; BP-21 and BP-23 preserve source-specific coverage limitations. | Explicit invariant and negative-case tests present. |
| S36.T01 | Each surveillance item identifies source device, coverage limits and time basis. | SUR-AT-001–020 and 061–080 test source identity/configuration, coverage, blind spots, raw timestamps, calibration, drift and uncertainty. | Acceptance suite directly tests the source intent. |

**Ownership and interface findings:** BP-24 owns forensic methods/results/interpretation; BP-23 owns exhibit identity/custody; BP-19 owns interview source records; BP-20 owns surveillance sources and capture; BP-21 owns intelligence assessment/dissemination; BP-16 consumes authorised information for investigative work; BP-38/BP-42 govern shared records/provenance and access. The inspected specifications consistently distinguish source originals from copies, derivatives, summaries and downstream conclusions.

**Semantic outcome:** S33–S36 are recorded as semantically covered at the specification-draft level on this review. No omission or conflicting authoritative owner was identified in these 16 source requirement/test checks. This is not division approval, implementation evidence or test execution. The source acceptance tests remain pending execution under BP-43; no test is marked passed.


## 8. Detailed semantic reconciliation: S37–S40

**Review method:** Compared each source requirement and acceptance test with the mapped target specification text, test suite, authoritative record owner and cross-division handoff. This is a specification-content review; it does not execute the tests or approve the divisions.

| Source item | Required meaning checked | Destination specification evidence | Semantic result |
|---|---|---|---|
| S37.R01 | Grounds, authority, applications, approvals, execution, searches, seizure, transport, booking, detention, welfare, reviews and release. | BP-25 §§4–22 owns grounds, warrants, search and seizure; BP-26 §§3–23 owns custody acceptance, booking, detention, welfare, reviews, transfers and release; BP-27 owns later legal process. | Covered with operational/legal boundary preserved. |
| S37.R02 | Custody clock and property continuity. | BP-26 §§10–11, 17, 25 and 29 derives custody time from BP-37; BP-26 owns detainee personal property; BP-23 owns exhibit continuity; BP-25 records explicit temporary custody and handover. | Covered; no parallel clock or exhibit ledger. |
| S37.R03 | Operational action remains separate from later legal decision. | BP-25 §§3, 21–24 and BP-26 §§3–4, 21–23 separate arrest/search/booking/release events from BP-27 charge/bail/remand process and BP-28 judicial orders/findings. | Covered. |
| S37.T01 | Custody and warrant events satisfy configured fictional rules and chronology. | ARREST-AT-061–075, 121–125 and 167–172; CUSTODY-AT-037–063 and 178–180; LEGAL-AT-117–122; all use versioned configured authority and BP-37 time. | Test intent mapped to operational and legal owner suites; execution pending. |
| S38.R01 | Charging, disclosure, prosecution, defence, hearings, evidence, rulings, verdicts, sentencing, appeals and outcomes. | BP-27 §§7–16 owns referrals, charges, prosecution/defence, disclosure, filings and party-side appeals; BP-28 §§9–21 owns listings, hearings, evidence adjudication, rulings, verdicts, sentencing, orders and judicial appeals. BP-15/BP-23 retain case and source ownership. | Covered with explicit division of responsibility. |
| S38.R02 | Procedural state and legal actors; preserve acquittals, dismissals and unresolved outcomes. | BP-27 §§5–10, 15, 18, 20–22 and BP-28 §§5–17, 28–30 preserve actor authority, party roles, separate charge/defendant outcomes, acquittals, dismissals and unresolved states. | Covered. |
| S38.R03 | Feed outcomes back without rewriting investigative history. | BP-28 §§4, 15–17, 27, 31 and 33 links authoritative orders/outcomes to BP-15/BP-16/BP-29 by immutable references; BP-27 §26 preserves legal record history. | Covered. |
| S38.T01 | Court outcomes link to correct charges, defendants and evidence versions. | LEGAL-AT-030–031, 071–087 and 112–120; COURT-AT-026–038, 048–055 and outcome/order tests; exact charge versions, party IDs and source/disclosure manifests are retained. | Test intent covered across BP-27/BP-28; execution pending. |
| S39.R01 | Sentence execution, prison/community supervision, rehabilitation, release, recall and post-release status proportionately. | BP-28 §§18–20 owns sentence authority and orders; BP-29 §§5–18 owns admission, execution, placements, supervision, rehabilitation, release, recall and post-release status. | Covered; non-police corrections remain proportionate, not equal-depth. |
| S39.R02 | Continuity between custody, court and person records. | BP-29 §§4, 7–10, 17–20 and 26; BP-26 owns police custody, BP-28 authoritative orders, BP-03 person identity/lifecycle. | Covered; each system consumes the other's versioned records without taking ownership. |
| S39.T01 | Sentence and release dates reconcile with court orders. | CORR-AT-007–013, 030–040, 044–048, 106–108; BP-28 sentence/order version and effective-time requirements; BP-37 canonical simulation clock. | Direct acceptance coverage present; execution pending. |
| S40.R01 | Public complaints, independent review, internal investigations, inspections, findings, remedies and published outcomes. | BP-31 §§6–17 owns complaint/professional-standards case lifecycle and findings; BP-30 §§14–15 and 19–25 owns institutional oversight and governance response; BP-41 owns publication/report delivery. | Covered with clear complaint, oversight and publication ownership. |
| S40.R02 | Due process, conflicts of interest and auditability. | BP-31 PS-AT-021–030, 065–096, 120–131 and BP-30 GOV-AT-073–096 enforce independent assignment, recusal, subject response, authorised findings, review, source audit and remedy accountability. | Covered. |
| S40.R03 | Institutional failure and public trust evolve from events. | BP-31 PS-AT-114–116 and BP-30 GOV-AT-088–093 record findings, institutional response and remedy follow-through; BP-35/BP-36 own causal trust effects; BP-41 reports authorised outcomes. | Covered; trust is not an arbitrary narrative score. |
| S40.T01 | Every complaint has a route, owner, status and outcome or pending reason. | PS-AT-002–030 and PS-AT-143; GOV-AT-075–095 and GOV-AT-147; referral, owner, status, pending reason and closure controls. | Direct acceptance coverage present; execution pending. |

**Ownership and interface findings:** BP-25 owns arrest/warrant/search/seizure execution; BP-26 owns police custody; BP-27 owns prosecution-side legal process and disclosure; BP-28 owns judicial adjudication and orders; BP-29 owns sentence execution and post-sentence supervision; BP-30 owns institutional oversight/governance response; BP-31 owns professional-standards and complaint investigations; BP-41 owns publication delivery. BP-03 remains person identity owner, BP-23 exhibit custody owner, BP-37 canonical clock owner, BP-38 record governance owner, and BP-35/BP-36 causal simulation owners.

**Semantic outcome:** S37–S40 are recorded as semantically covered at specification-draft level for the four source requirements and four source tests. No missing source requirement or conflicting authoritative owner was identified in this review. Configurable fictional legal/policy rules remain explicit configuration dependencies; no real-world legal periods or rules are silently imported. This is not implementation, test execution, division approval or verification. All acceptance tests remain pending execution under BP-43.


## 9. Detailed semantic reconciliation: S41–S44

**Review method:** All 16 source requirements and five source acceptance tests were compared with the source-to-target crosswalk, relevant target specification sections, acceptance tests and ownership interfaces. This is a specification-content audit only; it does not execute tests, approve divisions or establish implementation.

| Source item | Required meaning checked | Destination specification evidence | Semantic result |
|---|---|---|---|
| S41.R01 | One authoritative in-world clock/calendar/timezone, shifts, opening hours, deadlines and ordering. | BP-37 §§4–7, 9–15 owns canonical temporal model and schedule catalogue; BP-04/BP-07/BP-08/BP-11/BP-35 consume it for business, career, deployment, dispatch and event execution. | Covered; no competing domain clocks. |
| S41.R02 | No time advancement while outside simulation; exact resume without offline catch-up. | BP-01 §8; BP-35 §7 and AT-006–016; BP-37 §§7–8 and AT-014–018; BP-40 §15 and UI-AT-092. | Covered at global, engine, clock and interface layers. |
| S41.R03 | Paused, active, queued and historical event states. | BP-35 §§5–7 owns event lifecycle and execution gate; BP-37 §§7–12 owns clock advancement, due queue and schedule occurrence states; BP-38 retains authoritative records. | Covered with event execution distinct from temporal scheduling. |
| S41.T01 | Every event timestamp uses one canonical time basis and stable ordering. | BP-37 AT-002, AT-004, AT-053–055 and AT-059; BP-35 AT-032–034; BP-38 schema/provenance governance. | Direct acceptance coverage present; execution pending. |
| S42.R01 | Coordinate people, organisations, services, incidents, schedules, resources, weather and time through auditable deterministic event processing where feasible. | BP-35 §§4–6, 9–12 and 18 owns event orchestration; BP-03/BP-04/BP-14/BP-36/BP-37 retain domain truth and schedules; explicit interfaces prevent engine/domain ownership collapse. | Covered; deterministic execution applies where declared. |
| S42.R02 | Relevance-based processing without loss of persistence or continuity. | BP-03 individual identity/promotion and population fidelity; BP-35 §§9.4–9.5 and 14 controls relevant-person promotion and workload/fidelity; BP-37 §16 and AT-121–126 use bounded wake-ups and preserve case-relevant events; BP-38 preserves canonical records. | Covered; workload reduction cannot downgrade relevant people or discard case-relevant events. |
| S42.R03 | Prevent impossible simultaneous states, causal loops and unexplained mutation. | BP-35 §§5–6, 10, 15 and AT-036–040, 059–063, 118; BP-37 §§11–12 and AT-054–059; BP-38 validates identifiers, provenance and event persistence. | Covered through causal prerequisites, domain validation, concurrency constraints and quarantine. |
| S42.R04 | Background activity does not advance while player is out. | BP-01 §8; BP-35 §7 and AT-006–016; BP-37 §§7–8; BP-40 §15/UI-AT-092. | Covered; pause applies to all simulated activity, not merely the clock display. |
| S42.T01 | Replay produces the same authoritative state where deterministic replay is specified. | BP-35 §§12.4, 13, 15 and AT-128–132, 217, 224; BP-38/BP-39 retain event and recovery inputs; BP-43 owns execution of replay tests. | Direct acceptance coverage present; deterministic boundary and captured AI inputs are explicit; execution pending. |
| S43.R01 | Generate varied, naturalistic text consistent with records, knowledge, voice and uncertainty. | BP-01 §§5–7; BP-35 §§12.1–12.3 and AT-069–071; BP-40 §§11 and UI-AT-105. | Covered; generated presentation is grounded in authorised versioned context. |
| S43.R02 | Separate hidden world truth, player-visible information and NPC knowledge. | BP-01 §6; BP-35 §§9.2, 11–12 and AT-056–071; BP-21/BP-42 own intelligence and information permissions; BP-40 §11. | Covered across distinct truth, knowledge and permission boundaries. |
| S43.R03 | Reveal hidden offender identities/solution only after exact player input bingo. | BP-01 §6.1; BP-35 §§3, 11–12 and AT-075–080; BP-40 §§9, 11–12 and UI-AT-070–071, 109; BP-42 enforces information permissions. | Covered; exact, case-sensitive trigger, with no leakage through metadata, logs, visuals or NPC dialogue. |
| S43.R04 | No unsolicited solution hints or instructions about what to investigate next. | BP-01 §§5.2–5.4; BP-35 §11 and AT-075; BP-40 §9 and UI-AT-110. | Covered; player retains investigative decision-making. |
| S43.R05 | Canon-changing generated claims persist as structured events/records. | BP-35 §§5, 12.3 and 18; AT-020, 024–028, 069 and 129; BP-38 owns schemas and canonical record persistence; BP-42 controls access. | Covered; presentation-only text is not silently promoted into world truth. |
| S43.T01 | No hidden truth leaks before exact reveal trigger. | BP-01 acceptance criteria AC-C03; BP-35 AT-070, 075–079; BP-40 UI-AT-070–071, 109–110; BP-42 information controls. | Direct negative-case coverage present; execution pending. |
| S43.T02 | NPC knowledge never exceeds plausible information. | BP-01 §6.2; BP-35 §§9.2, 9.3 and AT-056–058, 066, 071, 080; BP-40 UI-AT-072 and 111. | Direct acceptance coverage present; execution pending. |
| S44.R01 | Laptop-style text-first interface with clear navigation, commands, records, status and contextual actions. | BP-40 §§4–8; UI-AT-001, 006–018, 027–039. | Covered. |
| S44.R02 | Individual-officer gameplay, with recruit-start option. | BP-01 §5; BP-06/BP-07 own personnel and career state; BP-40 UI-AT-002 and session/workflow contracts. | Covered; interface does not invent a parallel player/person identity. |
| S44.R03 | Readable prose/source records with compact navigation and metadata. | BP-40 §§5, 7, 13–14; UI-AT-007, 032–035, 128; BP-38 retains source record authority. | Covered; compact metadata cannot replace or truncate source content without explicit partial status. |
| S44.R04 | No essential action depends on graphics. | BP-40 §§2, 10, 14 and UI-AT-010–011, 055–064; BP-43 validates essential workflows. | Covered; visuals are optional projections with textual equivalents. |
| S44.T01 | All essential workflows operable through text commands and views. | BP-40 UI-AT-001–018, 098 and 132; BP-43 owns end-to-end and workflow test execution. | Direct acceptance coverage present; execution pending. |

**Ownership and interface findings:** BP-37 owns canonical time/calendar/schedules; BP-35 owns event execution, causal ordering, orchestration, pause/resume and deterministic replay; BP-03/BP-04 and other domain divisions own their domain facts; BP-38 owns schemas and canonical records; BP-39 owns recovery; BP-43 owns test execution. BP-01 owns foundational player-agency and hidden-truth invariants; BP-35 owns generation orchestration and canon-changing event flow; BP-42 owns information permissions; BP-40 owns presentation, commands and text workflows. BP-06/BP-07 retain personnel/career ownership.

**Semantic outcome:** S41–S44 are recorded as semantically covered at specification-draft level for all 16 source requirements and five source tests. No missing source requirement or conflicting authoritative owner was identified. The text interface remains complete without graphics; time and background activity remain frozen outside active play; relevant-person fidelity and persistent continuity are preserved; the exact bingo trigger and player-led investigation constraints remain binding. No acceptance test is marked passed: execution remains pending under BP-43. No division approval or implementation status changes follow from this audit.



## 10. Detailed semantic reconciliation: S45–S48

**Review method:** The 16 source requirements and five source acceptance tests in S45–S48 were checked against the unchanged source JSON, the 52→44 crosswalk, mapped BP specification content, ownership boundaries and corresponding acceptance criteria. This is a specification-level semantic review only; it does not execute tests, approve divisions or establish implementation.

| Source item | Required meaning checked | Destination specification evidence | Semantic result |
|---|---|---|---|
| S45.R01 | Optional maps, layouts, timelines, charts and forensic scene visuals when useful or requested. | BP-40 §§5, 8, 10 owns optional presentation and text fallback; BP-02 owns canonical spatial data; BP-12/BP-15/BP-16/BP-20/BP-22/BP-23/BP-24 own the relevant incident, case, investigative, surveillance, scene, exhibit and forensic source records; BP-35 coordinates projections; BP-41 owns report delivery. | Covered; no visual system becomes a separate domain authority. |
| S45.R02 | Visuals derive from canonical spatial/evidence data and cannot silently contradict text records. | BP-40 §10 requires source IDs, versions and transformation metadata, distinguishes measured facts/illustrative geometry and observed/inferred chronology, and prohibits visual mutation of source records; BP-02 spatial versions; BP-23 exhibit/source versions; BP-24 FORENSIC-AT-140–142. | Covered; uncertainty, derivative status and text fallback remain explicit. |
| S45.R03 | Text remains authoritative. | BP-01 §14; BP-38 §§3, 4 and 12; BP-40 §§2 and 10; UI-AT-007–011 and 055–056. | Covered; essential workflows and complete source records remain available without graphics. |
| S45.T01 | Every visual is traceable to underlying canonical records. | BP-40 UI-AT-056 requires canonical source IDs/version; BP-23 EVID-AT-125 and BP-24 FORENSIC-AT-140–142 require source linkage, transformation/uncertainty and non-contradiction; BP-38 preserves source/version references. | Direct acceptance coverage present; execution pending. |
| S46.R01 | Neon PostgreSQL persistence, GitHub source/specification/migration history and ChatGPT user-facing AI partner/interface. | BP-38 §§1, 16–17 defines the intended architecture and roles; BP-39 §§1–3 owns recoverable-copy/recovery operations; BP-40 owns user interface; BP-43 owns verification; BP-44 governs change approval. | Covered as intended architecture, not a claim of current live connectivity or implementation. |
| S46.R02 | Canonical schemas, constraints, relationships, IDs, migrations, indexes and transaction boundaries. | BP-38 §§5–11 and 17; DB-AT-001–020, 031–039, 051–060, 111–120 and 141–159. BP-44 §11 governs approval/coordination while BP-38 retains schema implementation ownership. | Covered; schema/record authority is separated from change approval and domain meaning. |
| S46.R03 | Lossless detailed narrative; normalised shared facts; references for repeated entities; no duplicate payloads. | BP-38 §§5–9, 13–14; DB-AT-041–050, 091–100; BP-39 backup classes preserve immutable source material and distinguish rebuildable projections. | Covered; structural compression and normalisation cannot discard meaningful narrative, provenance or case continuity. |
| S46.R04 | Immutable source records/events remain separate from derived views and summaries. | BP-38 §§9–10, 12–13; DB-AT-041–050, 061–070, 081–087; BP-35 §5.2 distinguishes projections from authoritative state; BP-39 separates source/event history from rebuildable projections. | Covered; corrections are additive and projections do not become a second source of truth. |
| S46.R05 | Do not claim live database connectivity without a successful connection test. | BP-38 §16 and DB-AT-124–129 require authenticated identity-checked evidence and safe health checks; BP-40 §13 requires honest status; BP-43 §15 prohibits assumptions/stale observations as proof. | Covered; connection claims require a current successful test against the expected target. |
| S46.T01 | Schema constraints enforce identity, referential integrity, population cap and valid lifecycle states. | BP-38 DB-AT-001–010, 021–039, 051–056 and 141–159; BP-03 retains person/population authority; BP-43 owns execution/evidence. | Direct acceptance coverage present; execution pending. |
| S47.R01 | Compact keys, enums, references, normalisation, deduplication and lossless compression; never compress meaningful narrative. | BP-38 §14; DB-AT-091–100; BP-01 storage-fidelity invariant; BP-39 retains required source/history during recovery. | Covered; efficiency is subordinate to meaning and fidelity. |
| S47.R02 | Avoid redundant fields/text, unnecessary indexes, repeated snapshots and unbounded logs. | BP-38 §§14 and 19; DB-AT-091–100 and 131–140; BP-39 §§6–9 distinguishes authoritative records from rebuildable projections and requires bounded backup/retention policy. | Covered; index and storage overhead must be justified and measured. |
| S47.R03 | Measure row, table, index and TOAST growth; benchmark representative high-entropy long text. | BP-38 §§14 and 18; DB-AT-094–097 and 131–135, 146–150; BP-43 §§12 and 15 defines representative narrative/storage benchmarks and measurement reporting. | Covered; actual compression and growth are measured rather than assumed. |
| S47.R04 | Before every Neon migration/schema change/seed/import/bulk write/upload, present measured baseline, byte and MB/MiB estimate, method, assumptions, uncertainty and projected total; wait for explicit user approval. | BP-01 §14; BP-38 §18 steps 1–7 and DB-AT-146–150; BP-43 §12; BP-44 §12. The rule applies to each individual operation; prior unrelated approval does not carry forward. | Covered as a mandatory hard gate; no blueprint or GitHub edit authorises a Neon write. |
| S47.R05 | After approved deployment, measure actual growth and compare with estimate; benchmark first if estimate is not credible. | BP-38 §18 steps 6–7 and DB-AT-149–150; BP-43 §§12, 15 and 17; BP-44 §12. | Covered; actual delta and variance must be recorded after each specifically approved operation. |
| S47.T01 | No Neon write occurs without explicit approval after a documented estimate. | BP-38 DB-AT-146–150; BP-43 §12; BP-44 §§9 and 12. | Direct negative-case acceptance coverage present; execution pending. |
| S47.T02 | Post-deployment measured delta is recorded. | BP-38 DB-AT-149; BP-43 §§12 and 17; BP-44 §12. | Direct acceptance coverage present; execution pending. |
| S48.R01 | Define user/player/officer/administrator/system roles; least privilege; secret handling; access checks and audit logs. | BP-42 §§4–8, 11 and 14 defines distinct principals/personas, default-deny least-privilege authorization, service identities, permission lifecycle, secret controls and attributable audit; BP-05/BP-30 own command/administrative authority; BP-40 applies controls; BP-38 enforces data-boundary checks. | Covered; identity, persona, institutional authority and data permission are not conflated. |
| S48.R02 | Protect hidden case truth and restricted personal information from player-facing leakage. | BP-42 §§9–13; SEC-AT-049–080 and 088–094; BP-01 §6; BP-40 §§9 and 12; BP-16/BP-17/BP-18/BP-19/BP-20/BP-21/BP-23 retain domain-specific case/source boundaries. | Covered; protection includes search, counts, metadata, maps, notifications, exports, logs, AI context, caches and NPC knowledge. Exact standalone case-sensitive bingo remains the sole reveal trigger. |
| S48.R03 | Keep credentials out of source control, narrative records and logs. | BP-42 §§5, 14 and 15; SEC-AT-043–048 and 088–092; BP-38 §§15–17 and DB-AT-106–107, 120; BP-44 §6 excludes secrets from ordinary configuration. | Covered; credentials remain in approved secret-management mechanisms and are excluded from ordinary records, source control and logs. |
| S48.T01 | Unauthorised reads/writes are rejected and audited. | BP-42 §§6, 11–12 and 14; SEC-AT-015–022, 032, 062–071 and 088–091; BP-38 DB-AT-101–110; BP-43 §13 requires service-boundary/adversarial tests. | Direct negative-case acceptance coverage present; execution pending. |

**Ownership and interface findings:** BP-40 owns optional visual presentation and text fallback; BP-02 owns canonical spatial data; relevant operational/case/evidence/forensic divisions own their source records; BP-38 owns canonical schemas, identity/reference integrity, transactions, indexes and read-model contracts; BP-39 owns backup/restore/recovery; BP-35 owns event execution; BP-42 owns security policy and secret handling; BP-43 owns test strategy/execution evidence; BP-44 owns change and approval governance. These interfaces do not create duplicate authorities.

**Semantic outcome:** S45–S48 are recorded as semantically covered at specification-draft level for all 16 source requirements and five source tests. No missing source requirement or competing authoritative owner was identified in this review. Visuals remain optional projections with source/version traceability and authoritative text fallback; database connectivity claims require successful tests; storage writes remain individually gated by measured estimates and explicit user approval; security is enforced beyond interface visibility. All acceptance tests remain pending execution. Division approval, implementation and verification statuses are unchanged. No Neon connection, migration or write was performed.

**Open design dependencies retained:** actual Neon project/branch/schema identity and connectivity evidence; physical schema and migration implementation; measured storage instrumentation and benchmark dataset; provider-specific backup/recovery capabilities; final authentication/secret-management provider configuration; final classification and permission catalogue values; and executable adversarial/integration test harness. These are not treated as completed merely because the specification contracts exist.


## 11. Detailed semantic reconciliation: S49–S52

**Review method:** The 13 source requirements and four source acceptance tests in S49–S52 were checked against the unchanged master source JSON, the 52→44 crosswalk, mapped BP specifications, section-level ownership contracts and corresponding acceptance criteria. This is a semantic specification review only. It does not execute tests, approve divisions or establish implementation.

| Source item | Required meaning checked | Destination specification evidence | Semantic result |
|---|---|---|---|
| S49.R01 | Define backup cadence, retention, restore testing, point-in-time recovery only where available, export format and disaster-recovery procedure. | BP-39 §§5–8 define recovery objectives, backup classes, cadence/retention/rotation and consistent checkpoints; §§10–16 define restore, validation, disaster scenarios and restore testing; §18 requires current provider capability verification; REC-AT-011–020, 041–081, 082–091 and 122–130. | Covered. Cadence, retention, RPO/RTO and provider capabilities remain explicit approved/configured values rather than assumed defaults. |
| S49.R02 | Protect canon and authoritative records against corruption, accidental overwrite and partial writes. | BP-39 §§8–14 require consistent checkpoints, isolated restore targets, layered validation, source preservation and controlled replay; REC-AT-028–040, 046–066, 086–097 and 102–111. BP-38 §§9–12 and DB-AT-041–070/302–311 own provenance, immutable source history and atomic transaction integrity. BP-44 controls recovery promotion. | Covered; integrity, transaction consistency, canon validation and recovery authority are separate required checks. |
| S49.R03 | Keep recoverable backups separate from live mutable state. | BP-39 §9 and §15; REC-AT-021–030 and 112–119; BP-43 QA-AT-100; BP-42 governs access policy. | Covered; backup isolation, environment separation and least-privilege access are explicit. |
| S49.T01 | A tested restore reproduces a verified checkpoint. | BP-39 REC-AT-067–081 requires isolated full restore, exact checkpoint/target, schema compatibility, representative records, integrity/provenance/permission checks and reproducible evidence; REC-AT-091 blocks completion before validation. BP-43 QA-AT-099; DB-AT-152; BP-44 CFG-AT-153. | Direct acceptance coverage present; restore execution and evidence remain pending. A backup file or written procedure alone is not a successful restore. |
| S50.R01 | Maintain unit, integration, schema, migration, end-to-end, replay, load, population, storage and narrative-quality tests. | BP-43 §§4–10 defines test taxonomy, artefacts, lifecycle, environments and test design; §§12–15 cover population/storage, adversarial, simulation/narrative, performance and resilience; QA-AT-011–021, 025–027, 063–071, 082–100 and 110–137. | Covered; test types are distinct and mapped to relevant risks rather than collapsed into a single generic test. |
| S50.R02 | Test edge cases, adversarial inputs, boundary conditions, race conditions, long-running continuity and cross-system reconciliation. | BP-43 §§10–15; QA-AT-013–018, 021–023, 025–026, 038–067, 082–085, 110–123 and 124–135. Cross-system reconciliation is explicit in §11; long-running drift/resource growth in §§14–15. | Covered; positive, negative, boundary, concurrency, adversarial, continuity and cross-domain tests are required. |
| S50.R03 | Use evidence-based completion criteria and regression gates. | BP-43 §§6, 16–18 define reproducible evidence, defects/exceptions, separate release gates and scoped reports; QA-AT-001–010, 015–020 and 124–143. BP-44 §§8–10/14 and CFG-AT-103–118/126–141 govern approval, change impact and release traceability. | Covered; documentation, a commit or a passing unrelated test cannot substitute for executed evidence and the correct gate. |
| S50.T01 | Every division has traceable acceptance tests and recorded results. | BP-43 QA-AT-001–009 and 132–143 require stable criteria, ownership, exact versions, execution records and evidence; BP-44 CFG-AT-111–118 and 157; BP-38 DB-AT-142–144. | Direct acceptance coverage present; tests are not claimed executed and every division's design/implementation/test/verification status remains distinct. |
| S51.R01 | Track service health, errors, latency, job queues, resource use, database size, failed events and recovery actions. | BP-35 §17 emits runtime lifecycle, queue/backlog, throughput/latency, retries, failures, resource and dependency-health signals; BP-38 §19 and DB-AT-131–140 cover database health, growth, query latency, deadlocks, queue lag and safe maintenance; BP-39 §17 and REC-AT-018–019/120/132 cover backup/recovery operations; BP-41 RPT-AT-099–105/178 covers authorised reporting; BP-09 tracks operational state/health of police resources. | Covered across owning services; metrics and alerts remain attributed, timestamped, redacted and distinguish measured, stale, degraded and unavailable states. |
| S51.R02 | Provide safe maintenance, migration, rollback and incident procedures. | BP-38 §§17–20 and DB-AT-111–120/131–140; BP-39 §§10–20 and REC-AT-041–091/117–147; BP-43 §15 and QA-AT-098–105/135; BP-44 §§11–16 and CFG-AT-081–090/129–150. | Covered; migration, recovery, operational maintenance and release/change authority are coordinated without merging their owners. Procedures are bounded, auditable, tested in isolation and preserve canon/pause semantics. |
| S51.R03 | Separate development/test data from authoritative simulation data. | BP-38 DB-AT-130/137; BP-39 §15 and REC-AT-112–119; BP-43 §9; BP-44 CFG-AT-031/099–101. | Covered; environment identities, credentials, data boundaries and promotion controls are explicit; fixtures cannot be mistaken for canon. |
| S51.T01 | Operational failures are detectable, attributable and recoverable. | BP-35 §17 and §18; BP-38 DB-AT-131–140; BP-39 REC-AT-018–019/041–066/082–091/120/132–150; BP-41 RPT-AT-102–105; BP-43 QA-AT-102–105/135; BP-44 CFG-AT-144–150. | Direct acceptance coverage present across runtime, persistence, recovery, reporting and QA; execution remains pending. |
| S52.R01 | Maintain one canonical blueprint version, decision log, glossary, schema registry and traceability matrix. | BP-44 §§4–7 and §19 establish artefact hierarchy, canonical blueprint/version governance, decision log, glossary, ownership registry and source traceability; CFG-AT-039–078 and 110–117. BP-38 owns the canonical schema/data contract registry and its implementation interfaces. | Covered; BP-44 governs canonical version and change history, while BP-38 retains schema/data contract authority. No parallel blueprint authority is introduced. |
| S52.R02 | No unapproved changes to canon, division structure, requirements or approved design. | BP-01 binding canon; BP-44 §§5, 8–9 and 16; CFG-AT-041–050, 058–065, 104–109 and 137–142. Explicit user approval is required for canon and 44-division structure changes. | Covered; AI/repository activity cannot self-approve or silently alter approved meaning. |
| S52.R03 | Record every amendment with reason, approval, affected requirements, migration impact and tests. | BP-44 §§8–11/14; CFG-AT-051–057, 066–070, 080–090 and 126–143; BP-43 QA-AT-003–010 and 124–134. | Covered; change requests, decision records, dependency impacts, migration plans, approvals, tests and post-change evidence are linked. |
| S52.R04 | Keep proposed, approved, implemented, verified and retired states distinct. | BP-44 §5 and §§8–9/14–15; CFG-AT-039–045, 111–118 and 156–159; BP-43 QA-AT-005–008/130/140–141; BP-38 DB-AT-143–144. | Covered; no state transition is inferred from silence, a document edit, a commit or an unexecuted test. |
| S52.T01 | Every implementation item maps to an approved requirement and evidence. | BP-43 QA-AT-003–004 and 132–134; BP-44 CFG-AT-157 and 111–118; BP-38 DB-AT-142–144. | Direct acceptance coverage present; no implementation item is claimed complete without approved requirement linkage and recorded evidence. |

**Ownership and interface findings:** BP-39 owns backup, restore and recovery execution; BP-38 owns schema, transaction and record integrity; BP-35 owns runtime event execution and engine telemetry; BP-37 owns canonical game-time semantics; BP-43 owns test strategy and independent evidence; BP-44 owns canonical versioning, decision/change approval, migration/release coordination and restore promotion. BP-09 owns police resource state; BP-40 presents authorised operational status; BP-41 owns alerts/report semantics and delivery; BP-42 owns security policy. These boundaries are explicit and do not create duplicate authoritative owners.

**Semantic outcome:** S49–S52 are recorded as semantically covered at specification-draft level for all 13 source requirements and four source acceptance tests. No missing source requirement or competing authoritative owner was identified in this review. Restore verification is distinguished from backup existence; testing includes edge, adversarial, race, scale and continuity coverage; operational monitoring spans runtime/database/recovery/resource/reporting owners; and canonical change control preserves approval and status distinctions. All acceptance tests remain pending execution. Division approval, implementation and verification statuses are unchanged. No Neon connection, migration or write was performed.

**Open design/implementation dependencies retained:** approved backup cadence, retention and RPO/RTO values; actual provider-supported PITR/export/restore capabilities; isolated restore harness and reproducible checkpoint evidence; concrete test runner, fixtures, CI/regression execution and evidence store; runtime/database/resource monitoring instrumentation and alert routing; environment provisioning and secret separation; and the executable change-approval/release workflow. These remain open until implemented and verified against the relevant acceptance criteria.


## 12. Detailed semantic reconciliation: S01–S08

**Review method:** All 27 source requirements and 14 source acceptance tests across S01–S08 were checked against their crosswalk destinations, actual target specification content, ownership boundaries, interfaces and acceptance criteria. This is a specification-content audit only; it does not execute tests or approve divisions.

| Source item | Required meaning checked | Destination specification evidence | Semantic result |
|---|---|---|---|
| S01.R01 | Sovereign status, bounded territory, jurisdiction, institutions, powers, succession and constitutional rules. | BP-01 §§2–3, 12 and 16 defines binding canon and constitutional authority; BP-02 §§2–3 and 10 fixes one sovereign city-state/city and off-map-only references; BP-30 §§5–7 defines institutions, offices, incumbency, authority and succession; BP-44 governs changes. | Covered; sovereign canon, geographic boundary, institutional mandate and change authority have distinct owners. |
| S01.R02 | Legal hierarchy, authority sources, emergency powers, separation of functions and jurisdictional limits. | BP-01 §12; BP-02 §§2 and 10; BP-27 §§2, 4, 6 and 27; BP-30 §§6–7; BP-42 permission enforcement. BP-27 keeps fictional legal hierarchy/actor authority as explicit configuration and blocks consequential action when authority is unresolved; BP-30 requires scoped, effective-dated grants and defined emergency-power triggers, scope, issuer, duration, review and termination. | Covered; undefined authority is not inferred from rank, title, database access or narrative. Emergency powers remain explicit fictional configuration, not an assumed power. |
| S01.R03 | Prevent external-city or territorial expansion. | BP-01 §§3 and 15; BP-02 §§2, 10 and AC-A01–A05; BP-44 change-control boundary. | Covered; external references cannot create a second playable city, local population or additional jurisdiction. |
| S01.T01 | Every location resolves inside Saltwater or is explicitly off-map. | BP-02 §§3, 7, 10 and AC-A04–A05; BP-12/BP-22 consumers use canonical spatial references. | Direct acceptance coverage present; invalid or unresolved locations are not silently placed inside the city. |
| S01.T02 | No institution exercises undefined authority. | BP-30 §§5–7, 19–20 require mandate, office, authority source, scope, exclusions, effective interval and validation; BP-27 LEGAL-AT-011/015/016 blocks actions without configured authority; BP-42 enforces access separately from substantive authority. | Direct acceptance coverage present across institutional, legal-process and access-control layers; no single permission grant is treated as a source of legal power. |
| S02.R01 | Canonical districts, neighbourhoods, zones, parcels, addresses, coordinates, boundaries, terrain, coastlines and land use. | BP-02 §§3–9 defines spatial entity classes, hierarchy, coordinate/geometry metadata, parcels/addresses, road network, natural geography and landmarks. | Covered; exact map features remain deliberate user-controlled canon decisions, not fabricated facts. |
| S02.R02 | All places, routes, incidents and properties resolve to consistent spatial IDs. | BP-02 §§5, 7–8, 13–14 and AC-B01–B05/E01–E04; BP-04 property/premises and BP-10/BP-12/BP-22 consumers reference BP-02 IDs; BP-35 validates location and route references. | Covered; BP-02 owns spatial identity/topology and consumers cannot create competing location authorities. |
| S02.R03 | Text descriptions remain complete and maps are optional. | BP-02 §§11 and 16, AC-F01–F02; BP-40 text-first interface; map output is a non-authoritative projection. | Covered; no gameplay-critical location function depends on graphics. |
| S02.T01 | No duplicate or contradictory canonical locations. | BP-02 §5 and AC-B01–B04; duplicate IDs and same-entity conflicts are rejected, with versioned parcel changes. | Direct acceptance coverage present. |
| S02.T02 | Every operational location is addressable and spatially related. | BP-02 §§7, 11, 13 and AC-B05/E01–E02; BP-04 assets link to valid parcel/address/access references. | Direct acceptance coverage present; unknown/ambiguous locations remain explicit rather than fabricated. |
| S03.R01 | Enforce opening 9,500 total (9,000 residents + 500 police), 500 headroom and 10,000 hard cap. | BP-01 §3.2; BP-03 §§2–3 and AC-A01–A08; BP-05/BP-06 police headcount references; BP-36 relationship/household links do not add population units. | Covered. A contradiction in BP-36's traceability note incorrectly described the 9,500 opening composition as superseded; corrected in finding A18 below. |
| S03.R02 | One authoritative person registry with exact living/deceased/entered/exited status. | BP-03 §§3–6 and 17; BP-38 owns physical schema/constraints while BP-03 remains domain owner; AC-A06–A08/C01–C07. | Covered; identity, lifecycle, population membership and derived totals are not separate competing registries. |
| S03.R03 | Track age, household, residence, occupation, eligibility, movement, births, deaths and permanent departures. | BP-03 §§4–9 and 17; BP-36 owns household/relationship semantics; BP-02 geography; BP-33 employment; BP-37 canonical age/time and schedules. | Covered across domain owners; unknown/disputed facts remain explicit and sourced. |
| S03.R04 | Atomic capacity checks for births/arrivals; reject events exceeding cap. | BP-03 §6.2 and AC-B01–B06; BP-35 event execution and BP-38 transaction integrity interfaces. | Covered; concurrent last-slot admissions, retries, partial failures and duplicate exits are explicitly addressed. |
| S03.R05 | Prevent double-counting police and multi-role persons. | BP-03 §§2–3, 9 and AC-A04–A08; BP-05/BP-06 personnel records reference one BP-03 person ID; BP-30 reiterates officers are included once. | Covered; police headcount is a subset/view of the population, not an additive population. |
| S03.T01 | Population ledger reconciles to person records. | BP-03 §§6.1, 6.3 and AC-A06–A08/B06; BP-38 transaction and reconciliation support. | Direct acceptance coverage present; execution pending. |
| S03.T02 | No valid operation produces 10,001 living persons. | BP-03 §6.2 and AC-A03/B01–B03; BP-35 validates event preconditions and BP-38 enforces transaction integrity. | Direct boundary and concurrency acceptance coverage present; execution pending. |
| S03.T03 | Police count is a subset, not an extra population. | BP-03 AC-A04–A05; BP-05 AC-C04; BP-06 §§3 and 14; BP-30 §8. | Direct acceptance coverage present; execution pending. |
| S04.R01 | Stable individual identity with attributes, history, needs, schedule, skills, employment, finances, relationships and relevant records. | BP-03 §§4, 7–10 and 17 defines identity attributes, life facts, routines, skills, financial references, relationships and owner links; BP-33 employment, BP-34 financial records, BP-36 relationships, BP-37 schedules and BP-04 business/premises details remain authoritative in their domains. | Covered; the person record links domain facts without duplicating their source records. |
| S04.R02 | Tiered processing without deleting/downgrading identities or established facts. | BP-03 §10 and AC-D01–D06; BP-35 relevance-based activation; BP-38/BP-39 preserve durable records and history. | Covered; processing optimisation changes runtime effort, not identity or retained facts. |
| S04.R03 | Permanently promote every materially police/case-connected person. | BP-03 §§10–11, AC-D02–D06 and promotion event contract in §17; case domains supply trigger references. | Covered; promotion is persistent, idempotent and never reversed after case closure. |
| S04.T01 | Identity remains stable across jobs, addresses and relationships. | BP-03 §§4, 8–9 and AC-C01/E01–E03; BP-36 AT-001–004 and BP-33 employment links. | Direct acceptance coverage present. |
| S04.T02 | Promoted persons are never downgraded or erased. | BP-03 AC-D02–D06; BP-36 AT-015 and case-linked interfaces; BP-35 preserves promoted fidelity. | Direct acceptance coverage present. |
| S05.R01 | Households, family, partners, dependants, friendships, conflicts, professional links and social networks. | BP-36 §§4–12, 18–19 and 22; BP-03 §8 owns person identity and link; BP-04 supplies premises/organisation identities. | Covered; household, family, professional and social relationship types remain distinct. |
| S05.R02 | Relationship history, shared addresses, contact patterns and plausible changes. | BP-36 §§8–9, 19–21 and AT-013–025/045–069; BP-02/BP-04 supply location and premises; BP-37 supplies canonical time. | Covered; effective/recorded time, source, confidence, dispute and correction lineage are retained. |
| S05.R03 | Plausible witness/victim/suspect/community connections without deterministic shortcuts. | BP-36 §§12–17 and AT-028–045; BP-14/BP-17/BP-18/BP-21/BP-35 consume social context without treating relationships as guilt, proof or deterministic role assignment. | Covered; social context informs but does not predetermine case roles or outcomes. |
| S05.T01 | Reciprocal relationship links where applicable and historically traceable. | BP-36 AT-020–021, AT-013–018 and AT-044–045; directionality is explicit and reciprocal projections derive from canonical records only where the relationship type requires it. | Direct acceptance coverage present; reciprocity is not incorrectly imposed on directed trust or other one-way relationships. |
| S06.R01 | Residential/commercial parcels, owners, landlords, tenants, leases, occupancy, vacancies, access, maintenance and disputes. | BP-02 §§7 and 13 owns parcel/address geography; BP-04 §§6–7 owns property/building/premises, ownership interests, tenancy, occupancy, access and maintenance; BP-34 owns financial transaction records. | Covered; property identity, spatial identity and financial settlement have separate owners. |
| S06.R02 | Lease terms, renewals, payments, occupancy, subletting/licences, keys and occupancy history. | BP-04 §§7, 9 and 12; BP-34 rent/payment references; BP-33 employment/occupant links; BP-38 record history. BP-04 AC-C01–C07 distinguishes owner/tenant/licensee/occupant, agreement, payment and physical occupancy. | Covered; agreement existence, payment and actual occupancy are not conflated; expired agreements may coexist with continued occupancy without silent renewal. |
| S06.R03 | Occupancy and access facts must be time-valid. | BP-04 §§7, 10 and 13; BP-20/BP-22 consume time-valid access/occupancy; BP-35/BP-37 coordinate effective time and event validity. | Covered; access, keys, occupancy and agreements retain effective intervals and history. |
| S06.T01 | No incompatible simultaneous occupancy/ownership state without explanation. | BP-04 AC-C01–C07 supports multiple/disputed/time-bounded interests and flags conflicts; BP-35/BP-37 validate temporal consistency. | Direct acceptance coverage present; exceptions require explicit recorded basis rather than silent normalisation. |
| S07.R01 | Dedicated business registry with stable IDs, sector, premises, ownership, operators, employees, hours, finances, assets, services and lifecycle. | BP-04 §§5 and 8–12 defines 10,000+ distinct local business records, identity, profile tiers, establishments, owners/operators, staff, hours, services, assets, transactions and lifecycle; BP-38 owns physical schema. | Covered; distinct business identity is not inflated by branches, brands, premises or aliases. |
| S07.R02 | Supply/demand, customers, contracts, inventory, deliveries, debts and commercial relationships at functional depth. | BP-04 §§8–12 and interfaces; BP-34 owns financial accounts/debts/payments; BP-35 coordinates deliveries/disruptions; BP-09 consumes police supply/resource relationships. | Covered at proportionate functional depth; no full economy simulator is implied. |
| S07.R03 | Businesses create plausible employment, access, records, witnesses, transactions and police-relevant activity. | BP-04 §§8–12; BP-33 employment/attendance; BP-10/BP-11/BP-12/BP-15/BP-16/BP-21 consume business records through authorised interfaces. | Covered; business records provide causal and investigative context without duplicating employment or case ownership. |
| S07.R04 | Avoid indistinguishable mass-generated businesses; preserve coherent variety and traceable ownership. | BP-04 §§5.2–5.4, 8–12 and AC-A01–A04; BP-35 tiered activity and BP-43 scale/variety tests. | Covered at specification level; variety metrics and actual generated baseline still require implementation/testing. |
| S07.T01 | Every active business has valid status, sector and location or explicit mobile/virtual basis. | BP-04 AC-A03–A04 and operational-profile criteria; BP-02 location contract; mobile/virtual basis is an explicit profile state. | Direct acceptance coverage present. |
| S07.T02 | Business employment and premises occupancy reconcile. | BP-04 AC-E01 and occupancy criteria; BP-33 employment records; BP-03 canonical person identities; BP-02/BP-04 premises IDs. | Direct acceptance coverage present; no employee or occupant is duplicated as a new person. |
| S08.R01 | Track jobs, employers, contracts, shifts, attendance, payroll, leave, skills, qualifications, discipline and separation. | BP-33 §§4–15 and 18–20 owns general HR, contracts, recruitment, working patterns, attendance, leave, employee relations and separation; BP-04 owns employer identity; BP-34 payroll/financial ledger; BP-32 qualifications; BP-31 discipline; police-specific personnel/career remain BP-06/BP-07. | Covered; each HR subdomain has one owner and linked records. |
| S08.R02 | Plausible work schedules and movement between work and home. | BP-33 §10 and HR-AT-034/037/133/149; BP-37 canonical schedules/time; BP-03/BP-02 person movement and spatial topology; BP-35 validates travel/location feasibility. | Covered; planned shift, actual attendance, physical location and movement are distinct evidence-bearing states. |
| S08.R03 | Link employment to businesses, public institutions and police staffing. | BP-33 §§4, 7–8 and 18; BP-04 employers/institutions; BP-06/BP-07/BP-08 police personnel/career/deployment; BP-30 institutional authority. | Covered; general HR does not duplicate police service, career or unit assignment. |
| S08.T01 | Simultaneous shifts and locations do not conflict without recorded explanation. | BP-33 HR-AT-034/133/149; BP-35 AT-062/063; BP-37 AT-081/083/084/086; BP-03 AC-E04–E06. | Direct acceptance coverage present; incompatible concurrent work/location/travel is blocked or explicitly explained. |

**Semantic finding A18 — incorrect supersession note for the opening population baseline**

**Source:** S03.R01 and the binding canon in BP-01/BP-03.

**Defect:** BP-36's S03.R01 traceability row and accompanying “Canon correction” incorrectly stated that the 9,500 opening composition was superseded. The source and binding Saltwater canon still require 9,000 residents + 500 police = 9,500 living people at opening, with 500 unused headroom and a 10,000 hard cap. The 500 headroom is not a separate reserve population.

**Resolution:** Corrected BP-36's traceability and canon clarification. BP-03 remains the sole population identity/counting/capacity owner; BP-36 owns household and relationship semantics only. No source JSON, population canon or other division structure was changed.

**Verification:** BP-36 was committed and re-fetched from `main`; the corrected wording now preserves the 9,500 opening total, 500 headroom and 10,000 hard cap. The correction does not authorise population seeding or a Neon write.

**S01–S08 result:** All 27 source requirements and 14 source acceptance tests are semantically represented in their mapped draft specifications. One cross-division canon contradiction (A18) was corrected. No other omission or competing authoritative owner was identified in this detailed review. Acceptance tests remain unexecuted; division approval, implementation and verification statuses are unchanged.


## 13. Detailed semantic reconciliation: S09–S16

**Review method:** All 24 source requirements and eight source acceptance tests across S09–S16 were checked against their exact crosswalk destinations, the current target specification text, domain ownership contracts, relevant acceptance criteria and cross-system interfaces. This is a specification-content audit only; it does not execute tests, approve divisions or establish implementation.

| Source item | Required meaning checked | Destination specification evidence | Semantic result |
|---|---|---|---|
| S09.R01 | Essential goods, wholesalers/retailers, local and off-map suppliers, gateways where configured, warehouses, transport and distribution. | BP-04 §§5, 9–10 and 13.1–13.4 owns business/provider/warehouse identity, supplier/customer links, operational stock and dependency profiles; BP-02 owns roads/routes/spatial topology; BP-09 owns police inventory/logistics; BP-34 owns procurement and financial transactions; BP-35 §10.4 coordinates route and delivery effects. | Covered at proportionate depth; external gateways/counterparties remain references and do not instantiate another playable territory. |
| S09.R02 | Stock, orders, shortages, deliveries, contracts and disruptions reconcile at the level needed for city and police continuity. | BP-04 §13.2–13.4 and §14 owns business stock, supplier relationships and stock events; BP-09 §§6–7/12/15 owns police receipt, inventory, stock/replenishment and shortage states; BP-34 §§9/13 owns purchase orders, invoices, payment and financial obligations; BP-35 §§10.3–10.4 coordinates causal delivery/disruption/restoration. | Covered; physical stock, financial valuation/payment, procurement authority and causal delivery execution are separate linked records. |
| S09.R03 | Off-map supply dependencies must not create additional playable territory. | BP-01 binding canon; BP-02 §§2/10; BP-04 §13.3; BP-35 §10.4. Off-map suppliers are external counterparties/boundary transactions only. | Covered; no external playable city, population or jurisdiction is created. |
| S09.T01 | Inventory and delivery events reconcile across sender, carrier and receiver. | BP-35 AT-101/102; BP-04 §13.2 and AC-E04; BP-09 receipt/transfer/inventory reconciliation; BP-34 AT-046/054/055 for purchase-order receipt, partial delivery and rejected goods. | Direct cross-domain acceptance coverage present for delivery identity, physical receipt and quantity/value reconciliation; execution pending. |
| S10.R01 | Currency, public revenue, taxation, fees, expenditure, budgets, debt, grants and financial periods. | BP-34 §§5–15 defines currency/accounting configuration, parties/accounts, transaction/journal model, budget and commitment controls, procurement, payroll, public revenue/tax/fees, debt/grants and period close; BP-30 §§12–13 owns public authority/approval matrix; BP-33 supplies approved employment/time inputs. | Covered; currency, chart of accounts, accounting basis and tax/fee policy remain explicit fictional configuration decisions, not silently imported real-world rules. |
| S10.R02 | Business and household finances represented at proportionate depth for city function and police cases. | BP-34 §§2, 5.2, 12–13 and 20; BP-03 supplies canonical person/household identity references; BP-04 supplies business identity and operational facts. Estimates and aggregates are labelled and cannot masquerade as exact bank balances or complete transaction histories. | Covered; detail increases when materially relevant without requiring deep accounting simulation for all 10,000+ businesses or all residents. |
| S10.R03 | Arithmetic, accounting records and audit trails reconcile; no fabricated unbalanced totals. | BP-34 §§6–7/14–18 and immutable transaction/journal/correction model; BP-38 §§9–11/19–20 provides provenance, atomicity and recovery integrity; BP-43 §§10–12/16 requires reproducible balance and reconciliation evidence. | Covered; no silent balancing entries, floating-point money, partial journals or unexplained write-offs. |
| S10.T01 | Every posted transaction balances under its configured accounting model. | BP-34 AT-011–018, AT-020–024, AT-026–030, AT-100/105/107/170/180; BP-38 DB-AT-051–060; BP-43 financial reconciliation test requirements. | Direct acceptance coverage present for balance, atomic rejection, idempotency, concurrency, projection watermark and recovery reconciliation; execution pending. |
| S11.R01 | Executive, legislative, administrative and oversight functions, offices, incumbents, mandates, decision processes and records. | BP-01 sovereign canon; BP-30 §§5–7/11/14–16 owns institutional architecture, offices/incumbency, appointment/succession, authority/delegation, decisions, oversight and interagency agreements; BP-38 supplies records/provenance; BP-42 enforces access. | Covered; office, officeholder, appointment, delegated authority, institutional decision and permission remain distinct. |
| S11.R02 | Public policy, procurement, permits, licensing, inspections and public complaints. | BP-30 §§10–14 owns policy/permit/licence/inspection workflows, governance and oversight; BP-04 owns entity/premises/provider facts; BP-31 owns professional-standards complaint/misconduct case lifecycle; BP-34 owns procurement execution and financial records. | Covered; governance approval is not mistaken for an operational inspection, asset receipt, payment or professional finding. |
| S11.R03 | Every government action has an accountable actor, valid authority and date. | BP-30 §§6–11/19–20 requires office, issuer, scope, authority, effective time, rationale and audit; BP-38 §§9–12 records immutable provenance; BP-42 separates access from substantive authority. | Covered; undefined authority, office-title inference and untraceable retrospective action are blocked. |
| S11.T01 | Every official action has an authorised actor and traceable record. | GOV-AT-005/006/017–020/100/145; BP-38 DB-AT-041–047/062–068; BP-42 service-boundary authorization tests. | Direct acceptance coverage present for authority, actor, effective time, version and provenance; execution pending. |
| S12.R01 | Civil status, identity, address, property, business, permits and other required registers. | BP-30 §12 explicitly owns civil-registry office/mandate, registrar appointment/authority, register catalogue, registration/certification workflows and corrections/challenges; BP-03 owns person/life-event identity; BP-04 owns property/business source records; BP-30 also owns permit workflow. | Covered; each register references the authoritative domain record rather than creating duplicate identity, property or business masters. |
| S12.R02 | Corrections, versions, issuing authority, access and provenance are preserved. | BP-30 §12; BP-38 §§6/8–12/15; BP-42 §§6/8–12; BP-44 change/version governance. Civil registration records identify issuer, effective/recorded times, status and correction lineage. | Covered; prior registered values and source history remain available, with controlled access and attributed correction. |
| S12.R03 | In-world retrieval and controlled disclosure of public records. | BP-30 §12 defines permitted disclosure authority; BP-38 §§13/15 applies access before query, search, aggregate and export; BP-42 §§6/9/11–13 governs record/field/purpose permissions; BP-16/BP-27 consume authorised registry references for investigative/legal workflows. | Covered; registry existence does not imply unrestricted access or public disclosure, and search/count/derived views cannot bypass policy. |
| S12.T01 | Record changes preserve prior values and the reason for change. | GOV-AT-151–155; DB-AT-043–047/062/066; SEC-AT-011–014/020–023; BP-44 change provenance. | Direct acceptance coverage present for registrar authority, correction lineage, prior value, reason, time and permissions; execution pending. |
| S13.R01 | Healthcare providers, practitioners, emergency care, capacity, appointments, treatment events and public-health alerts. | BP-04 §§9.1/9.3/10.1/14 represents providers/facilities, practitioner/service roles, emergency-care capability, capacity/availability, appointment/referral and treatment-event metadata, alerts and disruption/restoration; BP-35 §10.6 coordinates service/capacity events; BP-37 supplies time. | Covered at proportionate support-service depth; no separate deep healthcare simulator or fabricated clinical detail is introduced. |
| S13.R02 | Injuries, deaths, medical evidence and care access remain consistent across person, case, scene, custody, forensic and court workflows. | BP-03 person/life-event and care references; BP-17 §§8–10/13 stores minimum necessary participant needs and medical liaison; BP-22 scene context; BP-23 exhibit/custody; BP-24 forensic medical examination; BP-26 custody care; BP-28 court receipt/consideration; BP-35 AT-107/108 coordinates capacity and chronology. | Covered; clinical care, person-level facts, participant support, evidence custody, forensic interpretation, custody decisions and court findings retain separate owners. |
| S13.R03 | Sensitive healthcare information is protected by role-based in-world access. | BP-42 §§6/9/11–13 enforces domain/record/field/purpose permissions; BP-17 VIC-AT-083/086 limits medical liaison/referral disclosure; BP-35 AT-155 redacts protected medical data before AI context assembly. | Covered; a case role, provider relationship or operational need does not confer unrestricted clinical-record access. |
| S13.T01 | Medical timelines and service capacity remain internally consistent. | BP-35 AT-107/108; BP-04 AC-D06 and healthcare event contract; BP-17 VIC-AT-075/083/086; BP-37 canonical time and schedule execution. | Direct acceptance coverage present for capacity, appointments/treatment chronology, time-valid provider availability and protected liaison; execution pending. |
| S14.R01 | Schools, colleges, training providers, enrolment, attendance, staff, qualifications, schedules and facilities. | BP-03 §education participation and AC-EDU-01–06 owns individual learner enrolment/attendance/completion/qualification history; BP-04 §§9.1/9.3/10.1/14 owns provider/programme/facility/capacity and session facts; BP-33 owns staff employment; BP-37 schedules; BP-32 owns police training/credentials. | Covered; general learner records are not misplaced in police training, and provider/staff/schedule/person facts remain with their respective owners. |
| S14.R02 | Education/training supports police recruitment and training and wider city workforce development. | BP-32 §§7–17/25 owns police learning, training, assessment and credentials; BP-07 consumes qualifications for career gates; BP-09 provides training resources; BP-33 owns staff/employment; BP-04 represents providers and facilities. | Covered; non-police education is represented proportionately while police training receives the required deeper system. |
| S14.R03 | Education and qualification histories are credible and include issuing bodies, dates and applicable prerequisites. | BP-03 AC-EDU-04/06 preserves issuer/award date and unknowns; BP-32 §§8/11–14/24 validates prerequisites, assessment, authorised award and credential validity; BP-38 retains source/version/provenance. | Covered; attendance, completion, demonstrated competence, assessment pass and qualification award are not conflated. |
| S14.T01 | Qualifications have issuing bodies, dates and valid prerequisites where applicable. | BP-03 AC-EDU-04/05; BP-04 provider/issuer profile; BP-32 qualification lifecycle and TRN-AT-161 general-education boundary; BP-38 issuer/source references. | Direct acceptance coverage present; general education issuer/history and police credential prerequisites have distinct owners; execution pending. |
| S15.R01 | Social services, housing support, safeguarding, disability support, youth/elder services, charities and community organisations. | BP-04 §§9.1/9.3/10.1 represents providers, organisations, facilities and service availability; BP-30 §12 owns public-service mandate/governance; BP-17 §§8–10/13 owns participant-facing needs, safeguarding and referrals; BP-36 owns household/community relationships. | Covered at proportionate service depth; no second deep welfare/healthcare simulator or duplicated social relationship registry. |
| S15.R02 | Referrals track eligibility, capacity, case status and outcomes. | BP-17 §§9–10 defines referral origin, recipient, authority/consent, minimum disclosure, time-valid capacity, delivery, acknowledgement, acceptance, refusal, partial/full fulfilment and closure; BP-04 supplies provider/capacity facts; BP-30 GOV-AT-103–108 defines service governance; BP-38 preserves versions/provenance. | Covered; referral sent/acknowledged/accepted/fulfilled are distinct and provider outcome does not prove the underlying concern. |
| S15.R03 | Service interactions can affect vulnerability, risk, support and police interactions without deterministic assumptions. | BP-17 §§8–10/14; BP-03 identity/life context; BP-14/BP-18 retain crime/suspect/offender role ownership; BP-35 §10.6 coordinates service effects; BP-36 supplies social context. | Covered; support context may inform response but cannot determine guilt, credibility or a case outcome. |
| S15.T01 | Each referral has an origin, receiving service, status and outcome or pending state. | VIC-AT-028/066/071/075/086/118; GOV-AT-103–108; BP-17 explicit referral lifecycle and provider acknowledgement/fulfilment contract. | Direct acceptance coverage present for source, authority, recipient, capacity, state, outcome, idempotency and uncertainty; execution pending. |
| S16.R01 | Water, electricity, sanitation, waste, telecoms, internet and critical infrastructure assets/operators/capacity/outages/restoration. | BP-04 §§9.1/10.1–10.3/14 owns operator and asset identity, service area, capacity, dependencies, maintenance, outage history and service events; BP-09 owns police-specific infrastructure/resources only. | Covered; city infrastructure is represented as local service/operator/asset records, without turning BP-09 into a city-utility registry. |
| S16.R02 | Service dependencies and disruptions affect only relevant residents, businesses and police assets/services. | BP-04 §13.4 defines dependent entity, provider, service, criticality, area, period and consequence; BP-35 §10.3 and AT-092/094 limits effects to connected assets/areas; BP-09/BP-10/BP-11/BP-12 consume police resource and operational effects. | Covered; no unrelated area is affected without an explicit dependency and causal event. |
| S16.R03 | Maintenance, incidents and service notices are tracked. | BP-04 §§10.3/14 owns asset maintenance/failure/repair/outage/restoration events; BP-09 owns police asset maintenance; BP-12 owns operational incident records; BP-41 owns authorised service-notice generation and delivery state. | Covered; maintenance, incident, outage/restoration event and public notice are distinct linked records. |
| S16.T01 | Outages affect only connected areas/assets and resolve through recorded restoration. | BP-35 AT-092–094; BP-04 dependency and outage/restoration event contract; BP-41 RPT-AT-002/035/044/047/095/098 and source-traceability contract for S16.R03 service notices. | Direct acceptance coverage present for dependency-bounded effects, explicit restoration and notice provenance; execution pending. |

**Semantic findings:** No missing source requirement or competing authoritative owner was identified in the detailed S09–S16 review. The crosswalk ownership split is supported by the target specifications: BP-04 owns built-world/provider/operator facts; BP-02 geography; BP-03 person/civil-life facts; BP-09 police resource stock; BP-17 participant support/referrals; BP-30 public authority/registry workflows; BP-31 professional-standards complaints; BP-32 police training; BP-33 employment inputs; BP-34 finance/procurement; BP-35 causal execution; BP-37 canonical time; BP-38 record integrity; BP-41 notices/reports; BP-42 access control; BP-43 test evidence.

**Open fictional configuration and implementation dependencies retained:** initial currency and accounting basis/chart; tax/fee rates and assessment rules; public office and registrar appointments; permit/licence categories and approval thresholds; provider/service eligibility and capacity baselines; education provider/programme/qualification catalogues; utility network topology, service areas, redundancy and outage-response parameters; supplier/gateway and transport-route data; notification channels and delivery acknowledgement capabilities. These are configuration/implementation matters, not semantic omissions in the reviewed draft specifications.

**S09–S16 result:** All 24 source requirements and eight source acceptance tests are semantically represented in their mapped draft specifications. No source wording or fixed BP-01–BP-44 division structure was changed. Acceptance tests remain unexecuted; division approval, implementation and verification statuses are unchanged. No Neon connection, migration, seed or write was performed.
