# BP-41 — Notifications and Reporting

**Project:** Saltwater  
**Division:** BP-41 of the fixed 44-division structure  
**Specification:** DESIGNED_DRAFT — review/approval pending  
**Implementation / test execution / verification:** NOT_STARTED  
**Primary responsibility:** Authoritative notification and reporting workflows, rules, queues, generation and delivery state.  
**Write restriction:** No Neon write, migration, seed, import, bulk operation or production configuration change is authorised by this specification.

## 1. Purpose

BP-41 defines how Saltwater creates, governs, stores, distributes and reports operational information through notifications, alerts, reports, dashboards, digests, metrics and authorised public-accountability outputs. It establishes the authoritative lifecycle of each notification and report while preserving source ownership in the originating domain. BP-40 presents these outputs; BP-41 owns their semantics and generation/delivery state.

## 2. Binding principles

1. A notification is not its source event; a report is not the underlying source records.
2. Every output is attributable, permission-filtered, versioned and traceable.
3. Missing or inaccessible data is never represented as zero activity.
4. Preserve uncertainty, conflicting accounts, source wording and temporal distinctions.
5. No hidden offender truth, unsolicited investigative hints or omniscient NPC knowledge.
6. No report or notification itself creates an incident, case, investigation task, charge, finding or personnel action.
7. Delivery, acknowledgement and display are separate from completion of an underlying task or order.
8. Retries are bounded, idempotent and reconciled after uncertain outcomes.
9. Text is primary; all dashboards and reports have accessible text equivalents.
10. Simulation time and NPC activity freeze while the player is absent or the game is paused.

## 3. Scope and exclusions

**Included:** notification taxonomy and lifecycle; rules and recipient resolution; priorities and escalation; channels; queues, retries and acknowledgements; report catalogue/templates; generation and snapshots; dashboards and metrics; public accountability reporting; redaction, access, exports, retention, audit, observability and failure handling.

**Excluded:** source event/domain truth; case and complaint lifecycle; command policy; canonical time engine; user-interface rendering; security policy ownership; authoritative record schema and recovery; independent testing and configuration governance.

## 4. Core concepts and entities

- **Notification:** stable identity, source event, rule, recipient, priority, content/version, channel, timestamps and lifecycle.
- **Notification rule:** stable ID, owner, event selector, conditions, recipient resolver, channel, priority, suppression/escalation policy, version and activation state.
- **Delivery attempt:** notification, channel/provider, attempt number, request/acknowledgement, timestamps, result and failure reason.
- **Recipient interaction:** read, acknowledged, dismissed, archived or flagged state; does not rewrite source truth.
- **Report definition/template:** owner, purpose, query contract, fields, filters, aggregation, redaction, version and approval.
- **Report request/run:** requester or trigger, scope, parameters, source versions, template version, status, times and result reference.
- **Report snapshot:** immutable issued output or integrity reference, classification, recipients and supersession link.
- **Metric definition/observation:** formula, numerator, denominator, exclusions, unit, source, period, version and observation time.
- **Distribution/export:** recipient/destination, format, scope, actor, authorization, redactions, result and audit reference.
- **Queue/dead-letter item:** source reference, idempotency key, retry policy, attempts, last error, replay authority and state.
- **Audit/correction record:** actor/service, previous/new state, reason, source, timestamp and correction/supersession lineage.

## 5. Notification taxonomy and lifecycle

Distinguish informational message, advisory, warning, urgent/critical alert, task assignment, request, formal command notification, delivery receipt and escalation. A displayed message is not automatically a binding order. An acknowledgement does not prove compliance or task completion.

Lifecycle states include created, eligible, suppressed, queued, dispatching, delivered, partially delivered, delivery failed, delivery unknown, acknowledged, read, dismissed, archived, expired, withdrawn and superseded. Delivery state and recipient-interaction state are separate dimensions. Source events remain intact when a notification fails or expires.

## 6. Rules, recipients and priority

Rules have stable identity, owner, version, event filters, eligibility conditions, recipient resolver, channel, priority, suppression, escalation and enabled state. Event occurrence is distinct from notification eligibility and successful delivery. Resolve recipients from authoritative current roster/authority data and preserve event-time context where relevant. Re-evaluate access and eligibility before delivery.

