# BP-42 — Security and Permissions

**Project:** Saltwater  
**Division:** BP-42 of the fixed 44-division structure  
**Specification:** DESIGNED_DRAFT — review/approval pending  
**Implementation / test execution / verification:** NOT_STARTED  
**Primary responsibility:** Identity trust, authentication, authorization, access control, information protection, secrets and security audit.  
**Write restriction:** No Neon write, migration, seed, import, bulk operation, credential change or production security-policy deployment is authorised by this specification.

## 1. Purpose

BP-42 defines the security architecture governing who or what may authenticate, access information, issue commands, mutate records, administer systems, disclose data and perform privileged operations in Saltwater. It protects the fictional world's integrity, player agency, private information, evidence, institutional records, hidden case truth, infrastructure credentials and the separation between development and authoritative runtime environments.

Security is enforced at the authoritative service/data boundary. A hidden button, obscured identifier, interface route or AI instruction is not an access control. Every read, write, search, aggregation, export, delivery, visualisation and administrative operation must be checked against current principal, resource, action, purpose and policy context.

## 2. Binding principles

1. Deny by default; grant least privilege only through explicit, attributable policy.
2. Authentication proves identity; authorization separately determines each permitted action.
3. Player, officer persona, administrator, operator, developer, service and system identities are distinct.
4. Rank, position, grade, authority, clearance, qualification and assignment do not automatically confer identical privileges.
5. Enforce authorization at owning services, not merely in BP-40 presentation.
6. Apply controls to APIs, commands, search, reports, notifications, maps, media, exports and caches.
7. Protect hidden world truth and the exact `bingo` gate centrally.
8. Secrets never enter source control, narrative records, ordinary logs or player-facing output.
9. Security actions are attributable, auditable, reviewable and versioned.
10. Security processes do not advance simulation time or NPC activity while paused or absent.
11. Do not invent provider capabilities; verify implementation before claiming protection or connectivity.
12. Security controls do not alter domain truth or bypass owning-domain lifecycle rules.

## 3. Scope and exclusions

**Included:** principal/session model; authentication; authorization; role/attribute/purpose policies; service identities; least privilege; access lifecycle; classification; sensitive-data controls; secrets; API/input security; output/media security; search/cache/export controls; audit; monitoring; incident response; environment separation; policy administration; recovery security.

**Excluded:** canonical person/personnel identity ownership (BP-03/BP-06); police command authority (BP-05/BP-30); domain record lifecycle/schema ownership (BP-15/BP-38); simulation event execution (BP-35); canonical time (BP-37); persistence/recovery execution (BP-39); interface rendering (BP-40); notification/report semantics (BP-41); independent testing governance (BP-43); formal configuration/change governance (BP-44). BP-42 supplies mandatory security contracts to these domains.

## 4. Principal, identity and session model

Human accounts, player principals, officer personas, institutional actors, administrators, operators, developers, service principals, system principals and isolated test principals are distinct classes. Every principal has stable ID, owner, status, authentication binding, effective permissions, policy version, lifecycle and audit references. Canonical person identity remains BP-03/BP-06 owned; BP-42 references it and does not create duplicate people.

Session states: requested, authenticating, authenticated, active, step-up-required, restricted, expired, revoked, locked and terminated. A session records issue/expiry, principal, authentication context, active officer persona where relevant, environment, revocation version and correlation ID. Logout, expiry, disablement, persona change and critical permission revocation invalidate protected state and caches. Session expiry uses real security time and cannot progress NPCs or game time.

## 5. Authentication

Authentication mechanisms are configurable and must use verified provider capabilities; no particular external identity provider is assumed. Support secure credential handling, session protection, rate limits, account recovery, optional multi-factor/step-up checks and prompt revocation as configured. Authentication failure messages must not reveal whether a protected account or record exists. Authentication success never implies domain access.

Human and service authentication are distinct. Service credentials have named owners, workload purpose, restricted scopes, rotation and revocation. A service cannot impersonate a human without explicit, auditable delegation. Secrets are supplied through approved secret management and are never committed to GitHub or exposed to the player-facing interface.

## 6. Authorization architecture

Authorization is a decision over principal, action, resource, resource attributes, requested purpose, context, effective time and policy version. The implementation may combine role-based, attribute-based and relationship/context-based rules, but the final decision is explicit and deterministic.

