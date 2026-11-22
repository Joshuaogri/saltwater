# BP-22 — Crime Scenes

**Project:** Saltwater — fictional sovereign city-state, one city, one jurisdiction  
**Blueprint division:** BP-22 of the fixed 44-division structure  
**Specification:** DESIGNED_DRAFT | **Implementation:** NOT_STARTED | **Test execution:** NOT_STARTED | **Verification:** NOT_STARTED  
**Authority:** Derived from the unchanged 52-division source and fixed BP-01–BP-44 structure. No canon or division structure is changed.

## 1. Purpose

BP-22 defines the operational and evidential management of crime scenes and other police-controlled examination locations in Saltwater. It covers scene identification, initial assessment, control, boundaries, safety, access, entry logs, scene preservation, search planning and execution, documentation, photography/diagram references, environmental conditions, scene handover, release and post-release review. It coordinates with BP-23 for exhibits and continuity, BP-24 for specialist examinations, BP-20 for surveillance source material, BP-12 for incident command and BP-16 for investigative decisions.

A scene is a physical, digital or mixed location/area where an incident may have occurred, evidence may be present, or a controlled examination is justified. A scene may be a room, building, vehicle, outdoor area, route segment, water-adjacent area, business premises, public space, digital environment or connected set of locations. Scene designation is a police operational record, not proof that a crime occurred.

BP-22 owns scene records and scene-control activity. It does not own the canonical geography, property register, incident lifecycle, investigative strategy, surveillance capture, exhibit custody after formal transfer, forensic method/results, victim/suspect identities, or court findings.

## 2. Scope and explicit exclusions

In scope: scene creation and identifiers; scene classification; scene boundaries and zones; initial response and preservation; risk and safety assessment; authority and command references; access control and scene log; personnel and visitor roles; entry/exit records; contamination prevention; search planning; search areas and methods; scene photography and notes; measurements and sketches; environmental and lighting context; scene condition; observations and interpretation separation; item discovery and recovery requests; exhibit handover; specialist attendance; scene-to-scene relationships; scene continuity; release and reopening; records, audit and permissions.

Out of scope: canonical map geometry (BP-02); ownership, tenancy, occupancy and building access rights (BP-04); police staffing/deployment and resources (BP-05–BP-10); call/dispatch/incident lifecycle (BP-11/BP-12); offence taxonomy (BP-13); case lifecycle (BP-15); investigative plan and decisions (BP-16); victim/witness roles (BP-17); suspect/offender roles (BP-18); interviews (BP-19); surveillance source collection (BP-20); intelligence analysis (BP-21); exhibit custody/continuity after transfer (BP-23); forensic examination (BP-24); arrest/custody/legal/court outcomes (BP-25–BP-29); global simulation clock (BP-37); records/persistence/security/QA/change control (BP-38–BP-44).

## 3. Core scene model

A Scene record has stable scene_id; scene type; title/description; linked incident/case references; canonical location references; scene scope; scene status; priority; originating report; creating actor; command owner; responsible scene supervisor; authority basis; creation and effective times; known/unknown event interval; safety state; access state; boundary version; search status; preservation status; environment snapshot references; linked scenes; source records; exhibits recovered/referred; restrictions; review/release state; provenance and audit references.

A scene may exist before a case is opened, may be linked to multiple incidents/cases, and may be reopened after release. Case linkage never changes scene identity. A scene is not automatically created for every incident. A scene may be designated as potential, confirmed, precautionary, secondary, associated, vehicle, outdoor, digital or other configured type. Scene type is descriptive and does not establish an offence.

Separate Scene, Scene Zone, Boundary Version, Scene Access Event, Scene Personnel Assignment, Scene Safety Assessment, Search Plan, Search Area, Search Activity, Scene Observation, Scene Record/Media Reference, Scene Condition Assessment, Scene Handover, Scene Release, Scene Reopening, Recovery/Handover Request and Audit Event entities. Exhibit entities and custody remain BP-23 owned.

## 4. Canonical location and scene geometry

Every scene location must resolve to BP-02 canonical spatial references where possible: district/zone, parcel/address, coordinates, route segment, building/facility, floor, room, entrance/access point or outdoor feature. BP-22 may record scene-specific geometry such as boundary polygons, search grids, zones, measurements and annotated layouts, but must not redefine canonical street/building geometry or create conflicting address records.

A scene may span multiple parcels, buildings, floors, vehicles, public spaces or route segments. Represent components as linked scene zones or linked scene records with explicit relationships. A scene may also be mobile or transient; record the movement path/interval and uncertainty rather than inventing a fixed location. If exact location is unknown, preserve the best available description and unresolved status.

Geometry includes coordinate reference system, units, precision, source, capture method, author, time and uncertainty. Never imply survey-grade precision from an approximate sketch. Textual location description remains mandatory where geometry is unavailable. Maps are optional and must derive from canonical records.

## 5. Scene boundaries, zones and access points

A scene has one or more versioned boundaries. Each boundary version records author, time, authority, rationale, geometry/description, included/excluded areas, access points, hazards, adjoining areas and predecessor/successor. Boundaries may expand, contract, split or merge as facts change; prior versions remain preserved.

