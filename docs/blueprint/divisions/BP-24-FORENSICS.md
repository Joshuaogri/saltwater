# BP-24 — Forensics

**Project:** Saltwater — fictional sovereign city-state, one city, one jurisdiction  
**Blueprint division:** BP-24 of the fixed 44-division structure  
**Specification:** DESIGNED_DRAFT | **Implementation:** NOT_STARTED | **Test execution:** NOT_STARTED | **Verification:** NOT_STARTED  
**Authority:** Fixed BP-01–BP-44 structure and unchanged 52-division source. No canon or division structure is changed.

## 1. Purpose

BP-24 defines the forensic and specialist examination capability available to Saltwater Police. It governs requests, triage, allocation, examination planning, methods, observations, measurements, raw results, interpretation, limitations, contamination controls, quality review, reporting and specialist conclusions. It serves investigations, scenes, custody, legal processes and court proceedings without becoming a second healthcare, university, laboratory-business or national scientific-institution simulator.

BP-24 owns forensic work and its outputs: examination records, method versions, examiner attribution, raw observations/results, analytical interpretation, limitations, quality review and reports. BP-23 owns exhibit identity, packaging, seals, custody, storage and transfers. BP-16 owns investigative strategy and inference; BP-27/BP-28 own legal process and court findings. A forensic conclusion is not a finding of guilt, a legal ruling or an automatic investigative answer.

## 2. Scope and exclusions

In scope: forensic discipline catalogue; specialist capability and resources; examination requests; triage and prioritisation; acceptance/rejection; scope and questions; examination plans; methods and versions; personnel qualifications; equipment and calibration references; observations and measurements; raw data; analytical results; interpretation; uncertainty and limitations; contamination prevention/detection; quality assurance; peer review; reporting; exhibits, samples and derivatives interfaces; specialist consultation; turnaround and work queues; cancellation, repeat and re-examination; disclosure and court interfaces; provenance, audit and persistence.

Out of scope: exhibit registration/custody/packaging/storage (BP-23); scene control/search/recovery (BP-22); investigative plans, hypotheses and conclusions (BP-16); intelligence grading (BP-21); surveillance capture (BP-20); interview originals (BP-19); medical treatment/healthcare operation (BP-04/BP-17/BP-26); arrest/seizure authority (BP-25); charging/disclosure process (BP-27); court admissibility, verdict and weight (BP-28); global clock (BP-37); schemas and persistence mechanics (BP-38/BP-39); security (BP-42).

## 3. Core distinctions

Keep separate: submitted item; exhibit version; sample; derivative; examination request; question; method; observation; measurement; raw instrument output; analytical result; interpretation; opinion; limitation; uncertainty; quality review; forensic report; investigative inference; legal submission; judicial finding. A result is not an interpretation; an interpretation is not an investigative conclusion; an investigative conclusion is not a court finding.

A forensic report states what was examined, by whom, when, under what method/version, what was observed or measured, what results were obtained, what they support, what they do not support, limitations, uncertainty, deviations and review status. Do not turn absence of a result into proof of absence. Do not infer identity, intent, guilt or innocence beyond the stated scientific scope.

## 4. Discipline catalogue

The catalogue is extensible and versioned. It may include biology/DNA; pathology and post-mortem liaison; toxicology; fingerprints and friction-ridge impressions; footwear and tyre impressions; trace materials, fibres, glass, paint and particulates; firearms/toolmarks; questioned documents and handwriting; digital device and media examination; audio/video/image examination; collision and vehicle examination; fire/explosion scene examination; chemical/material analysis; entomology; anthropology; odontology; environmental sampling; injury-pattern documentation; and other specialist fields.

A discipline entry defines scope, accepted material, capabilities, exclusions, required facilities/equipment, qualification levels, method catalogue, hazards, contamination controls, expected outputs, dependencies, capacity and referral capability. Catalogue inclusion does not imply every method, facility or specialist is currently available. Capabilities have effective dates and status.

## 5. Specialist resources and capability

A capability record identifies discipline, method, facility or mobile capability, equipment, trained personnel, qualification/competency status, operating conditions, capacity, availability, restrictions, maintenance/calibration state, quality status and provenance. BP-09 owns physical resource inventory and maintenance; BP-08/BP-06/BP-32 own unit/personnel/qualification records; BP-24 consumes their authoritative status.

A resource unavailable, unqualified, uncalibrated, expired, compromised or restricted cannot be represented as available for an examination requiring it. Subcontracted or external specialists are bounded service providers, not a simulated external jurisdiction. Their identity, credentials, scope, transfer and returned records are explicit. No capability is conjured merely because a request exists.

## 6. Examination requests and authority

A request references one or more BP-23 exhibit IDs and exact versions, case/incident, requesting person/unit, authority, purpose, question(s), requested discipline, urgency, known hazards, contamination risks, package/seal condition, relevant provenance and any restrictions. Record the requested scope separately from the examiner's accepted scope. A request can be returned for clarification, accepted wholly or partly, deferred, rejected or cancelled with attributed reason.