Permission dimensions include read, list, search, inspect, create, edit, amend, approve, issue, assign, execute, disclose, export, delete, archive, administer and audit; domain, record, field, case, unit, assignment, location, purpose, classification and time scope; human, officer, service and system actor; and standing, temporary, delegated and emergency grants.

An officer's rank or job title alone is insufficient for protected actions. Effective authority is resolved from BP-05/BP-06/BP-07/BP-08 and applicable policy. Acting roles have explicit scope and expiry. A delegator cannot delegate powers they do not hold. Subdelegation is denied unless explicitly authorised.

Default deny. Explicit deny prevails over accidental broad grants. Unavailable policy evaluation fails closed for protected operations. Every decision records policy version, principal, requested action/resource, result, reason and time. Owning services recheck authorization at point of action rather than trusting stale interface decisions.

## 7. Separation of duties and privileged access

Support independent approval, review and execution where configured. A principal cannot approve their own restricted action where policy requires independent approval. Conflicts of interest may restrict access or require recusal; they are not evidence of misconduct. Emergency/break-glass access is separately justified, time-limited, scoped, audited and reviewed. It does not disable logging or hidden-truth protection.

## 8. Permission lifecycle and governance

Grant states include requested, pending approval, active, suspended, expired, revoked, denied and superseded. Each grant records grantor, recipient, scope, purpose, justification, approval, effective period, policy version and review date. Temporary grants expire by real security time. Personnel transfer, suspension, leave, separation, retirement, role change or assignment change triggers permission recalculation.

Revocation is enforced at the authoritative boundary without waiting for interface refresh. Access reviews identify stale, excessive, orphaned and conflicting grants. Activated policy versions are immutable; changes create new versions. Emergency changes are justified, time-bounded, audited and reviewed. BP-44 owns formal change governance.

## 9. Information classification and handling

Provide configurable handling classes suitable for public, internal, restricted, confidential and specially protected material; final fictional names and hierarchy remain open configuration. Classification may attach to records, fields, media, exports, reports, notifications and derived products. Missing classification does not make protected information public.

Medical, victim/witness, informant, minor/vulnerable-person, personnel, disciplinary, complaint, intelligence-source, surveillance, evidence, forensic, financial, government and civil-registry data require tailored access. Access may be purpose-limited. Public-facing statistics derive only from approved/redacted outputs; public access to a statistic does not grant source-record access.

Redaction is applied before data reaches a recipient, cache, queue or export. Recipient-specific redaction is independently computed. Redaction must not be reversible by ordinary recipients or leak through metadata, counts or placeholders.

## 10. Hidden world truth and player-agency firewall

Hidden offender/accomplice/perpetrator truth is specially protected. It is unavailable through ordinary player reads, operator dashboards, search, autocomplete, map labels, notifications, reports, exports, logs, telemetry, errors or AI prompts.

The exact, case-sensitive standalone trigger `bingo` is the sole reveal trigger established by project canon. Substrings, case variants, punctuation variants, whitespace variants, paraphrases and inferred intent do not trigger reveal. The reveal pathway is central and limited to its authorised response; it grants no unrelated privileges. No subsystem may implement a weaker duplicate gate.

BP-42 protects the boundary; BP-14 owns hidden occurrence truth; BP-35 owns engine execution; BP-40/BP-41 render permitted outputs. NPC knowledge remains limited to plausible observation, communication or lawful access. No unsolicited investigation hints or steering.

## 11. Application, API and input security

All API and command operations authenticate and authorize independently. Use parameterized queries or equivalent safe construction; bound resource use; validate types, lengths and allowed values; safely encode untrusted output; and protect command/template/query parsers from injection. Treat user text, external content, imported records and generated narrative as untrusted data, never as policy instructions.

Uploads validate file type, size, content and destination. Downloads re-check permission at retrieval. Session identifiers are protected and invalidated on logout/revocation. Authentication attempts are protected against abuse. Account recovery cannot bypass identity and audit requirements. Security-sensitive actions may require step-up authentication or confirmation.

## 12. Search, aggregation, cache and derived data