Zones may include inner/restricted, outer/perimeter, controlled access, sterile, public interface, staging, forensic work, hazardous, vehicle, temporary holding and other configured types. Labels are configurable. A zone has location, purpose, entry conditions, access route, controller, status and linked boundary version. A zone does not create a separate property or legal parcel.

Entrances, exits and alternative access paths are recorded, including windows, service routes, roof access, breaches and unknown routes. A scene log must not assume all access is through the main entrance. If boundary control is incomplete, explicitly record the gap and its time interval.

## 6. Scene creation and lifecycle

Scene states: proposed, designated, assessed, secured, controlled, under_examination, suspended, handed_over, released, reopened, closed, cancelled and archived. State transitions require actor, authority, time, reason, prior state and resulting state. Not every scene uses every state. Cancellation does not delete the record; it records why the location was not retained as a scene.

A scene may be created from an incident, patrol response, investigative decision, forensic referral, medical notification, public report or other plausible source. Creation records the source and uncertainty. A scene can be created before a crime classification or case exists. Multiple scenes can relate to one occurrence; one location can have multiple distinct scene episodes at different times.

Scene closure/release is not case closure. Case closure does not automatically release a scene. Scene release does not imply all exhibits have been examined or all investigative work is complete.

## 7. Initial response and preservation

The first responding officer records arrival time, identity, role, location, observed condition, people present, immediate risks, obvious access/egress, actions taken, disturbances, emergency interventions and notifications. Preserve what was observed before intervention as far as possible, but do not delay life-saving or hazard-control actions.

Initial actions may include protecting life, requesting medical/fire/utility support, preventing further harm, establishing an initial perimeter, controlling access, separating persons where justified, recording transient conditions, protecting fragile material from weather or disturbance, and notifying the appropriate supervisor/scene personnel. Record action, actor, reason, time, affected area and unavoidable disturbance.

Do not require a scene to remain untouched when emergency response, rescue, fire suppression, environmental control or public safety reasonably requires intervention. Such intervention must be documented with source and timing. A first responder's account is not a forensic conclusion.

## 8. Command, authority and responsibilities

Scene command is an operational assignment distinct from rank, position, grade, clearance or case ownership. Record the person who has scene control, the scope and effective period of authority, the assigning authority, handover and any limitations. The scene manager coordinates scene activity but does not gain ownership of all records created by attending specialists.

BP-12 retains incident command and operational incident record. BP-30 owns departmental governance and command policy. BP-16 owns investigative strategy. BP-22 owns scene-control decisions and scene log. BP-23 owns exhibit custody after accepted transfer. BP-24 owns forensic examination. Conflicts are resolved by explicit authority and recorded handover, not implicit hierarchy or rank assumptions.

If no qualified scene manager is available, record the interim controller and limitations. Specialist personnel may advise within their expertise without automatically assuming scene command.

## 9. Safety, hazards and environmental conditions

Before entry and during examination, assess known/possible hazards proportionately: structural instability, fire, electrical systems, gas, chemicals, biological hazards, sharps, weapons, traffic, water, weather, animals, confined spaces, contamination and other scene-specific risks. Record hazard, location/zone, severity/uncertainty, source, assessor, time, controls, required expertise, residual risk and reassessment triggers.

BP-19 environmental source provides weather/daylight/tide/hazard context as applicable; BP-35 owns causal environmental simulation. BP-22 records the conditions relevant to this scene and their source/time. Do not invent environmental conditions or infer them from generic seasonal averages.

Entry may be restricted, delayed, segmented or suspended where risk requires. Emergency intervention may override normal sequencing, with reasons and actions recorded. A hazard assessment is not a guarantee of safety.

## 10. Scene access control and entry log

Every known entry/exit into a controlled scene zone is recorded with person/actor ID or explicit unknown, role, organisation/unit, purpose, authority/escort, entry and exit time, zone, PPE/precautions where relevant, items/equipment carried in/out where material, actions, contamination risk and recorder. The system supports partial/incomplete logs and unknown access; it must never fabricate a complete log.

Roles include first responder, scene manager, investigator, forensic examiner, photographer, medical/emergency responder, property representative, specialist, witness, authorised visitor, support staff and unknown/unidentified person. Role is scoped to this scene and does not overwrite the person's canonical employment, rank or case role.

An entry record may be corrected additively. Backdated or reconstructed entries must be explicitly marked as reconstructed, with author, basis and uncertainty. If an access event is discovered later, append it and assess its potential effect on scene integrity.

## 11. Scene integrity and contamination control

Record baseline scene condition, known disturbances, prior access, weather exposure, emergency intervention, shared surfaces, cross-contamination risks, PPE changes, equipment entry/exit, packaging and segregation precautions, and any suspected contamination event. Controls may include controlled routes, clean/dirty zones, equipment checks, gloves/PPE changes, separate packaging and restricted movement. Exact technical protocols belong to BP-24 and specialist policy.

A contamination concern is a recorded risk or event, not an automatic finding that all material is invalid. Identify affected zones/items, people, possible transfer direction, timing, known controls, uncertainty and reviewer. Preserve both the concern and any subsequent assessment. Do not silently erase, relabel or invalidate an exhibit; BP-23/BP-24 decide exhibit/examination implications.

