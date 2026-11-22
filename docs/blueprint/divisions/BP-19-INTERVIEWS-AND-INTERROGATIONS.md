# BP-19 — Interviews and Interrogations

**Project:** Saltwater  
**Division:** BP-19 of the fixed 44-division structure  
**Specification:** DESIGNED_DRAFT  
**Implementation:** NOT_STARTED  
**Test execution:** NOT_STARTED  
**Verification:** NOT_STARTED  
**Authority:** Original 52-division source remains unchanged. This specification incorporates the BP-19 destination mappings and binding Saltwater canon; it does not change the 44-division structure.

## 1. Purpose

Define a complete, persistent, source-faithful system for planning, authorising, conducting, recording, reviewing and linking interviews, interrogations and other structured questioning. Preserve the actual sequence and content of interactions, participant roles, procedural status, cautions where configured, questions, answers, pauses, breaks, interruptions, recording media, notes, statements, corrections, disclosure references and provenance.

Support naturalistic and varied interactions while protecting player agency, participant knowledge boundaries, uncertainty, source integrity and hidden case truth. Text-first interaction is complete and permanent; no visual or audio interface is required to conduct, review or preserve an interview.

## 2. Scope and ownership

### 2.1 BP-19 owns

- Interview/interrogation episode identity, planning record and lifecycle.
- Interview purpose, scope, proposed topics and authorised participants.
- Interviewer, recorder, interpreter, legal representative, appropriate adult/support person and observer roles where configured.
- Interview setting, format, start/end, breaks, interruptions and attendance chronology.
- Procedural status and caution/rights notice record where fictional canon requires.
- Question, answer, non-answer, clarification, volunteered statement and interaction turn sequence.
- Audio/video/text recording references, recording segments, recording interruptions and technical faults.
- Contemporaneous notes, interview summaries, transcripts and formal statement versions.
- Participant review, adoption, disagreement, correction and signature/acknowledgement records where configured.
- Interview-specific disclosure, access restrictions and source integrity metadata.
- Interview event history, linked source references and auditable amendments.
- NPC interview behaviour within bounded knowledge and plausible characterisation.
- Interview completion, suspension, resumption, termination, cancellation and follow-up episode references.

### 2.2 Explicit exclusions and owners

| Concern | Owner | BP-19 relationship |
|---|---|---|
| Canonical person identity, aliases, life status and population cap | BP-03 | References person IDs; never creates duplicate identities |
| Police institutional authority, officer identity and qualifications | BP-05/BP-06/BP-32 | Validates interviewer identity, authority and qualification |
| Operational call/incident/dispatch records | BP-11/BP-12 | May initiate a request; BP-19 owns interview episode |
| Offence taxonomy | BP-13 | References offence version and elements; does not define law |
| Hidden occurrence truth and generation | BP-14 | Never supplied to ordinary interview generation |
| Case identity, lifecycle and assignment | BP-15 | References case; cannot open/close/merge/split case |
| Investigative plans, tasks, leads and decisions | BP-16 | May request an interview; BP-16 owns investigative purpose/decision |
| Victim/witness role, support, safeguarding and participant role | BP-17 | BP-17 owns role and support plan; BP-19 records participation episode |
| Suspect/POI/offender case role | BP-18 | BP-18 owns role/status; interview does not create guilt or suspect status |
| Surveillance | BP-20 | References lawfully sourced material only |
| Intelligence | BP-21 | References intelligence with restrictions; not evidence by default |
| Crime scenes | BP-22 | No scene authority |
| Exhibits, custody and continuity | BP-23 | Owns exhibit and evidential continuity; interview references exact exhibit/version |
| Forensics | BP-24 | Owns methods, raw results and interpretation |
| Arrests and warrants | BP-25 | Owns arrest/search authority and events |
| Custody | BP-26 | Owns detention, welfare, clock and custody decisions |
| Legal process, prosecution and disclosure | BP-27 | Owns legal disclosure and prosecution status; BP-19 provides source records |
| Court proceedings and outcomes | BP-28 | Owns testimony/hearing records and judicial findings |
| Corrections | BP-29 | No sentence execution authority |
| Governance and professional standards | BP-30/BP-31 | Own interview policy, oversight and misconduct process |
| Simulation causality and NPC behaviour | BP-35 | Runs interactions only under valid in-world time and knowledge constraints |
| Relationships/social context | BP-36 | Supplies relationship context, never proof of guilt |
| Time and scheduling | BP-37 | Canonical clock and pause |
| Records and persistence | BP-38/BP-39 | Schema, transactions, immutable history and recovery |
| Interface/reporting | BP-40/BP-41 | Presents permitted content; no separate source of truth |
| Security and permissions | BP-42 | Access, confidentiality, audit and hidden-truth firewall |
| Testing/change control | BP-43/BP-44 | Evidence and approved amendments |

### 2.3 Non-goals

BP-19 is not a general free-form chat transcript store, lie detector, guilt classifier, confession generator, automated interrogation strategist, legal-advice engine or evidence adjudicator. It must not coach the player toward a solution, decide which person should be interviewed next, or make every interview productive.

## 3. Governing invariants