Priority classes have explicit meanings, response expectations and escalation. Escalation is attributable and bounded; loops are prevented. Mandatory alerts cannot be muted where policy forbids it. Preferences and quiet periods affect only permitted classes. Changing a rule affects future events unless an explicit, audited replay is authorised.

## 7. Delivery channels, queues and idempotency

Channels are configurable; do not assume external connectivity. Each channel has a named owner, capability contract, acknowledgement semantics, retry policy and failure states. Do not claim external delivery without provider acknowledgement. An unavailable channel falls back only to an explicitly configured permitted channel.

Use stable idempotency keys scoped to source event, rule, recipient and channel. Persist queue state and delivery attempts. Retries are bounded. Reconcile unknown outcomes before retry. Dead-letter items retain provenance and cause. Replay requires authority and cannot duplicate an acknowledged delivery. Service restart cannot discard persisted queue state or falsely mark deliveries complete.

## 8. Reports, templates and snapshots

Reports cover operational activity, command, staffing, incidents, cases, crime, evidence, custody, legal process, courts, corrections, finance, resources, standards, complaints, civic context and system health, subject to explicit data-owner contracts.

Every report has stable identity, type, owner, scope, query/filters, period, source versions, template version, generation actor/service, timestamp, status and integrity reference. Distinguish live view, provisional result, partial output and immutable issued snapshot. Templates are versioned; changes do not rewrite prior issued reports. Regeneration preserves prior output and identifies supersession. A report never implies an unqueried source was checked.

## 9. Metrics, dashboards and public accountability

Every metric defines numerator, denominator where applicable, exclusions, period, unit, source and formula version. Distinguish count, rate, duration, proportion, estimate and qualitative assessment. Do not infer causation from correlation or present forecasts as actual observations. Small-number disclosure and repeated-query re-identification risks are controlled.

Public accountability outputs require explicit authority and recorded approval. Use approved aggregation and redaction; never unrestricted direct database extracts. Publish definitions, denominators, periods and limitations. Avoid misleading time-series comparisons when definitions or scope changed. Exclude external-city/territory activity from Saltwater statistics unless explicitly labelled external context.

## 10. Security, privacy and hidden truth

BP-42 owns authorization. BP-41 applies authorization before source retrieval, aggregation, report assembly, recipient resolution, preview, delivery, export and historical access. Redact before payloads enter caches or delivery queues. Recipient-specific redaction is independent. Counts, facets, errors and inaccessible placeholders must not leak protected record existence.

Hidden culprit/accomplice/perpetrator truth is excluded from every notification/report channel, including metadata, titles, previews, dashboards, exports, AI summaries and operator telemetry, until the exact `bingo` gate defined by governing canon is satisfied. NPC recipients receive only knowledge they plausibly observed, received or lawfully accessed. Technical operator status does not grant unrestricted domain access.

## 11. Domain ownership and integration

- BP-30 owns command policy, command authority and institutional governance; BP-31 owns complaint/professional-standards case lifecycle.
- BP-11/BP-12 own emergency communications and incident operations; BP-41 delivers authorised alert/report representations.
- BP-15 owns case identity/lifecycle; BP-16 investigative actions; BP-23 evidence custody; BP-24 forensic examination reports.
- BP-09 owns police resources; BP-34 owns finance/procurement truth.
- BP-35 owns simulation event execution; BP-37 canonical time/scheduling.
- BP-38 owns canonical records, schemas, queries and audit persistence; BP-39 recovery.
- BP-40 owns interface rendering/navigation/interactions; BP-41 owns notification/report semantics and generation/delivery.
- BP-42 authorization; BP-43 quality assurance; BP-44 configuration/change governance.

BP-41 cannot create a domain event or change the owning domain's state merely because it generated or delivered a report. Every message/report traces to a source event, query, rule or authorised manual request.

## 12. Time, pause and scheduling

Report generation and notification dispatch do not advance simulation time. Scheduled generation uses BP-37 recurrence and timezone. No schedule, escalation, notification queue or NPC delivery progression dependent on game time executes while the player is absent or the simulation is paused. Missed schedules do not silently cause catch-up simulation after resume. Any configured real-world transport retry is separate from in-game time and cannot trigger NPC/world activity. Late delivery is disclosed.

