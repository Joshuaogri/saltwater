# BP-36 — Relationships and Social Context

**Project:** Saltwater  
**Division:** BP-36 of the fixed 44-division master structure  
**Version:** 1.0  
**Specification status:** DESIGNED_DRAFT — review/approval pending  
**Implementation / test execution / verification:** NOT_STARTED  
**Authority:** Saltwater master blueprint, original 52-division source and authoritative 52→44 crosswalk.  
**Database status:** This specification authorises no Neon schema, migration, seed, import or other database write.

## 1. Purpose

BP-36 defines the canonical social-context and relationship domain that connects Saltwater's people, households, families, partners, dependants, friends, neighbours, colleagues, professional contacts, community groups, organisations and social networks. It represents the meaningful social structures through which people live, communicate, cooperate, depend on one another, disagree, provide care, gather, form communities and interact with public institutions.

Its purpose is to make the city socially coherent and causally alive without turning every relationship into a simplistic score or assuming that a recorded connection proves affection, trust, guilt, knowledge, consent, financial dependency or current contact. Relationships are contextual, potentially asymmetric, time-bounded, changing and sometimes disputed. The system must preserve their history and distinguish a person's own understanding from an independently verified fact.

BP-36 supplies relationship meaning and social context to other divisions. It does not own person identity, business identity, employment, case roles, police authority, legal status, service delivery, event scheduling or simulation execution. It supplies structured records and validated events to their authoritative owners.

## 2. Scope and exclusions

### 2.1 BP-36 owns

- Household membership and household history, including shared living arrangements and household composition.
- Family and kinship relationships, including biological, adoptive, legal, step, foster, chosen and culturally configured kinship categories.
- Partner and intimate relationship status as configured, including current, former, separated, disputed and unconfirmed states.
- Friendship, acquaintance, neighbour, colleague, professional, community, mentor, adversarial and other interpersonal relationship categories.
- Dependency and care relationships, including who provides or receives practical, financial, emotional or other support, with type and scope explicitly distinguished.
- Social-network membership, network structure, group affiliation and membership lifecycle.
- Community, voluntary, cultural, recreational and civic associations as social memberships, while BP-04 owns the organisation's canonical identity and BP-30 its public governance.
- Relationship assertions, sources, confidence, verification, dispute, consent and access restrictions.
- Relationship and household lifecycle, effective dates, history, separation, dissolution, reconciliation, transition and correction.
- Social-context facts such as shared routines, contact patterns, social proximity, known affiliations and support networks, where sourced and appropriately classified.
- Social effects and relationship-change requests, including grief, conflict, support, isolation, community participation and trust effects, only where supported by causal source events.
- Cross-domain relationship references and safe query contracts.
- Relationship-specific privacy, confidentiality, safeguarding and visibility metadata, subject to BP-42 security policy.
- Social-context contribution to NPC behaviour and narrative, with strict person-specific knowledge boundaries.
- Relationship and household integrity checks, historical traceability and acceptance-test contracts.

### 2.2 BP-36 does not own

- Person identity, legal identity, life status, population ledger, person attributes or canonical person lifecycle (BP-03).
- Business, employer, premises, organisation or institution identity (BP-04).
- Employment contracts, attendance, payroll, leave, disciplinary or job assignment records (BP-33); BP-36 may represent colleague relationships and social context.
- Police rank, authority, command, personnel dossier, career, roster, unit or deployment (BP-05–BP-08).
- Victim, witness, suspect, offender, complainant or other case-specific procedural roles (BP-17, BP-18, BP-31 and relevant case divisions). A social relationship must never determine guilt or procedural status.
- Investigation, intelligence, surveillance, interview, evidence, legal or court findings (BP-16, BP-19–BP-28). These divisions own their records and access controls.
- Social care provider identity or service delivery (BP-04 and relevant service owner); BP-36 may record a person's social/care relationship to another person or service.
- Public complaint adjudication, oversight or remedies (BP-30/BP-31).
- Canonical simulation time, calendar, deadline or schedule calculation (BP-37).
- Runtime execution, NPC action scheduling or causal event processing (BP-35).
- Authoritative record schemas, database transactions, persistence, backup and recovery (BP-38/BP-39).
- User interface, notifications, permissions or configuration governance (BP-40–BP-44).

### 2.3 Core boundary

BP-36 answers: **what social relationship or social membership is recorded, between whom, of what kind, according to which source, for what period, with what confidence and visibility?**

It does not answer: whether a person is guilty, whether an allegation is true, whether a relationship caused a crime, whether a person consented to an act, whether a household member knows another person's secret, or whether a relationship grants legal authority.

## 3. Binding Saltwater canon

1. Saltwater is one fictional sovereign city-state, one city and one jurisdiction. No second playable city or external territory may be created.
2. The total living population has a hard cap of **10,000 people**. Each person is counted once by BP-03, regardless of household, family, social-group, employment, police, community or other role.
3. The binding opening population is 9,000 residents + 500 police = 9,500 living people. The remaining 500 is unused capacity headroom, not a separate population. The hard cap is 10,000 living people total. BP-03 owns the sole population ledger, identity and counting rules; BP-36 owns household and relationship semantics and must not create a separate population count.
4. At least 10,000 businesses remain registered under BP-04. Social groups and memberships must not create duplicate business or organisation identities.
5. Police is the deepest simulated institution. Social context must support policing, investigations and city life without expanding into a separate all-institutions deep simulation.
6. Every person has one stable BP-03 identity. A person may hold multiple relationships, household memberships over time, group memberships and case roles without becoming multiple people.
7. Any person materially relevant to a case or police activity is promoted by the population/simulation architecture to full persistent simulation and is never downgraded. BP-36 must preserve the relationship history and references needed for that person's ongoing record.
8. Text is the permanent primary interface. Social context must remain fully inspectable in text. Visual network graphs and family diagrams are optional projections only.
9. No simulation time or social activity advances while the player is absent or the simulation is paused. No unseen relationship change, household move, meeting, argument, reconciliation, bereavement, birth, departure, message, social event or NPC reaction occurs offscreen.
10. All person knowledge is individual and source-bounded. A recorded relationship does not mean either person knows all facts held by the other.
11. Exact `bingo` hidden-truth protection remains binding. Social links, family ties, conflicts, group memberships and network patterns must never leak a hidden culprit or accomplice.
12. Player agency is preserved. The engine does not choose social/investigative actions for the player or provide unsolicited investigative hints.
13. Storage compression may reduce representation overhead but never remove relationship meaning, history, source, confidence, dispute, consent, access restrictions or provenance.

## 4. Conceptual model and terminology

### 4.1 Person