1. An interview is an event/record, not proof of the truth of every statement made during it.
2. Questions, answers, non-answers, volunteered statements, interviewer observations and later interpretations are distinct record types.
3. A summary is never represented as a verbatim transcript or original recording.
4. A transcript is not the recording; a recording reference is not proof that the recording is complete or intelligible.
5. Participant identity and role are explicit and sourced; presence does not imply participation.
6. Interview participation does not automatically create a suspect, victim, witness or offender role. BP-17/BP-18 own those roles.
7. Interviewing a person does not establish suspicion, guilt, credibility, dishonesty or cooperation.
8. A suspect interview does not establish guilt; an admission is an attributed statement and not a conviction.
9. A denial, silence, refusal, confusion, distress, inconsistency, anger, confidence or cooperation is not an automatic indicator of guilt or innocence.
10. Interview records preserve both inculpatory and exculpatory content, including uncertainty and contradictions.
11. Every substantive question/answer turn preserves order, speaker, source, time and version.
12. Leading, ambiguous, compound, repeated, misunderstood and withdrawn questions remain identifiable as asked; do not silently improve originals.
13. Corrections append a new version; originals remain preserved.
14. Participant review or signature does not make every statement objectively true.
15. An interpreter's words, interpretation uncertainties and source language are distinguished where available.
16. A recording gap, inaudible segment, equipment fault or missing source is explicitly marked; no content is fabricated to fill it.
17. NPC knowledge is limited to plausible observation, memory, communications and authorised disclosure.
18. BP-14 hidden occurrence truth is never used as ordinary interviewer/NPC knowledge or player-facing prompt content.
19. The culprit/perpetrator/accomplice identity remains hidden until the player types exactly lowercase bingo, alone, without punctuation or whitespace.
20. No unsolicited solution hints, recommended next questions, suggested suspect, culprit ranking or next-investigation instruction.
21. Player chooses whom to interview, when, why, and what to ask; the system presents available records without railroading.
22. No simulation time or interview progress advances while the player is outside the simulation.
23. Interviewers must possess configured authority/qualification and valid access; role/rank alone does not grant all permissions.
24. An interview may be cancelled, unproductive, incomplete, interrupted, disputed or unavailable without penalty or forced success.
25. Interview episodes, statements, media references and source histories persist after case closure, participant death, acquittal or elimination.
26. All materially relevant persons are permanently promoted through BP-03; all living persons count once within the 10,000 cap.
27. Every material record change is attributable, time-stamped, versioned and auditable.
28. Storage efficiency may compress representation but must never remove meaning, original wording, uncertainty, chronology, speaker attribution or provenance.

## 4. Core entities and identifiers

Identifiers are stable, opaque and non-semantic. Exact prefix formats are a BP-38 open decision.

| Entity | Required ID | Purpose |
|---|---|---|
| Interview episode | interview_id | One planned/conducted questioning episode |
| Interview plan | interview_plan_id | Purpose, scope, participants and authority |
| Participant link | interview_participant_id | Person's role in this episode |
| Interviewer assignment | interviewer_assignment_id | Interviewer and authority/qualification reference |
| Procedural notice | procedural_notice_id | Caution/rights/procedural notice event |
| Interview segment | segment_id | Continuous or interrupted session segment |
| Turn | interview_turn_id | Ordered speaker/question/answer event |
| Question | question_id | Exact question text and metadata |
| Answer | answer_id | Exact answer/non-answer/response |
| Recording asset | recording_id | Original media source reference |
| Recording segment | recording_segment_id | Time-bounded media portion |
| Note | interview_note_id | Contemporaneous note or observation |
| Transcript | transcript_id | Versioned transcript with source mapping |
| Statement | statement_id | Formal or adopted statement record |
| Statement version | statement_version_id | Immutable version of statement |
| Interpretation | interpretation_id | Interpreter/translation event |
| Review | interview_review_id | Quality, accuracy, participant review |
| Correction | interview_correction_id | Append-only amendment/dispute |
| Disclosure link | interview_disclosure_id | BP-27 disclosure reference |
| Source link | interview_source_link_id | Exact source/version association |

### 4.1 Required common fields

As applicable: ID; schema version; case and person references; role reference; episode/segment; actor; authority; interviewer qualification; source and version; canonical event time; record time; effective time; speaker; sequence number; content type; original text/media reference; language; interpretation status; confidentiality; access classification; integrity/hash reference; correction/supersession links; correlation/idempotency key.

Do not duplicate full person biographies, police personnel files, case summaries or evidence binaries in interview records. Store canonical IDs and versioned references; retain interview-owned content in its original form.

## 5. Interview types and purpose

Configured types may include victim interview, witness interview, suspect interview, person-of-interest clarification, informal voluntary account, formal recorded interview, follow-up interview, group/incident debrief where authorised, interpreter-assisted interview, specialist/technical interview, child or vulnerable participant interview under configured fictional safeguards, staff/police account or internal inquiry interview, and statement-taking appointment.

Type is a workflow descriptor, not a determination of legal status. An episode may have multiple purposes but must state its primary and secondary purposes. A change of purpose is recorded, not silently substituted. A group debrief must preserve each speaker's separate contribution and must not create one collective statement.

## 6. Planning, requests and authorisation

BP-16 or another authorised source may request an interview. A request records requester, case, participant reference, purpose, scope, known constraints, priority if configured, proposed interviewer, requested format and supporting source references. A request is not an instruction to the player or an automatic scheduling action.

Before commencement, record interview purpose and scope; participant identity/identity uncertainty; participant procedural role as supplied by BP-17/BP-18 or other owner; interviewer and recorder identities; authority and qualification checks; location/format and accessibility requirements; interpreter/support/representative requirements where configured; applicable notices/cautions and their version; recording plan and equipment availability; restrictions, conflicts, confidentiality and source access; whether participation is voluntary, required or otherwise classified by fictional policy; and any refusal, postponement or unavailability.

Exact legal thresholds, notice wording, age categories, consent rules and compulsory powers are open fictional policy decisions. The system must not invent real-world legal obligations. If authority cannot be confirmed, block the restricted workflow and preserve the attempted request and reason; do not fabricate authorisation.

## 7. Participant model

Each participant is linked to BP-03 person identity and has an episode-specific role: interviewee, interviewer/lead interviewer, second interviewer, recorder, interpreter, legal representative/adviser, appropriate adult/support person, observer/supervisor, specialist adviser or other configured role.

Presence, attendance, participation and speaking are separate. A participant may arrive late, leave, return, decline to answer, request a break or be removed. Record arrival/departure and role changes as events. Do not assume every attendee heard every segment.

For each participant record identity confidence, role source, attendance intervals, access/visibility, language, communication/accessibility requirements where supplied, relevant notices, permissions, and whether they contributed. Sensitive personal/health details remain in their owning systems and are not copied without an authorised need.

