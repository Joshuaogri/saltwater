# BP-21 — Intelligence

**Project:** Saltwater — fictional sovereign city-state, one city, one jurisdiction  
**Blueprint division:** BP-21 of the fixed 44-division structure  
**Specification:** DESIGNED_DRAFT | **Implementation:** NOT_STARTED | **Test execution:** NOT_STARTED | **Verification:** NOT_STARTED  
**Authority:** Derived from the unchanged 52-division source and the fixed BP-01–BP-44 structure. No canon or division structure is changed.

## 1. Purpose

BP-21 defines the intelligence lifecycle: receipt, registration, source provenance, evaluation, grading, collation, analysis, assessment, dissemination, handling restrictions, review, retention, correction, challenge and withdrawal of intelligence information and products used by the Saltwater Police Department and authorised fictional partner roles.

It enables a living, information-rich police environment without treating intelligence as proof, evidence, established fact or a substitute for investigation. It preserves uncertainty, competing explanations, source limitations, provenance, confidence and the difference between what a source said, what an analyst assessed and what is independently established.

Intelligence can concern people, groups, places, businesses, vehicles, events, methods, patterns, threats, networks, risks and emerging situations. An intelligence record may be accurate, inaccurate, incomplete, deceptive, outdated, misunderstood, deliberately fabricated or impossible to verify. The system must preserve those possibilities rather than convert every report into canon truth.

## 2. Scope and ownership

### 2.1 BP-21 owns

- Intelligence item, report, source-reference, assessment, analytical product and dissemination lifecycles.
- Source identity/alias references, source handling and source reliability assessments, including uncertainty and history.
- Information credibility and content-evaluation assessments, separately recorded.
- Intelligence grading frameworks and versioned evaluation vocabularies once configured.
- Raw intelligence receipt, registration, provenance, handling restrictions and validation.
- Collation of related information while preserving the identity and independence of original reports.
- Analytical hypotheses, competing explanations, confidence, caveats, assumptions, gaps and review dates.
- Intelligence requirements, collection requests and tasking interfaces where authorised; operational collection remains owned by the relevant source division.
- Intelligence holdings, subject/topic/place/entity indexing, relationship references and historical validity.
- Intelligence dissemination, recipient lists, purpose, restrictions, acknowledgements, onward-disclosure conditions and audit.
- Intelligence review, expiry, supersession, correction, withdrawal, retention and disposal requests under configured policy.
- Intelligence-specific access classifications, compartmentation and source protection.
- Links between intelligence and cases, incidents, investigations, surveillance, evidence, forensics, interviews and external contextual records.
- Intelligence reporting and products for authorised operational, tactical and strategic audiences.
- Separation of intelligence from evidence, allegations, observations, source statements, analytical conclusions and adjudicated findings.

### 2.2 Explicit ownership boundaries

| Concern | Owner | BP-21 contract |
|---|---|---|
| Canonical person identity and person lifecycle | BP-03 | References canonical IDs; source aliases are not duplicate people |
| Households, relationships and social-network semantics | BP-36 | References relationship records; does not turn association into guilt |
| Business registry, premises and commercial facts | BP-04 | References business IDs and source records; does not create authoritative business facts |
| Police hierarchy, authority and governance | BP-05/BP-30 | Uses configured authority and policy |
| Police personnel and qualifications | BP-06 | References authorised analyst/source-handler identities |
| Unit and deployment capacity | BP-08 | Intelligence tasking does not allocate operational personnel |
| Patrol observation | BP-10 | Patrol owns its original operational record; BP-21 may receive a sourced copy/reference |
| Call taking, dispatch and incident management | BP-11/BP-12 | Own call/dispatch/incident lifecycle; intelligence may inform but not overwrite them |
| Crime taxonomy and classification | BP-13 | Owns offence definitions and classification |
| Hidden occurrence truth and crime generation | BP-14 | Remains secret; intelligence cannot query or disclose generator truth |
| Case identity and lifecycle | BP-15 | Owns case creation, status, assignment and closure |
| Investigation strategy, leads, tasks and decisions | BP-16 | Owns investigative action; intelligence supplies information, not instructions |
| Victim/witness roles and safeguarding | BP-17 | Owns participant role/support; intelligence references but does not redefine |
| Suspect/offender roles and procedural status | BP-18 | Owns suspect/offender status; intelligence does not establish guilt or status |
| Interviews and statements | BP-19 | Owns interview session and statement source records |
| Surveillance and observation source records | BP-20 | Owns raw observation/capture and technical source metadata |
| Crime scene control and scene records | BP-22 | Owns scene management and scene observations |
| Evidence/exhibits and continuity | BP-23 | Owns evidential exhibits and custody; intelligence does not become an exhibit by relabelling |
| Forensic methods/results | BP-24 | Owns examination and expert interpretation; intelligence may reference results with provenance |
| Arrests and warrants | BP-25 | Owns arrest/warrant processes |
| Custody | BP-26 | Owns custody records |
| Legal procedure, disclosure and prosecution | BP-27 | Owns disclosure/legal decisions; intelligence handling restrictions are supplied as metadata |
| Court proceedings and findings | BP-28 | Owns judicial findings; intelligence is not a finding |
| Corrections | BP-29 | No custodial/corrections ownership |
| Professional standards | BP-31 | Owns misconduct/standards; intelligence records may be reviewed under authority |
| Simulation causality and NPC behaviour | BP-35 | May generate plausible reports and source behaviour, never hidden truth leakage |
| Canonical time and scheduling/pause | BP-37 | Owns simulation clock; all intelligence timers freeze while player absent |
| Records and databases | BP-38 | Owns schemas, identifiers and authoritative record infrastructure |
| Persistence and recovery | BP-39 | Owns durable storage and recovery |
| Interface and maps | BP-40 | Presents authorised intelligence products; text remains sufficient |
| Notifications and reporting | BP-41 | Delivers authorised notices; no secret leakage in previews |
| Security and permissions | BP-42 | Owns global access control and hidden-information protection |
| Testing and quality assurance | BP-43 | Executes acceptance tests |
| Configuration and change control | BP-44 | Controls versioned intelligence policy/configuration |

### 2.3 Non-goals

BP-21 is not a general-purpose fact database, evidence store, criminal guilt classifier, automated suspect generator, predictive policing verdict engine, surveillance platform, forensic laboratory, investigative command system, case-management system or hidden-truth query interface. It does not instruct the player what to investigate next. It does not automatically convert intelligence into leads, warrants, arrests, charges or court findings.

## 3. Binding invariants