Authorization occurs before search results, counts, facets, autocomplete, ranking, snippets, pagination totals or errors are produced. Inaccessible records cannot be discovered through timing, identifiers, map markers, graph edges, metadata or placeholders. Relationship graphs, spatial views, media thumbnails, OCR, transcripts, captions and AI descriptions inherit source permissions.

Caches are partitioned by principal and policy context. Revocation and policy changes invalidate affected caches before further access. Browser history, recent items, deep links and stale sessions cannot restore access. Cached permission decisions have documented freshness/invalidation contracts. Exports, clipboard, print and share enforce equivalent restrictions.

## 13. AI, generated content and NPC access

AI receives only information authorised for the requesting principal and task. Generated summaries cannot reveal source data the recipient cannot access. NPC and AI actor permissions are separate from player and operator permissions. No prompt, narrative record, generated caption, summary, notification or error can bypass hidden-truth controls. Generated text and external content cannot alter security policy. Canon-changing claims use owning-domain structured events and audit.

## 14. Secrets, keys and infrastructure security

Credentials, tokens, private keys, connection strings and encryption material are held only in approved secret-management mechanisms. Never commit them to source control, store them in narrative records, print them to output or include them in telemetry. Access is least-privileged and attributable. Rotate and revoke compromised credentials. Separate development/test and authoritative production secrets.

Encryption at rest and in transit, key management and provider security capabilities must be verified against actual Neon, GitHub and runtime configuration before being claimed. Backups and recovery artifacts require equivalent or stronger access protection than live data. Restore validation preserves permissions, secret separation and audit continuity.

## 15. Audit, monitoring and incident response

Record successful and denied authentication/authorization decisions, grants, revocations, policy changes, privileged actions, break-glass use, secret access, export, disclosure, administrative changes and security incidents. Audit events include actor/service, action, resource, outcome, policy version, timestamp, reason and correlation reference. Do not store raw secrets or unnecessary protected payloads.

Audit history is append-only or equivalently tamper-evident against ordinary users and administrators. Audit read access is separately controlled. Monitoring distinguishes confirmed compromise, suspicious activity, policy denial and routine failure. Incident response tracks discovery, containment, recovery and review without silently altering evidence or source records. Alerts must not leak protected content.

## 16. Environment boundaries and operations

Development, test and authoritative runtime environments are visibly and technically separated. Test identities/data cannot reach canonical records or real delivery channels absent explicit isolated authorization. Production credentials cannot be used unintentionally in test environments. Operator status does not imply unrestricted domain access.

Security service outage fails closed for protected operations. A narrowly defined safe status/read-only mode may remain available only if explicitly configured and proven not to disclose protected data. Policy caches, queues, monitoring and recovery expose actual source/time of observations; never claim Neon availability without a current successful check.

## 17. Time, pause and population integrity

Authentication expiry, secret rotation, security monitoring and access revocation may use real elapsed time; they do not advance game time. No security queue, alert, NPC response or scheduled task may progress simulation activity while paused or absent.

BP-03 owns canonical person identity and the hard 10,000-living-person cap. Accounts, officer personas, service identities and permissions do not create duplicate people or bypass population accounting. A person with several roles remains one canonical person with separate role grants.

## 18. Inputs, outputs and dependencies

**Inputs:** principals and canonical identities; authentication proofs; sessions; domain records/classifications; requested actions; role/assignment/authority context; policy versions; secret/key references; service identity; environment; audit and monitoring events.

**Outputs:** authentication/session decisions; authorization allow/deny; scoped grants; revocations; redaction decisions; protected service credentials/claims; audit events; security alerts; policy evaluation evidence; incident-response records.

**Dependencies:** BP-01–BP-41 and BP-43–BP-44. BP-42 is mandatory security authority for every domain, interface, service, queue and environment.

## 19. Acceptance tests

The following criteria define required coverage. They are design criteria only; none is claimed executed.