## 8. Procedural notices, cautions and rights

BP-19 records the exact configured notice/caution text/version, who delivered it, to whom, when, language, interpretation, acknowledgement/response, any question or clarification, and any failure or repetition. Distinguish notice prepared, delivered, received as recorded, understanding acknowledged or disputed, waiver/declination if fictional policy permits, re-delivery/correction, no notice required under configured rule, and unable to confirm.

A checkbox alone is insufficient where the underlying words and event matter. Never mark a notice delivered merely because a template was generated. Do not invent legal requirements or apply external jurisdiction rules to Saltwater. Open policy decisions remain unresolved until BP-30/BP-44 approval.

## 9. Interview lifecycle

Suggested lifecycle states: requested; awaiting_authorisation; authorised; scheduled; ready; in_progress; paused; interrupted; resumed; completed; suspended; terminated; cancelled; declined; no_show; unavailable; under_review; disputed; corrected; disclosed; archived.

Lifecycle is not legal status or case status. State transitions require an event with actor, authority, reason, canonical time and source. A completed interview can later be reviewed or corrected without changing its original completion event. An interrupted interview may resume in a new segment under the same episode if continuity is valid; otherwise create a linked follow-up episode. Cancellation or refusal does not imply guilt, non-cooperation or credibility.

## 10. Session segments and chronology

One interview episode may contain multiple segments. Each segment records segment ID and sequence; start/end canonical time; location/format reference; participants present during interval; recording state and media references; breaks, pauses, interruptions and reason if known; technical faults and recording gaps; language/interpreter status; resumption conditions and any procedural re-notice; source clock offsets and uncertainty where relevant.

The timeline must preserve overlapping participant attendance, multiple recording devices, clock drift and asynchronous transcript preparation. Never infer exact times from approximate sources without marking uncertainty. A break is not silently removed from the chronology.

## 11. Question and answer record

Each turn is an immutable ordered event with interview/segment ID and sequence; speaker person/role; turn type (question, answer, volunteered statement, clarification, interruption, objection, procedural notice, non-answer, pause marker, interpretation or configured type); original wording/content; language and translation reference; canonical time or bounded time interval; recording/transcript/note source references; attribution and confidence of transcription; redaction/access classification; correction/supersession links.

Answer categories include substantive answer, partial answer, denial, admission, qualified admission, uncertainty, cannot recall, does not understand, asks for clarification, refusal, silence/no answer, objection, interruption, volunteered material and inaudible/unavailable. These categories describe recorded response form, not truthfulness or guilt.

The original question remains unchanged even if a later transcript corrects a transcription error. Preserve repeated questions, leading phrasing, compound questions, contradictions, interruptions and interviewer comments. A summary or AI-generated condensation must be labelled as such and trace to underlying turns.

## 12. Recordings, notes and transcript

### 12.1 Recording

Recording records metadata and references the actual asset in the approved storage layer. Preserve source identity, format, duration, device/source, start/end, segment mapping, integrity/hash, access, export/copy events, clock offset, recording interruptions, corruption and missing sections. A recording may be audio, video, screen capture or other configured source. No fabricated media or claims of recording where none exists.

### 12.2 Notes

Notes are attributed to their author, created time, event time and type (contemporaneous, later reconstruction, observation, summary, administrative). Preserve original note versions. Distinguish direct quotation from paraphrase and personal observation from interpretation. Notes do not replace recordings.

### 12.3 Transcript

A transcript has a version, author/process, source recordings/notes, coverage, speaker attribution confidence, timestamps, inaudible markers, overlaps, interpretation markers, corrections and omissions. It may be verbatim, near-verbatim or summary; its declared type is visible. Automated transcription is a derived source, never silently authoritative. Human corrections preserve original machine output and reviewer changes.

### 12.4 Recording integrity

Never edit the original asset in place. Derived clips, redactions, conversions, transcripts and copies retain source links, operation history, responsible actor, time, scope and integrity references. Missing or inaccessible media is clearly marked; the UI must not present a placeholder as original evidence.

## 13. Statements, adoption and correction

A statement may be dictated, written, compiled from interview turns or provided independently. It records author, speaker, source material, version, language, preparation method, review, proposed corrections, adopted/disputed status and acknowledgement/signature reference where configured.

Statement statuses may include draft, prepared, presented_for_review, adopted, adopted_with_changes, disputed, declined_to_adopt, corrected, superseded, withdrawn, disclosed and restricted. The statement is not automatically identical to transcript or recording. Participant review is a distinct event: who reviewed which exact version, when, with what corrections, agreement or dispute.

A correction never overwrites original wording. Preserve both submitted and corrected versions, reason, author, time, exact differences and approval. A participant's disagreement remains visible. A statement may be withdrawn or superseded while retaining history. No system may fabricate a signature, consent, adoption or verbatim quotation.

## 14. Interpreter and language handling

Record source language, target language, interpreter identity/qualification reference, interpretation mode, interpreted turns, clarification requests, uncertainty, dialect/terminology issues, corrections and participant confirmation/dispute. Preserve original-language content where available and link translation as a separate attributed rendition. Do not collapse interpreter speech into participant speech.

Where the original language is unavailable, mark it unavailable. A machine translation is a derived aid and must not be represented as certified or verbatim. Translation ambiguity remains explicit. Interpreter conflicts or unavailability can pause or terminate the session under configured policy.

## 15. NPC behaviour and knowledge boundaries

NPC speech is generated from the person's actual knowledge state, memory, language, personality, stress/context, prior experiences and information plausibly received. It is not generated from hidden truth or full case context.

An interviewee may remember accurately, partially, incorrectly or not at all; misunderstand a question; correct themselves; contradict an earlier account; refuse; remain silent; volunteer unrelated information; be evasive or truthful; lie for varied reasons; be uncertain; or provide no useful information. These behaviours are not deterministic guilt cues. No personality, emotion, speech pattern, disability, accent, demographic trait or interview demeanour is a lie detector.

