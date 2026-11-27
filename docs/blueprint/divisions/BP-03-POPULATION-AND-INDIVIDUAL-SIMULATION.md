# BP-03 — Population and Individual Simulation

**Project:** Saltwater  
**Blueprint:** BP-01–BP-44  
**Version:** 0.1  
**Status:** `DESIGNED` — approved as part of the user-approved BP-01–BP-44 master blueprint (2026-11-23)  
**Date:** 2026-11-22  
**Owner:** BP-03  
**Dependencies:** BP-01, BP-02, BP-04, BP-06–BP-08, BP-17–BP-18, BP-30, BP-33, BP-35–BP-39, BP-42–BP-44  
**Authority:** User-approved BP-03 design under the fixed BP-01–BP-44 master blueprint. SW-CANON-001 settles population scope and opening countability. One authoritative person identity and population ledger. This design approval does not authorise a production Neon migration or population seed.

---

## 1. Purpose

BP-03 defines the population accounting system and individual-person simulation architecture. It establishes the authoritative identity for every person in Saltwater's counted population, the 10,000-person hard cap, lifecycle and demographic facts, population membership, residence and movement links, household interfaces, individual attributes, processing tiers, persistent promotion, and reconciliation controls.

The population is not a decorative headcount. People must be coherent individuals whose identities, histories, roles, schedules, needs, relationships, employment and relevant activities can support the police simulation and persistent city world.

BP-03 owns person identity and population accounting. It does not own:
- geographic identity/address topology (BP-02);
- properties, buildings, premises and tenancy (BP-04);
- police employee/career records (BP-05–BP-08);
- general employment contracts/payroll/HR (BP-33);
- relationship semantics and social networks (BP-36);
- simulation event execution and clock (BP-35,BP-37);
- physical database schemas and persistence implementation (BP-38,BP-39);
- permissions (BP-42).

Those divisions link to the canonical person ID; they must never create parallel person identities.

**Traceability:** S03.R01–R05; S04.R01–R03; S05.R01–R03; S08.R01–R03; S31.R01–R03; S39.R01–R02.

## 2. Binding population canon

| Rule | Binding value |
|---|---|
| Total living population ceiling | **10,000** |
| Opening resident count | **9,000** |
| Opening police count | **500** |
| Opening total | **9,500** |
| Opening headroom | **500** |
| Police accounting | Included within 10,000; never added separately |
| Person identity | One stable canonical identity per individual |
| Population count | Distinct living person identities, not roles or memberships |
| Capacity changes | Atomic, validated and auditable |
| Persistent promotion | Permanent; never downgrade or erase established facts |

The 500 headroom is unused capacity, not a second population. The initial total must reconcile exactly: 9,000 residents + 500 police = 9,500 living people. The system must not silently fill the remaining 500.

No event may produce 10,001 living countable persons. A failed admission/birth transaction must leave no partial person, membership, job, residence, relationship or downstream event.

## 3. Population scope and counting semantics

### 3.1 Canonical counting rule

At any authoritative in-game time, population count is the number of distinct living persons whose current population-scope status places them within Saltwater's population. Each person counts once, irrespective of the number of roles or memberships.

The population-scope model must explicitly distinguish:
- permanent resident;
- temporary resident;
- person physically present in Saltwater but not resident;
- commuter/worker physically present;
- visitor physically present;
- police employee;
- other public/private institutional employee;
- temporarily outside Saltwater but retaining resident status;
- deceased;
- permanently departed;
- off-map person/reference not part of Saltwater's current population.

A person may have multiple memberships but one person identity and one population count contribution.

### 3.2 Binding countability semantics

To prevent an uncounted-person loophole, this draft proposes:
1. A permanent or temporary Saltwater resident counts while alive, including during temporary travel outside the city-state.
2. A nonresident physically present inside Saltwater counts while present.
3. A nonresident worker/commuter counts while physically present; work membership does not create a second count.
4. A visitor counts while physically present.
5. A nonresident off-map person who is not physically present and has no current Saltwater resident status is not part of the local population ledger. If police-relevant, they may be represented by a restricted off-map reference or promoted case-linked person record, with explicit `population_scope=false`.
6. A deceased or permanently departed person remains in historical records but no longer contributes to the living count.
7. A person cannot evade counting through multiple addresses, jobs, roles, aliases, memberships or duplicate identities.