## 13. Errors, corrections and retention

Distinguish invalid recipient, permission denial, provider outage, malformed content, source unavailable, query failure, partial generation, delivery failure and unknown outcome. Missing source data is not zero. Preserve request and failure history. Corrections create new versions or supersession notices; never silently rewrite issued reports or source events. Route source-truth corrections to the owning domain. Retention and disposal are configurable and preserve audit/provenance and legal-hold requirements. Deleting a presentation copy never deletes the source event or authoritative record.

## 14. Inputs, outputs and dependencies

**Inputs:** domain events and records; approved report definitions/templates; notification rules; recipient/roster/authority state; permissions; canonical time; channel capabilities/acknowledgements; operator health observations; authorised manual requests.

**Outputs:** notification records; delivery attempts and queue state; recipient-specific payloads; report requests/runs/snapshots; metrics and dashboards; authorised exports; correction/supersession notices; audit and operational observations.

**Dependencies:** BP-01, BP-03–BP-16, BP-17–BP-24, BP-25–BP-40, BP-42–BP-44. BP-40 presents, BP-38/39 persist/recover, BP-42 authorizes.

## 15. Acceptance tests

The following criteria define required coverage. They are design criteria only; none is claimed executed.

- RPT-AT-001: Every report has a stable ID, report type, owner, scope, status, version and provenance.
- RPT-AT-002: Every notification has a stable ID, source event reference, recipient/target, channel, priority and lifecycle state.
- RPT-AT-003: Distinguish source event time, effective time, generated time, delivery time, read time and expiry time.
- RPT-AT-004: Distinguish notification, alert, report, dashboard, digest, bulletin, audit extract and operational metric.
- RPT-AT-005: Notification content is a presentation/delivery record, not a substitute for its source domain event.
- RPT-AT-006: Reports preserve their source query, filters, time range, data version and generation timestamp.
- RPT-AT-007: Report snapshots are distinguishable from live views.
- RPT-AT-008: Corrections and regenerated reports preserve prior versions and explain supersession.
- RPT-AT-009: Do not silently overwrite a previously issued report.
- RPT-AT-010: Every generated report identifies its producing service or authorised actor.
- RPT-AT-011: Every report identifies whether it is complete, partial, stale, provisional or final.
- RPT-AT-012: Partial reports identify missing sources, failed sections and limits.
- RPT-AT-013: Reports never imply that an unqueried source was checked.
- RPT-AT-014: Reports preserve uncertainty, conflicting accounts and disputed facts.
- RPT-AT-015: Reports distinguish allegation, intelligence, evidence, hypothesis, finding and adjudicated outcome.
- RPT-AT-016: Report summaries link to underlying source records.
- RPT-AT-017: Generated narrative is labelled and cannot replace original source wording.
- RPT-AT-018: Reports preserve source attribution and chain-of-custody references where applicable.
- RPT-AT-019: Reports preserve author, version, effective date and recorded date.
- RPT-AT-020: Reports can be regenerated reproducibly from a retained query definition and source version where supported.
- RPT-AT-021: Report scope is bounded and explicit; no unbounded city-wide extraction by default.
- RPT-AT-022: Report templates are versioned and have a named owner.
- RPT-AT-023: Template changes do not retroactively alter already issued report snapshots.
- RPT-AT-024: Report access is checked for every source record before content is assembled.
- RPT-AT-025: Redaction occurs before content is delivered, exported or cached.
- RPT-AT-026: Unauthorized source records are excluded without leaking their existence through counts or placeholders.
- RPT-AT-027: Sensitive reports support audience-specific redaction and controlled distribution.
- RPT-AT-028: Recipient eligibility and purpose are checked before dispatch.
- RPT-AT-029: Exported reports carry classification, handling and provenance metadata.
- RPT-AT-030: Clipboard, print, download and share functions enforce equivalent access controls.
- RPT-AT-031: Report formats preserve long text, tables, identifiers, timestamps and diacritics without silent truncation.
- RPT-AT-032: Every export records scope, format, recipient/destination and initiating actor where authorised.
- RPT-AT-033: Export failure does not leave a falsely successful delivery state.
- RPT-AT-034: Notification rules have stable IDs, owners, event filters, recipients, channels and enabled/disabled states.
- RPT-AT-035: Rules distinguish event occurrence from notification eligibility and delivery.
- RPT-AT-036: One source event cannot generate duplicate notifications through retry or repeated consumption.
- RPT-AT-037: Deduplication keys are stable and scoped to event, rule, recipient and channel as appropriate.
- RPT-AT-038: Multiple valid recipients receive separately attributable deliveries.
- RPT-AT-039: Recipient preferences cannot suppress mandatory safety-critical or command notifications where policy forbids suppression.
- RPT-AT-040: Priority levels have defined semantics and escalation rules.
- RPT-AT-041: Critical, urgent, routine and informational classes are distinguishable by text as well as visual treatment.
- RPT-AT-042: Escalation is attributable, bounded and does not create endless notification loops.
- RPT-AT-043: Delivery attempts, retries, failures and acknowledgements are recorded separately.
- RPT-AT-044: Delivery failure does not erase the underlying notification or source event.
- RPT-AT-045: Channels are configurable and may include in-interface, command desk, radio/dispatch integration, email-like fictional channels or digest, without assuming external connectivity.
- RPT-AT-046: An unavailable channel falls back only to an explicitly configured permitted channel.
- RPT-AT-047: Do not claim external delivery without confirmed provider acknowledgement.
- RPT-AT-048: Notification previews reveal only information authorised for that recipient.
- RPT-AT-049: Hidden offender truth is never included in notification body, title, metadata, counts, previews or delivery payload.
- RPT-AT-050: Notifications never provide unsolicited investigative hints or recommend what the player should investigate next.
- RPT-AT-051: NPC recipients receive only information they plausibly observed, were told or lawfully accessed.
- RPT-AT-052: Notifications to commanders reflect their actual authority and assignment at event time and current delivery eligibility.
- RPT-AT-053: Changes to recipient roles or permissions are re-evaluated before delivery.
- RPT-AT-054: Read, unread, acknowledged, dismissed and archived are distinct recipient-interaction states.
- RPT-AT-055: Opening a notification does not imply that its instruction was completed.
- RPT-AT-056: Acknowledgement is not proof of compliance or task completion.
- RPT-AT-057: Dismissal does not delete the source event or authoritative notification record.
- RPT-AT-058: Notification expiry does not delete audit history or source records.
- RPT-AT-059: Users can filter and group notifications without changing source priority or truth.
- RPT-AT-060: Notification digests preserve individual source references and original event times.
- RPT-AT-061: Quiet periods and preferences respect configured critical-alert exceptions.
- RPT-AT-062: Muted or suppressed notifications remain discoverable in authorised history where policy permits.
- RPT-AT-063: Reports can be produced for operational activity, command, staffing, incidents, cases, crime, evidence, custody, legal process, courts, corrections, finance, resources, standards, complaints and system health.
- RPT-AT-064: Each report domain has an explicit data owner and approved fields.
- RPT-AT-065: Police command reports distinguish operational demand, deployment, outcomes and performance measures.
- RPT-AT-066: Case reports distinguish case status from investigative progress and court outcome.
- RPT-AT-067: Crime reports distinguish recorded offences from allegations, intelligence and generated hidden truth.
- RPT-AT-068: Personnel reports respect sensitive HR, medical, disciplinary and security restrictions.
- RPT-AT-069: Evidence reports preserve exhibit identity, continuity and current custody state.
- RPT-AT-070: Financial reports distinguish budget, commitment, invoice, liability, payment and ledger posting.
- RPT-AT-071: Public accountability reports exclude protected personal data and hidden offender truth.
- RPT-AT-072: Public-facing statistics disclose definitions, period, denominator and known limitations.
- RPT-AT-073: Metrics do not reward unsafe quotas or encourage fabricated outcomes.
- RPT-AT-074: Metrics distinguish count, rate, duration, proportion, estimate and qualitative assessment.
- RPT-AT-075: Every metric has a definition, numerator, denominator where applicable, exclusions and source.
- RPT-AT-076: Metric calculations are versioned and reproducible.
- RPT-AT-077: Do not infer causation from correlation or present an estimate as a measured fact.
- RPT-AT-078: Small-number disclosure risks are assessed before public aggregation.
- RPT-AT-079: Reports support date/time filters using canonical BP-37 time and explicit timezone.
- RPT-AT-080: Time ranges specify inclusive/exclusive boundaries and treatment of incomplete periods.
- RPT-AT-081: Reports distinguish event time from record-entry time and later correction time.
- RPT-AT-082: Late-arriving records are identified and included/excluded according to declared report policy.
- RPT-AT-083: Historical reports retain the source version and policy applicable at generation.
- RPT-AT-084: Scheduled reports are defined but cannot execute while the simulation is paused or player absent.
- RPT-AT-085: Recurring report schedules use BP-37 recurrence and explicit timezone.
- RPT-AT-086: Missed schedules do not silently run catch-up simulations after resume.
- RPT-AT-087: Manual generation requires an explicit authorised user action.
- RPT-AT-088: Automated generation runs only from an explicitly authorised domain event or configured schedule.
- RPT-AT-089: Report generation does not advance simulation time or trigger NPC/world activity.
- RPT-AT-090: Notification dispatch is a delivery process and never itself advances simulation time.
- RPT-AT-091: Queued notifications freeze with the simulation when their delivery depends on game-time progression.
- RPT-AT-092: External real-world transport retries may occur only if explicitly configured and must not advance in-game time.
- RPT-AT-093: On resume, overdue notifications are not silently treated as timely; lateness is disclosed.
- RPT-AT-094: Report generation failure preserves the request, error and retry state without duplicating records.
- RPT-AT-095: Notification queue failure preserves source event and delivery-attempt history.
- RPT-AT-096: Retry policy is bounded, idempotent and observable.
- RPT-AT-097: Unknown delivery outcome is reconciled before retry.
- RPT-AT-098: Provider outage is distinguished from invalid recipient, denied permission and malformed content.
- RPT-AT-099: Queue backlog and age are visible to authorised operators.
- RPT-AT-100: Dead-letter items retain cause, provenance and controlled replay status.
- RPT-AT-101: Replay cannot duplicate a delivery already acknowledged.
- RPT-AT-102: Notification and report services expose actual health observations with source and timestamp.
- RPT-AT-103: Operational dashboards distinguish live, delayed, stale and unavailable measurements.
- RPT-AT-104: Service metrics include volume, latency, error rate, retry rate, backlog and delivery outcomes.
- RPT-AT-105: Database size/growth reports identify measurement time, units, scope and whether values are estimates.
- RPT-AT-106: Observability never exposes credentials, protected content or hidden world truth.
- RPT-AT-107: Operator actions, rule changes, template changes and replay actions are attributable and audited.
- RPT-AT-108: Reports and notifications have role-specific permissions for create, view, configure, approve, distribute and export.
- RPT-AT-109: Separation of duties is supported where configured.
- RPT-AT-110: Permission revocation prevents future delivery and access to protected historical content as policy dictates.
- RPT-AT-111: Search, filters, counts, previews and dashboards apply authorization before aggregation.
- RPT-AT-112: Audit logs for reports/notifications cannot be edited by ordinary recipients.
- RPT-AT-113: Retention and disposal rules are configurable and preserve required audit/provenance history.
- RPT-AT-114: Deletion of a presentation copy never deletes source event, case, evidence or authoritative record.
- RPT-AT-115: Corrections use versioning or supersession, never silent historical rewriting.
- RPT-AT-116: Recipients can flag incorrect or misleading notification/report content for correction review.
- RPT-AT-117: Correction workflow routes to the owning domain; BP-41 does not alter source truth.
- RPT-AT-118: Public releases require explicit authority and recorded approval.
- RPT-AT-119: Public reporting uses approved aggregation and redaction, never direct unrestricted database extracts.
- RPT-AT-120: Public-facing outputs never disclose protected case status or identity beyond authorised release.
- RPT-AT-121: Cross-city or external-territory statistics are excluded from Saltwater's single-city world unless explicitly labelled external context.
- RPT-AT-122: Every report and notification is text-readable without graphics or colour cues.
- RPT-AT-123: Dashboards provide equivalent tabular/text output and accessible descriptions.
- RPT-AT-124: Critical status is communicated by text, not colour alone.
- RPT-AT-125: Support keyboard and assistive-technology access to notification actions and report controls.
- RPT-AT-126: Long reports support complete pagination/download without silent omission.
- RPT-AT-127: Search results preserve report version, date and classification.
- RPT-AT-128: Interface presentation by BP-40 cannot bypass BP-41 content permissions or BP-42 security.
- RPT-AT-129: BP-41 owns report/notification semantics, rules, queues, generation and delivery state.
- RPT-AT-130: BP-40 owns presentation, navigation and user interaction, not notification truth or report generation.
- RPT-AT-131: BP-35 owns simulation event execution; BP-37 canonical time and scheduling.
- RPT-AT-132: BP-38 owns canonical records, schema, queries and audit persistence; BP-39 recovery.
- RPT-AT-133: BP-42 owns authorization; BP-43 testing; BP-44 configuration/change governance.
- RPT-AT-134: BP-30 owns command policy and authority; BP-31 complaint/standards case lifecycle.
- RPT-AT-135: BP-15 owns case identity/lifecycle; BP-16 investigation; BP-23 evidence custody; BP-24 forensic reports.
- RPT-AT-136: BP-11/BP-12 own emergency communication and incident operations; BP-41 presents authorised reports/alerts.
- RPT-AT-137: BP-09 owns police resource records; BP-34 finance and procurement truth.
- RPT-AT-138: BP-41 cannot create an incident, investigation task, case, charge, court finding or personnel action merely by issuing a report or notification.
- RPT-AT-139: Every message and report can be traced to its source event, query, rule or authorised manual request.
- RPT-AT-140: Every notification state transition records actor/service, timestamp, reason and previous state.
- RPT-AT-141: Every report generation records inputs, template version, source versions and output hash or equivalent integrity reference.
- RPT-AT-142: Every failure and correction retains original content or its immutable reference.
- RPT-AT-143: Recipient-specific redaction is applied independently, not by reusing a less restricted recipient's cached payload.
- RPT-AT-144: An alert cannot be elevated or suppressed by AI without an authorised rule and attributable action.
- RPT-AT-145: AI-generated summaries label inference and cite source records; no invented facts.
- RPT-AT-146: AI cannot reveal hidden culprit/accomplice identities before exact bingo.
- RPT-AT-147: AI cannot send unsolicited investigative hints or steer player decisions.
- RPT-AT-148: Notification content is neutral and concise; full evidence and reasoning remain in source records.
- RPT-AT-149: Do not expose internal queue identifiers, stack traces or secrets to ordinary recipients.
- RPT-AT-150: An alert with an unresolved source reference is quarantined or marked incomplete, not silently fabricated.
- RPT-AT-151: Reports clearly identify missing, delayed, conflicting or unavailable data.
- RPT-AT-152: Data corrections after report generation trigger a visible supersession or correction notice where configured.
- RPT-AT-153: Historical report snapshots remain reproducible or explicitly declare irreproducible source dependencies.
- RPT-AT-154: Retention expiry never occurs while a legal hold or configured preservation condition applies.
- RPT-AT-155: Bulk report/export requests are bounded, permission-checked and observable.
- RPT-AT-156: Bulk notification actions require explicit scope preview and confirmation.
- RPT-AT-157: Operator replay and redrive actions require authority and cannot bypass idempotency.
- RPT-AT-158: Service restart does not discard persisted queues or falsely mark deliveries complete.
- RPT-AT-159: Test and development notifications are visibly segregated from authoritative simulation output.
- RPT-AT-160: Test fixtures cannot reach real or player-facing delivery channels unless explicitly isolated and authorised.
- RPT-AT-161: An unavailable report source is represented as unavailable, never as zero activity.
- RPT-AT-162: Zero results are distinguished from failed query, inaccessible source and not-yet-generated report.
- RPT-AT-163: Report time-zone conversion preserves canonical instant and displays chosen local zone.
- RPT-AT-164: Public metrics cannot be reverse-engineered to expose a protected individual through repeated narrow queries.
- RPT-AT-165: Notification preferences are versioned and do not retroactively change delivery records.
- RPT-AT-166: Changing a rule affects only future eligible events unless an explicit audited replay is approved.
- RPT-AT-167: Rule precedence and conflict resolution are deterministic and inspectable by authorised operators.
- RPT-AT-168: Escalation recipients are resolved from current authoritative rosters and authority, not stale cached assumptions.
- RPT-AT-169: Command notifications distinguish advisory information from binding orders.
- RPT-AT-170: An order is not legally or operationally binding merely because it appears as a notification.
- RPT-AT-171: Recipients can distinguish information, request, task assignment, warning and formal command.
- RPT-AT-172: Task completion status is sourced from the owning workflow, never inferred from opening or acknowledging a message.
- RPT-AT-173: Every critical alert has an owner, expected response policy and escalation route.
- RPT-AT-174: Unowned critical alerts are surfaced as configuration defects to authorised operators.
- RPT-AT-175: Reports can be compared across periods only when definitions and scope are compatible.
- RPT-AT-176: Changes to report definitions disclose breaks in series and avoid misleading comparisons.
- RPT-AT-177: Forecasts, estimates and simulations are labelled separately from actual observations.
- RPT-AT-178: System health dashboards do not claim Neon/database availability without a current successful check.
- RPT-AT-179: Database growth and storage estimates include measurement timestamp, assumptions and uncertainty.
- RPT-AT-180: Operational reports support export only after authorization, redaction and explicit user action.
- RPT-AT-181: Source links in reports open only records the recipient is authorised to view.
- RPT-AT-182: Expired sessions cannot continue to receive protected payloads in a stale interface.
- RPT-AT-183: Notifications received while a user is offline are shown as delayed on next session if applicable.
- RPT-AT-184: Simulation-paused status is distinguished from service outage and user-session absence.
- RPT-AT-185: Report generation and delivery audit records are retained independently from notification display state.
- RPT-AT-186: All configured delivery channels have explicit ownership, supported capability and failure semantics.
- RPT-AT-187: Configuration changes are versioned, reviewed and reversible under BP-44.
- RPT-AT-188: All critical acceptance tests cover both allowed and denied access paths.
- RPT-AT-189: All test data is isolated from canonical people, cases, incidents and businesses.