NPC knowledge may include facts they observed, experienced, were told, read or lawfully received. Knowledge of another participant's confidential account, police-only material or hidden occurrence truth requires a plausible information path. NPCs cannot see the player's private notes unless explicitly shared in-world. NPCs do not know what the player has not disclosed to them.

The AI may create natural dialogue and source records, but every canon-changing statement/answer is persisted as a structured, attributed event. Non-canon flavour cannot contradict canonical records. If generation cannot establish plausible knowledge, the response must remain uncertain or unavailable rather than inventing facts.

## 16. Player agency and no-hint policy

The player controls whether an interview occurs, who is interviewed, timing, authorised approach, questions, follow-up, pause, termination and review. The interface may show the interview record, available source material, participant history the player is authorised to see, recording status, notices and chronological events. It must not recommend who to interview next; suggest the next question or line of enquiry; rank interviewees by culprit likelihood; reveal which answer is true from hidden generator knowledge; insert leading prompts or solution cues; auto-progress an interview or force a confession; penalise a player for not conducting a suggested action; or surface hidden occurrence truth in interviewer notes or generated questions.

If the player asks for a transcript, show the transcript and its limitations. If they ask for all interviews, list all authorised records neutrally. No unsolicited advice follows the record display.

## 17. Hidden truth protection

The exact trigger is the player's standalone input bingo in lowercase, with no punctuation, surrounding whitespace or extra words. Other variants do not trigger. Before that trigger:
- No culprit, perpetrator or accomplice identity is disclosed directly or indirectly.
- Hidden generator truth is excluded from ordinary interview prompts, NPC responses, metadata, record ordering, transcript generation, summaries, analytics, notifications, exports, error messages and visuals.
- Interviewer/NPC knowledge cannot exceed plausible information paths.
- No generated confession is used as a convenient reveal mechanism.
- No answer is marked true/false based on hidden truth.
- No suspicious-answer marker is generated from hidden truth.
- A permitted reveal does not waive unrelated access restrictions or transform allegation into adjudicated fact.

BP-42 owns enforcement across all channels; BP-35 prevents hidden data from entering ordinary generation context; BP-43 tests leakage.

## 18. Evidence, intelligence and disclosure links

BP-19 may reference exact source versions from BP-20/BP-21/BP-23/BP-24 and other authorised systems. It does not create exhibits, grade intelligence, determine forensic meaning or decide admissibility. If an interviewer shows an item, record which exact version/representation was shown, by whom, when, under what authority, and participant response. Showing a summary is not showing the original.

A statement may itself be a source record referenced by BP-23/BP-27, subject to their rules. BP-19 maintains source integrity; BP-23 owns exhibit conversion/continuity. BP-27 owns disclosure decisions and legal disclosure packages. Disclosure records identify exact version, recipient, authority, date/time, restrictions, redactions and acknowledgement where available. No automatic disclosure to all case participants.

## 19. Safeguarding, welfare and accessibility

BP-17 owns victim/witness support and safeguarding plans; BP-26 owns custody welfare; BP-30 owns policy; BP-42 controls sensitive access. BP-19 records interview-relevant requests and events without creating a duplicate clinical or welfare record.

Support may include breaks, accessible communication, interpreter, support person, adjusted pace, alternative format, postponement or termination. Exact eligibility, thresholds, notices and authority remain open fictional policy decisions. Record only information necessary for the interview and link to the authoritative owner. A distress event is not an admission or credibility assessment. A request for support is not grounds to infer unreliability.

## 20. Interview quality review

A review can assess procedural completeness, recording integrity, chronology, source consistency, transcription quality, question clarity, participant role, interpreter handling, corrections, disclosure readiness and policy compliance. It must not decide whether the interviewee is guilty or whether an answer is true based solely on demeanour.

Review records reviewer, authority, scope, exact version, findings, limitations, corrective action, due/pending state and closure. Review may identify a missing notice, incomplete recording, ambiguous question, disputed statement, inaccurate transcript or access incident. It cannot silently edit original source content. Internal standards and scoring vocabulary require BP-30/BP-31/BP-44 approval.

## 21. Permissions, confidentiality and audit

BP-42 owns access policy. Suggested capabilities: interview.read.index; interview.read.participant; interview.read.procedural; interview.read.turns; interview.read.recording; interview.read.restricted; interview.create.request; interview.authorise; interview.schedule; interview.conduct; interview.record; interview.transcribe; interview.review; interview.correct; interview.statement.prepare; interview.statement.present; interview.statement.adopt; interview.disclose.reference; interview.export; interview.audit.read.

Read does not imply record, correct, authorise, adopt, disclose or export. Apply least privilege to search, snippets, autocomplete, counts, reports, notifications, prompts, media, transcripts and backups. Participant access is not presumed. Confidentiality restrictions and sealed/restricted records are explicit. Emergency access, if configured, is scoped, reasoned, time-limited, logged and reviewed. Audit sensitive reads, writes, playback, copy, export, redaction and access changes.

## 22. Time, pause and scheduling

All interview times use BP-37 canonical in-world time, retaining source clock offsets and uncertainty. Distinguish event time, recording time, transcript preparation time, record time and effective time. A recording's embedded timestamp is a source claim, not automatically canonical time.

While the player is outside the simulation, no interview starts, continues, NPC answers, recording segment, break, notice, review, appointment, deadline, notification or scheduled event progresses. Resume restores exact persisted state; no real-world catch-up or invented off-screen interview. If an interview is in progress at pause, it remains at the exact paused turn/segment state. The player may resume or terminate after returning.

## 23. Persistence, provenance and correction

BP-38 owns schemas, constraints, provenance and retention policy; BP-39 owns durable persistence/recovery. BP-19 owns interview semantics and source content. Preserve original questions, answers, notices and participant wording; original recordings and source references; every transcript/statement/note version; speaker/author/interpreter attribution; chronology, sequence and uncertainty; participant attendance and procedural events; authority, access and disclosure history; corrections, disputes, redactions and supersession; derived summaries and AI generation provenance.