BP-16 creates and manages investigative requests; authorised scene/custody/legal actors may submit under their own authority. BP-24 does not manufacture a request, silently expand scope or collect an item merely because it appears relevant. Authority and permission failures remain visible. A request is not proof that the proposed hypothesis is correct.

## 7. Triage and prioritisation

Triage assesses urgency, risk of loss/degradation, safety, evidential question, legal/court dates supplied by authorised systems, resource capability, queue load, dependencies, sample quantity and competing requests. Store each factor, source, assessor, time and rationale. Priority is an operational scheduling decision, not a prediction of evidential value, guilt or likely result.

Priority classes and service targets are configurable and versioned. Emergency work may be escalated by authorised personnel with reason and audit. Conflicts remain visible; queue order is explainable and may be manually overridden by authorised roles. No request is silently dropped, and low priority does not mean unimportant.

## 8. Acceptance, scope and planning

Acceptance creates an examination job with defined items/versions, questions, disciplines, methods or candidate methods, assigned examiner(s), facility, resources, safety controls, contamination plan, sequence, expected outputs, dependencies, estimated work and review requirements. Scope changes are versioned and require authority and rationale. An accepted job may be split into sub-jobs while retaining parent links.

Acceptance confirms only that the work is accepted within stated scope and capability. It does not confirm that a usable result will be obtained. Rejection/deferment states the capability, authority, safety, sample, integrity or clarification reason and preserves the original request. Unavailable resources never cause fabricated completion.

## 9. Examination lifecycle

Job states include draft, submitted, triage, clarification, accepted, queued, scheduled, in progress, paused, awaiting resource, awaiting information, partially completed, completed, quality review, report issued, challenged, re-examination, cancelled, rejected and archived. Transitions require actor, authority, event time, reason and state validation. Partial results remain individually attributable and cannot be represented as a final whole-job result.

An examination may have multiple stages, examiners, methods, samples and reports. Work can stop for safety, contamination, equipment failure, insufficient material, contradictory findings, scope change or player decision. Resume continues from recorded state; no off-screen work is performed while the player is absent.

## 10. Method catalogue and versioning

Each method has a stable ID, title, discipline, version, purpose, applicability, accepted material, exclusions, equipment/reagents/software, required competency, procedure reference, validation/verification status, known limitations, contamination risks, output types, effective dates and retirement/supersession links. Method versions are immutable once used in an examination record. A current method does not rewrite a prior method record.

Method choice is examiner-controlled within authorised scope and capability. Deviations, adaptations, substitutions and non-standard methods are recorded with rationale, approval where required, impact and limitations. A method catalogue entry is not proof that it is scientifically valid for every material or question.

## 11. Personnel, competence and independence

Examiner records reference canonical BP-03 identity and BP-06/BP-32 employment and qualification records. Record role in the examination, discipline, competency level, training/authorisation status at work time, experience where relevant, supervision, conflicts declared and scope of responsibility. A title or rank alone does not establish competence.

Separate collector, examiner, reviewer and author roles where required by configured quality controls. One person may perform multiple roles only where permitted and disclosed. Conflicts, prior involvement, personal relationships or compromised independence trigger review, not automatic guilt or invalidity. External experts have source-verified identity and declared scope.

## 12. Equipment, calibration and facility conditions

Examinations record relevant equipment/instrument/software IDs, version, configuration, calibration or verification status, maintenance state, environmental conditions, consumables/reagents lot references and any known malfunction. BP-09 remains authoritative for asset inventory and maintenance. The examination records the actual equipment state used at the time, not merely today's status.

If calibration is absent, out of date, failed or uncertain, record the issue and assess its effect. Do not silently mark an instrument compliant. Facility conditions, contamination zones, access restrictions and environmental controls are recorded to the level relevant to the method. No unsupported precision is generated.

## 13. Observations, measurements and raw data

Observations describe what the examiner directly saw, heard, measured, operated or received. Record observer, date/time and time basis, instrument/method, units, conditions, source/version, uncertainty, repeatability and media/data reference as applicable. Separate direct observation from inferred explanation. Preserve original notes, instrument output, photographs, spectra, sequence data, logs and other raw records under controlled immutable references.

Measurements include units, scale, resolution, calibration basis and uncertainty where relevant. Qualitative results identify criteria and limitations. Negative, inconclusive, uninterpretable, not tested, not available and no result are distinct outcomes. Raw data is never silently replaced by a processed or summarised version.

## 14. Analysis, interpretation and uncertainty

Interpretation identifies the result, relevant propositions or question, assumptions, method, data considered, alternative explanations, limitations, uncertainty and strength language used. Any scale or verbal framework is explicit, versioned and discipline-specific; do not invent universal probabilities or numerical likelihoods. Explain what cannot be inferred. Distinguish source-level propositions from person-level propositions and activity-level propositions where applicable.

Conflicting results are preserved and reconciled only through attributed review. Uncertainty is not hidden by a single confidence label. An examiner may conclude that no reliable interpretation is possible. The system must support inconclusive, qualified, limited and conflicting conclusions without forcing a binary answer.

## 15. Contamination prevention and assessment

