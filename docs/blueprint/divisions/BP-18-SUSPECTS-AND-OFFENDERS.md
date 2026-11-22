# BP-18 — Suspects and Offenders

**Project:** Saltwater  
**Division:** BP-18 of the fixed 44-division structure  
**Specification:** DESIGNED_DRAFT  
**Implementation:** NOT_STARTED  
**Test execution:** NOT_STARTED  
**Verification:** NOT_STARTED  
**Authority:** Derived from the unchanged 52-division source blueprint and 52→44 crosswalk. This draft does not approve canon or structural changes.

## 1. Purpose

Define the complete, persistent and auditable model for people who are suspected, investigated as persons of interest, accused, charged, found responsible, convicted, acquitted, diverted or otherwise associated with alleged offending. Preserve the distinctions between identity, role, allegation, suspicion, investigative assessment, evidential support, charge, adjudicated finding and sentence. Support complex, concurrent, linked and unresolved cases without presuming guilt or exposing hidden world truth.

A person may be a suspect in one case, an offender in another, a victim or witness in a third, and an officer, employee or resident in another context. These are independent, time-bounded role records. No role automatically overrides another.

## 2. Scope and ownership

### 2.1 BP-18 owns

- Case-specific suspect, person-of-interest and offender role records and lifecycle.
- Basis, source, scope, effective period and status of each role.
- Suspect/offender procedural and investigative status, distinct from interview, arrest, custody, charge, court and sentence status.
- Person-to-case suspect/offender links, linked allegations and offence references.
- Versioned attribution of alleged conduct, suspected involvement and adjudicated outcomes.
- Role-specific identity-confidence references and unresolved identity associations, subject to BP-03 identity authority.
- Limited operational handling metadata necessary to manage role records and their restrictions.
- Reconciliation when allegations are withdrawn, evidence changes, a person is eliminated, charged, acquitted, convicted, deceased or otherwise leaves a role.
- Auditable, source-preserving history of every change.

### 2.2 Explicit exclusions and owners

| Concern | Owner | BP-18 relationship |
|---|---|---|
| Person identity, matching, life status, population ledger, 10,000 cap and permanent promotion | BP-03 | References canonical person; no shadow identity |
| Crime/offence taxonomy and elements | BP-13 | References versioned offence definitions |
| Hidden occurrence truth and generation | BP-14 | Never surfaced to ordinary BP-18 views |
| Case identity, lifecycle, assignment, closure/reopening and related-case links | BP-15 | References case; cannot create/close/merge/split cases |
| Investigative plans, leads, hypotheses, tasks, actions and decisions | BP-16 | References authorised investigative sources; does not direct investigation |
| Victim, witness, reporter, caller and affected-person roles/support | BP-17 | Independent role records; never overwritten |
| Interviews, cautions, questions, answers, recordings and statements | BP-19 | References exact source versions; BP-19 owns them |
| Surveillance requests, authorisations, collection and products | BP-20 | References only |
| Intelligence source grading, confidence and dissemination | BP-21 | References only; intelligence is not proof |
| Crime scenes | BP-22 | No scene authority |
| Exhibits, recovery, custody and continuity | BP-23 | References only |
| Forensic methods, raw results, interpretation and limitations | BP-24 | References exact versions |
| Arrest, search, warrants and execution | BP-25 | Suspect status grants no coercive authority |
| Custody, detention, welfare and release | BP-26 | Separate custody lifecycle |
| Charge, prosecution, disclosure and legal process | BP-27 | BP-27 owns legal state and charging decisions |
| Court proceedings, verdicts, findings, sentence orders and appeals | BP-28 | BP-28 owns adjudicated outcomes |
| Sentence execution, supervision, release and recall | BP-29 | BP-29 owns corrections lifecycle |
| Governance/command; professional standards | BP-30/BP-31 | Own authority and police accountability |
| Employment and police career | BP-06/BP-07/BP-33 | Independent employment/personnel domains |
| Canonical time | BP-37 | Owns time and pause |
| Schemas, provenance and records | BP-38 | Global record authority |
| Persistence and recovery | BP-39 | Durable state and restore |
| Interface/reporting | BP-40/BP-41 | Must enforce permissions and reveal gate |
| Security | BP-42 | Authoritative access/disclosure controls |
| Testing and change control | BP-43/BP-44 | Evidence and approved amendments |

## 3. Governing invariants

1. A suspect/offender role is contextual and case-specific, not a person's identity.
2. Suspicion is not proof, guilt, charge, conviction or sentence.
3. Allegation, intelligence, investigative hypothesis, evidence, forensic interpretation, charge, finding and conviction are distinct information classes.
4. A person is not guilty merely because they are generated as a suspect, linked to an incident, interviewed, arrested, charged, prosecuted or detained.
5. A person may be a suspect in one case and victim/witness in another, including simultaneously. Histories remain distinct.
6. A person may be wrongly suspected, falsely identified, eliminated, acquitted, exonerated, convicted in part or remain unresolved.
7. A suspect role requires a documented source and authorised basis. A name appearing in unverified material is not automatically a suspect.
8. A person-of-interest label is not a finding and must not silently become a suspect role.
9. Offender is a context-sensitive label; its basis must always be explicit.
10. An admission/confession is an attributed statement, not automatically proof or conviction.
11. A charge is a BP-27 legal event, not an investigative conclusion.
12. Only BP-28 owns adjudicated findings/verdicts; only BP-29 owns sentence execution.
13. No score, profile, association, proximity, demographic trait or AI inference establishes guilt.
14. No suspect/offender status is automatically inferred from family, employment, friendship, address, group membership, prior unrelated case or protected characteristic.
15. Errors are corrected by append-only records; roles and sources are never deleted to conceal mistakes.
16. Every materially relevant person is permanently promoted by BP-03 to full persistent simulation. No downgrade after closure, elimination, acquittal, release or death.
17. Total living population remains at or below 10,000. A role link never creates another person.
18. Culprit, perpetrator and accomplice identities remain inaccessible to the player until the exact input bingo. This applies to direct views, metadata, NPC dialogue, generated text, exports, reports, alerts, logs, analytics and visuals.
19. Never give unsolicited solution hints or tell the player what to investigate next. Present available records and let the player choose.
20. NPCs know only what they observed, were told, received through authorised handoff or derived through a permitted process. No NPC uses hidden generator truth as ordinary knowledge.
21. No simulation time advances while the player is outside the simulation. Reviews, status transitions, NPC actions, deadlines, notices and scheduled processes freeze.
22. All material changes carry actor, authority, source, canonical time, rationale and version history.
23. Storage compression may reduce representation, never meaning, source detail, uncertainty, chronology or relationships.

