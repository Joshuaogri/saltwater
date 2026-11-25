# BP04 player, police and BP-02 geography integration

**Status:** player command integration and officer-authorised adapter implemented on `main`; regression workflow passed on PostgreSQL-independent test fixtures. BP-02 canonical parcel/address binding remains blocked because no canonical parcel or address identities exist in the current BP-02 source map.

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

The adapter is ready for dispatch, incident and investigation services to call. Those service-level integrations remain future work because the corresponding complete police operational interfaces are not yet present in the runtime. This adapter does not bypass BP-42, evidence ownership, restricted-access policy or hidden-truth controls.

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
| Exactly one frontage-road candidate (unambiguous candidate only) | 88/420 |
| Multiple frontage-road candidates (requires address-side review) | 330/420 |
| No frontage-road candidate | 2/420 |

The three mismatches are explicitly preserved, not silently rewritten:
- `SWADDR-BPCSWD03N301701`: source `SWR-V16`; candidate frontage road `SWR-H17`.
- `SWADDR-BPCSWD03N301801`: source `SWR-V17`; candidate frontage road `SWR-H17`.
- `SWADDR-BPCSWD05N100201`: source `SWR-V01`; candidate frontage road `SWR-H01`.

Two addresses have no frontage-road candidate:
- `SWADDR-BPCSWD04N100402`: source road `SWR-B2`.
- `SWADDR-BPCSWD08N101802`: source road `SWR-B1`.

For a single frontage-road candidate, the register exposes a separate `address_road_candidate_id`; the original source road remains unchanged. This is a geometric design candidate only, not a canonical road correction, legal frontage, entrance or proof of access. The five exceptions remain open for BP-02 spatial/address review.

## 4. Verification and write boundary

The expanded BP04 player/police/geography workflow passed on `main` in [run 45685903741](https://github.com/Joshuaogri/saltwater/actions/runs/45685903741): 107 tests passed across player commands/runtime, ChatGPT host boundary, officer authorization, lookup, BP02 identity generation, address-frontage matching and geography reconciliation. The live-source reconciliation completed with 420/420 stable design parcel identities, 420/420 stable design address identities, 415 address-road/frontage candidate matches, 3 road conflicts, 2 no-frontage cases, 88 single-road candidate references and 330 multi-road ambiguous references. The authenticated player application composition test also passed in the Python-kernel job of [run 45681404048](https://github.com/Joshuaogri/saltwater/actions/runs/45681404048). The separate disposable-PostgreSQL job in that PKG-001 run remains blocked by an unrelated syntax error in `db/proposals/0028_bp12_incident_management.sql` at line 420; it is not a failure of the BP04 lookup tests.

The geography audit reports `database_write_performed: false`. No Neon writes, policy-grant writes, migrations, address promotions or archive re-uploads were performed. The separate PKG-001 and database-migration workflows remain blocked by the unrelated existing syntax error in `db/proposals/0028_bp12_incident_management.sql` at line 420; the dedicated BP04 integration workflow passed.

## 5. Remaining BP04 acceptance work

1. Complete BP-02 operational geography release: review the 420 candidate parcel geometries, prove/resolve frontage and address placement, confirm address scope/aliases and version lineage, and explicitly approve the operational geography version.
2. Promote the stable SWP/SWA design identities only through that release gate; then bind operational BP02 entity IDs and resolve database-specific spatial_id values by entity_code where materialised.
3. Provision the approved player and officer permission grants through the controlled authorization-policy process. This implementation deliberately did not modify Neon.
4. Wire `BP04PoliceLookupAccess` into actual dispatch, incident and investigation workflows when those owning services are implemented.
5. Complete the remaining business, ownership/tenancy, organisation/facility, operational-interface and 10,000-business performance acceptance criteria in the full BP04 audit.

**Decision:** player lookup commands are implemented and tested; the officer-authorised adapter is implemented and default-deny; source geography context is reconciled; canonical BP-02 parcel/address binding and full BP04 division acceptance are still incomplete.