1. Intelligence is not evidence, established fact, an allegation proven true, an offence finding or a conviction.
2. Every intelligence item preserves its originating source, source version/identity or explicit unknown status, receipt path and provenance.
3. Source reliability and information/content credibility are evaluated separately.
4. An assessment records the framework and version used; no silent grading vocabulary changes.
5. Every assessment preserves uncertainty, caveats, limitations, assumptions and review date where applicable.
6. Conflicting and exculpatory information is preserved; no automatic suppression or averaging.
7. Multiple reports repeating one originating claim are not automatically independent corroboration.
8. An analyst's inference is attributed and distinguishable from source statement and recorded fact.
9. An intelligence product must trace to the exact underlying items and versions used.
10. Corrections are additive and attributed; original submissions and prior assessments remain historically available to authorised users.
11. A source's identity may be protected by alias/compartment, but the underlying identity is not fabricated or duplicated.
12. Source protection does not erase provenance from appropriately authorised audit and review.
13. A source handler's opinion is not automatically a source reliability grade.
14. Intelligence cannot create or change a BP-18 suspect/offender role.
15. Intelligence cannot create a BP-15 case or BP-16 investigative task automatically unless an explicitly configured and authorised workflow is invoked; even then the decision is attributable and reviewable.
16. A lead, allegation, report, intelligence item, evidence item, fact and court finding remain distinct types.
17. Intelligence does not acquire evidential continuity merely because it is copied into a case.
18. Raw surveillance, interview, patrol, forensic, scene and business records remain owned by their source divisions.
19. BP-21 may store a reference or authorised intelligence derivative, not silently take ownership of the source record.
20. No relationship, contact, family, business, cultural, religious, political, employment or geographic association alone establishes criminality.
21. No demographic, protected or sensitive characteristic may be used as a proxy for suspicion or risk.
22. No unsupported prediction or risk score is presented as objective fact.
23. Hidden BP-14 occurrence truth is inaccessible to analysts, NPCs and player-facing intelligence products.
24. Exact standalone lowercase `bingo` is the only hidden culprit/perpetrator/accomplice reveal trigger.
25. No intelligence product, index, label, metadata, notification, count, graph, summary or export indirectly signals hidden offender identity.
26. No unsolicited investigation hints, next-step recommendations, suspect rankings or forced leads are generated.
27. Player agency remains intact: the player chooses what information to request, assess, compare and act upon.
28. NPC knowledge is bounded by information actually received, observed or legitimately accessed.
29. Every living person counts once under the 10,000-person cap; relevant persons are permanently promoted by BP-03, never downgraded.
30. No simulation time, source activity, review timer, expiry, scheduled dissemination or intelligence-processing queue advances while the player is outside the simulation.
31. Text-first intelligence functions remain complete; maps, graphs and link charts are optional representations.
32. All changes, access, assessment, dissemination, correction, review and disposal are attributable and auditable.
33. Storage optimisation cannot discard source provenance, uncertainty, conflict, version history, restrictions or relationships.
34. An absence of intelligence is not evidence that an event, person, relationship or threat does not exist.
35. Intelligence products must declare scope, date/time basis, information cut-off and limitations.

## 4. Conceptual information model

All identifiers are stable, opaque and allocated under BP-38. Prefixes are illustrative pending the common identifier policy.

| Entity | Identifier | Meaning |
|---|---|---|
| Intelligence item | intelligence_item_id | Registered information submission or report |
| Source identity | intelligence_source_id | Source person, organisation, system or explicit unknown |
| Source alias | source_alias_id | Compartmented reference to a source identity |
| Source assessment | source_assessment_id | Assessment of source reliability and handling history |
| Content assessment | content_assessment_id | Assessment of the specific information's credibility |
| Intelligence requirement | intelligence_requirement_id | Defined information need, owner and scope |
| Collection request | intelligence_collection_request_id | Authorised request to a source division |
| Intelligence holding | intelligence_holding_id | Indexed grouping/subject record |
| Link/association | intelligence_link_id | Attributed relationship between items/entities |
| Analytical assessment | intelligence_assessment_id | Reasoned evaluation with competing explanations |
| Hypothesis | intelligence_hypothesis_id | Explicitly uncertain analytical proposition |
| Product | intelligence_product_id | Versioned analytical output |
| Dissemination | intelligence_dissemination_id | Controlled release to recipients |
| Recipient | intelligence_recipient_id | Person, unit or authorised organisation reference |
| Restriction | intelligence_restriction_id | Handling, access, purpose or onward-sharing condition |
| Review | intelligence_review_id | Scheduled or event-triggered review |
| Correction | intelligence_correction_id | Additive amendment, retraction or qualification |
| Challenge | intelligence_challenge_id | Formal contest of source, content or analysis |
| Audit event | intelligence_audit_id | Access and material state transition |

### 4.1 Common fields

As applicable: stable ID; schema/configuration version; source identity/alias; source record ID; source type; received-by actor; received-at time; event/effective time; record time; location; person/business/place references; case/incident references; original text/content reference; language; translation status; classification; handling caveats; source reliability assessment; content credibility assessment; confidence; uncertainty; provenance; linked items; analytical author; reviewer; status; review date; retention status; correction/supersession link; access policy; dissemination history.

Do not duplicate BP-03 biographies, BP-04 business records, BP-19 interview recordings/statements, BP-20 surveillance originals, BP-22 scene records, BP-23 exhibits or BP-24 laboratory records. Use exact canonical references and clearly labelled intelligence derivatives.

## 5. Intelligence information classes

The system must distinguish at least:

- **Raw report:** information as received, preserving source wording and format.
- **Source statement:** claim attributed to a source, not independently established.
- **Observation reference:** a reference to an observation record owned by BP-10/BP-20 or another source division.
- **Allegation:** an assertion that wrongdoing occurred; not proof.
- **Intelligence item:** registered information retained for evaluation or use.
- **Source assessment:** assessment of the source's reliability, access, history and limitations.
- **Content assessment:** assessment of the particular information's credibility, plausibility, consistency and corroboration.
- **Intelligence analysis:** attributed reasoning that considers multiple items and uncertainty.
- **Hypothesis:** a proposition being considered, not a conclusion.
- **Intelligence product:** a versioned output prepared for a defined audience and purpose.
- **Lead:** an investigative opportunity or line of enquiry owned by BP-16; not a synonym for intelligence.
- **Evidence:** an item managed under BP-23 and applicable source divisions.
- **Established fact:** a fact supported under its authoritative record process; not created by an intelligence grade.
- **Adjudicated finding:** a finding owned by BP-28 or other configured authority.

Conversion between classes is never silent. If an intelligence item leads to a separately created investigative lead, evidence exhibit or court record, the receiving division creates its own record and preserves the source link and provenance.

## 6. Source registration, identity and protection

Sources may include named individuals, confidential human sources, anonymous reporters, public records, organisations, media outlets, technical systems, partner agencies, internal police records or unknown/unverified origins. Source type and identity certainty are separate.

A source record may contain identity references, aliases, handler, access/knowledge basis, contact history, source capability, restrictions, risk/safety notes, reliability history, incentives or possible bias where evidenced, verification history and compartmentation. Sensitive details are access-controlled and minimised. A source alias is a protected reference, not a second canonical person.

Source states may include proposed, registered, active, inactive, restricted, suspended, compromised, deceased/closed, unknown and archived. State transitions require actor, authority, reason and effective time. A source's status does not automatically determine the reliability of every report.

Unknown source identity is valid. Do not invent a person to fill missing source details. If a source is later identified, link the prior alias/unknown record to the canonical BP-03 person through an auditable resolution event; do not rewrite original submissions.

## 7. Receipt, registration and provenance