The binding population-scope rules are adopted in [SW-CANON-001](../decisions/SW-CANON-001-population-scope-and-foundational-geography.md). The categories below are implemented using that decision record; they are not provisional alternatives.

### 3.3 Counting formula

At time (t):

[
P(t)=\left|\{person\_id:\ status(t)=LIVING \land population\_scope(t)=INCLUDED\}\right|
]

Required invariant:

[
0\leq P(t)\leq 10{,}000
]

Opening invariant:

[
P(t_0)=9{,}000+500=9{,}500
]

Headroom:

[
H(t)=10{,}000-P(t)
]

Membership rows, role counts, employment counts, household counts and police strength summaries must never be summed to derive total population.

## 4. Canonical person identity

### 4.1 Single identity
Every person has one immutable `person_id`. All divisions reference this ID. Names, aliases, dates, employment, addresses, relationships, status and roles are attributes or linked history, not new identities.

Person identity must be independent of:
- name spelling or change;
- preferred name or alias;
- address/residence;
- employer or occupation;
- police/non-police role;
- relationship or household membership;
- case role or legal status;
- simulation processing tier.

### 4.2 Identity attributes

The canonical person profile supports, where known and relevant:
- stable person ID;
- legal/full name and preferred/display name;
- aliases and former names;
- date of birth or age range where exact DOB is unknown;
- nationality/citizenship/residency descriptors as fictional canon requires;
- sex/gender fields only where relevant to the simulation and explicitly defined;
- language(s);
- birth place/off-map reference where known;
- current life status;
- population-scope status;
- current residence and address references;
- household memberships;
- employment and role references;
- education/qualification references;
- skills and experience;
- schedules/routines;
- relationships;
- financial/asset references at proportionate depth;
- needs and support dependencies where relevant;
- behaviour/personality representation where justified;
- police relevance/promotion status;
- creation, source, provenance and effective dates.

Sensitive or highly personal attributes must not be generated or exposed without a defined gameplay purpose and permission model. BP-42 governs access. BP-03 defines the identity field semantics, not access rights.

### 4.3 Unknown, estimated and disputed attributes
Unknown values remain unknown. Do not invent exact DOBs, addresses, nationality, employment, relationship status or personal histories merely to fill fields.

Where an estimate is useful, store:
- estimated value/range;
- confidence;
- source;
- who recorded it;
- in-game time;
- basis/limitations;
- whether later confirmation supersedes it.

Conflicting values must coexist as sourced claims or be resolved through an attributed correction; do not silently overwrite the prior record.

### 4.4 Civil identity and registration references

Where Saltwater's configured civil registry recognises a fact, the canonical person record must link to its authoritative registration record and preserve the registered value, status, issuing/recording authority, effective date, recorded date, source, correction history and current validity. This includes birth and death registration and any configured civil-status, name, citizenship/residency or other legally registered life event; do not infer a registration from a social relationship, household membership, reported event or unverified claim. BP-30 owns the registry institution, mandate, authorised registrar roles and public-administration process; BP-38 owns common register/version/provenance/access standards; BP-36 owns the underlying social/family relationship semantics; BP-02/BP-04 own address, property and business source records. BP-03 owns the person-linked civil identity/life-status reference and population consequences. A correction to a register must not erase the prior value or silently rewrite historical case records.
Unknown values remain unknown. Do not invent exact DOBs, addresses, nationality, employment, relationship status or personal histories merely to fill fields.

Where an estimate is useful, store:
- estimated value/range;
- confidence;
- source;
- who recorded it;
- in-game time;
- basis/limitations;
- whether later confirmation supersedes it.

Conflicting values must coexist as sourced claims or be resolved through an attributed correction; do not silently overwrite the prior record.

## 5. Lifecycle and status model

### 5.1 Person lifecycle
A person's lifecycle supports:
- planned/not yet created;
- born/entered population;
- living and population-included;
- temporarily absent while retaining resident membership;
- deceased;
- permanently departed;
- historical/archived identity.

Exact status names and transitions must be enumerated in the schema specification. The lifecycle must not permit contradictory simultaneous terminal states.