## 4. Core entities and identifiers

All IDs are stable, opaque and non-semantic. Prefixes/display formats remain open for BP-38/BP-44.

| Entity | Required ID | Purpose |
|---|---|---|
| Person reference | person_id | BP-03 canonical identity |
| Case role | suspect_role_id | One person's role in one case |
| Role episode | role_episode_id | Effective-dated status period |
| Person-of-interest record | poi_id | Explicitly non-suspect relevance record |
| Allegation link | allegation_link_id | Source allegation/occurrence reference |
| Suspected involvement | involvement_id | Attributed involvement theory |
| Offence association | offence_association_id | BP-13 offence and case classification |
| Identity association | identity_association_id | Candidate/unresolved match |
| Procedural status link | procedural_status_link_id | Exact BP-19/BP-25/BP-26/BP-27/BP-28 source |
| Outcome link | outcome_link_id | Exact adjudicated outcome reference |
| Role decision | role_decision_id | Attributed decision to add/change/end role |
| Correction | correction_id | Append-only correction/dispute |
| Source link | source_link_id | Versioned provenance reference |

### 4.1 Common fields and assertion model

As applicable: stable ID; schema version; person/case references; role type; status/reason; source type and exact source version; actor/system; created/changed/effective canonical times; recorded-at; authority; scope; confidence/uncertainty; attribution type; sensitivity; access policy; supersession/correction links; correlation/idempotency identifiers.

Every assertion distinguishes who made it, who/what it concerns, alleged conduct, whether it is first-hand/hearsay/inferred/analytical/automated/adjudicated, source version, event/report/record/effective times, confidence, limitations, contradictions, authorising actor and permitted audience. Identity confidence and involvement confidence are separate.

## 5. Role catalogue and semantic model

### 5.1 Person of interest (POI)

A POI is a person whose possible relevance is recorded without formal suspect designation. The limited reason and source must be recorded. It may represent unresolved identity, possible witness, person requiring identification, contextual relevance or a person referred to by a line of enquiry. POI is not a low-confidence suspect label and cannot evade suspect safeguards. A later authorised suspect designation creates a separate role with its own source and rationale; POI history remains.

### 5.2 Suspect

A suspect role means an authorised case record identifies a person as reasonably suspected of involvement in specified alleged conduct under a fictional policy threshold still to be approved. It records:
- Case and alleged offence/conduct reference.
- Specific basis and source, including supporting and contradictory information.
- Attribution type and confidence/uncertainty.
- Authorising actor, authority and canonical time.
- Scope: offence, conduct, time period and suspected participation.
- Review trigger/status and access restrictions.
- Explicit player-facing non-finding disclaimer.

This draft does not invent a legal threshold or authorisation matrix.

### 5.3 Offender

Offender is not a synonym for suspect. Every offender role states its basis:
- **Alleged offender:** allegation only; no finding.
- **Admitted conduct:** attributed admission, not necessarily accepted or adjudicated.
- **Established offender under configured finding:** exact BP-28 outcome supports the specific conduct/offence.
- **Other configured basis:** must be explicitly approved and never silently inferred.

If an outcome is overturned or varied, update the role through a new episode while preserving the former finding and its historical effect. Conviction in one case does not establish guilt in another.

### 5.4 Participation terms

Terms such as principal, accomplice, aider, organiser, facilitator, accessory, conspirator or co-suspect must map to a BP-13/BP-27 fictional offence/participation concept and exact source basis. A relationship between suspects does not prove joint action. Group membership or association is not an offence. Hidden accomplice truth is never imported into player-visible records.

## 6. Role lifecycle and transitions

The role lifecycle is separate from case lifecycle and legal procedure. Minimum statuses: proposed; active_poi; active_suspect; alleged_offender; admitted_conduct; established_offender; under_review; disputed; identity_unresolved; eliminated; no_longer_suspected; allegation_withdrawn; role_ended; superseded; corrected; deceased; reopened.

Not every transition is valid. POI cannot become suspect without an authorised decision. Suspect cannot become established offender from interview or arrest alone. BP-18 cannot create a charge or conviction. Reopening creates a new episode or versioned transition and preserves prior history.

Every transition records prior/resulting status, actor, authority, canonical time, source, rationale, scope, confidence, review decision, affected offence/case and linked procedural/legal status. Automated transitions require an explicit configured rule, deterministic trigger and auditable system actor.

Reviews may be triggered by new evidence, source correction, identity challenge, contradictory information, forensic update, witness correction, legal decision, court outcome, new case linkage or authorised human decision. A trigger creates a review item; it does not decide the outcome. Mistaken or unjustified designation preserves original author/source/duration/access history, correction, downstream notifications and remedies.

