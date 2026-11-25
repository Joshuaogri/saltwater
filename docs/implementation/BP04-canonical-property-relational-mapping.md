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