### 5.2 Entry
Entry events include birth, migration/arrival, change of residence, or first physical presence for a nonresident person. Before entry:
1. resolve whether the person already exists;
2. check current population-scope status;
3. check whether the event changes the count;
4. atomically validate capacity;
5. create or update the canonical person record;
6. create dated membership/address/role records;
7. emit an auditable event;
8. reconcile population totals.

If capacity is insufficient, reject the event with no partial mutation.

### 5.3 Exit
Exit events include permanent departure, death and other canon-defined removal from the living local population. Temporary travel does not automatically remove a resident from population count.

An exit must:
- identify the person and prior status;
- record event type, time, source and actor;
- close or update relevant memberships;
- preserve all historical records and relationships;
- release one unit of population capacity only when the person's countable status actually ends;
- trigger downstream updates without deleting identity.

### 5.4 Death
Death is a life-status transition, not deletion. It must preserve identity, relationships, employment history, property links, case links, records and all historical facts. The time and source of death may have different certainty levels. A reported death is not automatically a confirmed death.

### 5.5 Re-entry
A person returning after temporary absence retains the same identity. A permanently departed person who later returns has the same identity unless a genuinely distinct person is established. Re-entry consumes capacity if the person was not already counted.

## 6. Atomic population ledger and capacity governance

### 6.1 Authoritative ledger
Maintain one population ledger derived from canonical person identity and effective-dated population-scope/life-status transitions. Cached totals are projections and must reconcile to the authoritative records.

### 6.2 Transaction contract
Every count-changing event is one atomic transaction:
- lock or serialise capacity decision;
- evaluate current authoritative count;
- validate unique person and state;
- determine count delta;
- reject if resulting count exceeds 10,000 or falls below zero;
- apply person/lifecycle/membership changes;
- append immutable population event;
- update/rebuild projections safely;
- commit as one unit.

Concurrent admissions must not both consume the same remaining capacity. The final available slot can be allocated to only one successful transaction.

### 6.3 Reconciliation
Reconciliation must detect:
- duplicate person identities;
- duplicate count contribution;
- living included person omitted from ledger;
- deceased/departed person still counted;
- police counted outside or twice within population;
- membership status inconsistent with person status;
- invalid overlapping effective dates;
- cached total different from authoritative count;
- capacity oversubscription;
- failed/partial population event.

Any mismatch blocks further count-changing operations until resolved or placed under an explicit controlled recovery process. Reconciliation must not silently delete or merge people.

### 6.4 Population reports
Provide:
- total living included count;
- opening baseline and current delta;
- headroom;
- resident/nonresident breakdown;
- police subset count;
- temporary presence count;
- births, arrivals, deaths and permanent departures over a period;
- pending/ambiguous population status;
- reconciliation exceptions.

Category counts may overlap. Reports must label this and never imply that overlapping groups sum to the total.

## 7. Demographics, life history and individual attributes

Track relevant life facts with effective dates:
- birth and age calculation;
- residence and movement;
- household and family membership;
- education participation and qualification history, including school/college/training-provider enrolment, participation/attendance, completed programmes and awarded qualifications;
- employment and occupation;
- income/financial references at proportionate depth;
- relationships and dependants;
- injury, death, medical-evidence and care-access references only where necessary, sourced, effective-dated and permission-controlled; full clinical records are not duplicated in the population profile;
- skills, routines and activities;
- significant life events;
- death/permanent departure.

Age is calculated against canonical in-game date, not the real-world clock. If the fictional clock or date of birth is unknown, exact age remains unresolved. Historical age calculations use the date relevant to the event.

A person may have multiple concurrent roles (e.g. resident, employee, student, police officer, household member). Roles are linked records; they do not create additional identities or population counts.

Person-level education history includes school, college, vocational and other non-police education participation: provider/programme references, enrolment status and effective dates, attendance/participation facts or sourced summaries, completion/withdrawal, and qualification/award references with issuer and award date where known. This is a proportionate person-life record, not a full education simulator. BP-04 owns the provider, programme/facility and service-capacity profile; BP-37 owns the canonical calendar/schedule; BP-33 owns staff employment; BP-32 owns police training and its authoritative course/credential records. Unknown or disputed history remains explicit and sourced.