Each received item records:
- exact originating source or explicit unknown;
- original source reference and originating record identifier, if available;
- receiving actor/system and receipt channel;
- received time and claimed event time, separately;
- original content or immutable content reference;
- language, translation and transcription status;
- whether content is verbatim, paraphrased, summarised or machine-extracted;
- any intermediary, handler or relay;
- source access/knowledge basis if known;
- handling caveats, classification and restrictions;
- related case, incident, operation or requirement references;
- initial uncertainty and missing context;
- duplicate/possible-duplicate links without deletion;
- integrity metadata and audit.

A later transcription, translation, redaction or summary is a derivative. Preserve the original as received. If the original cannot be retained for a configured reason, preserve the exact reason, authorising decision, available integrity details and limitations; never imply the derivative is the original.

Receipt does not imply verification, acceptance, credibility, relevance or permission to disseminate.

## 8. Source reliability and content credibility

Source reliability and information credibility are two independent assessment dimensions.

### 8.1 Source reliability

May consider demonstrated access to the information, past accuracy, consistency, opportunity to observe, motive, possible bias, coercion, inducement, personal interest, intermediary chain, source handling history and known limitations. Each factor is recorded only where supported. Lack of history means unknown, not unreliable or reliable by default.

### 8.2 Content credibility

May consider internal consistency, specificity, plausibility, contemporaneous detail, independent corroboration, contradiction, compatibility with known facts, source access, technical limitations and alternative explanations. A report may come from a generally reliable source yet contain inaccurate information; an unknown source may provide information later independently corroborated.

### 8.3 Grading framework

The precise grade vocabulary and matrix are configurable under BP-30/BP-44 and remain an open decision. The design requires:
- versioned source reliability scale;
- versioned content credibility scale;
- explicit unknown/not assessed/not applicable states;
- separate confidence in analytical conclusion;
- defined meaning for each grade;
- reviewer and assessment date;
- reasoned basis and supporting/contradictory references;
- no numeric score unless the scale and interpretation are approved;
- no automatic arithmetic averaging across incomparable sources;
- no grade inheritance from one report to another.

Never encode a grade as a fact or use a single opaque letter/number without its framework version and explanation.

## 9. Collation, duplication and corroboration

Collation groups information for comparison while retaining each item's original identity, source, wording, time and assessment. Similar reports may share a common origin, repeat hearsay or derive from one press release, chat, witness or database. The system must represent possible source dependence and intermediary chains.

Independent corroboration requires an explicit assessment of independence and basis. Several copies of one claim are not several independent sources. Corroboration can be partial and does not validate every detail. Contradiction does not automatically invalidate an entire source; it may affect only a particular claim, time or detail.

Duplicate detection produces a proposed relationship or duplicate candidate. It does not delete or merge originals without an authorised, attributable decision. If items are consolidated into a product, all source items remain individually traceable.

## 10. Intelligence requirements and collection requests

An intelligence requirement describes a defined information need, owner, rationale, scope, priority, time horizon, review date and authorised audience. It must not contain a hidden answer or covertly prescribe a suspect.

A collection request is a controlled request to the division that owns the source activity:
- BP-10 for patrol activity records;
- BP-19 for interview/statement source material;
- BP-20 for surveillance and observation sources;
- BP-22 for scene records;
- BP-23 for exhibit/source custody records;
- BP-24 for forensic results;
- BP-04 for business/premises information;
- BP-03/BP-36 for person and relationship context through authorised interfaces;
- BP-11/BP-12 for call/incident records.

BP-21 records request, purpose, scope, authority, recipient division, response status, limitations and returned source references. The receiving division decides whether and how it can fulfil the request under its own authority and operational rules. A request is not a command to collect, does not grant access, and does not guarantee a result.

BP-21 does not operate surveillance, interview people, search scenes, seize exhibits or conduct forensic examinations. It may receive a returned item or source reference and evaluate it as intelligence.

## 11. Analysis, hypotheses and confidence

An analytical assessment identifies the question, scope, information cut-off, author, audience, method, sources considered, assumptions, limitations, gaps, competing explanations, contradictions, confidence and review date. It must distinguish:
- what the source directly stated;
- what an original record actually contains;
- what has been independently verified;
- what is inferred;
- what is hypothesised;
- what remains unknown;
- what is contradicted;
- what is outside the assessment scope.

Hypotheses are explicit, versioned and attributed. A hypothesis may be created, supported, weakened, challenged, superseded, withdrawn or left unresolved. No hypothesis becomes fact by repetition or by being the only hypothesis currently recorded.

Confidence describes the strength of the analytical judgement given the information and method, not certainty that the underlying event occurred. It must state the scale/version, rationale and key limitations. Avoid false precision. Where the evidence base is weak or contradictory, the product must say so.

Analytical methods may include chronology comparison, link analysis, pattern analysis, network/context mapping, geospatial comparison, trend analysis, source comparison, hypothesis testing and structured uncertainty review. The method, assumptions, input versions and limitations must be recorded. A visual graph is not proof of a relationship.

## 12. Links, associations and entity resolution

Intelligence links may connect people, aliases, businesses, premises, vehicles, objects, events, cases, incidents, sources, reports and organisations. Each link records:
- subject and object IDs or unresolved references;
- relationship type;
- source item(s);
- author/assessor;
- confidence and uncertainty;
- effective period and observation/record time;
- whether direct, reported, inferred or disputed;
- alternative explanations and challenge status;
- access classification and review date.

Do not convert a contact, family, household, employment, business, cultural, religious, political, social or geographic connection into criminal association. Association does not establish knowledge, intent, participation or guilt. A link inferred from common location or communication may be coincidental, incomplete or misattributed.

Entity resolution must distinguish canonical identity from alias, same-name candidate, mistaken identity and unresolved reference. BP-03 owns canonical identity. BP-21 records the basis and confidence of a proposed link and refers resolution through the proper owner. Never merge person records solely because intelligence items use similar names, phone numbers, appearance or addresses.

## 13. Intelligence products and versioning

Products may include source summaries, subject profiles, threat/risk assessments where approved, network assessments, incident pattern summaries, location assessments, business-context assessments, strategic assessments, tactical briefings and case-linked intelligence reports.

Every product declares:
- product ID and version;
- author, reviewer and approving authority if required;
- audience, purpose and information cut-off;
- source items and exact versions;
- source/content grades and framework versions;
- analytical method, assumptions and confidence;
- contradictions, gaps and caveats;
- restrictions and handling instructions;
- created/reviewed/expiry dates;
- superseded or withdrawn status;
- distribution history.

A product is not a replacement for its source items. Revisions create a new version and preserve the old version and its distribution record. A recipient who received a superseded product may require an authorised correction notice. A withdrawn product remains auditable and must not silently disappear from historic records.

## 14. Dissemination and handling restrictions

Dissemination is purpose-bound and recipient-specific. Record sender, approving authority where required, recipient identity/role/unit, purpose, exact product/item version, date/time, delivery channel, classification, restrictions, onward-sharing conditions, acknowledgement, refusal, recall/correction and access history.

Handling restrictions may include compartmentation, named-recipient access, source identity protection, no onward disclosure, limited purpose, time-limited access, redaction requirements and restrictions on copying/export. Exact classification labels and rules remain configurable under BP-30/BP-42.