## 12. Search planning and search areas

A Search Plan is a scene-owned plan version with purpose, scope, authority, scene/boundary version, responsible supervisor, participants, method, sequence, priorities, resources, safety controls, contamination controls, recording requirements, exclusions, start/stop criteria and review. A plan may be amended as conditions change; preserve prior versions and rationale.

Search Areas have stable IDs, geometry/description, scene zone, search method, assigned person/team, start/end times, status, coverage, limitations, items found/referred, observations, unresolved gaps and supervisor review. Areas can be searched, partially searched, inaccessible, deferred, contaminated, disturbed, not searched or requiring repeat search. Never label an area fully searched if access or coverage was incomplete.

Methods may include systematic grid/strip/zone search, spiral, point-to-point, vehicle/building search, digital-location coordination and specialist methods. Method selection is recorded with rationale; no method is universally required. Search plans do not tell the player what to investigate next; they document authorised scene work the player chooses or performs.

## 13. Search execution and recording

Each Search Activity records actor/team, area and plan version, method, time interval, equipment/resources, conditions, route/coverage, observations, limitations, deviations, interruptions, safety events, contamination events, items located and supervisor review. A search record distinguishes planned coverage from actual coverage.

If an item or trace is noticed, record its original position and condition before recovery where feasible, along with observer, time, method, scale/reference, orientation and environmental context. If emergency action or scene constraints prevent full documentation, record what was omitted and why. Do not retrospectively invent measurements, photographs or observations.

A negative search result is bounded by the method, area, time, conditions, observer and limitations. It does not prove that an item was never present or that no event occurred.

## 14. Scene observations versus interpretation

A Scene Observation records what a named observer directly saw, heard, smelled, measured or otherwise perceived, with time, position, conditions, method, instrument where relevant, contemporaneous notes and uncertainty. Separate direct observation from interpretation, inference, hypothesis, hearsay and later recollection.

Examples: “a dark liquid-like mark on the floor” is an observation; “blood” requires appropriate identification; “the person entered through this door” requires a source and basis; “the offender used this route” is an inference unless independently established. The interface must preserve original wording and distinguish corrected transcription from changed interpretation.

Multiple observers may disagree. Preserve separate accounts and reconcile only through an attributed review. No automatic AI summarisation may overwrite original observation records.

## 15. Photography, video, diagrams and measurements

Scene media and diagrams include overview, mid-range, close-up, orientation, scale, measurement, sketch, plan, elevation, panoramic or other configured representations. Record creator, device/method, original media reference, capture time/time basis, location/position, direction, scale, units, lighting/conditions, file integrity metadata, editing/derivative history and linked scene zone/observation/item.

BP-22 owns scene documentation metadata and scene-specific diagrams. BP-20 owns surveillance originals and capture/retrieval records. BP-23 owns exhibit images/records after exhibit transfer where applicable. BP-40 renders optional maps and visual layouts; source records remain authoritative. Preserve originals; derivatives are separately identified and linked.

A diagram must state whether it is measured, approximate, illustrative or reconstructed. Geometry and measurements must not claim greater precision than the method supports. Text records must remain usable without images. If a requested visual cannot be rendered, the scene record remains complete.

## 16. Environmental and temporal scene context

Record scene conditions at relevant times: weather, precipitation, wind, temperature if actually measured or sourced, daylight/artificial lighting, visibility, water/tide where relevant, surface condition, noise, smoke, power state and other material conditions. Each value has source, location, time basis, measurement/estimate status and uncertainty.

Distinguish occurrence time, discovery time, first response, scene designation, access, observation, search, recovery, handover and release. Clock offsets, device drift, estimated intervals and unknown times are explicit. BP-37 owns canonical simulation time; BP-20 owns surveillance time basis; BP-22 records scene-local timing and discrepancies.

Environmental effects on fragile traces are described only where supported. No generic assumption that rain destroys all traces or that a trace survives indefinitely. BP-24 owns specialist interpretation of persistence and degradation.

## 17. People present and participant references

All people use BP-03 canonical identities where known. Unidentified persons remain unresolved until properly identified. Scene presence is a scene-specific role and time interval; it does not establish witness, suspect, victim, offender or employee status. BP-17 owns victim/witness roles; BP-18 owns suspect/offender roles; BP-19 owns interview sessions; BP-06 owns personnel identity/service details.

Record why a person's presence is known, source of identification, observed or reported presence, time interval, location/zone and uncertainty. Do not infer presence solely from a person's address, employment, relationship or access entitlement. A person materially connected to police activity is subject to permanent BP-03 full-record promotion, never downgraded, within the hard 10,000 living-person cap.

## 18. Recovery interface and exhibit handover

When an item is located, BP-22 records discovery context and creates a recovery/handover request or linked BP-23 exhibit registration. BP-22 does not own exhibit identity, packaging/seal state, custody location or continuity after BP-23 accepts the item. Before handover, record finder, exact location, condition, time, method, initial documentation, packaging request, hazards, contamination concerns and temporary control.