## 8. Households, residence and relationships interface

BP-03 owns person identity and links to household/address/relationship records. BP-36 owns household and relationship semantics; BP-02 owns geography/address identity; BP-04 owns property and occupancy.

Required interfaces:
- person ↔ household membership;
- person ↔ address/residence history;
- person ↔ property/premises occupancy reference;
- person ↔ relationship history;
- person ↔ employment;
- person ↔ education;
- person ↔ police personnel record;
- person ↔ case/incident roles.

An address change must not rewrite family relationships. A household is not automatically identical to a property. Multiple households may share an address; a person may have a changing or complex household history. Reciprocal relationship links must be maintained where the relationship type requires reciprocity.

## 9. Employment, police personnel and institutional roles

- Every employee is an existing canonical person.
- BP-33 owns general employment, contracts, payroll, leave, attendance and separation.
- BP-04 owns business/employer identity and business premises.
- BP-06 owns police employee/personnel records and police service history.
- BP-07 owns police career progression and training gates.
- BP-08 owns unit membership, qualification eligibility and deployment assignment.
- BP-32 owns training catalogue and qualification records.
- BP-30 owns institutional appointment/authority governance.

A police employee must not be represented by a separate person identity. The approximate 500 police personnel count is a distinct role/headcount view over the same population. All police personnel count within the 10,000-person total.

Employment changes do not create new person identities. Simultaneous jobs are permitted only where schedules and attendance do not conflict or where an explicit explanation exists.

## 10. Individual simulation and processing tiers

### 10.1 Purpose
Processing tiers manage computational cost while preserving identity and continuity. They must not become different classes of person or permit deletion of facts.

### 10.2 Required tier semantics
A tiered model may distinguish:
- **Tier 0 — registry:** stable identity, life status, core population memberships and essential links.
- **Tier 1 — routine:** ordinary schedule, employment/residence, routine movements and relevant life changes.
- **Tier 2 — detailed:** richer personal history, needs, relationships, behaviour, contacts and event-level activity.
- **Tier 3 — persistent full detail:** full relevant simulation, history and future continuity for police/case-connected persons and other explicitly promoted people.

These are processing/detail policies, not separate identity types. Exact computation budgets and promotion triggers are implementation decisions under BP-35/BP-43. No tier may remove or contradict established facts.

### 10.3 Permanent promotion
Any person materially connected to police activity or a case must be promoted to persistent full-detail status for the remainder of the simulation.

Material connection includes, at minimum:
- victim, witness, suspect, offender, complainant or reporting party;
- caller or person directly involved in an incident;
- person present at, near or otherwise materially connected to a relevant event/scene;
- employee, owner, tenant, operator or person whose role/records materially affect a case;
- person interviewed, observed, surveilled, searched, arrested, detained or otherwise directly processed by police;
- person whose relationship, communication, movement, access or transaction materially affects an investigation;
- person otherwise identified by a police process as materially relevant.

Promotion must be triggered by an auditable event with reason, time, source and triggering case/incident/activity. Promotion is irreversible. A person cannot be downgraded because a case closes, a lead is rejected, the person moves away, or processing resources are constrained.

### 10.4 Promotion effects
Promotion preserves/expands detail and future processing, including relevant:
- routines and schedule;
- residence/employment history;
- relationship and contact context;
- movements and location events;
- role-specific case links;
- known/unknown information boundaries;
- source records and provenance;
- subsequent life events.

Promotion must not fabricate retroactive facts. Missing historical detail remains unknown or is reconstructed only from supported sources.

## 11. Routines, schedules and movement

BP-03 stores person routine and movement references; BP-37 owns the clock/scheduling rules; BP-02 owns the spatial network; BP-35 executes permitted events.

A routine may include:
- work/education hours;
- home and regular destinations;
- recurring activities;
- travel mode and route preferences where known;
- availability and absence;
- household/care responsibilities;
- known schedule exceptions.

Movement events must be spatially and temporally plausible. Travel duration must be supported by route/network and mode information. A person cannot be simultaneously in incompatible places without a recorded explanation, communication mechanism or valid uncertainty.

Schedules are not proof of actual attendance. Planned shift, roster, location estimate, observed movement and verified presence are distinct facts.