Each job has a contamination-risk plan appropriate to material and method: personnel controls, clean/dirty zones, equipment, packaging interfaces, sequencing, controls, blanks, elimination references where applicable, sample handling and environmental conditions. Record control results, deviations, possible cross-transfer, contamination incidents, affected samples, timing, actors, containment, review and effect on conclusions.

A contamination allegation is not a confirmed event. A control failure or contamination concern does not automatically invalidate every item; assess affected scope and uncertainty. Never erase, relabel or conceal a contamination event. BP-23 owns exhibit custody; BP-24 owns contamination risks and effects during examination and links the events to custody records.

## 16. Sampling, consumption and derivatives

A sample request identifies parent exhibit/version, proposed quantity, purpose, method, authority, expected consumption, remainder and risks. BP-23 records custody, packaging and physical inventory changes; BP-24 records scientific sampling/examination actions and outputs. Child samples, extracts, fractions, swabs, casts, images and digital derivatives have unique IDs, parent-child lineage, creator, time, method and source.

No sample is consumed, destroyed, subdivided or exhausted without recorded authority and quantity/status. Unknown quantity remains unknown. Derivative creation never overwrites the parent. Failed or contaminated samples remain in the history. A derivative's evidential status is not automatically equivalent to its parent.

## 17. Discipline-specific examination profiles

Each discipline may define a profile with accepted materials, intake checks, preparation, method options, observations, controls, expected outputs, interpretation framework, uncertainty, contamination risks, reporting fields and limitations. Profiles are configuration, not hard-coded assumptions. A profile cannot bypass the common provenance, permission, time-freeze, audit or player-agency rules.

Biological work preserves sample identity, quantity, mixture/partial/low-template limitations and contamination controls. Fingerprint/impression work records substrate, quality, development/capture method and comparison limitations. Trace/material work records sampling location, comparison set and non-uniqueness limitations. Firearms/toolmark work records item and test context, method and comparison limits. Digital work preserves source acquisition, write protection where applicable, hashes, tool versions, extraction scope, deleted/unavailable data and clock uncertainty. Audio/video/image work preserves native source, codecs, transformations, metadata, synchronisation and enhancement limits. Medical/pathology liaison records only the forensic interface and authorised material; it does not simulate healthcare operations.

## 18. Environmental and temporal effects

Where justified, environmental conditions may affect evidence persistence, degradation, contamination, visibility, transport, biological activity, chemical stability or interpretation. Use BP-19/BP-02/BP-35 authoritative environmental/geographic records as applicable, recording source, location, time basis and uncertainty. Do not invent weather, temperature, exposure or degradation. A modelled effect must state the rule and inputs used.

No degradation, biological process, storage timer, instrument run, queue, examination duration or environmental change progresses while the player is absent. On resume, the simulation does not apply catch-up changes. Any player-authorised time advance is explicit and uses BP-37.

## 19. Specialist consultation and referral

A job may request consultation, second opinion, external referral or specialist service. Record question, scope, provider, credentials, conflicts, authority, material/version transferred, restrictions, transfer acceptance, method/source records, returned advice/report, limitations and review. Consultation is distinct from independent examination and formal peer review.

External work is represented through bounded records and transfers; no off-map world is simulated. Missing, delayed or disputed external results remain pending. External opinion is attributed and not silently adopted as Saltwater's own conclusion.

## 20. Quality assurance, review and proficiency

Quality controls may include method validation/verification status, control samples, blanks, replicate work, technical review, administrative review, peer review, proficiency status, audit findings and corrective actions. Each review identifies reviewer, independence/competence, scope, material considered, criteria/version, outcome, limitations and dissent.

Review states include pending, passed, passed with qualification, failed, returned for correction, disputed and not required with rationale. Quality review cannot silently change raw observations or the examiner's original opinion. Reanalysis and correction create new versions with links to superseded outputs. A review is not a guarantee of correctness.

## 21. Reports and conclusions

A report identifies case/request/job, items and exact versions, question/scope, examiner(s), qualifications relevant to work, dates/time basis, method/version, equipment where relevant, source materials, observations, results, interpretation, uncertainty, limitations, deviations, contamination issues, quality review, references, attachments and status. It clearly separates factual description, raw result, interpretation and opinion.

Reports support preliminary, interim, partial, final, amended, supplemental and withdrawn states. A report is immutable once issued; amendments append a new version with reasons and change summary. Summaries never replace the full report or raw data. A report cannot assert legal admissibility, guilt, innocence or court findings.

## 22. Disclosure, testimony and court interface

BP-24 supplies authorised reports, underlying data references, method/version details, limitations, quality records, relevant notes and disclosure-ready copies to BP-27/BP-28. BP-27 owns disclosure/prosecution workflow; BP-28 owns court proceedings, admissibility, evidential weight and findings. BP-24 may record a challenge, request for clarification, expert conference, testimony event, cross-examination issue or court direction as an external interface event, but does not decide the legal outcome.

Record exactly which report/version/material was supplied, to whom, when, under what authority, with redactions/limitations and source lineage. Corrected reports do not erase earlier disclosure history. Exculpatory, adverse, inconclusive and contradictory material is retained and made available to authorised review.