Transactions must be atomic across episode, participant, turn, source and audit records. Partial failures must not leave an interview that appears complete when turns/media/audit are missing. Idempotent retries must not duplicate turns or statements. Restore must reconcile media references, checksums, versions and event history. Retention/deletion/archiving remain open policy decisions; no destructive deletion is authorised by this draft.

## 24. Interface and reports

Text is the complete interface. It must support create/request and inspect an interview plan; view authorisation and qualification state; start, pause, resume, interrupt, complete, suspend, cancel or terminate with explicit event; add participants and record attendance intervals; record notices and procedural status; enter exact questions, answers and non-answer markers in sequence; link recording segments, notes, transcript versions and statements; review participant adoption, correction or dispute; view chronology and recording gaps; search and list authorised interview records neutrally; link exact source versions and disclosure references; inspect provenance, corrections and access history where authorised.

Reports include episode summary (clearly labelled summary), full turn chronology, participant/attendance list, procedural notice history, recording/media inventory, transcript and statement version history, correction log, source links, disclosure references and review outcome. Every report states scope, as-of time, version and limitations. Optional diagrams/timelines are derived views and never replace canonical text/records.

## 25. Inputs, outputs and event contracts

**Inputs:** BP-03 identity; BP-05/BP-06/BP-32 authority/qualification; BP-15 case; BP-16 interview request and investigative purpose; BP-17/BP-18 participant roles; BP-20 surveillance references; BP-21 intelligence references; BP-23 exhibits; BP-24 forensic references; BP-26 custody constraints; BP-27 disclosure requirements; BP-35 NPC generation; BP-37 time; BP-42 permissions.

**Outputs:** interview episodes; participant attendance; procedural notice events; ordered turns; media/recording references; notes; transcript and statement versions; review/correction records; source/disclosure links; audit events.

Every event includes event ID, interview/case/person references, actor, authority, canonical time, record time, source/version, schema version, sequence/idempotency key, prior/resulting state, access class and provenance.

Minimum events: interview requested/authorised/declined/scheduled/started/paused/resumed/interrupted/completed/suspended/terminated/cancelled; participant added/arrived/departed/role-changed; notice prepared/delivered/acknowledged/disputed/repeated; segment started/ended; turn recorded/corrected; recording linked/gap/fault/copy/export/redaction; note created/corrected; transcript created/reviewed/corrected/superseded; statement prepared/presented/adopted/disputed/corrected/withdrawn; interpreter assigned/changed/clarification; review opened/closed; disclosure reference added/updated; access granted/denied/emergency-used; restore reconciled.

## 26. Failure handling and edge cases

- Participant identity unresolved: preserve candidate/unidentified reference; do not invent a person.
- Participant identity disputed: preserve competing claims and source.
- Interview request without authority: retain request; block restricted start.
- Interviewer qualification expired/unknown: apply configured block; never infer qualification.
- Participant declines: record exact response and end state without guilt inference.
- Participant absent/no-show: record event; no fabricated interview.
- Interview interrupted: preserve segment and interruption; allow linked resumption.
- Recording failure: mark gap and source fault; never invent missing speech.
- Multiple recording devices disagree: preserve each source and offset.
- Overlapping speech: represent overlap/uncertainty.
- Unintelligible audio: mark inaudible; no guessed transcript.
- Transcript correction: preserve original machine/human version.
- Interpreter error: append correction and link affected turns.
- Participant disputes statement: preserve both statement and dispute.
- Participant adopts with changes: retain presented and adopted versions.
- Interviewer asks leading/compound question: preserve exact question; quality review may flag it.
- Repeated question: retain every instance and context.
- Contradictory answers: retain all versions; no automatic selection.
- Volunteered statement: distinguish from response to a question.
- Admission later withdrawn: retain original and retraction, link exact turns.
- Suspect becomes victim/witness elsewhere: independent BP-17/BP-18 roles.
- Case closed: interview remains immutable and accessible under policy.
- Case reopened: new episode or follow-up links to original.
- Participant deceased: preserve historic record; no simulated participation after death.
- Confidential participant: enforce access in every output.
- Hidden truth appears in generation context: reject/suppress and audit without exposing it.
- NPC lacks knowledge: answer uncertain/unavailable, not fabricated.
- Player pauses/exits: freeze exact interview state.
- Concurrent transcript edits: preserve both versions and reconcile.
- Duplicate event retry: idempotent operation.
- Partial persistence failure: atomic rollback or explicit incomplete state.
- Media missing after restore: flag unresolved asset, do not substitute placeholder as original.
- Disclosure request: BP-27 owns decision; BP-19 provides exact source version.
- Storage compaction: preserve full source wording and attribution.

## 27. Dependencies and failure contracts

| Dependency | Contract | Failure behaviour |
|---|---|---|
| BP-03 | Canonical person identity and permanent promotion | Keep unresolved; no duplicate identity |
| BP-05/BP-06/BP-32 | Interviewer authority and qualification | Block configured restricted workflow; audit |
| BP-15 | Case identity/access | No orphan episode |
| BP-16 | Purpose/request/investigative decision | No automatic investigative recommendation |
| BP-17/BP-18 | Participant case roles | Reference exact role version; do not redefine |
| BP-20/BP-21 | Surveillance/intelligence sources | Preserve restrictions and source version |
| BP-23/BP-24 | Exhibit/forensic source | Reference only; no altered evidence |
| BP-26 | Custody/welfare state | Respect authoritative constraints; no duplicate custody |
| BP-27 | Disclosure/legal process | No unilateral disclosure |
| BP-28 | Court proceedings | No judicial outcome inference |
| BP-35 | NPC knowledge and generation | Refuse hidden truth/unsupported knowledge |
| BP-37 | Canonical time/pause | Freeze all progression while paused |
| BP-38/BP-39 | Schema, provenance, transactions and recovery | Atomic persistence; no false completion |
| BP-40/BP-41 | Interface and reporting | Same access/reveal rules across every output |
| BP-42 | Permissions and hidden-truth security | Deny safely; audit |
| BP-43/BP-44 | Test evidence and change control | No completion without evidence/approval |