BP-23 accepts or rejects the handover with actor, time, exhibit ID, packaging/seal details, transfer condition, current location/status, continuity event and any limitation. The scene record retains a reference to the exhibit and the handover transaction. Rejected or incomplete transfer remains visible and requires resolution; no silent assumption of acceptance.

Digital/documentary items, biological/trace material, weapons, vehicles, clothing, impressions and other categories use BP-23/BP-24 handling rules. Scene recovery context is not a forensic conclusion.

## 19. Specialist attendance and cross-system coordination

Specialists may include forensic examiners, photographers, surveyors, medical personnel, fire investigators, digital specialists, utility/environmental specialists, dog handlers and other configured roles. Record request, authority, expertise, scope, attendance, findings/observations supplied, limitations and handover. Specialist attendance does not grant unrestricted access or scene command.

BP-24 owns specialist examination methods/results and expert interpretations. BP-13 owns offence classification; BP-14 hidden occurrence truth is inaccessible. BP-16 owns investigative tasks/decisions. BP-20 owns surveillance source collection. BP-21 may receive scene-derived intelligence references but does not own the scene record. BP-12 retains incident management. Cross-system updates are references and events with provenance, not duplicated authoritative records.

## 20. Multiple, linked, mobile and changing scenes

One incident may have multiple scenes; one scene may relate to several incidents/cases; a location may become a scene at a later time; a vehicle or mobile location may move; a scene may be split into zones or linked sub-scenes. Relationships are typed (same occurrence, related location, transfer route, secondary scene, linked but unconfirmed, shared premises, follow-up examination) and attributed.

Do not merge scenes solely because they share an address, person, business or case. Do not split a scene in a way that loses original boundary/access history. Mobile scene records preserve movement, route, interval and uncertainty with BP-02/BP-17 references. A changed boundary creates a new version, not an overwrite.

## 21. Scene handover, release and reopening

Handover records outgoing/incoming controller, authority, date/time, current scene condition, boundary version, safety/hazard state, access log status, search progress, unresolved areas, exhibits/recovery status, contamination concerns, restrictions, outstanding actions and acknowledgement. Handover can be partial by zone.

Release records authority, decision-maker, time, reason, recipient/landholder where appropriate, condition of premises, access restoration, items/equipment removed, remaining restrictions, outstanding records and any retained police control. Release does not determine ownership, tenancy, liability or legal rights; BP-04 retains property/access records.

Reopening creates a new scene activity episode or status transition with reason, authority, new boundary/access state and preservation review. Prior release and post-release access remain visible. Reopening does not reset the original scene history.

## 22. Evidence continuity, legal and disclosure interfaces

BP-22 preserves the context in which potential material was observed or recovered and the identity of persons who accessed the scene. BP-23 owns exhibit custody and continuity; BP-24 owns examination; BP-27 owns legal process/disclosure; BP-28 owns court findings. BP-22 cannot declare admissibility, guilt, offence proof or evidential weight.

Scene access logs, notes, photographs, sketches, measurements, search plans, observations and handover records may be relevant to disclosure or review. Preserve originals, corrections, provenance, limitations and access history. If a record is challenged, append the challenge and response; do not erase the original. Disclosure status and legal restrictions are supplied by BP-27 and BP-42.

## 23. Permissions, confidentiality and audit

BP-42 owns global security. BP-22 requires separate permissions for scene index, restricted scene details, scene location, boundary geometry, access logs, sensitive images, hazard details, search plans, observations, recovery context, release, reopening, correction, export and audit. A scene manager's operational access does not automatically grant all source-person or medical information. Sensitive information is minimised and role/purpose restricted.

Every creation, view of restricted content, boundary change, access-log correction, search-plan approval, observation amendment, recovery/handover, scene release/reopening, export, denial and administrative action is auditable with actor, authority, purpose, target/version, time, outcome and reason. Search previews, maps, notifications, counts and exports enforce the same restrictions.

## 24. Time, pause, population and persistence

BP-37 owns the sole simulation clock. When the player is outside the simulation, scene activity, officer movement, access events, search progression, specialist attendance, environmental progression, handover deadlines, release scheduling and all NPC decisions freeze. On return, restore exact state; do not invent off-screen access, evidence recovery, scene degradation or completed searches.

Every living person counts once under the 10,000 hard cap. Scene personnel and members of the public are canonical persons, not duplicate scene-local people. Materially relevant people are promoted permanently under BP-03. BP-38 owns record/schema governance; BP-39 persistence/recovery. Scene state, boundary versions, access events, search records, original observations, media references, recovery handovers and audit are durable and recoverable.

## 25. Interface and reporting

Text-only functions must support scene creation, scene list/search, location and boundary descriptions, current controller, access log, hazard assessment, scene status, search plan/areas, activity log, observations, media references, exhibit handover status, scene links, handover/release/reopening and audit. No map or image is required to operate the scene system.

Optional outputs: scene overview map, boundary/zone layout, entry/exit timeline, search coverage diagram, measured sketch, photographic index, contamination timeline, exhibit-location reference, scene handover report and release report. Visuals derive from canonical spatial and scene records, identify version/time and uncertainty, and never contradict text. Each diagram can be traced to underlying records.

## 26. Inputs, outputs and event contracts