A person is a canonical BP-03 entity. BP-36 stores only the person reference and relationship-specific information. It must not copy a person's full name, date of birth, address, biography or life status into a second authoritative identity record.

### 4.2 Relationship

A relationship is a typed, sourced and time-aware association between two or more canonical entities. Most interpersonal relationships are between two people, but some relationships connect a person to a household, group, organisation or community.

A relationship record must distinguish:
- the underlying asserted relationship category;
- the parties and their roles within it;
- whether it is reciprocal, directed or multi-party;
- who asserted or recorded it;
- whether it is verified, unverified, disputed, inferred or historical;
- when it is believed to have been effective;
- when the system learned or recorded it;
- whether it is current, ended, suspended or superseded;
- what each participant is permitted to know;
- who may access the record and for what purpose.

### 4.3 Household

A household is a social/living arrangement, not necessarily a family. It may include unrelated housemates, partners, dependants, carers, lodgers or temporary members. Household membership does not prove property ownership, tenancy, legal guardianship, financial dependency or relationship status.

A household has its own stable BP-36 ID and lifecycle. Its address/premises reference resolves through BP-02/BP-04. It must not create a new person or property identity.

### 4.4 Family and kinship

Kinship represents an asserted or verified family relationship with an explicit category and basis. Biological, adoptive, legal, step, foster, chosen and culturally configured categories must remain distinguishable. A family relationship may be known, unknown, disputed, confidential or not publicly acknowledged. Kinship is not automatically a household membership or a source of legal authority.

### 4.5 Social group and network

A social group is a bounded collection of people associated by a shared activity, identity, purpose, interest, community, occupation, institution or other configured basis. A network is a set of linked entities and relationships that can be queried as a projection. A network is not itself proof of coordination, conspiracy, criminal association or shared knowledge.

### 4.6 Assertion, observation and fact

An assertion records that a source claims a relationship exists or existed. An observation records something directly perceived, such as two people meeting or sharing an address. A verified relationship is one that has met an explicitly configured verification standard. None of these automatically establishes another category. A shared address does not prove a family tie; frequent contact does not prove intimacy; a witness's claim does not become objective truth merely because it is stored.

### 4.7 Social context

Social context is a sourced, time-bounded description of the circumstances surrounding a person or group: household arrangements, support, community participation, routine contacts, known affiliations, isolation, conflict or dependency. It must not be reduced to a single global reputation, trust or risk score.

## 5. Entity catalogue

All identifiers are stable, unique and non-semantic. Names and sensitive details are resolved from authoritative source records when needed.

### 5.1 Relationship record

Minimum fields:
- `relationship_id`
- `relationship_type_code`
- `party_refs[]` with explicit party roles
- `directionality` (reciprocal, directed, multi-party)
- `status` (asserted, active, disputed, suspended, ended, superseded, rejected)
- `verification_state`
- `basis_code` and optional explanatory reference
- `valid_from_sim`, `valid_to_sim` where known
- `recorded_at_sim`, `recorded_by`
- `source_type`, `source_ref`, `source_quality`
- `confidence` or uncertainty descriptor
- `consent_state` where relevant and lawfully captured
- `visibility_class`, `safeguarding_flags`
- `supersedes_ref`, `correction_ref`
- `created_event_ref`, `last_transition_event_ref`

### 5.2 Household record

Minimum fields:
- `household_id`
- `household_type`
- `status`
- `premises_ref` or explicit no-fixed-address/temporary basis
- `member_refs[]` through separate membership records
- `formation_date`, `dissolution_date` where known
- `household_source_ref`
- `privacy/visibility class`
- `responsible_contact_ref` only where a defined purpose exists
- `history/version reference`

### 5.3 Household membership

A separate membership entity records person-to-household association:
- `membership_id`, `household_id`, `person_id`
- `member_role` (adult, child, dependant, lodger, housemate, carer, temporary resident, other configured role)
- `status`, `valid_from_sim`, `valid_to_sim`
- `basis/source`, confidence and verification
- `recorded_at_sim`, actor and provenance
- restrictions, safeguarding and confidentiality metadata.

A person may have multiple sequential memberships and, where explicitly valid, overlapping arrangements. Conflicts are flagged, not silently normalised.

### 5.4 Social group

Fields:
- `group_id`, `group_type`, `canonical_org_ref` where the group is part of an organisation
- `display_label_ref` or configured name
- `purpose/category`, `status`, `formation/dissolution` timestamps
- `membership_policy`, `visibility`, `source/provenance`
- `parent_group_ref` where nested groups are supported.

BP-36 must not duplicate the BP-04 organisation record. Informal groups may have a BP-36 group identity where no formal organisation exists.

### 5.5 Group membership

Fields:
- `group_membership_id`, `group_id`, `member_ref`
- `member_role`, `membership_status`
- `valid_from_sim`, `valid_to_sim`
- `source_ref`, `verification_state`, `visibility_class`
- `recorded_by`, transition event references.

Membership may be individual, household-based or organisation-based if the group rules permit it. Each membership type must identify the actual member entity.

### 5.6 Relationship assertion/source

An assertion record captures a source's claim without prematurely promoting it to verified truth:
- asserting actor/source;
- subject and related party references;
- asserted relationship type and claimed period;
- acquisition/recorded time;
- source reliability and content credibility kept distinct;
- confidence, contradiction and corroboration references;
- verification decision, reviewer and rationale;
- confidentiality, consent and access basis.

### 5.7 Social event/context record

A social event may describe a meeting, gathering, household change, support action, group activity, conflict, separation, reconciliation or other relevant event. It records event source, participants, location/time references, observed versus reported details, confidence and visibility. BP-35/BP-37 coordinate execution/time; BP-36 owns the relationship-context record only where it changes or describes a social relationship.

### 5.8 Support/dependency link

A support link identifies who provides and who receives a specified type of support, its scope, frequency, period, evidence/source and whether the arrangement is voluntary, formal, informal, disputed or unknown. Financial support is not a bank transaction or payroll record; care delivery remains with the relevant service owner.

### 5.9 Contact pattern

A contact pattern is an aggregate or sourced description of interaction frequency/channel/period, not a complete copy of call, message or surveillance records. It must reference source records and preserve coverage gaps. It cannot infer relationship category or guilt automatically.

### 5.10 Relationship correction/audit event

Every creation, verification, dispute, correction, status transition, access restriction, merge or closure is recorded as an attributable immutable event. Corrections supersede prior assertions; they do not erase history.

## 6. Relationship taxonomy

The taxonomy is configurable under BP-44 and versioned. Initial categories should include:

- **Kinship:** parent/child, sibling, grandparent/grandchild, aunt/uncle, niece/nephew, cousin, spouse by configured status, adoptive, step, foster, chosen kin and other culturally appropriate categories.
- **Partner:** spouse, civil/domestic partner where configured, current partner, former partner, separated partner, co-parent, unconfirmed partner assertion.
- **Household:** co-resident, housemate, lodger, dependant, carer, temporary household member.
- **Friendship/social:** close friend, friend, acquaintance, neighbour, social contact, former friend, estranged contact.
- **Professional:** colleague, supervisor/subordinate as social/professional link only, mentor/mentee, client/provider, business associate, professional contact.
- **Care/support:** caregiver, care recipient, guardian/ward assertion, financial supporter/dependent, practical support, emergency contact.
- **Community/group:** member, organiser, volunteer, participant, leader, representative, former member.
- **Conflict/adversarial:** dispute, estrangement, rivalry, hostility, threatened relationship, known adversarial association.
- **Other configured:** any approved type with explicit meaning, directionality, evidence standard, privacy class and lifecycle.

Taxonomy rules:
1. No relationship category may itself encode criminal guilt or legal culpability.
2. A professional hierarchy is not proof of friendship, coercion or misconduct.
3. A relationship may have multiple independent dimensions, e.g. former partner and current co-parent.
4. Contradictory assertions may coexist with separate sources and confidence.
5. The system must not infer a sensitive relationship type from appearance, proximity, shared surname, address, contact frequency or group co-presence alone.
6. Relationship category changes are versioned and historically traceable.

## 7. Relationship lifecycle and state transitions

### 7.1 Standard lifecycle

`Proposed/Asserted → Recorded → UnderReview → Verified/Unverified/Disputed → Active/Inactive/Historical → Ended/Superseded`

Not every relationship passes through every state. A source assertion can remain unverified indefinitely. A relationship may be active while disputed, if the dispute concerns its type or scope rather than whether any contact exists. A historical relationship remains queryable under permissions.

### 7.2 Creation

A relationship may be created from:
- explicit player entry or authorised administrative action;
- a person's own statement;
- a third-party report;
- a verified civil or organisational record where configured;
- a case record or investigative observation;
- a social event or domain event;
- a generated world event authorised by BP-14/BP-35.

The source and basis are mandatory. Creation of an assertion is not verification.

### 7.3 Verification

Verification requires a defined evidence/basis standard and an attributable decision. A reviewer records what sources were considered, limitations, contradictions and rationale. A verified status can be withdrawn or narrowed through a new event if later evidence undermines it. No source is treated as universally authoritative for all relationship dimensions.

### 7.4 Dispute

A participant or authorised source may dispute a relationship's existence, type, dates, consent, scope or current status. The system preserves both the disputed claim and the dispute. A dispute does not automatically delete or suspend every related fact. Safeguarding or confidentiality restrictions may be applied where appropriate.

### 7.5 Ending and change

Relationships may end through separation, dissolution, death, departure, loss of contact, group departure, changed role or correction. The reason may be known, private, disputed or not recorded. Ending a relationship does not erase its historical existence or remove linked case, household or social-event records.

### 7.6 Correction

A mistaken relationship must be corrected through a superseding record with source, actor, reason and effective period. The original remains auditable but is marked corrected/superseded. A correction must propagate to derived projections and affected consumers without rewriting their source histories.

## 8. Household lifecycle and composition

Households are created, occupied, changed, split, merged or dissolved through explicit events. A household may exist without a conventional family structure. Household membership is separate from property ownership, tenancy, residence registration, employment, guardianship and financial account ownership.

Rules:
- Every member is a BP-03 person reference.
- A household can reference a BP-04 premises record or a configured temporary/no-fixed-address state.
- Household formation requires a valid source and effective date.
- Membership additions/removals have separate effective dates and actors.
- A person leaving a household remains a person and retains prior membership history.
- A household may split into successor households; lineage is recorded.
- A household may merge with another; prior household IDs remain historical.
- Household dissolution does not delete its members or relationships.
- A person may be part of a household without being related to every other member.
- Household role labels do not grant legal guardianship, authority, consent or access.
- Conflicting occupancy and tenancy are referred to BP-04; BP-36 does not decide property rights.
- Multiple or overlapping household memberships are permitted only under explicit configured semantics; suspicious or contradictory periods are flagged for review.
- Temporary shelter, institutional accommodation, shared housing, no-fixed-address and transient arrangements can be represented without inventing a permanent home.

## 9. Family, partners and care relationships

### 9.1 Family and kinship

Kinship records retain type, basis, source, confidence, effective period and confidentiality. Biological relation, legal relation, adoptive relation, social/chosen kinship and asserted relation are separate categories. A family tree is a projection, not the authoritative data structure.

### 9.2 Partner relationships

Partner records may include status, start/end dates, co-parenting links, shared household references and relevant safeguarding restrictions. The system must support disputed, undisclosed, former and separated relationships. Marriage or civil status is only recorded from an authoritative configured source; it is not inferred from cohabitation or self-presentation alone.

### 9.3 Care and dependency

A care/support relationship identifies roles and scope without assuming legal authority. Guardianship, parental responsibility, power of attorney or other legal authority must be sourced from the relevant configured legal/civil record and is not conferred by a social label. A dependant may receive support from multiple people; one provider may support multiple dependants.

### 9.4 Vulnerability and safeguarding

Sensitive safeguarding facts are stored only when necessary, sourced and permissioned. BP-36 may record that a support or relationship context exists, but specialist safeguarding assessments and service plans remain with their owning domain. The system must not label a person as vulnerable merely because they are elderly, disabled, a child, isolated or dependent; use specific, sourced needs and avoid unsupported inference.

## 10. Social groups, communities and civic participation

BP-36 supports informal and formal social group membership: neighbourhood groups, sports clubs, cultural associations, faith communities, charities, volunteer groups, hobby groups, professional associations, campaign groups, social circles and other configured entities.

- Formal organisation identity and premises are owned by BP-04.
- BP-36 stores the person's membership relationship, not a duplicate organisation profile.
- Public governance and official appointments are owned by BP-30 or the relevant institution.
- Group membership may be public, private, confidential, disputed or unknown.
- Membership may be active, prospective, suspended, honorary, former or ended.
- A person can belong to multiple groups, including groups with overlapping or conflicting purposes.
- Group leadership/office is a role with its own source and effective dates; it does not imply authority outside the group.
- Group events have time/place/organiser/attendance references and are scheduled through BP-35/BP-37.
- Attendance at an event does not prove membership, affiliation, endorsement or agreement.
- A group or network cannot be classified as criminal solely because a member is a suspect or offender.
- Membership alone is not evidence of knowledge of another member's conduct.
- Group membership privacy and risk of retaliation are respected through BP-42.

## 11. Social context, trust and reputation