## 16. Source traceability

The following source requirements are assigned to BP-41 by the authoritative 52→44 crosswalk. Wording is copied from the unchanged original source JSON.

| Source ID | Source division | Original requirement/test wording |
|---|---|---|
| S21.R02 | Culture, media, recreation and civic life | Generate schedules, attendance, public narratives and records that can affect incidents and investigations. |
| S26.R01 | Police command, policy and internal governance | Represent orders, policies, briefings, operational plans, supervision, approvals, audits, complaints, misconduct and review. |
| S30.R01 | Case management and investigative command | Create stable case IDs, ownership, classification, status, objectives, actions, decisions, reviews, deadlines, linked incidents and closure reasons. |
| S40.R01 | Complaints, oversight and public accountability | Represent public complaints, independent review, internal investigations, inspections, findings, remedies and published outcomes. |
| S45.R01 | Maps, diagrams and visual evidence | Provide optional maps, layouts, timelines, charts and forensic scene visuals when useful or requested. |
| S51.R01 | Operations, observability and maintenance | Track service health, errors, latency, job queues, resource use, database size, failed events and recovery actions. |

### Exact source requirement traceability and ownership boundary

The following are the exact source requirements assigned to BP-41 by the authoritative crosswalk. The source wording remains unchanged in `docs/governance/SALTWATER_MASTER_BLUEPRINT.json`.