## 23. Challenges, re-examination and disputes

A challenge identifies disputed report/version, issue, challenger, authority, grounds, supporting material and requested action. Responses may clarify, correct, supplement, review, repeat, independently examine, withdraw or maintain with explanation. Preserve all parties' positions and unresolved disagreement. Re-examination creates a linked job and does not overwrite prior findings.

A challenge does not automatically invalidate a report. A new result does not silently supersede an earlier result. Record whether the same material, retained sample, derivative or new source was examined and any changed method, examiner or conditions.

## 24. Permissions, confidentiality and protected material

BP-42 owns global access policy. BP-24 defines permission scopes for sensitive case material, medical/biological records, genetic data, protected-source material, confidential methods, raw data, examiner notes, quality records, draft reports, external submissions and court copies. Least privilege and purpose limitation apply independently of rank, case assignment or examiner status.

Search results, notifications, AI summaries, previews, exports, charts and visualisations enforce the same restrictions. Protected data is not copied into unrestricted narrative. Access, denied access, export, amendment and disclosure are audited. Health-related information is handled only to the extent necessary for the forensic interface and authorised purpose.

## 25. NPC knowledge and hidden information

Examiners and other NPCs know only the items, records, observations and results they personally examined, received or were authorised to access. A case link or database relationship does not create awareness. NPC interpretations may be mistaken, limited, contested or incomplete. They cannot know BP-14 hidden world truth or infer an offender identity from omniscient simulation data.

No report, result, metadata, placeholder, AI summary, test fixture, error message or court interface may leak hidden culprit/accomplice identity. The only reveal condition remains the player typing exactly bingo. Forensic outputs do not generate unsolicited investigative hints or tell the player what to investigate next.

## 26. Player agency and examination control

The player or authorised investigator controls requests, questions, priorities within authority, scope approvals, sample decisions and whether to accept or challenge outputs. No automatic forensic test is selected merely because an item exists. The simulation may present available capability and recorded status but must not recommend a suspect, reveal a solution or railroad the investigation. Player choices and NPC actions are recorded with provenance and consequences.

A request does not guarantee a result. A method may fail, be inconclusive, be unavailable or produce conflicting evidence. The game must not force success to advance a plot or force failure to preserve a mystery.

## 27. Time, queues and pause semantics

BP-37 is the sole simulation clock. Queue positions, scheduled jobs, estimates, deadlines, sample degradation, biological processes, equipment runs, external referrals, reviewer availability and NPC work do not advance while the player is outside the simulation. There is no off-screen processing or catch-up. When time advances in play, each consequential transition is attributable and uses the canonical clock.

Estimated turnaround is an estimate, not a timer that secretly completes work. Actual completion requires an explicit simulation event and available capability. Pause/resume preserves exact queue and job state.

## 28. Storage, records and persistence

BP-38 owns schemas, identifiers, constraints, transactions and indexes; BP-39 owns persistence, backup and recovery. Store raw data and reports as immutable source objects or controlled references with metadata, checksums, versions, retention and recoverability. Structured examination facts are normalised and linked to BP-23 exhibits, BP-03 people, BP-09 assets and BP-37 time. Avoid duplicate payloads while preserving full provenance and meaning.

Every result, method, report and review has a stable ID. Original raw data and issued reports are retained separately from derived summaries and interface views. Compression cannot remove source wording, measurement units, uncertainty, limitations, version history or audit. A missing object is flagged, never replaced with an invented reconstruction. No database write is authorised by this specification.

## 29. Interface and visualisation

Text-first workflows must support create/list/inspect requests, review triage, accept/reject/defer, define scope, assign capability, record methods and observations, inspect raw results, interpret, review quality, issue/amend reports, record challenges, refer externally, link disclosure/court versions and audit. A text-only player can complete every essential forensic interaction.

Optional visuals include annotated images, comparison boards, microscopy-style views, spectra, timelines, diagrams, measurement overlays, scene reconstructions and result charts. They must be generated from canonical source data, identify transformations and uncertainty, preserve originals, show scale/time/source where relevant and never silently contradict text. Visuals are aids, not independent evidence or required gameplay.

## 30. Inputs, outputs and event contracts

Inputs: BP-03 identities; BP-06 personnel; BP-08 unit/capability assignments; BP-09 equipment/facilities; BP-12 incident; BP-15 case; BP-16 authorised requests; BP-17 participant context; BP-19 interview material; BP-20 surveillance source/export; BP-21 intelligence source references; BP-22 scene observations/recovery; BP-23 exhibits/samples/custody; BP-27 legal/disclosure requests; BP-28 court directions; BP-32 qualifications; BP-35 causal events; BP-37 time; BP-38 records; BP-39 persistence; BP-42 permissions.

Outputs: triage decisions; examination jobs/plans; capability allocation; method records; observations/measurements/raw-data references; sample/derivative lineage; analytical results; interpretations/opinions; limitations/uncertainty; contamination and quality events; reports and versions; review outcomes; referral/consultation records; disclosure/testimony references; audit events.