## 7. Allegations, conduct and offence associations

An allegation is a claim about conduct, linked to its originating report/source. It cannot be rewritten as fact. BP-13 owns offence taxonomy, elements, severity and classification. BP-18 owns the person-specific association with alleged/suspected conduct.

One person may have multiple allegations in one case; one allegation may refer to multiple persons; one person may be associated with multiple offences. These are many-to-many links with independent sources, scope and status. Classification changes do not rewrite the original report or silently broaden alleged conduct.

Record occurrence/incident and case references; offence/conduct references and version; person's alleged role or unknown status; alleged act/omission, time and location; source and attribution; elements alleged supported/unknown/disputed/contradicted without legal determination; exact evidence/intelligence versions and limits; alternative explanations and exculpatory information; review status and authorised decision.

A person may be linked to an incident without any allegation. A suspect may exist before offence classification is settled. An offence may have no identified suspect.

## 8. Identity, attribution and mistaken identification

BP-03 alone owns identity resolution. BP-18 may store role-specific identity confidence and source references but cannot merge canonical people.

Support known identity with uncertain attribution; unidentified person; candidate identity; multiple competing candidates; mistaken/withdrawn identification; confidential identity; and aliases/name variants sourced from BP-03. Identity confidence never establishes involvement. Recognition, photo/video identification, biometric comparison, eyewitness identification, device attribution and third-party naming retain method, source, conditions, limitations, confidence and challenge. BP-24 owns forensic/biometric interpretation; BP-19 owns interview/identification procedure; BP-20 surveillance source; BP-23 exhibit continuity.

No demographic, family, location, association, occupation, appearance or prior-record similarity automatically identifies an offender. Mistaken identity is corrected through a new authorised event preserving original association and downstream impact.

## 9. Suspect-specific risk and operational handling

BP-18 may record limited handling metadata necessary for role integrity: identity uncertainty; documented intimidation/coercion allegation; sourced threat/safety concern; conflict between sources; restrictions on revealing identity/status; procedural restrictions referenced from BP-19/BP-25/BP-26/BP-27; explicit review/no-contact requirement.

BP-18 does not own general public-safety risk, victim safeguarding, custody welfare, clinical risk or police tactical assessment. Those remain BP-17/BP-26/BP-30/BP-35/BP-42. A risk flag is not a finding, warrant ground or permission for coercive action. No risk score is guilt evidence.

## 10. Procedural status interfaces

BP-18 keeps a timeline of references; source divisions remain authoritative.

| Event/status | Owner | BP-18 rule |
|---|---|---|
| Interview, caution/procedural status, admission/denial/no comment | BP-19 | Link exact interview/statement version; no invented answer |
| Surveillance application/authorisation/collection | BP-20 | Link only; no authority or source fabrication |
| Intelligence report/source grading | BP-21 | Link exact item and restrictions; not evidence by default |
| Arrest, grounds, warrant/search application and execution | BP-25 | Link authorised event; suspect role itself is not grounds |
| Detention, custody clock, welfare and release | BP-26 | Link exact episode; arrest is not guilt |
| Charge, prosecution, disclosure and legal procedure | BP-27 | Link authoritative legal state; BP-18 cannot charge |
| Verdict, finding, acquittal, dismissal, appeal and sentence order | BP-28 | Link exact decision/version; no independent judicial conclusion |
| Sentence, supervision, release and recall | BP-29 | Link execution state; no sentence lifecycle duplication |

Missing source event remains unknown/unavailable, not inferred. Conflicting source versions remain and are reconciled by the owner. Late charge/court outcome is effective-dated and cannot rewrite earlier investigative knowledge.

## 11. Intelligence, evidence and exculpatory material

BP-18 may reference source material but does not grade intelligence or determine admissibility. Every reference identifies source owner, exact version, collection/recording time, source reliability/confidence if supplied, restrictions and whether it supports, contradicts or is neutral to a stated proposition. Support/contradiction is an attributed assessment, not an objective property of the source.

Keep separate: unverified allegation; first-hand/hearsay account; intelligence item; investigative hypothesis; physical/digital/documentary/testimonial evidence; forensic result; analyst interpretation; investigative inference; admission/denial; charge; court finding/verdict; sentence.

Exculpatory, contradictory, neutral and inconclusive material must be representable with equal provenance and protection. Do not hide or downgrade information because it conflicts with a suspect theory. Missing record is not proof of absence. Lack of CCTV coverage is not an alibi or proof of presence. Association or proximity is not participation.

## 12. Multiple people, group cases and linked conduct

Support cases with no suspect, one/multiple suspects, unidentified participants, one person across many cases, multiple offences per person, multiple persons per allegation, suspected group conduct, organised networks, conspiracy allegations, linked series, co-suspects with conflicting accounts and unknown accomplices.

Each person's role is independently sourced and reviewed. Group membership is not collective guilt. One person's admission does not establish another's involvement. A suspect's allegation against another is an attributed statement, not automatic corroboration. Shared address, phone, vehicle, employer, family or social association is context only. Related cases are linked by BP-15; BP-18 does not merge them. An offence may have no identified suspect or competing candidates. Elimination in one offence does not eliminate a person from another. Role change in one case never silently propagates to another. Hidden accomplice truth remains inaccessible before exact bingo.

## 13. NPC knowledge and behaviour

NPC knowledge is bounded by person-specific observation, memory, communications, authorised records access and plausible inference. Suspects do not know the police case file, hidden generator facts, another person's confidential interview or all evidence without a plausible information path.

