# BP04 player, police and BP-02 geography integration

**Status:** player command integration and officer-authorised adapter implemented on `main`; BP02 structural parcel/address/access acceptance passed on 2026-11-26 (run 45831361588), including evidence-based dispositions for all five former P1 exceptions. Operational BP-02 canonical parcel/address binding remains blocked pending geography approval, bridge entrance engineering and operational validation.

## 1. Player command surface

The canonical player command catalogue, parser, player interface, authenticated PKG-005 runtime, PKG-006 host adapter and PKG-007 ChatGPT tool contract now support:

```text
find address Harbour Avenue
find business Harbour Bank
find property SWPROP-...
inspect property SWPROP-...
inspect address SWADDR-...
inspect business SWBIZ-...
inspect building SWBLD-...
inspect premises SWPRE-...
inspect unit SWUNIT-...
inspect access_point SWACC-...
inspect establishment SWEST-...
```

`find` supports address, property and business searches. Search returns at most 10 player-facing results. `inspect` resolves one stable ID and returns a bounded dossier. The interface deliberately identifies the current BP04 geography as `source_geography_reference_only`; it does not call source address labels canonical BP-02 addresses.

The authenticated path is:

1. The trusted host supplies the opaque game-session credential.
2. PKG-005 resolves the authoritative player identity from PostgreSQL.
3. The existing command gateway re-verifies the session and checks the current `player.command.find` or `player.command.inspect` grant.
4. Only after that grant succeeds does the command router invoke its lazy BP04 lookup provider.
5. The process-local `BP04Lookup` loads and verifies the compressed BP04 archives once and reuses the selected identity/navigation index.

The ChatGPT tool schema and handler now accept bounded lookup commands up to 256 characters. Model arguments still cannot provide player identity, credentials or host context. Lookup commands are read-only and do not advance simulation time.

**Player policy requirement:** the active `sw_auth.permission_grant` policy must explicitly allow `player.command.find` and `player.command.inspect` for the intended player principal/role, resource `player:*`, purpose `gameplay`. No such grant was created by this implementation. The existing default-deny gateway therefore remains authoritative.

## 2. Police workflow access

`runtime/bp04_police_access.py` supplies a separate `BP04PoliceLookupAccess` facade:

- `search(credential, entity_type, query, limit)`
- `inspect(credential, entity_type, identifier)`
- `resolve_address(credential, address_id)`

It is not exposed through the public player command surface. Each operation:
- requires the expected principal kind `OFFICER`;
- checks the current permission grant for the exact BP04 action/resource and purpose `police_workflow`;
- re-loads grants for each decision;
- appends an authorization record through the configured audit sink;
- fails closed on missing grants, invalid/revoked sessions or audit failure.

`create_postgres_bp04_police_lookup_access(connect, lookup, principal_id)` composes the existing `PostgresSessionVerifier`, `PostgresGrantProvider` and `PostgresAuditSink`. The audit sink is durable and append-only. The factory creates no grants and runs no migration.

### Required officer grant contract

The active policy must explicitly provision the actions required by the workflow. Examples of action/resource/purpose tuples:

| Action | Resource pattern | Purpose | Principal constraint |
|---|---|---|---|
| `bp04.lookup.search.address` | `bp04:address:search` | `police_workflow` | `OFFICER` plus approved role |
| `bp04.lookup.search.property` | `bp04:property:search` | `police_workflow` | `OFFICER` plus approved role |
| `bp04.lookup.search.business` | `bp04:business:search` | `police_workflow` | `OFFICER` plus approved role |
| `bp04.lookup.inspect.address` | `bp04:address:*` | `police_workflow` | `OFFICER` plus approved role |
| `bp04.lookup.inspect.property` | `bp04:property:*` | `police_workflow` | `OFFICER` plus approved role |
| `bp04.lookup.inspect.business` | `bp04:business:*` | `police_workflow` | `OFFICER` plus approved role |
| `bp04.lookup.inspect.building` | `bp04:building:*` | `police_workflow` | `OFFICER` plus approved role |
| `bp04.lookup.inspect.premises` | `bp04:premises:*` | `police_workflow` | `OFFICER` plus approved role |
| `bp04.lookup.inspect.unit` | `bp04:unit:*` | `police_workflow` | `OFFICER` plus approved role |
| `bp04.lookup.inspect.access_point` | `bp04:access_point:*` | `police_workflow` | `OFFICER` plus approved role |
| `bp04.lookup.inspect.establishment` | `bp04:establishment:*` | `police_workflow` | `OFFICER` plus approved role |