Events include request_submitted/clarification_requested/accepted/rejected/deferred/cancelled; job_created/scheduled/started/paused/resumed/completed; scope_changed; examiner_assigned/reassigned; method_selected/deviated; equipment_state_recorded; observation_recorded; raw_data_ingested; sample_created/consumed; derivative_created; contamination_suspected/confirmed/reviewed; result_recorded/interpreted; quality_review_started/passed/failed; report_issued/amended/withdrawn; challenge_received/resolved; referral_sent/accepted/returned; disclosure_copy_created; testimony_recorded. Each event carries stable ID, target/job/version, actor, authority, purpose, canonical time, source, outcome, idempotency key and schema version.

## 31. Failure modes and edge cases

No suitable discipline; no qualified examiner; resource unavailable; calibration failure; method withdrawn; request lacks authority; unclear question; conflicting priorities; urgent competing jobs; insufficient/degraded sample; unknown provenance; seal discrepancy; contamination concern; control failure; mixed/partial sample; exhausted sample; duplicate request; conflicting results; failed replicate; instrument outage; software/version mismatch; raw data corruption; clock drift; external provider delay; report challenged; examiner conflict; reviewer disagreement; missing source data; protected information restriction; court deadline changed; job paused mid-process; player leaves mid-process; attempted automatic test; NPC knowledge leak; report amendment after disclosure; missing backup object; visual mismatch; unsupported method; environmental uncertainty; no conclusion possible. Preserve state, uncertainty, original records and reason; block invalid transitions; do not invent results or silently repair history.

## 32. Dependencies and ownership boundaries

BP-22 owns scene control, search and original observations; BP-23 owns exhibit identity, packaging, custody and sample inventory; BP-24 owns examination work/results. BP-16 owns investigative plans and inferences; BP-21 owns intelligence; BP-19 interviews; BP-20 surveillance; BP-27 legal disclosure/prosecution; BP-28 courts. BP-09 owns physical equipment/facility inventory; BP-06/BP-32 own personnel and qualifications; BP-37 time; BP-38/BP-39 data and persistence; BP-42 security. BP-24 references, requests and returns data across these boundaries but never silently mutates another division's authoritative records.

## 26. Acceptance tests

These are specification acceptance criteria, not executed results. BP-43 owns test execution and reproducible evidence.