A suspect NPC may know some/all/none of alleged conduct; deny, admit, partially admit, misunderstand, forget, lie, remain silent or refuse; have independent motives, relationships, schedules and life events; react to lawful contact or information actually received; and change an account for plausible reasons with every version preserved. These possibilities are not solution cues. Dialogue quirks are not reliable guilt detectors. Silence, nervousness, anger, confidence, inconsistency, cooperation or refusal never automatically signals guilt. NPCs do not volunteer culprit identities from hidden truth.

## 14. Hidden truth and player agency firewall

BP-14 owns hidden occurrence truth. BP-18 is not a channel for exposing it. Player-visible records reflect only legitimately generated, discovered, reported, recorded or authorised information.

- No culprit/perpetrator/accomplice identity until the player types exactly lowercase bingo, alone and without punctuation or whitespace.
- Bingo with different case, punctuation, whitespace, extra words, quotation or NPC utterance does not qualify.
- The trigger only permits the defined reveal; it does not waive other privacy/security boundaries or turn speculation into fact.
- No indirect disclosure through ordering, counts, role names, metadata, distinctive descriptions, file paths, source references, errors, timing, narrative, hidden prompt context or selective omission.
- No automated “most likely offender” or suspect ranking may use hidden truth or present an ungrounded score.
- No unsolicited investigative recommendation, next step, culprit hint or leading question.
- Present requested records neutrally, with clear unknowns.
- NPC knowledge remains bounded even after a permitted player reveal unless a separate plausible knowledge path exists.

## 15. Information classification and permissions

BP-42 owns access policy. BP-18 supplies classification and enforces checks for read, write, search, autocomplete, counts, aggregation, reports, exports, notifications, logs, analytics, prompts and visuals.

Minimum classes: basic role index; suspect identity/basis; confidential identity/alias; allegation/conduct; restricted intelligence references; evidence/forensic references; interview/statement references; procedural/legal status; risk/handling; acquittal/elimination/correction/exoneration history; hidden occurrence truth (not player-visible before exact trigger).

Rules:
1. Case access does not grant every sensitive source.
2. A suspect does not see internal role records or police hypotheses unless an authorised legal/disclosure process permits.
3. Player/officer/administrator/system roles are distinct and least-privilege.
4. Access denial cannot confirm or deny a hidden person, role, source or outcome.
5. Search snippets, autocomplete, counts, errors, exports and analytics enforce identical restrictions.
6. Generated text receives only permitted fields; hidden truth is excluded from ordinary generation context.
7. Emergency access, if configured, is narrow, reasoned, time-limited, logged and reviewed.
8. Credentials/secrets never enter case/person records, prompts, logs or source control.
9. Sensitive reads, writes, corrections, exports and emergency access are audited.
10. Exact bingo does not bypass unrelated privacy/security controls.

## 16. Time, scheduling and pause

Every time-bearing event uses BP-37 canonical in-world time and preserves event, report, record, effective and correction times separately where needed. Time uncertainty and source basis remain explicit.

No suspect review, status transition, NPC decision, scheduled contact, legal event, notification, expiry, deadline, automated analysis or role update advances while the player is outside the simulation. No real-world catch-up. On resume, process only explicitly pending in-world events in deterministic order. A scheduled review trigger creates a pending item only when simulation resumes; it does not execute during pause.

## 17. Population, persistence and person lifecycle

BP-03 owns the sole person ledger and lifecycle. Every materially relevant suspect, POI or offender is permanently promoted to full persistent detail through BP-03. Promotion is idempotent. Multiple roles, cases, aliases, allegations and procedural episodes do not create duplicate persons. All qualifying living people, including police, suspects and offenders, count once against the hard 10,000-person cap.

A deceased or permanently departed person retains historical identity, role, source and legal outcome records. Case closure, elimination, acquittal, release or sentence completion never downgrades a promoted person. New-person admission is atomic and subject to BP-03 cap enforcement. Role links cannot bypass capacity checks or create shadow populations.

## 18. Records, provenance, correction and retention

BP-38 owns schema, identifiers, versioning, source provenance, retention and legal-hold framework. BP-18 owns semantic content and role history. Preserve original source/version; attribution and uncertainty; decision-maker/authority/rationale; prior/resulting states; effective/recorded times; source corrections and downstream impact; access history/disclosure restrictions; related cases and procedural/legal events; superseded and erroneous states.

Corrections are append-only. A source correction is made by its owner; BP-18 updates its reference and records resulting review. No destructive deletion to conceal error. Retention, deletion, anonymisation and legal-hold policy remain open; no BP-18 process silently destroys source history. Storage compaction preserves full meaning and audit.

## 19. Text interface and optional visuals

Text is the complete primary interface. Authorised workflows list requested case-specific roles neutrally; open a role and view source/basis/uncertainty/scope/status/history; distinguish person identity from case role and legal status; link/unlink authorised source versions with audit; record/review role decisions; correct mistaken identity/role through append-only workflow; view exact linked source references within permission; inspect contradictions/unknowns without automatic recommendation; compare role episodes across cases without implying collective guilt.

Command syntax belongs to BP-40. Optional visuals include role timeline, case/person link graph, procedural timeline and source-support matrix. They derive from canonical records, obey permissions and reveal no hidden truth. Visuals are never required.

## 20. Inputs, outputs and event contracts

**Inputs:** BP-03 identity/lifecycle; BP-13 offence catalogue; BP-14 authorised visible outputs only; BP-15 case; BP-16 investigative decisions; BP-17 independent victim/witness roles; BP-19 interviews; BP-20 surveillance; BP-21 intelligence; BP-23 evidence; BP-24 forensics; BP-25 arrest/warrant; BP-26 custody; BP-27 legal process; BP-28 court outcomes; BP-29 corrections; BP-37 time; BP-42 access.