These are policy requirements, not grants already present in production. No production policy rows were inserted or changed. Until a matching active grant exists, officer lookups are denied and audited.

The adapter remains the single officer-authorised BP04 lookup boundary. The current integration layer now includes explicit BP11 dispatch-to-incident location handoffs, BP08/BP10 deployment and arrival verification, BP12 event-backed incident location/timeline/history, and BP16 investigation-location history access. These are trusted injected service contracts and are covered by authorization/provenance tests; they do not constitute a complete CAD, patrol or investigation application, because those full operational service interfaces are not yet implemented in the runtime. No caller may bypass BP-42, evidence ownership, restricted-access policy or hidden-truth controls. Production policy grants remain default-deny until separately provisioned by the policy owner.

## 3. BP04-to-BP-02 address reconciliation

The read-only audit is implemented in `runtime/bp04_geography_reconciliation.py`. It regenerates the deterministic 420-parcel candidate set from SW-GEO-V1, reads the committed compressed BP04 property-world source, and reconciles every property/address relationship against the BP-02 source identity map.

Verified on the real committed source package in [workflow run 45680995361](https://github.com/Joshuaogri/saltwater/actions/runs/45680995361):

| Reconciliation | Result |
|---|---:|
| BP04 property records | 420 |
| BP04 address records | 420 |
| Source property-to-generated-parcel-candidate links | 420/420 |
| Primary property-to-address links | 420/420 |
| District IDs matched to BP-02 `entity_code` | 420/420 |
| Neighbourhood IDs matched to BP-02 `entity_code` | 420/420 |
| Road IDs matched to BP-02 `entity_code` | 420/420 |
| BP-02 canonical parcel identities in source map | 0 |
| BP-02 canonical address identities in source map | 0 |
| BP04 properties still awaiting canonical parcel binding | 420 |
| BP04 addresses still awaiting canonical address binding | 420 |

The 100-entry BP-02 identity map currently covers districts, neighbourhoods, roads, routes, landmarks and geographic zones. It does not contain parcel or address identity entries. The 420 parcel polygons are generated, unapproved design candidates; they have no BP-02 `spatial_id`. The BP04 `SWADDR-...` records are generated source-world address labels, not canonical BP-02 address entities.

**Reconciliation outcome:** all current district/neighbourhood/road context and internal BP04 property/address links reconcile, but canonical parcel/address binding remains `BLOCKED_BP02_CANONICAL_PARCEL_AND_ADDRESS_IDENTITIES_ABSENT`. Do not assign disposable integer IDs, infer canonical IDs from generated labels, or promote candidate geometry to operational geography.

### BP-02 stable parcel/address design identities — 2026-11-25

A new source-only identity layer, `runtime/bp02_parcel_address_identity.py`, now generates deterministic portable identities from the verified BP04 property/address source and BP04-03 parcel candidate geometry:

- Parcel IDs use `SWP-` plus 16 uppercase SHA-256 hex characters derived from the immutable parcel candidate ID.
- Address IDs use `SWA-` plus 16 uppercase SHA-256 hex characters derived from the immutable BP04 source address ID.
- Each of the 420 parcels retains its candidate geometry, source cell lineage, district/neighbourhood, area and road-frontage candidate references.
- Each of the 420 address identities links to its property, parcel identity, road, district and neighbourhood; original address attributes are preserved without fabricating missing numbers or entrances.
- Rebuilding from identical source inputs is deterministic. Duplicate IDs, orphan links, conflicting administrative context and unresolved road references fail closed.
- No PostgreSQL sequence values, production writes or operational seed approvals are embedded.

This closes the **portable design-identity mapping**: 420/420 properties map to stable parcel IDs and 420/420 primary addresses map to stable address IDs. It does not convert candidate geometry into an approved cadastral fabric. Parcel geometry remains `candidate_unreviewed`; frontage is not legal/usable frontage proof; source street labels/numbers remain unverified; the source geography remains unapproved for operational seed.

The reconciliation now reports separate measures:
- BP-02 design parcel identity matches: 420/420.
- BP-02 design address identity matches: 420/420.
- Operational canonical parcel/address release: still blocked (420/420 remain unapproved).
- Neon writes and address promotion: none.

The stable design IDs are source identities, not environment-specific `spatial_id` surrogates. Operational activation, geometry/address quality acceptance and later database materialisation remain separate release decisions.

A geometric road-frontage comparison now checks each BP04 source address road against the road IDs owning the parcel candidate's actual shared-boundary frontage segments. The latest real-source run found:

| Check | Count |
|---|---:|
| Source road matches parcel frontage-road candidate | 415 |
| Source road differs from parcel frontage-road candidate | 3 |
| No parcel frontage-road candidate | 2 |
| Exactly one geometric frontage-road candidate | 88/420 |
| Multiple geometric frontage-road candidates | 330/420 |
| Source road is a member of its parcel frontage candidate set | 415/420 |
| Single alternative frontage-road candidate proposed for review | 3/420 |
| No frontage-road candidate | 2/420 |
| Candidate road reference resolved (source match or single alternative) | 418/420 |

The three mismatches are explicitly preserved, not silently rewritten; the alternative is recorded separately as a review candidate:
- `SWADDR-BPCSWD03N301701`: source `SWR-V16`; candidate frontage road `SWR-H17`.
- `SWADDR-BPCSWD03N301801`: source `SWR-V17`; candidate frontage road `SWR-H17`.
- `SWADDR-BPCSWD05N100201`: source `SWR-V01`; candidate frontage road `SWR-H01`.

Two addresses have no frontage-road candidate:
- `SWADDR-BPCSWD04N100402`: source road `SWR-B2`.
- `SWADDR-BPCSWD08N101802`: source road `SWR-B1`.

For a single frontage-road candidate, the register exposes a separate `address_road_candidate_id`; the original source road remains unchanged. This is a geometric design candidate only, not a canonical road correction, legal frontage, entrance or proof of access. The five exceptions remain open for BP-02 spatial/address review.

### Building-access evidence cross-check

The same reconciliation now compares each source address against the generated building-boundary access candidates, not just parcel-boundary frontage:

| Measure | Result |
|---|---:|
| Property sites | 420 |
| Building design candidates | 1,474 |
| Building-boundary access-point candidates | 2,948 |
| Property sites with candidate buildings and road-access evidence | 384 |
| Source road matches the building-access road candidate set | 384/384 |
| Property sites with no generated building candidates | 36 |
| Unresolved building-to-road candidate links | 0 |

The two addresses with no parcel-boundary frontage candidate are not left without road context: both have building-access road-reserve proximity candidates matching their source road:
- `SWADDR-BPCSWD04N100402` → `SWR-B2`
- `SWADDR-BPCSWD08N101802` → `SWR-B1`

Both are `road_reserve_proximity_connection` with `POINT_CONTACT_ONLY`. They are proximity evidence, not frontage edges, entrances, traversable paths or legal/operational access.

The three source-road/frontage conflicts are all on property sites with no generated building candidates. Their alternatives remain `SWR-H17` (two addresses) and `SWR-H01` (one address); no source road is overwritten.

The 420-address review register classifies the records as P1=5 (three road conflicts plus two no-frontage cases), P2=33 (no-building sites not already classified P1), and P3=382 (source-context-coherent candidates). There are 36 no-building sites in total, three of which also have a P1 frontage conflict. The register remains an audit queue, not an approval.

## 4. Verification and write boundary

The expanded BP04 player/police/geography workflow passed on `main` in [run 45688271976](https://github.com/Joshuaogri/saltwater/actions/runs/45688271976): 120 tests passed across player commands/runtime, ChatGPT host boundary, officer authorization, lookup, BP02 identity generation, building-access reconciliation, address-frontage matching and the address review register. The live-source reconciliation completed with 420/420 stable design parcel identities, 420/420 stable design address identities, 415 source-road/frontage candidate matches, 3 single-alternative road candidates flagged for review, 2 no-frontage cases, 384/384 building-access source-road matches and 36 property sites without generated building candidates. The authenticated player application composition test also passed in the Python-kernel job of [run 45681404048](https://github.com/Joshuaogri/saltwater/actions/runs/45681404048). The separate disposable-PostgreSQL job in that PKG-001 run remains blocked by an unrelated syntax error in `db/proposals/0028_bp12_incident_management.sql` at line 420; it is not a failure of the BP04 lookup tests.

The geography audit reports `database_write_performed: false`. No Neon writes, policy-grant writes, migrations, address promotions or archive re-uploads were performed. The separate PKG-001 and database-migration workflows remain blocked by the unrelated existing syntax error in `db/proposals/0028_bp12_incident_management.sql` at line 420; the dedicated BP04 integration workflow passed.

## 5. Address placement review register

The read-only `SW-BP02-ADDRESS-PLACEMENT-REVIEW-V1` register now consolidates each of the 420 source addresses with its stable design IDs, original road, parcel frontage candidates and building-access candidates. It creates a five-record P1 queue for the three road conflicts and two missing-frontage cases; 36 properties without candidate buildings are separately classified. Source addresses and road references remain unchanged, and no operational address or access point is approved. See [BP-02 address placement review register](BP02-address-placement-review-register.md).

## 6. Remaining BP04 acceptance work

1. Complete BP-02 operational geography release: the full structural acceptance now passes (run 45831361588); all five former P1 exceptions have evidence-based design-geometry dispositions and zero address-road/access exceptions remain structurally unresolved. The remaining release work is separate: review/approve the SW-GEO-V1 operational version, review the 36 no-building-site cases as a distinct context question, confirm address scope/aliases and version lineage, and complete entrance engineering/operational validation for the four bridge connector candidates. No canonical addresses or operational access points are approved yet.
2. Promote the stable SWP/SWA design identities only through that release gate; then bind operational BP02 entity IDs and resolve database-specific spatial_id values by entity_code where materialised.
3. Provision the approved player and officer permission grants through the controlled authorization-policy process. This implementation deliberately did not modify Neon.
4. Integrate the provenance-preserving `BP04IncidentLocationResolver` candidate into the BP12 incident-location command and the dispatch/investigation owning services. The resolver requires separate incident and address grants and audits both reads. `record_address_location` now hands the reviewed candidate to a trusted BP12 writer, passing the caller/source reference and resolved BP04 address reference separately. BP12 `add_incident_location` writes an `INCIDENT_LOCATION_ADDED` simulation event and append-only location row in one transaction, enforces runtime/incident-state boundaries and canonical-spatial identity requirements, and is idempotent by event key. No spatial identity is inferred from an address candidate.
5. Complete the remaining business, ownership/tenancy, organisation/facility, operational-interface and 10,000-business performance acceptance criteria in the full BP04 audit.

**Decision:** player lookup commands and the officer-authorised adapter are implemented; BP04 address-to-incident resolution and BP12 event-backed location writes are implemented with separate source provenance and idempotency tests. `sw_incident.incident_location_history` provides an ordered, event-joined read model; the officer resolver exposes it only after the dedicated `bp12.incident.inspect.location.history` grant and verifies incident identity and mandatory provenance. Canonical BP-02 parcel/address binding, production grant provisioning and full BP04 division acceptance remain incomplete.


## Dispatch and investigation location handoffs

`BP04IncidentLocationResolver.prepare_dispatch_address_candidate` now provides BP11 with a minimal address reference and confidence/provenance fields; it does not copy the full BP04 address record into dispatch state. Access requires the dedicated `bp11.dispatch.location.resolve` grant, followed by the existing BP12 incident-inspection and BP04 address-inspection checks. `read_investigation_location_history` requires both the BP16 investigation-history grant and the BP12 incident-history grant before returning the event-backed chronology. Each decision is independently audited. These are cross-domain read adapters only: BP11 remains owner of dispatch/CAD, BP12 remains owner of incidents, and BP16 remains owner of investigative work.


The production read path is backed by `runtime/bp12_incident_location_history.py` (`PostgresIncidentLocationHistoryReader`). It calls the BP12 history function using a parameterised incident ID, returns the event-joined chronology as named fields, rejects invalid IDs and fails with a sanitised unavailable error. It performs no writes. The dispatch and investigation adapters accept this trusted reader's `read` method.

Investigation access is case-scoped: the adapter first authorises `bp16.investigation.inspect.case`, then requires a trusted BP15 case-to-incident link verifier to confirm that the incident belongs to that case, before it checks the dedicated BP16 location-history grant and BP12 history grant. An unlinked incident is denied before history is read. This is a read-only handoff; it does not create or own BP15 case records or BP16 investigative work objects.


## Dispatch-originated incident location updates

`BP04IncidentLocationResolver.record_dispatch_address_location` now provides the BP11-to-BP12 write handoff. It requires the distinct `bp11.dispatch.location.record` permission, then independently authorises dispatch location resolution, BP12 incident inspection and BP04 address inspection. It passes the dispatch/CAD reference, address source reference, dispatcher actor, authority, confidence, role, raw operational description and idempotency key to the trusted BP12 event-backed writer. BP11 receives the resulting location ID and dispatch reference; BP12 alone creates the authoritative incident location/event and chronology. Retries use the BP12 idempotency key. This adapter does not update CAD state, select units, or alter BP12 incident status.
Dispatch write-through also requires a trusted BP11 assignment verifier and a separate `bp11.dispatch.inspect.assignment` grant. The referenced CAD/dispatch record must independently prove its link to the target incident before BP12 is called; mismatched or unverified dispatch-to-incident links are rejected before incident/address resolution or persistence.
\n\n## Dispatch acknowledgement and field-arrival chronology reads\n\n`PostgresIncidentOperationalTimelineReader` calls `sw_incident.operational_timeline` with a parameterised incident ID and validates returned event identity, supported event codes, and source/actor/authority provenance. `BP04IncidentLocationResolver.read_operational_timeline` exposes the result only after the dedicated `bp12.incident.inspect.operational_timeline` authorisation decision has been audited. The read path is strictly read-only; BP11 continues to own dispatch acknowledgements and BP08/BP10 continue to own deployment and field activity. Regression tests cover successful reads, denied reads before database access, cross-incident row rejection and parameterised PostgreSQL access.\n

## Dispatcher and incident-commander chronology projection

`build_incident_operational_timeline_view` converts rows obtained through `BP04IncidentLocationResolver.read_operational_timeline` into a compact chronological view. It presents dispatch acknowledgement and unit arrival entries with their timestamps, world ticks, dispatch/deployment/field-activity references, source references, actor and authority. It rejects unsupported event types, incomplete provenance and noncanonical ordering. This is a presentation projection only: it performs no authorisation itself and must only receive rows after the audited officer access method; dispatch, deployment and field activity remain owned by BP11/BP08/BP10.


## Incident command handover reconciliation

`reconcile_incident_command_handover` accepts the canonical BP12 incident status, an authorised BP08 assignment snapshot and the BP12 operational timeline. It validates the snapshot source reference and world-tick context, duplicate assignment identities, arrival ordering and cross-domain unit/assignment references. It reports unresolved active assignments, arrivals without current assignments, unit mismatches, arrival/assignment-state conflicts and active deployments on terminal incidents. `handover_ready` is true only when the reconciliation finds neither unresolved assignments nor discrepancies. The function is a pure read-only reconciliation step; callers remain responsible for obtaining incident, deployment and timeline snapshots through their respective authorised readers. No source system is mutated.


`BP04IncidentLocationResolver.build_authorised_command_handover` is the officer-facing orchestration boundary. It independently audits `bp12.incident.inspect.command_handover`, `bp08.deployment.inspect.incident_assignments` and `bp12.incident.inspect.operational_timeline` before using the trusted incident, BP08 assignment and BP12 chronology readers. It then calls the pure reconciliation function. Denial occurs before protected readers are invoked; no BP08/BP10/BP11/BP12 operational source records are changed.


## Command handover record projection

`build_incident_command_handover_record` composes the assignment/arrival reconciliation with commander decisions and rationales, outstanding actions and owners, responsibility transfers, and acknowledgements. It validates record identity and provenance, world-tick chronology, duplicate record references, commander attribution, transfer direction, and acknowledgement recipient/handover identity. A handover is ready only when the assignment reconciliation is clear, responsibility is transferred from the outgoing commander to the incoming commander, and the incoming commander explicitly accepts. Outstanding actions can remain open if they retain a named owner and are carried into the record. The result status is `PROJECTED_NOT_PERSISTED`; this is deliberately a read-only projection. Durable persistence is now exposed through `BP04IncidentLocationResolver.record_authorised_command_handover`: it first audits `bp12.incident.record.command_handover`, then independently audits incident inspection, BP08 assignment inspection and BP12 operational-timeline inspection before building the projection and invoking the trusted BP12 writer. The writer only accepts a ready projection, and the SQL register appends the simulation event and immutable handover document. History is exposed through `read_authorised_command_handover_history`, protected by its separate `bp12.incident.inspect.command_handover.history` grant. Denials occur before protected readers or the writer are invoked. These adapters do not grant permissions or apply the migration; migration `0029` remains repository/disposable-test only and has not been applied to production Neon.


## BP04 completion plan — integration and acceptance only

**Scope decision:** the canonical BP04 property/business source inventory is frozen for completion work. Do not generate additional properties, buildings, premises, units, rooms, physical components or asset registers. Only add source detail when a concrete player or police workflow demonstrates a missing required field.

The remaining work is divided into four acceptance tracks:

1. **Player gameplay:** verify the authenticated `find`/`inspect` commands against the real archive-backed lookup, including all supported entity types, bounded results, missing records, malformed source data, lazy loading after authorisation, and proof that lookup commands do not advance world time. Verify both allow and deny policy paths in disposable PostgreSQL.
2. **Police operational integration:** retain BP04 as a read-only source. Complete service-level call sites as BP11 dispatch/CAD and BP16 investigation runtimes become available. Existing tested bridges cover dispatch-originated incident addresses, BP12 incident location/history/timeline, BP08/BP10 deployment and arrival verification, and command handover. Verify principal/session attribution, purpose-specific grants, durable audit, source provenance and fail-closed behavior across every call site. Do not invent missing CAD or investigation systems merely to make the checklist appear complete.
3. **Operational reference interfaces:** add only the bounded reads needed by actual workflows for business operating schedules, utilities, healthcare and transport. Each interface must identify its owning blueprint division, return source provenance and freshness, distinguish source-world information from live/verified state, and have a real consumer before it is counted as implemented.
4. **Consolidated acceptance:** run the pinned archive/source integrity and cross-register checks, player command integration, officer authorization and police handoff tests, BP02 address/parcel reconciliation and geometry audit, representative lookup performance, and failure/rollback/recovery checks. Publish a criterion-to-test matrix with explicit PASS, BLOCKED or NOT IMPLEMENTED results. BP04 is complete only when every required BP04 criterion passes or an explicitly accepted dependency is recorded; successful archive deployment alone is not division completion.

**Release boundaries:** BP02 operational parcel/address approval remains a separately owned geography dependency; BP04 must continue to label its stable SWP/SWA design identities as unapproved for operational use. No production Neon writes, grants or data promotions are authorised by this plan.


### Player command integration — real archive test added (2026-11-26)

Added `tests/pkg001/test_bp04_player_commands_archives.py` and wired it into the PostgreSQL 16/18 BP04 disposable workflow immediately after the archive-only import. Unlike the lookup-only archive test, this exercises the actual `PlayerCommandInterface` using the real `BP04Lookup` built from the imported compressed archives.

The integration covers `find` for property, address and business; `inspect` for property, address, building, premises, unit, access point, business and establishment; malformed/missing records; and proof that read-only lookup leaves lifecycle, player presence and world tick unchanged. The workflow is triggered by the new test and runs it on both PostgreSQL versions. Result remains pending until GitHub Actions reports the run; this is not yet a passing acceptance claim.


### Authenticated officer attribution — implemented, production resolver still required (2026-11-26)

`AuthorizationDecision` now carries `active_person_id` from the same verified session used for the audited authorization decision. The BP04 gateway returns that decision to the protected handover operation. Before owner snapshots are read or BP12 is called, handover persistence requires a trusted, injected personnel-reference verifier to confirm that `prepared_by_ref` belongs to that verified active person. Missing active-person identity, absent resolver, or a non-matching reference fails closed.

Regression coverage includes the matching authenticated preparer, a caller-supplied mismatched preparer, and a session without `active_person_id`. The audited officer-authorization test step passed in [BP04 workflow run 45825332438](https://github.com/Joshuaogri/saltwater/actions/runs/45825332438); the full geography workflow remains in progress at the time of this note. The repository now provides the fail-closed contract, but production handover remains unavailable until the owning personnel service is wired as the trusted reference verifier. No production grants were created and no production Neon changes were made.


### BP06-backed handover identity resolver (2026-11-26)

The trusted personnel-reference dependency now has a concrete PostgreSQL adapter: `PostgresPersonnelReferenceVerifier` queries the BP06 `sw_police.personnel_service_current` view and requires all of the following to match: the verified session's canonical `person_id`, the supplied opaque `personnel_id` UUID, `service_status='active'`, `personnel_category='sworn_officer'`, and `service_state='active'`. Invalid UUIDs and non-positive person IDs are rejected before database access. Database errors propagate, so the protected operation fails closed. `create_postgres_bp04_incident_location_resolver(...)` composes this verifier with the BP04/BP12 resolver. No grants are created and no production database is modified. Unit tests cover matching identity, missing/inactive identity, invalid references and database failure; the PKG-001 workflow now runs these tests.

This completes the repository-side personnel verifier implementation. It does not prove production deployment or a live authorised handover: BP06 schema availability and the caller's trusted connection factory must be supplied in the deployment environment, and production officer grants remain default-deny.


**CI result:** The new `test_bp06_personnel_reference.py` suite passed in the Python-kernel job of [PKG-001 run 45826593214](https://github.com/Joshuaogri/saltwater/actions/runs/45826593214). All 26 Python-kernel steps passed. The disposable PostgreSQL job has passed schema setup, BP06 dossier/supervisor acceptance, and is continuing through the population-cap and backup/restore checks; its overall workflow result is not yet final.


## BP02 structural acceptance update — 2026-11-26

The consolidated BP02 full parcel/address/access audit passed in [run 45831361588](https://github.com/Joshuaogri/saltwater/actions/runs/45831361588). All 12 structural assertions passed, all six geometry/access layers report zero failed checks, all 420 property/address links resolve, and all five former P1 exceptions now have resolved design-geometry dispositions. There are zero unresolved address-road/access exceptions. The three unique parcel-frontage associations and two bridge-to-public-network geometric dispositions are described in [the BP02 review register](BP02-address-placement-review-register.md).

This removes the previous structural exception blocker; it does not approve operational geography. SW-GEO-V1 remains a design baseline; the four bridge connector candidates still require entrance engineering and operational validation; canonical parcel/address records and operational access points remain unmaterialised/unapproved. BP04 remains NOT COMPLETED pending its separate permission, owner-service integration and cross-register acceptance criteria. No Neon writes or production grants were made.

### BP02 no-building-site evidence review — 2026-11-26

The 36 property sites without generated building candidates were reviewed against the Stage E generator logic. The available generated property records retain `site_state=unknown` and `boundary_status=unverified`. Zero-building output can result either from the footprint search finding no feasible footprint or from the generated `open_space` land-use class; the current summary does not retain a per-site reason code. It therefore cannot support a reliable classification of any site as vacant, undeveloped, open space, occupied or reserved.

The 36 are retained as `NO_BUILDING_CANDIDATE — CAUSE UNCLASSIFIED`. No properties or physical assets are added, and no land-use, occupancy, access or address facts are inferred. The frozen BP04 inventory remains unchanged. See [BP-02 address placement review register](BP02-address-placement-review-register.md). This resolves the evidence question as far as current source data permits; it does not approve operational geography or change BP04 completion status. No Neon writes or production grants were made.