The system must represent social context as a set of attributable dimensions rather than a single hidden score.

Possible context dimensions include:
- support availability and support gaps;
- social isolation or frequency of contact, when sourced;
- household stability or transition;
- community participation;
- known disputes and conflict history;
- trust asserted by a specific person toward another;
- cooperation or refusal in a defined interaction;
- dependency and caregiving burden;
- shared routines and social proximity;
- group participation and civic involvement.

Trust is subjective and directional. Person A may trust Person B while Person B does not trust Person A. Trust can vary by subject, time, context and source. It must not be represented as universal objective truth.

Reputation is an aggregation of sourced perceptions, not a fact about moral character. A negative report, criminal allegation, arrest or conviction must not automatically rewrite all social relationships or a person's general reputation. Any aggregate must expose its sources, coverage, age, uncertainty and limitations.

No relationship or social-context metric may automatically:
- classify a person as a criminal or suspect;
- generate an arrest ground;
- establish motive, opportunity or knowledge;
- prove collusion or conspiracy;
- alter a court finding;
- assign guilt to relatives, partners, colleagues or group members;
- determine the player's next investigative action.

## 12. Contact patterns and social events

Contact patterns may be sourced from direct statements, records held by other domains, observed meetings, event attendance or explicit social interactions. BP-36 stores a minimal summary and references the source record; it does not duplicate call logs, messages, CCTV, surveillance, interview transcripts or financial transactions.

A social event record distinguishes:
- planned versus actually occurred;
- observed versus reported attendance;
- named versus unidentified participants;
- direct observation versus inference;
- exact versus estimated time;
- precise versus approximate location;
- public versus private event;
- source coverage and gaps.

Meeting two people at the same place/time does not establish they met each other. Shared attendance does not establish conversation, agreement or knowledge. Repeated contact may be a clue for player interpretation only when surfaced as a factual, sourced observation; BP-36 must not turn it into an unsolicited investigative hint.

## 13. Causality and social change

Relationship changes are caused by attributable events, not arbitrary score fluctuations. Examples include household move, marriage or separation record, birth/death/life event, employment change, group joining/leaving, observed conflict, support action, public gathering, service referral or explicit statement.

BP-35 coordinates execution and cross-domain event delivery. BP-37 supplies canonical time. BP-36 validates whether the event changes a relationship record and emits a new relationship event. The source domain retains its own record.

Causal rules:
1. A causal event must identify its source and effective simulation time.
2. A relationship change must not be backdated without explicit historical correction authority and provenance.
3. Multiple effects from one event must be traceable to the initiating event.
4. Contradictory inputs remain visible as conflicting assertions until resolved.
5. An event cannot create a legal, family or household status that its source does not establish.
6. No relationship changes while paused or absent.
7. Generated events must respect prior history, geography, availability and actor knowledge.
8. The engine cannot force a relationship change solely to make a story more dramatic.
9. A person's death or permanent departure is handled by BP-03; BP-36 closes or updates relationships through linked lifecycle events without changing the person's canonical life status.
10. A case event may create a case-specific association in its owning domain; it does not automatically create a social relationship.

## 14. NPC behaviour and individual knowledge

BP-35 activates NPCs and coordinates action proposals. BP-36 supplies only the social context that a particular person knows or is authorised to access.

For each NPC, distinguish:
- objective relationship records held by BP-36;
- the person's own asserted view of a relationship;
- facts the person directly observed;
- information told to the person and by whom;
- inferences the person may reasonably make;
- rumours or disputed claims;
- facts the person does not know.

A parent, spouse, friend, colleague or housemate is not automatically aware of another person's movements, phone calls, work, finances, secrets, criminal activity, case involvement or thoughts. Shared household membership does not grant unrestricted access to each other's records.

NPC dialogue may express personal uncertainty, bias, affection, hostility or mistaken belief, but must be attributable to that NPC's knowledge and perspective. A generated line cannot silently turn an NPC belief into objective relationship truth.

The player may ask an NPC about a relationship. The NPC response must reflect their knowledge, willingness, memory, context and authority. The engine must not supply a perfect answer merely because BP-36 has a record.

## 15. Case and policing interfaces

BP-36 supplies social context only when requested and authorised by the case/police owner.

- BP-15/BP-16 own case and investigation records; BP-36 provides relevant relationship references, not investigative conclusions.
- BP-17 owns victim/witness roles and safeguarding in case procedure; BP-36 may supply household/support context with appropriate access controls.
- BP-18 owns suspect/offender roles; relationship to a victim, witness or co-suspect does not establish guilt or complicity.
- BP-19 owns interviews and statements; BP-36 may link a statement's asserted relationship without rewriting the interview.
- BP-20 owns surveillance records; observed contact is referenced, not duplicated or upgraded to relationship truth.
- BP-21 owns intelligence reports and analytical products; BP-36 does not convert network connections into intelligence conclusions.
- BP-23/BP-24 own evidence and forensic records; social context cannot substitute for evidential proof.
- BP-25–BP-29 own arrest, custody, legal process, court and corrections records.
- BP-30/BP-31 own governance, complaints and standards processes.
- Police access to sensitive relationship records must have an explicit permission and purpose basis under BP-42.
- A relationship query must return the status, source, confidence, effective period, dispute and access restrictions needed to interpret it correctly.
- The interface must distinguish no recorded relationship from evidence that no relationship exists.
- Missing, inaccessible, unverified and disproven records are separate outcomes.

## 16. Privacy, consent, safeguarding and access

BP-42 owns the permission model. BP-36 provides record-level visibility, confidentiality and safeguarding metadata.

Rules:
- Collect and expose only relationship detail necessary for the declared purpose.
- Distinguish public, restricted, confidential, highly sensitive and protected relationship data.
- Do not expose confidential partner, family, care, group or safeguarding information merely because a user has a social connection to the subject.
- Consent is specific to purpose and scope; it is not assumed from a relationship.
- A person's refusal to disclose a relationship does not prove it does not exist.
- A third-party assertion must not be presented as the subject's own statement.
- Sensitive records must support restricted existence indicators where revealing even the record's presence would create risk.
- Safeguarding restrictions can limit disclosure without altering source truth.
- Access, query, export, correction and disclosure actions are auditable.
- No AI context or optional visual projection may bypass permission filtering.
- A person's household membership does not authorise access to another member's private records.
- Where conflicting rights or safety needs arise, preserve the record and refer the access decision to the authorised BP-42 policy/role; do not invent a legal rule.

## 17. Data integrity and invariants