**Outputs:** case-specific role episodes; allegation/conduct associations; attributed role decisions; source/procedural links; status review requests; correction events; audit/provenance events for BP-38/BP-39; authorised text/report references for BP-40/BP-41.

Every event carries stable event ID, entity/case references, actor/system, authority, source/version, canonical and recorded time, correlation/idempotency key, schema version, prior/resulting state, access classification and reason.

Minimum event catalogue: POI proposed/recorded/ended; suspect role proposed/authorised/activated/reviewed/disputed/ended/reopened; offender basis recorded/changed/withdrawn; allegation association added/corrected/withdrawn; identity association proposed/confirmed/rejected/corrected; involvement assessment recorded/superseded; procedural status reference added/corrected; court outcome reference received/varied/overturned; elimination/no-longer-suspected decision recorded/reopened; source link added/restricted/withdrawn; correction submitted/resolved; access restriction changed; person promotion reference received from BP-03.

## 21. Failure handling and edge cases

- No suspect: case remains valid with zero suspect roles.
- Unidentified offender: retain unknown-person reference; no invented identity.
- Multiple candidate identities: keep separate, unresolved and sourced.
- Mistaken identification: preserve original and append correction/review.
- POI without suspect basis: retain POI only.
- Unsupported suspect role: require authorised review; no auto-promotion from mere mention.
- Allegation withdrawn: preserve source/history and review role.
- Conflicting evidence: preserve versions and uncertainty.
- Exculpatory material: retain and expose to authorised reviewers equally.
- Admission disputed/retracted: retain statement versions; no automatic finding.
- Charge withdrawn: BP-27 remains source; review role, do not erase it automatically.
- Acquittal: BP-28 authoritative; preserve allegation and acquittal without implying complainant dishonesty.
- Conviction on one count: scope status to exact finding.
- Appeal/overturn: append outcome update; preserve prior effective history.
- Death: preserve person and case records.
- Cross-case roles: separate status, sources, permissions and review.
- Co-suspect accusation: attributed claim, not corroboration.
- Shared address/device/vehicle: association only.
- Source unavailable: mark unavailable; do not infer status.
- Permission failure: deny without revealing existence.
- Pause: freeze all processes.
- Population cap: role link does not add person; new admission follows BP-03.
- Duplicate retry: idempotency prevents duplicate role/status.
- Concurrent updates: preserve both proposals for authorised reconciliation.
- Restore: preserve role/procedural histories and access audit.
- Hidden truth leakage: suppress and log through BP-42/BP-43 without exposing hidden value.

## 22. Dependencies and failure contracts

| Dependency | Contract | Failure behaviour |
|---|---|---|
| BP-03 | Identity, matching, lifecycle, population, permanent promotion | Hold unresolved; no shadow person |
| BP-13 | Versioned offence taxonomy/elements | Preserve allegation; classification pending |
| BP-14 | Hidden occurrence truth; authorised visible outputs | Never expose hidden truth |
| BP-15 | Case ID/status/access | No orphan role |
| BP-16 | Investigative source/decision references | No automatic investigative action |
| BP-17 | Independent victim/witness roles | Preserve both domains |
| BP-19 | Interview/statement source versions | Pending link; no invented state |
| BP-20/BP-21 | Surveillance/intelligence source and restrictions | Preserve unavailable/limited status |
| BP-23/BP-24 | Evidence/forensic source versions | No unsupported evidential claim |
| BP-25/BP-26 | Arrest/warrant/custody events | No coercive authority from suspect status |
| BP-27/BP-28/BP-29 | Legal/court/sentence authority | Await authoritative source; never infer |
| BP-35/BP-37 | Event causality, canonical time and pause | Freeze scheduled progression |
| BP-38/BP-39 | Schema, provenance, atomic persistence/recovery | No partial commit |
| BP-40/BP-41 | Text, reports, notifications and presentation | Enforce permissions/reveal gate |
| BP-42 | Access and hidden-truth controls | Deny safely and audit |
| BP-43/BP-44 | Test evidence and change control | No completion without evidence/approval |

## 23. Logical permissions

BP-42 owns capability assignment. BP-18 capabilities include: suspect.read.index; suspect.read.role_basis; suspect.read.identity_restricted; suspect.read.allegation; suspect.read.source_links; suspect.read.procedural_status; suspect.read.outcomes; suspect.create.poi; suspect.create.role; suspect.authorise.role; suspect.update.role; suspect.review.role; suspect.end.role; suspect.correct.identity_link; suspect.correct.role; suspect.link.source; suspect.export; suspect.audit.read; suspect.emergency_access.

Read does not imply write, authorisation, export or disclosure. Self-approval of access elevation is prohibited unless BP-42 explicitly approves a narrow exception. Suspect/offender permissions never grant hidden occurrence truth before exact reveal.

## 24. Acceptance tests

These criteria are specified, not executed. BP-43 must attach reproducible evidence before any test is passed.