- **FORENSIC-AT-001** — Every forensic request has a stable unique ID.
- **FORENSIC-AT-002** — Every examination job has a stable unique ID.
- **FORENSIC-AT-003** — A request references exact exhibit IDs and versions.
- **FORENSIC-AT-004** — A request records requesting actor, authority and purpose.
- **FORENSIC-AT-005** — A request preserves the question as submitted.
- **FORENSIC-AT-006** — An examination scope is distinct from the requested scope.
- **FORENSIC-AT-007** — An unauthorised request cannot be accepted as authorised work.
- **FORENSIC-AT-008** — A request can be returned for clarification without losing its original content.
- **FORENSIC-AT-009** — A request can be accepted partially with explicit scope.
- **FORENSIC-AT-010** — A request can be deferred with an attributed reason.
- **FORENSIC-AT-011** — A request can be rejected without deleting it.
- **FORENSIC-AT-012** — A request can be cancelled with actor, authority and reason.
- **FORENSIC-AT-013** — A request does not prove the hypothesis behind its question.
- **FORENSIC-AT-014** — Discipline catalogue entries have stable IDs and versions.
- **FORENSIC-AT-015** — Discipline catalogue supports extension without schema redesign.
- **FORENSIC-AT-016** — Catalogue capability is distinct from actual current availability.
- **FORENSIC-AT-017** — Discipline scope, exclusions and accepted materials are explicit.
- **FORENSIC-AT-018** — A catalogue entry cannot imply an unavailable laboratory exists.
- **FORENSIC-AT-019** — Every capability has effective dates and current status.
- **FORENSIC-AT-020** — Capability requires appropriate equipment and competent personnel.
- **FORENSIC-AT-021** — Unavailable equipment blocks work requiring it.
- **FORENSIC-AT-022** — Unqualified personnel cannot be silently assigned as competent examiners.
- **FORENSIC-AT-023** — Triage records the factors and sources considered.
- **FORENSIC-AT-024** — Triage priority is not treated as evidential strength or guilt.
- **FORENSIC-AT-025** — Priority overrides record actor, authority and rationale.
- **FORENSIC-AT-026** — Competing urgent requests remain visible.
- **FORENSIC-AT-027** — No request is silently dropped from the queue.
- **FORENSIC-AT-028** — Queue estimates are distinguished from guaranteed completion.
- **FORENSIC-AT-029** — Acceptance creates an explicit job and defined scope.
- **FORENSIC-AT-030** — Acceptance does not guarantee a usable result.
- **FORENSIC-AT-031** — A job can contain multiple stages and sub-jobs.
- **FORENSIC-AT-032** — Sub-jobs retain parent-job references.
- **FORENSIC-AT-033** — Job state transitions are validated and attributed.
- **FORENSIC-AT-034** — Partial results remain distinct from final job completion.
- **FORENSIC-AT-035** — Paused jobs preserve exact state.
- **FORENSIC-AT-036** — Method IDs are stable and method versions immutable.
- **FORENSIC-AT-037** — A completed examination identifies the method version used.
- **FORENSIC-AT-038** — Method scope and exclusions are recorded.
- **FORENSIC-AT-039** — Method validation/verification status is visible.
- **FORENSIC-AT-040** — A method deviation records rationale and effect.
- **FORENSIC-AT-041** — A current method version does not rewrite historical work.
- **FORENSIC-AT-042** — Method selection does not exceed authorised scope.
- **FORENSIC-AT-043** — Examiner identity resolves to a canonical person record.
- **FORENSIC-AT-044** — Examiner competence is evaluated for the work date.
- **FORENSIC-AT-045** — Rank alone does not establish forensic competence.
- **FORENSIC-AT-046** — Examiner, reviewer and author roles are recorded separately.
- **FORENSIC-AT-047** — Conflicts of interest are declared and reviewable.
- **FORENSIC-AT-048** — External specialists have attributed identity and scope.
- **FORENSIC-AT-049** — Equipment IDs and versions used are recorded.
- **FORENSIC-AT-050** — Relevant calibration status at examination time is recorded.
- **FORENSIC-AT-051** — Calibration failure is not silently represented as valid.
- **FORENSIC-AT-052** — Software/tool version and configuration are recorded where relevant.
- **FORENSIC-AT-053** — Facility conditions are recorded where material to method.
- **FORENSIC-AT-054** — Direct observation is separated from inference.
- **FORENSIC-AT-055** — Every observation identifies observer and time basis.
- **FORENSIC-AT-056** — Measurements preserve units and scale.
- **FORENSIC-AT-057** — Measurements identify relevant resolution and uncertainty.
- **FORENSIC-AT-058** — Raw instrument output is retained or referenced immutably.
- **FORENSIC-AT-059** — Processed data is linked to raw source data.
- **FORENSIC-AT-060** — Negative, inconclusive, uninterpretable and not tested are distinct.
- **FORENSIC-AT-061** — No result is not converted into a negative finding.
- **FORENSIC-AT-062** — Raw results are not overwritten by interpretation.
- **FORENSIC-AT-063** — Interpretation identifies assumptions and propositions considered.
- **FORENSIC-AT-064** — Interpretation states alternative explanations where material.
- **FORENSIC-AT-065** — Limitations and uncertainty accompany conclusions.
- **FORENSIC-AT-066** — No unsupported universal probability is generated.
- **FORENSIC-AT-067** — Source-level and person-level propositions remain distinct.
- **FORENSIC-AT-068** — Absence of a result is not proof of absence.
- **FORENSIC-AT-069** — Conflicting results remain visible pending review.
- **FORENSIC-AT-070** — An examiner can conclude no reliable interpretation is possible.
- **FORENSIC-AT-071** — Contamination risk is assessed for each relevant job.
- **FORENSIC-AT-072** — Contamination controls and results are recorded.
- **FORENSIC-AT-073** — Contamination concerns identify affected items and samples.
- **FORENSIC-AT-074** — An allegation of contamination is not treated as confirmed.
- **FORENSIC-AT-075** — Control failure triggers documented impact review.
- **FORENSIC-AT-076** — Contamination does not automatically invalidate unrelated items.
- **FORENSIC-AT-077** — BP-23 remains authoritative for exhibit custody and package events.
- **FORENSIC-AT-078** — BP-24 records examination-time handling and links custody events.
- **FORENSIC-AT-079** — Sampling identifies parent exhibit and version.
- **FORENSIC-AT-080** — Samples and derivatives receive unique identities.
- **FORENSIC-AT-081** — Sample lineage links parent, child and source version.
- **FORENSIC-AT-082** — Consumption records authority and quantity where known.
- **FORENSIC-AT-083** — Unknown sample quantity remains unknown.
- **FORENSIC-AT-084** — Exhausted samples remain represented in history.
- **FORENSIC-AT-085** — A derivative never overwrites its parent source.
- **FORENSIC-AT-086** — Digital examination preserves acquisition source and provenance.
- **FORENSIC-AT-087** — Digital hashes identify algorithm and exact data object.
- **FORENSIC-AT-088** — Hash match is not described as proof of authenticity.
- **FORENSIC-AT-089** — Digital examination records extraction scope and limitations.
- **FORENSIC-AT-090** — Audio/video/image transformations retain native-source links.
- **FORENSIC-AT-091** — Image enhancement is labelled as a derivative.
- **FORENSIC-AT-092** — Environmental effects use sourced conditions and time basis.
- **FORENSIC-AT-093** — No unsupported degradation or environmental fact is invented.
- **FORENSIC-AT-094** — No simulated degradation progresses while player is absent.
- **FORENSIC-AT-095** — External referral records provider, scope and transfer references.
- **FORENSIC-AT-096** — External opinion is attributed and not silently adopted.
- **FORENSIC-AT-097** — External work does not simulate an off-map jurisdiction.
- **FORENSIC-AT-098** — Quality review identifies reviewer and review scope.
- **FORENSIC-AT-099** — Quality review criteria and method versions are recorded.
- **FORENSIC-AT-100** — Review outcome supports qualified, failed and disputed states.
- **FORENSIC-AT-101** — Review cannot silently change raw observations.
- **FORENSIC-AT-102** — Corrective work creates new linked versions.
- **FORENSIC-AT-103** — A report identifies exact exhibits and versions examined.
- **FORENSIC-AT-104** — A report identifies examiner and relevant competence.
- **FORENSIC-AT-105** — A report identifies method/version and source materials.
- **FORENSIC-AT-106** — A report separates observations, results and interpretation.
- **FORENSIC-AT-107** — A report states limitations, uncertainty and deviations.
- **FORENSIC-AT-108** — A report records contamination issues and quality review.
- **FORENSIC-AT-109** — An issued report is immutable; amendments create versions.
- **FORENSIC-AT-110** — A summary never replaces full report or raw data.
- **FORENSIC-AT-111** — Reports support preliminary, interim, partial and final states.
- **FORENSIC-AT-112** — Withdrawal preserves prior report and reason.
- **FORENSIC-AT-113** — BP-24 does not decide admissibility or evidential weight.
- **FORENSIC-AT-114** — Disclosure copy records exact report/data versions supplied.
- **FORENSIC-AT-115** — Earlier disclosure history remains after report amendment.
- **FORENSIC-AT-116** — Exculpatory, adverse and inconclusive material is retained.
- **FORENSIC-AT-117** — A challenge does not automatically invalidate a report.
- **FORENSIC-AT-118** — Re-examination links to prior job and report versions.
- **FORENSIC-AT-119** — Re-examination does not overwrite prior findings.
- **FORENSIC-AT-120** — Protected forensic data is permission-filtered in previews and exports.
- **FORENSIC-AT-121** — Denied access and sensitive exports are audited.
- **FORENSIC-AT-122** — Rank or case assignment alone does not grant all forensic access.
- **FORENSIC-AT-123** — Medical/biological information is limited to authorised forensic purpose.
- **FORENSIC-AT-124** — NPC examiner knowledge follows actual receipt, access and examination.
- **FORENSIC-AT-125** — A database relationship alone does not create NPC knowledge.
- **FORENSIC-AT-126** — Hidden offender identity cannot leak through forensic output or metadata.
- **FORENSIC-AT-127** — Only exact player input bingo permits hidden-truth reveal.
- **FORENSIC-AT-128** — Forensic outputs do not provide unsolicited investigation hints.
- **FORENSIC-AT-129** — AI cannot invent methods, observations, results or examiner actions.
- **FORENSIC-AT-130** — BP-37 is the sole simulation clock.
- **FORENSIC-AT-131** — No job, queue, equipment run or referral advances while player is absent.
- **FORENSIC-AT-132** — No retention/degradation timer advances while player is absent.
- **FORENSIC-AT-133** — Resume does not apply off-screen catch-up.
- **FORENSIC-AT-134** — Every result and report has stable versioned identity.
- **FORENSIC-AT-135** — Raw records and derived summaries remain separate.
- **FORENSIC-AT-136** — Compression preserves units, limitations, provenance and history.
- **FORENSIC-AT-137** — Missing stored objects are flagged, not reconstructed as facts.
- **FORENSIC-AT-138** — No schema, seed, import or bulk database write is authorised here.
- **FORENSIC-AT-139** — Text-only workflows can complete every essential forensic operation.
- **FORENSIC-AT-140** — Optional visualisations derive from canonical source data.
- **FORENSIC-AT-141** — Every visualisation identifies transformations and uncertainty.
- **FORENSIC-AT-142** — A visual never silently contradicts authoritative text.
- **FORENSIC-AT-143** — Every conclusion identifies method, source material, limitations and examiner.