Inputs: BP-02 canonical geography; BP-04 property/building/occupancy/access records; BP-09 resources/equipment; BP-10 patrol and first-response records; BP-11/BP-12 call and incident references; BP-13 offence taxonomy; BP-15 case references; BP-16 investigative decisions; BP-17/BP-18 participant roles; BP-19 interview references; BP-20 surveillance references; BP-21 intelligence references; BP-23 exhibit registration/continuity; BP-24 specialist examination; BP-30 authority/policy; BP-35 causal world events; BP-37 time; BP-38/BP-39 records/persistence; BP-40 visuals; BP-42 access control.

Outputs: scene records and state transitions; boundary/zone versions; safety assessments; access logs; search plans and activities; scene observations; media/diagram references; contamination events; recovery/handover requests; specialist attendance records; scene handovers; releases/reopenings; audit and reporting events.

Minimum events: scene_created/designated/assessed/secured/controlled/suspended/handed_over/released/reopened/closed/cancelled; boundary_created/revised; zone_created/changed; hazard_assessed/changed; access_recorded/corrected; search_plan_created/revised/approved; search_started/paused/completed; search_area_updated; observation_recorded/corrected/challenged; media_registered/derivative_created; contamination_suspected/assessed; recovery_requested/accepted/rejected; specialist_requested/attended/completed; handover_started/completed; release_approved/completed; audit_access_granted/denied.

Each event carries stable event ID, scene ID/version, actor, authority, purpose, event/record/effective time, prior/resulting state, provenance, idempotency key and schema/configuration version.

## 27. Failure handling and edge cases

Unknown location remains unresolved; boundary cannot be confidently drawn; scene spans multiple premises; scene includes public and private areas; mobile scene changes location; weather changes during examination; lighting/power fails; emergency responders disturb material; an unauthorised person enters; entry log is incomplete; access is discovered retrospectively; a person refuses or cannot identify themselves; a scene manager becomes unavailable; specialist arrives before scene is secured; a search is interrupted; a zone is inaccessible; search method changes; a negative search is later challenged; a photograph lacks scale; device clock is wrong; original media is corrupted; diagram is approximate; measurement units differ; multiple observers disagree; contamination is suspected; contamination source is unknown; an item is discovered but not recovered; BP-23 rejects handover; packaging/seal is damaged; scene is released with unresolved records; property owner requires access; a released scene is re-entered; a new case links to an old scene; one scene is split; linked scenes are merged incorrectly; evidence is moved by emergency services; scene location is later corrected; sensitive image access is denied; map rendering fails; storage restoration lacks a referenced media file; idempotent retry occurs; player pauses mid-search. In every case preserve original records, uncertainty, actor/time/provenance and unresolved status; never invent missing events or silently rewrite history.

## 28. Dependencies and ownership contracts

BP-02 supplies canonical geometry; BP-04 supplies property/building topology, access points and time-valid occupancy; BP-09 supplies resources; BP-10 supplies field response; BP-11/BP-12 supply call/incident records and operational command; BP-13 supplies offence taxonomy; BP-15 supplies case references; BP-16 supplies investigative decisions; BP-17/BP-18 supply participant role references; BP-19 supplies interview source references; BP-20 supplies surveillance sources; BP-21 supplies intelligence references; BP-23 accepts exhibit custody; BP-24 conducts examinations; BP-30 governs authority; BP-35 supplies causal world events; BP-37 supplies time; BP-38/BP-39 govern records and persistence; BP-40 renders optional visuals; BP-42 controls permissions; BP-43 tests; BP-44 controls changes.

A failed dependency leaves an explicit pending/unresolved reference. BP-22 must not create substitute authoritative records or assume success. No dependency failure permits hidden truth disclosure, population cap violation, off-screen time progression or loss of source provenance.

## 29. Acceptance tests

These are design criteria, not executed results. BP-43 must execute them with reproducible evidence.