A product's existence does not mean every officer may see it. A recipient's access to one product does not grant access to all underlying source identities or unrelated holdings. Search results, counts, graph nodes, notifications, autocomplete, previews, exports, backups and AI context must apply the same access rules.

Dissemination is not proof of truth, authority to conduct an operation, or an investigative instruction. A recipient's acknowledgement confirms receipt only, not agreement or verification.

## 15. Challenges, corrections, retractions and review

Any authorised user or source owner may challenge an intelligence item or assessment through a recorded process. A challenge identifies the disputed item/version, challenger, basis, supporting references, requested action and status.

Possible outcomes include upheld, partly upheld, not upheld, unresolved, superseded, corrected, retracted or withdrawn. Preserve the original item and prior assessments. A correction adds a new version or linked correction event; it does not silently erase history.

Reviews may be triggered by a review date, new contradictory information, source compromise, identity correction, court outcome, source-owner correction, changed circumstances, expiry of relevance or policy. Review does not automatically delete an item. The retention/disposal decision is separately authorised under BP-30/BP-38/BP-39.

When an intelligence product has been disseminated, corrections and withdrawals must be linked to the recipient list and may generate a correction/withdrawal notice subject to access policy. Record delivery and acknowledgement.

## 16. Intelligence, evidence and legal boundaries

Intelligence can inform an investigative decision but does not itself prove the underlying claim. A copy of intelligence placed in a case file remains intelligence unless the relevant source material is separately obtained, registered and managed by the authoritative division.

BP-23 owns exhibits, evidential status and continuity. BP-19 owns original interview recordings/statements. BP-20 owns surveillance originals and capture metadata. BP-22 owns scene records. BP-24 owns forensic examination and interpretation. BP-27 owns disclosure and legal process. BP-28 owns court proceedings and findings.

An intelligence product may identify a source record that could be relevant to a case. It must not relabel it as evidence, change its provenance, assert admissibility, or imply that a court accepted it. If a legal process requires disclosure or restricted handling decisions, BP-27 decides under configured fictional policy. BP-21 supplies complete provenance and restrictions without deciding the legal outcome.

## 17. Relationship with cases, incidents and investigation

An intelligence item may be unconnected to a case, associated with one or more incidents, linked to several cases, or relevant to a citywide/strategic topic. Case links are references, not ownership transfer.

BP-15 owns case identity and lifecycle. BP-16 owns investigative leads, tasks, strategy and decisions. BP-21 may receive a request from BP-16 or disseminate a product to an authorised investigator. It must not automatically open a case, assign an investigator, create a lead or tell the player what action to take.

If a user/investigator chooses to create a lead from intelligence, BP-16 records that separate decision and its rationale, preserving the intelligence source and uncertainty. An intelligence item can be assessed as unreliable and still remain relevant as a record of what was reported.

## 18. NPC knowledge and intelligence generation

NPC source, handler, analyst and recipient knowledge is bounded by role, access, actual receipt and in-world time. An analyst cannot assess a report they have not received. A recipient cannot know a restricted product they were not authorised to access. A source cannot know facts outside their plausible observation, access or communication.

Generated intelligence must arise from a plausible source and causal information path: the source encountered or received information, recorded or communicated it, a handler/receiver obtained it, and an authorised process registered it. The simulation must preserve the possibility of error, deception, bias, hearsay, delay, incomplete context and contradiction.

BP-14 hidden occurrence truth must never be used to create a report that conveniently points to the true offender, to grade a source, to rank suspects, or to guide the player. BP-35 may generate a source's mistaken or incomplete account only from that NPC's plausible knowledge and the actual world information available to them. No NPC is omniscient.

## 19. Player agency and exact hidden-truth boundary

The player may inspect authorised holdings, request records, compare items, review assessments, question confidence, create authorised analytical work and decide what to do with the information. The interface must not produce unsolicited suspect rankings, culprit likelihood lists, next-step recommendations, investigative hints or forced leads.

The exact reveal trigger is a standalone player input of lowercase `bingo`, with no punctuation, surrounding whitespace or additional words. Before that trigger:
- no culprit, perpetrator or accomplice identity is disclosed directly or indirectly;
- hidden BP-14 truth is excluded from intelligence item creation, source grading, link analysis, product wording, metadata, IDs, labels, counts, graph layouts, sort order, notifications, exports and NPC prompts;
- no intelligence grade or confidence score is secretly calibrated against hidden truth;
- no report is marked incriminating/exculpatory because of hidden truth;
- no source is made reliable or unreliable solely to steer the player;
- no system suggests what the player should investigate next;
- no hidden identity can be inferred from suppressed records, missing counts or error messages.

After a valid trigger, other access controls, provenance and distinctions between allegation, evidence and adjudicated finding remain in force. The trigger reveals hidden solution identity only; it does not rewrite the record.

## 20. Security, access and audit

BP-42 owns global access and secret-handling rules. BP-21 defines domain-specific permission needs, including:
- intelligence.read.index
- intelligence.read.item
- intelligence.read.restricted
- intelligence.read.source_identity
- intelligence.read.source_history
- intelligence.read.assessment
- intelligence.read.product
- intelligence.read.audit
- intelligence.create.item
- intelligence.register.source
- intelligence.assess.source
- intelligence.assess.content
- intelligence.collate
- intelligence.analyse
- intelligence.create.product
- intelligence.review
- intelligence.challenge
- intelligence.correct
- intelligence.retract
- intelligence.disseminate
- intelligence.approve.dissemination
- intelligence.manage.restrictions
- intelligence.export
- intelligence.manage.retention

Permissions are separate: reading an item does not grant source identity access, analysis, correction, approval, dissemination, export or deletion. Access decisions are purpose-bound and apply to direct records and every derived surface.

Audit source registration, item receipt, viewing of restricted items, source identity reveal, search, assessment, product creation, correction, challenge, dissemination, export, access denial, emergency access, retention and disposal. Record actor, authority, purpose, target/version, action, time, outcome and relevant context. Credentials and secrets never enter intelligence content, source control or narrative records.

## 21. Time, scheduling and pause

BP-37 is the sole canonical simulation clock. Preserve event time claimed by source, actual receipt time, record time, assessment time, dissemination time, review date and effective time as distinct values. Time zones, source clock offsets and uncertainty are explicit where relevant.

While the player is outside the simulation:
- no source generates or communicates new simulated information;
- no intelligence collection request progresses;
- no analyst/NPC reads, collates, assesses or disseminates items;
- no review, expiry, retention or disposal timer advances;
- no scheduled briefing, notification or acknowledgement occurs;
- no source status, reliability history or intelligence confidence changes;
- no background AI processing advances.

On return, restore exact state. No off-screen catch-up, invented reports or elapsed deadlines are allowed.

## 22. Population, identity and sensitive context

All identified persons use BP-03 canonical IDs. Unknown or aliased sources do not create shadow people. If a person becomes materially relevant to a case or police activity, BP-03's permanent promotion rules apply; promotion is never reversed. Total living population, including officers and all other persons, remains capped at 10,000.

