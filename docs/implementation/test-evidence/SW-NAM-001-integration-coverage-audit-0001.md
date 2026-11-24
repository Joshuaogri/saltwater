# SW-NAM-001 — Domain integration coverage audit 0001

**Audit date:** 2026-11-24  
**Repository:** `Joshuaogri/saltwater`  
**Branch:** `main`  
**Audit purpose:** Establish which existing domain records are actually protected by the universal naming registry, and identify dependencies that cannot yet be integrated without inventing missing domain schemas.  
**Production Neon:** Not connected or modified.

## 1. Executive result

The shared registry is implemented and its core disposable PostgreSQL acceptance has passed. The current proposal 0009 and runtime adapter enforce naming for two existing authoritative entity families:

- **Geography:** `sw_geo.entity` identity and append-only `sw_geo.version.name`.
- **People:** `sw_people.person` identity and canonical full name assembled from given, middle and family name fields.

The registry's SQL guard rejects unsupported entity types rather than accepting unvalidated references. The PostgreSQL adapter is a generic, parameterized caller of the controlled registry functions, but this does not mean every domain has an adapter or authoritative table.

**SW-NAM-001 is therefore core-verified, not universally integrated across all 44 divisions.** The two supported families are connected. BP-04 business/property/organisation records and independent police/operational named entities remain NOT CONNECTED because the authoritative entity schemas are not present in the current proposal sequence.

## 2. Schema inventory performed

The audit inspected all SQL proposals currently committed under `db/proposals/` through 0009 and extracted their declared tables.

| Proposal | Relevant tables | Naming status |
|---|---|---|
| 0002 runtime/city/population | `sw_geo.entity`, `sw_geo.version`, `sw_people.person`, person/profile/population/residence records | Geography and person canonical names are integrated by proposal 0009 triggers |
| 0003 actor/session/authorization | `sw_auth.*` principal, session, role, grant and audit records | No independently named domain entity; not a naming adapter |
| 0004 recruit entry | `sw_player.profile`, `sw_police.recruit_intake`, `personnel`, supervisor authorisation, career episode and lifecycle event | Personnel links to the canonical person; no separate officer-name authority. Police unit/vehicle/facility schemas are absent |
| 0005 player identity activation | `sw_player.identity_binding` | Identity binding references a player/person context; not an independent name-owning entity |
| 0006 BP-37 scheduling | `sw_runtime.schedule` | Schedule identity is operational metadata; no named domain entity adapter |
| 0007 BP-35 dispatch | `sw_runtime.event_work`, prerequisites and attempts | Work IDs/event references are not independently named entities |
| 0008 BP-39 recovery | checkpoint manifest and event-claim recovery | Recovery records are IDs/provenance, not independently named entities |
| 0009 universal naming | `sw_names.generation_batch`, `name_reservation`, `name_event` | Shared naming authority; supported owners are explicitly whitelisted as GEOGRAPHY and PERSON |

The current proposal sequence contains no authoritative BP-04 business, organisation, property, building or premises tables. It also contains no independent police unit, vehicle, equipment or facility identity tables. No such schema has been fabricated to make the naming package appear complete.

## 3. Verified enforcement paths

### Geography

- `sw_geo.entity` owns stable `spatial_id` and `entity_code`.
- `sw_geo.version` owns effective-dated display names and is append-only.
- Proposal 0009's `geography_name_registry_sync` trigger reserves the canonical name when a version is inserted.
- The reservation guard verifies that the geography identity exists.
- The only duplicate canonical namespace exception is the exact approved Saltwater sovereign-root / playable-city pair, using separate stable root identities.
- Direct DML against `sw_names` reservation/history tables is revoked from PUBLIC and game roles; writes use controlled functions.

### People

- `sw_people.person` owns the stable `person_id` and source name fields.
- Proposal 0009's `person_name_registry_sync` trigger reserves the complete canonical name on insert or name-field update.
- The trigger requires given and family names and a committed event reference.
- Person profile history remains append-only and is preserved independently of the naming reservation history.
- The reservation guard verifies the referenced person exists.
- Preferred/alias forms are available through the controlled naming functions; no second person identity is introduced.