- **SCENE-AT-001** — Every scene has a stable unique scene ID.
- **SCENE-AT-002** — Scene creation records its originating report, event or decision.
- **SCENE-AT-003** — Scene designation does not assert that a crime occurred.
- **SCENE-AT-004** — A scene may exist before a case is opened.
- **SCENE-AT-005** — One incident may reference multiple scenes.
- **SCENE-AT-006** — One scene may be linked to multiple cases without merging case identities.
- **SCENE-AT-007** — Scene status transitions record actor, authority, time and reason.
- **SCENE-AT-008** — Cancellation preserves the scene record and reason.
- **SCENE-AT-009** — Scene release is distinct from case closure.
- **SCENE-AT-010** — Scene reopening preserves prior release history.
- **SCENE-AT-011** — Every known scene location resolves to BP-02 canonical geography or explicit unresolved status.
- **SCENE-AT-012** — Scene geometry records coordinate system, units, precision and source.
- **SCENE-AT-013** — Approximate sketches are not presented as measured plans.
- **SCENE-AT-014** — Scene-specific geometry does not overwrite canonical building or road geometry.
- **SCENE-AT-015** — A scene spanning multiple premises represents each component.
- **SCENE-AT-016** — A mobile scene preserves movement intervals and location uncertainty.
- **SCENE-AT-017** — Unknown location is not fabricated.
- **SCENE-AT-018** — Every boundary has a version and author.
- **SCENE-AT-019** — Boundary changes preserve prior geometry and rationale.
- **SCENE-AT-020** — Boundary includes/excludes are explicit.
- **SCENE-AT-021** — Every zone references a boundary version.
- **SCENE-AT-022** — Alternative access routes can be recorded.
- **SCENE-AT-023** — An incomplete perimeter is explicitly identified.
- **SCENE-AT-024** — Initial response records arrival, actor and observed condition.
- **SCENE-AT-025** — Life-saving intervention is not blocked by scene preservation rules.
- **SCENE-AT-026** — Emergency disturbance records actor, time, action and reason.
- **SCENE-AT-027** — First responder observation is distinct from forensic conclusion.
- **SCENE-AT-028** — Scene command is a scoped assignment, not inferred from rank alone.
- **SCENE-AT-029** — Interim scene control records authority and limitations.
- **SCENE-AT-030** — Scene manager does not assume ownership of all specialist records.
- **SCENE-AT-031** — Known hazards have source, location, assessor and time.
- **SCENE-AT-032** — Safety controls and residual risks are recorded.
- **SCENE-AT-033** — Scene suspension records reason and affected zones.
- **SCENE-AT-034** — Environmental values identify measured, estimated or sourced status.
- **SCENE-AT-035** — Every known scene entry/exit records person or explicit unknown.
- **SCENE-AT-036** — Access log includes role, purpose, authority and zone.
- **SCENE-AT-037** — Scene-specific role does not overwrite canonical employment or case role.
- **SCENE-AT-038** — Reconstructed access events are labelled and attributed.
- **SCENE-AT-039** — Unknown access remains an explicit integrity limitation.
- **SCENE-AT-040** — Scene condition and prior disturbance are recorded.
- **SCENE-AT-041** — Contamination concern identifies affected area/items and uncertainty.
- **SCENE-AT-042** — Contamination concern does not automatically invalidate exhibits.
- **SCENE-AT-043** — Search plan records purpose, authority, scope and boundary version.
- **SCENE-AT-044** — Search plan revisions preserve prior versions.
- **SCENE-AT-045** — Every search area has stable identity and defined scope.
- **SCENE-AT-046** — Partial, inaccessible and deferred search areas are distinguishable.
- **SCENE-AT-047** — Search activity records actual coverage, not just planned coverage.
- **SCENE-AT-048** — Search interruption and deviation are recorded.
- **SCENE-AT-049** — A negative search result is bounded by method, area, time and limitations.
- **SCENE-AT-050** — Search method selection and rationale are recorded.
- **SCENE-AT-051** — Item discovery records observer, time and original location.
- **SCENE-AT-052** — Original observation is preserved separately from interpretation.
- **SCENE-AT-053** — Multiple observers' conflicting accounts remain distinct.
- **SCENE-AT-054** — Corrections do not overwrite original observation wording.
- **SCENE-AT-055** — AI summaries cannot replace original scene observations.
- **SCENE-AT-056** — Photographic originals and derivatives are separately identified.
- **SCENE-AT-057** — Media records creator, device/method and capture time basis.
- **SCENE-AT-058** — Media references identify scene zone and related observation/item.
- **SCENE-AT-059** — Diagram states measured, approximate, illustrative or reconstructed.
- **SCENE-AT-060** — Measurements include units, method and uncertainty.
- **SCENE-AT-061** — Scene visual failure does not impair text operation.
- **SCENE-AT-062** — Environmental context is location- and time-valid.
- **SCENE-AT-063** — Occurrence, discovery, arrival, access and search times remain distinct.
- **SCENE-AT-064** — Device clock drift is recorded rather than silently corrected.
- **SCENE-AT-065** — Person presence records source, interval and uncertainty.
- **SCENE-AT-066** — Unidentified persons remain unresolved rather than fabricated.
- **SCENE-AT-067** — Scene presence does not automatically establish witness or suspect status.
- **SCENE-AT-068** — Relevant persons use canonical BP-03 identity.
- **SCENE-AT-069** — Permanent person promotion is never reversed.
- **SCENE-AT-070** — Total living population never exceeds 10,000.
- **SCENE-AT-071** — Recovery context is recorded before exhibit handover where feasible.
- **SCENE-AT-072** — BP-23 acceptance creates/returns the authoritative exhibit reference.
- **SCENE-AT-073** — BP-22 does not own exhibit custody after accepted transfer.
- **SCENE-AT-074** — Rejected or incomplete exhibit handover remains visible.
- **SCENE-AT-075** — Scene recovery does not create a forensic conclusion.
- **SCENE-AT-076** — Specialist attendance records scope, authority and limitations.
- **SCENE-AT-077** — BP-24 remains owner of forensic methods and results.
- **SCENE-AT-078** — BP-20 remains owner of surveillance originals.
- **SCENE-AT-079** — BP-21 intelligence references do not replace scene records.
- **SCENE-AT-080** — Scene links are typed and attributed.
- **SCENE-AT-081** — Shared address alone does not merge distinct scene episodes.
- **SCENE-AT-082** — Scene split/merge preserves original boundaries and history.
- **SCENE-AT-083** — Partial handover can be recorded by zone.
- **SCENE-AT-084** — Handover identifies outgoing and incoming controllers.
- **SCENE-AT-085** — Handover records unresolved areas and current condition.
- **SCENE-AT-086** — Release records authority, time and reason.
- **SCENE-AT-087** — Release does not alter BP-04 ownership or tenancy.
- **SCENE-AT-088** — Post-release access is retained in the history.
- **SCENE-AT-089** — Reopening records new authority, boundary and access state.
- **SCENE-AT-090** — Scene logs and media remain traceable for legal review.
- **SCENE-AT-091** — BP-22 does not decide admissibility, guilt or court findings.
- **SCENE-AT-092** — Sensitive scene content has purpose-bound permissions.
- **SCENE-AT-093** — Scene index access does not imply access to restricted images.
- **SCENE-AT-094** — Search previews, maps and exports enforce the same access policy.
- **SCENE-AT-095** — Restricted reads and state changes are audited.
- **SCENE-AT-096** — All scene activity uses BP-37 canonical simulation time.
- **SCENE-AT-097** — No scene/search/access activity progresses while player is absent.
- **SCENE-AT-098** — No environmental degradation or scene release progresses while paused.
- **SCENE-AT-099** — Resume restores exact scene state without off-screen catch-up.
- **SCENE-AT-100** — Scene records, boundary versions and access logs persist durably.
- **SCENE-AT-101** — Original media references and integrity metadata survive restore.
- **SCENE-AT-102** — Missing media is flagged, not replaced with unrelated content.
- **SCENE-AT-103** — Idempotent retry does not duplicate scene or access events.
- **SCENE-AT-104** — Scene handover transactions preserve source and recipient records.
- **SCENE-AT-105** — Text-only scene operations are complete.
- **SCENE-AT-106** — Every optional visual traces to canonical scene/spatial records.
- **SCENE-AT-107** — Visuals label uncertainty and do not contradict text records.
- **SCENE-AT-108** — Every material scene change has actor, authority, time and provenance.
- **SCENE-AT-109** — BP-43 test execution status is not inferred from specification creation.