Business, organisation, household, relationship, social and civic references use BP-04/BP-36 canonical records. Intelligence does not create duplicate businesses or organisations. Sensitive personal information is minimised and access-controlled. A person's protected or sensitive characteristic, lawful association, identity group, religion, political opinion, family status, employment or residence is not a proxy for suspicion.

## 23. Persistence, records and storage efficiency

BP-38 owns identifiers, schema and record governance; BP-39 owns persistence/recovery. BP-21 owns intelligence semantics and lifecycle.

Preserve:
- original received item and source content reference;
- source identity/alias and access/knowledge basis;
- receipt channel, time, intermediary chain and provenance;
- source and content assessments separately, with framework versions;
- all contradictions, corroboration/dependence analysis and uncertainty;
- hypotheses, assumptions, analytical method and confidence rationale;
- exact source item versions used in each product;
- product versions, recipients, restrictions and dissemination history;
- challenges, corrections, retractions and review decisions;
- access and audit history;
- canonical entity references and relationship provenance;
- time-validity and review/retention state.

Use references rather than duplicate canonical records or binary source material. Deduplication must preserve independent source claims, intermediary chains, access compartments and version histories. Compact representation may reduce redundant encoding but must never collapse separate reports into one unsupported claim or discard uncertainty, conflict or provenance.

Writes are atomic across item, assessment, product, dissemination and audit records. Idempotent retry must not create duplicate submissions or duplicate dissemination events. Restore validates references and integrity metadata. Missing source material is explicitly flagged; never substitute unrelated content.

## 24. Interface and reporting

Text-first capabilities are mandatory:
- register and search authorised intelligence items;
- inspect source and content assessments separately;
- view source provenance and restrictions subject to access;
- compare related/contradictory items without losing original records;
- inspect intelligence requirements and collection-request status;
- create and review analytical assessments/hypotheses;
- create versioned products with source traceability;
- disseminate to authorised recipients and record acknowledgements;
- challenge, correct, retract, review and withdraw items/products;
- inspect audit, review dates, retention and handling restrictions.

Reports may include source register, intelligence item history, source reliability history, content credibility assessment, collated information, contradiction matrix, analytical assessment, intelligence product, dissemination receipt, review/challenge log and correction/withdrawal notice. Each report states audience, scope, information cut-off, source versions, assessment framework, uncertainty and restrictions.

Optional link charts, timelines, maps and pattern visualisations are derived from canonical records. They must label inferred/disputed links and uncertainty, enforce permissions and never imply guilt from association. Visuals are optional and cannot be required to understand or operate the system.

## 25. Inputs, outputs and event contracts

**Inputs:** BP-03 person IDs; BP-04 business/premises/organisation records; BP-10 patrol records; BP-11/BP-12 call and incident records; BP-13 offence taxonomy; BP-15 case references; BP-16 investigative requests; BP-17/BP-18 participant roles; BP-19 interview sources; BP-20 surveillance sources; BP-22 scene records; BP-23 exhibit references; BP-24 forensic results; BP-27 disclosure restrictions; BP-30 policy; BP-35 plausible NPC/world information; BP-36 relationship context; BP-37 canonical time; BP-38/BP-39 records/persistence; BP-42 access controls.

**Outputs:** registered intelligence items; source and content assessments; intelligence requirements/collection requests; collated holdings; analytical assessments and hypotheses; intelligence products; dissemination records; challenges/corrections/retractions; review and retention events; audit events; source references returned to authorised consumers.

Minimum event types: intelligence_received/registered/validated; source_registered/aliased/restricted/suspended/compromised/resolved; source_assessed; content_assessed; item_linked/duplicate_candidate/independence_assessed; requirement_created/updated/closed; collection_requested/accepted/declined/fulfilled/failed; assessment_created/revised/challenged; hypothesis_created/supported/weakened/superseded/withdrawn; product_created/revised/approved/withdrawn; dissemination_requested/approved/sent/acknowledged/refused/recalled; challenge_opened/resolved; correction_added/retraction_recorded; review_due/completed/deferred; retention_hold_applied/released; disposal_requested/approved/completed; access_granted/denied; restore_verified/reconciliation_failed.

Each event includes event ID, actor, authority, purpose, target ID/version, event and record time, effective interval, provenance, prior/resulting state, schema/configuration version and idempotency key.

## 26. Failure handling and edge cases

- Unknown source: preserve unknown; do not fabricate identity.
- Anonymous source later identified: link to canonical person with resolution history; preserve original alias.
- Same person uses multiple aliases: maintain alias links without duplicate canonical people.
- Two people share a name: do not merge without adequate identity resolution.
- Source has no reliability history: mark unknown/not assessed.
- Source generally reliable submits inaccurate detail: retain separate content assessment.
- Unknown source provides corroborated detail: assess the content independently.
- Source is motivated or biased: record supported basis and uncertainty, not automatic dismissal.
- Source has limited access: preserve access boundary and indirect/hearsay chain.
- Several reports repeat one origin: represent dependence; do not count as independent corroboration.
- Reports partially corroborate: specify which details are supported.
- Reports conflict: preserve both and assess the scope of conflict.
- Report is later disproved: append correction/retraction and notify authorised recipients.
- Report cannot be verified: preserve unresolved status.
- Translated item is disputed: retain original and translation versions with translator/provenance.
- Machine extraction is wrong: preserve original and correct derived output.
- Timestamp is approximate: preserve interval/uncertainty.
- Event time differs from receipt time: store separately.
- Source identity is restricted: protect identity while retaining authorised audit trace.
- Handler changes: retain historical handler intervals.
- Source compromised: flag status and review affected reports; do not automatically delete them.
- Source dies or becomes inactive: historical information remains accessible under policy.
- Intelligence link is inferred: label inference and confidence; no factual relationship claim.
- Relationship is social/familial/business only: no criminal inference.
- Entity resolution is uncertain: preserve unresolved candidate.
- Intelligence item concerns multiple cases: use references; do not merge case records.
- Case closes: intelligence lifecycle remains independently governed.
- Product uses stale data: disclose information cut-off and review state.
- Product superseded: retain prior version and recipients.
- Recipient refuses or fails to acknowledge: record outcome without assuming receipt.
- Onward sharing is prohibited: prevent or flag attempted dissemination under policy.
- Recipient loses role/access: re-evaluate access to future and stored items.
- Search count reveals restricted item: enforce access at aggregate/query layer.
- Intelligence is copied to case: preserve intelligence classification and source reference.
- Intelligence is tendered as evidence: BP-23/BP-27 process must create/manage appropriate records; no relabelling.
- A lead is created: BP-16 records separate decision and rationale.
- Hidden truth appears in a generated source report: reject/suppress and audit; never expose.
- NPC analyst has not received item: cannot reference or assess it.
- Player pauses: all queues, reviews and source activity freeze.
- Duplicate receipt retry: idempotent; no duplicate item.
- Partial product/dissemination transaction: atomic rollback or explicit incomplete state.
- Restored source reference is missing: flag unresolved; do not substitute.
- Storage compaction merges similar reports: prohibited unless original distinct items and dependence are preserved.
- Retention expiry occurs while paused: no expiry progression until simulation resumes.
- Correction notice cannot reach recipient: preserve attempted delivery and unresolved status.
- Access denied: do not disclose record existence unless policy permits.