No routine, movement, appointment or life event progresses while simulation time is paused/absent.

## 12. Needs, behaviour, skills and finances

The person model may support needs, preferences, capabilities, habits, temperament, skills and financial context where they improve coherent simulation or police-relevant continuity.

Rules:
- Do not assign every person identical or generic traits.
- Do not infer a sensitive personal attribute without an explicit game-world basis.
- Behaviour is probabilistic/conditional only within the simulation's defined model; it is not a deterministic guilt marker.
- A personality profile is not proof of conduct.
- Financial records must link to BP-34 or relevant domain financial models; avoid duplicating account balances as competing truth.
- Health/welfare records are restricted and proportionate; BP-42 defines access.
- Skills and qualifications must have a source, level/status and validity period where relevant.
- Unknown information remains unknown.

## 13. NPC knowledge and information boundaries

Each person's knowledge must be limited by their experience, observation, role, communications and chronology. A person cannot know facts solely because those facts exist in hidden simulation state.

Store or derive, where relevant:
- observed event;
- received communication;
- source identity;
- time acquired;
- reliability/confidence;
- interpretation;
- knowledge sharing/dissemination;
- access restriction.

BP-21 owns intelligence-source grading and analytical dissemination. BP-17/BP-19 own statements/interviews. BP-42 owns permission and secret boundaries. BP-01 owns the absolute player-facing hidden-truth rule.

NPC knowledge must not reveal hidden perpetrator identities to the player through generated dialogue or indirect output before the exact `bingo` trigger.

## 14. Population activity and generation constraints

People and demographic changes must be generated only through valid causal events and approved population rules. Generation must consider:
- available population capacity;
- age/life-stage constraints;
- residence and movement;
- household relationships;
- employment/education availability;
- business and institutional staffing needs;
- schedules and location;
- existing person identity;
- prior events and continuity.

No bulk population generation may:
- exceed the 10,000 cap;
- create duplicate identities;
- produce impossible ages/statuses;
- create contradictory employment/attendance;
- assign unsupported relationships;
- create population outside the one-city boundary;
- create people that cannot be reconciled to the ledger.

The opening baseline and any later population additions require explicit seed/generation design and measured storage approval before Neon writes.

## 15. Failure and edge cases

The system must explicitly handle:
- duplicate identity candidate;
- unknown or conflicting name/DOB;
- person with multiple aliases;
- multiple simultaneous roles;
- person with multiple residences or households;
- temporary absence vs permanent departure;
- person present without resident status;
- off-map case-linked person;
- birth/arrival at full capacity;
- concurrent final-slot admissions;
- death report not yet confirmed;
- missing/uncertain date of death;
- return after departure;
- identity merge request;
- identity split/false duplicate;
- promoted person whose case closes;
- processing-tier downgrade request;
- conflicting schedules or locations;
- missing historical information;
- stale population projection;
- partial transaction or database failure;
- invalid/overlapping effective dates;
- population count mismatch.

Identity merge/split must be exceptional, reviewed, attributable and reversible where technically possible. It must preserve aliases, source IDs, references and historical links. No automated fuzzy match may merge two real individuals without an explicit confidence/decision process.

## 16. Security, privacy and permissions

BP-03 defines data categories and sensitivity labels; BP-42 defines access controls.

- Public/civic identity information, restricted personal details and highly sensitive records must be distinguishable.
- A police role does not automatically grant access to every personal record.
- Access is purpose- and role-based within the fictional world.
- Sensitive health, welfare, financial and personal details are exposed only through the relevant authority/permission.
- All restricted reads, changes, exports and disclosures are attributable.
- Hidden world truth and NPC private knowledge are not exposed to the player merely because they exist in storage.
- Credentials and system secrets are never person attributes or narrative data.

## 17. Data and event contracts

BP-03 requires the following logical record families; BP-38 determines physical schema, types, constraints, indexes and transaction implementation.