## 30. Source traceability

The original 52-division source JSON and 52→44 crosswalk remain unchanged. Requirement and test IDs below use the source division number and original array order.

| Source ID | Original requirement/test | BP-22 coverage |
|---|---|---|
| S02.R02 | All places, routes, incidents and properties resolve to consistent spatial IDs. | Sections 4, 26; BP-02 owns canonical geometry, BP-22 references it. |
| S06.R03 | Ensure occupancy and access facts are time-valid. | Sections 4, 5, 9, 16; time-valid property/access context is consumed from BP-04. |
| S13.R02 | Model injuries, deaths, medical evidence and care access consistently without turning healthcare into a separate deep simulation. | Sections 7, 9, 17, 19; emergency/medical presence and scene disturbance are recorded without owning medical records. |
| S17.R03 | Support dispatch, pursuit, traffic enforcement, emergency access and case timelines. | Sections 4, 7, 9, 16; scene access and response route context references BP-02/BP-10/BP-12. |
| S18.R01 | Represent buildings, entrances, exits, rooms, access controls and asset condition. | Sections 4–5; BP-04 owns building topology, BP-22 records scene-specific boundaries/zones. |
| S18.R02 | Track keys, locks, alarms, maintenance, ownership and authorised access. | Sections 5, 10, 11; scene access events consume BP-04 access facts and record actual entry. |
| S18.R03 | Ensure scene geometry and access timelines are internally consistent. | Sections 4–5, 10, 16, 20; versioned boundaries and time-valid access. |
| S19.R02 | Apply environmental conditions to visibility, travel, infrastructure, health and evidence persistence where justified. | Sections 9, 16; scene-local environment context is sourced and limited; BP-35 owns causal effects. |
| S28.R01 | Simulate patrol presence, response, scene arrival, dynamic risk, public contact and field decisions. | Sections 7–10, 17; first response and scene arrival records consume BP-10. |
| S32.R01 | Represent scene boundaries, entry logs, scene security, search areas, recovery methods, exhibits, packaging, seals, handlers and transfers. | Sections 5, 10–13, 18; scene boundary/access/search owned here; exhibit lifecycle/continuity BP-23. |
| S32.R02 | Preserve original observations separately from interpretation. | Sections 14–15; immutable source observations and attributed interpretation. |
| S32.R03 | Support physical, digital, documentary, biological, trace and testimonial evidence. | Sections 18–19; scene recovery/context supports BP-23/BP-24 and testimonial source interfaces. |
| S36.R01 | Represent physical observation, CCTV, ANPR or equivalent systems, authorised technical monitoring, coverage, blind spots, time drift, retention and retrieval. | Sections 15–16, 19; scene records reference surveillance source records; BP-20 remains owner. |
| S45.R01 | Provide optional maps, layouts, timelines, charts and forensic scene visuals when useful or requested. | Sections 4, 15, 25; scene layouts/visual references optional, text-first. |
| S45.R02 | Visuals must derive from canonical spatial/evidence data and never silently contradict text records. | Sections 4, 15, 25; visuals trace to BP-02/BP-22/BP-23/BP-24 records. |
| S18.T01 | Every access event resolves to a real access point, actor or explainable mechanism. | SCENE-AT-035–041, 082–085. |
| S32.T01 | Every exhibit has unique ID, recovery details, continuity and current location/status. | SCENE-AT-067–074; BP-23 owns exhibit ID/continuity; BP-22 supplies recovery context. |
| S45.T01 | Every visual can be traced to the underlying canonical records. | SCENE-AT-056–061, 100–102. |

