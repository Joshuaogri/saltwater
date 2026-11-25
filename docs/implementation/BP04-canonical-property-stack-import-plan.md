# BP04 canonical property-stack import package — design and benchmark plan

**Status:** design stage; no canonical property import has been run.
**Target repository:** `Joshuaogri/saltwater`, `main` only.
**Authoritative database:** Neon PostgreSQL project `misty-breeze-20463094`, branch `br-bitter-rain-bdz9ddid`, database `neondb`.
**Safety:** production Neon remains read-only until the user separately approves a measured schema/import operation.

## 1. Verified source estate

The expanded property stack is persisted on `main` as 14 deterministic gzip datasets under `data/property/` and `data/business/`. Their combined GitHub blob size is 23,023,562 bytes (21.96 MiB). The canonical physical estate contains 420 property sites, 1,474 buildings, 27,730 premises, 180,733 units, 110,920 named rooms and 2,984 access points/routes. The source stack includes business registry and weekly operations, tenure/occupancy, utilities/building systems, maintenance, security, valuation/tax/insurance, development control, lifecycle/title, rights/boundaries, insurance exposure, facilities operations and the global estate audit.

These compressed repository sizes are not a PostgreSQL storage estimate. JSONB tuple overhead, indexes, TOAST, row headers, WAL and database metadata must be measured independently.

## 2. Existing database code is not the canonical importer

The current BP04-01/BP04-02 SQL proposals and BP04-03 Stage E physical-asset importer are explicitly disposable-PostgreSQL acceptance assets. The Stage E importer rejects databases other than `saltwater_test`, imports candidate assets/profiles, and intentionally does not create operational addresses, operational access points, ownership, tenancy, occupancy or business assignments. It must not be repurposed as the canonical property-world importer.

Production Neon currently contains only the five foundation tables in `sw_core` and `sw_ops`. There is no canonical property-stack schema or approved property seed importer deployed.

## 3. Package contract

The import package must be reproducible from the exact compressed GitHub snapshots at a pinned `main` commit. It must contain:

- A package manifest identifying the source commit, generator/schema versions, canonical estate counts, source paths, source byte sizes and SHA-256 digests.
- Lossless source datasets or deterministic record streams derived from them; no generated record may be silently omitted.
- Stable source entity identifiers preserved verbatim in every record.
- Dataset and collection provenance on every extracted record.
- Explicit source-to-target mapping metadata for every register.
- A deterministic package digest and an idempotency key.
- A validation report covering record counts, uniqueness, required fields, parent references and cross-register reconciliation.

Do not re-encode all data as one opaque JSONB blob. The production target must use typed, domain-specific relational tables with stable unique constraints and foreign keys where the source semantics support them. Preserve uncertain or unverified relationships as such; do not promote geometric candidates, estimates, or inferred legal rights into operational facts.

## 4. Required dependency order

1. Canonical property, building, premises, unit, room, site-feature and access-point identities.
2. Building components, spatial/access route lineage and physical hierarchy relationships.
3. Property ownership and property-management interests.
4. Business registry, establishments, business-to-premises/unit links and occupancy agreements.
5. Utility providers, property connections, accounts, meters, building systems and equipment.
6. Maintenance plans, inspections, defects, work requests, work orders and materials.
7. Security doors, locks, access zones, business access groups and permissions.
8. Condition, valuation, risk, insurance exposure and assessed property tax.
9. Development permissions, building control, completion/safe-use and lawful-use records.
10. Title, lifecycle, transaction, easement, boundary and rights evidence.
11. Insurance claim-process templates and facilities-management operating schedules.
12. Global estate audit and final cross-register reconciliation.

A package can retain all registers in one immutable release, while the loader applies dependency order inside a single transaction or in restartable, checksummed batches.

## 5. Disposable PostgreSQL benchmark

The benchmark must use an isolated PostgreSQL 16 instance/container, never the production Neon branch. It must:

- Apply the exact candidate schema and importer source from the repository.
- Load the exact package generated from the pinned source commit.
- Measure `pg_database_size` before and after.
- Measure table, index and TOAST sizes separately.
- Record row counts, insert duration, validation duration, peak process memory and package compressed/uncompressed sizes.
- Verify all source record counts and cross-register references after load.
- Test a second import of the same package for idempotency (zero duplicate rows and no material growth).
- Test rollback on an intentionally invalid reference.
- Produce a machine-readable benchmark manifest and human-readable summary.

The final estimate for Neon must include a measured range and explicit assumptions for production indexes, constraints and expected operational metadata. It must not use gzip file size as a proxy for database size.

## 6. Production gate

No production migration, table creation, seed insert, upload or bulk write is authorised by this design document. Before any production operation, report:

- Current live Neon database size and user-relation size.
- Exact source commit and package digest.
- Compressed and uncompressed package sizes.
- Disposable benchmark's measured total, table, index and TOAST growth.
- Projected incremental and total Neon size, with range and assumptions.
- The exact migration/import operations to be run.

Wait for the user's explicit approval before applying any schema or data change to production Neon. Keep the GitHub source and README synchronized with the measured outcome.


## Phase 2 — building services and utilities typed mapping

The first additional operational register is now mapped through `db/proposals/0014_bp04_building_services_utilities.sql` and `runtime/bp04_property_stack_importer.py`. It covers all eight source collections in `SW-BUILDING-SERVICES-V1`, totaling 426,399 records:

- `building_systems` → `sw_property.building_system`
- `utility_connections` → `sw_property.utility_connection`
- `utility_providers` → `sw_property.utility_provider_profile`
- `utility_accounts` → `sw_property.utility_account`
- `meters` → `sw_property.meter`
- `equipment_assets` → `sw_property.equipment_asset`
- `system_inspections` → `sw_property.system_inspection`
- `business_utility_responsibilities` → `sw_property.business_utility_responsibility`

The mapping uses typed numeric, integer, bigint, boolean and text fields; primary IDs remain source IDs. Foreign keys connect services to the canonical property/building/unit/organisation/business/occupancy registers. Utility accounts and meters reference their upstream connection/account; equipment and inspections reference their building system. The original compressed source remains archived exactly once, not copied as per-row JSONB.

Source boolean flags in this dataset are encoded as 0/1 values, so the importer normalizes them to PostgreSQL booleans. The acceptance check now expects 28 tables across phases 1 and 2. The disposable benchmark run is [45635002711](https://github.com/Joshuaogri/saltwater/actions/runs/45635002711); the import/reconciliation and repeat-import/storage results remain pending final verification. No production Neon changes.