- SEC-AT-001: Principal identity is stable and distinct from officer persona and system identity.
- SEC-AT-002: Human, player, officer, administrator, operator, developer, service, system and test principals are distinct.
- SEC-AT-003: Authentication and authorization are separate decisions.
- SEC-AT-004: Unauthenticated protected requests are denied by default.
- SEC-AT-005: Authentication success does not grant domain access.
- SEC-AT-006: Every session records principal, authentication context, issue time, expiry, status and revocation state.
- SEC-AT-007: Expired, revoked, locked or terminated sessions cannot perform protected actions.
- SEC-AT-008: Session expiry uses real security time and never advances simulation time.
- SEC-AT-009: Officer rank, position, grade, authority, clearance, qualification and assignment remain separate permission attributes.
- SEC-AT-010: An acting appointment grants only explicitly scoped and time-limited permissions.
- SEC-AT-011: Permissions are checked at the authoritative service boundary for every read and write.
- SEC-AT-012: UI hiding, unguessable IDs and client-side checks are never treated as authorization.
- SEC-AT-013: Direct API, command, search, export, media, map and deep-link requests enforce the same policy.
- SEC-AT-014: Access decisions identify principal, action, resource, purpose, context, result and policy version.
- SEC-AT-015: Authorization is deny-by-default and least-privilege.
- SEC-AT-016: Explicit deny overrides accidental broad grants.
- SEC-AT-017: Unavailable policy evaluation fails closed for protected operations.
- SEC-AT-018: Role-based, attribute-based and relationship/context-based policies resolve deterministically.
- SEC-AT-019: Permissions distinguish read, list, search, create, edit, approve, issue, assign, execute, disclose, export, delete and administer.
- SEC-AT-020: Record-level permissions can differ for records of the same type.
- SEC-AT-021: Field-level permissions protect sensitive fields within accessible records.
- SEC-AT-022: Permission scopes may be limited by domain, case, unit, assignment, location, purpose and time.
- SEC-AT-023: Temporary grants record owner, recipient, justification, scope, approval, start and expiry.
- SEC-AT-024: Delegation identifies delegator, delegate, scope, authority and validity.
- SEC-AT-025: A delegator cannot grant powers they do not possess.
- SEC-AT-026: Subdelegation is denied unless explicitly authorised.
- SEC-AT-027: Emergency or break-glass access is justified, time-limited, attributable and reviewed.
- SEC-AT-028: Break-glass access does not disable audit or hidden-truth controls.
- SEC-AT-029: Separation of duties prevents self-approval where configured.
- SEC-AT-030: Conflicts of interest can restrict access or require independent review.
- SEC-AT-031: Personnel transfer, suspension, leave, separation and retirement trigger permission recalculation.
- SEC-AT-032: Revocation is enforced at the backend without waiting for interface refresh.
- SEC-AT-033: Access reviews identify stale, excessive, orphaned and conflicting grants.
- SEC-AT-034: Policy grants and changes are versioned with effective periods and review ownership.
- SEC-AT-035: Service principals have named owners, declared purpose and restricted scopes.
- SEC-AT-036: Service-to-service authentication is distinct from human authentication.
- SEC-AT-037: A service cannot impersonate a human without explicit auditable delegation.
- SEC-AT-038: Machine identities cannot exceed their declared workload purpose.
- SEC-AT-039: Authentication attempts are rate-limited or otherwise protected against abuse.
- SEC-AT-040: Account recovery cannot bypass identity verification and audit.
- SEC-AT-041: Failed authentication does not disclose whether an account or protected record exists.
- SEC-AT-042: Step-up authentication is required for configured sensitive actions.
- SEC-AT-043: Credentials, tokens, private keys and connection strings never appear in source control, narrative, output or ordinary logs.
- SEC-AT-044: Secrets are supplied only through approved secret-management mechanisms.
- SEC-AT-045: Secret access is least-privileged, attributable and monitored.
- SEC-AT-046: Compromised credentials can be revoked and rotated.
- SEC-AT-047: Development/test secrets are separate from authoritative production secrets.
- SEC-AT-048: GitHub tokens and Neon connection strings are never committed to repository files.
- SEC-AT-049: Information classification is explicit and configurable.
- SEC-AT-050: Missing classification does not silently make protected information public.
- SEC-AT-051: Classification changes are attributable, justified and versioned.
- SEC-AT-052: Medical information is restricted to authorised roles and purposes.
- SEC-AT-053: Victim, witness, informant, minor and vulnerable-person information has tailored access controls.
- SEC-AT-054: Personnel, disciplinary, grievance and complaint records have restricted access.
- SEC-AT-055: Intelligence source identities and protection details have separate controls.
- SEC-AT-056: Evidence, forensic, surveillance and custody records preserve controlled access and provenance.
- SEC-AT-057: Financial, procurement, government and civil-registry data enforce domain authority.
- SEC-AT-058: Public outputs use approved public data or redacted derivatives only.
- SEC-AT-059: Redaction occurs before protected content enters recipient payloads, caches, queues or exports.
- SEC-AT-060: Recipient-specific redaction is computed independently.
- SEC-AT-061: Redaction metadata does not disclose withheld content or protected record existence.
- SEC-AT-062: Search authorization occurs before counts, facets, autocomplete, snippets, ranking and pagination totals.
- SEC-AT-063: Denied records cannot be discovered through timing, IDs, placeholders or error details.
- SEC-AT-064: Relationship graphs enforce permissions on nodes, edges and labels.
- SEC-AT-065: Maps and spatial searches do not expose protected addresses or locations.
- SEC-AT-066: Notification and report previews are authorized for each recipient before delivery.
- SEC-AT-067: Caches are partitioned by principal and permission context.
- SEC-AT-068: Permission changes and revocation invalidate affected caches before subsequent access.
- SEC-AT-069: Browser history, recent items and deep links cannot restore revoked access.
- SEC-AT-070: Clipboard, print, download, export and share enforce equivalent restrictions.
- SEC-AT-071: Media thumbnails, OCR, transcripts, captions and generated descriptions inherit source permissions.
- SEC-AT-072: AI receives only data authorized for the requesting principal and task.
- SEC-AT-073: AI summaries cannot disclose source content the recipient cannot access.
- SEC-AT-074: NPC knowledge is bounded by plausible observation, communication or lawful access.
- SEC-AT-075: Hidden offender/accomplice truth is unavailable through ordinary player, operator, search, map, report, notification, export, log, telemetry and error paths.
- SEC-AT-076: The exact case-sensitive standalone trigger `bingo` is the only configured hidden-truth reveal trigger.
- SEC-AT-077: Substrings, case variants, punctuation variants, whitespace variants and paraphrases do not trigger reveal.
- SEC-AT-078: The reveal pathway is central and does not grant unrelated privileges.
- SEC-AT-079: AI prompts, generated captions and external content cannot override security policy.
- SEC-AT-080: User and retrieved content are treated as untrusted data, not executable instructions.
- SEC-AT-081: Input validation protects command, query and template parsers against injection.
- SEC-AT-082: Queries use parameterized or equivalently safe construction and bounded resource use.
- SEC-AT-083: Output encoding prevents untrusted text becoming executable markup or commands.
- SEC-AT-084: Uploads validate type, size, content and destination.
- SEC-AT-085: Downloads re-check authorization at retrieval time.
- SEC-AT-086: Session identifiers are protected and invalidated on logout or revocation.
- SEC-AT-087: Security-sensitive actions use confirmation or step-up authentication where configured.
- SEC-AT-088: Audit records capture successful and denied authentication and authorization decisions.
- SEC-AT-089: Audit records include actor, action, resource, outcome, policy version, timestamp and reason.
- SEC-AT-090: Audit history is append-only or equivalently tamper-evident against ordinary administrators.
- SEC-AT-091: Audit access is separately permissioned and monitored.
- SEC-AT-092: Audit payloads exclude raw secrets and unnecessary protected content.
- SEC-AT-093: Security events use explicit timestamp and clock semantics.
- SEC-AT-094: Security alerts distinguish confirmed compromise, suspicious activity, policy denial and routine failure.
- SEC-AT-095: Incident response records discovery, containment, recovery and review actions.
- SEC-AT-096: Security incident handling does not silently alter evidence or source truth.
- SEC-AT-097: Security administration is separate from domain record ownership.
- SEC-AT-098: Policy authorship, review, approval and deployment are attributable.
- SEC-AT-099: Activated policy versions are immutable; changes create new versions.
- SEC-AT-100: Policy changes are tested before activation and support controlled rollback.
- SEC-AT-101: Emergency policy changes are time-bounded, justified and reviewed.
- SEC-AT-102: Configuration drift is detected and reported to authorized operators.
- SEC-AT-103: Development, test and production environments are visibly and technically separated.
- SEC-AT-104: Test identities cannot access canonical records by default.
- SEC-AT-105: Production credentials cannot unintentionally be used in test environments.
- SEC-AT-106: Backups and recovery artifacts have equivalent or stronger access protection than live records.
- SEC-AT-107: Restore validates permissions, secret handling and audit continuity.
- SEC-AT-108: Encryption and key management are claimed only after actual provider capability is verified.
- SEC-AT-109: Key access and rotation are separated from ordinary database access.
- SEC-AT-110: Integrity checks detect unauthorized modification of protected records and policy.
- SEC-AT-111: Bulk retrieval and exports are bounded, authorized, attributable and monitored.
- SEC-AT-112: Bulk permission grants require explicit scope preview and confirmation.
- SEC-AT-113: Bulk revocation cannot accidentally grant access during partial failure.
- SEC-AT-114: Partial policy updates are atomic or safely recoverable.
- SEC-AT-115: Authorization outage fails closed for protected operations.
- SEC-AT-116: Policy cache has documented freshness and invalidation behaviour.
- SEC-AT-117: Stale policy cannot continue granting access after critical revocation.
- SEC-AT-118: Offline or paused simulation state does not weaken security.
- SEC-AT-119: Security monitoring and revocation never advance NPC activity or game time.
- SEC-AT-120: Every access path has positive, negative and boundary-condition tests.
- SEC-AT-121: Tests cover UI, API, commands, search, export, media, notifications and reports.
- SEC-AT-122: Tests cover same-resource access differences across roles.
- SEC-AT-123: Tests cover temporary access expiry and immediate revocation.
- SEC-AT-124: Tests cover leaks through counts, timing, autocomplete, errors, caches and history.
- SEC-AT-125: Tests cover exact bingo semantics and near-match non-triggers.
- SEC-AT-126: Tests verify secrets are absent from repository, output, telemetry and logs.
- SEC-AT-127: Tests verify service identities cannot impersonate users or exceed workload scope.
- SEC-AT-128: Tests verify restored data retains permissions, provenance and audit references.
- SEC-AT-129: Tests verify security remains effective during downstream outage and timeout.
- SEC-AT-130: Tests verify public release cannot retrieve unredacted source records.
- SEC-AT-131: Tests verify role changes invalidate stale privileges.
- SEC-AT-132: Tests verify no unapproved Neon write or migration can be triggered by security administration.
- SEC-AT-133: Tests verify the 10,000-person cap cannot be bypassed by account or role creation.
- SEC-AT-134: Tests verify one canonical person may hold multiple roles without duplicate identity.
- SEC-AT-135: Tests verify permission rules do not rewrite domain truth or adjudicated outcomes.
- SEC-AT-136: Tests verify every material authorization change is attributable and reviewable.
- SEC-AT-137: Tests verify policy rollback preserves audit history.
- SEC-AT-138: Tests verify test fixtures cannot reach player-facing or external delivery channels.
- SEC-AT-139: Tests verify operator dashboards do not expose hidden truth without reveal authority.
- SEC-AT-140: Tests verify UI visibility is never accepted as backend authorization.
- SEC-AT-141: Tests verify safe non-disclosing errors for all security failures.
- SEC-AT-142: Tests verify pause/exit freezes simulation activity while authentication and revocation remain effective.

