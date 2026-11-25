# BP04 canonical property import — relational mapping, phase 1

**Status:** candidate schema committed for disposable PostgreSQL 16 validation only. It is not a production migration and must never be applied to Neon without explicit user approval.

## Design rules

- Preserve canonical Saltwater source IDs verbatim as primary keys. No surrogate-key remapping is required for source identity.
- Keep all records in typed domain tables with explicit foreign keys and useful query indexes. Each row also retains its original source object in `source_record` JSONB so columnar reconstruction, generator-specific fields and future schema evolution remain lossless; JSONB is not the sole data model.
- Every imported row records its source dataset. The release ledger records the pinned Git commit, deterministic package digest, original compressed/uncompressed byte counts and exact record counts.
- Apply the package in one transaction with deferred foreign-key checks, in parent-first order. Deferred constraints permit cyclic references such as business ↔ primary establishment and property ↔ address while still enforcing integrity at commit.
- The property/person boundary is strict: no people, residents, staff, contractors-as-persons, credentials or population records are created by this import.
- Do not infer legal ownership, easements, survey boundaries or lawful access from geometry or physical route records. Preserve explicit uncertainty values in the source record.

## Dataset-to-table mapping

| Source dataset / collection | Relational destination | Identity and key relationships |
|---|---|---|
| `SW-PROPERTY-WORLD-V1.properties` | `property_site` | `property_id`; district/neighbourhood identifiers retained |
| `addresses` | `street_address` | `address_id`; one address per property site |
| `buildings` | `building` | `building_id` → property site |
| `premises` | `premises` | `premises_id` → property and building |
| `units` | `unit_space` | `unit_id` → property, building, premises |
| `access_points` | `access_point` | `access_point_id` → property and at most one building/premises/unit scope |
| `access_routes` | `access_route` | `route_id` → access point; road reference preserved |
| `site_features` | `site_feature` | `site_feature_id` → property |
| `building_components` | `building_component` | `component_id` → building |
| `premises_rooms` | `premises_room` | `room_id` → premises |
| `owner_organisations` | `organisation` | `organisation_id` |
| `ownership_interests` | `ownership_interest` | `ownership_interest_id` → property and owner organisation |
| `SW-BUSINESS-REGISTRY-V1.businesses` | `business` | `business_id`; parent group and primary establishment retained |
| `establishments` | `establishment` | `establishment_id` → business and physical location |
| `business_unit_links` | `business_unit_link` | `business_unit_link_id` → business, establishment, premises and unit |
| `SW-PROPERTY-TENURE-V1.organisations` | `organisation` | Upsert by stable `organisation_id`; preserve source provenance |
| `ownership_events`, `management_appointments` | Phase 2 typed registers | Separate event and appointment history tables; no flattening into current ownership |
| `agreements` | `occupancy_agreement` | `agreement_id` → property, unit, landlord, tenant, operator, establishment |
| `occupancies` | `occupancy` | `occupancy_id` → unit, business, establishment and agreement |
| `unit_occupancy_states` | Phase 2 typed register | Preserve vacant, residential-unassigned and business-occupied states without person creation |
| Remaining utility, maintenance, security, valuation, development, lifecycle, rights, claims and facilities collections | Phase 2 typed domain tables | One typed table per register; explicit FK only where the source establishes the relationship |

## Current phase 1 table inventory

The SQL proposal creates 17 domain tables plus a two-table immutable import-release ledger: organisation, property_site, street_address, building, premises, unit_space, access_point, access_route, site_feature, building_component, premises_room, ownership_interest, business, establishment, business_unit_link, occupancy_agreement and occupancy.

## Known integrity decisions

1. The primary business establishment pointer is deferred because the two source collections refer to each other. The transaction must load both before commit.
2. The property/address association is deferred for the same reason.
3. A physical access point may be scoped to a building, premises or unit, but not more than one of those levels. Property-only access remains valid.
4. A business unit can have only one current primary occupancy link. Historical links are retained with closed validity intervals.
5. An address is unique to a property site in this first canonical model. If source inspection shows a legitimate shared-address exception, represent that through a separate address-association table rather than weakening uniqueness silently.
6. A site may have no buildings; its site-level access points and routes remain valid.
7. All parent and cross-register checks are performed before package commit. Any missing parent, duplicate source ID, count mismatch or illegal multiple-current occupancy aborts the entire load.