## 28. Acceptance tests

These criteria are specified, not executed. BP-43 must attach reproducible evidence before a test is passed.

### Planning, identity and participants
- **INT-AT-001** — Every interview has a stable opaque ID.
- **INT-AT-002** — Every interview references a valid case or explicitly approved non-case context.
- **INT-AT-003** — Participant links reference canonical BP-03 person IDs.
- **INT-AT-004** — Unresolved identity remains explicitly unresolved.
- **INT-AT-005** — Interview episode does not create a duplicate person.
- **INT-AT-006** — Materially relevant person is permanently promoted through BP-03.
- **INT-AT-007** — Every participant has an episode-specific role.
- **INT-AT-008** — Presence and active participation are separate.
- **INT-AT-009** — Arrival/departure intervals are retained.
- **INT-AT-010** — Late arrival does not imply knowledge of prior segment.
- **INT-AT-011** — Participant may leave and return with chronology preserved.
- **INT-AT-012** — Interviewer authority is checked against BP-05/BP-30 policy.
- **INT-AT-013** — Interviewer qualification is checked against authoritative record.
- **INT-AT-014** — Invalid interviewer assignment is blocked or explicitly flagged per policy.
- **INT-AT-015** — Requester, authoriser and interviewer are separately attributable.
- **INT-AT-016** — Interview purpose and scope are recorded.
- **INT-AT-017** — Purpose change is a versioned event.
- **INT-AT-018** — Interview type does not determine legal/suspect status.
- **INT-AT-019** — No-show is recorded without fabricated content.
- **INT-AT-020** — Declined interview is preserved without guilt inference.

### Authority, notices and lifecycle
- **INT-AT-021** — Interview request does not automatically authorise restricted interview.
- **INT-AT-022** — Unconfirmed authority blocks configured restricted workflow.
- **INT-AT-023** — Exact configured notice/caution version is retained.
- **INT-AT-024** — Notice preparation is distinct from delivery.
- **INT-AT-025** — Delivery actor, recipient and time are recorded.
- **INT-AT-026** — Acknowledgement/dispute is separate from delivery.
- **INT-AT-027** — Repeated/corrected notice retains original event.
- **INT-AT-028** — System does not invent real-world legal requirements.
- **INT-AT-029** — Every lifecycle transition records actor, authority, reason and time.
- **INT-AT-030** — Invalid state transitions are rejected.
- **INT-AT-031** — Cancellation preserves reason and prior state.
- **INT-AT-032** — Suspension does not imply completion.
- **INT-AT-033** — Interrupted interview preserves segment and interruption.
- **INT-AT-034** — Resumption links to original episode or explicitly creates follow-up.
- **INT-AT-035** — Completed interview may be reviewed without rewriting completion event.
- **INT-AT-036** — Interview lifecycle is independent from case lifecycle.
- **INT-AT-037** — Interview lifecycle is independent from suspect/offender status.
- **INT-AT-038** — Refusal/non-answer is not automatically non-cooperation or guilt.
- **INT-AT-039** — Interview can be unproductive without forced success.
- **INT-AT-040** — Interview cannot progress while player is outside simulation.

### Turns and source content
- **INT-AT-041** — Every question/answer turn has a stable ID and sequence.
- **INT-AT-042** — Speaker identity and role are recorded for each turn.
- **INT-AT-043** — Exact original question wording is preserved.
- **INT-AT-044** — Exact answer wording is preserved where source permits.
- **INT-AT-045** — Non-answer, silence and refusal have distinct markers.
- **INT-AT-046** — Volunteered statement is distinguished from answer to question.
- **INT-AT-047** — Clarification and correction turns retain chronology.
- **INT-AT-048** — Repeated questions remain separate turns.
- **INT-AT-049** — Compound/leading/ambiguous questions are not silently rewritten.
- **INT-AT-050** — Overlapping speech is represented with uncertainty.
- **INT-AT-051** — Inaudible content is marked, not fabricated.
- **INT-AT-052** — Contradictory answers remain available as separate turns.
- **INT-AT-053** — Answer classification describes form, not truth.
- **INT-AT-054** — Admission is not automatically treated as proof.
- **INT-AT-055** — Denial is not automatically treated as exculpatory proof.
- **INT-AT-056** — Interview demeanour is not used as a lie detector.
- **INT-AT-057** — Original turn remains unchanged after correction.
- **INT-AT-058** — Turn ordering is stable across export/restore.
- **INT-AT-059** — Every derived summary links to underlying source turns.
- **INT-AT-060** — Summary is never labelled verbatim transcript.

### Recording, notes and transcripts
- **INT-AT-061** — Recording reference identifies exact source asset/version.
- **INT-AT-062** — Recording start/end and segment coverage are recorded.
- **INT-AT-063** — Recording gap is explicit and time-bounded where possible.
- **INT-AT-064** — Recording fault does not generate replacement content.
- **INT-AT-065** — Multiple recording sources remain independently preserved.
- **INT-AT-066** — Source clock offset/uncertainty is retained.
- **INT-AT-067** — Original recording is never edited in place.
- **INT-AT-068** — Derived clip links to original and records operation.
- **INT-AT-069** — Playback/copy/export events are audited.
- **INT-AT-070** — Note author and creation time are preserved.
- **INT-AT-071** — Contemporaneous note differs from later reconstruction.
- **INT-AT-072** — Direct quote differs from paraphrase.
- **INT-AT-073** — Transcript declares verbatim/near-verbatim/summary type.
- **INT-AT-074** — Transcript maps speakers and turns to source where possible.
- **INT-AT-075** — Automated transcript is labelled derived.
- **INT-AT-076** — Human transcript correction preserves machine/original version.
- **INT-AT-077** — Transcript omissions and unavailable source segments are explicit.
- **INT-AT-078** — Transcript version and author/process are recorded.
- **INT-AT-079** — Missing media after restore is flagged, not replaced by false original.
- **INT-AT-080** — Recording integrity metadata is retained through persistence.

