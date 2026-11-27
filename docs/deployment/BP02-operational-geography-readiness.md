# BP-02 Operational Geography Deployment — Readiness Assessment

**Status:** PREPARATION — production deployment not yet authorised  
**Assessment date:** 2026-11-27  
**Target:** Production Neon `neondb`, PostgreSQL 18.7  
**Git branch:** `main` only  
**Existing release:** `SW-GEO-V1` source archive, archive-only release completed 2026-11-27

## 1. Production baseline — read-only verification

The production database was inspected without writes.

| Measure | Verified value |
|---|---:|
| Database | `neondb` |
| PostgreSQL | 18.7 |
| Current database size | **9,961,472 bytes** |
| User tables | 7 |
| Extensions | `plpgsql` only |
| Global migration ledger | Versions 1 and 2 |
| BP02 independent migration ledger | Version 1 |
| `sw_geo.source_archive` | 1 immutable `SW-GEO-V1` row |
| Operational geography tables | None |

The seven user tables are `sw_core.event_type`, `sw_core.simulation_event`, `sw_core.world_config`, `sw_geo.bp02_schema_migration`, `sw_geo.source_archive`, `sw_ops.schema_migration` and `sw_ops.storage_operation`.

The existing archive contains two source files: 596,267 uncompressed bytes, 25,689 compressed bytes, SHA-256 `6b46d62a944334a1853bc7190e33476bb06adc835e433d5592d6b0ee4c700d0c`. It is an immutable source archive, not operational geography.

## 2. Geography data already present in GitHub

The current `SW-GEO-V1` source dataset contains:

| Layer | Count | Current evidence |
|---|---:|---|
| Districts | 8 | Canonical source geometry |
| Neighbourhoods | 24 | Canonical source geometry |
| Stable source entities | 100 | 100 resolved; 0 unresolved |
| Named roads | 42 | Stable road identities |
| Junction nodes | 367 | Unique node IDs |
| Road/bridge segments | 685 | All endpoints and parent-road references resolve |
| Named routes | 5 | Ordered node/segment references resolve |
| Connected road graph | 1 component | Structural validation passed |
| Landmarks | 18 | Stable source identities |
| Geography zones | 3 | Stable source identities |

The graph baseline is two-way. Segment modes and access values are source attributes; no speed, ETA, live traffic, closure, vehicle restriction or road-condition facts are inferred.

## 3. Parcel, address and access-point layer — candidate status

The property/geography pipeline has generated useful design data, but its own manifests and acceptance reports explicitly keep it non-operational.

| Layer | Count | Current status |
|---|---:|---|
| Property/parcel candidate sites | 420 | Geometry-derived candidates, not approved cadastral parcels |
| Source addresses | 420 | Stable design identities; not operationally verified |
| Address review queue | 420 | 5 P1, 33 P2, 382 P3 |
| Candidate buildings | 384 | Generated design candidates |
| Building-boundary access-location candidates | 768 | Unreviewed geometric candidates |
| Persistent connector candidates | 768 | Unreviewed geometric lines |
| Point-contact-only road-reserve connections | 4 | Not frontage or usable access |
| Operational canonical addresses created | 0 | Confirmed by existing acceptance evidence |
| Operational access points created | 0 | Confirmed by existing acceptance evidence |

All 420 addresses remain marked `operational_address_approved=false`. Even the 382 P3 records mean only that available source and geometric context is coherent; P3 is not operational approval. The five P1 exceptions and 33 P2 records remain review items. The 768 access points/connectors do not prove doors, constructed paths, public/legal access, traversability or emergency egress.

## 4. Source-authority conflict that must be reconciled

The source JSON labels `SW-GEO-V1` as `APPROVED_FOR_OPERATIONAL_USE`, and BP-02 is marked VERIFIED. However, related authority records still say:

- `saltwater-geography-v1-identity-map.json`: `operational_seed_approved=false`;
- BP04-03 source spatial reconciliation: `operational_approval=false`;
- BP02 map register: `DESIGN_BASELINE_NOT_YET_USER_APPROVED_FOR_OPERATIONAL_SEED`;
- parcel/address identity and address review outputs: operational approval false;
- BP04-03 approval package: production authority NONE.

These statements are not equivalent. BP-02 design/gameplay acceptance and the source archive release do not, by themselves, authorize production seeding. The operational release manifest must explicitly distinguish the approved road-network layer from parcel/address/access candidates. No source status is silently changed in this preparation.

## 5. Existing storage measurements — interpretation

Two prior disposable measurements are relevant but must not be confused with a geography-only production estimate:

1. **BP04-03 Stage B:** an earlier 396-parcel candidate import added 1,187,840 bytes in disposable PostgreSQL 16. This predates the later 420-site Stage E dataset and is not a current full-geography estimate.
2. **BP04-03 Stage E:** the full physical-asset candidate import added 130,973,696 bytes in disposable PostgreSQL 16. That import included 420 property sites, 384 buildings, 1,327 premises, 15,199 units, 768 access-location candidates, 18,098 profiles, 181,915 typed detail records, 1,572 geometry candidates and connector records. It is a broad BP04 physical-inventory benchmark, not the expected cost of the BP02 road/parcel/address/access geography layer.

**No defensible exact production storage estimate exists yet for the requested operational geography package.** The road graph has not been benchmarked in the intended compact production schema, and the candidate parcel/address/access data must not be mislabelled as operational. A fresh PostgreSQL 18.7 benchmark must separately measure schema growth, road-network rows, parcel candidates, address candidates and access-point candidates, plus total database growth and repeat-import growth.

## 6. Deployment design required before production

The implementation must use a separate BP02 domain migration/import stream. It must not apply the disposable-only PKG-001 runtime/population proposal, the BP04 candidate proposals, or unrelated global migrations as a shortcut.

Required sequence:

1. Reconcile the source-authority flags and publish a versioned release manifest that identifies operational road-network records separately from non-operational parcel/address/access candidates.
2. Define a compact BP02-owned schema for stable geography identities, area geometry, road nodes, roads, segments and routes. Keep candidate parcel, address and access-point records explicitly typed and status-labelled; do not activate them by implication.
3. Build a deterministic importer using stable source IDs/entity codes, source checksums and database-generated surrogate IDs where required. Do not hard-code disposable IDs.
4. Run Python regression tests and a fresh PostgreSQL 18.7 disposable end-to-end import. Test referential integrity, connectedness, bridge links, exact counts, candidate-status preservation, checksum mismatch rejection, immutable history and zero-growth repeat import.
5. Measure each layer independently and together. Record baseline, schema-only growth, each data-layer delta, total delta, projected production total and exact package/source hashes.
6. Prepare a manual-only production workflow restricted to `main`. It must check the live database name/version, exact expected baseline, recovery-point reference, source hashes and expected measured delta before any write. It must leave the global migration ledger unchanged unless a separately approved migration is explicitly required.
7. Present the completed test evidence and exact storage figures for user approval. Only after explicit approval may the production workflow be run.

## 7. Production write boundary

**No operational-geography production write was performed during this assessment.** Production remains at 9,961,472 bytes. The BP02 archive row and migration ledger remain unchanged. The recovery branch `br-gentle-moon-bdtc0y32` must remain preserved.

The existing archive-only approval does not extend to operational geography. A separate explicit approval is required after the benchmark and acceptance package are complete.