| Source ID | BP-41 responsibility | Authoritative source owner / boundary |
|---|---|---|
| S16.R03 | Generate and distribute authorised service notices for infrastructure maintenance, incidents, outages and restoration; identify affected scope, source, effective period, uncertainty and update/supersession state. | BP-04 owns infrastructure/operator facts; BP-35 owns outage/restoration event execution and effects; BP-41 owns notice eligibility, content version, recipients and delivery state. |
| S21.R02 | Distribute authorised schedules, public communications, event notices and report representations; preserve organiser/source attribution, event time/place, attendance-data limitations and distinctions between original public statements and generated summaries. | BP-04 owns organisations/venues; BP-14/BP-17/BP-21 own their respective incident, participant and intelligence records; BP-35 executes causal events; BP-36 owns social context; BP-37 owns canonical schedules. BP-41 does not create event attendance or public narrative truth. |
| S26.R01 | Deliver and retain authorised notifications representing policies, briefings, operational plans, supervision, approvals, audits, complaints, misconduct and review activity. Distinguish advisory information, requests, tasks and formal command notifications. | BP-30 owns policy, command authority, approvals and institutional governance; BP-31 owns complaint/standards case lifecycle; BP-05/BP-08/BP-12 own their organisational, assignment and operational interfaces. BP-41 cannot issue, vary or validate an order. |
| S30.R01 | Produce permission-filtered case status, ownership, classification, objectives, actions, decisions, reviews, deadlines, linked-incident and closure reports with source links and snapshot provenance. | BP-15 owns case identity/lifecycle; BP-16 owns investigative actions/decisions; BP-30 owns command governance; BP-38 owns canonical persistence. BP-41 is a read/reporting consumer and cannot mutate case state. |
| S40.R01 | Generate authorised public-accountability reports and publication-ready representations of complaints, independent review, internal investigations, inspections, findings, remedies and published outcomes. | BP-30 owns institutional oversight; BP-31 owns complaint/misconduct lifecycle and findings. BP-41 owns report generation, approved redaction, distribution and publication records only. |
| S40.R03 | Present authorised, source-attributed reporting of institutional events and public-trust indicators without inventing causal effects or converting generated narratives into established facts. | BP-14/BP-30/BP-31/BP-35/BP-36 own occurrence, governance, complaint, event-causality and social-context facts. BP-41 reports those facts under approved definitions; it does not generate or alter them. |
| S45.R01 | Generate traceable report-ready timelines, charts, map annotations and other optional visual-data outputs when requested or authorised; retain text equivalents and source references. | BP-02/BP-12/BP-15/BP-16/BP-20/BP-22/BP-23/BP-24/BP-35 own spatial, incident, case, investigation, surveillance, scene, evidence, forensic and event facts. BP-40 owns presentation/rendering; BP-41 owns report semantics, scope and generated-output provenance. |
| S51.R01 | Expose attributable, time-stamped notification/report service observations, including queue/backlog, latency, errors, retry/delivery outcomes and measured database/storage-report values where supplied by an authorised measurement source. | BP-09/BP-35/BP-38/BP-39/BP-43 own source resources, event processing, persistence, recovery and quality evidence. BP-41 owns report/alert representation and delivery state; it must not claim live health or database availability without a current successful observation. |