### Statements, interpreter and review
- **INT-AT-081** — Statement has its own ID and version.
- **INT-AT-082** — Statement is not silently equated with recording/transcript.
- **INT-AT-083** — Presented version is preserved before participant review.
- **INT-AT-084** — Adopted-with-changes retains both versions.
- **INT-AT-085** — Participant dispute is retained without forced resolution.
- **INT-AT-086** — Declined adoption is not represented as adoption.
- **INT-AT-087** — Signature/acknowledgement is never fabricated.
- **INT-AT-088** — Correction is append-only with author, time and reason.
- **INT-AT-089** — Withdrawal/supersession preserves previous statement.
- **INT-AT-090** — Interpreter identity and role are recorded.
- **INT-AT-091** — Original language and translated rendition remain distinct.
- **INT-AT-092** — Interpreter uncertainty and correction are preserved.
- **INT-AT-093** — Machine translation is labelled derived.
- **INT-AT-094** — Participant clarification/dispute of translation is retained.
- **INT-AT-095** — Quality review references exact episode/version.
- **INT-AT-096** — Review does not determine guilt from demeanour.
- **INT-AT-097** — Review flags missing/ambiguous source without rewriting it.
- **INT-AT-098** — Corrective action is tracked separately from original event.
- **INT-AT-099** — Interview chronology, participants and recording references reconcile.
- **INT-AT-100** — Review and statement status remain independently auditable.

### NPC knowledge and player agency
- **INT-AT-101** — NPC response uses only plausible known information.
- **INT-AT-102** — NPC cannot access hidden generator truth through interview context.
- **INT-AT-103** — NPC cannot know confidential account without plausible information path.
- **INT-AT-104** — NPC cannot see private player notes without in-world sharing.
- **INT-AT-105** — Memory uncertainty can be expressed without forced precision.
- **INT-AT-106** — NPC may refuse, remain silent or provide no useful information.
- **INT-AT-107** — NPC demeanour is not a deterministic guilt cue.
- **INT-AT-108** — Personality/demographic/health traits do not act as lie detectors.
- **INT-AT-109** — No generated confession is used as a hidden-truth reveal.
- **INT-AT-110** — Every canon-changing generated turn is persisted as attributed event.
- **INT-AT-111** — Non-canon flavour cannot contradict canonical records.
- **INT-AT-112** — Player chooses whom to interview and what to ask.
- **INT-AT-113** — Interface does not recommend next interviewee.
- **INT-AT-114** — Interface does not suggest next question or line of enquiry.
- **INT-AT-115** — No suspect/culprit ranking is generated.
- **INT-AT-116** — No unsolicited solution hint is emitted.
- **INT-AT-117** — No answer is labelled true/false using hidden truth.
- **INT-AT-118** — Exact standalone lowercase bingo is the only reveal trigger.
- **INT-AT-119** — Case/punctuation/whitespace/extra-word variants do not trigger.
- **INT-AT-120** — No indirect leak through metadata, order, summary, export or visual.

### Security, time, population and persistence
- **INT-AT-121** — Access restrictions apply to index, turns, media, transcripts and exports.
- **INT-AT-122** — Participant access is not presumed.
- **INT-AT-123** — Sensitive playback, copy, export and access changes are audited.
- **INT-AT-124** — Disclosure decision remains BP-27-owned.
- **INT-AT-125** — Exact source version is identified in disclosure reference.
- **INT-AT-126** — No interview progress occurs during pause/outside simulation.
- **INT-AT-127** — Resume restores exact turn/segment state without catch-up.
- **INT-AT-128** — Each living participant is counted once under the 10,000 cap.
- **INT-AT-129** — Permanent person promotion is never reversed after case closure.
- **INT-AT-130** — Atomic persistence prevents orphan episode/participant/turn records.
- **INT-AT-131** — Idempotent retry does not duplicate turns or statements.
- **INT-AT-132** — Concurrent edits preserve both versions for reconciliation.
- **INT-AT-133** — Restore reconciles record/media references and integrity metadata.
- **INT-AT-134** — Storage compaction preserves wording, uncertainty and provenance.
- **INT-AT-135** — Every material record change has actor, authority, time and version.
- **INT-AT-136** — No sensitive content leaks through error or search snippets.
- **INT-AT-137** — Optional visual timeline traces to canonical source records.
- **INT-AT-138** — Every report states scope, as-of time and limitations.
- **INT-AT-139** — No test is marked passed without reproducible BP-43 evidence.
- **INT-AT-140** — Every implementation change maps to approved requirement and BP-44 change record.

## 29. Traceability to original source

Original source JSON is unchanged. IDs use crosswalk 1-based source array positions and original JSON pointers.