1. Every person reference resolves to exactly one BP-03 person ID.
2. No BP-36 record creates a person or changes the population ledger.
3. Household and group IDs are unique and stable.
4. Relationship parties are valid canonical references with declared entity types.
5. Relationship type, directionality and party roles are compatible.
6. Reciprocal relationship projections derive from one canonical record or linked reciprocal assertions; they are not duplicated as independent facts without provenance.
7. Historical periods are internally valid; end time cannot precede start time.
8. Overlapping relationships are permitted only where taxonomy semantics allow them.
9. Conflicting assertions remain separately sourced and visible.
10. Every verification or correction decision has an actor, source, timestamp and rationale.
11. Every relationship change is attributable and append-only.
12. No record is deleted to hide a former relationship or prior error.
13. A person leaving a household/group does not lose historical membership.
14. Household membership does not imply kinship, tenancy, ownership or guardianship.
15. Group membership does not imply knowledge, agreement or criminal association.
16. Contact frequency does not automatically establish relationship type.
17. Social context does not establish guilt, motive, opportunity or legal authority.
18. Access restrictions are applied before rendering or context assembly.
19. All social activity is frozen when simulation is paused or player absent.
20. Population cap and permanent-promotion rules remain controlled by BP-03/BP-35.
21. No relationship event is committed with a non-canonical simulation timestamp.
22. Corrections preserve source and supersession lineage.
23. Derived network graphs are reproducible from canonical records and never become independent truth.
24. Storage compaction preserves every material assertion, transition, source and restriction.

## 18. Inputs and outputs

### Inputs

- Canonical person IDs and lifecycle events from BP-03.
- Household premises, property and organisation references from BP-02/BP-04.
- Employment, role and separation references from BP-33 and police personnel domains.
- Social/civic organisation identities and event references from BP-04/BP-30.
- Case-related participant and safeguarding references from BP-15–BP-18 and BP-31.
- Observations, interview statements, surveillance references and intelligence references from their owning divisions.
- Canonical simulation time and event timestamps from BP-37.
- Runtime event delivery, causation and pause gate from BP-35.
- Permission decisions, confidentiality and safeguarding rules from BP-42.
- Versioned taxonomy and policy configuration from BP-44.
- Schema validation and durable transaction/persistence services from BP-38/BP-39.

### Outputs

- Relationship, household, kinship, support and group membership records.
- Assertions, verification decisions, disputes, corrections and lifecycle events.
- Social context query results with source, confidence, time and visibility.
- Relationship change events and causal links for BP-35.
- NPC-specific permitted knowledge/context references.
- Case/police social-context references for authorised consumers.
- Integrity exceptions, conflict flags and audit records.
- Optional derived household/family/network projections.
- Reports and notifications requested by BP-41 through authorised interfaces.

## 19. State and event contracts

Each BP-36 command/event declares:
- event ID and schema version;
- actor/source and permission context;
- affected relationship/household/group IDs;
- person/entity references;
- relationship type and party roles;
- effective and recorded simulation times;
- source and verification state;
- confidence/uncertainty and dispute details;
- visibility/safeguarding metadata;
- causation/correlation references;
- idempotency key;
- expected current version or precondition;
- result state and audit reference.

Commands include create assertion, verify, dispute, correct, end, suspend, reinstate, create household, add/remove member, split/merge household, create group, add/remove member, create support link, record social event, restrict access and query social context.

Events include relationship asserted, verified, disputed, corrected, changed, ended; household formed, member joined/left, household split/merged/dissolved; group formed, membership changed, support started/ended; social event recorded; access restriction changed.

A command is not an event until accepted and committed. Duplicate commands are idempotent. Stale-version commands are rejected as conflicts. No domain side effect is inferred from a presentation-only narrative.

## 20. Failure handling and recovery

- Invalid person/entity reference: reject without partial relationship mutation.
- Missing source for a factual assertion: reject or store only as explicitly unsubstantiated user note under configured policy.
- Conflicting date/type: retain separate assertions and create a review conflict; do not overwrite.
- Duplicate membership or event: return existing result under idempotency key.
- Permission denied: deny and audit without disclosing protected record details.
- BP-03 person lifecycle unavailable: hold or reject relationship mutation; never create a substitute person.
- BP-04 premises/org reference unavailable: retain explicit unresolved reference only if the source policy permits; do not invent an address or organisation.
- BP-35 paused: no relationship event execution; incoming commands remain pending or read-only.
- BP-37 time unavailable: reject/hold time-sensitive mutation.
- Persistence failure: do not acknowledge commit; preserve retry/idempotency information.
- Recovery: reconcile event and record versions, restore append-only history and preserve the paused simulation watermark.
- Replay: use original accepted inputs and recorded source versions; do not regenerate social events or NPC beliefs from a newer model.
- Any integrity failure that could corrupt person identity, household history, access restrictions or case-relevant provenance blocks affected writes.

## 21. Storage, performance and projections

The system must support up to 10,000 living people and many relationship edges without creating an unbounded dense graph or duplicating person records.

- Use compact stable IDs and versioned relationship type codes.
- Store each canonical relationship once where possible; use party-role rows/references for multi-party relationships.
- Store lifecycle transitions as append-only events or equivalent immutable history.
- Keep source details in their authoritative domain; BP-36 stores references and minimal necessary metadata.
- Index person ID, relationship type, status, effective period, household/group ID, source and visibility class.
- Query adjacency for a person without scanning the full city graph.
- Build family trees, household views, network graphs and contact summaries as derived projections with source watermarks.
- Cache only with explicit invalidation/version rules.
- Avoid global all-pairs relationship generation.
- Do not assume every pair of people has a relationship record.
- Use aggregate contact patterns only when coverage and precision are labelled; do not invent individual interactions from aggregate counts.
- Preserve all material relationships and source history for permanently promoted persons.
- Archive only under BP-38/BP-39 policy, retaining provenance and queryability.
- Benchmark high-degree social nodes, large households, group membership churn, network traversal and case-context queries.
- Any future Neon write requires baseline measurement, incremental byte/MiB estimate with assumptions and uncertainty, explicit user approval, and post-write size measurement. This document authorises none.

## 22. Acceptance tests

These are design criteria, not evidence that tests have been executed. Fixtures are fictional. Tests must not write to production Neon.