## 27. Source traceability

The 52-division source JSON remains unchanged. IDs refer to original source-array positions (1-based). The BP-24 crosswalk mapping is retained; this specification expands its mapped intent without changing the 44-division structure.

| Source ID | Original source requirement/test | BP-24 coverage |
|---|---|---|
| S13.R02 | Model injuries, deaths, medical evidence and care access consistently without a separate deep healthcare simulation. | Sections 4, 15, 18, 20; forensic medical/pathology interface only, no healthcare simulator. |
| S19.R02 | Apply environmental conditions to visibility, travel, infrastructure, health and evidence persistence where justified. | Section 17; sourced environmental effects on evidence/examination only, with BP-35/BP-37 ownership respected. |
| S32.R02 | Preserve original observations separately from interpretation. | Sections 3, 12, 13, 21; immutable raw observations/results and separate interpretation. |
| S32.R03 | Support physical, digital, documentary, biological, trace and testimonial evidence. | Sections 4, 15; extensible discipline/material catalogue and source ownership. |
| S33.R01 | Represent forensic disciplines, submissions, prioritisation, methods, results, limitations, contamination risks, quality and expert interpretation. | Sections 4–19; full forensic lifecycle and specialist capability. |
| S33.R02 | Distinguish raw result, analyst interpretation and investigative inference. | Sections 3, 12, 13, 21; separate epistemic layers and ownership. |
| S33.R03 | Support specialist resources and realistic turnaround times. | Sections 5–9, 17–18, 24; capability, triage, estimates and pause-aware queues. |
| S45.R01 | Provide optional maps, layouts, timelines, charts and forensic scene visuals when useful or requested. | Section 23; optional traceable forensic visualisations. |
| S45.R02 | Visuals derive from canonical spatial/evidence data and never silently contradict text records. | Sections 12, 23; source links, versions, transformation and uncertainty. |
| S32.T01 | Every exhibit has unique ID, recovery details, continuity and current location/status. | BP-23 owns exhibit ID/recovery/custody; BP-24 requires exact exhibit/version references in FORENSIC-AT-003 and section 6. |
| S33.T01 | Every conclusion identifies method, source material, limitations and examiner. | FORENSIC-AT-143; sections 13, 16, 21. |
| S45.T01 | Every visual can be traced to underlying canonical records. | FORENSIC-AT-140–142; section 23. |