**Source-test boundary:** The crosswalk does not map S16.T01, S21.T01, S26.T01, S30.T01, S40.T01, S45.T01 or S51.T01 directly to BP-41. Those tests remain with their mapped domain owners. BP-41's RPT-AT criteria add reporting/delivery-specific coverage but do not replace or claim execution of source tests.

## 17. Open fictional and technical configuration decisions

1. Notification taxonomy, priority levels, mandatory-alert policy and escalation thresholds.
2. Authoritative recipient resolution and event-time versus delivery-time role rules.
3. Supported delivery channels and provider acknowledgement contracts.
4. Retry limits, backoff, dead-letter review and replay authorization.
5. Report catalogue, templates, ownership and approval requirements.
6. Public-accountability publication authority and aggregation thresholds.
7. Metric definitions, denominators and performance safeguards.
8. Report snapshot format, integrity mechanism and reproducibility horizon.
9. Retention, archival, legal-hold and disposal policy.
10. Scheduled-report behaviour and game-time scheduling configuration.
11. AI summary provider, constraints and source citation presentation.
12. Operator dashboard metrics, thresholds and observation intervals.
13. Recipient preferences, quiet periods and critical-alert exceptions.
14. Export formats, classification labels and destination allowlist.
15. Correction/withdrawal workflow and recipient notification policy.
16. Queue implementation and verified persistence/recovery integration.

## 18. Completion status

- Specification: DESIGNED_DRAFT; review/approval pending.
- Implementation: NOT_STARTED.
- Test execution: NOT_STARTED; listed acceptance criteria are not executed evidence.
- Verification: NOT_STARTED.
- Neon writes, migrations, seeds, imports and production configuration changes: none performed or authorised.
- Next division: BP-42 — Security and Permissions.