### Identity and role separation
- **SUS-AT-001** — Every role references one canonical BP-03 person or explicitly unresolved identity.
- **SUS-AT-002** — Creating a role does not create a duplicate person.
- **SUS-AT-003** — One person may hold multiple independent case roles.
- **SUS-AT-004** — Victim/witness and suspect/offender roles coexist without overwrite.
- **SUS-AT-005** — Role in one case does not propagate to another.
- **SUS-AT-006** — A person may be suspect in one case and established offender in another.
- **SUS-AT-007** — POI does not silently become suspect.
- **SUS-AT-008** — A mention/name in source material does not automatically create a suspect role.
- **SUS-AT-009** — Every role has a stable opaque identifier.
- **SUS-AT-010** — Every role episode has effective dates and source basis.
- **SUS-AT-011** — Multiple roles do not duplicate population count.
- **SUS-AT-012** — Unknown person is representable without fabricated identity.
- **SUS-AT-013** — Multiple candidate identities remain separate and unresolved.
- **SUS-AT-014** — BP-18 cannot merge canonical people.
- **SUS-AT-015** — Mistaken identity correction preserves original association.
- **SUS-AT-016** — Identity confidence is separate from involvement confidence.
- **SUS-AT-017** — Role end preserves historical source and status.
- **SUS-AT-018** — Reopening creates traceable new episode/transition.
- **SUS-AT-019** — Deceased person's historical role remains available to authorised users.
- **SUS-AT-020** — Permanent promotion through BP-03 is never reversed.

### Allegation, suspicion and proof distinctions
- **SUS-AT-021** — Allegation is not displayed as established fact.
- **SUS-AT-022** — Suspicion is not guilt or conviction.
- **SUS-AT-023** — POI is not represented as suspect.
- **SUS-AT-024** — Suspect role requires source, scope and authorised basis.
- **SUS-AT-025** — Arrest does not automatically establish offender status.
- **SUS-AT-026** — Interview does not automatically establish offender status.
- **SUS-AT-027** — Admission is attributed statement, not automatic proof.
- **SUS-AT-028** — Charge is sourced from BP-27 and is not conviction.
- **SUS-AT-029** — Conviction/finding is sourced from BP-28 only.
- **SUS-AT-030** — Sentence execution is sourced from BP-29 only.
- **SUS-AT-031** — Conviction in one case does not establish guilt in another.
- **SUS-AT-032** — Elimination from one offence does not eliminate from another.
- **SUS-AT-033** — Allegation withdrawal preserves original source/history.
- **SUS-AT-034** — Acquittal is preserved without labelling complainant dishonest.
- **SUS-AT-035** — Conviction on one count is scoped to exact finding.
- **SUS-AT-036** — Appeal/overturn updates current status without rewriting history.
- **SUS-AT-037** — Contradictory and exculpatory sources remain represented.
- **SUS-AT-038** — Missing source is not interpreted as proof of absence.
- **SUS-AT-039** — Lack of surveillance coverage is not proof of absence/presence.
- **SUS-AT-040** — Association/proximity is not automatically participation.
- **SUS-AT-041** — Family, employer, address or social link does not create suspicion.
- **SUS-AT-042** — Demographic/protected characteristic does not generate suspect status.
- **SUS-AT-043** — Automated score cannot establish guilt/offender status.
- **SUS-AT-044** — Alternative explanations and uncertainty can be preserved.
- **SUS-AT-045** — Role designation identifies decision-maker, authority and rationale.

### Lifecycle, review and correction
- **SUS-AT-046** — Every transition records prior/resulting state, actor, authority, time and source.
- **SUS-AT-047** — Invalid POI-to-established-offender transition is rejected.
- **SUS-AT-048** — Suspect-to-established-offender requires BP-28 basis.
- **SUS-AT-049** — Scheduled review trigger creates review item, not conclusion.
- **SUS-AT-050** — New evidence can trigger review without automatic role change.
- **SUS-AT-051** — Identity challenge is retained with resolution.
- **SUS-AT-052** — Role correction is append-only.
- **SUS-AT-053** — Downstream summaries are identified for correction after source change.
- **SUS-AT-054** — Charge withdrawal is received from BP-27 and reviewed, not guessed.
- **SUS-AT-055** — Acquittal is received from BP-28 and linked to exact charge/count.
- **SUS-AT-056** — Late court outcome retains effective and recorded times.
- **SUS-AT-057** — Conflicting status updates are reconciled by authoritative owner.
- **SUS-AT-058** — One user's correction cannot erase another source.
- **SUS-AT-059** — Role history remains after case closure.
- **SUS-AT-060** — Destructive deletion cannot conceal incorrect designation.

### Offence and multi-person relationships
- **SUS-AT-061** — One person can be associated with multiple offences in a case.
- **SUS-AT-062** — One allegation can reference multiple persons without collective guilt.
- **SUS-AT-063** — One offence can remain without identified suspect.
- **SUS-AT-064** — Multiple candidate suspects remain independently sourced.
- **SUS-AT-065** — Co-suspect allegation is attributed, not automatic corroboration.
- **SUS-AT-066** — One person's admission does not establish another's involvement.
- **SUS-AT-067** — Group membership is not automatic offender status.
- **SUS-AT-068** — Accomplice/conspiracy labels require configured offence concept.
- **SUS-AT-069** — Related-case links remain BP-15-owned.
- **SUS-AT-070** — Role changes do not propagate across linked cases.
- **SUS-AT-071** — Alleged conduct preserves time/location/source uncertainty.
- **SUS-AT-072** — Offence taxonomy version is retained with each association.
- **SUS-AT-073** — Reclassification does not rewrite original allegation.
- **SUS-AT-074** — Suspected involvement and offence classification remain separate.
- **SUS-AT-075** — Unknown accomplice truth is not exposed through group records.

