# Saltwater

## Gemini active-blueprint engineering collaboration

Gemini is used as an independent engineering collaborator for the **currently active
blueprint division**. Every review is explicitly told the active BP identifier and
must focus on that BP rather than conducting an unfocused whole-project audit.
The active division is selected through the workflow's `active_bp` input; the
current default is **BP03 — Population and Individual Simulation**. When project work
moves to another BP, update the default so automatic push and scheduled reviews
target the new active division. Manual runs can select a different BP.

For BP03, Gemini's primary review scope is population accounting and individual simulation: canonical person identity, opening 9,500-person cohort, 10,000-person hard cap, population-scope rules, lifecycle and residence history, atomic admissions, demographic/provenance handling, processing tiers, permanent police-relevance promotion, and the BP-02/BP-04/BP-06 interfaces. Other BPs are examined only for concrete dependencies affecting the active BP; they are not independently audited.

For BP02, Gemini's previous review scope was operational geography: deployment
package, source-to-table mapping, stable identity, districts, neighbourhoods,
features, roads, network nodes and segments, routes, parcels, addresses,
access-point locators, referential integrity, deterministic packaging, tests,
measured Neon storage impact, and separation from the completed archive-only
release. Other BPs are examined only for concrete dependencies affecting the
active BP; they are not independently audited.

The workflow runs on pushes to `main`, weekly, and on manual dispatch. It can
collect changed or full repository context, but the review mandate remains
focused on the selected BP. Large JSON datasets are structurally summarised
with bounded samples and hashes; compressed and binary artifacts are excluded.
Gemini must distinguish evidence from hypotheses and must not claim it ran
tests or inspected live Neon.

Gemini is read-only and has no repository write permission or Neon credentials.
ChatGPT checks its findings, implements justified fixes directly on `main`,
and validates them. Production Neon writes remain subject to explicit approval
and a measured storage estimate. The workflow uses the existing
`GEMINI_API_KEY` Actions secret; never place the key in source code or chat.

## BP03 ↔ BP02 canonical residence linkage

BP03 now has a residence record linked by foreign key to the operational BP02 address identity (sw_geo.bp02_address.source_id). A person has one current residence link with effective-dated history; assigning or moving residence updates the same canonical person and usual-resident qualification. Ending residence removes only the residence qualification: a person still physically present or serving in the police remains counted once.

The disposable acceptance fixture creates two BP02 addresses, tests idempotent assignment, moves a person between addresses, confirms the previous residence is closed, and verifies that ending residence does not remove a physically present person. It then removes physical presence and checks the count returns to zero. No production address or resident records have been imported or written.

## BP03 ↔ BP06 police population integration

BP06 service-appointment events now update the BP03 canonical population ledger automatically. The integration uses the existing canonical person ID, preserves resident and physical-presence qualifications, and toggles only the overlapping active-police-service qualification. A person already counted as a resident or physically present remains one person; police membership does not add a second headcount.

Countable service states are active, leave, suspended, secondment-out, secondment-in and notice for primary sworn, civilian, technical-professional and auxiliary appointments. Contractors and terminal/non-service states do not qualify as active police-service members. The sync is driven by the append-only BP06 personnel service event, not by an independently maintained headcount.

Disposable acceptance now reconciles BP06 personnel dossiers against BP03 active-police membership, including leave, suspension, separation, event history and idempotent replay. Production Neon remains unchanged.


## BP03 household membership and residential unit linkage

BP03 has a disposable-only household service linking canonical people to BP04 dwelling units and BP02 operational addresses. The BP04↔BP02 address crosswalk is accepted only when the BP04 property's source parcel identity, BP04 address provenance and BP02 address all resolve to the same canonical parcel; no street-name or approximate-location matching is used. A household is limited to one current household per dwelling unit, and a person can have only one current household membership. Membership requires the person's current BP02 residence to match the household address.

The BP04 importer preserves the source property's `primary_use` as `property_site.use_class`; household eligibility therefore requires an active `unit_class='dwelling'` in an active parent property whose use class is `dwelling` (pure residential) or `mixed_use`. The earlier pure-residential acceptance passed in disposable PostgreSQL (run 46025839757; evidence: `docs/implementation/test-evidence/BP03-household-membership-acceptance-0003.md`); a follow-on fixture now exercises a mixed-use residential site. The property-world generator separately reports pure-residential and mixed-use dwelling counts plus their combined household-eligible inventory. Physical occupancy capacity remains unassessed, so dwelling counts are not treated as a 9,000-person capacity estimate.

Household creation, membership additions and departures retain append-only event history. Household membership does not itself create or remove a person's population qualification: two people in one household remain two canonical people, and ending a household membership does not silently end residence. Disposable acceptance covers exact parcel crosswalk, dwelling validation, two-member household reconciliation, contact uniqueness, membership departure and unchanged population count. The household acceptance runs in the PKG-001 disposable workflow against the canonical BP04 property stack and BP02 operational geography. No production household, unit or resident records have been imported.

## BP03 population service — qualification union implementation in CI

A disposable-only follow-on proposal, db/proposals/0010_bp03_population_qualification_union.sql,
now replaces the earlier single scope_status counter with the binding
SW-CANON-001 union: a living canonical person counts once when any of
usual_resident, physically_present, or active_police_service is true.
The counter row remains the serialization point for concurrent admissions and
lifecycle transitions. A read-only population summary exposes the total and
overlapping category sub-counts.

The proposal adds controlled canonical-person creation through the SW-UNS
name registry, qualification transitions, death handling, idempotency keys,
and append-only qualification history. The disposable acceptance checks cover
single-category counting, overlapping categories counting once, removal of
one qualification while another remains, exit/separation, death, and refusal
to requalify a deceased identity. The existing 9,999-to-10,000 concurrent
admission test now qualifies its test people explicitly as usual residents.

The migration refuses to infer categories for existing population rows and
requires an empty population state/counter. Existing scope_status values alone
do not identify whether someone is a resident, physically present, or an
active police-service member. No production Neon migration or population
seed has been run. BP03 remains in progress pending disposable PostgreSQL
acceptance and later BP02 address / BP06 service integration.



The 9,000-person civilian candidate set now has a disposable PostgreSQL SW-UNS acceptance test. It stages all candidates, creates canonical person identities in one transaction, verifies that all 9,000 receive unique canonical reservations against the existing global registry, checks the exact 9,000 + 500 opening arithmetic and civilian/police name separation, then rolls back the entire test. The separate 500-person police registry preflight remains in place. These are preflight-only records; no production identities or population qualifications are created.
## BP03 stable BP04-to-BP02 parcel/address crosswalk

The BP03 household crosswalk now validates the shared immutable source parcel identity carried in the BP04 property/address provenance and the BP02 address/parcel records. It separately retains the BP02 stable hashed parcel source ID in the crosswalk; it no longer incorrectly compares that hash with the raw BP04 candidate parcel ID. The disposable household acceptance fixture now uses distinct stable BP02 parcel/address IDs and the matching source-candidate parcel provenance. This is a source/acceptance correction only; it does not alter the already released BP02 production records or create BP03 production links.

## BP03 opening resident-to-dwelling allocation — candidate build

A deterministic allocation builder is now on `main`. It maps the 9,000 civilian identity candidates to unique active dwelling-unit candidates, allocating by largest-remainder proportional shares of eligible dwelling inventory across neighbourhoods and stable unit ordering. It derives the released BP02 stable parcel/address IDs from the same source-identity hashing rules used by BP02. Multiple dwellings may correctly share one site-level BP04/BP02 address.

The allocation is strictly a planning manifest: no canonical person IDs, residence records, household records, occupancy assignments or production imports are created. The builder validates source hashes, parcel/address provenance, property/building/premises/unit eligibility, and exact population arithmetic. Its property-world workflow completed successfully in [run 46032784314](https://github.com/Joshuaogri/saltwater/actions/runs/46032784314), committing both compressed datasets and their summaries to `main` at `89a3ac4cf8cbfbb7894555b5f9387606ba88af4b`. The accepted candidate output contains **9,000 unique candidate-to-dwelling matches** across **55,558 eligible dwelling units**, leaving **46,558 eligible units unallocated**. The allocation file is **244,187 compressed bytes**; manifest SHA-256 is `256d2471eb62a97cd4cacb444aa194d54ba0765b17a3dd0763f460712d8ed993`. Six allocation regression tests passed, covering deterministic output/hash, BP02 identity derivation, unique candidate/unit mapping, exact reconciliation, proportional neighbourhood distribution, and non-materialisation. The manifest remains candidate-only: no canonical person, residence or household rows are created; occupancy capacity remains `NOT_ASSESSED`; `production_seed_authorized=false`.

## BP03 residential dwelling inventory — 2026-11-27

The canonical property-world manifest reports **55,558 household-eligible dwelling units**: **31,785** in pure-residential properties and **23,773** in mixed-use properties. These are active inventory classifications for allocation planning, not a verified person-capacity figure. Physical occupancy capacity remains **NOT_ASSESSED**; resident allocation remains **NOT_ASSIGNED**; the manifest records zero people created and `production_seed_authorized=false`. The 9,000-person civilian candidate cohort must therefore not be described as housed or resident-linked until deterministic BP04-unit/BP04-address/BP02-address mapping and its acceptance checks are complete.

## BP03 opening identity candidate cohorts — 2026-11-27

BP03 now has deterministic, source-controlled candidate datasets for both exact
opening cohorts. The civilian resident build workflow
[46016834874 — success](https://github.com/Joshuaogri/saltwater/actions/runs/46016834874)
generated and committed the resident dataset to `main` at
`e6422fb04ea4d40d6ef33bb973a6375b057f541f`.

- **9,000 civilian usual-resident name candidates** in
  `data/people/saltwater-opening-civilian-resident-seed-v1.json` and its
  deterministic gzip companion.
- **500 police-person name candidates** remain in
  `data/people/saltwater-opening-police-person-seed-v1.json` and its gzip
  companion.
- Exact candidate names are unique within each cohort, and the two cohorts
  have zero exact-name overlap. The 9,000-person cohort is checked for exact
  duplicates; final global/near-duplicate reservation remains the responsibility
  of the authoritative SW-UNS registry.
- Opening arithmetic is exactly **9,000 + 500 = 9,500** distinct people, with
  **500 unused places** below the 10,000-person ceiling.
- Resident dataset manifest SHA-256:
  `e8dcfca02f7a3f2d80d53a90a79eae1b572be135d68653f57a3c451f014dbe43`.
  Readable JSON is 4,603,381 bytes; deterministic gzip is 253,572 bytes.
- Five resident-seed regression tests and five police-seed regression tests
  passed in the build workflow.

These files are **identity candidates only**. They do not create canonical
`sw_people.person` rows, assign BP02 addresses/parcels, invent ages or other
demographic facts, or create BP06 personnel appointments. No production Neon
write or import was performed; `production_import_authorized=false`.

BP03 remains in implementation, not complete. The next substantive runtime
slice is the canonical person/population service, including the approved
deduplicated qualification union (usual residence, physical presence and active
police membership), atomic cap enforcement, lifecycle history and residence
links. The existing disposable population proposal's single inclusion flag is
not sufficient to implement that rule and must not be treated as production
schema.

## BP02 operational geography — production release completed (2026-11-27)

The approved BP02 operational geography release is now deployed to production Neon.
GitHub Actions [run 46014720819](https://github.com/Joshuaogri/saltwater/actions/runs/46014720819)
completed successfully on `main`. The workflow built and validated the approved
package, passed the exact-target production preflight, applied
`0002_operational_geography`, imported the package, verified all records and
relationships, confirmed the repeat import was idempotent with **0 bytes** of
additional growth, and uploaded the exact deployed package.

Production BP02 migration ledger now contains versions 1 and 2. Migration 0002
checksum: `1c483229b407dc824cbb2464944394f8b1e997517e6f95d77372010bdec4eb22`.
The immutable source archive `SW-GEO-V1` remains intact, and the global
`sw_ops.schema_migration` ledger remains unchanged at versions [1, 2].
The production release record is
`SW-BP02-OPERATIONAL-GEOGRAPHY-V1`, package SHA-256
`ee250551239292e16808eb2d063d54dd290a04d001ab2127f2dd3773686ecc10`,
with `production_seed_approved=true` based on the user's explicit approval.

Imported and independently verified production row counts:

- 8 districts; 24 neighbourhoods; 54 geographic features.
- 42 roads; 367 network nodes; 685 road segments.
- 5 routes; 116 route-node links; 111 route-segment links.
- 420 parcels; 420 addresses; 2,948 access-point locators; 4 bridge connectors.
- All 685 road segments resolve to their endpoint nodes and parent roads;
  all 420 addresses resolve to parcels.
- All 2,948 access-point locators and all four bridge connectors retain their
  approved in-game status. Candidate access/bridge semantics were not silently
  promoted to verified physical entrances or routable connectors.

The release workflow measured production at **16,728,064 bytes** after import,
a **6,766,592-byte** increase from the guarded 9,961,472-byte baseline
(approximately 6.45 MiB). A subsequent independent read-only Neon check measured
**16,752,640 bytes**; this is the latest direct database-size reading, or
**6,791,168 bytes** above the same baseline (approximately 6.47 MiB).
The 24,576-byte difference between the two readings is retained transparently;
the workflow's recorded repeat-import check itself showed identical before/after
sizes and **0 bytes** growth. The isolated disposable estimate was a projection,
not a substitute for these production measurements.

The deployed package is 227,656 compressed bytes and 5,354,226 uncompressed
bytes. The exact deployed package and manifest are retained in artifact
[bp02-operational-geography-v1-production-package](https://github.com/Joshuaogri/saltwater/actions/runs/46014720819/artifacts/15206266694)
(212,032-byte ZIP; expires 2027-02-25). The pre-release recovery branch
`br-gentle-moon-bdtc0y32` was preserved unchanged.

This production deployment supersedes the earlier BP02 README notes stating
that operational geography had not been seeded, that migration 0002 was
pending, or that production remained at 9,961,472 bytes. Those entries are
historical preparation records, not the current state.

## BP02 bridge identity and business-naming lock remediation — 2026-11-26

The BP02 bridge assessment builder now selects only the four connector identities
confirmed by the address-frontage exception register. Matching is by bridge road,
property, parcel, access-point candidate and road-access candidate; unrelated
corridors that happen to share a bridge road ID are excluded. Each selected
connector receives a distinct bridge-approach ID and a one-to-one engineering
assessment record. The acceptance audit now verifies all four approach identities.

The BP04 business-name reservation path no longer takes a table-wide
`SHARE ROW EXCLUSIVE` lock on `sw_names.name_reservation`. The global exact/near-
duplicate check is serialized with a transaction-scoped advisory lock in the
reservation guard, allowing autovacuum to work without waiting for a relation lock.
The PostgreSQL regression test checks that the advisory lock is held and the
table-wide lock is absent during a bulk reservation transaction.

The previous disposable PostgreSQL run timed out during the 20,000-name business
reservation acceptance. Its server log repeatedly reported autovacuum skipping
`name_reservation` because the table lock was unavailable. This is a CI-only
disposable database finding: inspection of the connected Neon database found no
`sw_names` schema/table and no active blocking lock or long-running query. No
production Neon data was changed.

The remediation is committed on `main` (latest source/test commit
`f1c4f4ba6fb4705b9e5d3f207ae80a23d3c5e073`). Latest validation status:

- Database migration validation: passed, run [45881868532](https://github.com/Joshuaogri/saltwater/actions/runs/45881868532).
- BP04-03 geography readiness: passed, run [45881868543](https://github.com/Joshuaogri/saltwater/actions/runs/45881868543).
- BP04 player/police/geography integration: passed, run [45881748368](https://github.com/Joshuaogri/saltwater/actions/runs/45881748368).
- BP02 full parcel/address/access acceptance: running, run [45881748459](https://github.com/Joshuaogri/saltwater/actions/runs/45881748459).
- PKG-001 disposable PostgreSQL validation: running the business-name acceptance step, run [45881868578](https://github.com/Joshuaogri/saltwater/actions/runs/45881868578).

The two long-running acceptance workflows have not reported a failure in their
current steps. Their final results are not yet claimed.


Saltwater is a fictional sovereign city-state and a single-city police simulation.

## BP03 active division — population and individual simulation

BP02 is complete and its operational geography is deployed to production Neon.
The active division is now **BP03 — Population and Individual Simulation**.
The full master blueprint BP01–BP44 is approved; no repeat division-approval
gate is required.

Binding population canon is already settled in SW-CANON-001: 10,000 living
people maximum; opening target 9,000 residents plus 500 police (9,500 total);
500 unused shared headroom; police are a subset of population; one canonical
person identity per individual; no automatic filling of headroom. The exact
population-scope rules and single-person counting semantics are adopted.

Existing implementation is partial, not a completed population service:
- Disposable-only proposal `db/proposals/0002_runtime_city_population.sql`
  defines canonical person identity/profile history, population state/history,
  a serialised population counter and the 10,000 cap.
- PKG-001 run [45265769796](https://github.com/Joshuaogri/saltwater/actions/runs/45265769796)
  passed the disposable concurrent 9,999-to-10,000 admission test: one
  transaction admitted and the competing 10,001st admission was rejected.
- Compact full-cap fixture growth measured 8,192,000 bytes on disposable
  PostgreSQL 16.16; this is not a Neon production estimate.
- A 500-name opening police identity candidate dataset exists, but those names
  are not yet canonical person records or BP06 service dossiers in production.
- The authoritative 9,000-resident opening cohort has not yet been created or
  seeded. No BP03 population/person production seed is authorised by this
  status note.

Next BP03 work is to complete the population service and reproducible disposable
acceptance against current `main`, then prepare the opening population seed
using canonical geography/address links and SW-UNS identity reservations.
Keep population headroom unused, preserve one identity per person, and do not
write to production Neon without a separate exact-operation approval and
measured storage estimate.

## Single-player NPC world

Saltwater has one human player. Every other person is an NPC: police staff, commanders, dispatchers, residents, business owners, officials, witnesses and suspects. NPCs are world actors, not separate player accounts, and are intended to operate autonomously. BP05 defines 500 authorised posts, but vacancies are not people. The synthetic workforce generator is for tests/sandbox scenarios only; production NPC dispatch loads existing personnel and active unit memberships, excludes the player-bound person, and respects BP08 unit availability. The opening disposable establishment currently has 500 vacant posts and no active memberships, so it correctly has no dispatch-ready units. The opening 500-person police population cohort has not yet been provisioned as BP06 personnel service records; the PKG-001 disposable fixture has zero active personnel service rows. See [single-player NPC world architecture](docs/implementation/single-player-npc-world.md).

## NPC-led police dispatch

The NPC workforce now has a gameplay dispatch layer. Given an incident, the
simulator chooses a suitable available unit, assembles its crew from the
current NPC shift, selects a crew lead and tracks the deployment through
responding, on-scene, busy, returning and available. Specialist units are
preferred when their domain matches; general patrol can cover general
response. The player does not enter officer IDs or manage crew membership.
The console also exposes a priority-ordered autonomous dispatch tick. It is
connected to BP37's authoritative recurring tick scheduler through
`runtime/npc_dispatch_scheduler.py`: `register_npc_dispatch_schedule()` installs
the police owner handler and recurring schedule. The scheduler invokes dispatch
on due world ticks without a player command; unserviceable incidents remain
queued. The game-session host must register this schedule when it composes the
NPC dispatch world and continue running the shared tick scheduler. This is an in-memory gameplay layer, not a production Neon
write or a claim that persistent staffing is complete. See
[the NPC world design](docs/implementation/single-player-npc-world.md).

## Player-operated NPC dispatch commands

The NPC dispatch simulator is now reachable through the player command
interface. Use `dispatch` to view the NPC incident queue and units, or
`dispatch assign <incident-id>` to let NPC dispatch choose a suitable unit
and crew. Deployment progress can be advanced with `dispatch arrive`,
`dispatch begin`, `dispatch finish`, `dispatch clear`,
`dispatch stand_down` and `dispatch available`, each followed by the
deployment ID. The player never enters personnel or membership IDs. The
simulator is currently in-memory; durable workforce persistence is still a
separate future step.

## Canonical NPC workforce source

The NPC dispatch factory now loads existing active personnel and current primary
unit memberships from BP05–BP08 PostgreSQL records using read-only queries. It
excludes the person bound to the human player and does not create staff from
vacant posts. Personnel without a current post/unit membership remain
unassigned; BP08's current unit status is authoritative. The current opening
fixture has 500 vacant posts and no memberships, so no dispatch-ready crew is
fabricated. The roster and deployments remain in-memory gameplay state; the
factory does not write personnel, membership or deployment rows to Neon.

## NPC shift and live-source validation

The synthetic workforce helper preserves sworn, civilian and mixed post types
and distributes test actors across four shifts. Production shift assignment
distributes existing canonical personnel identities; it never multiplies them.
The disposable PostgreSQL integration test now verifies the actual opening
boundary: 500 authorised posts remain vacant, no career appointments or unit
memberships exist, and the adapter does not invent NPCs or dispatch assignments.
This is read-only source integration and does not persist NPC personnel or
deployments to production.

## Business naming rebuild — 2026-11-26

The SW-UNS business-name generator changes are now on `main`. The registry build completed successfully and generated 10,000 businesses with 20,000 public trading/legal names; its generator regression suite passed, and the refreshed registry was committed in [`eae9f7d`](https://github.com/Joshuaogri/saltwater/commit/eae9f7d58f7a04872d735d7966cba353f3d3b6aa). The PostgreSQL reservation run [45852648985](https://github.com/Joshuaogri/saltwater/actions/runs/45852648985) used the preceding source commit and therefore the preceding generated registry: it reported three near-duplicate pairs in that stale input. That failure does not validate or invalidate the newly generated file. A fresh PostgreSQL acceptance run against commit `eae9f7d` is still required before the 20,000 persistent name reservations can be accepted. No production Neon write or persistent name reservation was made.

## BP12 incident operations service — 2026-11-26

The first officer-facing BP12 incident operations service is implemented on `main` in [`runtime/bp12_incident_service.py`](runtime/bp12_incident_service.py). It provides an audited, officer-only open-incident queue, incident inspection with ordered location history, and incident creation through the existing canonical `sw_incident.create_incident` function. Actor attribution comes from the verified officer session; default-deny grants and audit failure prevent protected database actions. Adapter tests are included in PKG-001 CI. This is a usable incident-service foundation, not a claim that CAD/dispatch is complete: BP11 dispatch assignment and its BP08 unit/deployment integration are the next operational build. No production Neon writes or permission grants were made. See [BP12 Incident Operations Service](docs/implementation/BP12-incident-operations-service.md).

## BP11 dispatcher board — 2026-11-26

The first BP11 dispatcher board is implemented on `main` in [`runtime/bp11_dispatch_board.py`](runtime/bp11_dispatch_board.py). It provides an audited officer-only queue over BP12's canonical active incidents and reads BP08's unit-readiness projection, including capability and ineligibility reasons. It is read-only and does not claim dispatch or deployment. BP08 currently reports `dispatch_eligible=false` while BP09 resource readiness is not integrated; the board surfaces that truth rather than inventing available units. Tests are included in PKG-001 CI. See [BP11 Dispatch Board](docs/implementation/BP11-dispatch-board.md).

### BP11 deployment creation and crew assignment — 2026-11-26

Added proposal `0032_bp11_authorised_deployment_creation.sql` and the officer-authorised `PostgresDispatchCreationService`. Creation is atomic and binds an incident, one existing dispatchable unit, and an explicit list of current unit-membership IDs. The database rejects incidents outside ASSESSED/ALLOCATED, inactive or non-dispatchable units, units not marked dispatch-eligible with verified resource readiness, insufficient/inactive crew, duplicate membership IDs, and units already carrying an active deployment. Successful creation records BP35 event intake, BP08 deployment and append-only authorisation history, plus the selected crew membership links. Added PostgreSQL adapter support, dispatcher-console delegation, tests and disposable PostgreSQL acceptance. The current seed has no memberships or eligible units, so the new guardrails correctly prevent a live deployment until staffing, availability and resources are genuinely recorded. No production Neon writes or grants were made.

### BP11 dispatcher console — 2026-11-26

Added `runtime/bp11_dispatcher_console.py` to compose the audited BP11 incident queue, BP08 unit-readiness board and authorised deployment lifecycle service behind one officer-facing console boundary. The console renders open incidents, dispatchable unit profiles, eligibility and readiness reasons, and delegates lifecycle transitions without accepting credentials from player-entered command text. Added the `dispatch` player command, canonical command-catalogue entry, player-interface tests and dedicated console tests. The board view remains read-only; dispatch mutations still require the separate authorised lifecycle command path and an existing deployment. New deployment creation and live unit assignment are not yet implemented. CI includes the console regression suite. No production Neon writes or grants were made.

### BP11 PostgreSQL deployment writer — 2026-11-26

Added proposal `0031_bp11_dispatch_lifecycle_writer.sql`, which provides an atomic compare-and-transition function over the existing BP08 `unit_deployment` and append-only `unit_deployment_event` records. It validates allowed state transitions, locks the deployment row, uses BP35 event intake with idempotency, records verified officer attribution and source/reason provenance, and returns the resulting deployment/event identifiers. Added `runtime/postgres_deployment_port.py` as the concrete adapter consumed by BP11 orchestration, plus adapter and disposable-schema acceptance tests. CI now applies the proposal only to disposable PostgreSQL and checks its contract. This adds a real persistence path for transitions; it does not yet create new deployments or expose the dispatcher console. Production Neon remains untouched.

### BP11 dispatch lifecycle orchestration — 2026-11-26

Added an officer-authorised dispatch lifecycle command service over the canonical BP08 deployment port. It supports issue, acknowledge, refusal, cancellation, reassignment, mobilisation, start, completion and stand-down, with explicit state-transition validation, stale-state rejection, command idempotency metadata, source provenance and verified active-officer attribution. The BP08 port remains responsible for atomic persistence, BP35 event creation, append-only BP08 deployment history and transactionality; no parallel assignment store was introduced. Added lifecycle tests and included them in PKG-001. This is the command orchestration boundary; the concrete PostgreSQL BP08 command writer and dispatcher/player UI wiring remain subsequent integration work. No production Neon writes or live unit deployments were made.

### BP09 resource readiness service — 2026-11-26

Added an officer-authorised, read-only BP09 service for unit resource readiness and per-model inventory. It reports required, allocated and serviceable quantities from the canonical resource allocation and asset records; it does not allocate equipment or mutate asset state. The service preserves default-deny access and durable audit integration through the existing authorisation boundary. Added focused tests for readiness summaries, inventory counts, denied/player access, unknown units and invalid identifiers. BP09's initial catalogue and resource-readiness schema acceptance already passes in PKG-001; the new service is now included in the Python workflow. The BP11 snapshot test fixture was also corrected to provide separate result sets for incident and unit queries. No production Neon writes or resource allocations were made.

## Latest verified delivery — 2026-11-26

The **full BP04 division is not yet complete**. An earlier README entry reported 14 BP04 source archives deployed in production and a 41,525,248-byte live database. A direct read-only check of the connected production Neon branch on 2026-11-26 does not confirm that report: the live `neondb` currently has only five application tables (three `sw_core`, two `sw_ops`), only migration versions 1 and 2 in `sw_ops.schema_migration`, and measures 9,781,248 bytes. Neither `sw_property` nor `sw_geo` exists. Treat the earlier BP04 archive-deployment and 41,525,248-byte claims as stale/unverified until reconciled against this live database. No production writes were made. The property/address/business lookup API is connected to authenticated player commands (`find` and `inspect`) and the ChatGPT tool boundary. A separate officer-only adapter remains default-deny until policy grants are provisioned. BP02 now has 420 stable parcel design IDs and 420 stable address design IDs (SWP/SWA), with all 420 property/address relationships reconciled. The geometric frontage check found 415 source-road matches, 3 conflicts and 2 parcels without boundary frontage. Follow-up review now incorporates the full direct-connector audit and road-network topology: the three conflicts each have one unique parcel frontage road association (`SWR-H17` twice, `SWR-H01` once), while the two bridge properties each have two geometrically feasible, property-contained connector candidates to a public bridge connected to public streets. These are design-geometry dispositions, not verified entrances or operational access. The original source-road values remain preserved; no canonical address or operational access point has been promoted. The raw 420-address review queue retains its initial 5 P1, 33 P2 and 382 P3 triage classifications; the revised full BP02 acceptance audit passed in [run 45831361588](https://github.com/Joshuaogri/saltwater/actions/runs/45831361588): all 12 structural checks and all six geometry/access layers passed, all five exceptions have resolved design-geometry dispositions, and zero address-road/access exceptions remain unresolved. The raw queue's 5 P1/33 P2/382 P3 labels are original triage priorities, not the final evidence-based exception status. The full BP04/BP02 integration passed 120 tests in [run 45688271976](https://github.com/Joshuaogri/saltwater/actions/runs/45688271976). No addresses/access points were operationally approved and no Neon writes were made. Full division acceptance remains blocked by operational geography approval, canonical address/access promotion, unprovisioned access grants, remaining police-service integrations and cross-register acceptance; see [BP04 full acceptance audit](docs/implementation/test-evidence/BP04-full-acceptance-audit-2026-11-25.md) and [player/police/geography integration](docs/implementation/BP04-player-police-geography-integration.md). This status supersedes older BP04 production-pending statements elsewhere in this README.


The BP04-to-BP02 reconciliation now emits a deterministic 420-address placement review register (`runtime/bp02_address_review_register.py`). It preserves all source road references, joins parcel-frontage and building-access evidence, and classifies the five P1 frontage/address exceptions, 33 P2 no-building-only cases and 382 P3 coherent candidates (36 no-building sites total, including three P1 conflicts). All 420 remain unapproved for operational use. The complete review-register and source reconciliation passed in the dedicated integration workflow; see [BP-02 address placement review register](docs/implementation/BP02-address-placement-review-register.md).

### BP02 full parcel/address/access structural acceptance — 2026-11-26

The revised full acceptance audit passed in [run 45831361588](https://github.com/Joshuaogri/saltwater/actions/runs/45831361588). It confirms all 12 structural assertions, zero failed checks across six geometry/access layers, 420/420 property-address links and zero unresolved address-road/access exceptions. The three source-road conflicts have unique frontage associations; both bridge cases have two property-contained connector candidates reaching a connected public bridge network. All source address values remain unchanged. The report's overall result is `STRUCTURAL_PASS_OPERATIONAL_RELEASE_BLOCKED`: SW-GEO-V1 remains a design baseline, canonical parcel/address records and operational access points have not been promoted, and bridge entrance engineering/operational validation remains outstanding. The 2,926 geometrically feasible direct connector candidates remain unreviewed; 22 obstructed direct lines remain blocked. The JSON report is published as a 45,291-byte CI artifact. No Neon writes or operational approvals were made.

### BP02 no-building-site review — 2026-11-26

### BP02 bridge connector engineering review — 2026-11-26

### BP02 identity lineage correction — 2026-11-26

### BP02 no-building / exception reconciliation — 2026-11-26

A dedicated read-only audit now cross-checks all no-building sites against the five frontage exceptions using explicit address, property, parcel and source-road identities. It counts no-building sites independently of primary review classifications, preserving the distinction between P1 frontage conflicts and P2 no-building review items. Acceptance expects 36 no-building properties, three overlapping frontage exceptions and two bridge exceptions on sites with building candidates. Tests and full acceptance workflow are pending. Inventory and Neon remain unchanged.


Bridge exception resolution now uses the explicit BP04 `property_id` from the validated address-to-property relationship rather than deriving a property identifier from an address-ID suffix. Missing identity fails closed. A regression test proves resolution with unrelated address/property identifiers. Full BP02 acceptance is running against this change; no property/address identities were changed and no Neon write or operational promotion occurred.


The four Customs Bridge/Harbour Bridge connector candidates have 2D geometric centreline evidence only. Width/corridor width are null; gradient has no elevation source; surface is unknown; drainage and vertical clearance are unassessed; access-control type is unknown; and no constructed entrance, legal access, traversability or emergency-egress evidence exists. Planar building/water clearance checks do not establish engineering clearance. All four remain `UNREVIEWED_GEOMETRIC_LINE_ONLY`; bridge-to-public-road connectivity remains a design-geometry finding, not operational approval. The required next evidence is site-specific survey and engineering assessment. BP02 remains `STRUCTURAL_PASS_OPERATIONAL_RELEASE_BLOCKED`; no inventory changes or Neon writes were made. See [BP-02 address placement review register](docs/implementation/BP02-address-placement-review-register.md).


The 36 property sites without generated building candidates have been reviewed against the Stage E generator. Their generated site state remains unknown and boundaries remain unverified. The generator can omit a building because no feasible footprint was found or because the generated land-use class is open space; the current evidence does not preserve a per-site reason code. These sites therefore remain **NO_BUILDING_CANDIDATE — CAUSE UNCLASSIFIED**. They are not assumed vacant, undeveloped or unoccupied, and no buildings or other property assets have been added. The frozen BP04 inventory is unchanged. This evidence review does not alter BP02's structural pass or operational-release blocker. See [BP-02 address placement review register](docs/implementation/BP02-address-placement-review-register.md). No Neon writes, canonical promotions, operational access approvals or grants were made.

### BP04-03 Stage E — detailed asset import verified — 2026-11-26

The complete Stage E disposable PostgreSQL workflow passed in [run 45736034489](https://github.com/Joshuaogri/saltwater/actions/runs/45736034489). All 35 steps succeeded, including detailed asset generation/import, same-manifest idempotency, full database acceptance, indexed representative lookups, storage measurement, backup/restore and artifact preservation.

The inventory contains 420 properties, 1,474 buildings, 27,730 premises, 180,733 units, 2,948 access points/connectors, 213,305 profiles, 421,768 physical measurements, 27,730 building levels, 17,688 building components, 83,190 premises rooms, 453,706 utility systems, 246,297 physical features, 251,773 condition assessments and 644,337 asset assertions. Manifest SHA-256: `f67e0493b580e01e2cb655c9fee4077dc0b6da8ca3f55880b9ac0843557d062c`.

The detailed import reported **1,525,071,872 bytes** of disposable database growth. Re-importing the identical manifest produced **0 bytes** of additional growth and 0 new relationships. The generated gzip manifest was 17,788,176 bytes; the retained GitHub Actions artifact ZIP is 6,466,165 bytes. These are CI/disposable measurements, not production Neon storage. **No Stage E data was written to Neon.**

Backup/restore verified 420 property assets, 180,733 units, 4,842 asset geometry candidates, 2,948 access connector candidates and the same manifest checksum. See [BP04-03 Stage E acceptance evidence](docs/implementation/test-evidence/BP04-03-stage-e-run-45736034489.md).

### BP04 gameplay lookup integrity — 2026-11-26

BP12 also exposes `sw_incident.incident_location_history`, an ordered read model joining immutable location rows to their source events. The officer-facing history reader requires a separate `bp12.incident.inspect.location.history` grant, audits access, rejects cross-incident rows and requires provenance fields. PostgreSQL acceptance verifies chronology and caller/address source separation.

`BP04IncidentLocationResolver` now resolves incident addresses under separate audited incident/address grants and hands reviewed candidates to BP12's `add_incident_location` writer. BP12 appends an `INCIDENT_LOCATION_ADDED` simulation event and immutable location record, retains caller/source and BP04 address provenance separately, validates runtime and incident state, and enforces idempotency. No spatial ID is inferred from an address. Regression tests cover authorisation, provenance and the writer handoff.

The officer-only lookup adapter also has regression coverage for revoked sessions and audit-store outages: revoked sessions are denied, and an otherwise authorised lookup is denied if its durable audit decision cannot be recorded. Dispatch/investigation address resolution remains a read-only, permission-checked address dossier operation; no operational access or canonical geography is inferred.

The lookup integrity checks now extend through the corporate/business register: parent-company references must resolve and remain acyclic; registered addresses must exist; each declared primary establishment must belong to that business; and establishment property/building/premises/unit/address links must agree across the physical hierarchy. Added regression tests for missing parent companies, self-parenting/cycles, mismatched primary establishments, missing registered addresses and conflicting establishment location links. This remains read-only and process-local; no Neon writes or operational geography promotion occur.

The archive-backed lookup now fails closed on dangling or inconsistent property/building/premises/unit/access-point relationships. It validates parent-child hierarchy across the detailed property stack before exposing records to gameplay, preventing an apparently valid address or establishment lookup from masking broken physical-location links. Regression coverage includes missing premises buildings, unit-to-premises conflicts and access-point-to-unit conflicts. This remains read-only and process-local; no Neon writes or operational geography promotion occur.

**Release boundary:** Stage E's detailed disposable database acceptance now passes, but generated physical detail and connector geometry remain unapproved candidates. BP04/BP02 gameplay integration and operational geography release gates remain open. This result does not authorise Neon deployment.

## Canonical constraints

- Country and city: **Saltwater**.
- One sovereign city-state; no external playable cities or territory.
- Maximum population: **10,000 living people total**, police included; opening baseline 9,000 residents + 500 police = 9,500, leaving 500 unused headroom.
- Primary experience: exceptionally detailed, permanently text-first simulation; maps and selected graphics are optional.
- Primary simulation: the police service and its operations, supported by a credible, interconnected society.
- Persistent database: Neon PostgreSQL.
- Source, migrations and documentation: this GitHub repository.
- Player interface and AI partner: ChatGPT.

## Development principles

- Preserve meaningful detail and exact recoverability while minimising storage use; the simulation is text-first and narrative may be extensive.
- Prefer the smallest lossless representation (compact JSON, short keys/IDs/enums, normalisation, references and event/delta records); compress structure, never meaning.
- Avoid every unnecessary byte: duplicate payloads, repeated boilerplate, derivable fields, needless indexes/snapshots and oversized database blobs.
- HARD GATE: before every Neon migration, schema change, seed/import, bulk write or upload, calculate and show expected incremental bytes/MB, assumptions/range, current baseline and projected total; wait for explicit user approval. If the estimate is not credible, do not deploy—benchmark first.
- After approval, measure actual database/table/index/TOAST growth and compare it with the estimate.
- Normalise shared facts and reference them rather than duplicating them.
- Use compact identifiers where useful; never sacrifice human-readable records or provenance.
- Record meaningful state changes and chronology without indiscriminate full snapshots.
- Measure actual database growth after each approved deployment; report actual delta against the pre-deployment estimate.
- Do not upload simulation seed data until the schema, validation and storage baseline are ready.
- Never commit credentials. The Neon connection string belongs in a protected secret named `DATABASE_URL`.

## Current database-integrity implementation

BP38-01 is implemented on `main`; disposable PostgreSQL validation passed in [run 45428332686](https://github.com/Joshuaogri/saltwater/actions/runs/45428332686). BP38-02's independent PostgreSQL 18 replay and live baseline comparison passed in [run 45437263676](https://github.com/Joshuaogri/saltwater/actions/runs/45437263676). The guarded version-1 checksum adoption was separately approved, executed and verified. Migration 0002 was then separately approved and applied to Neon production on 2026-11-24. Both constraints and the fingerprint column are present; the authoritative ledger now contains versions 1 and 2 with exact source checksums, and version 2 has a recorded live schema fingerprint. The new [read-only Neon migration-ledger workflow](.github/workflows/neon-migration-ledger-readonly.yml) ran the committed Python migration runner against production with server-enforced read-only mode; checksum and live fingerprint verification passed in [run 45444735686](https://github.com/Joshuaogri/saltwater/actions/runs/45444735686). The migration source is 726 bytes; database size remained 9,306,112 bytes (0-byte measured delta). See [BP38-01 migration 0002 execution evidence](docs/implementation/test-evidence/BP38-01-run-0002.md). The push-triggered Neon production deployment workflow remains disabled; the new workflow is read-only and never applies migrations.

Package: [BP38-01 — Database Integrity and Migration Foundation](docs/implementation/approval-packages/BP38-01-database-integrity-and-migration-foundation.md). [Read-only Neon legacy-baseline verification](docs/implementation/test-evidence/BP38-01-legacy-baseline-read-only-verification.md).


## Repository layout

- `db/migrations/`: ordered PostgreSQL migrations.
- `docs/architecture/`: architecture decisions and storage design.
- `docs/operations/`: operational procedures and measurement records.
- `docs/implementation/`: dependency-led implementation sequence and delivery gates.
- `.github/workflows/`: automated checks.

## Current status

The **platform foundation and BP04 compressed source archive release are deployed**. The full police simulation runtime and several domain interfaces remain in development.

- Neon project: Saltwater (`misty-breeze-20463094`), production branch `br-still-cloud-bdvaw8u4`, database `neondb`.
- Production migration ledger contains versions 1–12; BP04 migrations 0003–0012 are applied.
- BP04 production archive release passed in [workflow run 45675735246](https://github.com/Joshuaogri/saltwater/actions/runs/45675735246). It stores 14 compressed datasets, 105 collections and 1,950,923 source records (29,434,820 compressed bytes); zero typed static source rows were materialised.
- Read-only Neon verification on 2026-11-25 measured `pg_database_size` at **41,525,248 bytes (41.53 MB / 39.60 MiB)**, an increase of **32,219,136 bytes (32.22 MB)** over the 9,306,112-byte pre-BP04 baseline.
- The BP04 schema contains 92 base tables. Archive/provenance ledgers contain the deployed source package; the other static domain tables remain empty by design under the archive-only storage model.
- BP04's full division acceptance audit **has not passed**. The process-local lookup API is integrated with authenticated player commands and ChatGPT's bounded tool contract. The separate police adapter requires an active officer principal, live policy grant and durable audit; no production grants have been provisioned, so it remains default-deny. BP02 now supplies 420/420 stable parcel design IDs and 420/420 stable address design IDs, reconciled to all property and road/district/neighbourhood references. Operationally approved canonical parcel/address identities remain zero because geometry, frontage and address placement have not passed the operational geography release gate. The latest frontage audit found 415 road matches, 3 road conflicts and 2 parcels with no frontage candidate; see the integration record for the exact IDs. See [lookup design](docs/implementation/BP04-gameplay-lookup.md), [player/police/geography integration](docs/implementation/BP04-player-police-geography-integration.md) and [full acceptance audit](docs/implementation/test-evidence/BP04-full-acceptance-audit-2026-11-25.md).
- No resident, police-personnel, case or evidence production seed records have been loaded. The 10,000-person cap remains binding. Production simulation seeding beyond the approved BP04 archive release remains blocked.
- The storage/write gate remains mandatory for every future Neon write: measure the current baseline, estimate incremental bytes and MB/MiB with assumptions/range, show the projected total and wait for explicit user approval.

Provider-reported logical-size metadata is a different measurement from PostgreSQL `pg_database_size`; do not compare or substitute the two without an explicit metric definition.

## Latest canon decisions — 2026-11-24

- Adopted [SW-CANON-001 — Population Scope and Foundational Geography](docs/blueprint/decisions/SW-CANON-001-population-scope-and-foundational-geography.md).
- Population cap now has a closed distinct-person counting formula: usual residents ∪ persons physically present ∪ active Saltwater Police Service members; one person ID counts once. Opening target: 9,000 civilian residents + 500 police personnel = 9,500 unique people, 500 shared headroom.
- Foundational geography is fixed: one contiguous coastal island city-state, 12 km × 9 km fictional local grid, eastern harbour, eight districts and 24 neighbourhoods. Detailed map construction and routing validation remain implementation work.
- BP-02 and BP-03 updated; SW-DB-001 now references the adopted canon. BP04 now has a 10,000-business source registry baseline; full registry and gameplay acceptance remains open.
- The approved BP38-01 migration writes are complete; no operational geography import or simulation seed data has been authorised or performed.

## BP04-03 — citywide terrain/obstacle survey coverage grid

SW-TERRAIN-SURVEY-GRID-001 divides the fictional 12 km × 9 km city planning extent into 432 500 m coverage cells. Each cell carries district/neighbourhood lineage, generated property/building candidate references, road/route candidate coverage, terrain/water intersections and explicit evidence gaps for elevation and physical obstacles. Cells are coverage-planning units, not parcels or physical assets. No terrain or obstacle facts, survey priority, passability or access are inferred. Workflow: .github/workflows/bp04-03-terrain-obstacle-survey-coverage-grid.yml.

## BP04-03 — detailed terrain and physical-obstacle register

The geometry-derived SW-TERRAIN-OBSTACLE-DETAIL-001 register (runtime/terrain_obstacle_detail_register.py) preserves source terrain polygons and adds planar area/perimeter, bounding boxes, centroids, boundary rings/edges, edge lengths/bearings, district/neighbourhood overlays and lineage-linked route-centreline intersections. Obstacle classes remain separately inventoried; classes without supplied source records are marked as coverage gaps, never asserted absent. No elevation, gradient, material, condition, passability, legal access or egress is inferred. Workflow: .github/workflows/bp04-03-terrain-obstacle-detail-register.yml. Generated artifact is read-only and is not an operational terrain/obstacle layer.

## BP04-03 — terrain, elevation and physical-obstacle source model

The read-only source model [SW-TERRAIN-OBSTACLE-001](runtime/terrain_obstacle_source_model.py) inventories terrain and physical-obstacle evidence without inventing missing facts. It recognises elevation surfaces, contours, spot elevations, terrain features, retaining structures, walls, fences, gates, drainage structures and natural/other barriers. Current SW-GEO-V1 supplies one terrain polygon (Central-Western Ridge) and no elevation surfaces, contours, spot elevations or mapped physical-obstacle records. This is a source-coverage statement, not proof that absent features do not exist. Elevation, vertical datum, gradient, obstacle dimensions/material/condition, traversal, accessibility, legal access and emergency egress remain null, unknown or not assessed. The 47 existing route-centreline/ridge intersections remain contextual only. No operational terrain/obstacle records, route approvals or Neon writes are created. Regression workflow: [BP04-03 Terrain and Physical Obstacle Source Inventory](.github/workflows/bp04-03-terrain-obstacle-source-inventory.yml).

## Detailed map and road network — SW-GEO-V1

- [Open the master Saltwater map (SVG)](docs/maps/saltwater-master-map-v1.svg)
- [Machine-readable geography and routable road graph](data/geography/saltwater-geography-v1.json)
- [Map register, network specification and limitations](docs/maps/README.md)

The initial map baseline contains 8 districts, 24 neighbourhoods, 42 named roads, 367 junction nodes, 685 connected road/bridge segments and 5 named route definitions. It uses the fictional `SW-LOCAL-01` metre grid. Structural graph checks passed at generation time; parcel/address/building coverage and full BP-02 operational acceptance remain outstanding. This is planning-grade fictional geometry, not survey-grade, and no Neon production data was changed.


## Core universal naming standard — SW-UNS-001

**Adopted 2026-11-24 as a core, mandatory Saltwater foundation.** The standard applies to all 44 blueprint divisions and every named entity: people, roads, places, properties, buildings, businesses, organisations, police units, vehicles, equipment and operational records. One shared registry must enforce permanent entity IDs, globally unique canonical names, normalization, exact/near-duplicate checks, reservations, concurrency safety, aliases and immutable historical name records. The sole user-approved exception allows the sovereign territory and playable city to both retain the exact name Saltwater, with separate IDs; no other entity may use that name. Domain-specific naming vocabularies are allowed; domain-specific bypasses or competing registries are not.

- [Read SW-UNS-001 — Universal Naming Standard](docs/blueprint/decisions/SW-UNS-001-universal-naming-standard.md)
- Existing adopted names must be preserved and registered before new names are generated, including the eight districts, 24 neighbourhoods and 42 named SW-GEO-V1 roads.
- Policy adoption is complete. SW-NAM-001 is approved; core disposable SQL/Python/PostgreSQL acceptance passed in runs `45409845359` and `45410340222`. Final storage-detail run `45411243093` passed. Populated registry relations total 12,279,808 bytes (4,546,560 heap; 7,643,136 indexes; 90,112 TOAST/auxiliary). No Neon production changes were made or authorised.

### Universal naming implementation

The adopted core naming policy is being implemented through [SW-NAM-001 — Universal Naming Registry, Generator and Enforcement](docs/implementation/approval-packages/SW-NAM-001-universal-naming-registry-generator-and-enforcement.md). Committed slices include disposable proposal `0009`, Python normalization/registry and transactional PostgreSQL adapter, deterministic candidate generation, geography/person adapters, dry-run canon inventory, immutable generator manifests, SQL/Python/concurrency/rollback/restore tests and disposable PostgreSQL CI. **Core regression and disposable identity mapping are verified**: full Python and PostgreSQL jobs passed in [run 45441551968](https://github.com/Joshuaogri/saltwater/actions/runs/45441551968), including all 100 geography identity-map entries and naming reservations, 10,000-person cap boundary, access controls, checkpoint-manifest capture and backup/restore. The full 10,000-person fixture grew its disposable database by 2,334,720 bytes (2.226562 MiB); full database size was 32,250,903 bytes. At the full fixture stage, 10,111 name reservations occupied 8,642,560 bytes total (854.77 bytes/reservation). Detailed heap/index/TOAST figures and the restore manifest are in [SW-NAM-001 run evidence](docs/implementation/test-evidence/SW-NAM-001-run-0001.md). The checkpoint validator intentionally remains partial: business-minimum, player-absence-freeze and permission/hidden-truth gates were not executed. BP-04 and other operational entity adapters remain NOT CONNECTED until their authoritative schemas exist. The 100-entry identity map is validated only in disposable PostgreSQL; no operational canon import, production spatial-ID allocation or Neon seed/write occurred. See [SW-NAM-001 integration coverage audit 0001](docs/implementation/test-evidence/SW-NAM-001-integration-coverage-audit-0001.md) for connected/NOT CONNECTED domain coverage.


## BP40-02 — stable player command catalogue and typed parser

The user approved BP40-02 on 2026-11-24. The implementation is committed directly to `main`: [canonical catalogue/parser](runtime/player_commands.py), [player command interface](runtime/player_interface.py), authorization gateway, trusted host adapter and ChatGPT tool handler all use the same parser and command metadata. The registry contains the existing fourteen command forms only; no new police-domain capability or permission was added. Typed parse failures distinguish empty, malformed, unknown, missing-argument, invalid-argument-count and invalid-value input. Help and [machine-readable tool schema](docs/integration/player-command-tool.schema.json) expose the same contract. The full Python regression, dedicated parser acceptance, full disposable PostgreSQL regression and database migration validation passed; see [BP40-02 run 0001 evidence](docs/implementation/test-evidence/BP40-02-run-0001.md). The registry and parse-result structures are immutable. No Neon production change occurred.


## SW-DB-001 — canonical world provisioning (approved; disposable implementation verified)

The user approved SW-DB-001 on 2026-11-24 for GitHub main development and disposable PostgreSQL testing only. [Proposal 0010](db/proposals/0010_canonical_world_provisioning.sql) extends the existing universal naming registry with a business adapter and adds business-owned identity/lifecycle history plus immutable provisioning-batch metadata. The deterministic [opening fixture](tests/pkg001/sw_db_001_world_fixture.sql) targets 9,000 resident-cohort people + 500 police-subset-cohort people = 9,500 distinct living identities, leaving 500 headroom, and 10,000 distinct named businesses. The police subset and business category/legal-form/staff-band variety are test-only labels; no police appointments or detailed geography are fabricated, and business sites remain unassigned. Generator v2 creates deterministic pronounceable pseudowords, while the immutable batch manifest records source revision and separate person/business SHA-256 content checksums. [Manifest](data/fixtures/sw-db-001-opening-manifest.json) and [candidate model](docs/architecture/SW-DB-001-canonical-world-data-model.md) document the boundaries. The [dedicated disposable workflow](.github/workflows/sw-db-001-disposable.yml) passed both Python and PostgreSQL 16 jobs in [run 45456851773](https://github.com/Joshuaogri/saltwater/actions/runs/45456851773). It verified the 9,500-person/10,000-business fixture, 10,000 unique business names, 0-byte same-manifest repeat delta, both restored content checksums, backup/restore, 9,999-person concurrent final-slot admission, exact 10,000 cap and world tick 0. Proposal 0010 schema growth was 278,528 bytes; the opening fixture added 39,632,896 bytes (37.796875 MiB) in 169.295 seconds (115.18 fixture rows/second). Person-domain relations totalled 5,259,264 bytes (553.61 bytes/person); business-domain relations 4,399,104 bytes (439.91 bytes/business). Full measurements and limitations are recorded in [SW-DB-001 run 0001 evidence](docs/implementation/test-evidence/SW-DB-001-run-0001.md). This is disposable test evidence only: no Neon production connection, migration, seed, import, upload or configuration change occurred; production write authority remains NONE.


## BP04 — physical built-world records

[BP04-01 — Property, Building, Premises, Unit and Access-Point Identity Foundation](docs/implementation/approval-packages/BP04-01-property-premises-identity-foundation.md) is approved, implemented and verified on `main`. The corrected disposable PostgreSQL 16 workflow [run 45477359265](https://github.com/Joshuaogri/saltwater/actions/runs/45477359265) passed both Python regression and full disposable PostgreSQL acceptance. The corrected acceptance checks all three access-point creation-history rows, including the deliberately unnamed access point.

**BP04-02 — Deep Physical Asset and Space Profiles** is approved and implemented as a disposable-only candidate migration `0012_bp04_physical_asset_detail_profiles.sql`. It adds versioned typed profiles for all five physical identity types; provenance-rich measurements; building levels/components; premises rooms; utility systems; physical features; element-level condition assessments; defects; and knowledge-state assertions. Profiles and child records are append-only; revisions are additional effective-dated records. Its acceptance tests and workflow integration are committed on `main`; full Python regression and disposable PostgreSQL 16 acceptance passed in [run 45478587738](https://github.com/Joshuaogri/saltwater/actions/runs/45478587738). The completed run applied proposals 0002–0012, measured migration-only schema growth, provisioned and measured the deterministic fixture, passed BP04-01 and BP04-02 SQL acceptance, verified idempotency, query latency and backup/restore, passed the concurrent final-slot population-cap test, and completed final SW-DB-001 reconciliation. Detailed byte-level step output was not exposed by the available workflow API response, so no new exact BP04-02 storage figure is asserted here. See [BP04-02 run 0001 evidence](docs/implementation/test-evidence/BP04-02-run-0001.md).

**Mandatory physical-record depth:** property, building, premises, unit and access point records must be extensive, structured and individually meaningful. Do not stop at IDs and names. Capture applicable classification/use, physical form, dimensions and measurement basis, floor/space structure, materials/components, utilities/services, facilities, condition by element, defects/hazards, accessibility, security/physical controls, access modes/restrictions, capacity/suitability, lifecycle and inspection/maintenance history. Every material fact must retain source/provenance, confidence/quality and recorded/effective chronology. Unknown, not assessed, not applicable, not present and measured zero must remain distinct. Use typed, normalised child records; do not collapse detail into unstructured notes or one oversized JSON field. Do not invent missing facts or false precision.

The detailed profile model does **not** populate the actual Saltwater property inventory, ownership/tenancy/occupancy, or business operators. No actual Saltwater property/building/premises/unit/access-point population has been seeded. BP04-02 passed full Python and disposable PostgreSQL 16 acceptance in [run 45478587738](https://github.com/Joshuaogri/saltwater/actions/runs/45478587738); see [BP04-02 run evidence](docs/implementation/test-evidence/BP04-02-run-0001.md). [BP04-03 — City Physical Inventory and Geography-Linked Population](docs/implementation/approval-packages/BP04-03-city-physical-inventory-and-geography-linked-population.md) was approved on 2026-11-24 for GitHub `main` implementation and disposable PostgreSQL testing only. Stage A's read-only geography audit is committed in [runtime/geography_readiness.py](runtime/geography_readiness.py), with regression tests in [test_geography_readiness.py](tests/pkg001/test_geography_readiness.py) and a dedicated [GitHub Actions workflow](.github/workflows/bp04-03-geography-readiness.yml). The audit checks the committed district/neighbourhood/road/network structure and keeps the 100 resolved stable source-to-entity_code mappings, absent parcel/address fabric and absent footprints/entrances explicit. It cannot approve BP-02 geography. The audit passed in [run 45480493889](https://github.com/Joshuaogri/saltwater/actions/runs/45480493889): 28/28 checks passed; all 100 source identities are mapped one-to-one to stable entity_code values; no spatial IDs were fabricated or assigned. See [BP04-03 Stage A run evidence](docs/implementation/test-evidence/BP04-03-stage-a-run-0001.md) and the [100-record reconciliation register](data/geography/bp04-03-stage-a-source-spatial-reconciliation-v1.json). Stage A structural audit is verified; all 100 source identity mappings are resolved to stable entity_code values. Database-specific spatial_id surrogates are resolved by entity_code at materialisation. Stage B now has a BP-02-owned candidate schema in [proposal 0013](db/proposals/0013_bp02_parcel_address_candidate.sql), with parcel profiles, structured address locators/frontage, parcel lineage, address aliases, kind guards, checksum verification and append-only controls. Its Python and disposable PostgreSQL acceptance passed in [run 45481959712](https://github.com/Joshuaogri/saltwater/actions/runs/45481959712); schema-only growth was 294,912 bytes and the proposal source is 10,668 bytes. See [Stage B run evidence](docs/implementation/test-evidence/BP04-03-stage-b-schema-run-0001.md). The schema foundation is verified. Stage B now also has a deterministic [parcel/block candidate generator](runtime/parcel_candidate_generator.py), five regression tests and a dedicated [candidate workflow](.github/workflows/bp04-03-parcel-candidates.yml). Run [45482818681](https://github.com/Joshuaogri/saltwater/actions/runs/45482818681) passed: 396 block-scale candidates across all 24 neighbourhoods; 36 water-conflict cells excluded; 392 road-edge matches and 4 frontage-unresolved candidates. The generated artifact is 11,656 bytes compressed and has manifest SHA-256 `6afc12c8e27717523bb581057da8c936481b1950faa5703f52bb5e7560e8cba4`; see [Stage B candidate evidence](docs/implementation/test-evidence/BP04-03-stage-b-parcel-candidates-run-0001.md). These are 500m planning block candidates, not final cadastral parcels. The generator was refined to calculate exact water polygon-to-cell intersection area for the current single-ring SW-GEO-V1 water polygons (Sutherland–Hodgman clipping); unsupported holes/geometry fail closed. Refined [run 45483557867](https://github.com/Joshuaogri/saltwater/actions/runs/45483557867) passed all 7 tests, retained 396 candidates / 36 excluded water cells / 392 road-edge matches / 4 frontage-unresolved, and emitted manifest SHA-256 `4da7999ef7b5f98b3b1214096f11fbce633317ae38585ca231f6f8131c3c39bf`. Its artifact is 11,815 bytes compressed: [candidate artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45483557867/artifacts/14962966036). Evidence: [Stage B candidate run 0001](docs/implementation/test-evidence/BP04-03-stage-b-parcel-candidates-run-0001.md). The generator now also validates candidate containment and pairwise interior overlap: 432 source grid cells reconcile to 396 candidates plus 36 water-excluded cells; zero candidate overlaps and zero out-of-neighbourhood candidates. Eight Python tests passed in [run 45483804394](https://github.com/Joshuaogri/saltwater/actions/runs/45483804394). Latest manifest SHA-256 `83ec53dc09f51483110e1e564b82919d2da63a0f5c5adcd92b42e04bf508f85f`; artifact size 12,033 bytes compressed: [artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45483804394/artifacts/14962257890). This validates generated candidate rectangles only, not cadastral topology. The 15m road-reserve inset remains provisional; the unallocated area is not classified as road, public space or developable land. Road access, land-use capacity and full parcel topology remain. No spatial IDs or canonical addresses were assigned; all 100 source identities are resolved to stable entity_code values; database-specific spatial_id surrogates are looked up during materialisation. No database or Neon production write occurred.


BP04-03 Stage B now imports the 396 generated candidate parcels into disposable PostgreSQL 16 through [the guarded importer](runtime/parcel_candidate_importer.py). [Run 45484639045](https://github.com/Joshuaogri/saltwater/actions/runs/45484639045) passed: 396 candidate identities, 396 checksummed geometry versions and 396 parcel profiles; zero address identities; repeat import inserted zero rows and had 0-byte database growth. First import added 1,187,840 database bytes in the disposable CI database (739.125 ms); proposal 0013 schema growth was 294,912 bytes and its SQL source was 10,668 bytes. Full [ingestion evidence](docs/implementation/test-evidence/BP04-03-stage-b-disposable-ingestion-run-0001.md). These are candidate records only; no operational geography approval, canonical addresses, or Neon writes occurred.


BP04-03 Stage C road-centreline and road-reserve design is now resolved and verified in [run 45487528624](https://github.com/Joshuaogri/saltwater/actions/runs/45487528624). Both bridge lengths now reconcile to 2,019.804m from their stored geometry. Fictional canonical standard SW-RDS-V1 defines 18m local streets, 24m district connectors, 30m primary arterials and 24m bridges. Deterministic geometry generated all 685 segment corridor polygons; zero width or bridge-length exceptions remain. The 42-road, 685-segment, 367-node network remains connected with zero degree/membership/endpoint mismatches. Segment polygons intentionally overlap at junctions and must be dissolved before unique reserve-area calculations. The preserved road register is 23,915 compressed bytes ([artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45487528624/artifacts/14962764058)); [full evidence](docs/implementation/test-evidence/BP04-03-stage-c-road-centreline-audit-run-0001.md).


BP04-03 Stage C parcel coverage area reconciliation passed in [run 45486168411](https://github.com/Joshuaogri/saltwater/actions/runs/45486168411). The 24 neighbourhoods total 108,000,000 m² (432 grid cells); 396 candidate parcel interiors total 87,476,400 m²; exact water intersections in 36 excluded cells total 5,740,000 m². The 14,783,600 m² unallocated balance is decomposed into 11,523,600 m² of provisional 15m inset residual and 3,260,000 m² non-water area inside water-hit cell envelopes. Area balance delta: 0 m². These residuals remain unclassified, not assumed to be roads or developable land. The per-neighbourhood audit is retained as a 1,713-byte compressed [workflow artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45486168411/artifacts/14964432302). [Full evidence](docs/implementation/test-evidence/BP04-03-stage-c-parcel-coverage-area-run-0001.md).


BP04-03 Stage C road-reserve dissolve and neighbourhood-boundary reconciliation passed in [run 45488230508](https://github.com/Joshuaogri/saltwater/actions/runs/45488230508). The 685 segment corridor polygons dissolve into one connected road-reserve geometry of 7,057,146.032 m²; 140,804.555 m² of duplicate junction overlap is removed. The dissolved reserve lies entirely inside the city boundary. All 24 neighbourhood polygons exactly partition the 108,000,000 m² city: zero overlap, zero gap, zero outside area. Neighbourhood road-reserve allocations sum to 7,057,146.032 m² with a 0 m² difference. The topology artifact is 9,850 compressed bytes ([artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45488230508/artifacts/14964976654)). [Full evidence](docs/implementation/test-evidence/BP04-03-stage-c-road-centreline-audit-run-0001.md). Next: regenerate parcel candidates against the dissolved fictional road-reserve and water geometry, replacing the provisional 15m inset.


**BP04-03 Stage D geometry-derived parcel candidates — supersedes the earlier 396-cell / provisional 15m-inset candidate layer:** [Disposable PostgreSQL run 45490203072](https://github.com/Joshuaogri/saltwater/actions/runs/45490203072) and [candidate regression run 45490210942](https://github.com/Joshuaogri/saltwater/actions/runs/45490210942) passed. The generator now subtracts the actual dissolved SW-RDS-V1 road reserve and mapped water geometry from each 500m source lineage cell, then splits the remaining land into deterministic valid polygon components. It creates **420** parcel candidates; **418** have a geometric road-reserve edge-contact candidate. The 36 water-intersected cells are no longer excluded wholesale. Area reconciles exactly: 108,000,000.000 m² = 7,057,146.032 m² road reserve + 5,605,030.589 m² water outside road reserve + 95,337,823.379 m² candidate land; delta 0 m² across all 24 neighbourhoods. Candidate manifest: 28,513 compressed bytes ([artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45490203072/artifacts/14965647916)). Disposable PostgreSQL inserted 420 candidate identities, 420 geometry versions and 420 parcel profiles; first-import growth 1,081,344 bytes. Repeat import inserted zero rows and produced 0-byte growth. Zero canonical addresses were created. The first generic labels tripped SW-UNS-001 near-duplicate checks; deterministic unique fictional names now pass through the existing registry without bypassing it. [Full Stage D evidence](docs/implementation/test-evidence/BP04-03-stage-d-geometry-derived-parcel-candidates-run-0001.md). Next: detailed parcel dossier and boundary/frontage review before detailed property/building/premises/unit/access-point inventory. No Neon writes or operational geography activation occurred.


**BP04-03 Stage D detailed parcel dossiers and relationship layer completed:** [Run 45494991970](https://github.com/Joshuaogri/saltwater/actions/runs/45494991970) passed all eight Python suites (41 tests), disposable SQL acceptance, candidate import, dossier import and repeat-import idempotency. All 420 parcel candidates have measured dossiers (area, perimeter, compactness, centroid, representative point, bounds, ring counts, road frontage and water contact). Results: 418 parcels require frontage review; 2 have no road-edge contact; 1,374 parcel-to-road frontage relationships and unreviewed access-location candidates; 100 shared-boundary relationships; 32 water-adjacent parcels and 32 water relationships. These are candidate geometric relationships, not legal frontage, entrances, addresses or operational access points. The five-table append-only dossier schema is proposal 0014; source 10,311 bytes, disposable schema growth 368,640 bytes. First dossier import growth 1,859,584 bytes; repeat import 0 bytes. The 68,438-byte compressed dossier artifact is [preserved here](https://github.com/Joshuaogri/saltwater/actions/runs/45494991970/artifacts/14968720668). [Full evidence](docs/implementation/test-evidence/BP04-03-stage-d-parcel-dossiers-run-0001.md). Next: full-depth property, building, premises, unit and access-point inventory, with BP04-02 physical profiles and provenance. No Neon writes or operational addresses/access points were created.


**BP04-03 Stage E physical-asset candidate generation — first successful slice:** [Run 45502416189](https://github.com/Joshuaogri/saltwater/actions/runs/45502416189) passed seven regression tests and generated 420 property-site candidates, 384 contained building-footprint candidates, 1,327 floor-level premises, 15,199 units and 768 unreviewed building-boundary access-location candidates. 36 candidate properties have no building footprint and remain sites without fabricated structures. The 10,981,615-byte manifest is preserved as a 356,640-byte compressed [artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45502416189/artifacts/14970964187); SHA-256 `b710fcc3f5d08d24154ede08ebf99ec6a2f099a08c7f9c5d310c93ddb8aa30fe`. All five record classes have deterministic identities/names and provenance; geometry tests confirm each building footprint lies within its property candidate. This is candidate generation only: no asset records have yet been imported into PostgreSQL, and generated access points are not operational entrances. No addresses, operational spatial IDs, ownership, tenancy, occupancy or business assignments were created; all 100 source records resolve to stable entity_code values (100 resolved, 0 unresolved). Production spatial_id surrogates remain unassigned until activation and are looked up by entity_code. Full [Stage E evidence](docs/implementation/test-evidence/BP04-03-stage-e-physical-asset-candidates-run-0001.md). Next: complete BP04-02 profile and typed child-record depth, then disposable PostgreSQL schema/import/idempotency/storage/restore acceptance. No Neon production writes occurred.


**BP04-03 Stage E full physical-asset inventory — verified:** [Disposable PostgreSQL 16 run 45504985010](https://github.com/Joshuaogri/saltwater/actions/runs/45504985010) passed 15 Python tests, proposal 0015 migration, full import/SQL acceptance, repeat-import idempotency, query measurements and PostgreSQL 16 backup/restore. The hierarchy contains **420 property-site candidates, 384 building candidates, 1,327 premises, 15,199 units and 768 unreviewed access-location candidates**. All five identity classes have **18,098 typed BP04-02 profiles** and the inventory includes **181,915 detailed child records**: 34,624 measurements, 1,327 building levels, 4,608 components, 3,981 room allocations, 37,979 utility records, 21,417 features, 22,533 condition assessments and 55,446 knowledge-state assertions. There are no fabricated defect records. Proposal 0015 source SQL is 9,238 bytes and disposable schema growth 303,104 bytes. First asset import growth was 130,441,216 bytes; repeat import inserted zero records and grew 0 bytes. Full compressed inventory artifact: 1,523,057 bytes ([artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45504985010/artifacts/14971474446)). [Full Stage E evidence](docs/implementation/test-evidence/BP04-03-stage-e-physical-asset-inventory-run-0001.md).

All records remain generated, non-operational candidates. No canonical addresses, operational spatial IDs, confirmed entrances, ownership, tenancy, occupancy or business assignments were created. All 100 source records now map to stable entity_code values; database spatial_id is generated per database and looked up by entity_code. No Neon production connection, migration, seed, upload or activation occurred. Next dependency is BP-02 geography approval/versioning and source-to-spatial reconciliation before operational parcel/address/entrance identity creation.


## Geography source-identity reconciliation correction (2026-11-24)

The earlier statement that 100 source-to-spatial mappings remained unresolved is superseded. All **100 source records now map one-to-one to stable `sw_geo.entity.entity_code` values**: 8 districts, 24 neighbourhoods, 18 landmarks, 5 routes, 3 geography zones and 42 roads. The exact source record, entity type/kind, canonical name and parent are checked against SW-GEO-V1 by `runtime/geography_identity_reconciliation.py`; the readiness workflow runs regression tests for full coverage, duplicate IDs, incorrect parents and missing records. The reconciliation register now reports 100 resolved and 0 unresolved source-identity mappings.

PostgreSQL `spatial_id` is a GENERATED ALWAYS AS IDENTITY surrogate, so its integer is database-specific and must be looked up using the stable `entity_code` in each database. The portable source manifest intentionally does not freeze a disposable integer as a production ID. This correction resolves source-to-identity mapping; it does **not** approve SW-GEO-V1 for operational seeding, create parcel/address/entrance geometry, or authorize Neon writes. Those separate geography quality and activation gates remain.


**Disposable database materialisation proof:** the existing PKG-001 geography identity SQL fixture has now materialised all 100 `sw_geo.entity` rows and their database-generated `spatial_id` values, with all 100 version/parent/name relationships and naming-registry activations accepted. The materialisation step passed in [workflow run 45508321133](https://github.com/Joshuaogri/saltwater/actions/runs/45508321133). These integers belong to that disposable database only; production IDs remain unassigned and will be generated/looked up by `entity_code` when the operational geography version is activated.


### SW-GEO-V1 geometric QA extension (read-only)

A dedicated standard-library geometry and routing audit is added at `runtime/geography_geometry_audit.py`, with regression coverage in `tests/pkg001/test_geography_geometry_audit.py`. It checks polygon ring validity/self-intersection, point containment, neighbourhood-to-district containment, neighbourhood interior overlap and area balance, segment geometry against node coordinates and declared lengths, city-boundary containment, graph degree/connectivity, and route segment sequencing. The existing BP04-03 geography-readiness workflow runs this audit on relevant `main` changes. The audit is deliberately read-only and always reports operational seed eligibility as false; it does not approve SW-GEO-V1, validate cadastral parcels, establish legal frontage/access, or authorize Neon writes. Acceptance passed in [run 45510749489](https://github.com/Joshuaogri/saltwater/actions/runs/45510749489): 18 Python tests (4 structural, 9 geometric/routing, 5 identity) passed; the structural audit passed 28/28 checks with 100 resolved/0 unresolved source identities; the geometric/routing audit passed 10/10 checks with zero failed checks. City and neighbourhood areas both measure 108,000,000 m²; all 24 neighbourhoods are contained by their assigned districts with no interior overlaps; 367 road nodes form one connected component across 685 segments, with zero endpoint/length, degree or route-sequence exceptions. Full [SW-GEO-V1 geometric QA run 0001 evidence](docs/implementation/test-evidence/SW-GEO-V1-geometric-qa-run-0001.md). This remains read-only planning-geometry QA; no operational geography approval, cadastral/address/entrance acceptance or Neon write occurred.


### BP04-03 independent parcel-dossier geometry QA (read-only)

A second, independent geometry audit now verifies the 420 geometry-derived parcel candidates and their dossiers against the source road-reserve and water layers. It checks parcel containment/non-overlap, road-reserve/water exclusion, complete frontage-to-road-segment geometry, frontage candidate points, unreviewed access-location candidates, water adjacency and the complete measured parcel adjacency register. Successful [workflow run 45511739957](https://github.com/Joshuaogri/saltwater/actions/runs/45511739957) passed 8 regression tests and all 10 audit checks: 420 valid parcel dossiers, 95,337,823.379 m² candidate land, zero interior overlap, 1,374 frontage candidates, 1,374 unreviewed access-location candidates, 100 parcel adjacency relationships and 32 water adjacency relationships, with zero geometry exceptions. The audit is read-only; it creates no canonical addresses or operational access points and does not approve cadastral or operational geography. Full [BP04-03 parcel-dossier geometry QA evidence](docs/implementation/test-evidence/BP04-03-parcel-dossier-geometry-qa-run-0001.md). Next: reconcile parcel frontage/access candidates with the 768 building-boundary access-location candidates, retaining candidate-only status.


### BP04-03 building access and point-contact road-connection reconciliation

The four building-boundary candidates previously left without frontage links are now resolved through two separately classified road-reserve proximity candidates. The affected parcels are `BPC-SWD04N1-004-02` and `BPC-SWD08N1-018-02`, with point-only contact to bridge roads `SWR-B2`/`SWS-0685` and `SWR-B1`/`SWS-0684`. These are not conventional linear frontages: the dossier preserves them as `POINT_CONTACT_ONLY` proximity candidates, and all four building access candidates link to the corresponding same-parcel candidate. No building candidate remains without a road-connection candidate.

The latest independent audits passed: [parcel dossier QA run 45516792963](https://github.com/Joshuaogri/saltwater/actions/runs/45516792963) passed 9 tests and 10/10 checks (420 parcels, 1,374 true frontage candidates and 1,376 access-location candidates); [building access reconciliation run 45516972156](https://github.com/Joshuaogri/saltwater/actions/runs/45516972156) passed 7 tests and 8/8 checks (768 building-boundary candidates, four point-contact links, zero unlinked); [direct connector feasibility run 45516793015](https://github.com/Joshuaogri/saltwater/actions/runs/45516793015) passed 6 tests and 7/7 checks (768 geometric lines feasible under property/building/water checks, zero blocked and zero unlinked). A geometric line is not a driveway, entrance, legal access or traversable/emergency route.

Disposable PostgreSQL validation also passed: [Stage B/Stage D run 45517627917](https://github.com/Joshuaogri/saltwater/actions/runs/45517627917) and [Stage E run 45516793086](https://github.com/Joshuaogri/saltwater/actions/runs/45516793086). Proposal 0016 adds the separate point-contact/nearest-edge candidate classification; its measured disposable schema growth was 24,576 bytes (2,586-byte SQL source). Dossier import growth was 1,933,312 bytes with zero repeat-import growth. Stage E physical asset import growth was 130,744,320 bytes with zero repeat-import growth; 18,098 identities/profiles, 181,915 details, 1,572 geometry candidates, 420 site links and 16,910 relationships were accepted. All 100 stable source entity-code mappings resolved; zero remained unresolved. No production Neon writes or operational access/address records were created. The read-only Neon size remains 9,306,112 bytes.

Full [four-candidate resolution evidence](docs/implementation/test-evidence/BP04-03-four-unlinked-building-access-candidates-resolution-run-0001.md). Continue to keep frontage and point-contact proximity distinct; never promote either candidate to an actual entrance, driveway, legal access or emergency route without separate evidence and review.


### BP04-03 persistent access connector candidates

Stage E now extends beyond boundary-point proposals to a separate, provenance-bearing connector candidate for every building boundary access-location candidate. Each record carries stable candidate IDs, building access-point lineage, road/frontage or road-reserve relationship IDs, road and segment references, a two-endpoint LineString, measured straight-line length, coordinate reference, source manifest checksum and explicit review status. Construction, surface, gradient, barriers, pedestrian/vehicle suitability, accessibility, legal/public access and emergency-egress states remain unknown or not assessed. The four point-contact-only road-reserve cases remain distinct from frontage. The new append-only table is `sw_property.access_connector_candidate` (proposal 0017); disposable PostgreSQL acceptance requires 768 records, including four point-contact-only proximity records. No operational access or Neon production write is involved.


### BP04-03 persistent access connector candidates — validated

[Stage E disposable PostgreSQL run 45519143869](https://github.com/Joshuaogri/saltwater/actions/runs/45519143869) passed. The physical-asset inventory now persists 768 distinct connector candidates in the append-only `sw_property.access_connector_candidate` table, including four explicitly typed point-contact-only road-reserve connections. All 768 connector records retain road-segment lineage, two-endpoint LineString geometry, length, source manifest checksum and unknown/not-assessed physical and legal attributes. The corrected parcel dossier generator now supplies road segment IDs to every frontage access candidate; missing lineage is rejected before import.

The disposable PostgreSQL import added 130,973,696 bytes (130.97 MB decimal), including 768 connector records, 18,098 profiles and 181,915 typed detail records. The connector table occupies 1,007,616 bytes. Re-import of the same manifest grew the database by 0 bytes; backup/restore preserved the connector rows and manifest checksum. No operational access, canonical addresses, or production Neon writes were created. Neon remains 9,306,112 bytes on read-only measurement. See [complete connector candidate evidence](docs/implementation/test-evidence/BP04-03-persistent-access-connector-candidates-stage-e-run-0002.md).


### BP04-03 independent access connector road topology

The new independent topology audit [45519989730](https://github.com/Joshuaogri/saltwater/actions/runs/45519989730) passed all 9 checks and 6 regression tests. It verifies all 768 connector candidates against their building/property/parcel lineage, source road and segment identity, endpoint coordinates, measured length, parent-property containment and road-reserve geometry. It confirms 764 frontage connectors, four distinct point-contact-only road-reserve connectors, and zero unlinked connectors or topology exceptions. This remains geometric QA only; no built or legally usable access route is inferred and no Neon writes occur. See [independent topology audit evidence](docs/implementation/test-evidence/BP04-03-independent-access-connector-road-topology-run-0001.md).


### BP04-03 route-corridor centreline candidates — validated

[Route-corridor audit 45520905232](https://github.com/Joshuaogri/saltwater/actions/runs/45520905232) passed all 7 checks and 6 regression tests. The generated CI artifact contains 768 traceable two-dimensional centreline candidates: 764 frontage-linked and four point-contact/proximity-linked. There are zero unresolved connectors, mapped building intersections, mapped water intersections, originating-building interior crossings or road-reserve overlaps. Forty-seven centrelines intersect the mapped Central-Western Ridge terrain feature; this is recorded as context, not as an impassable obstacle. Other-building separation ranges from 31.894 m to 480.755 m, which is not available route width or a safety clearance.

No corridor width, available width, gradient, surface, barriers, accessibility, legal/public access or emergency-egress state is inferred: these remain null, unknown or not assessed. The artifact is CI-only; no production database write or operational access activation occurred. See [route-corridor candidate evidence](docs/implementation/test-evidence/BP04-03-route-corridor-centreline-candidates-run-0001.md).

### BP04-03 terrain evidence intake and append-only review register — validated

[Evidence intake and review workflow 45568025845](https://github.com/Joshuaogri/saltwater/actions/runs/45568025845) passed all **12 regression tests** and generated the source-linked [read-only evidence register artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45568025845/artifacts/15001455213) (1,061 bytes; SHA-256 `4142a88b349ae143b9e82a9f1c3c0d47df2d72b7ee79519bc2709bfbef80c446`). The register preserves stable evidence/subject IDs, evidence type, capture and submission times, actor/source references and hashes, collection method, instrument/calibration references, observation geometry, typed measurements, uncertainty, attachment hashes, chain-of-custody, validity intervals, supersession and append-only reviewer decisions. Accepted evidence remains non-operational and cannot automatically activate a physical fact. Terminal review decisions cannot be overwritten; changes require new records. The baseline contains 0 submitted observations, 0 review events, 0 accepted evidence records and 0 operational facts activated; 7/7 model checks passed. No survey facts were fabricated and no production database writes occurred. Full [run 0001 evidence](docs/implementation/test-evidence/BP04-03-terrain-evidence-intake-review-register-run-0001.md). Next: field-survey work orders and inspection protocols tied to survey cells and source subjects, including measurement requirements and instrument/calibration controls.

## BP04-03 — canonical fictional physical world (SW-PHYS-V1)

Saltwater now has a populated, playable physical geography layer in `data/geography/saltwater-physical-world-v1.json`. This is authored fictional game canon, not an empty survey-candidate register. It defines **9 terrain zones** with elevation ranges on the fictional SW-VERT-01 datum, landform, substrate, ground condition and gameplay context. It also defines **32 physical assets** with individual IDs, names, neighbourhood placement, geometry, height, width, construction material, condition and continuity: retaining walls, masonry walls, fences, gates, reservoir embankment, culvert, open/covered drainage, quay walls, flood wall, seawall and acoustic barrier. The dataset includes movement rules for barriers, gates, drainage and road-based vehicle travel. Gates have game operating states and access schedules; the existence of a gate does not imply it is open. All coordinates are fictional SW-LOCAL-01 coordinates. Automated validation checks geometry, parent-neighbourhood containment, unique IDs, dimensions, materials, terrain datum and required feature categories. Workflow: [Saltwater Canonical Physical World Validation](.github/workflows/saltwater-physical-world-validation.yml).

## BP04 — canonical playable property world (SW-PROPERTY-WORLD-V1)

The property-world generator now converts Saltwater's deterministic fictional parcel/building design into persistent in-game records. It creates one canonical property identity and street address per generated property site; links buildings, floor-level premises, units and ownership interests; creates the referenced property-holding organisations; and supplies named rooms, building components, site boundary/yard/parking/drainage/waste features, utility connections, construction profiles and condition states. Building access locations become actual fictional entrances, service entrances and emergency exits, each linked to a constructed in-game route and a named road. The four proximity-only building connections are represented as shared access spurs rather than being left unserved. Sites without buildings receive a site gate and pedestrian/maintenance path. Units remain unassigned: this dataset creates no residents or businesses and cannot exceed the 10,000-person population cap. Output is stored as normalized, columnar textual JSON at `data/property/saltwater-property-world-v1.json` so repeated field names are stored once rather than repeated across thousands of unit/component rows. It is generated and committed to `main` by [Saltwater Canonical Property World Build](.github/workflows/saltwater-property-world-build.yml). Regression tests verify identity uniqueness, property/building/premises/unit lineage, addresses, ownership references, access-route continuity and population isolation.

### Current generated baseline

The committed property-world baseline contains **420 properties, 384 buildings, 1,327 premises, 15,199 units, 420 addresses, 804 access points and 804 constructed access routes**. It also contains 420 ownership interests and property-holding organisations, 4,992 building-component records, 5,308 named room records and 2,100 site-feature records. The 36 sites without a building have a site-level entrance and maintenance path. The four proximity-only cases are represented by shared access spurs. The unit register creates no residents and leaves all units unassigned. The columnar JSON file is **12,788,522 bytes** (about 12.19 MiB), down from the first expanded-object encoding of 23,833,730 bytes. The property-world workflow passed all **11 regression tests**, including parsing the persisted JSON file and checking the record totals.

## BP04 — 10,000-business registry foundation (SW-BUSINESS-REGISTRY-V1)

The next built-world layer is a deterministic registry of **10,000 distinct Saltwater businesses**, distributed across 15 fictional sectors. Every business receives its own immutable business ID, registered name, trading name, activity, legal form, size, employee band, operating status and establishment. Each establishment links to a canonical property, building, premises, unit and street address. Business-to-unit occupancy is stored as a separate time-valid relationship. Home-based businesses are used where needed to represent the full range of local economic activity without inventing extra properties or buildings. Employee bands do not create people: the registry creates zero residents, staff-person records or additional population. Textual columnar JSON is persisted at `data/business/saltwater-business-registry-v1.json` by [Saltwater 10,000 Business Registry Build](.github/workflows/saltwater-business-registry-build.yml).

### Current business registry baseline

The generated registry now contains **10,000 distinct businesses**, **10,000 establishments** and **10,000 business-to-unit links** across **15 sectors**. The baseline comprises 9,400 active, 286 seasonal and 314 temporarily inactive businesses. All 10,000 establishments resolve through the property/building/premises/unit/address hierarchy. No staff or resident person records are created. The compact columnar textual JSON file is **8,025,670 bytes** (about 7.65 MiB). The build and its regression tests passed; the registry is committed on `main`.

### Business operations and opening-hours records

The next textual world layer adds a weekly operating schedule for every registered establishment. Each business has seven explicit weekday rows (70,000 daily records across 10,000 businesses), local customer opening and closing times, service windows, staff shift patterns, delivery windows, operational status and an access reference for dispatch. Seasonal and temporarily inactive businesses receive appropriate closure states. These schedules do not create employee, customer or resident person records and do not change the 10,000-person city cap. Source: `runtime/business_operations_generator.py`; output: `data/business/saltwater-business-operations-v1.json`; regression tests: `tests/pkg001/test_business_operations_generator.py`.


## SW-CANON-002 — primate city and global international hub

**Adopted 2026-11-25 as binding canon across all 44 blueprint divisions.** Saltwater is the country's single primate city and dominant national and international metropolis: the highest national and international levels of government, diplomacy, corporate headquarters, banking and finance, entertainment, media, technology, healthcare, education, hospitality, professional services, trade and culture are concentrated here. Saltwater is also a world-leading maritime transit, export, transshipment and logistics exchange hub, comparable in strategic role to the Suez Canal and the world's major port, financial and commercial centres. It must never be modelled as an ordinary small city.

The 10,000-person permanent population cap remains in force, but it does not limit corporate scale, subsidiaries, establishments, institutional capacity, cargo throughput, vessel movements, passenger flows, international reach or economic activity. Transient people must continue to be counted under the existing population rules; this canon does not authorise bypassing the person cap. The existing 10,000-business registry is an initial baseline, not a ceiling on global corporate presence or a claim that all businesses are small. Future property, business, transport, port, airport, institutional, economic and police systems must reflect this global primate-city role.

- [Read SW-CANON-002 — Primate City and Global International Hub](docs/blueprint/decisions/SW-CANON-002-primate-city-global-hub.md)


## BP-04 — property ownership, tenancy and occupancy (SW-PROPERTY-TENURE-V1)

The first property tenure layer is generated and committed on `main`. The deterministic generator consumes the existing compact property-world and business-registry datasets rather than rebuilding geometry, and writes a compact columnar JSON dataset at [`data/property/saltwater-property-tenure-v1.json`](data/property/saltwater-property-tenure-v1.json) (10,833,623 bytes; approximately 10.33 MiB).

The dataset contains:
- 420 current property ownership interests, with chronological fictional acquisition and transfer events and resolvable historical owner organisations.
- 420 current property-management appointments, with separate property-management organisations where appointed.
- 10,000 current commercial leases, licences or operating concessions, each linked to its landlord, business, establishment, property, building, premises and unit.
- 2,500 expired historical agreement records, retained alongside current agreements.
- 10,000 current business occupancy records.
- 15,199 unit occupancy-state records. Residential units remain unallocated for the separate population-allocation process; no resident or other person records are created.
- Contractual rent bands and repair/renewal terms are references only. Rent postings, balances and accounting remain BP-34.

The output uses the same lossless textual columnar representation as the property-world baseline. The build reuses persisted canonical property and business datasets, avoiding duplicate geometry generation. Regression workflow [45577532056](https://github.com/Joshuaogri/saltwater/actions/runs/45577532056) completed successfully, including generation, six tenure regression tests and persistence to `main`.

## BP-04 — weekly business operating schedules (SW-BUSINESS-OPERATIONS-V1)

The weekly schedule layer is generated and committed at [`data/business/saltwater-business-operations-v1.json`](data/business/saltwater-business-operations-v1.json) (15,319,899 bytes; approximately 14.61 MiB). It contains 70,000 daily opening/service/shift/delivery schedule records (seven per establishment) and 10,000 weekly profiles. Build and regression workflow [45574250446](https://github.com/Joshuaogri/saltwater/actions/runs/45574250446) completed successfully. Schedules do not create staff, customers or resident person records.

These datasets remain in GitHub only. No Neon upload or production seed write has occurred. Neon upload remains scheduled after the property-management layers are completed, with compact import packaging, a fresh live storage measurement, an incremental/projected storage estimate and explicit approval before any production write.


## BP-04 — building systems, utilities and metering (SW-BUILDING-SERVICES-V1)

The first building-services layer is generated, regression-tested and persisted on `main`. It consumes the existing compact property-world and tenure datasets and is stored as compact textual columnar JSON at [`data/property/saltwater-building-services-v1.json`](data/property/saltwater-building-services-v1.json) (16,961,533 bytes; approximately 16.18 MiB).

The dataset contains:
- Four citywide utility operators: electricity, potable water, wastewater and telecommunications.
- 1,680 property utility connections and 1,680 linked master utility accounts across 420 property sites.
- 32,078 meters: property master meters plus dedicated electricity and water submeters for all 15,199 units.
- 2,862 building systems across 384 buildings, including electrical distribution, water distribution, wastewater/sanitary, HVAC, fire protection, security/access control, building controls and vertical transport where installed.
- 6,431 equipment assets with installation year, condition, operational state, maintenance class and replacement priority.
- 2,862 system inspection schedules with intervals, last inspection years and next-due simulation ticks.
- 10,000 business utility-responsibility assignments linked to current occupancy records and dedicated unit submeters.

The layer records service availability, capacity bands, redundancy, account responsibility, equipment condition and inspection schedules. It does not create bills, meter readings, balances, financial postings, residents, employees or other person records. BP-34 retains authority over financial transactions; the population ledger remains unchanged.

Build and seven regression tests passed in workflow [45578689850](https://github.com/Joshuaogri/saltwater/actions/runs/45578689850). The final regression-test optimisation also passed the regenerated workflow [45578778424](https://github.com/Joshuaogri/saltwater/actions/runs/45578778424).

This dataset remains in GitHub only. No Neon upload or production seed write has occurred. Neon preparation remains after the remaining property-management layers, with compact import packaging, a fresh live database storage measurement, projected incremental storage and explicit approval before production writes.


## BP-04 — property maintenance, defects and repairs (SW-PROPERTY-MAINTENANCE-V1)

The maintenance and repair layer is generated from the persisted property-world, tenure and building-services datasets. It establishes:
- 384 integrated building maintenance plans and 1,920 linked maintenance cycles.
- 3,282 inspection schedules covering all 2,862 building systems and all 420 property sites.
- 3,169 equipment-linked defect records with severity, discovery basis, operational and safety implications, urgency, root-cause profile and temporary controls.
- 3,169 linked work requests; 2,119 open corrective work orders with trade requirements, responsible maintenance contractors, managing organisations, duration bands, line items, materials and lifecycle events.
- 2,119 material issue records, 384 building emergency-maintenance procedures, equipment warranties and capital replacement forecasts.
- 11 specialist fictional maintenance contractor organisations; contractor organisations are not individual people.

The generated dataset is compact columnar JSON (9,261,100 bytes). Seven regression tests passed in [workflow 45579288100](https://github.com/Joshuaogri/saltwater/actions/runs/45579288100). The generator and tests verify property/building/system/equipment/work-order linkages, full inspection coverage, deterministic manifests and zero person, population or financial postings.

No invoices, payments, cost ledger, capital commitments, residents, employees or contractor-person records are created. BP-34 retains financial authority. The dataset is committed to GitHub `main` only; no Neon upload or production seed write has occurred.

- [Maintenance dataset](data/property/saltwater-property-maintenance-v1.json)
- [Generator](runtime/property_maintenance_generator.py)
- [Regression tests](tests/pkg001/test_property_maintenance_generator.py)
- [Build workflow](.github/workflows/saltwater-property-maintenance-build.yml)


## BP-04 — property security and access control (SW-PROPERTY-SECURITY-ACCESS-V1)

The property security layer is generated from the canonical property, tenure and building-services records:
- 804 door/gate records and 804 linked lock records, covering every canonical property/building access point.
- 1,233 controlled physical key records across 1,233 mechanical key cylinders, with restricted keyway profiles, duplicate controls and organisation-managed key cabinets.
- Electronic door-controller/reader devices for electronically controlled entrances.
- 18,830 access zones across building entry, building security areas, premises and individual units.
- 10,000 business-occupancy access groups, permission sets and organisation-level assignments linked to current leases/concessions and unit occupancy.
- Door policies cover schedules, contractor/work-order authorisation, visitor passes, lost-credential revocation and emergency override audit.

The model preserves free emergency egress and does not issue credentials to named people. Individual credential assignment, access logs and key issue events are runtime gameplay records, not fabricated baseline history. No residents, employees, person credentials, population records, invoices or financial postings are created.

Generation and seven regression tests passed in [workflow 45579877325](https://github.com/Joshuaogri/saltwater/actions/runs/45579877325). The compact columnar dataset is 13,065,912 bytes.

- [Security and access dataset](data/property/saltwater-property-security-access-v1.json)
- [Generator](runtime/property_security_access_generator.py)
- [Regression tests](tests/pkg001/test_property_security_access_generator.py)
- [Build workflow](.github/workflows/saltwater-property-security-access-build.yml)

No Neon upload or production seed write has occurred.

## BP-04 — property condition, valuation, insurance and taxation (SW-PROPERTY-VALUE-RISK-TAX-V1)

Implemented on `main` and generated from the persisted property, tenure, building-services, maintenance and security datasets. The deterministic compact columnar dataset contains 804 site/building condition assessments; 420 land valuations; 384 building-improvement valuations; 804 whole-property/building asset valuations; 1,327 premises valuations; 420 property insurance policies with 1,260 coverage records; 420 property risk profiles; 420 annual 2026 property-tax assessments; 420 exemption-screening records; five fictional insurer organisations; and one annual property-tax rule. Valuations use fictional SWC simulation units and replacement-cost/land-assessment profiles, not real market quotes. Condition records reference the existing defect and building-system baseline. Tax assessments remain assessed-not-billed; exemption is not presumed. No insurance claims, premiums, tax bills, invoices, payments, financial postings, residents or other person records were created. BP-34 retains transaction authority. Seven regression tests passed and the dataset was persisted in [run 45601885026](https://github.com/Joshuaogri/saltwater/actions/runs/45601885026). Output size: 1,309,420 bytes (~1.25 MiB); manifest SHA-256: `921a3dd9274d74a53e8113c78099224a9a4a5b103532edcb672a21a7c8eb165e`.

- [Property valuation, insurance and tax dataset](data/property/saltwater-property-value-risk-tax-v1.json)
- [Deterministic generator](runtime/property_value_risk_tax_generator.py)
- [Regression tests](tests/pkg001/test_property_value_risk_tax_generator.py)
- [Build workflow](.github/workflows/saltwater-property-value-risk-tax-build.yml)

## BP-04 — property development control, building control and lawful use (SW-PROPERTY-DEVELOPMENT-CONTROL-V1)

Implemented on `main`; the deterministic generator consumes the persisted property, tenure, building-services, maintenance and valuation/condition datasets. It records 420 site development plans; 384 existing-building planning permissions; 384 building-control cases; 384 completion/safe-use certificates; 384 periodic inspection schedules; 1,327 premises lawful-use certificates; 15,199 unique unit-level use-compliance records; 72 approved pre-construction development projects; and four development-control rule profiles covering port/maritime, logistics, residential and critical digital infrastructure. The 384 permissions and completion certificates establish the existing fictional built-world baseline; they are not represented as newly submitted applications or fabricated historical inspection visits. All inspection schedules remain scheduled, not completed. The planning application register is empty until gameplay creates applications. The 72 development projects are approved but have not started construction. No people, population records, invoices, fees, payments or financial commitments were created. Seven regression tests passed in [run 45603224586](https://github.com/Joshuaogri/saltwater/actions/runs/45603224586). Output size: 15,029,136 bytes (~14.33 MiB); manifest SHA-256: `9699f165769898af8bc71a7911a2608f0ec8b464a94e6f950f92deccac7c9f60`.

- [Property development-control dataset](data/property/saltwater-property-development-control-v1.json)
- [Deterministic generator](runtime/property_development_control_generator.py)
- [Regression tests](tests/pkg001/test_property_development_control_generator.py)
- [Build workflow](.github/workflows/saltwater-property-development-control-build.yml)



## BP-04 — property title, transactions and lifecycle register (SW-PROPERTY-LIFECYCLE-TRANSACTIONS-V1)

The deterministic property lifecycle generator is `runtime/property_lifecycle_transactions_generator.py`; its compact columnar output is `data/property/saltwater-property-lifecycle-transactions-v1.json`. It creates a unified title register for all 420 canonical property sites, 420 current property-interest records, 531 title instruments and 531 property-transaction index rows. Each transaction row references the authoritative ownership event ID in `SW-PROPERTY-TENURE-V1`; ownership history is not duplicated or re-authored. It also records baseline lifecycle lineage for all 384 buildings and 1,327 premises, linked to their existing development permissions, completion certificates and lawful-use certificates.

Every property has an encumbrance register, but the absence of supplied mortgage, lien, easement or charge data is explicitly recorded as **not asserted**, not as proof that no such interests exist. Ten future gameplay action types are defined: acquisition, sale/transfer, subdivision, consolidation, redevelopment, demolition, change of use, easement/wayleave, mortgage/charge and lease/concession change. These action definitions do not fabricate completed events or mutate the current physical hierarchy. Subdivision and consolidation require new parcel geometry and parent/child lineage before execution. No financial postings, settlement, payments, people or population records are created.

Eight regression tests passed in [workflow 45604525551](https://github.com/Joshuaogri/saltwater/actions/runs/45604525551). The generated dataset is approximately 1.00 MiB (1,044,637 bytes); manifest SHA-256: `c3d35be72d8175d4c9e096ba0aa4e93a1353bb92902c6f19f54acbf7e82fe1ea`. This is GitHub artifact size, not a PostgreSQL storage estimate. No Neon writes were made.


## BP-04 — property rights, easements, wayleaves and boundary evidence (SW-PROPERTY-RIGHTS-AND-BOUNDARIES-V1)

The deterministic generator `runtime/property_rights_boundaries_generator.py` produces `data/property/saltwater-property-rights-boundaries-v1.json`. It creates 420 property-rights schedules, 12,500 contractual-right indexes (10,000 current and 2,500 expired), 420 parcel-boundary evidence records, 804 physical-access evidence records and 1,680 utility-wayleave requirement records. Contractual-right indexes reference existing lease/licence/concession agreement IDs from `SW-PROPERTY-TENURE-V1`; they do not create duplicate agreements.

The boundary register references the existing planning parcel geometry but explicitly marks it as non-survey-grade and not independently verified as a legal boundary. Physical entrances and constructed routes are recorded as physical access evidence only; no legal right of way is inferred. Utility connections are indexed separately from legal wayleaves: the existence of a connected service does not prove an easement, landowner consent or utility corridor right. Nine instrument templates define evidence required for easements, rights of way, utility wayleaves, covenants, mortgages/charges, liens/caveats, boundary agreements and access licences. The registered-instrument register remains empty because no supporting source instruments were present; missing rights are marked unverified, not presumed absent.

Eight regression tests passed in [workflow 45605593292](https://github.com/Joshuaogri/saltwater/actions/runs/45605593292). The generated compact dataset is 5,011,509 bytes (about 4.78 MiB); manifest SHA-256: `8b3f864c0f524c0482271ae4989ceddafe19ce1124169e7a149008ae9a621e69`. This is a GitHub artifact size, not a PostgreSQL storage estimate. No Neon writes were made.


## BP-04 — property insurance exposure, loss events and claims controls (SW-PROPERTY-INSURANCE-CLAIMS-V1)

The deterministic generator `runtime/property_insurance_claims_generator.py` produces `data/property/saltwater-property-insurance-claims-v1.json`. It indexes all 420 existing property insurance policies and their insurers, coverage references, sums insured, deductibles and property valuations. It creates 384 building insurance schedules, 6,431 equipment insurance schedules, 3,169 defect exposure links and 4,200 peril assessments (10 peril categories for each property). Equipment remains covered within its parent property/building schedule; no separate equipment sum insured or duplicate insurance is invented.

The claims process defines ten stages from first notification and coverage triage through loss mitigation, evidence preservation, adjuster review, quantum assessment, coverage decision, settlement authorisation and closure. Sixteen loss-event types are available for future simulation, including coastal flood, storm surge, extreme rainfall, fire, machinery breakdown, utility outage, port-adjacent property damage and business interruption. The operational claims and loss-event registers remain empty: no historical loss, claim, reserve, settlement, premium posting or payment was fabricated. Known maintenance defects are linked as exposures only; causation and insurable loss remain unassessed. Full policy wording, exclusions, endorsements and site-specific hazard surveys remain unverified inputs for future adjudication.

Eight regression tests passed in [workflow 45606397673](https://github.com/Joshuaogri/saltwater/actions/runs/45606397673). The compact dataset is 4,966,651 bytes (about 4.74 MiB); manifest SHA-256: `54e7b58825b843acc146f57fe604fd47f70f122fd5182dd6787950fc1041f12b`. This is a GitHub artifact size, not a PostgreSQL storage estimate. No Neon writes were made.

## BP-04 — property facilities management and operational services (SW-PROPERTY-FACILITIES-OPERATIONS-V1)

The deterministic generator `runtime/property_facilities_operations_generator.py` produces `data/property/saltwater-property-facilities-operations-v1.json`. The opening operating model covers all 420 property sites, 384 buildings and 1,327 premises. It defines 6,720 property-level facilities framework contracts, 6,720 service zones and target service-level agreements, and 13,243 planned service schedules. Service domains include cleaning, general/recycling/organic and specialist waste, pest management, grounds, water hygiene, fire systems, lifts and vertical transport, HVAC/air quality, security systems, energy management, drainage/flood readiness, roofs/facades and port/cargo specialist operations. Premises and building schedules are linked to canonical property IDs; specialist providers are framework-calloff arrangements where applicable.

The service-failure rules cover missed routine work, critical plant/life-safety failures, waste overflow or misclassification, flood/drainage obstruction and repeated supplier failure. Schedules and SLA values are opening targets, not measured performance. Service requests, completed visits and supplier-performance actuals remain empty until gameplay creates them. No staff/person records, waste tonnage, invoices, payments or financial postings are fabricated; BP-34 remains the sole financial posting authority.

Six regression tests passed in [workflow 45607314182](https://github.com/Joshuaogri/saltwater/actions/runs/45607314182). The compact dataset is 7,150,576 bytes (about 6.82 MiB); manifest SHA-256: `f324312f2764c5dac491ef47235b5e1acc976f9ed0ed5cf35452461f2fe95ba3`. This is a GitHub artifact size, not a PostgreSQL storage estimate. No Neon writes were made.

**Unit-count reconciliation completed:** the 62,585 figure was caused by a duplicate nested premises loop in the development-control generator, which emitted each unit's compliance row repeatedly for every premises in its building. The generator now emits one row per actual unit identity. The corrected property-world, tenure occupancy, utility submeter and development-control registers each resolve to the same 15,199 unit IDs; the facilities-operations dataset now verifies identity-set equality and reports `reconciled`. No units were added or removed to force a count match.


## BP-04 — unit identity reconciliation correction (SW-PROPERTY-UNIT-RECONCILIATION-001)

An integrity review traced the apparent 47,386-unit excess to a duplicate nested premises loop in `runtime/property_development_control_generator.py`. Unit compliance had been emitted repeatedly for every premises in the same building. The generator was corrected to emit one record for each unit under its actual premises, and regression tests now assert both one-to-one count equality and uniqueness of unit IDs. The corrected development-control dataset contains **15,199 unit-use compliance records for 15,199 canonical unit identities**. Seven regression tests passed in [workflow 45608515021](https://github.com/Joshuaogri/saltwater/actions/runs/45608515021). Corrected output size: 4,688,872 bytes; manifest SHA-256: `3c83da9b66389a451fb1997ee0801876305cc25c046bc621cd2eb0b5cb6814fe`. Dataset commit: `a722aa7eae9abd5ee3fbda5f886d738fda8f566a`.

The facilities-operations generator now reads the corrected development-control dataset and compares the actual unit-ID sets across property world, tenure, utility submeters and development control. All four contain the same **15,199** unit IDs and the result is **reconciled**. Six regression tests passed in [workflow 45608676475](https://github.com/Joshuaogri/saltwater/actions/runs/45608676475). Updated facilities dataset size: 7,150,790 bytes (~6.82 MiB); manifest SHA-256: `dd66d415612d66be74662b00d6ecfd2fcd5533b4061c8a18b63f9a520e43d2ca`. Dataset commit: `9a1e949808345fe856a581f968dfa2e985bcceda`. Neither dataset update involved a Neon production write.

## SW-GLOBAL-ESTATE-CAPACITY-AUDIT-001 — global-city estate scale review

The first vertical-intensification phase is now fully regenerated, regression-tested and persisted as one consistent property/business snapshot on `main`. Sequential rebuild workflow: [45611785956](https://github.com/Joshuaogri/saltwater/actions/runs/45611785956), completed successfully. Snapshot commit: `ed0b77e`.

The deterministic district-specific `GLOBAL-ESTATE-VERTICAL-V1` profiles create commercial towers up to 58 storeys, with distinct financial, civic, university and harbour skylines. Industrial, freight, port-yard and utility assets retain appropriately lower-rise forms.

**Verified regenerated estate totals**
- 420 property sites; 384 buildings; 6,954 premises; 80,965 canonical units.
- 12,430,234.506 m² gross floor area; maximum height 58 storeys; mean building height 18.109 storeys.
- 265 buildings have at least 10 storeys; 146 have at least 20 storeys.
- 10,000 businesses and 10,000 establishments.
- 163,610 utility meters; 6,815 equipment assets; 3,054 building systems.
- 90,223 access-control zones; 804 canonical access points and 804 constructed access routes.
- Facilities schedules and service zones have been regenerated against the same canonical unit set.

Unit identity reconciliation is exact across the property world, tenure occupancy, utility submeters, development-control use records and facilities operations: **80,965 unique unit IDs in each register, with no missing or extra IDs**. All sequential rebuild test groups passed, including the final insurance, facilities and estate-capacity audit regression suites.

The 10,000-person population hard cap is unchanged. No residents, workers, employees, police personnel or other person records were created. No Neon production writes were made.

**Next physical-estate phase:** replace the single-building-per-property limitation with multi-building campuses and specialist megasites. This includes international port and bonded-logistics terminals, intermodal freight/passenger complexes, export-manufacturing estates, financial/corporate headquarters campuses and major international institutions. Every additional building must receive unique building, premises, unit and access identifiers, site-contained geometry, a connected constructed entrance/route and fully regenerated downstream property records. Existing site-only entrances and no-frontage access solutions must be preserved. The one-contiguous-city-state canon and 10,000-person cap remain binding.

## SW-PROPERTY-ESTATE-V2 — expanded campus estate and regenerated property stack

**Verified and persisted on `main` on 2026-11-25.** This section supersedes all earlier property-estate counts and dataset-size statements above where they describe the pre-campus or single-building estate. The sequential full-stack rebuild and all 13 validation stages passed in [workflow run 45623907617](https://github.com/Joshuaogri/saltwater/actions/runs/45623907617). All dependent registers were regenerated in dependency order, compressed, and persisted together in one consistent snapshot.

### Canonical expanded physical estate

- 420 property sites.
- 1,474 buildings across multi-building campuses and specialist sites.
- 27,730 premises.
- 180,733 canonical units.
- 110,920 named rooms.
- 2,984 building/site access points and constructed access routes.
- 36 sites without buildings retain site-level entrances and maintenance paths.
- Existing shared access spurs continue to resolve the four original frontage-deficient cases.
- No resident, worker, employee, police-personnel or other person records were generated. The distinct-person population cap remains 10,000.

### Regenerated dependent registers

The same expanded estate was used to regenerate business registry and weekly operations, ownership and occupancy, utility connections/meters/building systems/equipment, maintenance and defects, security and access control, condition/valuation/insurance/tax, development and lawful use, title/lifecycle/transactions, rights/boundary evidence, insurance exposure/claims controls, facilities operations, and the global estate-capacity audit. All 13 workflow validation stages passed, including exact canonical unit-identity reconciliation across the property world, tenure, utility submeters, development-control and facilities records.

### Compressed source inventory

All 14 property/business datasets are stored as deterministic gzip snapshots under `data/property/` and `data/business/`. Their combined GitHub blob size is **23,023,562 bytes (21.96 MiB)**. No uncompressed `.json` dataset files remain in those two folders. The canonical property-world snapshot is 8,924,278 bytes compressed; the building-services snapshot is 4,284,913 bytes compressed. These are source-repository compressed sizes, **not** PostgreSQL storage estimates.

The full-stack workflow restores compressed inputs, rebuilds and validates the complete dependency stack, compresses every output and commits the consistent snapshot to `main`. No Neon production seed/import/upload or population write occurred. Before any proposed Neon import, the compact package must be prepared and benchmarked, the live PostgreSQL baseline remeasured, and projected database growth reported for explicit approval.

## Canonical property-stack import preparation

The expanded 14-dataset property/business stack is persisted and validated on `main`. The next database phase is governed by [BP04 canonical property-stack import and disposable benchmark plan](docs/implementation/BP04-canonical-property-stack-import-plan.md). Existing BP04-01/BP04-02 schema proposals and the BP04-03 Stage E importer are disposable-only candidate assets, not the canonical property-world importer. The production property schema and lossless relational import pipeline must be built and benchmarked in isolated PostgreSQL 16 first. The live Neon database remains unchanged; no property seed rows or production property tables have been written.

### BP04 canonical property relational schema — phase 1

The first typed relational import model is now committed on `main` for isolated PostgreSQL 16 validation. Candidate SQL: `db/proposals/0012_bp04_canonical_property_stack.sql`. The mapping and integrity contract is documented in [BP04 canonical property relational mapping](docs/implementation/BP04-canonical-property-relational-mapping.md). It establishes stable source-ID primary keys and typed property, building, premises, unit, access, room/component, ownership, business, establishment and occupancy tables, with explicit foreign keys, provenance and a deterministic import-release ledger. Original source objects are retained per typed row for lossless round-trip verification; this is not a single opaque JSONB store.

This is a disposable-only schema proposal. It has not been applied to Neon. The deterministic importer, full phase-2 register coverage and PostgreSQL 16 benchmark are the next implementation tasks. No production schema or data writes have occurred.

The phase-1 schema now has a dedicated disposable PostgreSQL 16 acceptance workflow (`.github/workflows/bp04-property-schema-disposable.yml`) and SQL contract checks (`tests/pkg001/bp04_property_schema_acceptance.sql`). The workflow applies only the candidate proposal to an ephemeral CI database, verifies the 19-table inventory, deferred cyclic reference, current-unit uniqueness and release ledger, and records disposable schema size. It has not been run against Neon.

### BP04 phase-1 importer implemented

A deterministic, compressed-columnar importer is now available at `runtime/bp04_property_stack_importer.py`. It reads the canonical property-world, business-registry and tenure snapshots directly from their gzip files, verifies dataset identities and package digests, preserves each complete source row in JSONB alongside typed columns, uses stable source IDs, records an import-release manifest, and imports within one transaction with deferred FK checks. It refuses to connect to any database other than the disposable `saltwater_test` database. The dedicated PostgreSQL 16 workflow now applies the candidate schema, imports the package, repeats the import for row-count/idempotency checks, and reports database/table storage. CI run: [BP04 schema and import](https://github.com/Joshuaogri/saltwater/actions/runs/45628722456). This has no connection to production Neon.

### BP04 compressed-archive import benchmark — passed

The phase-1 schema was optimized after the first disposable benchmark showed that duplicating every complete source row as per-row JSONB inflated the database to 453.5 MiB. The storage-efficient proposal is now `db/proposals/0013_bp04_compressed_source_archive.sql`: complete original datasets are retained once as their original gzip byte streams in `source_dataset_archive`, while the typed relational tables retain stable source IDs and mapped operational columns. The importer is `runtime/bp04_property_stack_importer.py`.

The PostgreSQL 16 disposable workflow passed using this design: [BP04 compressed archive benchmark](https://github.com/Joshuaogri/saltwater/actions/runs/45630476765). It imported and reconciled **402,658 records across 17 typed tables**, covering 420 property sites, 1,474 buildings, 27,730 premises, 180,733 units, 110,920 rooms, 2,984 access points/routes, 10,000 businesses, 10,000 establishments, 10,000 business-unit links, 12,500 occupancy agreements and 10,000 occupancies. Cross-reference violations: **0**.

The three compressed source archives total **10,934,275 bytes (10.43 MiB)**; their uncompressed JSON totals **196,604,988 bytes (187.45 MiB)**. The measured disposable PostgreSQL database is **135,257,111 bytes (128.99 MiB)**, including typed rows, indexes and the compressed source archives. Re-importing the same release left database size unchanged (**135,257,111 bytes before and after**) and all row-count checks passed. This is a **71.6% reduction** against the initial row-level-JSONB design.

This remains a partial import benchmark: only property world, business registry and property tenure are included. The other dependent property registers still need typed mappings and a complete combined benchmark. The 128.99 MiB figure is not a final Neon projection. **No production Neon schema or data writes have occurred.**


## BP04 — complete compressed property-source inventory

The read-only source inventory is implemented in `runtime/bp04_source_inventory.py`, with regression tests in `tests/pkg001/test_bp04_source_inventory.py` and CI workflow `.github/workflows/bp04-source-inventory.yml`. Successful inventory run: [45633081533](https://github.com/Joshuaogri/saltwater/actions/runs/45633081533).

- 14 compressed property/business source datasets.
- 105 columnar collections.
- 1,950,947 source records.
- 23,023,562 compressed bytes (21.96 MiB).
- 559,420,873 uncompressed bytes (533.5 MiB).
- Every collection was checked for valid columnar structure and row-width consistency; inventory records column names, row counts, candidate identity columns, compressed/uncompressed sizes and SHA-256 source digests.
- Canonical dataset IDs are read from source metadata rather than inferred from filenames.
- This is source-package inventory only. It is not a relational import, Neon storage estimate or production upload. The phase-one PostgreSQL benchmark remains limited to the three mapped datasets; typed mapping and full disposable benchmarking of the remaining registers are next.


## BP04 — building services and utilities relational phase 2

The candidate schema `db/proposals/0014_bp04_building_services_utilities.sql` and importer mappings now cover all eight collections in the compressed building-services source: **426,399 records** across building systems, utility connections, utility provider profiles, utility accounts, meters, equipment assets, system inspections and business utility responsibilities. The importer preserves the original gzip dataset once in the source archive and writes typed operational columns with stable source IDs and explicit links to canonical property, building, unit, organisation, business and occupancy records.

The disposable PostgreSQL 16 workflow applies proposals 0013 and 0014 in order and validates the 28-table schema. Successful end-to-end benchmark: [BP04 phase-2 run 45636655387](https://github.com/Joshuaogri/saltwater/actions/runs/45636655387). It imported the complete four-dataset property/business/tenure package plus all eight building-services collections, including 426,399 building-services source records. The resulting database contains **362,093,591 bytes (345.37 MiB)** across typed records, indexes and four compressed source archives. The repeat import passed: **362,093,591 bytes before and after**, with all row counts unchanged and **zero cross-reference violations**. The importer explicitly normalizes source boolean flags encoded as 0/1 and adds the four utility-provider organisations to the canonical organisation register before inserting their provider profiles.

The 4 compressed archives total **15,219,188 bytes (14.51 MiB)**; the phase-2 building-services archive contributes 4,284,913 bytes. The database figure is a measured disposable PostgreSQL result for the four mapped datasets only, not a final full-estate or Neon projection. Phase 2 is accepted; maintenance, security, valuation, development, lifecycle, rights, insurance and facilities registers still need typed mappings and inclusion in the complete benchmark. This remains disposable-only. No Neon production schema or data writes have occurred.


## BP04 — property maintenance and repairs relational phase 3

Candidate schema `db/proposals/0015_bp04_property_maintenance_repairs.sql` adds 13 typed tables for maintenance contractor profiles, building maintenance plans and cycles, site/system inspections, equipment defects, work requests, work orders and lines, material issues, maintenance events, warranties, replacement forecasts and emergency maintenance procedures. The deterministic importer maps the complete `SW-PROPERTY-MAINTENANCE-V1` source and extends the canonical organisation register with its maintenance contractors. Relationships point to the canonical property/building/system/equipment records and maintenance work-order lineage; no person or financial-posting records are introduced.

The disposable PostgreSQL 16 workflow applies all three schema proposals and validates the 41-table inventory. The first attempt exposed colliding inspection identifiers caused by truncating long slugs; the generator now appends a SHA-256 suffix to long identifiers and a new regression test checks all 13 register ID sets. The maintenance build and uniqueness tests passed, and the regenerated gzip archive is 2,536,846 bytes (about 2.42 MiB).

The complete phase-3 disposable benchmark passed: [BP04 phase-3 run 45639343963](https://github.com/Joshuaogri/saltwater/actions/runs/45639343963). The five-source package now loads **947,720 typed domain records across 38 domain tables**, plus the three import/archive ledger tables (41 tables total). Maintenance records include 12,194 inspections, 13,139 defects and work requests, 8,888 work orders, 8,888 work-order lines, 8,888 material issues and events, 26,341 equipment warranties, 16,846 replacement forecasts, 1,474 building emergency procedures and 11 maintenance contractors. Cross-reference violations: **0**.

Measured disposable PostgreSQL size is **420,174,871 bytes (400.71 MiB)**, including typed rows, indexes and five compressed source archives. Those archives total **17,756,034 bytes (16.93 MiB)**; their uncompressed source JSON totals **368,978,617 bytes (351.86 MiB)**. Repeat import passed with **420,174,871 bytes before and after**, and all table counts remained unchanged. This is still a partial import: security/access, valuation/tax, development control, lifecycle, rights/boundaries, insurance/claims and facilities operations remain to be mapped and included before the final full-estate benchmark. Neon production remains unchanged.


## BP04 — property security and access-control relational phase 4

Candidate schema `db/proposals/0016_bp04_property_security_access.sql` adds 12 typed tables for doors/gates, locks, key cylinders and physical keys, electronic security devices, hierarchical access zones, business occupancy access groups, permission sets and normalized permission-to-zone grants, organisation access assignments, key cabinets and access policies. The importer maps the source permissions array into explicit grant rows and retains the compressed source archive once. Database constraints prevent person-bound physical-key issuance and person membership in access groups; credentials remain organisation/group-level until runtime simulation assigns people.

The security generator now uses collision-resistant identifiers for long source IDs, and regression coverage checks uniqueness across all security registers. Its build workflow restores canonical gzip inputs and persists a compressed output (3,025,865 bytes; 2.89 MiB). The first schema acceptance run exposed auto-generated constraint-name assumptions; the person-credential exclusion checks now use explicit stable constraint names.

The complete 53-table disposable PostgreSQL 16 benchmark passed: [BP04 phase-4 run 45640703939](https://github.com/Joshuaogri/saltwater/actions/runs/45640703939). It loaded **1,232,690 typed domain records across 50 domain tables**, plus the three import/archive ledger tables, with **zero cross-reference violations**. Security records include 217,307 access zones, 20,000 permission-to-zone grants, 10,000 business access groups, 10,000 permission sets, 10,000 organisation assignments, 2,984 doors, 2,984 locks, 4,572 physical keys, 1,524 key cylinders, 721 electronic devices, 420 key cabinets and 4,458 access policies. Database constraints enforce empty person membership in access groups and prevent person-bound physical-key assignment.

Measured disposable PostgreSQL size is **532,839,447 bytes (508.16 MiB)**, including typed rows, indexes and six compressed source archives totalling **20,781,899 bytes (19.82 MiB)**. Their uncompressed source JSON totals **430,913,963 bytes (410.95 MiB)**. Repeat import passed with **532,839,447 bytes before and after**, and all row counts remained unchanged. This is still a partial import: valuation/tax, development control, lifecycle, rights/boundaries, insurance/claims and facilities operations remain to be mapped and included before the final full-estate benchmark. Neon production remains unchanged.


## BP04 — property valuation, insurance exposure and taxation relational phase 5

Candidate schema `db/proposals/0017_bp04_property_valuation_tax.sql` adds 12 typed tables for site/building condition, land and improvement valuation, whole-property and premises valuations, insurer profiles, insurance policies and coverage, property risk, annual tax assessments, exemption reviews and tax rules. The importer adds five fictional insurers to the shared organisation register and preserves typed SWC values and explicit valuation/policy/property/owner/manager links. Assessments remain assessed-not-billed; no premiums, claims, invoices, tax bills, payments or financial postings are created.

The valuation generator now uses collision-resistant long identifiers, with uniqueness regression checks across all 12 source collections. Its build workflow restores five compressed canonical dependencies and persists only a compressed dataset. The complete seven-source, 65-table disposable PostgreSQL 16 benchmark passed: [BP04 phase-5 run 45641900441](https://github.com/Joshuaogri/saltwater/actions/runs/45641900441). Valuation/tax records include 1,894 condition assessments, 420 land valuations, 1,474 improvement valuations, 1,894 asset valuations, 27,730 premises valuations, 420 insurance policies, 1,260 coverage records, 420 risk profiles, 420 annual tax assessments, 420 exemption reviews, one tax rule and five insurer profiles. The combined database measured **546,020,375 bytes (520.73 MiB)** with **zero cross-reference violations**. Repeat import passed with **546,020,375 bytes before and after**, and all row counts remained unchanged. Seven mapped gzip sources total **21,190,376 bytes (20.21 MiB)**; their uncompressed source JSON totals **437,861,928 bytes (417.58 MiB)**. This remains a partial import: development control, lifecycle transactions, rights/boundaries, insurance claims and facilities operations still require mapping and inclusion in the final benchmark. Neon production remains unchanged.


## BP04 canonical property stack — source archive, corrected mapping ledger and business operations

The full disposable PostgreSQL 16 workflow [45646271478](https://github.com/Joshuaogri/saltwater/actions/runs/45646271478) passed on main commit `f9e18f63dff763134073050e3409432f82bd5c79`. The workflow applied proposals 0013–0019, passed source-identity unit tests, passed 68-table schema acceptance, imported all 14 gzip sources, passed the post-import ledger/business-schedule acceptance, and passed repeat-import storage/idempotency checks.

A correction was made after reviewing Phase 6's first mapping ledger: its collection keys used some relational target names rather than the original source collection names. The importer now retains each source collection identity directly while expanding columnar records. The corrected ledger reconciles all 105 source collections and 1,950,947 source records. **63 source collections (1,337,925 rows) are typed-mapped; 42 collections (613,022 rows) remain archive-only.** Six datasets are fully mapped, two are partially mapped (property world and tenure), and six are archive-only. All 14 source gzip datasets are retained losslessly regardless of mapping status.

| Measure | Verified result |
|---|---:|
| Source datasets archived | 14 / 14 |
| Source collections reconciled | 105 |
| Total source records | 1,950,947 |
| Typed-mapped source collections / rows | 63 / 1,337,925 |
| Archive-only source collections / rows | 42 / 613,022 |
| Compressed package | 23,023,562 bytes (21.96 MiB) |
| Uncompressed source JSON | 559,420,873 bytes (533.50 MiB) |
| Compressed source archive relation | 23,797,760 bytes |
| Typed relational schema | 68 tables |
| Business daily schedules | 70,000 |
| Business weekly profiles | 10,000 |
| Disposable PostgreSQL database | 577,395,735 bytes (550.65 MiB) |
| Cross-reference violations | 0 |
| Database size after repeat import | 577,395,735 bytes (unchanged) |
| Repeat-import row mutations | 0 |

The business schedule layer records each business's seven-day customer opening status, opening/closing times, service window, shift pattern, delivery window and emergency contact route. It is useful for time-aware dispatch, call-for-service context and scene access; it creates no employee, customer or resident person records. The repeat import produced zero inserts, updates or deletes. Largest measured relations include meter (195,067,904 bytes), access_zone (83,640,320), unit_space (58,318,848), business_daily_schedule (25,821,184), premises_room (23,887,872) and source_dataset_archive (23,797,760).

The remaining archive-only sources are the existing development-control, facilities, insurance-claims, lifecycle/transactions, rights/boundaries and global-estate-audit datasets. Next, map only gameplay-relevant content: lawful-use and development restrictions where useful to investigations/scene access; title/lifecycle and rights evidence where relevant to disputes or property crime; and insurance claim/loss workflows for relevant incidents. Keep the global estate audit as evidence, and avoid expanding facilities-management systems without a direct police-gameplay need.

This is disposable benchmark evidence only. No production Neon schema, seed, import or upload was performed.


### BP04 phase 9 — title, transaction and lifecycle mapping (validation in progress)

Candidate migration `db/proposals/0021_bp04_property_title_lifecycle.sql` adds nine typed tables for the title register, property-interest index, title instruments, transaction index, property/building/premises lifecycle, encumbrance status and runtime lifecycle-action rules. The importer maps all nine source collections from `SW-PROPERTY-LIFECYCLE-TRANSACTIONS-V1` while keeping `SW-PROPERTY-TENURE-V1` authoritative for ownership-event facts. The mapping covers 31,956 source rows: 420 title records, 420 interest records, 531 title instruments, 531 transaction indexes, 420 property registration events, 1,474 building baselines, 27,730 premises baselines, 420 encumbrance registers and 10 action rules.

The first disposable import correctly exposed truncated-ID collisions in the generated premises lifecycle IDs (only 9,461 of 27,730 rows could be inserted). The generator now uses full-source SHA-256-derived identifiers for title, interest, property, building, premises and encumbrance IDs. Its dedicated build and regression workflow [45653180837](https://github.com/Joshuaogri/saltwater/actions/runs/45653180837) passed: **9 tests**, including uniqueness checks across all generated lifecycle ID collections. It regenerated the 27,730 premises and 1,474 building baseline rows without collisions. The full dependent property-stack rebuild [45653180817](https://github.com/Joshuaogri/saltwater/actions/runs/45653180817) completed successfully on main (rebuild commit `85dc08d`). It regenerated the 27,730 premises lifecycle rows with unique identifiers and regenerated the dependent rights/boundary dataset. The rights generator reports 420 property-rights schedules, 12,500 contractual-right indexes, 420 boundary-evidence records, 2,984 physical-access evidence records and 1,680 utility-wayleave requirement records. The 92-table phase-10 disposable import benchmark is running against this rebuilt snapshot. No production Neon writes have occurred.


### BP04 phase 10 — property rights, boundary and access evidence

Added seven typed relational tables and mapped all seven collections from `SW-PROPERTY-RIGHTS-AND-BOUNDARIES-V1`: 420 property-rights schedules, 12,500 contractual-right indexes, 420 boundary-evidence records, 2,984 physical-access evidence records, 1,680 utility-wayleave requirement records, zero registered instruments, and nine future instrument templates (**18,013 source rows**). Contractual rights link to existing tenure agreements; access points/routes remain physical evidence, not inferred legal rights; parcel geometry remains non-survey-grade evidence. Migration: `db/proposals/0022_bp04_property_rights_boundaries.sql`. The disposable import acceptance now checks all seven collections and their principal relationships. No Neon production writes.

### BP04 phases 1–10 — complete disposable import benchmark

The full 14-source package was imported into disposable PostgreSQL 16 using the 92-table schema. Benchmark workflow [45656098435](https://github.com/Joshuaogri/saltwater/actions/runs/45656098435) completed successfully:
- Compressed source package: **29,434,820 bytes (28.07 MiB)**; uncompressed source total: **558,602,287 bytes (532.72 MiB)**.
- Source inventory: **14 datasets, 105 collections and 1,950,923 source records**.
- Mapping: **8 fully mapped datasets, 3 partially mapped, 3 archive-only**; 86 collections mapped and 19 retained archive-only; **1,422,202 rows mapped**.
- Cross-reference violations: **0**.
- Disposable database size after import: **627,792,919 bytes (598.71 MiB)**.
- Repeat import: database size remained **627,792,919 bytes**; **0 inserts, updates or deletes**. Idempotency passed.
- Live Neon baseline (read-only measurement): **9,306,112 bytes (8.875 MiB)**. Estimated incremental storage for this package is approximately **618,486,807 bytes (589.83 MiB)**, giving an estimated post-import total near **627.8 MB (598.71 MiB)**. This is a PostgreSQL 16 benchmark estimate, not a production Neon measurement.
- No production Neon schema or data writes have been made.

The 19 archive-only collections remain losslessly retained in their compressed source datasets; they are not fabricated into gameplay records. The mapped collections provide typed relational access for the core property, business, tenure, operating-hours, building-services, maintenance, security, lawful-use, title/lifecycle, rights and access relationships.


### BP05 — Saltwater Police Service architecture

Implemented the initial fictional police organisation on `main` in `db/proposals/0023_bp05_police_architecture.sql`. The Saltwater Police Service now has **48 canonical components**: one department, four command portfolios, 12 divisions and 31 operational/support units. The structure includes nine substantive ranks (Recruit remains a service standing, not a rank), 24 position definitions and an **authorised establishment of 500 vacant posts** distributed across the service. All 47 parent reporting relationships are recorded. The seed creates no personnel or person records; those are generated and linked in the personnel stage, preserving the 10,000-person cap and avoiding fictitious filled posts.

Full Python and disposable PostgreSQL regression [PKG-001 workflow run 45658350599](https://github.com/Joshuaogri/saltwater/actions/runs/45658350599) passed. It verified component hierarchy, rank/position separation, 500-post count, initial vacancy status, append-only post authorisation history and zero personnel created by the structure seed.


### BP06 — personnel service records (first increment)

Added `db/proposals/0024_bp06_personnel_service_records.sql` and a PostgreSQL-backed dossier model for service engagements, immutable service events, service-number history and effective-dated supervision. Every personnel appointment now creates its service engagement and history in the same transaction. Recruit appointments additionally require an active established supervisor and create the formal supervision link; established personnel do not need a recruit-supervisor relationship. The schema preserves canonical BP-03 person identity and does not create duplicate people, ranks or post occupancy.

The dedicated BP06 acceptance and complete PKG-001 disposable regression [run 45659232002](https://github.com/Joshuaogri/saltwater/actions/runs/45659232002) passed, including the 10,000-person cap, concurrency, backup/restore and runtime checks. It verifies dossier/event/service-number completeness, living population linkage, recruit supervision and no automatic filling of the 500 vacant posts.

## Current implementation update — 2026-11-25

This dated update supersedes earlier status statements above where they describe the runtime, police architecture or property stack as not yet implemented.

- **Property stack:** BP04 phases 1–10 are implemented as disposable-only PostgreSQL proposals and imported successfully into a 92-table PostgreSQL 16 benchmark. The package contains 14 compressed datasets, 105 source collections and 1,950,923 source records. 1,422,202 rows are mapped to typed tables; the remaining 19 collections are preserved losslessly in compressed source archives. The package is 29,434,820 compressed bytes (28.07 MiB); the benchmark database is 627,792,919 bytes (598.71 MiB). Cross-reference violations: zero. Repeat import produced zero mutations and no database-size change. Evidence: [BP04 92-table benchmark](https://github.com/Joshuaogri/saltwater/actions/runs/45656098435).
- **Police architecture (BP05):** the disposable proposal defines 48 organisational components, nine substantive ranks, 24 position definitions and 500 authorised posts, initially vacant. The hierarchy and establishment acceptance passed. No officers were fabricated or appointed by the architecture seed.
- **Personnel service records (BP06):** the disposable proposal now creates a personnel dossier, service engagement, immutable appointment event and service-number history when personnel are appointed. Recruit supervision is required only for recruits; established direct-entry supervisors do not need a recruit supervisor of their own. BP06 acceptance passed in the current disposable workflow.
- **Population/runtime:** the disposable regression suite filled the population to exactly 10,000, verified that concurrent admission at 9,999 permits exactly one final admission, and verified that an additional living person is rejected. Backup/restore reproduced 10,000 people, population states, histories, events and name-registry records exactly. The checkpoint validator explicitly leaves business-minimum, player-absence-freeze and permission/hidden-truth gates unexecuted; these are not claimed as passed.
- **Production boundary:** all of the above database work is disposable PostgreSQL validation. No BP04 property import or BP05/BP06 schema proposal has been applied to production Neon. The live Neon baseline remains a separate read-only measurement. No production seed data has been written.
- **Execution approach:** fictional canon, NPCs, organisations and gameplay systems are developed directly on GitHub `main` using established engineering and simulation standards. Routine fictional work does not require repeated user approval. Production Neon writes remain separate from fictional design and disposable testing.


### BP07 — career history foundation

Added `db/proposals/0025_bp07_career_rank_and_post_history.sql`: append-only career episode events, separate rank assignments and authorised post appointments, current-rank/current-post projections, and registered career event types. Opening a career episode now records its event automatically. Rank and post assignments remain separate, and a recruit receives neither a substantive rank nor an occupied post automatically. The BP07 career-history acceptance and full PKG-001 disposable regression [run 45660272493](https://github.com/Joshuaogri/saltwater/actions/runs/45660272493) passed, including population-cap, concurrency, backup/restore and runtime checks.


### BP08 — unit catalogue and deployment readiness foundation

Added `db/proposals/0026_bp08_unit_deployment.sql`. All **31 operational/support units** now have canonical profiles, mandate boundaries, capability codes, crew thresholds and dispatchability classification. Their establishment view reconciles **480 unit posts**, all currently vacant. Unit membership is linked automatically to a BP07 post appointment in a unit; deployment and status histories are append-only. With no staffed memberships or verified status/resource records, all units correctly remain unavailable and none is dispatch-eligible. The schema deliberately does not fabricate crews, deployments, vehicles or radio readiness.

BP08 disposable acceptance passed in [PKG-001 run 45661335150](https://github.com/Joshuaogri/saltwater/actions/runs/45661335150); the complete regression is continuing through the population-cap and backup/restore tests. BP09 resource readiness is the next dependency before real dispatch eligibility.


## BP04 — production release packaging

The BP04 schema has been promoted from disposable-only proposals into the ordered production migration sequence `db/migrations/0003`–`0012`. The original proposal files remain for design provenance. The 92-table disposable benchmark workflow now applies the production migration copies. The canonical importer defaults to `saltwater_test`; writes to the production database name `neondb` require the explicit `--allow-production` flag. The migration ledger read-only verifier can report pending migrations without treating an un-deployed release as schema drift.

The accepted benchmark package contains 14 compressed datasets, 105 collections and 1,950,923 source records; 1,422,202 typed-mapped rows across 92 tables; 19 archive-only collections; three partially mapped collections; zero cross-reference violations; 29,434,820 compressed bytes; and a 627,792,919-byte (598.71 MiB) disposable PostgreSQL footprint. Repeat import was storage-stable. Benchmark package SHA-256: `54090f74332c1d0fedb09b48ad1fd669b9d62c593c9a5c253e979cbafaf4a3be`.

**Production deployment remains pending.** The current release commit must pass a fresh disposable benchmark, then production preflight must confirm the latest source/package digest, backup/restore point, migration ledger, live schema fingerprint, storage headroom and before/after measurements. The latest read-only Neon baseline on 2026-11-25 is 9,306,112 bytes; five user tables exist and no `sw_property` tables are present. No BP04 production writes have occurred. See [BP04 production release runbook](docs/operations/BP04-production-release-runbook.md).


### BP09 — police resource inventory and readiness

Added `db/proposals/0027_bp09_police_resource_readiness.sql`: 15 resource models, **527 individually tagged assets**, 50 fleet vehicles, 500 initial unit-pool allocations and 27 unallocated central-store assets. Every asset has a registration-history event; each unit-pool allocation has an allocation event. Seven dispatchable units have complete minimum equipment requirements. The readiness projection now requires verified staffing, operational availability and resource sufficiency together. No unit is dispatch-eligible until it has a real roster and an available status; resource inventory alone cannot create a dispatchable unit.

BP09 disposable acceptance passed in [PKG-001 run 45663358864](https://github.com/Joshuaogri/saltwater/actions/runs/45663358864). Full regression is completing the population-cap and backup/restore checks. Next is to connect the communications/CAD and incident workflow, then field response, using only units that become genuinely ready.


The current production-release workflow is manual-only: `.github/workflows/neon-production-migrations.yml`. It requires the exact confirmation `APPLY_BP04_TO_NEON`, a pre-release Neon restore-point reference, the pinned source package digest and the production database name `neondb`; no push can trigger it. The final combined migration-runner/import benchmark passed on PostgreSQL 16 and 18 in [run 45664193870](https://github.com/Joshuaogri/saltwater/actions/runs/45664193870). Full disposable database sizes were 628,120,599 bytes (PostgreSQL 16) and 628,569,791 bytes (PostgreSQL 18); repeat imports left both unchanged. Using the PostgreSQL 18 result, expected incremental Neon database growth from the 9,306,112-byte live baseline is approximately 619,263,679 bytes (619.26 MB / 590.58 MiB), with a projected total near 628.57 MB (599.45 MiB). This remains an estimate until measured on Neon. The production workflow has not been executed; no BP04 production schema or data writes have occurred.


The 14 compressed source archives total 29,434,820 bytes (29.43 MB / 28.07 MiB); the ten production migration files total 65,681 bytes; the importer source is 68,115 bytes and executes in the GitHub runner. Combined static release files are 29,568,616 bytes (29.57 MB / 28.20 MiB). This is not the total database growth: typed rows, indexes and PostgreSQL overhead account for the much larger measured disposable footprint.


## BP04 production release checkpoint — 2026-11-25

A manual Neon restore snapshot was created on the production branch before the BP04 production release attempt:

- Neon project: `misty-breeze-20463094`; branch: `production`; database: `neondb`.
- Restore snapshot: `snap-calm-credit-bdfp5tog` (created 2026-11-25T17:37:13Z).
- Read-only PostgreSQL baseline after snapshot: **9,306,112 bytes (9.306 MB / 8.875 MiB)**; five user base tables.
- Migration ledger remains at versions **1 (foundation)** and **2 (migration_integrity)**.
- BP04 migrations **0003–0012 have not been applied**; no BP04 source datasets or typed relational records have been uploaded. Production remains unchanged by BP04.
- The validated BP04 release remains 14 compressed datasets (29,434,820 bytes; 29.43 MB) and ten migrations. The PostgreSQL 18 disposable benchmark projected approximately 619,263,679 bytes (619.26 MB / 590.58 MiB) of incremental database growth; this is not a production measurement.
- The manual production workflow has not been dispatched. The production release must remain pending until the workflow is started from `main`, its required `DATABASE_URL` secret is available, and the workflow completes all migration, import, acceptance and repeat-import checks.

No production BP04 write is claimed by this checkpoint.


## BP04 Neon production upload — result (2026-11-25)

The manual production release workflow ran on `main` at commit `8854d66180a074f0e425d45803590ffbe14dc1a9` (run [45667318478](https://github.com/Joshuaogri/saltwater/actions/runs/45667318478)). The pre-write Neon restore snapshot was verified by the workflow: `snap-calm-credit-bdfp5tog`.

**Production data deployment succeeded; the workflow ended in failure only at the strict repeat-import storage-stability assertion.**

- Migrations **0003–0012** applied successfully; Neon migration ledger now contains versions 1–12.
- All **14/14** compressed source datasets imported.
- Package digest: `54090f74332c1d0fedb09b48ad1fd669b9d62c593c9a5c253e979cbafaf4a3be`.
- Compressed source archives: **29,434,820 bytes (29.43 MB)**; uncompressed source data: **558,602,287 bytes**.
- Source ledger: **1,950,923** source records; **1,422,202** typed mapped records; **0** cross-reference violations.
- Production acceptance: schema acceptance and import acceptance both passed.
- Neon now has **92 BP04 tables** in `sw_property` and **97 user base tables** overall.
- Pre-upload database size: **9,306,112 bytes (9.31 MB)**.
- Before repeat-import test: **624,893,952 bytes (624.89 MB)**.
- After repeat-import test as measured by the workflow: **625,033,216 bytes (625.03 MB)**, an increase of **139,264 bytes (0.139 MB)** during the repeat operation. The workflow's exact-size-equality guard therefore failed; do not record the repeat-import storage-stability check as passed.
- Latest live read-only measurement after the run: **625,811,456 bytes (625.81 MB / 596.82 MiB)**. This is **616,505,344 bytes (616.51 MB)** above the original baseline.
- All 14 dataset ledger rows and all 12 migration ledger rows are present in production.

The BP04 release is present and accepted in Neon. The outstanding item is to explain the small database-size delta during the repeat import, confirm row-count idempotency independently, and adjust the workflow's storage assertion if PostgreSQL maintenance/operation-ledger writes explain the delta. Do not re-import the package merely to retry the size assertion. No rollback was performed; retain the pre-release restore snapshot.


## BP04 storage architecture update — compressed archive only (2026-11-25)

The earlier BP04 Neon import was rolled back to its pre-release restore point at the user's request. Production is currently restored to **9,306,112 bytes (9.31 MB)**, with five original user tables, migration versions 1–2, and no BP04 schema or data. The restored production branch is `br-still-cloud-bdvaw8u4`.

The prior typed-row design stored the 14 compressed source files (29.43 MB) and also expanded 1,422,202 mapped source records into 92 relational tables. That previous representation measured approximately 616.51 MB of incremental Neon database growth. It is superseded for production use.

**Selected model:** store the 14 original gzip datasets exactly once in `sw_property.source_dataset_archive`, preserve release/dataset/collection provenance and exact source counts, and do not permanently materialise the 1.42 million typed rows. The dataset is decompressed and expanded in application memory only when requested through `runtime/bp04_archive_reader.py`; SHA-256 is verified before use. The original compressed archive remains the lossless source of truth. Domain tables remain empty for static BP04 source data; only genuinely changing game state should be stored as transactional records.

The disposable PostgreSQL workflow and manual-only Neon release workflow now select `--archive-only` and the new archive-only acceptance checks. The target is storage close to the 29.43 MB compressed package plus PostgreSQL metadata, TOAST and provenance overhead. The actual archive-only database size is **not yet measured**; do not reuse the former 628 MB typed-row benchmark as the new estimate. No Neon production write has been made as part of this change. The manual Neon workflow still requires fresh explicit user authorisation and a restore point.


## Verified archive-only storage benchmark — PostgreSQL 16 and 18 (2026-11-25)

The archive-only release workflow passed on both PostgreSQL 16 and PostgreSQL 18 in GitHub Actions run [45672135316](https://github.com/Joshuaogri/saltwater/actions/runs/45672135316), commit `a1836b83df980824a5291d7ed67b89cba5c624e9`.

| Measure | PostgreSQL 16 | PostgreSQL 18 (closest Neon benchmark) |
|---|---:|---:|
| Full disposable database size | 40,434,711 bytes (40.43 MB) | 40,875,711 bytes (40.88 MB) |
| Baseline before BP04 import | 9,306,112 bytes | 9,306,112 bytes |
| Incremental database growth | 31,128,599 bytes (31.13 MB) | 31,569,599 bytes (31.57 MB) |
| Compressed source package | 29,434,820 bytes (29.43 MB) | 29,434,820 bytes (29.43 MB) |
| `source_dataset_archive` relation | 28,368,896 bytes | 28,368,896 bytes |
| Typed rows permanently imported | 0 | 0 |
| Repeat-import size change | 0 bytes | 0 bytes |
| Repeat-import row mutations | 0 | 0 |

The import preserved all 14 archives, 105 source collections and 1,950,923 source records. The archive-only acceptance test passed on both PostgreSQL versions, and the second import left database size unchanged. Against the previous typed-row production growth of 616,505,344 bytes, the PostgreSQL 18 archive-only benchmark reduces incremental growth by approximately **94.88%** (about 19.5 times smaller).

The 31.57 MB figure is incremental database growth in the disposable PostgreSQL 18 benchmark, not the production measurement. The later archive-only production deployment is measured separately in the latest status section at the top of this README.


**Safe default:** the importer now defaults to `compressed_archive_only` even when no storage flag is supplied. The previous expanded representation is available only through the explicit `--typed-relational` option for disposable benchmarking; the importer itself rejects typed-relational mode when the target database is `neondb`. The production workflow also explicitly passes `--archive-only`.

## BP-02 frontage exception dispositions and full acceptance audit

The five P1 BP04 address/frontage exceptions have been examined against the SW-GEO-V1 road-reserve and parcel-boundary candidate geometry. Three have a single geometric parcel-frontage candidate (North Coast Road for two parcels; South Coast Road for one), but all three sites have no candidate building, so the original source address road is preserved and no address correction is promoted. The other two have only point-contact proximity to Customs Bridge / Harbour Bridge road reserves; bridge point contact is not street frontage.

New implementation: `runtime/bp02_address_frontage_exception_resolution.py`. The consolidated, read-only BP-02 audit combines city/road geometry, all 420 parcel dossiers, address/property references, 2,948 building-boundary access candidates, connector topology and route-corridor candidate checks.

The first full audit identified 26 connector centrelines crossing other generated building footprints. The asset generator now performs a final connector reconciliation after all buildings are generated, preserving access-point locations and selecting only parent-property-contained candidate lines that do not intersect any other building footprint (including point contacts, matching the independent audit's strict intersection rule). A Shapely spatial index limits each candidate check to nearby building footprints. Where a direct line is obstructed, a visibility-graph pathfinder now searches for a multi-segment route around buffered building/water obstacles while remaining inside the parent parcel; if no path exists, the original candidate remains blocked. Independent route-corridor audit [run 45696915823](https://github.com/Joshuaogri/saltwater/actions/runs/45696915823) passed all 7 checks for 2,948 candidates: zero mapped-building intersections and zero mapped-water intersections. The consolidated full BP-02 acceptance audit [run 45696915906](https://github.com/Joshuaogri/saltwater/actions/runs/45696915906) subsequently passed all structural checks: all 420 property/address source links resolve, all 2,948 building access/connector candidates pass, and all five frontage exceptions have geometry dispositions. Its explicit result is `STRUCTURAL_PASS_OPERATIONAL_RELEASE_BLOCKED`: no canonical addresses or operational access points were promoted, and operational geography/access approval remains blocked. Independent connector-road topology audit [run 45696857582](https://github.com/Joshuaogri/saltwater/actions/runs/45696857582) also passed all 9 checks and 6 regression tests: 2,944 frontage connectors, four separate point-contact/proximity connectors and zero unlinked candidates or topology mismatches. Direct-connector feasibility audit [run 45696857695](https://github.com/Joshuaogri/saltwater/actions/runs/45696857695) passed all 7 checks: 2,926 straight-line candidates are geometrically clear and 22 remain explicitly classified as blocked direct lines; the visibility-graph detours are assessed separately by the passing route-corridor audit. The regenerated Stage E inventory [run 45697967671](https://github.com/Joshuaogri/saltwater/actions/runs/45697967671) also passed all 12 generator regressions and produced 420 properties, 1,474 buildings, 27,730 premises, 180,733 units and 2,948 each of access-point/connector candidates, plus 213,305 profiles and 1,204,450,591 bytes of uncompressed detail in a 17,789,101-byte gzip payload (~67.7:1). The manifest resolves all 100 source entity-code mappings and creates zero operational IDs, addresses or access approvals. The artifact is CI/GitHub-only; no Neon upload was made. Disposable PostgreSQL import, idempotency, storage and restore acceptance are still running. A dedicated synthetic detour regression also passed. This does not establish constructed or operational access.

Operational release remains blocked: SW-GEO-V1 is still a design baseline; canonical operational addresses and operational access-point approvals are absent. No Neon writes or property archive uploads were performed. under separate audited incident/address grants and hands reviewed candidates to BP12's `add_incident_location` writer. BP12 appends an `INCIDENT_LOCATION_ADDED` simulation event and immutable location record, retains caller/source and BP04 address provenance separately, validates runtime and incident state, and enforces idempotency. No spatial ID is inferred from an address. Regression tests cover authorisation, provenance and the writer handoff.

The officer-only lookup adapter also has regression coverage for revoked sessions and audit-store outages: revoked sessions are denied, and an otherwise authorised lookup is denied if its durable audit decision cannot be recorded. Dispatch/investigation address resolution remains a read-only, permission-checked address dossier operation; no operational access or canonical geography is inferred.

The lookup integrity checks now extend through the corporate/business register: parent-company references must resolve and remain acyclic; registered addresses must exist; each declared primary establishment must belong to that business; and establishment property/building/premises/unit/address links must agree across the physical hierarchy. Added regression tests for missing parent companies, self-parenting/cycles, mismatched primary establishments, missing registered addresses and conflicting establishment location links. This remains read-only and process-local; no Neon writes or operational geography promotion occur.

The archive-backed lookup now fails closed on dangling or inconsistent property/building/premises/unit/access-point relationships. It validates parent-child hierarchy across the detailed property stack before exposing records to gameplay, preventing an apparently valid address or establishment lookup from masking broken physical-location links. Regression coverage includes missing premises buildings, unit-to-premises conflicts and access-point-to-unit conflicts. This remains read-only and process-local; no Neon writes or operational geography promotion occur.

**Release boundary:** Stage E's detailed disposable database acceptance now passes, but generated physical detail and connector geometry remain unapproved candidates. BP04/BP02 gameplay integration and operational geography release gates remain open. This result does not authorise Neon deployment.

## Canonical constraints

- Country and city: **Saltwater**.
- One sovereign city-state; no external playable cities or territory.
- Maximum population: **10,000 living people total**, police included; opening baseline 9,000 residents + 500 police = 9,500, leaving 500 unused headroom.
- Primary experience: exceptionally detailed, permanently text-first simulation; maps and selected graphics are optional.
- Primary simulation: the police service and its operations, supported by a credible, interconnected society.
- Persistent database: Neon PostgreSQL.
- Source, migrations and documentation: this GitHub repository.
- Player interface and AI partner: ChatGPT.

## Development principles

- Preserve meaningful detail and exact recoverability while minimising storage use; the simulation is text-first and narrative may be extensive.
- Prefer the smallest lossless representation (compact JSON, short keys/IDs/enums, normalisation, references and event/delta records); compress structure, never meaning.
- Avoid every unnecessary byte: duplicate payloads, repeated boilerplate, derivable fields, needless indexes/snapshots and oversized database blobs.
- HARD GATE: before every Neon migration, schema change, seed/import, bulk write or upload, calculate and show expected incremental bytes/MB, assumptions/range, current baseline and projected total; wait for explicit user approval. If the estimate is not credible, do not deploy—benchmark first.
- After approval, measure actual database/table/index/TOAST growth and compare it with the estimate.
- Normalise shared facts and reference them rather than duplicating them.
- Use compact identifiers where useful; never sacrifice human-readable records or provenance.
- Record meaningful state changes and chronology without indiscriminate full snapshots.
- Measure actual database growth after each approved deployment; report actual delta against the pre-deployment estimate.
- Do not upload simulation seed data until the schema, validation and storage baseline are ready.
- Never commit credentials. The Neon connection string belongs in a protected secret named `DATABASE_URL`.

## Current database-integrity implementation

BP38-01 is implemented on `main`; disposable PostgreSQL validation passed in [run 45428332686](https://github.com/Joshuaogri/saltwater/actions/runs/45428332686). BP38-02's independent PostgreSQL 18 replay and live baseline comparison passed in [run 45437263676](https://github.com/Joshuaogri/saltwater/actions/runs/45437263676). The guarded version-1 checksum adoption was separately approved, executed and verified. Migration 0002 was then separately approved and applied to Neon production on 2026-11-24. Both constraints and the fingerprint column are present; the authoritative ledger now contains versions 1 and 2 with exact source checksums, and version 2 has a recorded live schema fingerprint. The new [read-only Neon migration-ledger workflow](.github/workflows/neon-migration-ledger-readonly.yml) ran the committed Python migration runner against production with server-enforced read-only mode; checksum and live fingerprint verification passed in [run 45444735686](https://github.com/Joshuaogri/saltwater/actions/runs/45444735686). The migration source is 726 bytes; database size remained 9,306,112 bytes (0-byte measured delta). See [BP38-01 migration 0002 execution evidence](docs/implementation/test-evidence/BP38-01-run-0002.md). The push-triggered Neon production deployment workflow remains disabled; the new workflow is read-only and never applies migrations.

Package: [BP38-01 — Database Integrity and Migration Foundation](docs/implementation/approval-packages/BP38-01-database-integrity-and-migration-foundation.md). [Read-only Neon legacy-baseline verification](docs/implementation/test-evidence/BP38-01-legacy-baseline-read-only-verification.md).


## Repository layout

- `db/migrations/`: ordered PostgreSQL migrations.
- `docs/architecture/`: architecture decisions and storage design.
- `docs/operations/`: operational procedures and measurement records.
- `docs/implementation/`: dependency-led implementation sequence and delivery gates.
- `.github/workflows/`: automated checks.

## Current status

The **platform foundation and BP04 compressed source archive release are deployed**. The full police simulation runtime and several domain interfaces remain in development.

- Neon project: Saltwater (`misty-breeze-20463094`), production branch `br-still-cloud-bdvaw8u4`, database `neondb`.
- Production migration ledger contains versions 1–12; BP04 migrations 0003–0012 are applied.
- BP04 production archive release passed in [workflow run 45675735246](https://github.com/Joshuaogri/saltwater/actions/runs/45675735246). It stores 14 compressed datasets, 105 collections and 1,950,923 source records (29,434,820 compressed bytes); zero typed static source rows were materialised.
- Read-only Neon verification on 2026-11-25 measured `pg_database_size` at **41,525,248 bytes (41.53 MB / 39.60 MiB)**, an increase of **32,219,136 bytes (32.22 MB)** over the 9,306,112-byte pre-BP04 baseline.
- The BP04 schema contains 92 base tables. Archive/provenance ledgers contain the deployed source package; the other static domain tables remain empty by design under the archive-only storage model.
- BP04's full division acceptance audit **has not passed**. The process-local lookup API is integrated with authenticated player commands and ChatGPT's bounded tool contract. The separate police adapter requires an active officer principal, live policy grant and durable audit; no production grants have been provisioned, so it remains default-deny. BP02 now supplies 420/420 stable parcel design IDs and 420/420 stable address design IDs, reconciled to all property and road/district/neighbourhood references. Operationally approved canonical parcel/address identities remain zero because geometry, frontage and address placement have not passed the operational geography release gate. The latest frontage audit found 415 road matches, 3 road conflicts and 2 parcels with no frontage candidate; see the integration record for the exact IDs. See [lookup design](docs/implementation/BP04-gameplay-lookup.md), [player/police/geography integration](docs/implementation/BP04-player-police-geography-integration.md) and [full acceptance audit](docs/implementation/test-evidence/BP04-full-acceptance-audit-2026-11-25.md).
- No resident, police-personnel, case or evidence production seed records have been loaded. The 10,000-person cap remains binding. Production simulation seeding beyond the approved BP04 archive release remains blocked.
- The storage/write gate remains mandatory for every future Neon write: measure the current baseline, estimate incremental bytes and MB/MiB with assumptions/range, show the projected total and wait for explicit user approval.

Provider-reported logical-size metadata is a different measurement from PostgreSQL `pg_database_size`; do not compare or substitute the two without an explicit metric definition.

## Latest canon decisions — 2026-11-24

- Adopted [SW-CANON-001 — Population Scope and Foundational Geography](docs/blueprint/decisions/SW-CANON-001-population-scope-and-foundational-geography.md).
- Population cap now has a closed distinct-person counting formula: usual residents ∪ persons physically present ∪ active Saltwater Police Service members; one person ID counts once. Opening target: 9,000 civilian residents + 500 police personnel = 9,500 unique people, 500 shared headroom.
- Foundational geography is fixed: one contiguous coastal island city-state, 12 km × 9 km fictional local grid, eastern harbour, eight districts and 24 neighbourhoods. Detailed map construction and routing validation remain implementation work.
- BP-02 and BP-03 updated; SW-DB-001 now references the adopted canon. BP04 now has a 10,000-business source registry baseline; full registry and gameplay acceptance remains open.
- The approved BP38-01 migration writes are complete; no operational geography import or simulation seed data has been authorised or performed.

## BP04-03 — citywide terrain/obstacle survey coverage grid

SW-TERRAIN-SURVEY-GRID-001 divides the fictional 12 km × 9 km city planning extent into 432 500 m coverage cells. Each cell carries district/neighbourhood lineage, generated property/building candidate references, road/route candidate coverage, terrain/water intersections and explicit evidence gaps for elevation and physical obstacles. Cells are coverage-planning units, not parcels or physical assets. No terrain or obstacle facts, survey priority, passability or access are inferred. Workflow: .github/workflows/bp04-03-terrain-obstacle-survey-coverage-grid.yml.

## BP04-03 — detailed terrain and physical-obstacle register

The geometry-derived SW-TERRAIN-OBSTACLE-DETAIL-001 register (runtime/terrain_obstacle_detail_register.py) preserves source terrain polygons and adds planar area/perimeter, bounding boxes, centroids, boundary rings/edges, edge lengths/bearings, district/neighbourhood overlays and lineage-linked route-centreline intersections. Obstacle classes remain separately inventoried; classes without supplied source records are marked as coverage gaps, never asserted absent. No elevation, gradient, material, condition, passability, legal access or egress is inferred. Workflow: .github/workflows/bp04-03-terrain-obstacle-detail-register.yml. Generated artifact is read-only and is not an operational terrain/obstacle layer.

## BP04-03 — terrain, elevation and physical-obstacle source model

The read-only source model [SW-TERRAIN-OBSTACLE-001](runtime/terrain_obstacle_source_model.py) inventories terrain and physical-obstacle evidence without inventing missing facts. It recognises elevation surfaces, contours, spot elevations, terrain features, retaining structures, walls, fences, gates, drainage structures and natural/other barriers. Current SW-GEO-V1 supplies one terrain polygon (Central-Western Ridge) and no elevation surfaces, contours, spot elevations or mapped physical-obstacle records. This is a source-coverage statement, not proof that absent features do not exist. Elevation, vertical datum, gradient, obstacle dimensions/material/condition, traversal, accessibility, legal access and emergency egress remain null, unknown or not assessed. The 47 existing route-centreline/ridge intersections remain contextual only. No operational terrain/obstacle records, route approvals or Neon writes are created. Regression workflow: [BP04-03 Terrain and Physical Obstacle Source Inventory](.github/workflows/bp04-03-terrain-obstacle-source-inventory.yml).

## Detailed map and road network — SW-GEO-V1

- [Open the master Saltwater map (SVG)](docs/maps/saltwater-master-map-v1.svg)
- [Machine-readable geography and routable road graph](data/geography/saltwater-geography-v1.json)
- [Map register, network specification and limitations](docs/maps/README.md)

The initial map baseline contains 8 districts, 24 neighbourhoods, 42 named roads, 367 junction nodes, 685 connected road/bridge segments and 5 named route definitions. It uses the fictional `SW-LOCAL-01` metre grid. Structural graph checks passed at generation time; parcel/address/building coverage and full BP-02 operational acceptance remain outstanding. This is planning-grade fictional geometry, not survey-grade, and no Neon production data was changed.


## Core universal naming standard — SW-UNS-001

**Adopted 2026-11-24 as a core, mandatory Saltwater foundation.** The standard applies to all 44 blueprint divisions and every named entity: people, roads, places, properties, buildings, businesses, organisations, police units, vehicles, equipment and operational records. One shared registry must enforce permanent entity IDs, globally unique canonical names, normalization, exact/near-duplicate checks, reservations, concurrency safety, aliases and immutable historical name records. The sole user-approved exception allows the sovereign territory and playable city to both retain the exact name Saltwater, with separate IDs; no other entity may use that name. Domain-specific naming vocabularies are allowed; domain-specific bypasses or competing registries are not.

- [Read SW-UNS-001 — Universal Naming Standard](docs/blueprint/decisions/SW-UNS-001-universal-naming-standard.md)
- Existing adopted names must be preserved and registered before new names are generated, including the eight districts, 24 neighbourhoods and 42 named SW-GEO-V1 roads.
- Policy adoption is complete. SW-NAM-001 is approved; core disposable SQL/Python/PostgreSQL acceptance passed in runs `45409845359` and `45410340222`. Final storage-detail run `45411243093` passed. Populated registry relations total 12,279,808 bytes (4,546,560 heap; 7,643,136 indexes; 90,112 TOAST/auxiliary). No Neon production changes were made or authorised.

### Universal naming implementation

The adopted core naming policy is being implemented through [SW-NAM-001 — Universal Naming Registry, Generator and Enforcement](docs/implementation/approval-packages/SW-NAM-001-universal-naming-registry-generator-and-enforcement.md). Committed slices include disposable proposal `0009`, Python normalization/registry and transactional PostgreSQL adapter, deterministic candidate generation, geography/person adapters, dry-run canon inventory, immutable generator manifests, SQL/Python/concurrency/rollback/restore tests and disposable PostgreSQL CI. **Core regression and disposable identity mapping are verified**: full Python and PostgreSQL jobs passed in [run 45441551968](https://github.com/Joshuaogri/saltwater/actions/runs/45441551968), including all 100 geography identity-map entries and naming reservations, 10,000-person cap boundary, access controls, checkpoint-manifest capture and backup/restore. The full 10,000-person fixture grew its disposable database by 2,334,720 bytes (2.226562 MiB); full database size was 32,250,903 bytes. At the full fixture stage, 10,111 name reservations occupied 8,642,560 bytes total (854.77 bytes/reservation). Detailed heap/index/TOAST figures and the restore manifest are in [SW-NAM-001 run evidence](docs/implementation/test-evidence/SW-NAM-001-run-0001.md). The checkpoint validator intentionally remains partial: business-minimum, player-absence-freeze and permission/hidden-truth gates were not executed. BP-04 and other operational entity adapters remain NOT CONNECTED until their authoritative schemas exist. The 100-entry identity map is validated only in disposable PostgreSQL; no operational canon import, production spatial-ID allocation or Neon seed/write occurred. See [SW-NAM-001 integration coverage audit 0001](docs/implementation/test-evidence/SW-NAM-001-integration-coverage-audit-0001.md) for connected/NOT CONNECTED domain coverage.


## BP40-02 — stable player command catalogue and typed parser

The user approved BP40-02 on 2026-11-24. The implementation is committed directly to `main`: [canonical catalogue/parser](runtime/player_commands.py), [player command interface](runtime/player_interface.py), authorization gateway, trusted host adapter and ChatGPT tool handler all use the same parser and command metadata. The registry contains the existing fourteen command forms only; no new police-domain capability or permission was added. Typed parse failures distinguish empty, malformed, unknown, missing-argument, invalid-argument-count and invalid-value input. Help and [machine-readable tool schema](docs/integration/player-command-tool.schema.json) expose the same contract. The full Python regression, dedicated parser acceptance, full disposable PostgreSQL regression and database migration validation passed; see [BP40-02 run 0001 evidence](docs/implementation/test-evidence/BP40-02-run-0001.md). The registry and parse-result structures are immutable. No Neon production change occurred.


## SW-DB-001 — canonical world provisioning (approved; disposable implementation verified)

The user approved SW-DB-001 on 2026-11-24 for GitHub main development and disposable PostgreSQL testing only. [Proposal 0010](db/proposals/0010_canonical_world_provisioning.sql) extends the existing universal naming registry with a business adapter and adds business-owned identity/lifecycle history plus immutable provisioning-batch metadata. The deterministic [opening fixture](tests/pkg001/sw_db_001_world_fixture.sql) targets 9,000 resident-cohort people + 500 police-subset-cohort people = 9,500 distinct living identities, leaving 500 headroom, and 10,000 distinct named businesses. The police subset and business category/legal-form/staff-band variety are test-only labels; no police appointments or detailed geography are fabricated, and business sites remain unassigned. Generator v2 creates deterministic pronounceable pseudowords, while the immutable batch manifest records source revision and separate person/business SHA-256 content checksums. [Manifest](data/fixtures/sw-db-001-opening-manifest.json) and [candidate model](docs/architecture/SW-DB-001-canonical-world-data-model.md) document the boundaries. The [dedicated disposable workflow](.github/workflows/sw-db-001-disposable.yml) passed both Python and PostgreSQL 16 jobs in [run 45456851773](https://github.com/Joshuaogri/saltwater/actions/runs/45456851773). It verified the 9,500-person/10,000-business fixture, 10,000 unique business names, 0-byte same-manifest repeat delta, both restored content checksums, backup/restore, 9,999-person concurrent final-slot admission, exact 10,000 cap and world tick 0. Proposal 0010 schema growth was 278,528 bytes; the opening fixture added 39,632,896 bytes (37.796875 MiB) in 169.295 seconds (115.18 fixture rows/second). Person-domain relations totalled 5,259,264 bytes (553.61 bytes/person); business-domain relations 4,399,104 bytes (439.91 bytes/business). Full measurements and limitations are recorded in [SW-DB-001 run 0001 evidence](docs/implementation/test-evidence/SW-DB-001-run-0001.md). This is disposable test evidence only: no Neon production connection, migration, seed, import, upload or configuration change occurred; production write authority remains NONE.


## BP04 — physical built-world records

[BP04-01 — Property, Building, Premises, Unit and Access-Point Identity Foundation](docs/implementation/approval-packages/BP04-01-property-premises-identity-foundation.md) is approved, implemented and verified on `main`. The corrected disposable PostgreSQL 16 workflow [run 45477359265](https://github.com/Joshuaogri/saltwater/actions/runs/45477359265) passed both Python regression and full disposable PostgreSQL acceptance. The corrected acceptance checks all three access-point creation-history rows, including the deliberately unnamed access point.

**BP04-02 — Deep Physical Asset and Space Profiles** is approved and implemented as a disposable-only candidate migration `0012_bp04_physical_asset_detail_profiles.sql`. It adds versioned typed profiles for all five physical identity types; provenance-rich measurements; building levels/components; premises rooms; utility systems; physical features; element-level condition assessments; defects; and knowledge-state assertions. Profiles and child records are append-only; revisions are additional effective-dated records. Its acceptance tests and workflow integration are committed on `main`; full Python regression and disposable PostgreSQL 16 acceptance passed in [run 45478587738](https://github.com/Joshuaogri/saltwater/actions/runs/45478587738). The completed run applied proposals 0002–0012, measured migration-only schema growth, provisioned and measured the deterministic fixture, passed BP04-01 and BP04-02 SQL acceptance, verified idempotency, query latency and backup/restore, passed the concurrent final-slot population-cap test, and completed final SW-DB-001 reconciliation. Detailed byte-level step output was not exposed by the available workflow API response, so no new exact BP04-02 storage figure is asserted here. See [BP04-02 run 0001 evidence](docs/implementation/test-evidence/BP04-02-run-0001.md).

**Mandatory physical-record depth:** property, building, premises, unit and access point records must be extensive, structured and individually meaningful. Do not stop at IDs and names. Capture applicable classification/use, physical form, dimensions and measurement basis, floor/space structure, materials/components, utilities/services, facilities, condition by element, defects/hazards, accessibility, security/physical controls, access modes/restrictions, capacity/suitability, lifecycle and inspection/maintenance history. Every material fact must retain source/provenance, confidence/quality and recorded/effective chronology. Unknown, not assessed, not applicable, not present and measured zero must remain distinct. Use typed, normalised child records; do not collapse detail into unstructured notes or one oversized JSON field. Do not invent missing facts or false precision.

The detailed profile model does **not** populate the actual Saltwater property inventory, ownership/tenancy/occupancy, or business operators. No actual Saltwater property/building/premises/unit/access-point population has been seeded. BP04-02 passed full Python and disposable PostgreSQL 16 acceptance in [run 45478587738](https://github.com/Joshuaogri/saltwater/actions/runs/45478587738); see [BP04-02 run evidence](docs/implementation/test-evidence/BP04-02-run-0001.md). [BP04-03 — City Physical Inventory and Geography-Linked Population](docs/implementation/approval-packages/BP04-03-city-physical-inventory-and-geography-linked-population.md) was approved on 2026-11-24 for GitHub `main` implementation and disposable PostgreSQL testing only. Stage A's read-only geography audit is committed in [runtime/geography_readiness.py](runtime/geography_readiness.py), with regression tests in [test_geography_readiness.py](tests/pkg001/test_geography_readiness.py) and a dedicated [GitHub Actions workflow](.github/workflows/bp04-03-geography-readiness.yml). The audit checks the committed district/neighbourhood/road/network structure and keeps the 100 resolved stable source-to-entity_code mappings, absent parcel/address fabric and absent footprints/entrances explicit. It cannot approve BP-02 geography. The audit passed in [run 45480493889](https://github.com/Joshuaogri/saltwater/actions/runs/45480493889): 28/28 checks passed; all 100 source identities are mapped one-to-one to stable entity_code values; no spatial IDs were fabricated or assigned. See [BP04-03 Stage A run evidence](docs/implementation/test-evidence/BP04-03-stage-a-run-0001.md) and the [100-record reconciliation register](data/geography/bp04-03-stage-a-source-spatial-reconciliation-v1.json). Stage A structural audit is verified; all 100 source identity mappings are resolved to stable entity_code values. Database-specific spatial_id surrogates are resolved by entity_code at materialisation. Stage B now has a BP-02-owned candidate schema in [proposal 0013](db/proposals/0013_bp02_parcel_address_candidate.sql), with parcel profiles, structured address locators/frontage, parcel lineage, address aliases, kind guards, checksum verification and append-only controls. Its Python and disposable PostgreSQL acceptance passed in [run 45481959712](https://github.com/Joshuaogri/saltwater/actions/runs/45481959712); schema-only growth was 294,912 bytes and the proposal source is 10,668 bytes. See [Stage B run evidence](docs/implementation/test-evidence/BP04-03-stage-b-schema-run-0001.md). The schema foundation is verified. Stage B now also has a deterministic [parcel/block candidate generator](runtime/parcel_candidate_generator.py), five regression tests and a dedicated [candidate workflow](.github/workflows/bp04-03-parcel-candidates.yml). Run [45482818681](https://github.com/Joshuaogri/saltwater/actions/runs/45482818681) passed: 396 block-scale candidates across all 24 neighbourhoods; 36 water-conflict cells excluded; 392 road-edge matches and 4 frontage-unresolved candidates. The generated artifact is 11,656 bytes compressed and has manifest SHA-256 `6afc12c8e27717523bb581057da8c936481b1950faa5703f52bb5e7560e8cba4`; see [Stage B candidate evidence](docs/implementation/test-evidence/BP04-03-stage-b-parcel-candidates-run-0001.md). These are 500m planning block candidates, not final cadastral parcels. The generator was refined to calculate exact water polygon-to-cell intersection area for the current single-ring SW-GEO-V1 water polygons (Sutherland–Hodgman clipping); unsupported holes/geometry fail closed. Refined [run 45483557867](https://github.com/Joshuaogri/saltwater/actions/runs/45483557867) passed all 7 tests, retained 396 candidates / 36 excluded water cells / 392 road-edge matches / 4 frontage-unresolved, and emitted manifest SHA-256 `4da7999ef7b5f98b3b1214096f11fbce633317ae38585ca231f6f8131c3c39bf`. Its artifact is 11,815 bytes compressed: [candidate artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45483557867/artifacts/14962966036). Evidence: [Stage B candidate run 0001](docs/implementation/test-evidence/BP04-03-stage-b-parcel-candidates-run-0001.md). The generator now also validates candidate containment and pairwise interior overlap: 432 source grid cells reconcile to 396 candidates plus 36 water-excluded cells; zero candidate overlaps and zero out-of-neighbourhood candidates. Eight Python tests passed in [run 45483804394](https://github.com/Joshuaogri/saltwater/actions/runs/45483804394). Latest manifest SHA-256 `83ec53dc09f51483110e1e564b82919d2da63a0f5c5adcd92b42e04bf508f85f`; artifact size 12,033 bytes compressed: [artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45483804394/artifacts/14962257890). This validates generated candidate rectangles only, not cadastral topology. The 15m road-reserve inset remains provisional; the unallocated area is not classified as road, public space or developable land. Road access, land-use capacity and full parcel topology remain. No spatial IDs or canonical addresses were assigned; all 100 source identities are resolved to stable entity_code values; database-specific spatial_id surrogates are looked up during materialisation. No database or Neon production write occurred.


BP04-03 Stage B now imports the 396 generated candidate parcels into disposable PostgreSQL 16 through [the guarded importer](runtime/parcel_candidate_importer.py). [Run 45484639045](https://github.com/Joshuaogri/saltwater/actions/runs/45484639045) passed: 396 candidate identities, 396 checksummed geometry versions and 396 parcel profiles; zero address identities; repeat import inserted zero rows and had 0-byte database growth. First import added 1,187,840 database bytes in the disposable CI database (739.125 ms); proposal 0013 schema growth was 294,912 bytes and its SQL source was 10,668 bytes. Full [ingestion evidence](docs/implementation/test-evidence/BP04-03-stage-b-disposable-ingestion-run-0001.md). These are candidate records only; no operational geography approval, canonical addresses, or Neon writes occurred.


BP04-03 Stage C road-centreline and road-reserve design is now resolved and verified in [run 45487528624](https://github.com/Joshuaogri/saltwater/actions/runs/45487528624). Both bridge lengths now reconcile to 2,019.804m from their stored geometry. Fictional canonical standard SW-RDS-V1 defines 18m local streets, 24m district connectors, 30m primary arterials and 24m bridges. Deterministic geometry generated all 685 segment corridor polygons; zero width or bridge-length exceptions remain. The 42-road, 685-segment, 367-node network remains connected with zero degree/membership/endpoint mismatches. Segment polygons intentionally overlap at junctions and must be dissolved before unique reserve-area calculations. The preserved road register is 23,915 compressed bytes ([artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45487528624/artifacts/14962764058)); [full evidence](docs/implementation/test-evidence/BP04-03-stage-c-road-centreline-audit-run-0001.md).


BP04-03 Stage C parcel coverage area reconciliation passed in [run 45486168411](https://github.com/Joshuaogri/saltwater/actions/runs/45486168411). The 24 neighbourhoods total 108,000,000 m² (432 grid cells); 396 candidate parcel interiors total 87,476,400 m²; exact water intersections in 36 excluded cells total 5,740,000 m². The 14,783,600 m² unallocated balance is decomposed into 11,523,600 m² of provisional 15m inset residual and 3,260,000 m² non-water area inside water-hit cell envelopes. Area balance delta: 0 m². These residuals remain unclassified, not assumed to be roads or developable land. The per-neighbourhood audit is retained as a 1,713-byte compressed [workflow artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45486168411/artifacts/14964432302). [Full evidence](docs/implementation/test-evidence/BP04-03-stage-c-parcel-coverage-area-run-0001.md).


BP04-03 Stage C road-reserve dissolve and neighbourhood-boundary reconciliation passed in [run 45488230508](https://github.com/Joshuaogri/saltwater/actions/runs/45488230508). The 685 segment corridor polygons dissolve into one connected road-reserve geometry of 7,057,146.032 m²; 140,804.555 m² of duplicate junction overlap is removed. The dissolved reserve lies entirely inside the city boundary. All 24 neighbourhood polygons exactly partition the 108,000,000 m² city: zero overlap, zero gap, zero outside area. Neighbourhood road-reserve allocations sum to 7,057,146.032 m² with a 0 m² difference. The topology artifact is 9,850 compressed bytes ([artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45488230508/artifacts/14964976654)). [Full evidence](docs/implementation/test-evidence/BP04-03-stage-c-road-centreline-audit-run-0001.md). Next: regenerate parcel candidates against the dissolved fictional road-reserve and water geometry, replacing the provisional 15m inset.


**BP04-03 Stage D geometry-derived parcel candidates — supersedes the earlier 396-cell / provisional 15m-inset candidate layer:** [Disposable PostgreSQL run 45490203072](https://github.com/Joshuaogri/saltwater/actions/runs/45490203072) and [candidate regression run 45490210942](https://github.com/Joshuaogri/saltwater/actions/runs/45490210942) passed. The generator now subtracts the actual dissolved SW-RDS-V1 road reserve and mapped water geometry from each 500m source lineage cell, then splits the remaining land into deterministic valid polygon components. It creates **420** parcel candidates; **418** have a geometric road-reserve edge-contact candidate. The 36 water-intersected cells are no longer excluded wholesale. Area reconciles exactly: 108,000,000.000 m² = 7,057,146.032 m² road reserve + 5,605,030.589 m² water outside road reserve + 95,337,823.379 m² candidate land; delta 0 m² across all 24 neighbourhoods. Candidate manifest: 28,513 compressed bytes ([artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45490203072/artifacts/14965647916)). Disposable PostgreSQL inserted 420 candidate identities, 420 geometry versions and 420 parcel profiles; first-import growth 1,081,344 bytes. Repeat import inserted zero rows and produced 0-byte growth. Zero canonical addresses were created. The first generic labels tripped SW-UNS-001 near-duplicate checks; deterministic unique fictional names now pass through the existing registry without bypassing it. [Full Stage D evidence](docs/implementation/test-evidence/BP04-03-stage-d-geometry-derived-parcel-candidates-run-0001.md). Next: detailed parcel dossier and boundary/frontage review before detailed property/building/premises/unit/access-point inventory. No Neon writes or operational geography activation occurred.


**BP04-03 Stage D detailed parcel dossiers and relationship layer completed:** [Run 45494991970](https://github.com/Joshuaogri/saltwater/actions/runs/45494991970) passed all eight Python suites (41 tests), disposable SQL acceptance, candidate import, dossier import and repeat-import idempotency. All 420 parcel candidates have measured dossiers (area, perimeter, compactness, centroid, representative point, bounds, ring counts, road frontage and water contact). Results: 418 parcels require frontage review; 2 have no road-edge contact; 1,374 parcel-to-road frontage relationships and unreviewed access-location candidates; 100 shared-boundary relationships; 32 water-adjacent parcels and 32 water relationships. These are candidate geometric relationships, not legal frontage, entrances, addresses or operational access points. The five-table append-only dossier schema is proposal 0014; source 10,311 bytes, disposable schema growth 368,640 bytes. First dossier import growth 1,859,584 bytes; repeat import 0 bytes. The 68,438-byte compressed dossier artifact is [preserved here](https://github.com/Joshuaogri/saltwater/actions/runs/45494991970/artifacts/14968720668). [Full evidence](docs/implementation/test-evidence/BP04-03-stage-d-parcel-dossiers-run-0001.md). Next: full-depth property, building, premises, unit and access-point inventory, with BP04-02 physical profiles and provenance. No Neon writes or operational addresses/access points were created.


**BP04-03 Stage E physical-asset candidate generation — first successful slice:** [Run 45502416189](https://github.com/Joshuaogri/saltwater/actions/runs/45502416189) passed seven regression tests and generated 420 property-site candidates, 384 contained building-footprint candidates, 1,327 floor-level premises, 15,199 units and 768 unreviewed building-boundary access-location candidates. 36 candidate properties have no building footprint and remain sites without fabricated structures. The 10,981,615-byte manifest is preserved as a 356,640-byte compressed [artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45502416189/artifacts/14970964187); SHA-256 `b710fcc3f5d08d24154ede08ebf99ec6a2f099a08c7f9c5d310c93ddb8aa30fe`. All five record classes have deterministic identities/names and provenance; geometry tests confirm each building footprint lies within its property candidate. This is candidate generation only: no asset records have yet been imported into PostgreSQL, and generated access points are not operational entrances. No addresses, operational spatial IDs, ownership, tenancy, occupancy or business assignments were created; all 100 source records resolve to stable entity_code values (100 resolved, 0 unresolved). Production spatial_id surrogates remain unassigned until activation and are looked up by entity_code. Full [Stage E evidence](docs/implementation/test-evidence/BP04-03-stage-e-physical-asset-candidates-run-0001.md). Next: complete BP04-02 profile and typed child-record depth, then disposable PostgreSQL schema/import/idempotency/storage/restore acceptance. No Neon production writes occurred.


**BP04-03 Stage E full physical-asset inventory — verified:** [Disposable PostgreSQL 16 run 45504985010](https://github.com/Joshuaogri/saltwater/actions/runs/45504985010) passed 15 Python tests, proposal 0015 migration, full import/SQL acceptance, repeat-import idempotency, query measurements and PostgreSQL 16 backup/restore. The hierarchy contains **420 property-site candidates, 384 building candidates, 1,327 premises, 15,199 units and 768 unreviewed access-location candidates**. All five identity classes have **18,098 typed BP04-02 profiles** and the inventory includes **181,915 detailed child records**: 34,624 measurements, 1,327 building levels, 4,608 components, 3,981 room allocations, 37,979 utility records, 21,417 features, 22,533 condition assessments and 55,446 knowledge-state assertions. There are no fabricated defect records. Proposal 0015 source SQL is 9,238 bytes and disposable schema growth 303,104 bytes. First asset import growth was 130,441,216 bytes; repeat import inserted zero records and grew 0 bytes. Full compressed inventory artifact: 1,523,057 bytes ([artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45504985010/artifacts/14971474446)). [Full Stage E evidence](docs/implementation/test-evidence/BP04-03-stage-e-physical-asset-inventory-run-0001.md).

All records remain generated, non-operational candidates. No canonical addresses, operational spatial IDs, confirmed entrances, ownership, tenancy, occupancy or business assignments were created. All 100 source records now map to stable entity_code values; database spatial_id is generated per database and looked up by entity_code. No Neon production connection, migration, seed, upload or activation occurred. Next dependency is BP-02 geography approval/versioning and source-to-spatial reconciliation before operational parcel/address/entrance identity creation.


## Geography source-identity reconciliation correction (2026-11-24)

The earlier statement that 100 source-to-spatial mappings remained unresolved is superseded. All **100 source records now map one-to-one to stable `sw_geo.entity.entity_code` values**: 8 districts, 24 neighbourhoods, 18 landmarks, 5 routes, 3 geography zones and 42 roads. The exact source record, entity type/kind, canonical name and parent are checked against SW-GEO-V1 by `runtime/geography_identity_reconciliation.py`; the readiness workflow runs regression tests for full coverage, duplicate IDs, incorrect parents and missing records. The reconciliation register now reports 100 resolved and 0 unresolved source-identity mappings.

PostgreSQL `spatial_id` is a GENERATED ALWAYS AS IDENTITY surrogate, so its integer is database-specific and must be looked up using the stable `entity_code` in each database. The portable source manifest intentionally does not freeze a disposable integer as a production ID. This correction resolves source-to-identity mapping; it does **not** approve SW-GEO-V1 for operational seeding, create parcel/address/entrance geometry, or authorize Neon writes. Those separate geography quality and activation gates remain.


**Disposable database materialisation proof:** the existing PKG-001 geography identity SQL fixture has now materialised all 100 `sw_geo.entity` rows and their database-generated `spatial_id` values, with all 100 version/parent/name relationships and naming-registry activations accepted. The materialisation step passed in [workflow run 45508321133](https://github.com/Joshuaogri/saltwater/actions/runs/45508321133). These integers belong to that disposable database only; production IDs remain unassigned and will be generated/looked up by `entity_code` when the operational geography version is activated.


### SW-GEO-V1 geometric QA extension (read-only)

A dedicated standard-library geometry and routing audit is added at `runtime/geography_geometry_audit.py`, with regression coverage in `tests/pkg001/test_geography_geometry_audit.py`. It checks polygon ring validity/self-intersection, point containment, neighbourhood-to-district containment, neighbourhood interior overlap and area balance, segment geometry against node coordinates and declared lengths, city-boundary containment, graph degree/connectivity, and route segment sequencing. The existing BP04-03 geography-readiness workflow runs this audit on relevant `main` changes. The audit is deliberately read-only and always reports operational seed eligibility as false; it does not approve SW-GEO-V1, validate cadastral parcels, establish legal frontage/access, or authorize Neon writes. Acceptance passed in [run 45510749489](https://github.com/Joshuaogri/saltwater/actions/runs/45510749489): 18 Python tests (4 structural, 9 geometric/routing, 5 identity) passed; the structural audit passed 28/28 checks with 100 resolved/0 unresolved source identities; the geometric/routing audit passed 10/10 checks with zero failed checks. City and neighbourhood areas both measure 108,000,000 m²; all 24 neighbourhoods are contained by their assigned districts with no interior overlaps; 367 road nodes form one connected component across 685 segments, with zero endpoint/length, degree or route-sequence exceptions. Full [SW-GEO-V1 geometric QA run 0001 evidence](docs/implementation/test-evidence/SW-GEO-V1-geometric-qa-run-0001.md). This remains read-only planning-geometry QA; no operational geography approval, cadastral/address/entrance acceptance or Neon write occurred.


### BP04-03 independent parcel-dossier geometry QA (read-only)

A second, independent geometry audit now verifies the 420 geometry-derived parcel candidates and their dossiers against the source road-reserve and water layers. It checks parcel containment/non-overlap, road-reserve/water exclusion, complete frontage-to-road-segment geometry, frontage candidate points, unreviewed access-location candidates, water adjacency and the complete measured parcel adjacency register. Successful [workflow run 45511739957](https://github.com/Joshuaogri/saltwater/actions/runs/45511739957) passed 8 regression tests and all 10 audit checks: 420 valid parcel dossiers, 95,337,823.379 m² candidate land, zero interior overlap, 1,374 frontage candidates, 1,374 unreviewed access-location candidates, 100 parcel adjacency relationships and 32 water adjacency relationships, with zero geometry exceptions. The audit is read-only; it creates no canonical addresses or operational access points and does not approve cadastral or operational geography. Full [BP04-03 parcel-dossier geometry QA evidence](docs/implementation/test-evidence/BP04-03-parcel-dossier-geometry-qa-run-0001.md). Next: reconcile parcel frontage/access candidates with the 768 building-boundary access-location candidates, retaining candidate-only status.


### BP04-03 building access and point-contact road-connection reconciliation

The four building-boundary candidates previously left without frontage links are now resolved through two separately classified road-reserve proximity candidates. The affected parcels are `BPC-SWD04N1-004-02` and `BPC-SWD08N1-018-02`, with point-only contact to bridge roads `SWR-B2`/`SWS-0685` and `SWR-B1`/`SWS-0684`. These are not conventional linear frontages: the dossier preserves them as `POINT_CONTACT_ONLY` proximity candidates, and all four building access candidates link to the corresponding same-parcel candidate. No building candidate remains without a road-connection candidate.

The latest independent audits passed: [parcel dossier QA run 45516792963](https://github.com/Joshuaogri/saltwater/actions/runs/45516792963) passed 9 tests and 10/10 checks (420 parcels, 1,374 true frontage candidates and 1,376 access-location candidates); [building access reconciliation run 45516972156](https://github.com/Joshuaogri/saltwater/actions/runs/45516972156) passed 7 tests and 8/8 checks (768 building-boundary candidates, four point-contact links, zero unlinked); [direct connector feasibility run 45516793015](https://github.com/Joshuaogri/saltwater/actions/runs/45516793015) passed 6 tests and 7/7 checks (768 geometric lines feasible under property/building/water checks, zero blocked and zero unlinked). A geometric line is not a driveway, entrance, legal access or traversable/emergency route.

Disposable PostgreSQL validation also passed: [Stage B/Stage D run 45517627917](https://github.com/Joshuaogri/saltwater/actions/runs/45517627917) and [Stage E run 45516793086](https://github.com/Joshuaogri/saltwater/actions/runs/45516793086). Proposal 0016 adds the separate point-contact/nearest-edge candidate classification; its measured disposable schema growth was 24,576 bytes (2,586-byte SQL source). Dossier import growth was 1,933,312 bytes with zero repeat-import growth. Stage E physical asset import growth was 130,744,320 bytes with zero repeat-import growth; 18,098 identities/profiles, 181,915 details, 1,572 geometry candidates, 420 site links and 16,910 relationships were accepted. All 100 stable source entity-code mappings resolved; zero remained unresolved. No production Neon writes or operational access/address records were created. The read-only Neon size remains 9,306,112 bytes.

Full [four-candidate resolution evidence](docs/implementation/test-evidence/BP04-03-four-unlinked-building-access-candidates-resolution-run-0001.md). Continue to keep frontage and point-contact proximity distinct; never promote either candidate to an actual entrance, driveway, legal access or emergency route without separate evidence and review.


### BP04-03 persistent access connector candidates

Stage E now extends beyond boundary-point proposals to a separate, provenance-bearing connector candidate for every building boundary access-location candidate. Each record carries stable candidate IDs, building access-point lineage, road/frontage or road-reserve relationship IDs, road and segment references, a two-endpoint LineString, measured straight-line length, coordinate reference, source manifest checksum and explicit review status. Construction, surface, gradient, barriers, pedestrian/vehicle suitability, accessibility, legal/public access and emergency-egress states remain unknown or not assessed. The four point-contact-only road-reserve cases remain distinct from frontage. The new append-only table is `sw_property.access_connector_candidate` (proposal 0017); disposable PostgreSQL acceptance requires 768 records, including four point-contact-only proximity records. No operational access or Neon production write is involved.


### BP04-03 persistent access connector candidates — validated

[Stage E disposable PostgreSQL run 45519143869](https://github.com/Joshuaogri/saltwater/actions/runs/45519143869) passed. The physical-asset inventory now persists 768 distinct connector candidates in the append-only `sw_property.access_connector_candidate` table, including four explicitly typed point-contact-only road-reserve connections. All 768 connector records retain road-segment lineage, two-endpoint LineString geometry, length, source manifest checksum and unknown/not-assessed physical and legal attributes. The corrected parcel dossier generator now supplies road segment IDs to every frontage access candidate; missing lineage is rejected before import.

The disposable PostgreSQL import added 130,973,696 bytes (130.97 MB decimal), including 768 connector records, 18,098 profiles and 181,915 typed detail records. The connector table occupies 1,007,616 bytes. Re-import of the same manifest grew the database by 0 bytes; backup/restore preserved the connector rows and manifest checksum. No operational access, canonical addresses, or production Neon writes were created. Neon remains 9,306,112 bytes on read-only measurement. See [complete connector candidate evidence](docs/implementation/test-evidence/BP04-03-persistent-access-connector-candidates-stage-e-run-0002.md).


### BP04-03 independent access connector road topology

The new independent topology audit [45519989730](https://github.com/Joshuaogri/saltwater/actions/runs/45519989730) passed all 9 checks and 6 regression tests. It verifies all 768 connector candidates against their building/property/parcel lineage, source road and segment identity, endpoint coordinates, measured length, parent-property containment and road-reserve geometry. It confirms 764 frontage connectors, four distinct point-contact-only road-reserve connectors, and zero unlinked connectors or topology exceptions. This remains geometric QA only; no built or legally usable access route is inferred and no Neon writes occur. See [independent topology audit evidence](docs/implementation/test-evidence/BP04-03-independent-access-connector-road-topology-run-0001.md).


### BP04-03 route-corridor centreline candidates — validated

[Route-corridor audit 45520905232](https://github.com/Joshuaogri/saltwater/actions/runs/45520905232) passed all 7 checks and 6 regression tests. The generated CI artifact contains 768 traceable two-dimensional centreline candidates: 764 frontage-linked and four point-contact/proximity-linked. There are zero unresolved connectors, mapped building intersections, mapped water intersections, originating-building interior crossings or road-reserve overlaps. Forty-seven centrelines intersect the mapped Central-Western Ridge terrain feature; this is recorded as context, not as an impassable obstacle. Other-building separation ranges from 31.894 m to 480.755 m, which is not available route width or a safety clearance.

No corridor width, available width, gradient, surface, barriers, accessibility, legal/public access or emergency-egress state is inferred: these remain null, unknown or not assessed. The artifact is CI-only; no production database write or operational access activation occurred. See [route-corridor candidate evidence](docs/implementation/test-evidence/BP04-03-route-corridor-centreline-candidates-run-0001.md).

### BP04-03 terrain evidence intake and append-only review register — validated

[Evidence intake and review workflow 45568025845](https://github.com/Joshuaogri/saltwater/actions/runs/45568025845) passed all **12 regression tests** and generated the source-linked [read-only evidence register artifact](https://github.com/Joshuaogri/saltwater/actions/runs/45568025845/artifacts/15001455213) (1,061 bytes; SHA-256 `4142a88b349ae143b9e82a9f1c3c0d47df2d72b7ee79519bc2709bfbef80c446`). The register preserves stable evidence/subject IDs, evidence type, capture and submission times, actor/source references and hashes, collection method, instrument/calibration references, observation geometry, typed measurements, uncertainty, attachment hashes, chain-of-custody, validity intervals, supersession and append-only reviewer decisions. Accepted evidence remains non-operational and cannot automatically activate a physical fact. Terminal review decisions cannot be overwritten; changes require new records. The baseline contains 0 submitted observations, 0 review events, 0 accepted evidence records and 0 operational facts activated; 7/7 model checks passed. No survey facts were fabricated and no production database writes occurred. Full [run 0001 evidence](docs/implementation/test-evidence/BP04-03-terrain-evidence-intake-review-register-run-0001.md). Next: field-survey work orders and inspection protocols tied to survey cells and source subjects, including measurement requirements and instrument/calibration controls.

## BP04-03 — canonical fictional physical world (SW-PHYS-V1)

Saltwater now has a populated, playable physical geography layer in `data/geography/saltwater-physical-world-v1.json`. This is authored fictional game canon, not an empty survey-candidate register. It defines **9 terrain zones** with elevation ranges on the fictional SW-VERT-01 datum, landform, substrate, ground condition and gameplay context. It also defines **32 physical assets** with individual IDs, names, neighbourhood placement, geometry, height, width, construction material, condition and continuity: retaining walls, masonry walls, fences, gates, reservoir embankment, culvert, open/covered drainage, quay walls, flood wall, seawall and acoustic barrier. The dataset includes movement rules for barriers, gates, drainage and road-based vehicle travel. Gates have game operating states and access schedules; the existence of a gate does not imply it is open. All coordinates are fictional SW-LOCAL-01 coordinates. Automated validation checks geometry, parent-neighbourhood containment, unique IDs, dimensions, materials, terrain datum and required feature categories. Workflow: [Saltwater Canonical Physical World Validation](.github/workflows/saltwater-physical-world-validation.yml).

## BP04 — canonical playable property world (SW-PROPERTY-WORLD-V1)

The property-world generator now converts Saltwater's deterministic fictional parcel/building design into persistent in-game records. It creates one canonical property identity and street address per generated property site; links buildings, floor-level premises, units and ownership interests; creates the referenced property-holding organisations; and supplies named rooms, building components, site boundary/yard/parking/drainage/waste features, utility connections, construction profiles and condition states. Building access locations become actual fictional entrances, service entrances and emergency exits, each linked to a constructed in-game route and a named road. The four proximity-only building connections are represented as shared access spurs rather than being left unserved. Sites without buildings receive a site gate and pedestrian/maintenance path. Units remain unassigned: this dataset creates no residents or businesses and cannot exceed the 10,000-person population cap. Output is stored as normalized, columnar textual JSON at `data/property/saltwater-property-world-v1.json` so repeated field names are stored once rather than repeated across thousands of unit/component rows. It is generated and committed to `main` by [Saltwater Canonical Property World Build](.github/workflows/saltwater-property-world-build.yml). Regression tests verify identity uniqueness, property/building/premises/unit lineage, addresses, ownership references, access-route continuity and population isolation.

### Current generated baseline

The committed property-world baseline contains **420 properties, 384 buildings, 1,327 premises, 15,199 units, 420 addresses, 804 access points and 804 constructed access routes**. It also contains 420 ownership interests and property-holding organisations, 4,992 building-component records, 5,308 named room records and 2,100 site-feature records. The 36 sites without a building have a site-level entrance and maintenance path. The four proximity-only cases are represented by shared access spurs. The unit register creates no residents and leaves all units unassigned. The columnar JSON file is **12,788,522 bytes** (about 12.19 MiB), down from the first expanded-object encoding of 23,833,730 bytes. The property-world workflow passed all **11 regression tests**, including parsing the persisted JSON file and checking the record totals.

## BP04 — 10,000-business registry foundation (SW-BUSINESS-REGISTRY-V1)

The next built-world layer is a deterministic registry of **10,000 distinct Saltwater businesses**, distributed across 15 fictional sectors. Every business receives its own immutable business ID, registered name, trading name, activity, legal form, size, employee band, operating status and establishment. Each establishment links to a canonical property, building, premises, unit and street address. Business-to-unit occupancy is stored as a separate time-valid relationship. Home-based businesses are used where needed to represent the full range of local economic activity without inventing extra properties or buildings. Employee bands do not create people: the registry creates zero residents, staff-person records or additional population. Textual columnar JSON is persisted at `data/business/saltwater-business-registry-v1.json` by [Saltwater 10,000 Business Registry Build](.github/workflows/saltwater-business-registry-build.yml).

### Current business registry baseline

The generated registry now contains **10,000 distinct businesses**, **10,000 establishments** and **10,000 business-to-unit links** across **15 sectors**. The baseline comprises 9,400 active, 286 seasonal and 314 temporarily inactive businesses. All 10,000 establishments resolve through the property/building/premises/unit/address hierarchy. No staff or resident person records are created. The compact columnar textual JSON file is **8,025,670 bytes** (about 7.65 MiB). The build and its regression tests passed; the registry is committed on `main`.

### Business operations and opening-hours records

The next textual world layer adds a weekly operating schedule for every registered establishment. Each business has seven explicit weekday rows (70,000 daily records across 10,000 businesses), local customer opening and closing times, service windows, staff shift patterns, delivery windows, operational status and an access reference for dispatch. Seasonal and temporarily inactive businesses receive appropriate closure states. These schedules do not create employee, customer or resident person records and do not change the 10,000-person city cap. Source: `runtime/business_operations_generator.py`; output: `data/business/saltwater-business-operations-v1.json`; regression tests: `tests/pkg001/test_business_operations_generator.py`.


## SW-CANON-002 — primate city and global international hub

**Adopted 2026-11-25 as binding canon across all 44 blueprint divisions.** Saltwater is the country's single primate city and dominant national and international metropolis: the highest national and international levels of government, diplomacy, corporate headquarters, banking and finance, entertainment, media, technology, healthcare, education, hospitality, professional services, trade and culture are concentrated here. Saltwater is also a world-leading maritime transit, export, transshipment and logistics exchange hub, comparable in strategic role to the Suez Canal and the world's major port, financial and commercial centres. It must never be modelled as an ordinary small city.

The 10,000-person permanent population cap remains in force, but it does not limit corporate scale, subsidiaries, establishments, institutional capacity, cargo throughput, vessel movements, passenger flows, international reach or economic activity. Transient people must continue to be counted under the existing population rules; this canon does not authorise bypassing the person cap. The existing 10,000-business registry is an initial baseline, not a ceiling on global corporate presence or a claim that all businesses are small. Future property, business, transport, port, airport, institutional, economic and police systems must reflect this global primate-city role.

- [Read SW-CANON-002 — Primate City and Global International Hub](docs/blueprint/decisions/SW-CANON-002-primate-city-global-hub.md)


## BP-04 — property ownership, tenancy and occupancy (SW-PROPERTY-TENURE-V1)

The first property tenure layer is generated and committed on `main`. The deterministic generator consumes the existing compact property-world and business-registry datasets rather than rebuilding geometry, and writes a compact columnar JSON dataset at [`data/property/saltwater-property-tenure-v1.json`](data/property/saltwater-property-tenure-v1.json) (10,833,623 bytes; approximately 10.33 MiB).

The dataset contains:
- 420 current property ownership interests, with chronological fictional acquisition and transfer events and resolvable historical owner organisations.
- 420 current property-management appointments, with separate property-management organisations where appointed.
- 10,000 current commercial leases, licences or operating concessions, each linked to its landlord, business, establishment, property, building, premises and unit.
- 2,500 expired historical agreement records, retained alongside current agreements.
- 10,000 current business occupancy records.
- 15,199 unit occupancy-state records. Residential units remain unallocated for the separate population-allocation process; no resident or other person records are created.
- Contractual rent bands and repair/renewal terms are references only. Rent postings, balances and accounting remain BP-34.

The output uses the same lossless textual columnar representation as the property-world baseline. The build reuses persisted canonical property and business datasets, avoiding duplicate geometry generation. Regression workflow [45577532056](https://github.com/Joshuaogri/saltwater/actions/runs/45577532056) completed successfully, including generation, six tenure regression tests and persistence to `main`.

## BP-04 — weekly business operating schedules (SW-BUSINESS-OPERATIONS-V1)

The weekly schedule layer is generated and committed at [`data/business/saltwater-business-operations-v1.json`](data/business/saltwater-business-operations-v1.json) (15,319,899 bytes; approximately 14.61 MiB). It contains 70,000 daily opening/service/shift/delivery schedule records (seven per establishment) and 10,000 weekly profiles. Build and regression workflow [45574250446](https://github.com/Joshuaogri/saltwater/actions/runs/45574250446) completed successfully. Schedules do not create staff, customers or resident person records.

These datasets remain in GitHub only. No Neon upload or production seed write has occurred. Neon upload remains scheduled after the property-management layers are completed, with compact import packaging, a fresh live storage measurement, an incremental/projected storage estimate and explicit approval before any production write.


## BP-04 — building systems, utilities and metering (SW-BUILDING-SERVICES-V1)

The first building-services layer is generated, regression-tested and persisted on `main`. It consumes the existing compact property-world and tenure datasets and is stored as compact textual columnar JSON at [`data/property/saltwater-building-services-v1.json`](data/property/saltwater-building-services-v1.json) (16,961,533 bytes; approximately 16.18 MiB).

The dataset contains:
- Four citywide utility operators: electricity, potable water, wastewater and telecommunications.
- 1,680 property utility connections and 1,680 linked master utility accounts across 420 property sites.
- 32,078 meters: property master meters plus dedicated electricity and water submeters for all 15,199 units.
- 2,862 building systems across 384 buildings, including electrical distribution, water distribution, wastewater/sanitary, HVAC, fire protection, security/access control, building controls and vertical transport where installed.
- 6,431 equipment assets with installation year, condition, operational state, maintenance class and replacement priority.
- 2,862 system inspection schedules with intervals, last inspection years and next-due simulation ticks.
- 10,000 business utility-responsibility assignments linked to current occupancy records and dedicated unit submeters.

The layer records service availability, capacity bands, redundancy, account responsibility, equipment condition and inspection schedules. It does not create bills, meter readings, balances, financial postings, residents, employees or other person records. BP-34 retains authority over financial transactions; the population ledger remains unchanged.

Build and seven regression tests passed in workflow [45578689850](https://github.com/Joshuaogri/saltwater/actions/runs/45578689850). The final regression-test optimisation also passed the regenerated workflow [45578778424](https://github.com/Joshuaogri/saltwater/actions/runs/45578778424).

This dataset remains in GitHub only. No Neon upload or production seed write has occurred. Neon preparation remains after the remaining property-management layers, with compact import packaging, a fresh live database storage measurement, projected incremental storage and explicit approval before production writes.


## BP-04 — property maintenance, defects and repairs (SW-PROPERTY-MAINTENANCE-V1)

The maintenance and repair layer is generated from the persisted property-world, tenure and building-services datasets. It establishes:
- 384 integrated building maintenance plans and 1,920 linked maintenance cycles.
- 3,282 inspection schedules covering all 2,862 building systems and all 420 property sites.
- 3,169 equipment-linked defect records with severity, discovery basis, operational and safety implications, urgency, root-cause profile and temporary controls.
- 3,169 linked work requests; 2,119 open corrective work orders with trade requirements, responsible maintenance contractors, managing organisations, duration bands, line items, materials and lifecycle events.
- 2,119 material issue records, 384 building emergency-maintenance procedures, equipment warranties and capital replacement forecasts.
- 11 specialist fictional maintenance contractor organisations; contractor organisations are not individual people.

The generated dataset is compact columnar JSON (9,261,100 bytes). Seven regression tests passed in [workflow 45579288100](https://github.com/Joshuaogri/saltwater/actions/runs/45579288100). The generator and tests verify property/building/system/equipment/work-order linkages, full inspection coverage, deterministic manifests and zero person, population or financial postings.

No invoices, payments, cost ledger, capital commitments, residents, employees or contractor-person records are created. BP-34 retains financial authority. The dataset is committed to GitHub `main` only; no Neon upload or production seed write has occurred.

- [Maintenance dataset](data/property/saltwater-property-maintenance-v1.json)
- [Generator](runtime/property_maintenance_generator.py)
- [Regression tests](tests/pkg001/test_property_maintenance_generator.py)
- [Build workflow](.github/workflows/saltwater-property-maintenance-build.yml)


## BP-04 — property security and access control (SW-PROPERTY-SECURITY-ACCESS-V1)

The property security layer is generated from the canonical property, tenure and building-services records:
- 804 door/gate records and 804 linked lock records, covering every canonical property/building access point.
- 1,233 controlled physical key records across 1,233 mechanical key cylinders, with restricted keyway profiles, duplicate controls and organisation-managed key cabinets.
- Electronic door-controller/reader devices for electronically controlled entrances.
- 18,830 access zones across building entry, building security areas, premises and individual units.
- 10,000 business-occupancy access groups, permission sets and organisation-level assignments linked to current leases/concessions and unit occupancy.
- Door policies cover schedules, contractor/work-order authorisation, visitor passes, lost-credential revocation and emergency override audit.

The model preserves free emergency egress and does not issue credentials to named people. Individual credential assignment, access logs and key issue events are runtime gameplay records, not fabricated baseline history. No residents, employees, person credentials, population records, invoices or financial postings are created.

Generation and seven regression tests passed in [workflow 45579877325](https://github.com/Joshuaogri/saltwater/actions/runs/45579877325). The compact columnar dataset is 13,065,912 bytes.

- [Security and access dataset](data/property/saltwater-property-security-access-v1.json)
- [Generator](runtime/property_security_access_generator.py)
- [Regression tests](tests/pkg001/test_property_security_access_generator.py)
- [Build workflow](.github/workflows/saltwater-property-security-access-build.yml)

No Neon upload or production seed write has occurred.

## BP-04 — property condition, valuation, insurance and taxation (SW-PROPERTY-VALUE-RISK-TAX-V1)

Implemented on `main` and generated from the persisted property, tenure, building-services, maintenance and security datasets. The deterministic compact columnar dataset contains 804 site/building condition assessments; 420 land valuations; 384 building-improvement valuations; 804 whole-property/building asset valuations; 1,327 premises valuations; 420 property insurance policies with 1,260 coverage records; 420 property risk profiles; 420 annual 2026 property-tax assessments; 420 exemption-screening records; five fictional insurer organisations; and one annual property-tax rule. Valuations use fictional SWC simulation units and replacement-cost/land-assessment profiles, not real market quotes. Condition records reference the existing defect and building-system baseline. Tax assessments remain assessed-not-billed; exemption is not presumed. No insurance claims, premiums, tax bills, invoices, payments, financial postings, residents or other person records were created. BP-34 retains transaction authority. Seven regression tests passed and the dataset was persisted in [run 45601885026](https://github.com/Joshuaogri/saltwater/actions/runs/45601885026). Output size: 1,309,420 bytes (~1.25 MiB); manifest SHA-256: `921a3dd9274d74a53e8113c78099224a9a4a5b103532edcb672a21a7c8eb165e`.

- [Property valuation, insurance and tax dataset](data/property/saltwater-property-value-risk-tax-v1.json)
- [Deterministic generator](runtime/property_value_risk_tax_generator.py)
- [Regression tests](tests/pkg001/test_property_value_risk_tax_generator.py)
- [Build workflow](.github/workflows/saltwater-property-value-risk-tax-build.yml)

## BP-04 — property development control, building control and lawful use (SW-PROPERTY-DEVELOPMENT-CONTROL-V1)

Implemented on `main`; the deterministic generator consumes the persisted property, tenure, building-services, maintenance and valuation/condition datasets. It records 420 site development plans; 384 existing-building planning permissions; 384 building-control cases; 384 completion/safe-use certificates; 384 periodic inspection schedules; 1,327 premises lawful-use certificates; 15,199 unique unit-level use-compliance records; 72 approved pre-construction development projects; and four development-control rule profiles covering port/maritime, logistics, residential and critical digital infrastructure. The 384 permissions and completion certificates establish the existing fictional built-world baseline; they are not represented as newly submitted applications or fabricated historical inspection visits. All inspection schedules remain scheduled, not completed. The planning application register is empty until gameplay creates applications. The 72 development projects are approved but have not started construction. No people, population records, invoices, fees, payments or financial commitments were created. Seven regression tests passed in [run 45603224586](https://github.com/Joshuaogri/saltwater/actions/runs/45603224586). Output size: 15,029,136 bytes (~14.33 MiB); manifest SHA-256: `9699f165769898af8bc71a7911a2608f0ec8b464a94e6f950f92deccac7c9f60`.

- [Property development-control dataset](data/property/saltwater-property-development-control-v1.json)
- [Deterministic generator](runtime/property_development_control_generator.py)
- [Regression tests](tests/pkg001/test_property_development_control_generator.py)
- [Build workflow](.github/workflows/saltwater-property-development-control-build.yml)



## BP-04 — property title, transactions and lifecycle register (SW-PROPERTY-LIFECYCLE-TRANSACTIONS-V1)

The deterministic property lifecycle generator is `runtime/property_lifecycle_transactions_generator.py`; its compact columnar output is `data/property/saltwater-property-lifecycle-transactions-v1.json`. It creates a unified title register for all 420 canonical property sites, 420 current property-interest records, 531 title instruments and 531 property-transaction index rows. Each transaction row references the authoritative ownership event ID in `SW-PROPERTY-TENURE-V1`; ownership history is not duplicated or re-authored. It also records baseline lifecycle lineage for all 384 buildings and 1,327 premises, linked to their existing development permissions, completion certificates and lawful-use certificates.

Every property has an encumbrance register, but the absence of supplied mortgage, lien, easement or charge data is explicitly recorded as **not asserted**, not as proof that no such interests exist. Ten future gameplay action types are defined: acquisition, sale/transfer, subdivision, consolidation, redevelopment, demolition, change of use, easement/wayleave, mortgage/charge and lease/concession change. These action definitions do not fabricate completed events or mutate the current physical hierarchy. Subdivision and consolidation require new parcel geometry and parent/child lineage before execution. No financial postings, settlement, payments, people or population records are created.

Eight regression tests passed in [workflow 45604525551](https://github.com/Joshuaogri/saltwater/actions/runs/45604525551). The generated dataset is approximately 1.00 MiB (1,044,637 bytes); manifest SHA-256: `c3d35be72d8175d4c9e096ba0aa4e93a1353bb92902c6f19f54acbf7e82fe1ea`. This is GitHub artifact size, not a PostgreSQL storage estimate. No Neon writes were made.


## BP-04 — property rights, easements, wayleaves and boundary evidence (SW-PROPERTY-RIGHTS-AND-BOUNDARIES-V1)

The deterministic generator `runtime/property_rights_boundaries_generator.py` produces `data/property/saltwater-property-rights-boundaries-v1.json`. It creates 420 property-rights schedules, 12,500 contractual-right indexes (10,000 current and 2,500 expired), 420 parcel-boundary evidence records, 804 physical-access evidence records and 1,680 utility-wayleave requirement records. Contractual-right indexes reference existing lease/licence/concession agreement IDs from `SW-PROPERTY-TENURE-V1`; they do not create duplicate agreements.

The boundary register references the existing planning parcel geometry but explicitly marks it as non-survey-grade and not independently verified as a legal boundary. Physical entrances and constructed routes are recorded as physical access evidence only; no legal right of way is inferred. Utility connections are indexed separately from legal wayleaves: the existence of a connected service does not prove an easement, landowner consent or utility corridor right. Nine instrument templates define evidence required for easements, rights of way, utility wayleaves, covenants, mortgages/charges, liens/caveats, boundary agreements and access licences. The registered-instrument register remains empty because no supporting source instruments were present; missing rights are marked unverified, not presumed absent.

Eight regression tests passed in [workflow 45605593292](https://github.com/Joshuaogri/saltwater/actions/runs/45605593292). The generated compact dataset is 5,011,509 bytes (about 4.78 MiB); manifest SHA-256: `8b3f864c0f524c0482271ae4989ceddafe19ce1124169e7a149008ae9a621e69`. This is a GitHub artifact size, not a PostgreSQL storage estimate. No Neon writes were made.


## BP-04 — property insurance exposure, loss events and claims controls (SW-PROPERTY-INSURANCE-CLAIMS-V1)

The deterministic generator `runtime/property_insurance_claims_generator.py` produces `data/property/saltwater-property-insurance-claims-v1.json`. It indexes all 420 existing property insurance policies and their insurers, coverage references, sums insured, deductibles and property valuations. It creates 384 building insurance schedules, 6,431 equipment insurance schedules, 3,169 defect exposure links and 4,200 peril assessments (10 peril categories for each property). Equipment remains covered within its parent property/building schedule; no separate equipment sum insured or duplicate insurance is invented.

The claims process defines ten stages from first notification and coverage triage through loss mitigation, evidence preservation, adjuster review, quantum assessment, coverage decision, settlement authorisation and closure. Sixteen loss-event types are available for future simulation, including coastal flood, storm surge, extreme rainfall, fire, machinery breakdown, utility outage, port-adjacent property damage and business interruption. The operational claims and loss-event registers remain empty: no historical loss, claim, reserve, settlement, premium posting or payment was fabricated. Known maintenance defects are linked as exposures only; causation and insurable loss remain unassessed. Full policy wording, exclusions, endorsements and site-specific hazard surveys remain unverified inputs for future adjudication.

Eight regression tests passed in [workflow 45606397673](https://github.com/Joshuaogri/saltwater/actions/runs/45606397673). The compact dataset is 4,966,651 bytes (about 4.74 MiB); manifest SHA-256: `54e7b58825b843acc146f57fe604fd47f70f122fd5182dd6787950fc1041f12b`. This is a GitHub artifact size, not a PostgreSQL storage estimate. No Neon writes were made.

## BP-04 — property facilities management and operational services (SW-PROPERTY-FACILITIES-OPERATIONS-V1)

The deterministic generator `runtime/property_facilities_operations_generator.py` produces `data/property/saltwater-property-facilities-operations-v1.json`. The opening operating model covers all 420 property sites, 384 buildings and 1,327 premises. It defines 6,720 property-level facilities framework contracts, 6,720 service zones and target service-level agreements, and 13,243 planned service schedules. Service domains include cleaning, general/recycling/organic and specialist waste, pest management, grounds, water hygiene, fire systems, lifts and vertical transport, HVAC/air quality, security systems, energy management, drainage/flood readiness, roofs/facades and port/cargo specialist operations. Premises and building schedules are linked to canonical property IDs; specialist providers are framework-calloff arrangements where applicable.

The service-failure rules cover missed routine work, critical plant/life-safety failures, waste overflow or misclassification, flood/drainage obstruction and repeated supplier failure. Schedules and SLA values are opening targets, not measured performance. Service requests, completed visits and supplier-performance actuals remain empty until gameplay creates them. No staff/person records, waste tonnage, invoices, payments or financial postings are fabricated; BP-34 remains the sole financial posting authority.

Six regression tests passed in [workflow 45607314182](https://github.com/Joshuaogri/saltwater/actions/runs/45607314182). The compact dataset is 7,150,576 bytes (about 6.82 MiB); manifest SHA-256: `f324312f2764c5dac491ef47235b5e1acc976f9ed0ed5cf35452461f2fe95ba3`. This is a GitHub artifact size, not a PostgreSQL storage estimate. No Neon writes were made.

**Unit-count reconciliation completed:** the 62,585 figure was caused by a duplicate nested premises loop in the development-control generator, which emitted each unit's compliance row repeatedly for every premises in its building. The generator now emits one row per actual unit identity. The corrected property-world, tenure occupancy, utility submeter and development-control registers each resolve to the same 15,199 unit IDs; the facilities-operations dataset now verifies identity-set equality and reports `reconciled`. No units were added or removed to force a count match.


## BP-04 — unit identity reconciliation correction (SW-PROPERTY-UNIT-RECONCILIATION-001)

An integrity review traced the apparent 47,386-unit excess to a duplicate nested premises loop in `runtime/property_development_control_generator.py`. Unit compliance had been emitted repeatedly for every premises in the same building. The generator was corrected to emit one record for each unit under its actual premises, and regression tests now assert both one-to-one count equality and uniqueness of unit IDs. The corrected development-control dataset contains **15,199 unit-use compliance records for 15,199 canonical unit identities**. Seven regression tests passed in [workflow 45608515021](https://github.com/Joshuaogri/saltwater/actions/runs/45608515021). Corrected output size: 4,688,872 bytes; manifest SHA-256: `3c83da9b66389a451fb1997ee0801876305cc25c046bc621cd2eb0b5cb6814fe`. Dataset commit: `a722aa7eae9abd5ee3fbda5f886d738fda8f566a`.

The facilities-operations generator now reads the corrected development-control dataset and compares the actual unit-ID sets across property world, tenure, utility submeters and development control. All four contain the same **15,199** unit IDs and the result is **reconciled**. Six regression tests passed in [workflow 45608676475](https://github.com/Joshuaogri/saltwater/actions/runs/45608676475). Updated facilities dataset size: 7,150,790 bytes (~6.82 MiB); manifest SHA-256: `dd66d415612d66be74662b00d6ecfd2fcd5533b4061c8a18b63f9a520e43d2ca`. Dataset commit: `9a1e949808345fe856a581f968dfa2e985bcceda`. Neither dataset update involved a Neon production write.

## SW-GLOBAL-ESTATE-CAPACITY-AUDIT-001 — global-city estate scale review

The first vertical-intensification phase is now fully regenerated, regression-tested and persisted as one consistent property/business snapshot on `main`. Sequential rebuild workflow: [45611785956](https://github.com/Joshuaogri/saltwater/actions/runs/45611785956), completed successfully. Snapshot commit: `ed0b77e`.

The deterministic district-specific `GLOBAL-ESTATE-VERTICAL-V1` profiles create commercial towers up to 58 storeys, with distinct financial, civic, university and harbour skylines. Industrial, freight, port-yard and utility assets retain appropriately lower-rise forms.

**Verified regenerated estate totals**
- 420 property sites; 384 buildings; 6,954 premises; 80,965 canonical units.
- 12,430,234.506 m² gross floor area; maximum height 58 storeys; mean building height 18.109 storeys.
- 265 buildings have at least 10 storeys; 146 have at least 20 storeys.
- 10,000 businesses and 10,000 establishments.
- 163,610 utility meters; 6,815 equipment assets; 3,054 building systems.
- 90,223 access-control zones; 804 canonical access points and 804 constructed access routes.
- Facilities schedules and service zones have been regenerated against the same canonical unit set.

Unit identity reconciliation is exact across the property world, tenure occupancy, utility submeters, development-control use records and facilities operations: **80,965 unique unit IDs in each register, with no missing or extra IDs**. All sequential rebuild test groups passed, including the final insurance, facilities and estate-capacity audit regression suites.

The 10,000-person population hard cap is unchanged. No residents, workers, employees, police personnel or other person records were created. No Neon production writes were made.

**Next physical-estate phase:** replace the single-building-per-property limitation with multi-building campuses and specialist megasites. This includes international port and bonded-logistics terminals, intermodal freight/passenger complexes, export-manufacturing estates, financial/corporate headquarters campuses and major international institutions. Every additional building must receive unique building, premises, unit and access identifiers, site-contained geometry, a connected constructed entrance/route and fully regenerated downstream property records. Existing site-only entrances and no-frontage access solutions must be preserved. The one-contiguous-city-state canon and 10,000-person cap remain binding.

## SW-PROPERTY-ESTATE-V2 — expanded campus estate and regenerated property stack

**Verified and persisted on `main` on 2026-11-25.** This section supersedes all earlier property-estate counts and dataset-size statements above where they describe the pre-campus or single-building estate. The sequential full-stack rebuild and all 13 validation stages passed in [workflow run 45623907617](https://github.com/Joshuaogri/saltwater/actions/runs/45623907617). All dependent registers were regenerated in dependency order, compressed, and persisted together in one consistent snapshot.

### Canonical expanded physical estate

- 420 property sites.
- 1,474 buildings across multi-building campuses and specialist sites.
- 27,730 premises.
- 180,733 canonical units.
- 110,920 named rooms.
- 2,984 building/site access points and constructed access routes.
- 36 sites without buildings retain site-level entrances and maintenance paths.
- Existing shared access spurs continue to resolve the four original frontage-deficient cases.
- No resident, worker, employee, police-personnel or other person records were generated. The distinct-person population cap remains 10,000.

### Regenerated dependent registers

The same expanded estate was used to regenerate business registry and weekly operations, ownership and occupancy, utility connections/meters/building systems/equipment, maintenance and defects, security and access control, condition/valuation/insurance/tax, development and lawful use, title/lifecycle/transactions, rights/boundary evidence, insurance exposure/claims controls, facilities operations, and the global estate-capacity audit. All 13 workflow validation stages passed, including exact canonical unit-identity reconciliation across the property world, tenure, utility submeters, development-control and facilities records.

### Compressed source inventory

All 14 property/business datasets are stored as deterministic gzip snapshots under `data/property/` and `data/business/`. Their combined GitHub blob size is **23,023,562 bytes (21.96 MiB)**. No uncompressed `.json` dataset files remain in those two folders. The canonical property-world snapshot is 8,924,278 bytes compressed; the building-services snapshot is 4,284,913 bytes compressed. These are source-repository compressed sizes, **not** PostgreSQL storage estimates.

The full-stack workflow restores compressed inputs, rebuilds and validates the complete dependency stack, compresses every output and commits the consistent snapshot to `main`. No Neon production seed/import/upload or population write occurred. Before any proposed Neon import, the compact package must be prepared and benchmarked, the live PostgreSQL baseline remeasured, and projected database growth reported for explicit approval.

## Canonical property-stack import preparation

The expanded 14-dataset property/business stack is persisted and validated on `main`. The next database phase is governed by [BP04 canonical property-stack import and disposable benchmark plan](docs/implementation/BP04-canonical-property-stack-import-plan.md). Existing BP04-01/BP04-02 schema proposals and the BP04-03 Stage E importer are disposable-only candidate assets, not the canonical property-world importer. The production property schema and lossless relational import pipeline must be built and benchmarked in isolated PostgreSQL 16 first. The live Neon database remains unchanged; no property seed rows or production property tables have been written.

### BP04 canonical property relational schema — phase 1

The first typed relational import model is now committed on `main` for isolated PostgreSQL 16 validation. Candidate SQL: `db/proposals/0012_bp04_canonical_property_stack.sql`. The mapping and integrity contract is documented in [BP04 canonical property relational mapping](docs/implementation/BP04-canonical-property-relational-mapping.md). It establishes stable source-ID primary keys and typed property, building, premises, unit, access, room/component, ownership, business, establishment and occupancy tables, with explicit foreign keys, provenance and a deterministic import-release ledger. Original source objects are retained per typed row for lossless round-trip verification; this is not a single opaque JSONB store.

This is a disposable-only schema proposal. It has not been applied to Neon. The deterministic importer, full phase-2 register coverage and PostgreSQL 16 benchmark are the next implementation tasks. No production schema or data writes have occurred.

The phase-1 schema now has a dedicated disposable PostgreSQL 16 acceptance workflow (`.github/workflows/bp04-property-schema-disposable.yml`) and SQL contract checks (`tests/pkg001/bp04_property_schema_acceptance.sql`). The workflow applies only the candidate proposal to an ephemeral CI database, verifies the 19-table inventory, deferred cyclic reference, current-unit uniqueness and release ledger, and records disposable schema size. It has not been run against Neon.

### BP04 phase-1 importer implemented

A deterministic, compressed-columnar importer is now available at `runtime/bp04_property_stack_importer.py`. It reads the canonical property-world, business-registry and tenure snapshots directly from their gzip files, verifies dataset identities and package digests, preserves each complete source row in JSONB alongside typed columns, uses stable source IDs, records an import-release manifest, and imports within one transaction with deferred FK checks. It refuses to connect to any database other than the disposable `saltwater_test` database. The dedicated PostgreSQL 16 workflow now applies the candidate schema, imports the package, repeats the import for row-count/idempotency checks, and reports database/table storage. CI run: [BP04 schema and import](https://github.com/Joshuaogri/saltwater/actions/runs/45628722456). This has no connection to production Neon.

### BP04 compressed-archive import benchmark — passed

The phase-1 schema was optimized after the first disposable benchmark showed that duplicating every complete source row as per-row JSONB inflated the database to 453.5 MiB. The storage-efficient proposal is now `db/proposals/0013_bp04_compressed_source_archive.sql`: complete original datasets are retained once as their original gzip byte streams in `source_dataset_archive`, while the typed relational tables retain stable source IDs and mapped operational columns. The importer is `runtime/bp04_property_stack_importer.py`.

The PostgreSQL 16 disposable workflow passed using this design: [BP04 compressed archive benchmark](https://github.com/Joshuaogri/saltwater/actions/runs/45630476765). It imported and reconciled **402,658 records across 17 typed tables**, covering 420 property sites, 1,474 buildings, 27,730 premises, 180,733 units, 110,920 rooms, 2,984 access points/routes, 10,000 businesses, 10,000 establishments, 10,000 business-unit links, 12,500 occupancy agreements and 10,000 occupancies. Cross-reference violations: **0**.

The three compressed source archives total **10,934,275 bytes (10.43 MiB)**; their uncompressed JSON totals **196,604,988 bytes (187.45 MiB)**. The measured disposable PostgreSQL database is **135,257,111 bytes (128.99 MiB)**, including typed rows, indexes and the compressed source archives. Re-importing the same release left database size unchanged (**135,257,111 bytes before and after**) and all row-count checks passed. This is a **71.6% reduction** against the initial row-level-JSONB design.

This remains a partial import benchmark: only property world, business registry and property tenure are included. The other dependent property registers still need typed mappings and a complete combined benchmark. The 128.99 MiB figure is not a final Neon projection. **No production Neon schema or data writes have occurred.**


## BP04 — complete compressed property-source inventory

The read-only source inventory is implemented in `runtime/bp04_source_inventory.py`, with regression tests in `tests/pkg001/test_bp04_source_inventory.py` and CI workflow `.github/workflows/bp04-source-inventory.yml`. Successful inventory run: [45633081533](https://github.com/Joshuaogri/saltwater/actions/runs/45633081533).

- 14 compressed property/business source datasets.
- 105 columnar collections.
- 1,950,947 source records.
- 23,023,562 compressed bytes (21.96 MiB).
- 559,420,873 uncompressed bytes (533.5 MiB).
- Every collection was checked for valid columnar structure and row-width consistency; inventory records column names, row counts, candidate identity columns, compressed/uncompressed sizes and SHA-256 source digests.
- Canonical dataset IDs are read from source metadata rather than inferred from filenames.
- This is source-package inventory only. It is not a relational import, Neon storage estimate or production upload. The phase-one PostgreSQL benchmark remains limited to the three mapped datasets; typed mapping and full disposable benchmarking of the remaining registers are next.


## BP04 — building services and utilities relational phase 2

The candidate schema `db/proposals/0014_bp04_building_services_utilities.sql` and importer mappings now cover all eight collections in the compressed building-services source: **426,399 records** across building systems, utility connections, utility provider profiles, utility accounts, meters, equipment assets, system inspections and business utility responsibilities. The importer preserves the original gzip dataset once in the source archive and writes typed operational columns with stable source IDs and explicit links to canonical property, building, unit, organisation, business and occupancy records.

The disposable PostgreSQL 16 workflow applies proposals 0013 and 0014 in order and validates the 28-table schema. Successful end-to-end benchmark: [BP04 phase-2 run 45636655387](https://github.com/Joshuaogri/saltwater/actions/runs/45636655387). It imported the complete four-dataset property/business/tenure package plus all eight building-services collections, including 426,399 building-services source records. The resulting database contains **362,093,591 bytes (345.37 MiB)** across typed records, indexes and four compressed source archives. The repeat import passed: **362,093,591 bytes before and after**, with all row counts unchanged and **zero cross-reference violations**. The importer explicitly normalizes source boolean flags encoded as 0/1 and adds the four utility-provider organisations to the canonical organisation register before inserting their provider profiles.

The 4 compressed archives total **15,219,188 bytes (14.51 MiB)**; the phase-2 building-services archive contributes 4,284,913 bytes. The database figure is a measured disposable PostgreSQL result for the four mapped datasets only, not a final full-estate or Neon projection. Phase 2 is accepted; maintenance, security, valuation, development, lifecycle, rights, insurance and facilities registers still need typed mappings and inclusion in the complete benchmark. This remains disposable-only. No Neon production schema or data writes have occurred.


## BP04 — property maintenance and repairs relational phase 3

Candidate schema `db/proposals/0015_bp04_property_maintenance_repairs.sql` adds 13 typed tables for maintenance contractor profiles, building maintenance plans and cycles, site/system inspections, equipment defects, work requests, work orders and lines, material issues, maintenance events, warranties, replacement forecasts and emergency maintenance procedures. The deterministic importer maps the complete `SW-PROPERTY-MAINTENANCE-V1` source and extends the canonical organisation register with its maintenance contractors. Relationships point to the canonical property/building/system/equipment records and maintenance work-order lineage; no person or financial-posting records are introduced.

The disposable PostgreSQL 16 workflow applies all three schema proposals and validates the 41-table inventory. The first attempt exposed colliding inspection identifiers caused by truncating long slugs; the generator now appends a SHA-256 suffix to long identifiers and a new regression test checks all 13 register ID sets. The maintenance build and uniqueness tests passed, and the regenerated gzip archive is 2,536,846 bytes (about 2.42 MiB).

The complete phase-3 disposable benchmark passed: [BP04 phase-3 run 45639343963](https://github.com/Joshuaogri/saltwater/actions/runs/45639343963). The five-source package now loads **947,720 typed domain records across 38 domain tables**, plus the three import/archive ledger tables (41 tables total). Maintenance records include 12,194 inspections, 13,139 defects and work requests, 8,888 work orders, 8,888 work-order lines, 8,888 material issues and events, 26,341 equipment warranties, 16,846 replacement forecasts, 1,474 building emergency procedures and 11 maintenance contractors. Cross-reference violations: **0**.

Measured disposable PostgreSQL size is **420,174,871 bytes (400.71 MiB)**, including typed rows, indexes and five compressed source archives. Those archives total **17,756,034 bytes (16.93 MiB)**; their uncompressed source JSON totals **368,978,617 bytes (351.86 MiB)**. Repeat import passed with **420,174,871 bytes before and after**, and all table counts remained unchanged. This is still a partial import: security/access, valuation/tax, development control, lifecycle, rights/boundaries, insurance/claims and facilities operations remain to be mapped and included before the final full-estate benchmark. Neon production remains unchanged.


## BP04 — property security and access-control relational phase 4

Candidate schema `db/proposals/0016_bp04_property_security_access.sql` adds 12 typed tables for doors/gates, locks, key cylinders and physical keys, electronic security devices, hierarchical access zones, business occupancy access groups, permission sets and normalized permission-to-zone grants, organisation access assignments, key cabinets and access policies. The importer maps the source permissions array into explicit grant rows and retains the compressed source archive once. Database constraints prevent person-bound physical-key issuance and person membership in access groups; credentials remain organisation/group-level until runtime simulation assigns people.

The security generator now uses collision-resistant identifiers for long source IDs, and regression coverage checks uniqueness across all security registers. Its build workflow restores canonical gzip inputs and persists a compressed output (3,025,865 bytes; 2.89 MiB). The first schema acceptance run exposed auto-generated constraint-name assumptions; the person-credential exclusion checks now use explicit stable constraint names.

The complete 53-table disposable PostgreSQL 16 benchmark passed: [BP04 phase-4 run 45640703939](https://github.com/Joshuaogri/saltwater/actions/runs/45640703939). It loaded **1,232,690 typed domain records across 50 domain tables**, plus the three import/archive ledger tables, with **zero cross-reference violations**. Security records include 217,307 access zones, 20,000 permission-to-zone grants, 10,000 business access groups, 10,000 permission sets, 10,000 organisation assignments, 2,984 doors, 2,984 locks, 4,572 physical keys, 1,524 key cylinders, 721 electronic devices, 420 key cabinets and 4,458 access policies. Database constraints enforce empty person membership in access groups and prevent person-bound physical-key assignment.

Measured disposable PostgreSQL size is **532,839,447 bytes (508.16 MiB)**, including typed rows, indexes and six compressed source archives totalling **20,781,899 bytes (19.82 MiB)**. Their uncompressed source JSON totals **430,913,963 bytes (410.95 MiB)**. Repeat import passed with **532,839,447 bytes before and after**, and all row counts remained unchanged. This is still a partial import: valuation/tax, development control, lifecycle, rights/boundaries, insurance/claims and facilities operations remain to be mapped and included before the final full-estate benchmark. Neon production remains unchanged.


## BP04 — property valuation, insurance exposure and taxation relational phase 5

Candidate schema `db/proposals/0017_bp04_property_valuation_tax.sql` adds 12 typed tables for site/building condition, land and improvement valuation, whole-property and premises valuations, insurer profiles, insurance policies and coverage, property risk, annual tax assessments, exemption reviews and tax rules. The importer adds five fictional insurers to the shared organisation register and preserves typed SWC values and explicit valuation/policy/property/owner/manager links. Assessments remain assessed-not-billed; no premiums, claims, invoices, tax bills, payments or financial postings are created.

The valuation generator now uses collision-resistant long identifiers, with uniqueness regression checks across all 12 source collections. Its build workflow restores five compressed canonical dependencies and persists only a compressed dataset. The complete seven-source, 65-table disposable PostgreSQL 16 benchmark passed: [BP04 phase-5 run 45641900441](https://github.com/Joshuaogri/saltwater/actions/runs/45641900441). Valuation/tax records include 1,894 condition assessments, 420 land valuations, 1,474 improvement valuations, 1,894 asset valuations, 27,730 premises valuations, 420 insurance policies, 1,260 coverage records, 420 risk profiles, 420 annual tax assessments, 420 exemption reviews, one tax rule and five insurer profiles. The combined database measured **546,020,375 bytes (520.73 MiB)** with **zero cross-reference violations**. Repeat import passed with **546,020,375 bytes before and after**, and all row counts remained unchanged. Seven mapped gzip sources total **21,190,376 bytes (20.21 MiB)**; their uncompressed source JSON totals **437,861,928 bytes (417.58 MiB)**. This remains a partial import: development control, lifecycle transactions, rights/boundaries, insurance claims and facilities operations still require mapping and inclusion in the final benchmark. Neon production remains unchanged.


## BP04 canonical property stack — source archive, corrected mapping ledger and business operations

The full disposable PostgreSQL 16 workflow [45646271478](https://github.com/Joshuaogri/saltwater/actions/runs/45646271478) passed on main commit `f9e18f63dff763134073050e3409432f82bd5c79`. The workflow applied proposals 0013–0019, passed source-identity unit tests, passed 68-table schema acceptance, imported all 14 gzip sources, passed the post-import ledger/business-schedule acceptance, and passed repeat-import storage/idempotency checks.

A correction was made after reviewing Phase 6's first mapping ledger: its collection keys used some relational target names rather than the original source collection names. The importer now retains each source collection identity directly while expanding columnar records. The corrected ledger reconciles all 105 source collections and 1,950,947 source records. **63 source collections (1,337,925 rows) are typed-mapped; 42 collections (613,022 rows) remain archive-only.** Six datasets are fully mapped, two are partially mapped (property world and tenure), and six are archive-only. All 14 source gzip datasets are retained losslessly regardless of mapping status.

| Measure | Verified result |
|---|---:|
| Source datasets archived | 14 / 14 |
| Source collections reconciled | 105 |
| Total source records | 1,950,947 |
| Typed-mapped source collections / rows | 63 / 1,337,925 |
| Archive-only source collections / rows | 42 / 613,022 |
| Compressed package | 23,023,562 bytes (21.96 MiB) |
| Uncompressed source JSON | 559,420,873 bytes (533.50 MiB) |
| Compressed source archive relation | 23,797,760 bytes |
| Typed relational schema | 68 tables |
| Business daily schedules | 70,000 |
| Business weekly profiles | 10,000 |
| Disposable PostgreSQL database | 577,395,735 bytes (550.65 MiB) |
| Cross-reference violations | 0 |
| Database size after repeat import | 577,395,735 bytes (unchanged) |
| Repeat-import row mutations | 0 |

The business schedule layer records each business's seven-day customer opening status, opening/closing times, service window, shift pattern, delivery window and emergency contact route. It is useful for time-aware dispatch, call-for-service context and scene access; it creates no employee, customer or resident person records. The repeat import produced zero inserts, updates or deletes. Largest measured relations include meter (195,067,904 bytes), access_zone (83,640,320), unit_space (58,318,848), business_daily_schedule (25,821,184), premises_room (23,887,872) and source_dataset_archive (23,797,760).

The remaining archive-only sources are the existing development-control, facilities, insurance-claims, lifecycle/transactions, rights/boundaries and global-estate-audit datasets. Next, map only gameplay-relevant content: lawful-use and development restrictions where useful to investigations/scene access; title/lifecycle and rights evidence where relevant to disputes or property crime; and insurance claim/loss workflows for relevant incidents. Keep the global estate audit as evidence, and avoid expanding facilities-management systems without a direct police-gameplay need.

This is disposable benchmark evidence only. No production Neon schema, seed, import or upload was performed.


### BP04 phase 9 — title, transaction and lifecycle mapping (validation in progress)

Candidate migration `db/proposals/0021_bp04_property_title_lifecycle.sql` adds nine typed tables for the title register, property-interest index, title instruments, transaction index, property/building/premises lifecycle, encumbrance status and runtime lifecycle-action rules. The importer maps all nine source collections from `SW-PROPERTY-LIFECYCLE-TRANSACTIONS-V1` while keeping `SW-PROPERTY-TENURE-V1` authoritative for ownership-event facts. The mapping covers 31,956 source rows: 420 title records, 420 interest records, 531 title instruments, 531 transaction indexes, 420 property registration events, 1,474 building baselines, 27,730 premises baselines, 420 encumbrance registers and 10 action rules.

The first disposable import correctly exposed truncated-ID collisions in the generated premises lifecycle IDs (only 9,461 of 27,730 rows could be inserted). The generator now uses full-source SHA-256-derived identifiers for title, interest, property, building, premises and encumbrance IDs. Its dedicated build and regression workflow [45653180837](https://github.com/Joshuaogri/saltwater/actions/runs/45653180837) passed: **9 tests**, including uniqueness checks across all generated lifecycle ID collections. It regenerated the 27,730 premises and 1,474 building baseline rows without collisions. The full dependent property-stack rebuild [45653180817](https://github.com/Joshuaogri/saltwater/actions/runs/45653180817) completed successfully on main (rebuild commit `85dc08d`). It regenerated the 27,730 premises lifecycle rows with unique identifiers and regenerated the dependent rights/boundary dataset. The rights generator reports 420 property-rights schedules, 12,500 contractual-right indexes, 420 boundary-evidence records, 2,984 physical-access evidence records and 1,680 utility-wayleave requirement records. The 92-table phase-10 disposable import benchmark is running against this rebuilt snapshot. No production Neon writes have occurred.


### BP04 phase 10 — property rights, boundary and access evidence

Added seven typed relational tables and mapped all seven collections from `SW-PROPERTY-RIGHTS-AND-BOUNDARIES-V1`: 420 property-rights schedules, 12,500 contractual-right indexes, 420 boundary-evidence records, 2,984 physical-access evidence records, 1,680 utility-wayleave requirement records, zero registered instruments, and nine future instrument templates (**18,013 source rows**). Contractual rights link to existing tenure agreements; access points/routes remain physical evidence, not inferred legal rights; parcel geometry remains non-survey-grade evidence. Migration: `db/proposals/0022_bp04_property_rights_boundaries.sql`. The disposable import acceptance now checks all seven collections and their principal relationships. No Neon production writes.

### BP04 phases 1–10 — complete disposable import benchmark

The full 14-source package was imported into disposable PostgreSQL 16 using the 92-table schema. Benchmark workflow [45656098435](https://github.com/Joshuaogri/saltwater/actions/runs/45656098435) completed successfully:
- Compressed source package: **29,434,820 bytes (28.07 MiB)**; uncompressed source total: **558,602,287 bytes (532.72 MiB)**.
- Source inventory: **14 datasets, 105 collections and 1,950,923 source records**.
- Mapping: **8 fully mapped datasets, 3 partially mapped, 3 archive-only**; 86 collections mapped and 19 retained archive-only; **1,422,202 rows mapped**.
- Cross-reference violations: **0**.
- Disposable database size after import: **627,792,919 bytes (598.71 MiB)**.
- Repeat import: database size remained **627,792,919 bytes**; **0 inserts, updates or deletes**. Idempotency passed.
- Live Neon baseline (read-only measurement): **9,306,112 bytes (8.875 MiB)**. Estimated incremental storage for this package is approximately **618,486,807 bytes (589.83 MiB)**, giving an estimated post-import total near **627.8 MB (598.71 MiB)**. This is a PostgreSQL 16 benchmark estimate, not a production Neon measurement.
- No production Neon schema or data writes have been made.

The 19 archive-only collections remain losslessly retained in their compressed source datasets; they are not fabricated into gameplay records. The mapped collections provide typed relational access for the core property, business, tenure, operating-hours, building-services, maintenance, security, lawful-use, title/lifecycle, rights and access relationships.


### BP05 — Saltwater Police Service architecture

Implemented the initial fictional police organisation on `main` in `db/proposals/0023_bp05_police_architecture.sql`. The Saltwater Police Service now has **48 canonical components**: one department, four command portfolios, 12 divisions and 31 operational/support units. The structure includes nine substantive ranks (Recruit remains a service standing, not a rank), 24 position definitions and an **authorised establishment of 500 vacant posts** distributed across the service. All 47 parent reporting relationships are recorded. The seed creates no personnel or person records; those are generated and linked in the personnel stage, preserving the 10,000-person cap and avoiding fictitious filled posts.

Full Python and disposable PostgreSQL regression [PKG-001 workflow run 45658350599](https://github.com/Joshuaogri/saltwater/actions/runs/45658350599) passed. It verified component hierarchy, rank/position separation, 500-post count, initial vacancy status, append-only post authorisation history and zero personnel created by the structure seed.


### BP06 — personnel service records (first increment)

Added `db/proposals/0024_bp06_personnel_service_records.sql` and a PostgreSQL-backed dossier model for service engagements, immutable service events, service-number history and effective-dated supervision. Every personnel appointment now creates its service engagement and history in the same transaction. Recruit appointments additionally require an active established supervisor and create the formal supervision link; established personnel do not need a recruit-supervisor relationship. The schema preserves canonical BP-03 person identity and does not create duplicate people, ranks or post occupancy.

The dedicated BP06 acceptance and complete PKG-001 disposable regression [run 45659232002](https://github.com/Joshuaogri/saltwater/actions/runs/45659232002) passed, including the 10,000-person cap, concurrency, backup/restore and runtime checks. It verifies dossier/event/service-number completeness, living population linkage, recruit supervision and no automatic filling of the 500 vacant posts.

## Current implementation update — 2026-11-25

This dated update supersedes earlier status statements above where they describe the runtime, police architecture or property stack as not yet implemented.

- **Property stack:** BP04 phases 1–10 are implemented as disposable-only PostgreSQL proposals and imported successfully into a 92-table PostgreSQL 16 benchmark. The package contains 14 compressed datasets, 105 source collections and 1,950,923 source records. 1,422,202 rows are mapped to typed tables; the remaining 19 collections are preserved losslessly in compressed source archives. The package is 29,434,820 compressed bytes (28.07 MiB); the benchmark database is 627,792,919 bytes (598.71 MiB). Cross-reference violations: zero. Repeat import produced zero mutations and no database-size change. Evidence: [BP04 92-table benchmark](https://github.com/Joshuaogri/saltwater/actions/runs/45656098435).
- **Police architecture (BP05):** the disposable proposal defines 48 organisational components, nine substantive ranks, 24 position definitions and 500 authorised posts, initially vacant. The hierarchy and establishment acceptance passed. No officers were fabricated or appointed by the architecture seed.
- **Personnel service records (BP06):** the disposable proposal now creates a personnel dossier, service engagement, immutable appointment event and service-number history when personnel are appointed. Recruit supervision is required only for recruits; established direct-entry supervisors do not need a recruit supervisor of their own. BP06 acceptance passed in the current disposable workflow.
- **Population/runtime:** the disposable regression suite filled the population to exactly 10,000, verified that concurrent admission at 9,999 permits exactly one final admission, and verified that an additional living person is rejected. Backup/restore reproduced 10,000 people, population states, histories, events and name-registry records exactly. The checkpoint validator explicitly leaves business-minimum, player-absence-freeze and permission/hidden-truth gates unexecuted; these are not claimed as passed.
- **Production boundary:** all of the above database work is disposable PostgreSQL validation. No BP04 property import or BP05/BP06 schema proposal has been applied to production Neon. The live Neon baseline remains a separate read-only measurement. No production seed data has been written.
- **Execution approach:** fictional canon, NPCs, organisations and gameplay systems are developed directly on GitHub `main` using established engineering and simulation standards. Routine fictional work does not require repeated user approval. Production Neon writes remain separate from fictional design and disposable testing.


### BP07 — career history foundation

Added `db/proposals/0025_bp07_career_rank_and_post_history.sql`: append-only career episode events, separate rank assignments and authorised post appointments, current-rank/current-post projections, and registered career event types. Opening a career episode now records its event automatically. Rank and post assignments remain separate, and a recruit receives neither a substantive rank nor an occupied post automatically. The BP07 career-history acceptance and full PKG-001 disposable regression [run 45660272493](https://github.com/Joshuaogri/saltwater/actions/runs/45660272493) passed, including population-cap, concurrency, backup/restore and runtime checks.


### BP08 — unit catalogue and deployment readiness foundation

Added `db/proposals/0026_bp08_unit_deployment.sql`. All **31 operational/support units** now have canonical profiles, mandate boundaries, capability codes, crew thresholds and dispatchability classification. Their establishment view reconciles **480 unit posts**, all currently vacant. Unit membership is linked automatically to a BP07 post appointment in a unit; deployment and status histories are append-only. With no staffed memberships or verified status/resource records, all units correctly remain unavailable and none is dispatch-eligible. The schema deliberately does not fabricate crews, deployments, vehicles or radio readiness.

BP08 disposable acceptance passed in [PKG-001 run 45661335150](https://github.com/Joshuaogri/saltwater/actions/runs/45661335150); the complete regression is continuing through the population-cap and backup/restore tests. BP09 resource readiness is the next dependency before real dispatch eligibility.


## BP04 — production release packaging

The BP04 schema has been promoted from disposable-only proposals into the ordered production migration sequence `db/migrations/0003`–`0012`. The original proposal files remain for design provenance. The 92-table disposable benchmark workflow now applies the production migration copies. The canonical importer defaults to `saltwater_test`; writes to the production database name `neondb` require the explicit `--allow-production` flag. The migration ledger read-only verifier can report pending migrations without treating an un-deployed release as schema drift.

The accepted benchmark package contains 14 compressed datasets, 105 collections and 1,950,923 source records; 1,422,202 typed-mapped rows across 92 tables; 19 archive-only collections; three partially mapped collections; zero cross-reference violations; 29,434,820 compressed bytes; and a 627,792,919-byte (598.71 MiB) disposable PostgreSQL footprint. Repeat import was storage-stable. Benchmark package SHA-256: `54090f74332c1d0fedb09b48ad1fd669b9d62c593c9a5c253e979cbafaf4a3be`.

**Production deployment remains pending.** The current release commit must pass a fresh disposable benchmark, then production preflight must confirm the latest source/package digest, backup/restore point, migration ledger, live schema fingerprint, storage headroom and before/after measurements. The latest read-only Neon baseline on 2026-11-25 is 9,306,112 bytes; five user tables exist and no `sw_property` tables are present. No BP04 production writes have occurred. See [BP04 production release runbook](docs/operations/BP04-production-release-runbook.md).


### BP09 — police resource inventory and readiness

Added `db/proposals/0027_bp09_police_resource_readiness.sql`: 15 resource models, **527 individually tagged assets**, 50 fleet vehicles, 500 initial unit-pool allocations and 27 unallocated central-store assets. Every asset has a registration-history event; each unit-pool allocation has an allocation event. Seven dispatchable units have complete minimum equipment requirements. The readiness projection now requires verified staffing, operational availability and resource sufficiency together. No unit is dispatch-eligible until it has a real roster and an available status; resource inventory alone cannot create a dispatchable unit.

BP09 disposable acceptance passed in [PKG-001 run 45663358864](https://github.com/Joshuaogri/saltwater/actions/runs/45663358864). Full regression is completing the population-cap and backup/restore checks. Next is to connect the communications/CAD and incident workflow, then field response, using only units that become genuinely ready.


The current production-release workflow is manual-only: `.github/workflows/neon-production-migrations.yml`. It requires the exact confirmation `APPLY_BP04_TO_NEON`, a pre-release Neon restore-point reference, the pinned source package digest and the production database name `neondb`; no push can trigger it. The final combined migration-runner/import benchmark passed on PostgreSQL 16 and 18 in [run 45664193870](https://github.com/Joshuaogri/saltwater/actions/runs/45664193870). Full disposable database sizes were 628,120,599 bytes (PostgreSQL 16) and 628,569,791 bytes (PostgreSQL 18); repeat imports left both unchanged. Using the PostgreSQL 18 result, expected incremental Neon database growth from the 9,306,112-byte live baseline is approximately 619,263,679 bytes (619.26 MB / 590.58 MiB), with a projected total near 628.57 MB (599.45 MiB). This remains an estimate until measured on Neon. The production workflow has not been executed; no BP04 production schema or data writes have occurred.


The 14 compressed source archives total 29,434,820 bytes (29.43 MB / 28.07 MiB); the ten production migration files total 65,681 bytes; the importer source is 68,115 bytes and executes in the GitHub runner. Combined static release files are 29,568,616 bytes (29.57 MB / 28.20 MiB). This is not the total database growth: typed rows, indexes and PostgreSQL overhead account for the much larger measured disposable footprint.


## BP04 production release checkpoint — 2026-11-25

A manual Neon restore snapshot was created on the production branch before the BP04 production release attempt:

- Neon project: `misty-breeze-20463094`; branch: `production`; database: `neondb`.
- Restore snapshot: `snap-calm-credit-bdfp5tog` (created 2026-11-25T17:37:13Z).
- Read-only PostgreSQL baseline after snapshot: **9,306,112 bytes (9.306 MB / 8.875 MiB)**; five user base tables.
- Migration ledger remains at versions **1 (foundation)** and **2 (migration_integrity)**.
- BP04 migrations **0003–0012 have not been applied**; no BP04 source datasets or typed relational records have been uploaded. Production remains unchanged by BP04.
- The validated BP04 release remains 14 compressed datasets (29,434,820 bytes; 29.43 MB) and ten migrations. The PostgreSQL 18 disposable benchmark projected approximately 619,263,679 bytes (619.26 MB / 590.58 MiB) of incremental database growth; this is not a production measurement.
- The manual production workflow has not been dispatched. The production release must remain pending until the workflow is started from `main`, its required `DATABASE_URL` secret is available, and the workflow completes all migration, import, acceptance and repeat-import checks.

No production BP04 write is claimed by this checkpoint.


## BP04 Neon production upload — result (2026-11-25)

The manual production release workflow ran on `main` at commit `8854d66180a074f0e425d45803590ffbe14dc1a9` (run [45667318478](https://github.com/Joshuaogri/saltwater/actions/runs/45667318478)). The pre-write Neon restore snapshot was verified by the workflow: `snap-calm-credit-bdfp5tog`.

**Production data deployment succeeded; the workflow ended in failure only at the strict repeat-import storage-stability assertion.**

- Migrations **0003–0012** applied successfully; Neon migration ledger now contains versions 1–12.
- All **14/14** compressed source datasets imported.
- Package digest: `54090f74332c1d0fedb09b48ad1fd669b9d62c593c9a5c253e979cbafaf4a3be`.
- Compressed source archives: **29,434,820 bytes (29.43 MB)**; uncompressed source data: **558,602,287 bytes**.
- Source ledger: **1,950,923** source records; **1,422,202** typed mapped records; **0** cross-reference violations.
- Production acceptance: schema acceptance and import acceptance both passed.
- Neon now has **92 BP04 tables** in `sw_property` and **97 user base tables** overall.
- Pre-upload database size: **9,306,112 bytes (9.31 MB)**.
- Before repeat-import test: **624,893,952 bytes (624.89 MB)**.
- After repeat-import test as measured by the workflow: **625,033,216 bytes (625.03 MB)**, an increase of **139,264 bytes (0.139 MB)** during the repeat operation. The workflow's exact-size-equality guard therefore failed; do not record the repeat-import storage-stability check as passed.
- Latest live read-only measurement after the run: **625,811,456 bytes (625.81 MB / 596.82 MiB)**. This is **616,505,344 bytes (616.51 MB)** above the original baseline.
- All 14 dataset ledger rows and all 12 migration ledger rows are present in production.

The BP04 release is present and accepted in Neon. The outstanding item is to explain the small database-size delta during the repeat import, confirm row-count idempotency independently, and adjust the workflow's storage assertion if PostgreSQL maintenance/operation-ledger writes explain the delta. Do not re-import the package merely to retry the size assertion. No rollback was performed; retain the pre-release restore snapshot.


## BP04 storage architecture update — compressed archive only (2026-11-25)

The earlier BP04 Neon import was rolled back to its pre-release restore point at the user's request. Production is currently restored to **9,306,112 bytes (9.31 MB)**, with five original user tables, migration versions 1–2, and no BP04 schema or data. The restored production branch is `br-still-cloud-bdvaw8u4`.

The prior typed-row design stored the 14 compressed source files (29.43 MB) and also expanded 1,422,202 mapped source records into 92 relational tables. That previous representation measured approximately 616.51 MB of incremental Neon database growth. It is superseded for production use.

**Selected model:** store the 14 original gzip datasets exactly once in `sw_property.source_dataset_archive`, preserve release/dataset/collection provenance and exact source counts, and do not permanently materialise the 1.42 million typed rows. The dataset is decompressed and expanded in application memory only when requested through `runtime/bp04_archive_reader.py`; SHA-256 is verified before use. The original compressed archive remains the lossless source of truth. Domain tables remain empty for static BP04 source data; only genuinely changing game state should be stored as transactional records.

The disposable PostgreSQL workflow and manual-only Neon release workflow now select `--archive-only` and the new archive-only acceptance checks. The target is storage close to the 29.43 MB compressed package plus PostgreSQL metadata, TOAST and provenance overhead. The actual archive-only database size is **not yet measured**; do not reuse the former 628 MB typed-row benchmark as the new estimate. No Neon production write has been made as part of this change. The manual Neon workflow still requires fresh explicit user authorisation and a restore point.


## Verified archive-only storage benchmark — PostgreSQL 16 and 18 (2026-11-25)

The archive-only release workflow passed on both PostgreSQL 16 and PostgreSQL 18 in GitHub Actions run [45672135316](https://github.com/Joshuaogri/saltwater/actions/runs/45672135316), commit `a1836b83df980824a5291d7ed67b89cba5c624e9`.

| Measure | PostgreSQL 16 | PostgreSQL 18 (closest Neon benchmark) |
|---|---:|---:|
| Full disposable database size | 40,434,711 bytes (40.43 MB) | 40,875,711 bytes (40.88 MB) |
| Baseline before BP04 import | 9,306,112 bytes | 9,306,112 bytes |
| Incremental database growth | 31,128,599 bytes (31.13 MB) | 31,569,599 bytes (31.57 MB) |
| Compressed source package | 29,434,820 bytes (29.43 MB) | 29,434,820 bytes (29.43 MB) |
| `source_dataset_archive` relation | 28,368,896 bytes | 28,368,896 bytes |
| Typed rows permanently imported | 0 | 0 |
| Repeat-import size change | 0 bytes | 0 bytes |
| Repeat-import row mutations | 0 | 0 |

The import preserved all 14 archives, 105 source collections and 1,950,923 source records. The archive-only acceptance test passed on both PostgreSQL versions, and the second import left database size unchanged. Against the previous typed-row production growth of 616,505,344 bytes, the PostgreSQL 18 archive-only benchmark reduces incremental growth by approximately **94.88%** (about 19.5 times smaller).

The 31.57 MB figure is incremental database growth in the disposable PostgreSQL 18 benchmark, not the production measurement. The later archive-only production deployment is measured separately in the latest status section at the top of this README.


**Safe default:** the importer now defaults to `compressed_archive_only` even when no storage flag is supplied. The previous expanded representation is available only through the explicit `--typed-relational` option for disposable benchmarking; the importer itself rejects typed-relational mode when the target database is `neondb`. The production workflow also explicitly passes `--archive-only`.

## BP-02 frontage exception dispositions and full acceptance audit

The five P1 BP04 address/frontage exceptions have been examined against the SW-GEO-V1 road-reserve and parcel-boundary candidate geometry. Three have a single geometric parcel-frontage candidate (North Coast Road for two parcels; South Coast Road for one), but all three sites have no candidate building, so the original source address road is preserved and no address correction is promoted. The other two have only point-contact proximity to Customs Bridge / Harbour Bridge road reserves; bridge point contact is not street frontage.

New implementation: `runtime/bp02_address_frontage_exception_resolution.py`. The consolidated, read-only BP-02 audit combines city/road geometry, all 420 parcel dossiers, address/property references, 2,948 building-boundary access candidates, connector topology and route-corridor candidate checks.

The first full audit identified 26 connector centrelines crossing other generated building footprints. The asset generator now performs a final connector reconciliation after all buildings are generated, preserving access-point locations and selecting only parent-property-contained candidate lines that do not intersect any other building footprint (including point contacts, matching the independent audit's strict intersection rule). A Shapely spatial index limits each candidate check to nearby building footprints. Where a direct line is obstructed, a visibility-graph pathfinder now searches for a multi-segment route around buffered building/water obstacles while remaining inside the parent parcel; if no path exists, the original candidate remains blocked. Independent route-corridor audit [run 45696915823](https://github.com/Joshuaogri/saltwater/actions/runs/45696915823) passed all 7 checks for 2,948 candidates: zero mapped-building intersections and zero mapped-water intersections. The consolidated full BP-02 acceptance audit [run 45696915906](https://github.com/Joshuaogri/saltwater/actions/runs/45696915906) subsequently passed all structural checks: all 420 property/address source links resolve, all 2,948 building access/connector candidates pass, and all five frontage exceptions have geometry dispositions. Its explicit result is `STRUCTURAL_PASS_OPERATIONAL_RELEASE_BLOCKED`: no canonical addresses or operational access points were promoted, and operational geography/access approval remains blocked. Independent connector-road topology audit [run 45696857582](https://github.com/Joshuaogri/saltwater/actions/runs/45696857582) also passed all 9 checks and 6 regression tests: 2,944 frontage connectors, four separate point-contact/proximity connectors and zero unlinked candidates or topology mismatches. Direct-connector feasibility audit [run 45696857695](https://github.com/Joshuaogri/saltwater/actions/runs/45696857695) passed all 7 checks: 2,926 straight-line candidates are geometrically clear and 22 remain explicitly classified as blocked direct lines; the visibility-graph detours are assessed separately by the passing route-corridor audit. The regenerated Stage E inventory [run 45697967671](https://github.com/Joshuaogri/saltwater/actions/runs/45697967671) also passed all 12 generator regressions and produced 420 properties, 1,474 buildings, 27,730 premises, 180,733 units and 2,948 each of access-point/connector candidates, plus 213,305 profiles and 1,204,450,591 bytes of uncompressed detail in a 17,789,101-byte gzip payload (~67.7:1). The manifest resolves all 100 source entity-code mappings and creates zero operational IDs, addresses or access approvals. The artifact is CI/GitHub-only; no Neon upload was made. Disposable PostgreSQL import, idempotency, storage and restore acceptance are still running. A dedicated synthetic detour regression also passed. This does not establish constructed or operational access.

Operational release remains blocked: SW-GEO-V1 is still a design baseline; canonical operational addresses and operational access-point approvals are absent. No Neon writes or property archive uploads were performed.

BP04 now exposes two constrained cross-domain location handoffs: dispatch receives only a location reference/confidence/provenance (not a duplicated address record), while investigation history requires both BP16 and BP12 grants. Both paths are independently audited and preserve BP11/BP12/BP16 ownership boundaries.

The BP12 incident location chronology now has a read-only PostgreSQL adapter using a parameterised query, with regression coverage for provenance preservation, invalid IDs and failure handling. Dispatch and investigation adapters can consume this trusted reader without creating duplicate location records.

Investigation history access is additionally bound to an authorised case reference: a trusted case-to-incident verifier must confirm the link before any BP12 history read. An unlinked incident is denied without revealing its location history.

Dispatch-originated location updates now have a BP11-to-BP12 writer handoff. The dispatcher must hold a dedicated record grant; dispatch, incident and address reads are separately authorised and audited. The BP12 writer receives CAD provenance, dispatcher authority, confidence and an idempotency key, and remains the sole owner of the incident-location event and history.
Dispatch-originated location writes additionally verify that the referenced CAD assignment is actually linked to the target incident, under a separate BP11 assignment-inspection grant. A mismatched link is rejected before BP04 address lookup or BP12 persistence.

BP11 dispatch acknowledgements and BP10 field-unit arrivals can now be mirrored into the BP12 incident operational timeline. Both paths verify their originating dispatch/deployment/activity references and enforce separate domain grants. BP12 stores only the append-only event chronology; it does not own CAD acknowledgement, deployment, unit availability or patrol task state. PostgreSQL acceptance covers idempotency and provenance for both event types.
\n\nThe BP12 operational timeline now has a read-only PostgreSQL reader and an audited officer-facing access method. It returns dispatch acknowledgements and verified field-unit arrivals in event order, validates incident identity, event type and actor/authority/source provenance, and requires the dedicated `bp12.incident.inspect.operational_timeline` grant. It does not mutate CAD, deployment or patrol state.\n

The operational chronology now has a compact read-only projection for dispatcher and incident-commander views. It presents dispatch acknowledgements and unit arrivals in canonical world-tick/event-ID order, with source, actor, authority and owning-system references. The projection accepts only rows already obtained through audited officer access; it does not grant access or write to BP11/BP08/BP10 records.


Command handover reconciliation now compares authorised BP08 deployment-assignment snapshots with BP12's incident event chronology. It identifies active assignments without arrival records, arrivals without current assignments, unit-reference mismatches, arrival/state conflicts and active assignments remaining on terminal incidents. It uses canonical BP12 incident statuses, requires snapshot provenance and world-tick context, and reports `handover_ready` only when no unresolved assignments or discrepancies remain. The reconciliation is read-only; callers must obtain each source snapshot through its owning system's authorised reader.


`BP04IncidentLocationResolver.build_authorised_command_handover` now orchestrates the command handover using separate audited permissions for incident inspection, BP08 deployment-assignment inspection and BP12 operational chronology. It calls trusted owner readers only after the corresponding grants pass, then applies the read-only reconciliation. The dispatcher/incident-commander projection cannot independently grant access or bypass owner-system authorisation.


A command-handover record projection now brings together the incident reconciliation, outgoing and incoming commanders, commander decisions and rationales, outstanding actions with named owners, responsibility transfers, and handover acknowledgements. It validates identity, authority/source provenance, chronology, duplicate references, commander attribution and acknowledgement recipients. Readiness requires a clean assignment reconciliation, a recorded transfer from the outgoing to incoming commander, and explicit acceptance by the incoming commander; outstanding actions may remain open when they have named owners and are carried into the handover. The result is explicitly `PROJECTED_NOT_PERSISTED`: no durable handover register or production Neon write is claimed by this projection.


## BP12 durable command handover — implementation in validation

A durable append-only command-handover register has been added in proposal migration `0029_bp12_command_handover.sql`. It records the validated commander handover projection against a BP12 simulation event, preserves outgoing/incoming command identities, effective world tick and source/authority provenance, enforces incoming acceptance and responsibility transfer, supports idempotent replay, and exposes chronological immutable history. PostgreSQL writer/reader adapters and SQL/Python acceptance tests are included. The officer gateway now separately audits handover recording, incident inspection, BP08 assignment inspection and BP12 operational-timeline inspection before persistence; history reads require their own explicit audited grant. Denials stop before protected readers or the writer run. The change is repository/disposable-test only; it has not been applied to production Neon. See [BP12 durable command handover](docs/implementation/BP12-durable-command-handover.md).

### BP12 incident command handover — 2026-11-26

The incident command handover now has a complete read-only reconciliation and audited persistence path. The authorised officer gateway separately checks the command-handover record grant, incident inspection, BP08 assignment inspection and BP12 operational timeline inspection before writing through the BP12-owned register. History reads use a separate audited permission.

Migration proposal `0029_bp12_command_handover.sql` adds an append-only command-handover register, a source simulation event and chronological history reader. Same-key retries are serialised with a transaction advisory lock; identical retries return the original record, while a changed payload using the same key is rejected. The stored document is marked `PERSISTED`. Row-level update/delete and statement-level truncate protections prevent ordinary mutation of the register.

The disposable SQL acceptance test now explicitly activates the test runtime inside its rollback-only transaction, so it exercises the positive persistence path rather than silently taking the inactive-runtime branch. It verifies persistence, successful replay, conflicting replay rejection, update/delete/truncate rejection and rejection of an unready assignment reconciliation. The full PKG-001 disposable PostgreSQL workflow passed in [run 45821133649](https://github.com/Joshuaogri/saltwater/actions/runs/45821133649), including the BP12 SQL acceptance, Python adapter suite, population-cap, storage and backup/restore checks. Database migration validation also passed in [run 45821133762](https://github.com/Joshuaogri/saltwater/actions/runs/45821133762). **No production Neon writes were made.**


## BP04 completion direction — 2026-11-26

BP04 source inventory is frozen for completion work. No further property/building/premises/unit/room/physical-asset expansion is planned unless a concrete gameplay requirement proves it necessary. Remaining effort is directed to authenticated player lookup, authorised police workflow call sites, bounded operational reference interfaces with real consumers, and one consolidated BP04 acceptance audit. Existing BP11/BP08/BP10/BP12/BP16 handoff adapters are integration contracts, not a claim that full CAD, patrol or investigation applications already exist. BP02 operational parcel/address approval remains a separate dependency. See [BP04 completion plan](docs/implementation/BP04-player-police-geography-integration.md#bp04-completion-plan--integration-and-acceptance-only). No production Neon changes are authorised by this work.


### BP04 player command integration — 2026-11-26

The PostgreSQL 16/18 BP04 disposable workflow now includes a real-archive player-command integration test. It drives the player `find` and `inspect` interface against the compressed BP04 archives imported into disposable PostgreSQL, covering all supported inspect entity types, missing/malformed records and no world-time advancement. The test has been added and wired into CI; its first workflow result is pending. This does not change the frozen property inventory or write to production Neon. See [BP04 player/police integration](docs/implementation/BP04-player-police-geography-integration.md).


### BP04 authenticated handover attribution — 2026-11-26

Authorization decisions now expose the verified session's `active_person_id`. BP12 handover persistence checks the submitted preparer reference against a trusted injected personnel-reference verifier before reading owner snapshots or writing. Missing identity, missing resolver or mismatch is denied. The targeted officer-authorization test step passed in [workflow run 45825332438](https://github.com/Joshuaogri/saltwater/actions/runs/45825332438); full workflow is still running. Production use remains blocked until the personnel-service resolver is wired. No production grants or Neon writes were made. See [BP04 player/police integration](docs/implementation/BP04-player-police-geography-integration.md).


### BP04 closure reassessment — 2026-11-26

The production archive release and frozen source inventory remain complete. Player find/inspect now has real archive-backed integration coverage; the latest BP04 workflow has passed its player command, officer authorization and lookup contract steps but remains in its full 420-address reconciliation stage. Authorization decisions now carry the verified session's active_person_id; BP12 handover requires a trusted personnel-reference verifier to match the preparer before reading protected snapshots or writing. Mismatch and missing identity fail closed. Targeted officer authorization and migration validation passed; full BP04 and PKG-001 disposable PostgreSQL runs were still in progress at the time of this update. BP02 operational geography, five priority exceptions, production grants, personnel-service resolver wiring, owner-service consumers and consolidated acceptance remain open. BP04 is not declared complete. No production Neon writes, grants or geography promotions were made. See [BP04 full acceptance audit](docs/implementation/test-evidence/BP04-full-acceptance-audit-2026-11-25.md).


### BP04 CI closure validation — 2026-11-26

The previously pending closure workflows have now passed: BP04 player/police/geography run [45825332438](https://github.com/Joshuaogri/saltwater/actions/runs/45825332438) (12/12 steps), PKG-001 disposable PostgreSQL run [45825332524](https://github.com/Joshuaogri/saltwater/actions/runs/45825332524) (31 database and 25 Python steps), and database migration validation [45825332455](https://github.com/Joshuaogri/saltwater/actions/runs/45825332455) (21/21 steps). These pass the real archive-backed player integration, officer identity boundary tests, full 420-address BP02 structural reconciliation and regression baseline. They do not approve BP02's five operational frontage exceptions, create production grants, wire the production personnel-reference resolver or implement owner-service consumers. BP04 remains NOT COMPLETED pending those dependencies and consolidated division acceptance. No production Neon changes were made.


### BP04/BP06 personnel identity integration — 2026-11-26

Added `PostgresPersonnelReferenceVerifier`, backed by BP06's `sw_police.personnel_service_current` view. Handover preparer references must be the UUID dossier of the verified session's same canonical person and must be active sworn service. Invalid/mismatched references fail closed; database errors propagate. Added a PostgreSQL resolver factory and unit tests, now included in PKG-001 CI. This is repository implementation only; production deployment, BP42 grants, BP02 operational geography and remaining owner-service integrations remain separate blockers. No production Neon changes were made. See [BP04/BP06 personnel integration](docs/implementation/BP04-player-police-geography-integration.md).


The BP06 personnel-reference verifier's four unit tests have passed in [PKG-001 run 45826593214](https://github.com/Joshuaogri/saltwater/actions/runs/45826593214); all 26 Python-kernel steps passed. Disposable PostgreSQL validation remains in progress, so no full workflow pass is claimed yet.


BP04/BP06 update: the repository-side handover identity resolver is now implemented against `sw_police.personnel_service_current`, matching the authenticated session person to an active sworn personnel UUID. Its tests and the full PKG-001 disposable PostgreSQL workflow passed in [run 45826593214](https://github.com/Joshuaogri/saltwater/actions/runs/45826593214). A further session-person propagation test also passed in the Python job of [run 45826915217](https://github.com/Joshuaogri/saltwater/actions/runs/45826915217); the full disposable PostgreSQL and BP04 geography runs remain underway. Production wiring still depends on BP06 schema deployment and production application composition; grants remain default-deny. No production Neon changes were made.


The latest PKG-001 run [45826915217](https://github.com/Joshuaogri/saltwater/actions/runs/45826915217) completed successfully: 26 Python-kernel and 31 disposable-PostgreSQL steps passed, including verified session person-ID propagation, BP06 personnel-reference matching, population-cap, database access and backup/restore checks. The separate BP04 420-address reconciliation run 45826915157 remains in progress. BP04 is not yet declared complete.

### BP02 no-building / frontage-exception cross-register audit — 2026-11-26

Added a read-only reconciliation that counts no-building sites from the independent building-access status, then cross-checks all five frontage exceptions against the 420-row address review using exact address, property, parcel and original-road identities. It explicitly prevents duplicate property IDs across different exception addresses, as well as duplicate source addresses, missing review links and provenance mismatches. The output includes the 36-site list, review-class breakdown and five-row exception crosswalk; the structural audit expects three exception overlaps with no-building sites and two exceptions on sites with building candidates. Regression coverage includes the cross-register duplicate-property case. The newest migration validation passed; full BP02 geometry/cross-register acceptance and PKG-001 disposable PostgreSQL checks are still running, so no final acceptance claim is made yet. See [BP02 address placement review register](docs/implementation/BP02-address-placement-review-register.md). No property inventory, Neon data, canonical address or operational access approval was changed.


## BP04 status correction — 2026-11-26

A previous README entry prematurely described BP04 as closed. That declaration is withdrawn. BP04 is **NOT COMPLETE**. The strict criterion-level audit evaluates all 48 BP04 acceptance criteria: 5 PASS, 19 PARTIAL, 3 BLOCKED and 21 NOT VERIFIED. See [BP04 strict acceptance audit](docs/implementation/BP04-strict-acceptance-audit-2026-11-26.md). The earlier [completion record](docs/implementation/BP04-completion-record-2026-11-26.md) has been corrected and is not a division-closure approval.

The five-digit sequence-suffix defect has been corrected. The generator now creates 10,000 normalized-unique names from a versioned SW-UNS-001 vocabulary, screens within-batch near-duplicates, checks exact collisions against 102 adopted geography names and regenerates both textual and compressed registry files. AC-A04 is now PARTIAL, not FAIL: candidates still require persistent reservation against the complete global naming namespace. AC-A01 remains PARTIAL pending that reservation and the full validity audit. The regenerated registry is 8,171,566 bytes as JSON and 638,533 bytes compressed; the gzip is committed alongside the source JSON. This is a GitHub source-data update only—the production Neon archive was not changed. The next blocker is the shared naming SQL adapter: its current bigint owner ID and GEOGRAPHY/PERSON trigger do not support BP04's text business IDs, so a dedicated text-ID BUSINESS adapter must be implemented and tested on disposable PostgreSQL before these names can be persistently reserved. The source inventory, compressed archive deployment, bounded lookup and selected player/police integration tests are completed deliverables. Ownership/tenancy temporal coverage, complete business identity-quality and lifecycle acceptance, operational geography binding, service-provider interfaces, staff/stock/event integrations, security disclosure acceptance, 10,000-business performance and full traceability remain incomplete or unverified. No new production Neon writes, grants, address promotions or access-point approvals were made.


## BP-01 foundations — 2026-11-26

BP-01 version 1.0 has been reconciled against the approved Saltwater master canon, adopted population/geography decision SW-CANON-001, primate-city decision SW-CANON-002 and universal naming standard SW-UNS-001. Its machine-readable immutable canon contract is in `runtime/bp01_foundations.py`; the exact standalone lowercase `bingo` reveal trigger is shared with the authorization service. The dedicated BP01 contract suite is included in PKG-001 disposable validation. BP-01 is design-complete, while implementation and tests remain in progress and global verification remains blocked pending linked evidence for all cross-division requirements, especially NPC knowledge boundaries and hidden-information non-leakage. No production Neon writes or permission changes were made.


The exact `bingo` command is now recognised only as a standalone lowercase token. It is intentionally omitted from ordinary help. The authenticated player gateway maps it to the player-only `reveal_hidden_truth` authorization action and passes the exact raw trigger to the gate before dispatch. A trusted reveal provider can be injected through the durable application/runtime composition; no case-owned provider or production hidden-truth records have been created yet.

BP-01's dedicated contract workflow passed on 2026-11-26: 12 suites, 128 tests, zero failures ([run 45862390355](https://github.com/Joshuaogri/saltwater/actions/runs/45862390355)). This verifies the foundational canon, exact hidden-truth command path, player gateway, runtime absence freeze, causal event processing, scheduling and recovery contracts within the tested scope. BP-01 remains implementation-in-progress and verification-blocked pending the case-owned reveal provider, cross-channel hidden-truth non-leakage, NPC knowledge boundaries and full host composition. Evidence: [BP-01 run 0001](docs/test-evidence/BP01-foundational-contracts-run-0001.md).


BP-01 foundational contract run 0002 passed on 2026-11-26: 16 test steps, 155 tests, zero failures ([run 45863188374](https://github.com/Joshuaogri/saltwater/actions/runs/45863188374)). It covers the foundational command, authorization, time, event, recovery and synthetic NPC shift contracts. Production dispatch has since been corrected to use existing personnel and memberships only; vacancies do not create NPCs, and the player-bound person is excluded. The opening 500-person police population cohort has not yet been provisioned as BP06 personnel service records. The PKG-001 disposable fixture has zero active personnel service rows, no staffed posts and no available units. Full BP-01 verification remains blocked by cross-division information-boundary, staffing and host-persistence gaps. Evidence: [BP-01 run 0002](docs/test-evidence/BP01-foundational-contracts-run-0002.md).


BP-01 foundational contract run 0003 passed on 2026-11-26: 16 test steps, 156 tests, zero failures ([run 45864752181](https://github.com/Joshuaogri/saltwater/actions/runs/45864752181)). It validates the production NPC source-adapter contract: canonical personnel identities only, player exclusion, no staff fabricated from vacant posts, and BP08 unit-status enforcement. The NPC source integration step also passed in [PKG-001 run 45865031957](https://github.com/Joshuaogri/saltwater/actions/runs/45865031957); the overall PKG-001 workflow remains in progress. Evidence: [BP-01 run 0003](docs/test-evidence/BP01-foundational-contracts-run-0003.md).


BP-01 next-step implementation: BP06 opening police cohort provisioning is now specified in [the implementation note](docs/implementation/BP06-opening-police-cohort-provisioning.md) and migration proposal [0033](db/proposals/0033_bp06_opening_personnel_cohort.sql). It links exactly 500 existing BP03 person IDs to BP06 service dossiers, excludes the human player, preserves the population count and leaves BP05 posts/BP07/BP08 assignments untouched. The first disposable PostgreSQL acceptance passed in [PKG-001 run 45868150806](docs/test-evidence/BP06-opening-personnel-cohort-run-0001.md); no 500-person seed data or production Neon write is included.


## Opening police identity candidates — 2026-11-26

A deterministic BP03 opening police identity candidate generator is now on `main`. It produces 500 varied three-part name candidates from a versioned SW-UNS vocabulary, screens internal exact/near-duplicate names, and writes [readable JSON](data/people/saltwater-opening-police-person-seed-v1.json) plus [compressed JSON](data/people/saltwater-opening-police-person-seed-v1.json.gz) under `data/people/`. Build 0001 passed five generator tests; see [build evidence](docs/test-evidence/BP03-opening-police-person-seed-build-0001.md). Each row has a stable candidate reference but no canonical person ID, personnel category, demographic attributes or personnel appointment. Names are not reserved until checked against the authoritative SW-UNS database registry. This is the identity-seed preparation step, not a BP03 population import or a production Neon write. See [the generator](runtime/opening_police_person_seed.py).

## BP-02 bridge connector engineering register — superseded 2026-11-26

The initial evidence-only connector register was superseded by the fictional gameplay engineering assessments in the BP-02 fictional geography release below. The current canonical register uses site-specific, internally consistent Saltwater game-world specifications for all four Customs Bridge and Harbour Bridge approaches, links them to the source access points and route corridors, and promotes them for gameplay. The earlier `NOT_ASSESSED` / `HOLD_NOT_APPROVED` status is historical and is not the current BP-02 state.


### BP-02 completion confirmed — 2026-11-26

The user accepted BP-02 as complete after the full acceptance workflow passed: [run 45889071983](https://github.com/Joshuaogri/saltwater/actions/runs/45889071983), job `140146960703`. The blueprint and division register now record **DESIGNED / IMPLEMENTED / TESTED / VERIFIED** for the fictional gameplay geography release. This covers the canonical geography source, 420 parcel identities, 420 linked address identities, generated building access-point inventory, five resolved address/frontage dispositions and four bridge connector assessments. The source and evidence are on GitHub `main`; **no BP-02 geography data has been uploaded to production Neon**. Database seeding remains separate.

## BP-02 fictional gameplay geography release — 2026-11-26

BP-02 has now been advanced from design-only status to a fictional in-game operational geography release. The four bridge connectors are assessed as game-world infrastructure: two Customs Bridge and two Harbour Bridge approaches. The assessment register supplies consistent fictional specifications for clear width, vertical clearance, gradient, crossfall, surface, load limit, drainage, access control, lighting, pedestrian access, emergency vehicle suitability and egress. These are explicitly fictional Saltwater facts, not claims about real infrastructure.

The canonical geography builder promotes the 420 stable parcel identities and 420 linked address identities into the gameplay register, materialises the generated building access-point inventory, and binds the four bridge connectors to their engineering assessments. The geography source and identity map are marked approved for gameplay. Stable portable string IDs remain authoritative; database-specific integer spatial IDs are not embedded in source data.

The full BP02 audit now checks the fictional release and canonical counts. Regression coverage includes all four assessments, fail-closed missing-connector handling, and 420/420 parcel/address materialisation. GitHub `main` is the source of truth. This release does not write to Neon; a later database seed can be prepared separately if requested.


### BP-02 canonical address/access integration — 2026-11-26

- Canonical address records now carry the resolved in-game road association while preserving the original BP04 source-road ID as provenance.
- The three unique frontage-road dispositions and two bridge-access dispositions are materialised against their five source addresses.
- The two bridge properties carry their paired connector assessment IDs and approved gameplay access modes; all four connectors remain linked to their source access points and route corridors.
- The released identity-register snapshot now explicitly reports `operational_approval: true` and `RELEASED_FOR_GAMEPLAY`; the immutable design identity source remains preserved as lineage.
- BP-02 acceptance audit version 1.1 now fails CI if the overall operational gameplay release is not PASS. The audit remains read-only; no Neon write is performed.

## BP04 engineering review and performance baseline — 2026-11-26

- Independent Gemini review run: [45901239195](https://github.com/Joshuaogri/saltwater/actions/runs/45901239195). The report is retained as the workflow artifact `gemini-bp04-engineering-review`.
- The reviewed disposable PostgreSQL acceptance reserved and validated all 20,000 public business names (10,000 businesses × trading/legal names) and completed its 10 tests successfully in 1,054.518 seconds (about 17.6 minutes).
- The review identified repeated per-name SQL function/trigger work, trigram screening, owner-row locking, and reservation-event writes as areas to measure. It did not provide a per-statement EXPLAIN profile or a granular CPU profile; these remain hypotheses for optimisation, not proven bottleneck attribution.
- **Driver correction for future reviews:** the repository installs `psycopg[binary]>=3.2,<4`. Psycopg 3.1+ uses pipeline mode internally for `executemany()`; therefore it is incorrect to assume 20,000 independent network roundtrips from the Python call alone. Separate per-item SQL executions from actual network synchronization points. Reference: [Psycopg pipeline mode documentation](https://www.psycopg.org/psycopg3/docs/advanced/pipeline.html).
- Gemini's suggested bulk-function sketch is not adopted verbatim. The canonical row trigger must continue to enforce the 0.90 near-duplicate threshold for every writer; moving threshold configuration only into one batch entry point could leave other insert paths dependent on caller session settings. Any batch optimisation must preserve trigger enforcement, exact uniqueness, stable text IDs, owner locking, generator-manifest validation, provenance, idempotency, and atomic rollback.
- Next BP04 experiment: collect phase timings, statement counts, representative `EXPLAIN (ANALYZE, BUFFERS)` output, and lock/wait evidence on disposable PostgreSQL before changing the reservation path.

## SW-DB-001 contract correction — 2026-11-26

- Corrected `tests/pkg001/test_sw_db_001_contract.py` so proposal isolation checks reject the exact disposable proposal `0010_canonical_world_provisioning.sql`, rather than rejecting every source migration with the `0010_` prefix.
- The broader prefix assertion incorrectly rejected the legitimate source migration `0010_bp04_lawful_use_building_control.sql`.
- Fix committed on `main`: `34c72d0ce3057740a8f9c9f268697d8fbb2e1afe`. The new SW-DB-001 Python regression job passed all tests, including the previously failing contract check.


## Claude independent engineering review — 2026-11-26

A separate, manually triggered GitHub Actions workflow, [Claude independent engineering review](.github/workflows/claude-bp04-review.yml), is available alongside the Gemini BP04 reviewer. It accepts a PKG-001 run ID and a Claude model ID (default: `claude-sonnet-5-5`), collects the available BP04 workflow evidence and relevant source files, and publishes a Markdown report plus a 14-day artifact. The workflow uses the Anthropic Messages API and requires the repository Actions secret `ANTHROPIC_API_KEY`.

The Claude workflow has read-only `actions: read` and `contents: read` permissions. It does not write repository files, access production Neon, or make database changes. If a selected PKG-001 run is still active and its full logs are unavailable, Claude receives the available job/step metadata and is instructed not to infer runtime measurements. Keep all universal naming, duplicate-screening, provenance, immutability, idempotency, atomicity and population-cap safeguards intact. Configure the API key under [GitHub Actions secrets](https://github.com/Joshuaogri/saltwater/settings/secrets/actions) as `ANTHROPIC_API_KEY`; never put the key in source code or chat.

To run it, open [Actions → Claude independent engineering review](https://github.com/Joshuaogri/saltwater/actions/workflows/claude-bp04-review.yml), choose **Run workflow**, enter a PKG-001 run ID, and optionally change the model ID. Current model IDs are listed in [Anthropic's model overview](https://platform.claude.com/docs/en/models/overview). The default Sonnet model is intended as a balanced code-review option; API access and billing must be enabled for the Anthropic account.


## DeepSeek independent engineering review — 2026-11-26

A third, manually triggered read-only reviewer is available through [DeepSeek independent engineering review](.github/workflows/deepseek-bp04-review.yml), alongside Gemini and Claude. It accepts a PKG-001 run ID and a DeepSeek model ID (default: `deepseek-v4-pro`), gathers the BP04 run evidence and the same canonical Python/SQL source files, and publishes a Markdown report plus a 14-day artifact. It uses the official DeepSeek Chat Completions API at `https://api.deepseek.com/chat/completions` with thinking enabled. The workflow requires the repository Actions secret `DEEPSEEK_API_KEY`.

The workflow has only `actions: read` and `contents: read` permissions. It does not commit code, access production Neon, or make database changes. It preserves the universal naming registry, exact and trigram duplicate screening, stable IDs, owner locking, generator manifest validation, provenance, immutable history, idempotency, atomicity and rollback requirements. If the selected PKG-001 run is still active and full logs are unavailable, it supplies available job/step metadata and instructs DeepSeek not to infer runtime measurements.

To run it, open [Actions → DeepSeek independent engineering review](https://github.com/Joshuaogri/saltwater/actions/workflows/deepseek-bp04-review.yml), choose **Run workflow**, enter a PKG-001 run ID, and leave the model as `deepseek-v4-pro` or select `deepseek-flash`. Configure `DEEPSEEK_API_KEY` under [GitHub Actions secrets](https://github.com/Joshuaogri/saltwater/settings/secrets/actions). GitHub does not reveal saved secret values, so successful authentication will be confirmed by the workflow run; never put the key in source code or chat. See [DeepSeek official Chat Completions API documentation](https://api-docs.deepseek.com/api/create-chat-completion/).

## Fast, evidence-backed AI engineering fixes

Gemini and DeepSeek are independent engineering reviewers intended to help resolve verified problems quickly. Their reviews must prioritise the smallest practical, evidence-backed fix rather than lengthy speculative redesigns. When a clear fix is supported by repository/run evidence, they should state the exact files and changes, explain why the fix resolves the failure, and specify focused regression tests.

Saltwater's implementation workflow is to act promptly on a recommendation when it demonstrably addresses the problem and preserves all canonical invariants: implement directly on `main`, run the relevant regression and acceptance checks, inspect the resulting workflow outcomes, and update the README. Do not wait for unnecessary re-approval for ordinary fictional-game code fixes. Do not blindly apply unsupported hypotheses, weaken tests or safeguards, bypass canonical database paths, or write to production Neon without the user's explicit approval. If the evidence is insufficient, identify the fastest targeted experiment needed to establish the cause.

DeepSeek's current run `45905783120` was reached successfully but the API returned HTTP 402 `insufficient_balance_error`; the configured key was present, but the account had insufficient API balance for the request. Add API credit in the [DeepSeek platform](https://platform.deepseek.com/) before rerunning the reviewer.

### Latest PKG-001 population fixture measurement (2026-11-26)

Successful run [45901786454](https://github.com/Joshuaogri/saltwater/actions/runs/45901786454) completed both Python and disposable PostgreSQL jobs. The set-based population-cap fixture ran from approximately 22:21:48 to 22:38:48 UTC (about 17 minutes). The concurrent admission test then passed in under one second. Backup/restore reconciliation matched exactly: 10,000 people, 10,000 population states, 10,000 population-history rows, 30,115 name reservations and 60,233 name events. The deliberate extra admission at the 10,000-person boundary was rejected as expected.

This elapsed interval identifies a high-priority optimisation target but is not yet a phase-level profile. Do not infer the precise hot operation from elapsed time alone. The next safe experiment is to add phase timings around staging generation, event insertion, person insertion/name-registry trigger work, population-state insertion and final reconciliation in the disposable fixture; preserve all canonical triggers, exact/near-duplicate checks, history and concurrency assertions. Then use Gemini's independent review on this successful run. DeepSeek review remains blocked until the DeepSeek API account has sufficient balance.

The disposable population fixture now emits `CAP_FIXTURE_PHASE` timing notices for PERSON_CREATED events, people plus canonical name-registry trigger work, population-state events, population-state/history insertion, and final reconciliation. These are measurement-only notices; they do not change fixture data, triggers, transaction boundaries, safeguards or acceptance criteria. Use the next successful PKG-001 PostgreSQL run to identify the dominant phase before selecting an optimisation.


### BP02 compressed geography release package measurement — 2026-11-26

Added a deterministic, read-only package measurement workflow at [BP02 Geography Release Package Measurement](.github/workflows/bp02-release-package-measurement.yml). The workflow passed in [run 45908083960](https://github.com/Joshuaogri/saltwater/actions/runs/45908083960). It validates all 100 SW-GEO-V1 stable source identities (100 resolved, zero unresolved) and builds a reproducible gzip archive containing the geography source and identity map.

Measured source size: **596,267 bytes**. The initial GNU-tar measurement produced a 25,212-byte archive (SHA-256 `8b185559fa26ef732920afc055b12286d8fd88469e97f5672c7bcbd9a610f007`). The production-importer builder uses a deterministic Python PAX tar format; its canonical package is **25,689 bytes** (0.0257 MB; 4.3083% of source size, a 95.69% reduction), SHA-256 `6b46d62a944334a1853bc7190e33476bb06adc835e433d5592d6b0ee4c700d0c`. The latter is the package measured by the importer acceptance workflow and is the correct size for the archive-only import path.

This is a measured source-package size, **not** a Neon storage-growth estimate. The workflow has no Neon connection and made no database changes. A read-only production check on 2026-11-26 measured `pg_database_size` at **9,781,248 bytes** (9,552 kB); the only application tables are the three `sw_core` tables and two `sw_ops` tables. No `sw_geo` schema or BP02 geography tables exist in production. The package is therefore measured but not deployed. Database growth must be benchmarked against the actual proposed schema/import on a disposable PostgreSQL database before a production estimate or approval request.


### BP02 archive-only importer and disposable storage benchmark — 2026-11-26

Initially, BP-02 archive persistence was added as global migration 0013 and tested in [run 45908582591](https://github.com/Joshuaogri/saltwater/actions/runs/45908582591). That placement incorrectly coupled BP-02 to the BP04 global sequence. It has since been superseded by the independent BP-02 domain migration stream documented below; the former global migration 0013 has been removed from `db/migrations/`, and the legacy archive regression workflow now invokes the independent runner. The original run remains historical evidence for the archive payload and idempotent importer, not for the final independent migration path.

The canonical importer archive is **25,689 bytes**. On disposable PostgreSQL, the first archive insert increased `pg_database_size` by **81,920 bytes**; repeating the identical import increased it by **0 bytes**. The disposable database grew from 11,992,087 to 12,074,007 bytes for the archive insert. The full ordered migrations 0001–0013 increased the empty disposable database from 7,773,207 to 11,992,087 bytes (4,218,880 bytes); that includes the BP04 schema migrations 0003–0012 and must not be attributed to BP02 alone.

**Production remains untouched.** The live Neon migration ledger has only versions 1 and 2 applied; global BP04 migrations 0003–0012 remain pending. BP-02 no longer occupies the global migration sequence: its independent `scripts/migrate_bp02.py` runner applies only `db/domain-migrations/bp02/0001_source_archive.sql` and records it in `sw_geo.bp02_schema_migration`. It does not require BP04 migrations 0003–0012 and does not modify `sw_ops.schema_migration`. The separate BP02 runner defaults to a no-write dry run; production application requires `--apply`, `--expected-database neondb` and `--allow-production`. This archive-only release stores source bytes and does not create operational geography entities, routes, parcels, addresses or access points.


### BP-02 independent domain migration and PostgreSQL 18.7 benchmark — 2026-11-27

BP-02 archive persistence now has an independent migration stream at `db/domain-migrations/bp02/`, separate from the global platform/BP04 sequence in `db/migrations/`. Its dedicated runner, `scripts/migrate_bp02.py`, maintains the checksum-controlled `sw_geo.bp02_schema_migration` ledger and does not read, modify, or require `sw_ops.schema_migration`. It refuses database-name mismatches, defaults to a no-write dry run, and requires both `--apply` and `--allow-production` for the production database name `neondb`.

The isolated migration creates only the BP-02 archive persistence schema and immutable source archive table. It does not apply BP04 migrations 0003–0012 or promote operational geography records. The existing global migrations and the BP04 production release workflow are unchanged.

A dedicated GitHub Actions workflow, [BP02 Independent Domain Migration — PostgreSQL 18.7](.github/workflows/bp02-independent-domain-migration.yml), passed in [run 45910034882](https://github.com/Joshuaogri/saltwater/actions/runs/45910034882). It tested the independent stream on PostgreSQL 18.7, validated 100/100 geography identities, confirmed dry-run creates no schema, applied only the BP-02 domain migration, imported the archive, and verified repeat migration/import idempotency. The global `sw_ops.schema_migration` ledger remained absent throughout the isolated test.

Measured on the clean PostgreSQL 18.7 fixture: baseline **7,935,679 bytes**; after BP-02 schema **8,083,135 bytes** (schema growth **147,456 bytes**); after the 25,689-byte archive import **8,165,055 bytes** (archive insertion growth **81,920 bytes**); identical repeat migration and import **0 bytes** additional growth. Total isolated BP-02 delta: **229,376 bytes**. The source package remains 596,267 bytes and compresses to 25,689 bytes.

For planning only, adding the measured 229,376-byte delta to the last read-only production baseline of 9,781,248 bytes gives a provisional projected total of **10,010,624 bytes**. This is an estimate, not a production measurement: the production database has its existing foundation objects and data, and exact growth must be confirmed by the post-deployment size query. Reconfirm the live baseline immediately before any release.

This implementation is a deployment-path change only. **No production Neon writes have been made.** Production deployment still requires separate explicit approval after a fresh baseline check, backup/restore-point reference and final release plan.


**Production release preparation (2026-11-27):** Reconfirmed the live Neon production database read-only at 9,781,248 bytes on PostgreSQL 18.7, with global migrations 1–2 only and no BP-02 schema/archive tables. The corrected global database migration validation passed in [run 45910255603](https://github.com/Joshuaogri/saltwater/actions/runs/45910255603). A gated [BP-02 production release runbook](docs/deployment/BP02-production-release-runbook.md) now records preflight checks, the measured storage envelope, execution order, post-release verification and recovery handling. It is a prepared procedure only: no production Neon writes have been made, and explicit user approval is still required before execution.


### BP02 current-production recovery-point check — 2026-11-27

A read-only Neon control-plane audit found one manual snapshot, `snap-calm-credit-bdfp5tog` (created 2026-11-25 17:37:13 UTC), named “Saltwater BP04 pre-production release 2026-11-25”. The production branch metadata identifies it as the source used to create the current production branch. Its source branch is no longer present, and the current production branch has no automatic snapshot schedule configured. This is historical restore provenance, not a fresh snapshot of the current production branch immediately before the BP02 release. The runbook now records this finding; a current-production recovery point must be created or otherwise confirmed and its ID/time recorded before any production migration/import. No snapshot or production database write was made during this audit.


The Neon manual snapshot attempt was blocked by the project's snapshot limit. To avoid deleting the only historical snapshot, a no-compute copy-on-write recovery branch was created from the current production branch instead: `br-gentle-moon-bdtc0y32`, parent `br-still-cloud-bdvaw8u4`, parent LSN `0/FFB0F510`, parent timestamp `2026-11-26T23:30:47Z`, created `2026-11-27T00:35:27Z`. Neon reports the branch `ready`; it has no compute, and creation reported zero compute time and data transfer. This is a branch-level recovery point, not a manual snapshot. SQL verification on that no-compute branch was unavailable because it has no endpoint. Preserve it unchanged through the BP02 release; do not add compute or delete it as part of routine cleanup. The runbook records the exact identifiers and limitation.


### BP02 production archive release — 2026-11-27

After explicit user approval, a fresh read-only production check found that the BP02 independent schema migration was already present in Neon. The assistant did not apply that schema migration. Production currently has the BP02 ledger version 1 with checksum `0801ca73441e3170df270d55747ca18ad3b2ede4937dec11c74b106b490c1850`, but **zero** `SW-GEO-V1` archive rows. The global migration ledger remains versions 1 and 2 only.

The current production database baseline is **9,879,552 bytes** on PostgreSQL 18.7. The schema-only increase from the earlier 9,781,248-byte baseline is 98,304 bytes. The remaining archive insertion is benchmarked at 81,920 bytes, giving a provisional projected total of **9,961,472 bytes**. The actual size must be measured after insertion.

Added the manual-only workflow [BP02 archive-only production release](.github/workflows/bp02-production-archive-release.yml). It is restricted to `main`, requires the exact confirmation input and recorded recovery-branch ID, checks the exact live database baseline, verifies the source migration checksum and canonical 25,689-byte archive digest, inserts only the immutable archive, checks that global migrations remain unchanged, and verifies repeat-import idempotency. It uses the existing GitHub Actions `DATABASE_URL` secret. The runbook is updated at [BP02 production release runbook](docs/deployment/BP02-production-release-runbook.md).

**Production release verified complete (2026-11-27):** GitHub Actions run [45990887217](https://github.com/Joshuaogri/saltwater/actions/runs/45990887217) completed successfully. It inserted exactly one immutable `SW-GEO-V1` archive row with SHA-256 `6b46d62a944334a1853bc7190e33476bb06adc835e433d5592d6b0ee4c700d0c`; compressed archive 25,689 bytes, source data 596,267 bytes, two source files, and identity validation 100 resolved / 0 unresolved. The workflow measured production at **9,961,472 bytes**, an actual increase of **81,920 bytes** from the guarded 9,879,552-byte baseline. Repeat import returned `already_present` and added zero bytes. A separate read-only Neon query independently confirmed the row, metadata, checksum, BP02 ledger version 1 and unchanged global migration versions [1, 2]. Release scope remains `SOURCE_ARCHIVE_ONLY`; operational geography was not promoted. Recovery branch `br-gentle-moon-bdtc0y32` remains preserved.

## BP-02 operational geography deployment preparation

The BP02 `SW-GEO-V1` source archive-only production release remains complete and independently verified. A separate operational-geography readiness assessment is now recorded in [BP-02 Operational Geography Deployment — Readiness Assessment](docs/deployment/BP02-operational-geography-readiness.md).

Production Neon was read-only verified at **9,961,472 bytes** on PostgreSQL 18.7. It contains the immutable source archive but no operational geography tables. The source road graph contains 42 roads, 367 nodes, 685 segments and 5 routes; all 100 source identity mappings resolve. The 420 parcel/address records and 768 access-point/connector records remain design candidates, not operational records. The address review queue has 5 P1, 33 P2 and 382 P3 records; none is operationally approved.

No production operational-geography write has been performed. The existing 130,973,696-byte BP04 Stage E disposable benchmark represents a much broader physical-asset inventory and is not used as the BP02 geography estimate. A dedicated PostgreSQL 18.7 geography benchmark and end-to-end deployment test must establish the exact delta before a separate explicit production approval.


## BP02 operational-geography deployment preparation — 2026-11-27

A read-only review of the successful full acceptance artifact from run
[45889071983](https://github.com/Joshuaogri/saltwater/actions/runs/45889071983)
confirms that the approved gameplay release register contains 420 canonical
parcels, 420 canonical addresses, 420 primary property-address links, 2,948
building access-point locators and four bridge connector candidates. The
underlying SW-GEO-V1 source contains 8 districts, 24 neighbourhoods, 54
geographic features, 42 named roads, 367 network nodes, 685 road segments and
five routes. The full acceptance report records operational approval and zero
unresolved address-road-access exceptions; it also records that no database or
Neon write was performed.

Important status semantics must be retained during seeding: the 2,948 access
point records are canonical gameplay locators, but their point status remains
unreviewed and their road links are proximity candidates, not confirmed routes.
The four bridge connector records also retain unreviewed geometry and
not-assessed physical/legal access fields. Importing these records must not
silently promote them to verified entrances or routable connectors.

A source-only sizing check of the canonical geography register measured
5,039,798 bytes as deterministic JSON and 204,098 bytes as gzip. These are
package sizes, not PostgreSQL storage-growth measurements. The full audit
artifact is 9,225,005 bytes and must not be imported wholesale; the deployment
package should contain only the source and canonical gameplay records required
by operational queries.

Production Neon remains unchanged by this preparation. Its current measured
database size is 9,961,472 bytes. It currently has the BP02 migration ledger
and immutable source archive, but no operational geography tables, no
sw_geo.entity/sw_geo.version foundation and no sw_property schema.

The current scripts/migrate_bp02.py is still hard-coded to migration 0001;
it must be extended to a checksum-verified sequential BP02 migration stream
before an operational schema migration can be deployed. The existing global
proposal 0013 is explicitly a disposable candidate-only parcel/address
profile schema and is not an approved production migration. A separate
PostgreSQL 18.7 disposable schema-and-seed benchmark is required before any
production storage estimate or release approval. No production write is
authorised by this preparation note.


## BP02 operational geography package preparation — 2026-11-27

Added `runtime/bp02_operational_geography_package.py`, which reruns the complete BP02 gameplay acceptance audit and builds a deterministic, gzip-compressed, source-hash-pinned operational geography release package. It includes the canonical geography source, identity map, gameplay parcels and addresses, building access points, bridge connectors and their acceptance evidence. The builder refuses to package unless the full acceptance and operational authority gates pass and all expected record counts match. It writes only local build artifacts and explicitly records that no database write occurred.

The package validation workflow is [BP02 Operational Geography Package — PostgreSQL 18.7 Source Validation](.github/workflows/bp02-operational-geography-package.yml). It runs the package regression, measures compressed/uncompressed bytes, verifies source and package checksums, and uploads the package and manifest as a CI artifact. Run [45994846380](https://github.com/Joshuaogri/saltwater/actions/runs/45994846380) was still running at the time this note was added; no package size or test success is claimed until it completes.

This is a release-package build and measurement stage only. It does not create operational Neon tables, write production data, or authorise a production deployment. The next stage is a separate PostgreSQL 18.7 disposable schema/import benchmark, including per-layer growth, total growth, index/relation sizes, idempotency and lookup-plan tests. Production Neon remains at the last independently verified baseline of 9,961,472 bytes until any separately approved deployment.


BP02 release-authority correction (2026-11-27): the operational geography package now distinguishes fictional gameplay acceptance from production database seed authority. Canonical `ACTIVE_IN_GAME` statuses and fictional bridge assessments remain intact; the immutable identity map's `operational_seed_approved=false` is preserved as `production_seed_approved=false`. No production operational-geography write is authorised by gameplay acceptance. See [BP02 readiness assessment](docs/deployment/BP02-operational-geography-readiness.md).

### Gemini collaboration — active-blueprint review sizing

The GitHub Actions Gemini reviewer is explicitly assigned the current active blueprint on every run (BP02 at present). Its BP02 evidence pack is deliberately curated to the operational-geography blueprint, readiness/runbook, package and acceptance code, focused tests, workflow, and canonical geography/identity data. Changed files are added to that pack. Requests are capped at 45,000 characters per slice, and transient Gemini capacity failures use longer exponential retry waits. The reviewer remains read-only and cannot write to production Neon. This reduces request size and irrelevant context; successful Gemini review still depends on the API account's available capacity.


### BP02 simplification — single acceptance pass

The operational-geography package workflow now runs the complete BP02 acceptance audit once, builds the deterministic package from that result, then performs only lightweight checksum/decompression checks before uploading the artifact. The previous separate regression step rebuilt the full audit twice more and was removed from this release workflow. Focused unit tests remain available for code changes that specifically need them; they are not redundantly run alongside the full acceptance build on every package release. This is a CI-efficiency change only: acceptance criteria and production-write protections are unchanged.


## BP02 operational geography schema — preparation

The BP02-owned migration stream now includes `0002_operational_geography.sql`, a compact gameplay schema for districts, neighbourhoods, geographic features, roads, junction nodes, road segments, named routes and ordered route links, plus canonical parcel, address, access-point and bridge-connector records. It uses stable source identifiers, JSON geometry/payloads and ordinary PostgreSQL indexes; it does not require PostGIS or alter the global/BP04 migration ledger.

The BP02 migration runner applies numbered domain migrations in order and verifies each exact SHA-256 checksum. Gameplay records are explicitly labelled `ACTIVE_IN_GAME`; the release record keeps `production_seed_approved=false` unless separately authorised. At the time this note was written, this was schema preparation only. The importer and disposable end-to-end acceptance were subsequently completed; see the dated acceptance and isolated storage measurement below. Production Neon remains unchanged.




## BP02 operational geography — disposable end-to-end acceptance passed (2026-11-27)

The complete [BP02 operational geography workflow](https://github.com/Joshuaogri/saltwater/actions/runs/46001930271) completed successfully on main commit `554da810c7136ebc6c9c113e4ccc26e40c40b14d`. This supersedes the earlier preparation notes above that described the importer and disposable import benchmark as future work.

The workflow built and checksum-verified package SHA-256 `872c1829826336b0901c3de60086038aa4fad324ef289762418b3bcb1a384f03`: 227,468 compressed bytes and 5,353,853 uncompressed bytes. Full BP02 acceptance status was PASS. The package contained 8 districts, 24 neighbourhoods, 54 features, 42 roads, 367 network nodes, 685 road segments, 5 routes, 420 parcels, 420 addresses, 2,948 access-point locators and 4 bridge connector candidates.

Both BP02 domain migrations applied successfully to disposable PostgreSQL 18.7. The operational importer inserted all expected records, including 116 ordered route-node links and 111 route-segment links. The workflow verified per-table counts: districts 8; neighbourhoods 24; features 54; roads 42; nodes 367; segments 685; routes 5; route nodes 116; route segments 111; parcels 420; addresses 420; access points 2,948; bridge connectors 4. The first import produced a measured disposable database size of 14,915,263 bytes from a pre-migration baseline of 7,935,679 bytes (net increase 7,979,584 bytes across schema and data). A repeat import returned `already_present` and added exactly 0 bytes.

The workflow artifact `bp02-operational-geography-v1-package` (211,841-byte ZIP) is available from [run 46001930271](https://github.com/Joshuaogri/saltwater/actions/runs/46001930271). The release record explicitly retains `production_seed_approved=false`; this successful disposable import is not a production authorisation. No production Neon writes were performed. Production sizing and any production release remain a separate decision, using the measured production baseline and avoiding double-counting the already-installed BP02 archive/migration foundation.

The BP02 Gemini review on the same commit did not produce a report: the API returned `RESOURCE_EXHAUSTED` after its configured retries. This is a reviewer-capacity failure, not a BP02 acceptance failure; no Gemini approval is claimed. The main database-migration validation workflow also passed. The wider PKG-001 disposable PostgreSQL workflow was still running when this note was written.


## Free AI coding collaboration

Shared coding-agent rules and the zero-cost toolchain setup are documented in [AGENTS.md](AGENTS.md), [Gemini instructions](GEMINI.md), [Copilot instructions](.github/copilot-instructions.md), and the [free AI coding toolchain guide](docs/development/free-ai-coding-toolchain.md). Development remains on `main` only; production Neon remains protected.


## BP02 isolated operational storage measurement — passed (2026-11-27)

The updated [BP02 operational geography workflow](https://github.com/Joshuaogri/saltwater/actions/runs/46003181718), on main commit `0b3da715f1cd8409446ae23643fcde9a46499ace`, completed successfully. Its new measurement stage applies `0001_source_archive` and measures the database, then applies `0002_operational_geography` and measures again. On disposable PostgreSQL 18.7, the database measured 8,083,135 bytes after 0001 and 8,533,695 bytes after 0002: the incremental 0002 schema growth is exactly **450,560 bytes**.

After importing the operational geography package, the database measured 14,964,415 bytes. Subtracting the post-0002 schema measurement gives **6,430,720 bytes** of operational data/import growth. The combined incremental addition attributable to 0002 plus the operational import is therefore **6,881,280 bytes**. A repeat import added **0 bytes**. Full acceptance and package generation completed successfully in the same workflow.

Production currently measures 9,961,472 bytes and already contains the 0001 archive foundation but not 0002 or operational geography. On that baseline, the estimated post-release total is **16,842,752 bytes** (approximately 16.07 MiB), assuming comparable storage behaviour. This is a disposable-database projection, not a production measurement. The estimate adds only the isolated 0002 and data increments, so 0001 is not double-counted. No production Neon writes were performed; `production_seed_approved=false` remains in force, and operational production release still requires the user's explicit approval.


## BP03 individual simulation — tiering and permanent relevance promotion

BP03 now includes the individual-simulation tier and permanent police-relevance promotion service in `db/proposals/0036_bp03_individual_simulation_promotion.sql`. Each canonical person can carry a processing tier from registry (0) through routine/detail tiers to persistent full detail (3). Tier transitions retain append-only, event-linked history and source, actor, trigger and reason provenance. A material police/case relevance promotion records its trigger and is irreversible: tier 3 cannot be downgraded, including after case closure. The read-only summary exposes current tier and promotion status without creating a second person identity.

The focused disposable acceptance workflow is [BP03 Individual Simulation Acceptance](https://github.com/Joshuaogri/saltwater/actions/workflows/bp03-individual-simulation-acceptance.yml). It exercises default tier, tier progression, promotion provenance, idempotent retry, downgrade rejection and immutable history. The proposal remains a source/disposable implementation; it has not been applied to production Neon. This slice does not claim that routines, movement, NPC knowledge or the complete BP03 division are finished.


The focused acceptance completed successfully on 2026-11-27 in [run 46039112729](https://github.com/Joshuaogri/saltwater/actions/runs/46039112729). The disposable PostgreSQL 16.16 schema-only growth for proposal 0036 was **139,264 bytes**. Acceptance verified tier 0 → 1 → 3, permanent promotion provenance, idempotent retry, downgrade rejection, append-only tier history and exactly one promotion record. The transaction rolled back; no population records were retained. See [BP03 tier and promotion acceptance evidence](docs/implementation/test-evidence/BP03-individual-simulation-tier-promotion-acceptance-0001.md).


## BP03 routines and movement — disposable acceptance passed

BP03 now also has `db/proposals/0037_bp03_person_routines_and_movement.sql`. It records effective-dated, structured person routines separately from attendance, supports explicit routine succession, and stores sourced movement events with origin/destination references, travel mode, certainty, confidence and simulation time. Routine and movement records are append-only; retries are idempotent; future movement and movement chronology regressions are rejected. The current-routine view respects the simulation tick and successor chain.

The expanded focused workflow [46039460668](https://github.com/Joshuaogri/saltwater/actions/runs/46039460668) passed on 2026-11-27. It verified routine replay, replacement/supersession, movement certainty, movement summary, future-event rejection and immutable history. See [BP03 routines and movement acceptance evidence](docs/implementation/test-evidence/BP03-person-routines-movement-acceptance-0001.md). These records are a person simulation data contract; actual schedule execution remains BP37 and route resolution remains BP02. No production population data was written.


## BP03 person knowledge boundary — disposable acceptance passed

BP03 now includes `db/proposals/0038_bp03_person_knowledge_boundary.sql`. A person's knowledge item must reference a canonical source event and retain its knowledge kind, source person where applicable, acquisition tick, confidence and provenance. The write contract rejects knowledge acquired before its source event or after the current simulation tick. Knowledge history is append-only and stores information references rather than exposing hidden global truth directly.

The focused [BP03 Individual Simulation Acceptance workflow](https://github.com/Joshuaogri/saltwater/actions/runs/46039675633) passed on 2026-11-27, including source/recipient identity, knowledge provenance, idempotent replay, summary reconciliation and immutable-history checks. See [BP03 knowledge-boundary acceptance evidence](docs/implementation/test-evidence/BP03-person-knowledge-boundary-acceptance-0001.md). This establishes a data boundary, not a complete NPC reasoning engine. No Neon production migration or population seed was performed.


## BP03 person attribute claims and registry tier initialisation — passed

Every canonical person now receives a persisted tier-0 registry state and creation-history entry automatically. BP03 also includes `db/proposals/0039_bp03_person_attribute_claims.sql`, an append-only sourced-claim ledger for a bounded set of non-sensitive identity and demographic attributes. It preserves reported, estimated, confirmed and disputed claims, supports explicit supersession and does not silently resolve conflicting values.

The complete focused BP03 workflow [46040104903](https://github.com/Joshuaogri/saltwater/actions/runs/46040104903) passed on 2026-11-27. In one disposable PostgreSQL run it applied proposals 0036–0039 and passed tier/promotion, routine/movement, sourced knowledge and conflicting attribute-claim acceptance. Evidence: [tier and promotion](docs/implementation/test-evidence/BP03-individual-simulation-tier-promotion-acceptance-0001.md), [routines and movement](docs/implementation/test-evidence/BP03-person-routines-movement-acceptance-0001.md), [knowledge boundary](docs/implementation/test-evidence/BP03-person-knowledge-boundary-acceptance-0001.md), and [attribute claims](docs/implementation/test-evidence/BP03-person-attribute-claims-acceptance-0001.md). These are disposable schema and transaction tests; they do not represent a production population seed.


## BP03 opening 9,500 identity names — SW-UNS preflight passed

The dedicated [BP03 Opening Identity Registry Acceptance](https://github.com/Joshuaogri/saltwater/actions/runs/46040287960) passed on 2026-11-27. It reserved all 500 police candidate names and all 9,000 civilian candidate names against the disposable authoritative SW-UNS registry, checking unique canonical identities, unique normalized names, candidate manifest integrity and exact opening arithmetic (9,500 people, 500 unused places under the 10,000 cap). Civilian/police exact-name overlap was checked before reservation. Both cohort tests rolled back their transactions; no canonical population or production Neon records were created. See [opening identity preflight evidence](docs/implementation/test-evidence/BP03-opening-9500-identity-name-registry-preflight-0001.md).


## BP03 10,000-person cap and concurrency — passed

The focused [BP03 Individual Simulation Acceptance](https://github.com/Joshuaogri/saltwater/actions/runs/46042030165) passed on 2026-11-27. The disposable fixture reached 9,999 people, then raced two concurrent admissions for the final slot: exactly one succeeded and the other was rejected. Final counts reconciled to 10,000 canonical people, 10,000 included living people, 10,000 tier states, 10,000 tier-history rows and a population counter of 10,000. The disposable database measured **37,592,087 bytes**; proposal 0036 schema-only growth was **139,264 bytes**. These are PostgreSQL 16.16 disposable measurements, not Neon estimates. Full evidence: [BP03 10,000-person cap and concurrency](docs/implementation/test-evidence/BP03-10000-person-cap-concurrency-acceptance-0001.md).


## BP03 integrated opening world — passed

The integrated [SW-DB-001 disposable world provisioning and capacity proof](https://github.com/Joshuaogri/saltwater/actions/runs/46041993980) passed on 2026-11-27. BP03's population union and BP02-linked residence service were applied with the individual-simulation proposals. The opening fixture reconciled **9,500 canonical people** (9,000 usual residents and 500 physically present police-subset cohort members), then the full shared-cap test reached **10,000** with exactly one successful concurrent final-slot admission. Final world counts were 10,000 people, 10,000 counted living people, 10,000 businesses and 10,000 business-name reservations; simulation tick remained 0. Residence integration, lifecycle history, rollback, idempotency, query-latency and backup/restore checks passed.

The disposable database measured **57,506,839 bytes** after the 9,500-person / 10,000-business opening fixture, with **43,573,248 bytes** fixture growth. BP03 population + residence schema growth was **212,992 bytes** and BP03 individual simulation schema growth was **532,480 bytes**. These are disposable PostgreSQL measurements, not Neon estimates. See [BP03 integrated opening world evidence](docs/implementation/test-evidence/BP03-integrated-opening-world-acceptance-0001.md).

Boundary: the 500 police-subset members in this structural fixture are counted as physically present, not as active police-service dossiers. Actual BP06 personnel, BP07 careers and BP08 unit assignments remain separate. The 9,000 resident-to-dwelling allocation is still candidate-only; this run did not materialise all residence/household rows or write production Neon data.

## BP03 integrated acceptance workflow — individual simulation coverage added (2026-11-27)

The SW-DB-001 disposable world workflow now executes all four BP03 individual-simulation transaction acceptance scripts immediately after applying proposals 0036–0039: tier progression and irreversible case-relevance promotion, sourced/conflicting attribute claims, event-bounded person knowledge, and effective-dated routines with sourced movement. Each script is also included in the workflow path filters so changes to an acceptance contract trigger the integrated disposable run. These tests execute in the disposable PostgreSQL service and roll back their test transactions; this workflow change does not write to production Neon.

The preceding run [46043958824](https://github.com/Joshuaogri/saltwater/actions/runs/46043958824) was cancelled during the BP02 operational-geography import. Its Python regression job passed, but the disposable database job did not reach the BP03 acceptance steps; no integrated database pass is claimed from that run. The workflow update is committed on main as [4b2a174](https://github.com/Joshuaogri/saltwater/commit/4b2a174c594b59c303be6d198865fc9ec635b5ff). The next run will provide the integrated result.

## BP03 resident identity crosswalk and repeat-run integrity — verification in progress (2026-11-27)

The disposable BP03 residence materialiser now resolves each of the 9,000 civilian candidates through its stable `SWCIV-######` reference to the corresponding existing fixture person key. It updates those existing canonical person profiles with sourced profile-history events, preflights all candidate names against the global SW-UNS exact/near-duplicate registry, and reserves each canonical name before linking the person to the allocation's BP02 address. It does not create additional people or alter the separate 500-person police-subset cohort.

The idempotent repeat path now checks the full 9,000-row identity crosswalk, exact person names and source references, distinct people and dwelling units, current permanent residences against active BP02 addresses, usual-resident status, active canonical name reservations, and preservation of all 500 police-subset people. The integrated workflow invokes the materialiser twice so the second invocation exercises these checks rather than treating matching row counts as sufficient evidence.

The latest integrated disposable run is [46048619576](https://github.com/Joshuaogri/saltwater/actions/runs/46048619576); its Python regression job passed, while the PostgreSQL job is still building the BP02 operational geography package before it can reach the resident materialisation steps. The BP03 Gemini review is running in [46048619487](https://github.com/Joshuaogri/saltwater/actions/runs/46048619487). An earlier Gemini attempt ended with the API's `RESOURCE_EXHAUSTED` capacity response and produced no review report; the current attempt has not yet produced a report. No production Neon data has been written, and no BP03 residence-materialisation pass is claimed yet.

## BP03 focused opening identity registry acceptance — passed (2026-11-27)

The dedicated disposable PostgreSQL workflow [46060309607](https://github.com/Joshuaogri/saltwater/actions/runs/46060309607) passed both the 500-person police and 9,000-person civilian SW-UNS identity acceptance tests on commit `04ae2929afd8c60ae332251399f8e2e1e01521f5`. The civilian test verified the source manifest, unique normalized candidate names, no normalized-name overlap with the police cohort, set-based authoritative registry preflight, canonical reservation counts and transaction rollback. The duplicate-name negative case was rejected as expected. This is focused disposable identity evidence only: it does not prove resident-to-dwelling materialisation, and it did not write production Neon.

The follow-up trigger correction is committed on `main` as [d1ea709](https://github.com/Joshuaogri/saltwater/commit/d1ea7093d611c2bf8df85eccc90fc4f0b10a27bd), ensuring registry SQL and materialiser changes trigger the BP03 identity workflow. Its rerun [46060745398](https://github.com/Joshuaogri/saltwater/actions/runs/46060745398) also passed on that commit: all 500 police and all 9,000 civilian identity tests succeeded. The integrated SW-DB-001 residence materialisation and replay proof remains pending.