- AT-001: Every relationship party resolves to a canonical BP-03 person or explicitly permitted entity reference.
- AT-002: Creating a relationship does not create a new person.
- AT-003: A person has one canonical identity across all household and social roles.
- AT-004: Relationship IDs remain stable across type/status changes.
- AT-005: Duplicate relationship command with same idempotency key creates one record.
- AT-006: A relationship assertion records its source and asserting actor.
- AT-007: An assertion is not automatically marked verified.
- AT-008: Verification requires a configured basis and attributable reviewer.
- AT-009: Verification records rationale and considered sources.
- AT-010: A disputed relationship retains both original assertion and dispute.
- AT-011: Conflicting assertions from two sources coexist without silent overwrite.
- AT-012: A relationship can be unverified indefinitely without invented resolution.
- AT-013: Correction supersedes rather than deletes the original record.
- AT-014: Correction retains actor, reason, source and effective period.
- AT-015: Historical relationship remains queryable subject to permissions.
- AT-016: Ended relationship is not represented as current.
- AT-017: End date cannot precede effective start date.
- AT-018: Unknown start/end dates remain unknown rather than guessed.
- AT-019: Relationship status and verification status are separate fields.
- AT-020: Relationship directionality is explicit.
- AT-021: Reciprocal projection derives from canonical source without duplicate contradictory truth.
- AT-022: Directed trust from person A to B does not imply B trusts A.
- AT-023: Multi-party relationships identify each party's role.
- AT-024: Multiple relationship dimensions between the same people are supported.
- AT-025: A former partner relationship can coexist with a current co-parent relationship.
- AT-026: Relationship taxonomy is versioned and configuration-controlled.
- AT-027: Unsupported relationship type is rejected or held for configuration review.
- AT-028: Relationship category cannot encode criminal guilt.
- AT-029: Shared surname alone does not create kinship.
- AT-030: Shared address alone does not create family relationship.
- AT-031: Frequent contact alone does not establish intimacy or partnership.
- AT-032: Shared group attendance does not establish membership.
- AT-033: Co-presence does not prove a meeting or conversation.
- AT-034: Relationship status is not inferred from appearance or demographic similarity.
- AT-035: A professional reporting line does not automatically create friendship or coercion.
- AT-036: A relationship record does not confer legal authority or consent.
- AT-037: Biological, legal, adoptive, step, foster and chosen kinship remain distinct.
- AT-038: Kinship basis and confidence are retained.
- AT-039: Confidential kinship can be restricted from ordinary household views.
- AT-040: Family tree is a projection and does not become independent canonical truth.
- AT-041: Partner relationship supports current, former, separated, disputed and unconfirmed states.
- AT-042: Cohabitation does not automatically create marriage or civil status.
- AT-043: Marriage/civil status requires configured authoritative source.
- AT-044: Former partner status remains historically traceable.
- AT-045: Relationship end does not erase shared child/co-parenting links.
- AT-046: Household ID is unique and stable.
- AT-047: Household is distinct from family.
- AT-048: Household membership is a separate entity with its own ID.
- AT-049: Household member resolves to one BP-03 person.
- AT-050: Household may contain unrelated housemates.
- AT-051: Household may include dependants, carers, lodgers or temporary members.
- AT-052: Household formation records source and effective date.
- AT-053: Household premises reference resolves through BP-02/BP-04 or explicit no-fixed-address state.
- AT-054: Household membership does not imply property ownership.
- AT-055: Household membership does not imply tenancy.
- AT-056: Household membership does not imply legal guardianship.
- AT-057: Household membership does not imply financial dependency.
- AT-058: Adding a member records actor, source and effective time.
- AT-059: Removing a member preserves historical membership.
- AT-060: A person leaving a household retains identity and relationship history.
- AT-061: Household dissolution does not delete members.
- AT-062: Household split creates successor IDs and lineage.
- AT-063: Household merge preserves both predecessor records.
- AT-064: Overlapping memberships are accepted only under configured semantics.
- AT-065: Conflicting household periods are flagged, not silently normalised.
- AT-066: Temporary accommodation can be represented without inventing a permanent home.
- AT-067: No-fixed-address state does not create a fictional premises record.
- AT-068: Household responsible-contact label does not confer legal authority.
- AT-069: Household membership does not grant access to another member's private data.
- AT-070: Group ID is unique and stable.
- AT-071: Formal group references BP-04 organisation rather than duplicating it.
- AT-072: Informal social group can exist without a formal organisation record.
- AT-073: Group membership records member entity type and role.
- AT-074: Membership supports prospective, active, suspended, former and ended states.
- AT-075: Membership start/end periods are validated.
- AT-076: Group leadership role has source and effective dates.
- AT-077: Group leadership grants no authority outside the group.
- AT-078: A person may belong to multiple groups.
- AT-079: Group membership can be confidential or restricted.
- AT-080: Group event attendance does not prove endorsement or agreement.
- AT-081: Group membership does not prove knowledge of another member's actions.
- AT-082: A suspect's group membership does not classify the group as criminal.
- AT-083: Group membership history survives departure.
- AT-084: Group dissolution preserves historic membership.
- AT-085: Nested group references cannot create cycles unless explicitly supported.
- AT-086: Support link identifies provider, recipient, support type and scope.
- AT-087: Support may be practical, care-related, financial or other configured type.
- AT-088: Support relationship does not create a financial transaction.
- AT-089: Financial support payment remains in BP-34 or relevant finance owner.
- AT-090: Care service delivery remains with the relevant service owner.
- AT-091: One person may support multiple recipients.
- AT-092: A recipient may receive support from multiple people.
- AT-093: Support link records voluntary/formal/informal/disputed/unknown basis.
- AT-094: Guardian or ward social label does not confer legal guardianship.
- AT-095: Legal authority requires authoritative configured source.
- AT-096: Safeguarding metadata is restricted and sourced.
- AT-097: Vulnerability is not inferred solely from age, disability or isolation.
- AT-098: Support ending preserves prior support history.
- AT-099: Contact pattern references source records rather than copying them.
- AT-100: Contact frequency does not automatically establish relationship type.
- AT-101: Aggregate contact pattern discloses coverage gaps and precision.
- AT-102: Missing contact record is not proof of no contact.
- AT-103: Social event distinguishes planned from occurred.
- AT-104: Social event records time, place, organiser and attendance source where known.
- AT-105: Unidentified participant remains unidentified rather than guessed.
- AT-106: Observed and reported attendance remain distinct.
- AT-107: Estimated time/location retains uncertainty.
- AT-108: Two people at one location are not automatically recorded as meeting.
- AT-109: Event attendance does not establish group membership.
- AT-110: Social event does not create a case role.
- AT-111: Case role does not automatically create a social relationship.
- AT-112: Social event records preserve source and causation references.
- AT-113: A relationship change caused by a source event links to that event.
- AT-114: Relationship event uses BP-37 canonical simulation time.
- AT-115: Relationship event cannot be backdated without explicit correction authority.
- AT-116: A single source event's multiple social effects retain causal lineage.
- AT-117: Conflicting causal inputs remain visible pending resolution.
- AT-118: Relationship change is not generated solely for narrative drama.
- AT-119: Relationship event cannot create legal status unsupported by source.
- AT-120: Person death/lifecycle remains owned by BP-03.
- AT-121: Person departure/lifecycle remains owned by BP-03.
- AT-122: Relationship closure follows person lifecycle through linked events.
- AT-123: No relationship or household change executes while simulation is paused.
- AT-124: No social event executes while player is absent.
- AT-125: Wall-clock passage does not change relationship state.
- AT-126: Resume does not invent missed household/social events.
- AT-127: NPC context contains only information the specific NPC knows or is authorised to access.
- AT-128: A spouse/partner does not automatically know another person's movements.
- AT-129: A household member does not automatically know another member's finances or secrets.
- AT-130: A colleague does not automatically know another employee's private records.
- AT-131: NPC belief remains distinct from objective relationship record.
- AT-132: NPC rumour remains attributed and uncertain.
- AT-133: NPC dialogue cannot upgrade a belief to verified fact.
- AT-134: NPC knowledge includes source and acquisition time.
- AT-135: NPC response reflects knowledge gaps and uncertainty.
- AT-136: Player question does not cause NPC to disclose information they do not know.
- AT-137: AI context excludes hidden crime truth.
- AT-138: Relationship network cannot leak hidden offender identity.
- AT-139: Network proximity is not proof of criminal association.
- AT-140: Social context cannot establish guilt, motive, opportunity or conspiracy.
- AT-141: No unsolicited investigative hint is generated from relationship graph.
- AT-142: Engine does not select the player's next investigative action.
- AT-143: Case owner receives relationship references only under permission.
- AT-144: Case-specific roles remain with BP-17/BP-18 and relevant divisions.
- AT-145: Victim/witness support context does not overwrite procedural role.
- AT-146: Suspect relationship to victim does not prove guilt.
- AT-147: Intelligence/network analysis remains owned by BP-21.
- AT-148: Surveillance observations remain owned by BP-20.
- AT-149: Interview statements remain owned by BP-19.
- AT-150: Evidence and forensic conclusions remain owned by BP-23/BP-24.
- AT-151: Relationship query distinguishes no record from no relationship.
- AT-152: Query distinguishes inaccessible, unverified, disputed and disproven.
- AT-153: Query result includes source, confidence and effective period.
- AT-154: Sensitive relationship data is filtered before output.
- AT-155: Confidential existence can be concealed where required by access policy.
- AT-156: Consent is purpose-specific and not inferred from relationship.
- AT-157: Third-party assertion is not displayed as subject's own statement.
- AT-158: Access, query, correction and export are auditable.
- AT-159: AI and visual projections cannot bypass access controls.
- AT-160: A denied query does not reveal protected record content.
- AT-161: Every correction preserves supersession lineage.
- AT-162: Every status transition is attributable.
- AT-163: No relationship history is deleted to hide prior state.
- AT-164: Reciprocal links remain internally consistent.
- AT-165: Household membership and premises conflicts are referred to BP-04.
- AT-166: All person references remain valid or explicitly historical after lifecycle change.
- AT-167: Population ledger is not changed by household/group/relationship operations.
- AT-168: Population never exceeds 10,000 because of relationship processing.
- AT-169: Relevant-person promotion remains permanent under BP-03/BP-35.
- AT-170: Relationship records for promoted persons remain persistent.
- AT-171: Storage compaction preserves relationship meaning and source provenance.
- AT-172: Network projection is reproducible from canonical records and source watermark.
- AT-173: A stale projection cannot overwrite canonical relationship state.
- AT-174: Query adjacency for a person does not require full graph scan.
- AT-175: High-degree social node does not cause unbounded traversal.
- AT-176: Group membership churn preserves append-only history.
- AT-177: Archive/retention preserves case-relevant relationship history.
- AT-178: Data correction does not alter source interview/surveillance/evidence records.
- AT-179: Relationship schema version is recorded for every committed change.
- AT-180: Taxonomy change is controlled through BP-44.
- AT-181: Permission is checked before relationship mutation.
- AT-182: Permission is rechecked at commit if authority may change.
- AT-183: Event payload cannot grant its actor additional authority.
- AT-184: A generated narrative cannot create a relationship record by itself.
- AT-185: Invalid person or group reference causes no partial mutation.
- AT-186: Persistence failure prevents commit acknowledgement.
- AT-187: Recovery reconciles relationship event and record versions.
- AT-188: Recovery does not duplicate household membership or relationship change.
- AT-189: Replay uses recorded inputs, source versions and canonical timestamps.
- AT-190: Replay does not regenerate a new social event from a newer model.
- AT-191: Integrity failure blocks affected mutation and emits attributable diagnostics.
- AT-192: Text interface can inspect authorised relationship and household history.
- AT-193: Optional family/network graph is derived from canonical source records.
- AT-194: Optional visual projection cannot become authoritative truth.
- AT-195: Every displayed relationship label has a defined taxonomy meaning.
- AT-196: Every displayed confidence/verification state is sourced.
- AT-197: Public group/community events use BP-35/BP-37 scheduling contracts.
- AT-198: Event time/place/organiser and attendance remain separately represented.
- AT-199: Community participation does not imply political, religious or ideological belief.
- AT-200: Faith/cultural group membership is not inferred from name, ethnicity or attendance.
- AT-201: The system supports culturally configured kinship categories without assuming one universal family model.
- AT-202: A person may privately reject or dispute an asserted relationship.
- AT-203: A relationship can remain confidential without being deleted.
- AT-204: A relationship source's reliability and the content's credibility are stored separately where supported.
- AT-205: A social network is not proof of coordinated activity.
- AT-206: Relationship graph query preserves edge direction, time and uncertainty.
- AT-207: A relationship that ended remains available for historical case chronology subject to access.
- AT-208: A group member's offence does not transfer guilt to other members.
- AT-209: A household member's offence does not transfer guilt to relatives or co-residents.
- AT-210: A family link does not establish motive or opportunity.
- AT-211: A social-context score cannot be used as an arrest ground.
- AT-212: Reputation aggregates expose source, coverage, age and uncertainty.
- AT-213: No global objective trust score is inferred from one person's subjective view.
- AT-214: A person's relationship view may differ from another participant's view.
- AT-215: Relationship privacy restrictions survive projection, export and replay.
- AT-216: A safeguarding restriction is not silently removed by relationship status change.
- AT-217: A relationship can be corrected without changing the person's canonical identity.
- AT-218: Relationship IDs and historical membership IDs are not reused after dissolution.
- AT-219: Household merge/split lineage is queryable.
- AT-220: No relationship graph creates an external playable city or territory.
- AT-221: Social groups do not reduce the minimum 10,000-business registry.
- AT-222: BP-36 does not create a parallel population count.
- AT-223: Police remains the deepest simulation; social context does not expand all institutions to equal depth.
- AT-224: Text-first access remains complete without network graphics.
- AT-225: Relationship queries and event processing are bounded and observable.
- AT-226: Social-context processing does not run continuous all-pairs comparisons.
- AT-227: A material case-related person is promoted permanently, not represented only as a temporary graph node.
- AT-228: No offscreen social event, relationship change or NPC reaction occurs while player absent.
- AT-229: A source correction invalidates dependent projections without deleting historical records.
- AT-230: No Neon schema/data write occurs without explicit user approval.