### Specialist source interfaces
- **SUS-AT-076** — BP-19 owns interview and statement content/version.
- **SUS-AT-077** — Interview request does not create fabricated interview.
- **SUS-AT-078** — Admission/denial links to exact interview source.
- **SUS-AT-079** — BP-20 owns surveillance request/authorisation/collection.
- **SUS-AT-080** — BP-21 owns intelligence source grading and confidence.
- **SUS-AT-081** — Intelligence is not automatically evidence.
- **SUS-AT-082** — BP-23 owns exhibit identity and continuity.
- **SUS-AT-083** — BP-24 owns forensic methods, raw results and interpretation.
- **SUS-AT-084** — BP-25 owns arrest and warrant events.
- **SUS-AT-085** — Suspect status alone cannot authorise arrest/search.
- **SUS-AT-086** — BP-26 owns custody and detention clock.
- **SUS-AT-087** — BP-27 owns charge/prosecution/disclosure status.
- **SUS-AT-088** — BP-28 owns court verdicts and findings.
- **SUS-AT-089** — BP-29 owns sentence execution/release/recall.
- **SUS-AT-090** — Missing authoritative source leaves status unknown, not inferred.

### NPC knowledge and hidden-truth firewall
- **SUS-AT-091** — NPC knowledge is limited to observation, receipt or permitted inference.
- **SUS-AT-092** — Suspect NPC cannot see hidden generator truth through ordinary context.
- **SUS-AT-093** — Suspect NPC cannot know confidential interview without plausible handoff.
- **SUS-AT-094** — Dialogue behaviour is not a reliable guilt indicator.
- **SUS-AT-095** — Nervousness, silence, anger or cooperation does not automatically imply guilt.
- **SUS-AT-096** — NPC statements preserve source and chronology.
- **SUS-AT-097** — No culprit identity before exact lowercase bingo.
- **SUS-AT-098** — Case/punctuation/whitespace/extra-word variants do not trigger reveal.
- **SUS-AT-099** — No hidden identity leakage through counts, ordering, metadata or errors.
- **SUS-AT-100** — Reports, exports, alerts, prompts and visuals enforce reveal gate.
- **SUS-AT-101** — No unsolicited hint or next-investigation instruction.
- **SUS-AT-102** — Suspect lists are not ranked by hidden culprit relevance.
- **SUS-AT-103** — Player-visible records reflect discovered/authorised information only.
- **SUS-AT-104** — Exact bingo does not waive unrelated privacy/security permissions.

### Security, time, population and persistence
- **SUS-AT-105** — Least-privilege checks apply to every role/source view.
- **SUS-AT-106** — Access denial does not confirm/deny protected suspect existence.
- **SUS-AT-107** — Search/autocomplete/count/export/analytics apply same restrictions.
- **SUS-AT-108** — Sensitive read/write/export is audited.
- **SUS-AT-109** — Emergency access is scoped, reasoned, time-limited and reviewed.
- **SUS-AT-110** — Credentials/secrets are absent from records, prompts, logs and repository.
- **SUS-AT-111** — No suspect review/status/NPC/legal event progresses while paused.
- **SUS-AT-112** — Resume uses exact persisted state without real-world catch-up.
- **SUS-AT-113** — Every materially relevant person is permanently promoted through BP-03.
- **SUS-AT-114** — No promoted person is downgraded after elimination/acquittal/release/closure.
- **SUS-AT-115** — Person counted once across roles, aliases and cases.
- **SUS-AT-116** — New person admission cannot exceed 10,000 living-person cap.
- **SUS-AT-117** — Failed transaction leaves no orphan role/person/case link.
- **SUS-AT-118** — Retry does not duplicate role or status event.
- **SUS-AT-119** — Concurrent updates preserve both versions for reconciliation.
- **SUS-AT-120** — Restore preserves role, source, procedural and audit histories.
- **SUS-AT-121** — Storage compaction preserves meaning, uncertainty and provenance.
- **SUS-AT-122** — Every output identifies as-of time/source version where appropriate.
- **SUS-AT-123** — Optional visual traces to canonical source and obeys access controls.
- **SUS-AT-124** — No test marked passed without reproducible BP-43 evidence.
- **SUS-AT-125** — Every implementation item maps to approved requirement and BP-44 change record.

## 25. Traceability to the original 52-division source

The source JSON remains unchanged. IDs use the crosswalk's stable 1-based requirement/test array positions and original JSON-pointer convention.

| Source ID | Original source area | BP-18 incorporation |
|---|---|---|
| S03.R01–R05 / S03.T01–T03 | Population accounting | BP-03 owns unique-person count and atomic cap; roles never double-count. |
| S04.R01–R03 / S04.T01–T02 | Person identity/life records | BP-03 owns identity and permanent relevance promotion; BP-18 owns case role. |
| S05.R01–R03 / S05.T01 | Relationships/social networks | BP-36 owns relationships; association alone does not imply guilt. |
| S29.R01–R03 / S29.T01 | Crime taxonomy/occurrence generation | BP-13 taxonomy, BP-14 hidden truth, BP-18 person-specific allegation/suspect role; occurrence/report/allegation/finding distinct. |
| S30.R01–R03 / S30.T01 | Case management/investigative command | BP-15 case lifecycle; BP-16 investigative decisions; BP-18 role history/source links. |
| S31.R01–R03 / S31.T01 | Victims/witnesses/suspects | BP-17/BP-18 own distinct role domains; suspicion is not guilt. |
| S32.R01–R03 / S32.T01 | Scene/evidence collection | BP-23 owns exhibits; BP-18 references source versions only. |
| S33.R01–R03 / S33.T01 | Forensics/specialist examination | BP-24 owns methods/results/limitations; result distinct from inference. |
| S34.R01–R03 / S34.T01 | Interviews/statements | BP-19 owns process/source; admissions/denials are attributed statements. |
| S35.R01–R03 / S35.T01 | Intelligence/analysis | BP-21 owns source grading/confidence; intelligence distinct from evidence. |
| S36.R01–R03 / S36.T01 | Surveillance/monitoring | BP-20 owns collection/coverage/retrieval; no inference from absent coverage. |
| S37.R01–R03 / S37.T01 | Arrest/search/warrants/custody | BP-25/BP-26 own coercive/procedural events; suspect role does not authorise them. |
| S38.R01–R03 / S38.T01 | Prosecution/courts/outcomes | BP-27/BP-28 own charge, disclosure, findings, verdicts and appeals. |
| S39.R01–R03 / S39.T01 | Corrections/post-sentence | BP-29 owns sentence execution, supervision and release. |
| S40.R01–R03 / S40.T01 | Complaints/oversight | BP-31/BP-30 own misconduct/oversight; distinct from criminal suspect role. |
| S43.R01–R05 / S43.T01–T02 | AI/player agency | Plausible NPC knowledge, hidden truth firewall, exact bingo trigger, no unsolicited hints. |
| S48.R01–R03 / S48.T01 | Security/permissions | Least privilege, restricted identity/source, hidden truth, audit and secret protection. |
| S50.R01–R03 / S50.T01 | Testing/quality | 125 acceptance criteria; evidence-based completion gate. |
| S52.R01–R04 / S52.T01 | Canon/change control | BP-44 owns amendments; approval/implementation/testing/verification remain separate. |