## 20. Source traceability

The following source requirements/tests are mapped to BP-42 by the authoritative 52→44 crosswalk. Wording is copied from the unchanged source JSON.

| Source ID | Source division | Original requirement/test wording |
|---|---|---|
| S01.R01 | Sovereignty, jurisdiction and constitutional order | Define Saltwater's sovereign status, territory boundary, jurisdiction, institutions, powers, succession and constitutional rules. |
| S01.R02 | Sovereignty, jurisdiction and constitutional order | Define legal hierarchy, authority sources, emergency powers, separation of functions and jurisdictional limits. |
| S01.R03 | Sovereignty, jurisdiction and constitutional order | Prevent external-city or territorial expansion. |
| S01.T01 | Sovereignty, jurisdiction and constitutional order | Every location resolves inside the single Saltwater jurisdiction or is explicitly marked off-map. |
| S01.T02 | Sovereignty, jurisdiction and constitutional order | No institution exercises undefined authority. |
| S11.R01 | Government and public administration | Define executive, legislative, administrative and oversight functions, offices, incumbents, mandates, decision processes and records. |
| S11.R02 | Government and public administration | Represent public policy, procurement, permits, licensing, inspections and public complaints. |
| S11.R03 | Government and public administration | Ensure government actions have accountable actors, authority and dates. |
| S11.T01 | Government and public administration | Every official action has an authorised actor and traceable record. |
| S12.R01 | Civil registry and public records | Maintain civil status, identity, address, property, business, permits and other canonically required registers. |
| S12.R02 | Civil registry and public records | Track corrections, versions, issuing authority, access and provenance. |
| S12.R03 | Civil registry and public records | Support lawful in-world retrieval and controlled disclosure. |
| S12.T01 | Civil registry and public records | Record changes preserve prior values and reason for change. |
| S13.R01 | Healthcare and public health | Represent hospitals, clinics, practitioners, emergency care, capacity, appointments, treatment events and public-health alerts. |
| S13.R02 | Healthcare and public health | Model injuries, deaths, medical evidence and care access consistently without turning healthcare into a separate deep simulation. |
| S13.R03 | Healthcare and public health | Protect sensitive information through role-based access in-world. |
| S13.T01 | Healthcare and public health | Medical timelines and capacity are internally consistent. |
| S23.R01 | Police service governance and structure | Define police mandate, command hierarchy, ranks, grades, positions, authority, powers, clearance, divisions, units and reporting lines as separate concepts. |
| S23.R02 | Police service governance and structure | Maintain approximately 500 individually recorded police personnel within the 10,000 population cap. |
| S23.R03 | Police service governance and structure | Define appointment, promotion, transfer, acting roles, succession, discipline, grievance, standards and retirement rules. |
| S23.R04 | Police service governance and structure | Police service must be alive, internally coherent and operationally functional. |
| S23.T01 | Police service governance and structure | Every officer has one authoritative personnel record and valid command/position relationships. |
| S26.R01 | Police command, policy and internal governance | Represent orders, policies, briefings, operational plans, supervision, approvals, audits, complaints, misconduct and review. |
| S26.R02 | Police command, policy and internal governance | Record who authorised, issued, received and executed every material instruction. |
| S26.R03 | Police command, policy and internal governance | Support fair internal process and traceable decisions. |
| S26.T01 | Police command, policy and internal governance | Material command decisions have authority, rationale and audit trail. |
| S27.R01 | 911, call-taking, CAD and dispatch | Represent emergency/non-emergency intake, caller identity or anonymity, call recording, triage, incident creation, unit recommendation, dispatch, radio, status and closure. |
| S27.R02 | 911, call-taking, CAD and dispatch | Preserve original call content and event chronology; distinguish caller claims from verified facts. |
| S27.R03 | 911, call-taking, CAD and dispatch | Support concurrent calls, priority changes, escalation and interagency dispatch. |
| S27.T01 | 911, call-taking, CAD and dispatch | Every dispatched unit and status transition is chronologically auditable. |
| S31.R01 | Victims, witnesses, suspects and persons of interest | Maintain role-specific case links without assuming guilt; track contact, vulnerability, risk, statements, availability and procedural status. |
| S31.R02 | Victims, witnesses, suspects and persons of interest | Keep allegation, suspicion, evidential support, charge and finding distinct. |
| S31.R03 | Victims, witnesses, suspects and persons of interest | Promote relevant people to persistent full simulation. |
| S31.T01 | Victims, witnesses, suspects and persons of interest | No person is treated as guilty solely because of a generated role or suspicion. |
| S34.R01 | Interviews, interrogations and statements | Represent interview planning, cautions/procedural status as fictional canon requires, participants, recordings, notes, questions, answers, breaks, disclosure and statement versions. |
| S34.R02 | Interviews, interrogations and statements | Preserve verbatim or detailed source content where available; distinguish summaries from originals. |
| S34.R03 | Interviews, interrogations and statements | Do not generate leading prompts or reveal hidden case solutions to the player. |
| S34.T01 | Interviews, interrogations and statements | Interview chronology, participants and recording references reconcile. |
| S35.R01 | Intelligence, analysis and information handling | Represent source grading, reliability, confidence, dissemination, restrictions, analytical products, links and review dates. |
| S35.R02 | Intelligence, analysis and information handling | Separate intelligence from evidence and established fact. |
| S35.R03 | Intelligence, analysis and information handling | Preserve source provenance and uncertainty. |
| S35.T01 | Intelligence, analysis and information handling | Every intelligence item has source, confidence and handling status. |
| S36.R01 | Surveillance, observation and technical monitoring | Represent physical observation, CCTV, ANPR or equivalent systems, authorised technical monitoring, coverage, blind spots, time drift, retention and retrieval. |
| S36.R02 | Surveillance, observation and technical monitoring | Track requests, authorisations, collection windows, operators, exports and evidential continuity. |
| S36.R03 | Surveillance, observation and technical monitoring | Never treat absence of coverage as proof of absence. |
| S36.T01 | Surveillance, observation and technical monitoring | Every surveillance item has source device, coverage limits and time basis. |
| S40.R01 | Complaints, oversight and public accountability | Represent public complaints, independent review, internal investigations, inspections, findings, remedies and published outcomes. |
| S40.R02 | Complaints, oversight and public accountability | Preserve due process, conflicts of interest and auditability. |
| S40.R03 | Complaints, oversight and public accountability | Allow institutional failure and public trust to evolve from events. |
| S40.T01 | Complaints, oversight and public accountability | Every complaint has a route, owner, status and outcome or pending reason. |
| S43.R01 | AI generation, narrative and player agency | Generate detailed, varied, naturalistic text consistent with records, knowledge boundaries, character voice and uncertainty. |
| S43.R02 | AI generation, narrative and player agency | Separate hidden world truth from player-visible information and from NPC knowledge. |
| S43.R03 | AI generation, narrative and player agency | Never disclose culprit/accomplice/perpetrator identities or hidden solution unless the player types exactly 'bingo'. |
| S43.R04 | AI generation, narrative and player agency | Never provide unsolicited solution hints or tell the player what to investigate next; present available records and let the player decide. |
| S43.R05 | AI generation, narrative and player agency | All generated claims that alter canon must be persisted as structured events or records. |
| S43.T01 | AI generation, narrative and player agency | No hidden truth leaks before the exact reveal trigger. |
| S43.T02 | AI generation, narrative and player agency | NPC knowledge never exceeds their plausible information. |
| S48.R01 | Security, permissions and information boundaries | Define user, player, officer, administrator and system roles; least privilege; secret handling; access checks and audit logs. |
| S48.R02 | Security, permissions and information boundaries | Protect hidden case truth and restricted personal information from player-facing leakage. |
| S48.R03 | Security, permissions and information boundaries | Keep credentials out of source control, narrative records and logs. |
| S48.T01 | Security, permissions and information boundaries | Unauthorised reads/writes are rejected and audited. |