## Next implementation slice

Build a deterministic importer that reads plain JSON and gzip columnar documents through `runtime.dataset_io`, expands each collection without changing values, constructs the release manifest, inserts parent and child records in deterministic batches, and runs source-to-table count plus cross-reference reconciliation. Then exercise the proposal and importer in the existing disposable PostgreSQL 16 CI service, including second-run idempotency, invalid-reference rollback and storage measurement. This remains separate from production Neon.

## Storage-efficient lossless archive design (supersedes per-row JSONB preservation)

The initial candidate `0012` stored each full source row in JSONB alongside typed columns. The disposable benchmark showed 453.5 MiB for the three-dataset package, so that duplication is not the selected import design.

The optimized candidate is `db/proposals/0013_bp04_compressed_source_archive.sql`. It stores each original gzip dataset exactly once in `sw_property.source_dataset_archive.compressed_payload` (bytea), keyed by its SHA-256. Every typed row retains its stable source primary key and `source_dataset`; the release manifest links the source file path, digest, compressed/uncompressed sizes and source collection counts. The compressed archive is the lossless source of record; typed tables are the indexed operational representation. This avoids repeating the full source object in every row while retaining exact recovery and provenance.

The importer inserts the archive before release-dataset rows, enforces the archive hash foreign key, and applies all typed rows in one transaction. On conflict it updates only when mapped relational values actually differ. Re-import of the same release is tested to leave database size unchanged.

### Verified disposable benchmark

Workflow run [45630476765](https://github.com/Joshuaogri/saltwater/actions/runs/45630476765) passed on PostgreSQL 16. It loaded 402,658 records across all 17 typed tables with zero cross-reference violations. The three gzip source archives total 10,934,275 bytes; the uncompressed JSON totals 196,604,988 bytes. Measured final disposable database size: 135,257,111 bytes (128.99 MiB). Repeat import left size unchanged at 135,257,111 bytes.

The 0013 schema and importer are still candidate/disposable-only. This benchmark covers property world, business registry and tenure only; all remaining property-domain registers must be added and benchmarked before the total property package can be sized. Production Neon remains untouched.


## Complete 14-dataset source inventory (2026-11-25)

The new read-only inventory implementation `runtime/bp04_source_inventory.py` was verified by GitHub Actions run [45633081533](https://github.com/Joshuaogri/saltwater/actions/runs/45633081533). All 14 compressed inputs passed structural validation:

| Source measure | Verified total |
|---|---:|
| Datasets | 14 |
| Columnar collections | 105 |
| Source records | 1,950,947 |
| Compressed source bytes | 23,023,562 (21.96 MiB) |
| Uncompressed source bytes | 559,420,873 (533.5 MiB) |

The inventory preserves each dataset's canonical metadata ID, source path, SHA-256, compressed and uncompressed byte counts, collection names, row counts, column names and candidate identity columns. It validates every row width against its collection's declared columns. The audit-only global-estate-capacity findings collection is included as evidence but is not automatically treated as operational property records.

The inventory exposed the actual canonical source ID `SW-PROPERTY-RIGHTS-AND-BOUNDARIES-V1` (the filename alias omits “AND”), and the global estate audit's canonical ID `SW-GLOBAL-ESTATE-CAPACITY-AUDIT-V1`. The implementation uses source metadata as authoritative.

This inventory is not a database import and does not imply that all 105 collections have typed relational mappings. The existing phase-one importer still relationally maps only property world, business registry and tenure. Next, map remaining operational collections into typed tables with explicit key/reference rules, while retaining each original gzip source exactly once in the compressed archive. Keep the global capacity audit as a validation/evidence source unless a specific operational need requires otherwise. Then run complete disposable PostgreSQL 16 reconciliation, idempotency, rollback and storage tests. No Neon production changes.