## 27. Dependencies and failure contracts

| Dependency | Contract | Failure behaviour |
|---|---|---|
| BP-03/BP-04/BP-36 | Canonical persons, businesses, organisations and relationships | Preserve unresolved references; do not create duplicates |
| BP-10/BP-11/BP-12 | Patrol/call/incident source records | Reference source-owned records; no overwrite |
| BP-13/BP-14 | Offence taxonomy and hidden occurrence generation | Use taxonomy only; never access hidden truth |
| BP-15/BP-16 | Case and investigative workflow | No automatic case/lead/task creation |
| BP-17/BP-18 | Victim/witness/suspect roles | No role or guilt inference |
| BP-19/BP-20/BP-22 | Interview, surveillance and scene sources | Preserve exact source ownership and provenance |
| BP-23/BP-24 | Evidence and forensic records | No evidence/forensic status by intelligence relabelling |
| BP-27/BP-28 | Legal disclosure and court findings | Supply restrictions/provenance; do not decide outcome |
| BP-30/BP-42 | Policy and access | Block undefined restricted handling; audit access |
| BP-35/BP-37 | Causal NPC knowledge and canonical time | No omniscience; freeze all progression |
| BP-38/BP-39 | Records and persistence | Atomic, versioned, recoverable and auditable records |
| BP-40/BP-41 | Interface and notifications | Enforce identical permissions and hidden-truth controls |
| BP-43/BP-44 | Testing and change control | No completion claim without evidence and approved configuration |

## 28. Acceptance tests

These are specified acceptance criteria, not executed results. BP-43 must execute them with reproducible evidence.

### Record classes and provenance
- **INTEL-AT-001** — Every intelligence item has a stable opaque identifier.
- **INTEL-AT-002** — Every item has an explicit source or unknown-source state.
- **INTEL-AT-003** — Original received content is retained or its non-retention reason is explicit.
- **INTEL-AT-004** — Receipt time and claimed event time are separate.
- **INTEL-AT-005** — Receiving actor/channel and intermediary chain are recorded.
- **INTEL-AT-006** — Verbatim, paraphrase, summary, translation and machine extraction are distinct.
- **INTEL-AT-007** — A derivative links to exact original item/version.
- **INTEL-AT-008** — Receipt does not automatically mark information verified.
- **INTEL-AT-009** — Receipt does not automatically authorise dissemination.
- **INTEL-AT-010** — Unknown provenance remains explicitly unknown.
- **INTEL-AT-011** — Duplicate candidates retain both original records.
- **INTEL-AT-012** — Provenance survives product creation and export.
- **INTEL-AT-013** — Original source text cannot be silently overwritten.
- **INTEL-AT-014** — Corrections are additive and attributable.
- **INTEL-AT-015** — Every material record change is auditable.

### Source identity and reliability
- **INTEL-AT-016** — Source identity and source alias are distinct.
- **INTEL-AT-017** — Source alias does not create a duplicate canonical person.
- **INTEL-AT-018** — Unknown source does not fabricate a person.
- **INTEL-AT-019** — Later source identification preserves prior alias/history.
- **INTEL-AT-020** — Same-name candidates are not automatically merged.
- **INTEL-AT-021** — Source reliability is distinct from content credibility.
- **INTEL-AT-022** — No source history yields unknown/not-assessed, not default grade.
- **INTEL-AT-023** — Source access/knowledge basis is recorded where known.
- **INTEL-AT-024** — Handler opinion is not silently substituted for source grade.
- **INTEL-AT-025** — Source bias or motive is attributed and evidence-based.
- **INTEL-AT-026** — Source status does not automatically determine report accuracy.
- **INTEL-AT-027** — Source compromise triggers review without deleting history.
- **INTEL-AT-028** — Source assessment identifies framework version.
- **INTEL-AT-029** — Source assessment has author, time and rationale.
- **INTEL-AT-030** — Source identity access is separately permissioned.

### Content assessment, corroboration and uncertainty
- **INTEL-AT-031** — Content assessment is separate from source reliability.
- **INTEL-AT-032** — Content assessment identifies supporting references.
- **INTEL-AT-033** — Content assessment identifies contradictions and limitations.
- **INTEL-AT-034** — Unknown content credibility remains unknown.
- **INTEL-AT-035** — A reliable source can provide inaccurate information.
- **INTEL-AT-036** — An unknown source can provide independently corroborated information.
- **INTEL-AT-037** — Repeated copies of one originating claim are not independent corroboration.
- **INTEL-AT-038** — Intermediary/relay chains are represented.
- **INTEL-AT-039** — Partial corroboration identifies exactly which details are supported.
- **INTEL-AT-040** — Contradictory accounts remain separately accessible.
- **INTEL-AT-041** — Conflicting information is not automatically averaged.
- **INTEL-AT-042** — Disproven information receives an additive correction/retraction.
- **INTEL-AT-043** — Unverified information remains unresolved.
- **INTEL-AT-044** — Every grade uses a versioned framework.
- **INTEL-AT-045** — Grade meanings are explicit and inspectable.
- **INTEL-AT-046** — Unknown/not-assessed/not-applicable are distinct states.
- **INTEL-AT-047** — No numeric score is invented without an approved scale.
- **INTEL-AT-048** — Confidence in analysis is distinct from source/content grades.
- **INTEL-AT-049** — Uncertainty and caveats survive summaries.
- **INTEL-AT-050** — No intelligence grade is represented as established fact.

### Analysis, hypotheses and links
- **INTEL-AT-051** — Every analytical assessment identifies author, scope and information cut-off.
- **INTEL-AT-052** — Analytical method and assumptions are recorded.
- **INTEL-AT-053** — Competing explanations are preserved.
- **INTEL-AT-054** — Hypothesis is distinct from conclusion and fact.
- **INTEL-AT-055** — Hypothesis revisions preserve prior versions.
- **INTEL-AT-056** — Confidence includes scale/version and rationale.
- **INTEL-AT-057** — False precision is not generated.
- **INTEL-AT-058** — Analytical gaps and unknowns are visible.
- **INTEL-AT-059** — Analyst inference is attributed to analyst.
- **INTEL-AT-060** — Source statement is not rewritten as analyst-established fact.
- **INTEL-AT-061** — Link records identify both endpoints or unresolved state.
- **INTEL-AT-062** — Link records identify source item and author.
- **INTEL-AT-063** — Inferred links are labelled as inferred.
- **INTEL-AT-064** — Disputed links remain marked disputed.
- **INTEL-AT-065** — Contact or proximity alone does not establish criminal association.
- **INTEL-AT-066** — Family, work or business links do not imply guilt.
- **INTEL-AT-067** — Protected characteristics are not used as suspicion proxies.
- **INTEL-AT-068** — Entity resolution is distinct from alias matching.
- **INTEL-AT-069** — BP-03 remains canonical identity owner.
- **INTEL-AT-070** — Intelligence links cannot merge canonical person records.