### Unsupported entity types

Proposal 0009's reservation guard deliberately raises an error for any entity type other than the explicit GEOGRAPHY and PERSON adapters. This is the required fail-closed behavior. A generic string value cannot create an orphaned or unvalidated business, property, unit or vehicle reference.

## 4. Geography canon import remains blocked

The dry-run SW-GEO-V1 inventory contains 102 candidates: two Saltwater roots, eight districts, 24 neighbourhoods, 42 roads, five routes and 21 named features.

The previously approved source-name corrections are present in the repository:
- `SW-D01-N1`: **Westgate Gardens**, while district `SW-D01` remains **Westgate**.
- `SW-D03-N2`: **Civic Terrace**, while landmark `SW-POI-002` remains **Government Square**.

A deterministic mapping candidate is now committed at [saltwater-geography-v1-identity-map.json](../../../data/geography/saltwater-geography-v1-identity-map.json). It maps all 100 non-root source IDs to the same stable `entity_code`, records the typed geography kind and parent source identity, and deliberately leaves every generated integer `spatial_id` NULL. The 100 integer spatial-ID mappings are now materialised and checked in the disposable acceptance fixture [geography_identity_map_acceptance.sql](../../../tests/pkg001/geography_identity_map_acceptance.sql). The fixture inserts the 100 typed identities and their first versions, captures the generated `spatial_id` values through a final result set, validates parent links and confirms that the geography trigger activates all 100 naming reservations. Its dedicated workflow step passed again in [run 45441551968](https://github.com/Joshuaogri/saltwater/actions/runs/45441551968), including the explicit guard requiring database `saltwater_test` on PostgreSQL 16. The workflow's remaining full regression, 10,000-person fixture, access-boundary and backup/restore jobs were still running when this audit update was prepared; final workflow conclusion and measured storage values will be appended after completion. The map source is not approved for operational seeding. Therefore:
- no geography canon import is performed;
- no production names are reserved;
- no generated geography names are accepted as canon;
- no source IDs or geometry are rewritten to conceal the mapping gap.

The correct next geography dependency is a deterministic, reviewable source-ID-to-stable-spatial-identity mapping and its disposable acceptance test, followed by the separate map/canon approval required for operational import.

## 5. Remaining integration work

| Domain | Owner | Current status | Required dependency |
|---|---|---|---|
| Geography names | BP-02 | Registry trigger connected; canon import blocked | Resolve all 100 stable spatial-ID mappings and operational map approval |
| Person names | BP-03 | Registry trigger connected; core tests passed | Preserve integration in future person lifecycle/profile changes |
| Business/trading names | BP-04 | NOT CONNECTED | Authoritative BP-04 business schema and ownership model |
| Property/building/premises names | BP-04 | NOT CONNECTED | Authoritative property/building schema and typed relationships |
| Organisation names | BP-04 / relevant domain owner | NOT CONNECTED | Authoritative organisation identity schema |
| Police unit/facility/vehicle/equipment labels | BP-05–BP-09 and resource owners | NOT CONNECTED | Domain-owned stable entity schemas and typed adapters |
| Operational call signs | BP-05–BP-12 | NOT CONNECTED | Unit/vehicle identity, effective-time and uniqueness-window semantics |

These are dependency gaps, not permission to create substitute registries. Each adapter must use the shared reservation service, preserve the domain's stable ID, validate the typed owner, and include direct-write bypass tests before being marked connected.

## 6. Acceptance status and boundaries

**Passed:** core disposable registry schema, normalisation, uniqueness, Saltwater exception, ambiguity, historical-name protection, person/geography integration, concurrency, idempotency, rollback, generator manifest linkage, access controls and backup/restore. See [SW-NAM-001 run 0001 evidence](SW-NAM-001-run-0001.md) and follow-up workflow runs recorded there.

**Not claimed:** full 44-division integration; BP-04 or operational entity adapters; operational geography canon import; Neon production migration; Neon name reservation or seed; public runtime deployment.

No Neon production operation, upload, seed, migration or credential change occurred during this audit.