Cross-cutting rules X01–X10 apply where relevant: one-city canon and bounded population; canonical spatial identity; causal and time-valid records; source/provenance separation; fact/allegation/inference/evidence/finding distinctions; immutable originals and additive corrections; player agency and exact hidden-truth firewall; time freeze; storage/persistence integrity; text-first operation with optional traceable visuals. The crosswalk remains authoritative for the full wording and complete division mapping.

## 31. Open decisions and risk register

### Open decisions
1. Scene type taxonomy and which scene classes require formal designation.
2. Scene command/authority matrix and qualification requirements.
3. Boundary/zone naming conventions and minimum perimeter standards by scene type.
4. Access-log mandatory fields and reconstruction policy.
5. Search-method catalogue and approval/review requirements.
6. Scene photography, measurement and diagram metadata standards.
7. Hazard assessment vocabulary and specialist escalation rules.
8. Scene release authority, property access notification and reopening thresholds.
9. Exhibit handover acceptance protocol with BP-23.
10. Media retention and high-volume storage policy with BP-38/BP-39.
11. Sensitive scene-image classifications and access matrix with BP-42.
12. Rules for digital scenes and virtual evidence locations.
13. Scene review/quality assurance sampling policy.
14. Optional visual rendering formats and export requirements.

### Risk register

| Risk | Mitigation |
|---|---|
| Scene boundary mistaken for property boundary | Explicit BP-02/BP-04 ownership and versioned scene geometry |
| Scene designation mistaken for proof of crime | Scene status and offence classification kept separate |
| Unlogged access undermines integrity | Incomplete/unknown access remains explicit; retrospective additions attributed |
| Emergency intervention omitted | Mandatory disturbance record without delaying rescue |
| Search plan mistaken for completed search | Planned and actual coverage stored separately |
| Observation contaminated by interpretation | Separate immutable observation and attributed analysis |
| Exhibit ownership duplicated | BP-23 accepts authoritative exhibit custody |
| Weather/time assumptions corrupt chronology | Source/time/uncertainty on scene conditions |
| Visual suggests unsupported precision | Diagram precision class and source metadata |
| Paused simulation advances scene | BP-37 freeze tests |
| Hidden truth leaks through scene prompts | BP-14/BP-35/BP-42 information boundary |
| Storage compression loses provenance | Preserve originals, versions, access and handover events |

## 32. Design completion checklist

- [ ] All BP-22 source requirements and tests mapped in the 52→44 crosswalk are represented.
- [ ] Original 52-division source and crosswalk remain unchanged.
- [ ] Scene identity, lifecycle and ownership boundaries are explicit.
- [ ] Canonical geography/property/access remain owned by BP-02/BP-04.
- [ ] Boundaries, zones, access points and versions are represented.
- [ ] Initial response and emergency disturbance are preserved.
- [ ] Command, authority, safety and hazard handling are specified.
- [ ] Access logs and scene integrity/contamination controls are specified.
- [ ] Search plans, areas, execution and limitations are specified.
- [ ] Original observation is distinct from interpretation.
- [ ] Photography, diagrams, measurements and time basis are traceable.
- [ ] Environment and temporal context are sourced and uncertain where appropriate.
- [ ] People use canonical identity and distinct scene roles.
- [ ] Exhibit handover is explicit; BP-23 owns exhibit continuity.
- [ ] Specialist and surveillance ownership boundaries are explicit.
- [ ] Multiple/mobile/linked scenes are supported.
- [ ] Handover, release and reopening preserve history.
- [ ] Permissions, audit, persistence and failure cases are specified.
- [ ] Exact hidden-truth and no-unsolicited-hints rules remain binding.
- [ ] Pause freezes all scene activity and timers.
- [ ] Hard 10,000-person cap and permanent person promotion remain binding.
- [ ] Text-first operation is complete; visuals are optional and traceable.
- [ ] All 105 acceptance tests await BP-43 execution.
- [ ] Open policy decisions remain explicit and unassumed.
- [ ] No Neon write, migration, seed, import or bulk write has been made or authorised.

## 33. Status and next dependencies

This is a complete division design draft, not approved policy or implementation evidence.

- Specification: **DESIGNED_DRAFT**
- User approval: **PENDING**
- Implementation: **NOT_STARTED**
- Test execution: **NOT_STARTED**
- Verification: **NOT_STARTED**
- Neon/database writes: **NONE; NOT AUTHORISED**

Next fixed division: **BP-23 — Evidence Management**. BP-23 owns exhibit identity, packaging, seals, custody, transfers, storage, continuity and evidential lifecycle. BP-22 retains scene discovery context, search records and scene-to-exhibit handover references.