### Requirements, collection and source ownership
- **INTEL-AT-071** — Intelligence requirement has owner, purpose and scope.
- **INTEL-AT-072** — Requirement does not encode hidden solution or suspect.
- **INTEL-AT-073** — Collection request is distinct from operational collection.
- **INTEL-AT-074** — Request identifies recipient source division.
- **INTEL-AT-075** — Request does not grant access or operational authority.
- **INTEL-AT-076** — Declined or unfulfilled request remains recorded.
- **INTEL-AT-077** — BP-20 retains surveillance source ownership.
- **INTEL-AT-078** — BP-19 retains interview and statement source ownership.
- **INTEL-AT-079** — BP-22 retains crime-scene record ownership.
- **INTEL-AT-080** — BP-23 retains exhibit/custody ownership.
- **INTEL-AT-081** — BP-24 retains forensic method/result ownership.
- **INTEL-AT-082** — BP-10 retains original patrol observation ownership.
- **INTEL-AT-083** — BP-04 retains authoritative business registry ownership.
- **INTEL-AT-084** — Intelligence derivative links to exact source record/version.
- **INTEL-AT-085** — Source-owner correction is traceable in intelligence.
- **INTEL-AT-086** — Intelligence does not silently overwrite source records.
- **INTEL-AT-087** — Collection failure is not interpreted as absence of information.
- **INTEL-AT-088** — No operational collection occurs without source-division process.
- **INTEL-AT-089** — Intelligence request does not guarantee a result.
- **INTEL-AT-090** — No source record is relabelled as intelligence-owned original.

### Products and dissemination
- **INTEL-AT-091** — Every product has stable ID and version.
- **INTEL-AT-092** — Product declares audience and purpose.
- **INTEL-AT-093** — Product declares information cut-off.
- **INTEL-AT-094** — Product references exact source item versions.
- **INTEL-AT-095** — Product includes relevant uncertainty and caveats.
- **INTEL-AT-096** — Product records author and reviewer where required.
- **INTEL-AT-097** — Product revision preserves prior version.
- **INTEL-AT-098** — Superseded product remains historically traceable.
- **INTEL-AT-099** — Withdrawal does not erase distribution history.
- **INTEL-AT-100** — Dissemination records exact product/item version.
- **INTEL-AT-101** — Dissemination records sender, recipient, purpose and time.
- **INTEL-AT-102** — Recipient acknowledgement is not treated as agreement.
- **INTEL-AT-103** — Restricted onward disclosure is enforced.
- **INTEL-AT-104** — Correction notice links to prior recipients.
- **INTEL-AT-105** — Failed correction delivery remains unresolved and visible.
- **INTEL-AT-106** — Product access does not automatically grant source identity access.
- **INTEL-AT-107** — Search previews enforce same access restrictions.
- **INTEL-AT-108** — Counts and link charts do not reveal restricted holdings.
- **INTEL-AT-109** — Export preserves restrictions and provenance.
- **INTEL-AT-110** — Dissemination does not create an investigative instruction.

### Case, evidence and legal boundaries
- **INTEL-AT-111** — BP-15 remains case lifecycle owner.
- **INTEL-AT-112** — BP-16 remains investigative lead/task/decision owner.
- **INTEL-AT-113** — Intelligence does not automatically create a case.
- **INTEL-AT-114** — Intelligence does not automatically create a lead.
- **INTEL-AT-115** — A lead created from intelligence is a separate BP-16 decision.
- **INTEL-AT-116** — Intelligence does not create suspect/offender status.
- **INTEL-AT-117** — Intelligence is not automatically evidence.
- **INTEL-AT-118** — Copying intelligence into a case does not change its class.
- **INTEL-AT-119** — BP-23 owns exhibit continuity after accepted transfer.
- **INTEL-AT-120** — BP-27 owns disclosure/legal-process decisions.
- **INTEL-AT-121** — BP-28 owns judicial findings.
- **INTEL-AT-122** — Intelligence does not assert admissibility or conviction.
- **INTEL-AT-123** — Exculpatory intelligence is preserved alongside adverse information.
- **INTEL-AT-124** — Court outcome triggers review without rewriting source history.
- **INTEL-AT-125** — Case closure does not silently close intelligence holdings.

### Security, hidden truth, NPC knowledge and player agency
- **INTEL-AT-126** — Role-based permissions distinguish item, source identity and product.
- **INTEL-AT-127** — Read permission does not imply correction, export or dissemination.
- **INTEL-AT-128** — Sensitive reads and material changes are audited.
- **INTEL-AT-129** — Credentials/secrets never appear in intelligence records.
- **INTEL-AT-130** — NPC analyst cannot assess information not received.
- **INTEL-AT-131** — NPC source cannot know facts outside plausible access.
- **INTEL-AT-132** — BP-14 hidden truth is excluded from intelligence generation.
- **INTEL-AT-133** — No direct or indirect culprit identity leaks before exact trigger.
- **INTEL-AT-134** — Exact standalone lowercase bingo is the only reveal trigger.
- **INTEL-AT-135** — No hidden-truth-based source grade or confidence score is generated.
- **INTEL-AT-136** — No suspect ranking or culprit likelihood list is emitted.
- **INTEL-AT-137** — No unsolicited investigative hint or next-step recommendation is emitted.
- **INTEL-AT-138** — Player controls whether to act on intelligence.
- **INTEL-AT-139** — Optional visualisations preserve uncertainty and access control.
- **INTEL-AT-140** — Text-only operation remains fully functional.

### Time, population, persistence and QA
- **INTEL-AT-141** — All intelligence events use BP-37 canonical time.
- **INTEL-AT-142** — Event, receipt, record, assessment and dissemination times are distinct.
- **INTEL-AT-143** — No source/analysis/review queue advances while player is absent.
- **INTEL-AT-144** — No retention/expiry timer advances while paused.
- **INTEL-AT-145** — Resume restores exact state without off-screen catch-up.
- **INTEL-AT-146** — Every living person is counted once under 10,000 cap.
- **INTEL-AT-147** — Permanent BP-03 person promotion is never reversed.
- **INTEL-AT-148** — Unknown aliases do not create duplicate identities.
- **INTEL-AT-149** — Original, assessments, products and audit persist atomically.
- **INTEL-AT-150** — Idempotent retry does not duplicate items or dissemination.
- **INTEL-AT-151** — Restore verifies source references and integrity metadata.
- **INTEL-AT-152** — Missing source content is flagged, not replaced.
- **INTEL-AT-153** — Storage deduplication preserves independent source items.
- **INTEL-AT-154** — Compaction preserves uncertainty, conflicts and provenance.
- **INTEL-AT-155** — Correction and retraction histories survive restore.
- **INTEL-AT-156** — Access denial does not leak restricted record existence.
- **INTEL-AT-157** — Retention/disposal requires configured authority.
- **INTEL-AT-158** — Disposal is audited and cannot erase required provenance.
- **INTEL-AT-159** — No design test is reported as executed without BP-43 evidence.
- **INTEL-AT-160** — Acceptance test evidence identifies version, actor, time and result.

## 29. Source traceability

The original 52-division JSON remains unchanged. IDs below follow its 1-based division array and exact requirement/test ordering. The 52→44 crosswalk remains authoritative for all other mappings.