Cross-cutting X05, X06 and X08 apply: preserve distinctions among fact/allegation/estimate/inference/intelligence/opinion/conclusion/finding; preserve originals and additive corrections; text-first gameplay with optional visuals that cannot contradict authoritative records. Other global rules apply through BP-01 and relevant owner divisions, including one-city canon, 10,000-person hard cap, time freeze, player agency and exact bingo reveal firewall.

## 28. Open decisions and risk register

### Open decisions
1. Discipline catalogue initial breadth and versioning governance.
2. Capability and competency levels by discipline.
3. Requesting-authority matrix and emergency triage override.
4. Priority classes, queue rules and service-time estimates.
5. Method catalogue governance, validation status vocabulary and retirement policy.
6. Examiner independence and mandatory reviewer separation.
7. Equipment calibration and facility-condition recording thresholds.
8. Measurement uncertainty and discipline-specific interpretation vocabularies.
9. Contamination control profiles and escalation matrix.
10. Sample/derivative ID conventions and quantity precision.
11. External specialist credential and referral standards.
12. Quality review and proficiency status model.
13. Report templates, amendment and withdrawal rules.
14. Disclosure copy and expert testimony interfaces.
15. Retention periods and raw-data object-storage boundary with BP-38/BP-39.
16. Which specialist capabilities are resident, mobile or external.

### Risk register

| Risk | Mitigation |
|---|---|
| Result confused with guilt or fact | Explicit epistemic layers and ownership |
| Raw observations overwritten by interpretation | Immutable raw sources and additive versions |
| Unsupported scientific certainty | Discipline-specific uncertainty and limitations |
| Contamination concealed | Attributed event history and impact review |
| Unqualified examiner or invalid equipment | Time-specific capability/competence checks |
| Forensic queues secretly progress offline | BP-37 pause/freeze invariant |
| Sample consumption loses provenance | Parent-child lineage and quantity events |
| Derivative replaces original | Immutable source and version lineage |
| Medical information overexposed | Purpose-bound BP-42 permissions |
| NPCs learn hidden generator truth | Knowledge-boundary and exact bingo tests |
| Visuals contradict records | Canonical data lineage and text authority |
| External result silently adopted | Attribution, scope and review |

## 29. Design completion checklist

- [ ] Discipline catalogue and capability model specified.
- [ ] Request, authority, triage and acceptance lifecycle specified.
- [ ] Examination jobs, scope, stages and transitions specified.
- [ ] Method versioning and deviations specified.
- [ ] Personnel competence, independence and equipment state specified.
- [ ] Observations, measurements, raw data and interpretation separated.
- [ ] Uncertainty, limitations and alternative explanations specified.
- [ ] Contamination prevention, incidents and impact review specified.
- [ ] Sampling, consumption, derivatives and lineage specified.
- [ ] Digital, audio/video/image and specialist profiles specified.
- [ ] Environmental effects and pause-aware turnaround specified.
- [ ] Quality review, reports, challenges and re-examination specified.
- [ ] Disclosure/court boundaries and protected information specified.
- [ ] NPC knowledge and exact reveal firewall specified.
- [ ] Text-first workflow and optional traceable visuals specified.
- [ ] All 143 acceptance tests await BP-43 execution.
- [ ] Open decisions remain explicit; no policy invented.
- [ ] No Neon schema, seed, import or bulk write has been made or authorised.

## 30. Status and next dependencies

This is a complete division design draft, not approved policy or implementation evidence.

- Specification: **DESIGNED_DRAFT**
- User approval: **PENDING**
- Implementation: **NOT_STARTED**
- Test execution: **NOT_STARTED**
- Verification: **NOT_STARTED**
- Neon/database writes: **NONE; NOT AUTHORISED**

Next fixed division: **BP-25 — Arrests and Warrants**. BP-25 owns arrest grounds, warrants, applications, execution, search and seizure authority. BP-24 remains the owner of forensic examination methods, results, limitations, quality review and expert conclusions.