## 21. Open fictional and technical configuration decisions

1. Principal taxonomy and supported authentication mechanisms/providers.
2. Session lifetime, idle expiry, step-up and account recovery rules.
3. Role/attribute/purpose policy model and conflict-resolution precedence.
4. Canonical permission catalogue and domain-specific access matrix.
5. Information classification names, hierarchy and handling rules.
6. Medical, personnel, victim/witness, intelligence and protected-source restrictions.
7. Temporary delegation, emergency access and separation-of-duties policy.
8. Audit retention, integrity mechanism and review responsibilities.
9. Secret-management provider, rotation and incident response procedures.
10. Encryption/key-management capabilities verified for each provider.
11. Security monitoring thresholds, escalation and operator responsibilities.
12. Data redaction standards and public-release approval boundaries.
13. Cache freshness, revocation propagation and outage behaviour.
14. Test environment isolation and synthetic identity strategy.
15. Backup/restore access model and key recovery.
16. Security incident classification and response workflow.
17. Formal security review and policy activation under BP-44.

## 22. Completion status

- Specification: DESIGNED_DRAFT; review/approval pending.
- Implementation: NOT_STARTED.
- Test execution: NOT_STARTED; listed acceptance criteria are not executed evidence.
- Verification: NOT_STARTED.
- Neon writes, migrations, credential changes, seed data, imports or production policy deployment: none performed or authorised.
- Next division: BP-43 — Testing and Quality Assurance.