| Record family | Core content | Owner |
|---|---|---|
| Person identity | Stable ID, core identity, life status, provenance | BP-03 |
| Person attribute history | Attribute, value/claim, source, confidence, effective dates | BP-03 |
| Population membership | Person, category, inclusion status, effective interval | BP-03 |
| Population event | Event type, person, count delta, actor/source, time, transaction reference | BP-03 |
| Residence/address link | Person, canonical address, role, effective dates | BP-03 + BP-02 |
| Household membership | Person, household, role, dates | BP-36 + BP-03 link |
| Relationship link | Person pair, type, status, source, dates | BP-36 |
| Employment link | Person, employer, job, status, dates | BP-33 |
| Education participation link | Person, provider/programme reference, enrolment state, effective interval, attendance/participation references, completion/withdrawal and source | BP-03 person history; BP-04 provider; BP-37 schedule |
| Education/qualification history | Person, qualification/award reference, issuing body, award date, scope/status, evidence/source and validity where known | BP-03 person history; BP-32 owns police-training credentials |
| Police personnel link | Person, officer/personnel record, service status | BP-06 |
| Routine/schedule link | Person, routine, time window, location reference | BP-03/BP-37 |
| Movement event | Person, from/to spatial IDs, time, mode, confidence/source | BP-03/BP-02 |
| Simulation tier | Person, tier, reason, effective time | BP-03/BP-35 |
| Promotion event | Person, trigger, reason, case/incident reference, actor/time | BP-03 |
| Person knowledge item | Person, information, source, acquired time, confidence/access | BP-03/BP-21 |
| Reconciliation result | Snapshot time, counts, exceptions, resolution links | BP-03/BP-38 |

Education history events include enrolment_started/changed/suspended/withdrawn/completed; attendance_recorded/corrected; education_programme_completed; qualification_recorded/verified/corrected/revoked. Each references the canonical person, provider/programme/issuer where applicable, source, actor, effective and recorded times, status and correction lineage. These events do not create or remove a person or alter the population count.

Event contract: each population-changing event includes unique event ID, person ID, event type, prior/new population status, count delta, effective in-game time, recorded time, actor/system, reason/source, transaction outcome and related entity IDs.

## 18. Acceptance criteria and test suite

### A. Population baseline and cap
- **AC-A01:** Opening count equals exactly 9,500: 9,000 residents + 500 police.
- **AC-A02:** Headroom equals exactly 500; reserve is not counted as population.
- **AC-A03:** Maximum living population never exceeds 10,000.
- **AC-A04:** Police are included exactly once in the population total.
- **AC-A05:** Multi-role persons count once.
- **AC-A06:** Every countable person has a canonical person ID and population status.
- **AC-A07:** All defined visitor/commuter/temporary categories have explicit countability semantics.
- **AC-A08:** Population reports reconcile to unique living included person identities.

### B. Atomicity and concurrency
- **AC-B01:** Arrival/birth at capacity is rejected without partial records.
- **AC-B02:** Two concurrent admissions for one remaining slot result in at most one successful admission.
- **AC-B03:** Failed transaction leaves person, memberships, employment, residence and event ledger unchanged.
- **AC-B04:** Death/permanent departure releases capacity exactly once.
- **AC-B05:** Duplicate exit or retry does not release capacity twice.
- **AC-B06:** Ledger and projection reconcile after commit, rollback and recovery.

### C. Identity and lifecycle
- **AC-C01:** Identity remains stable across name, address, employer, role and relationship changes.
- **AC-C02:** Duplicate identity candidates do not auto-merge.
- **AC-C03:** Death preserves history and references.
- **AC-C04:** Temporary absence does not incorrectly release resident capacity.
- **AC-C05:** Permanent departure and later return follow explicit count transitions.
- **AC-C06:** Unknown/conflicting attributes remain sourced and unresolved until supported correction.
- **AC-C07:** Historical person links remain valid after status changes.
- **AC-C08:** A person-linked civil identity/life-status fact references an authoritative registration record, registrar/issuing authority, effective and recorded times, source and current validity.
- **AC-C09:** A reported event or BP-36 social relationship cannot silently create or prove a civil registration; corrections preserve prior values and provenance.

### D. Processing tiers and promotion
- **AC-D01:** Tier changes do not create/delete person identities.
- **AC-D02:** Material police/case relevance triggers persistent full-detail promotion.
- **AC-D03:** Promotion records reason, source, actor/system, time and triggering reference.
- **AC-D04:** Promoted persons cannot be downgraded, including after case closure.
- **AC-D05:** Promotion does not fabricate missing historical facts.
- **AC-D06:** Processing optimisation cannot erase established facts or history.