## 23. Cross-system ownership and interfaces

| Division | Authoritative responsibility | BP-36 interface |
|---|---|---|
| BP-01 | Global canon and player agency | Enforce one-city, population, pause, agency and hidden-truth rules |
| BP-02 | Geography and spatial identity | Reference canonical locations only |
| BP-03 | Person identity, lifecycle and population | Reference stable person IDs; obey cap and lifecycle events |
| BP-04 | Property, businesses, organisations and service providers | Reference premises/org IDs; do not duplicate |
| BP-05–BP-08 | Police structure, personnel, career and deployment | Supply professional relationship context without changing authority |
| BP-09–BP-12 | Resources, patrol, communications and incidents | Reference relevant social context through authorised operational queries |
| BP-13–BP-16 | Crime, cases and investigation | Provide sourced relationship references; no guilt or investigative conclusions |
| BP-17 | Victims and witnesses | Exchange support/household context under safeguarding and access controls |
| BP-18 | Suspects and offenders | Keep social links distinct from suspect/offender status |
| BP-19–BP-21 | Interviews, surveillance and intelligence | Reference source observations/statements; do not duplicate them |
| BP-22–BP-29 | Scenes, evidence, forensics, arrest, custody, legal, courts and corrections | Preserve their own authoritative records and procedural roles |
| BP-30–BP-31 | Department governance and professional standards | Reference complaint/oversight parties without changing process |
| BP-32–BP-34 | Training, HR, finance/procurement | Reference instructor, colleague, employer and support links; no duplicate employment/financial records |
| BP-35 | Simulation engine | Execute relationship events only while active; coordinate causal delivery and NPC activation |
| BP-37 | Time and scheduling | Supply canonical simulation time and due-event semantics |
| BP-38 | Records and databases | Validate schemas, IDs, constraints and transaction boundaries |
| BP-39 | Persistence and recovery | Persist event history, projections/watermarks and restore state |
| BP-40–BP-41 | Interface, notifications and reporting | Render permission-filtered text and optional projections |
| BP-42 | Security and permissions | Decide access, visibility, confidentiality and audit policy |
| BP-43 | Testing and quality assurance | Execute fixtures and retain test evidence |
| BP-44 | Configuration and change control | Version relationship taxonomy and policy changes |