BP-18 applies X01–X10, C01–C09, P01–P10 and M01–M09 as relevant: stable identity/provenance; single source of truth; effective-dated facts; reconciliation; distinctions among fact/allegation/estimate/inference/intelligence/opinion; source preservation; no hidden time; text-first operation; proportionate non-police depth; evidence-based completion.

## 26. Open decisions

1. Formal threshold and authorised role for creating a suspect record.
2. Whether POI is a distinct formal category or controlled investigative annotation.
3. Approved role/status catalogue and transition matrix.
4. Fictional offence participation vocabulary and alignment with BP-13/BP-27.
5. Offender designation rules and permitted bases beyond BP-28 findings.
6. Representation of admissions and diversion outcomes without implying guilt.
7. Identity-confidence vocabulary and identification procedure with BP-19/BP-20/BP-24.
8. Suspect-specific risk/handling taxonomy and separation from BP-17/BP-26/BP-35.
9. Review triggers, intervals, authority and thresholds.
10. Disclosure, retention, expungement, sealing and legal-hold policy with BP-27/BP-38/BP-42.
11. Confidential identity/alias architecture and access matrix.
12. Role-summary sharing across linked cases and permissions.
13. NPC autonomy and permitted self-initiated conduct with BP-35.
14. Identifier prefixes/display formats with BP-38.
15. Text command/workflow syntax with BP-40.

### Risks and mitigations

| Risk | Mitigation |
|---|---|
| Suspicion presented as guilt | Separate semantics and mandatory source/basis |
| POI used to evade safeguards | Distinct category and explicit transition |
| Victim/witness role overwritten | Independent BP-17/BP-18 records |
| Mistaken identity persists | Append-only correction, review and downstream impact |
| Admission treated as proof | BP-19 source ownership and explicit distinction |
| Charge/confession/arrest treated as conviction | BP-27/BP-28 authoritative boundaries |
| Intelligence/evidence conflated | BP-21/BP-23/BP-24 source separation |
| Exculpatory material suppressed | Equal provenance and review |
| Group association treated as guilt | Independent role basis |
| NPC omniscience leaks truth | Knowledge provenance and firewall |
| Indirect culprit disclosure | Gate all outputs, metadata, counts, prompts and visuals |
| Role history erased after acquittal | Persistent, auditable history |
| Population cap bypassed | BP-03 single ledger and idempotent promotion |
| Pause allows background progression | BP-35/BP-37 freeze invariant |
| Compression loses nuance | Lossless semantic preservation |

## 27. Design completion checklist

- [ ] Every applicable source requirement/test is incorporated or assigned to owner.
- [ ] BP-03 remains sole identity/population owner.
- [ ] Suspect, POI and offender semantics are distinct.
- [ ] Victim/witness roles remain independent under BP-17.
- [ ] Allegation, suspicion, evidence, charge, finding, conviction and sentence remain distinct.
- [ ] Identity and involvement confidence are independent.
- [ ] Every role has source, scope, authority, uncertainty and chronology.
- [ ] Mistaken identification, elimination, acquittal and overturned outcome preserve history.
- [ ] BP-19 through BP-29 procedural ownership is explicit.
- [ ] Exculpatory and contradictory information is preserved.
- [ ] NPC knowledge is bounded; dialogue is not a guilt detector.
- [ ] Exact bingo gate covers all direct/indirect output channels.
- [ ] No unsolicited hints or next-investigation instructions are generated.
- [ ] Pause/resume covers scheduled and autonomous changes.
- [ ] Permanent promotion and 10,000 cap are enforced by BP-03.
- [ ] Material changes are attributable, versioned and auditable.
- [ ] All 125 tests are traceable and later receive BP-43 evidence.
- [ ] Open decisions are resolved or explicitly retained for approved configuration.
- [ ] No Neon write, migration, seed or import has been performed or authorised.

## 28. Status and next dependencies

This is a full division design draft, not user-approved design or implementation evidence.

- Specification: **DESIGNED_DRAFT**
- User approval: **PENDING**
- Implementation: **NOT_STARTED**
- Test execution: **NOT_STARTED**
- Verification: **NOT_STARTED**
- Neon/database writes: **NONE; NOT AUTHORISED**

Next fixed division: **BP-19 — Interviews and Interrogations**. BP-19 must own interview planning, procedural status, questions, answers, recordings and statement versions while preserving source integrity, player agency and the hidden-truth rule.