### E. Relationships, employment and schedules
- **AC-E01:** Person links to household, address, employer, police record and case roles resolve to the same person ID.
- **AC-E02:** Address changes do not rewrite relationships.
- **AC-E03:** Multiple roles/memberships do not duplicate population count.
- **AC-E04:** Conflicting shifts/locations are rejected or explicitly explained.
- **AC-E05:** Planned roster, attendance, observed location and verified presence remain distinct.
- **AC-E06:** Movement respects spatial topology and supported travel time.

### F. Knowledge, security and persistence
- **AC-F01:** NPC knowledge is constrained by source and acquisition chronology.
- **AC-F02:** Player-visible personal data respects BP-42 access rules.
- **AC-F03:** Hidden perpetrator information cannot leak through person profile or generated dialogue before exact `bingo`.
- **AC-F04:** Original claims and later corrections remain distinguishable.
- **AC-F05:** Every material attribute/status change is attributable and effective-dated.
- **AC-F06:** Population reconciliation identifies and reports every seeded test discrepancy.

Required test classes: boundary/cap, duplicate identity, concurrency/race, lifecycle, promotion permanence, temporal history, cross-domain references, privacy, NPC knowledge, replay, recovery, 10k-scale population, storage-growth and regression.

### Health, injury, death and care-history references
- **AC-HLTH-01:** Injury, death and care-access facts link to the canonical person ID and an attributable source/event.
- **AC-HLTH-02:** Allegation, observation, clinical finding, forensic interpretation and court finding remain distinct; no injury or cause of death is inferred from an allegation.
- **AC-HLTH-03:** Sensitive health details are stored only where necessary and protected by BP-42; the person profile holds proportionate references, not a duplicate clinical chart.
- **AC-HLTH-04:** Medical evidence and exhibit continuity link to BP-23/BP-24; BP-03 does not take over forensic interpretation.

### Education participation and qualification history
- **AC-EDU-01:** A learner is linked to one canonical BP-03 person ID; enrolment does not create a duplicate person.
- **AC-EDU-02:** School, college and non-police education enrolment records preserve provider/programme, status and effective dates.
- **AC-EDU-03:** Attendance/participation is distinct from enrolment and completion; unknown or disputed attendance remains explicit.
- **AC-EDU-04:** Education history records issuing body and award date when known and preserves unknown values rather than inventing them.
- **AC-EDU-05:** Provider/facility identity resolves to BP-04 and schedules resolve to BP-37; staff employment resolves to BP-33.
- **AC-EDU-06:** Police training course and credential authority remains with BP-32; general education history is not duplicated there.

## 19. Source traceability

| Source IDs | BP-03 obligation |
|---|---|
| C03–C06 | Opening population, reserve, hard cap and counting |
| P04–P06 | Lossless identity, stable provenance and reconciliation |
| S03.R01–R05; S03.T01–T03 | Population ledger, demographics, cap and atomicity |
| S04.R01–R03; S04.T01–T02 | Individual identity, processing tiers and permanent promotion |
| S05.R01–R03; S05.T01 | Household/relationship interfaces |
| S08.R02; S08.T01 | Work/home routines and movement |
| S12.R01 | Person-linked civil identity and life-status references; authoritative registry process is BP-30 and common register controls are BP-38 |
| S13.R02 | Person-level injury, death and care-access references, with medical evidence kept distinct from clinical/forensic owners |
| S14.R01; S14.R03; S14.T01 | Person-level education enrolment, attendance and qualification history; issuer/date/prerequisite references |
| S31.R01–R03; S31.T01 | Case-role identity and promotion |
| S39.R01–R02; S39.T01 | Person continuity through sentence/release status |
| S42.R01–R03; S42.T01 | Event processing, relevance and state consistency |
| X01–X06 | Identity, source of truth, time, reconciliation, epistemic distinctions and original records |

## 20. Closed population canon and remaining implementation decisions

Population scope and opening arithmetic are closed by [SW-CANON-001](../decisions/SW-CANON-001-population-scope-and-foundational-geography.md). There are no unresolved canon questions about residents, police, visitors, commuters, temporary presence, temporary absence, permanent departure, death or the 10,000-person cap.