## 24. Open fictional and technical decisions

1. Final relationship taxonomy and culturally configured kinship catalogue.
2. Which relationship types are reciprocal, directed or multi-party by default.
3. Verification standards and acceptable authoritative sources by relationship type.
4. Household formation and membership evidence standards.
5. Rules for overlapping households and temporary accommodation.
6. Household merge/split governance and correction authority.
7. Partner/marital status categories and authoritative civil-status source.
8. Legal guardian/parental responsibility reference integration.
9. Group catalogue, group types, membership and leadership roles.
10. Social event catalogue and attendance evidence standards.
11. Support/dependency types and service-owner interfaces.
12. Contact-pattern aggregation precision and retention.
13. Trust and reputation dimensions, if any, and display policy.
14. Safeguarding flags, confidential relationship handling and restricted-existence policy.
15. Retention and archival rules for sensitive historical relationships.
16. NPC knowledge/memory model and social context refresh cadence.
17. Relationship query response schemas and projection cache invalidation.
18. Network traversal depth/limits and high-degree node performance thresholds.
19. Social event and household change generation rates under BP-14/BP-35.
20. Exact BP-42 access matrix for police, social services, group administrators and persons concerned.
21. Correction and appeal process for disputed relationship records.
22. Optional family/network diagram formats and text equivalents.
23. Test harness, fixture catalogue and evidence format under BP-43.
24. Indexing and storage budgets to be measured before implementation.

## 25. Source traceability

The following are the exact source requirement/test IDs mapped to BP-36 in the authoritative crosswalk. Original source wording remains in `docs/governance/SALTWATER_MASTER_BLUEPRINT.json`. Mapping does not imply implementation or test completion.

| Source ID | Source division | Source intent preserved |
|---|---|---|
| S03.R01 | Population accounting and demographic model | Population accounting and hard cap interface; the old 9,500 opening composition is superseded by current Saltwater canon |
| S04.R01 | Person identity and life records | Stable person references and relationship attributes/history without duplicate identity |
| S05.R01 | Households, relationships and social networks | Households, families, partners, dependants, friendships, conflicts, professional links and networks |
| S05.T01 | Households, relationships and social networks | Reciprocal relationship semantics where applicable and historically traceable links |
| S07.R01 | Businesses and commercial economy | Reference business/organisation identity, ownership, operators, employees, premises and lifecycle without duplicating BP-04 |
| S08.R01 | Employment, labour and professional life | Reference work/professional relationships while employment/contract facts remain with BP-33 and police owners |
| S15.R01 | Social care, welfare and community support | Social support, housing support, safeguarding, disability, youth/elder services, charities and community organisations |
| S21.R01 | Culture, media, recreation and civic life | Social membership/context for media, events, venues, sports, cultural organisations and gatherings |
| S21.T01 | Culture, media, recreation and civic life | Events have time, place, organiser and plausible attendance |
| S29.R01 | Incidents, crime taxonomy and occurrence generation | Preserve social/participant references to incidents without owning crime taxonomy or implying guilt |
| S40.R01 | Complaints, oversight and public accountability | Reference complaint/oversight parties and social context without owning complaint process |
| S42.R01 | Simulation engine, causality and world activity | Supply relationship/social state for deterministic, auditable causal world activity coordinated by BP-35 |

**Canon clarification:** The S03.R01 opening composition remains binding: 9,000 residents + 500 police = 9,500 living people. The remaining 500 is unused capacity headroom, not an additional population. The hard cap is 10,000 living people total. BP-03 owns the population ledger and counting rules; BP-36 owns household/relationship semantics and must not create a separate population count.

## 26. Completion status

- Specification: **DESIGNED_DRAFT**; user review/approval pending.
- Implementation: **NOT_STARTED**.
- Test execution: **NOT_STARTED**; the 230 acceptance tests are criteria only.
- Verification: **NOT_STARTED**.
- Neon: **No database write performed or authorised**.
- Next division: **BP-37 — Time and Scheduling**.