| Source ID | Original requirement/test | BP-21 implementation |
|---|---|---|
| S05.R03 | Generate consistent witness, victim, suspect and community connections without deterministic shortcuts. | Sections 2, 12, 22; relationship references are contextual and never guilt shortcuts; BP-36 owns relationship semantics. |
| S07.R03 | Ensure businesses create realistic employment, premises access, records, witnesses, transactions and police-relevant activity. | Sections 2, 10, 12, 25; business records are source inputs and context, not duplicate intelligence-owned facts. |
| S21.R02 | Generate schedules, attendance, public narratives and records that can affect incidents and investigations. | Sections 10, 12, 18, 25; civic/media information can be registered with source, time, context and uncertainty. |
| S29.R03 | Distinguish occurrence, report, allegation, intelligence, offence and proven finding. | Sections 3, 5, 16–17; explicit record-class boundaries. |
| S30.R02 | Support referrals, concurrent investigations, cold cases and related case work. | Sections 10, 17; intelligence may be linked across cases without merging case ownership or creating leads automatically. |
| S32.R03 | Support physical, digital, documentary, biological, trace and testimonial evidence. | Sections 5, 10, 16; BP-21 can reference intelligence derived from source records; BP-23/BP-24 retain evidence/examination ownership. |
| S33.R02 | Preserve chain of custody, continuity, contamination controls, provenance and interpretation limits. | Sections 7, 16, 23; intelligence references forensic/exhibit sources without replacing chain of custody or interpretation. |
| S35.R01 | Represent source grading, reliability, confidence, dissemination, restrictions, analytical products, links and review dates. | Sections 6–15, 20; full intelligence lifecycle and versioned grading. |
| S35.R02 | Separate intelligence from evidence and established fact. | Sections 3, 5, 16–17; strict class boundaries and acceptance tests. |
| S35.R03 | Preserve source provenance and uncertainty. | Sections 7–9, 11–15, 23; immutable source traceability and uncertainty preservation. |
| S35.T01 | Every intelligence item has source, confidence and handling status. | INTEL-AT-001–015, 021–050, 091–110, 126–160. |
| S36.R03 | Never treat absence of coverage as proof of absence. | Sections 3, 10, 18; surveillance gaps remain source-specific limitations, not negative proof. |
| S43.R02 | Separate hidden world truth from player-visible information and from NPC knowledge. | Sections 18–19; generation firewall and recipient knowledge constraints. |
| S43.R03 | Never disclose culprit/accomplice/perpetrator identities or hidden solution unless the player types exactly 'bingo'. | Sections 3, 19; exact standalone lowercase trigger and direct/indirect leak tests. |
| S43.T02 | NPC knowledge never exceeds their plausible information. | Sections 18–19; source/handler/analyst/recipient knowledge path and test. |
| S48.R02 | Protect hidden case truth and restricted personal information from player-facing leakage. | Sections 19–22, 24; permission and hidden-information boundaries. |

Cross-cutting rules X03, X05, X06 and X08 apply in full: time-valid facts; distinct fact/allegation/estimate/inference/intelligence/opinion/source statement/conclusion/finding; immutable originals and additive corrections; text-first sufficiency and optional visual consistency. The crosswalk remains authoritative for every other cross-cutting reference.

## 30. Open decisions and risk register

### Open decisions

1. Exact source reliability and content credibility grading vocabulary and matrix.
2. Analytical confidence scale, if any, and its interpretation.
3. Source types, source status lifecycle and source-handler roles.
4. Intelligence classification/compartmentation labels and handling caveats.
5. Dissemination approval matrix, recipient categories and onward-sharing rules.
6. Intelligence requirement priority and review periods.
7. Collection request approval and escalation rules.
8. Retention, review, expiry and disposal policy by intelligence class.
9. Challenge and correction authority and notification requirements.
10. Rules for sensitive personal information minimisation and access.
11. Whether strategic/tactical risk assessments are included and what safeguards apply.
12. AI-assisted collation/analysis boundaries and mandatory human review.
13. Exact source identity compartmentation and emergency access process.
14. Integration with BP-16 lead creation workflow without automatic conversion.
15. Storage architecture and binary/source-reference policy with BP-38/BP-39.

### Risk register

| Risk | Mitigation |
|---|---|
| Intelligence treated as fact | Explicit class boundaries and UI labels |
| Source reliability confused with content credibility | Separate assessments and tests |
| Circular reporting mistaken for corroboration | Origin/intermediary dependency graph |
| Uncertainty lost in summary | Mandatory caveat and provenance propagation |
| Association mistaken for guilt | Link semantics and non-inference rules |
| Hidden truth leaks through generated products | BP-14/BP-35/BP-42 firewall and adversarial tests |
| Restricted source identity exposed | Compartmented IDs and field-level access |
| Intelligence copied into evidence store | BP-23 ownership and explicit transfer |
| Old product remains in circulation | Versioned dissemination and correction notices |
| Off-screen analysis progresses | BP-37 pause/freeze invariant |
| Storage compression collapses separate claims | Preserve independent item IDs and source lineage |

## 31. Design completion checklist

- [ ] All BP-21 source requirements and tests in the 52→44 crosswalk are incorporated.
- [ ] Original 52-division source remains unchanged.
- [ ] Intelligence, allegation, evidence, fact and finding remain distinct.
- [ ] Source identity, alias, provenance and protection are specified.
- [ ] Source reliability and content credibility are separate.
- [ ] Grading and confidence frameworks are versioned and configurable.
- [ ] Collation preserves independence, contradiction and duplicate lineage.
- [ ] Requirements and collection requests do not perform source-division operations.
- [ ] Analysis preserves hypotheses, uncertainty and competing explanations.
- [ ] Entity and relationship links do not imply guilt.
- [ ] Products are versioned and traceable to exact sources.
- [ ] Dissemination is purpose-bound and audited.
- [ ] Challenges, corrections, retractions and reviews preserve history.
- [ ] Case, investigation, evidence and legal boundaries are explicit.
- [ ] NPC knowledge and hidden truth remain protected.
- [ ] Exact bingo rule and no-unsolicited-hints rule are enforced.
- [ ] Pause freezes all source, analysis and retention progression.
- [ ] 10,000-person cap and permanent promotion remain BP-03 governed.
- [ ] Text-first operation is complete; visuals are optional.
- [ ] Permissions, audit, persistence, recovery and storage efficiency are specified.
- [ ] All 160 acceptance tests await BP-43 execution.
- [ ] Open policy decisions remain explicit and unassumed.
- [ ] No Neon write, migration, seed, import or bulk write has been made or authorised.

## 32. Status and next dependencies

This is a complete division design draft, not approved policy or implementation evidence.

- Specification: **DESIGNED_DRAFT**
- User approval: **PENDING**
- Implementation: **NOT_STARTED**
- Test execution: **NOT_STARTED**
- Verification: **NOT_STARTED**
- Neon/database writes: **NONE; NOT AUTHORISED**

Next fixed division: **BP-22 — Crime Scenes**. BP-22 owns scene control, scene examination/search and scene records; BP-21 may receive and assess intelligence derived from scene sources without taking ownership of scene or evidence records.