The binding formula is the distinct living-person union of: usual Saltwater residents; all persons physically present inside Saltwater; and active Saltwater Police Service members. Each canonical person ID counts once. The exact opening cohorts are 9,000 civilian usual residents plus 500 active police-service personnel, for 9,500 unique people and 500 unused shared capacity. All 500 police personnel are included in the cap.

Remaining work is specification/implementation detail rather than unresolved population canon:
1. Define and test the additional person fields genuinely required by gameplay; avoid unnecessary sensitive attributes.
2. Define processing-tier budgets and permanent-promotion trigger implementation under BP-35/BP-43.
3. Define exact population event types, ledger/projection reconciliation and recovery implementation under BP-38/BP-39.
4. Generate the individual opening identities and prove count reconciliation before any production seed.
5. Test concurrent arrivals, boundary entry/exit, resident moves, police appointment/separation, death, duplicate/retried events and recovery against the adopted union formula.

These tasks do not alter the binding population scope, one-person-one-ID rule, 10,000 hard cap or permanent-promotion rule.

## SW-NAM-001 — canonical person naming integration

The first naming implementation slice attaches a `PERSON` canonical full-name reservation to the existing `sw_people.person` identity. The full display name is composed from given, optional middle and family names; given and family names are required before person creation. Person IDs remain unchanged across rename, former names remain reserved and searchable, and aliases use separate registry entries. Recruit appointment now requires a complete given/family name pair. Existing person lifecycle, population counting and player identity rules remain authoritative. This is a bounded naming adapter, not population generation or full BP-03 implementation. It passed the disposable PostgreSQL 10,000-person, naming and restore suite in run `45409845359`; final manifest-version verification also passed in run `45410340222`; a storage-only rerun is capturing heap/index/TOAST detail. No Neon write is authorised.

## 21. Completion statement

**Design status:** `DESIGNED_DRAFT`; population scope and opening arithmetic are adopted by SW-CANON-001. Individual identity generation, processing budgets, event-ledger mechanics and full acceptance testing remain.  
**Implementation status:** `NOT_STARTED` unless separately evidenced.  
**Test status:** `NOT_STARTED`.  
**Verification status:** `NOT_STARTED`.

No Neon schema, migration, seed, import, upload or database write is performed or authorised by this document.


## 20.1 Implemented BP03 service slices (2026-11-27)

The following source-only implementation slices are now present on `main`:

- `0010_bp03_population_qualification_union.sql`: distinct living-person union count, atomic 10,000-person cap, qualification history, canonical person creation and death transition.
- `0034_bp03_person_residence.sql`: effective-dated person residence linked to BP02 canonical addresses.
- `0035_bp03_household_membership.sql`: dwelling-linked household and person membership, with exact BP04↔BP02 address crosswalk.
- `0036_bp03_individual_simulation_promotion.sql`: persisted tier 0 at person creation, event-backed tier history, permanent tier-3 police-relevance promotion.
- `0037_bp03_person_routines_and_movement.sql`: effective-dated routines, explicit supersession, sourced movement with certainty/confidence and chronology checks.
- `0038_bp03_person_knowledge_boundary.sql`: source-event-bound NPC knowledge acquisition with chronology and append-only history.
- `0039_bp03_person_attribute_claims.sql`: sourced, effective-dated non-sensitive attribute claims, retaining conflicting and disputed values without silent resolution.

Focused disposable PostgreSQL acceptance for proposals 0036–0039 passed in [run 46040104903](https://github.com/Joshuaogri/saltwater/actions/runs/46040104903). The routine/movement acceptance also passed with successor-chain and current-tick checks in [run 46039460668](https://github.com/Joshuaogri/saltwater/actions/runs/46039460668). The opening police-name registry check passed in the current dedicated opening-identity workflow; the 9,000-person civilian registry check remains in progress at the time of this update.

These are source and disposable acceptance results. The 9,000 civilian and 500 police cohorts remain candidate identities; no canonical opening population or BP03 production seed has been written. Residence/household materialisation depends on BP04 production property records and canonical address crosswalks. The 500 police cohort also depends on production BP05/BP06 service structures and subsequent BP07/BP08 assignments.