| Source ID | Original source area | BP-19 incorporation |
|---|---|---|
| S34.R01 | Interview planning, cautions/procedural status, participants, recordings, notes, questions, answers, breaks, disclosure and statement versions | Sections 5–14, 18–25; BP-19 owns episode and source records; BP-17/BP-18 retain role ownership; BP-27 owns legal disclosure. |
| S34.R02 | Verbatim/detailed source preservation; summaries distinguished from originals | Sections 11–14, 23–24; immutable original turns/media and versioned derivatives. |
| S34.R03 | No leading prompts or hidden solution disclosure | Sections 15–17; NPC knowledge firewall and player agency. |
| S34.T01 | Interview chronology, participants and recording references reconcile | INT-AT-099 and lifecycle/chronology/media requirements. |
| S43.R01 | Naturalistic, varied text consistent with records, knowledge boundaries, voice and uncertainty | Sections 15–16; generated dialogue bounded by character knowledge and persisted as attributed turns. |
| S43.R02 | Separate hidden world truth, player-visible information and NPC knowledge | Sections 15–17; three-way information separation. |
| S43.R03 | Exact bingo reveal condition | Section 17; exact lowercase standalone trigger only. |
| S43.R04 | No unsolicited hints or next-investigation instructions | Section 16; player controls questions and next action. |
| S43.R05 | Canon-changing generated claims persisted as structured events | Sections 15, 23 and 25; all turns/events persisted with provenance. |
| S43.T01 | No hidden truth leak before exact trigger | INT-AT-102, INT-AT-109, INT-AT-118–120. |
| S43.T02 | NPC knowledge does not exceed plausible information | INT-AT-101–108. |
| S12.R03 | Restricted public/civil records access and provenance interfaces | Sections 21 and 23; BP-38/BP-42 own records/access. |
| S38.R01–R03 | Legal disclosure, proceedings and outcome references | Sections 18, 21, 25 and 27; BP-27/BP-28 remain authoritative. |
| S45.R01–R03 | Optional maps/diagrams/visual evidence traceable to canonical data | Section 24; optional timeline/visuals are derived, never required. |
| S46.R01–R05 | Database schemas, transactions, versioning and persistence | Sections 3, 4, 23 and 25; BP-38/BP-39 own infrastructure. |
| S47.R01–R05 | Storage efficiency and capacity governance | Section 23; lossless semantic compaction and no duplicate binary/content storage. |
| S48.R01–R03 | Security, permissions and audit | Section 21; BP-42 owns access and audit controls. |
| S50.R01–R03 | Testing and quality assurance | Section 28; BP-43 owns evidence-based execution. |
| S52.R01–R04 | Canon and change governance | Section 30; BP-44 owns approved changes and fixed structure. |

Cross-cutting invariants X01–X10 and C01–C09 apply: canonical identity, stable IDs, source provenance, distinct fact/allegation/inference/opinion, effective-dated records, single authoritative owner, immutable history, bounded time, player agency, text-first sufficiency, lossless storage and explicit interfaces.

## 30. Open decisions and risk register

### Open decisions

1. Exact fictional interview categories and which require formal authorisation.
2. Caution/rights notice wording and when each applies.
3. Interviewer authority, qualification and supervisory approval matrix.
4. Voluntary/required/compulsory participation categories in Saltwater canon.
5. Age/vulnerability/support categories and corresponding fictional safeguards.
6. Interpreter qualification and translation certification vocabulary.
7. Recording requirements, exceptions, storage format and retention periods.
8. Statement adoption/signature/withdrawal policy.
9. Transcript standards, timestamp precision and speaker-confidence vocabulary.
10. Permitted interview formats, locations and equipment.
11. Interview quality-review standards and escalation authority.
12. Disclosure and sealing/retention policy with BP-27/BP-38/BP-42.
13. NPC dialogue generation boundaries and character-state model with BP-35.
14. Interview ID/turn ID formats with BP-38.
15. Exact text command syntax and optional visual design with BP-40.

### Risks and mitigations

| Risk | Mitigation |
|---|---|
| Summary mistaken for original | Explicit content type and source mapping |
| Transcription invents missing speech | Inaudible markers; immutable source reference |
| Interview response treated as guilt | Separate semantics; no demeanour scoring |
| NPC omniscience | Knowledge provenance and generation isolation |
| Hidden culprit leaked through dialogue | BP-14 firewall, exact bingo gate and adversarial tests |
| Leading prompt railroads player | No unsolicited prompts or next-question suggestions |
| Recording gap concealed | Explicit segment/gap/fault records |
| Correction erases original | Append-only versions |
| Interpreter changes meaning | Original and interpreted turns separated |
| Disclosure bypasses legal owner | BP-27 decision contract |
| Sensitive media leaks | BP-42 checks on playback/export/search |
| Background interview advances while paused | BP-37 freeze invariant |
| Storage compaction loses exact wording | Lossless preservation and checksums |

## 31. Design completion checklist

- [ ] All S34.R01–R03 and S34.T01 source requirements incorporated.
- [ ] All applicable S43 requirements/tests incorporated.
- [ ] Interview episode is separate from case, investigation and participant role.
- [ ] Participant identity and roles are canonical and versioned.
- [ ] Authority and qualification are explicit.
- [ ] Procedural notices are recorded as actual events, not assumed.
- [ ] Questions, answers and non-answers preserve exact chronology.
- [ ] Recordings, notes, transcripts and statements remain distinct.
- [ ] Original media and text are never overwritten.
- [ ] Interpreter/translation uncertainty is preserved.
- [ ] Participant review, adoption, dispute and correction are separate.
- [ ] NPC knowledge is plausible and bounded.
- [ ] No guilt inference from demeanour, silence or inconsistency.
- [ ] Exact bingo reveal gate covers all outputs.
- [ ] No unsolicited hints or next-question prompts.
- [ ] No progression while player is outside simulation.
- [ ] Population cap and permanent promotion are enforced by BP-03.
- [ ] BP-27 owns disclosure and BP-42 owns permissions.
- [ ] All 140 acceptance tests are traceable and await BP-43 execution.
- [ ] Open decisions remain explicit; no unsupported policy invented.
- [ ] No Neon write, migration, seed or import has been made or authorised.

## 32. Status and next dependencies

This is a full division design draft, not user-approved design or implementation evidence.

- Specification: **DESIGNED_DRAFT**
- User approval: **PENDING**
- Implementation: **NOT_STARTED**
- Test execution: **NOT_STARTED**
- Verification: **NOT_STARTED**
- Neon/database writes: **NONE; NOT AUTHORISED**

Next fixed division: **BP-20 — Surveillance**. BP-20 owns surveillance planning/authorisation, observation operations, technical monitoring, source/coverage/collection/retrieval and surveillance products, while BP-23 owns evidential continuity after collection.
