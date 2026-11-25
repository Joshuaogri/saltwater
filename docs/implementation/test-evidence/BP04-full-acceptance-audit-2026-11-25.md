# BP04 full acceptance audit — 2026-11-25

**Result: NOT PASSED — BP04 is partially implemented and must not be marked COMPLETED.**

**Audit source:** `main` at `625a75612dd760a8de7ef1362df1b23f61b23db1`  
**Production release:** [GitHub Actions run 45675735246](https://github.com/Joshuaogri/saltwater/actions/runs/45675735246) — completed successfully  
**Latest disposable archive-only validation:** [run 45672436619](https://github.com/Joshuaogri/saltwater/actions/runs/45672436619) — completed successfully  
**Neon target:** project `misty-breeze-20463094`, production branch `br-still-cloud-bdvaw8u4`, database `neondb`.

This audit distinguishes successful delivery of the compressed BP04 source package from completion of every BP04 division acceptance criterion. The production deployment is successful; the complete division acceptance is not.

## 1. Verified production deployment

A read-only query against Neon on 2026-11-25 verified:

| Measure | Verified value |
|---|---:|
| BP04 production migrations | 0003–0012 (10 versions) |
| BP04 base tables | 92 |
| Archived source datasets | 14 |
| Source collections | 105 |
| Source records represented | 1,950,923 |
| Compressed source bytes | 29,434,820 (29.43 MB) |
| Uncompressed source bytes | 558,602,287 (558.60 MB) |
| Dataset ledger rows | 14 |
| Collection ledger rows | 105 |
| Dataset/collection mappings in archive-only state | 14 / 105 |
| Permanently materialised typed source rows | 0 |
| Current `pg_database_size` | 41,525,248 bytes (41.53 MB) |
| Pre-BP04 baseline | 9,306,112 bytes (9.31 MB) |
| Measured production growth | 32,219,136 bytes (32.22 MB) |

The production workflow passed both jobs and every deployment step: target/commit/package-digest verification, ordered migrations, archive-only import, production acceptance, repeat-import idempotency/storage stability and final measurements. The 14 original compressed archives are retained once. The zero typed-row count is intentional under the selected archive-only storage design.

The archive-only disposable workflow also passed on PostgreSQL 16 and 18. Its acceptance verifies 14 datasets, 105 collections, source counts, archive byte accounting, archive-only mapping states, zero typed rows and repeat-import stability.

## 2. Source-world coverage verified in GitHub

The committed property-world source and its generator tests cover a canonical fictional estate baseline of:

- 420 property sites and 420 generated address records;
- 1,474 buildings;
- 27,730 premises;
- 180,733 units;
- 110,920 named rooms;
- 2,984 access points and 2,984 access routes.

The source ledgers also account for:

- 10,000 business identities;
- 10,000 establishments;
- 10,000 business-to-unit links;
- 10,000 weekly business profiles;
- 70,000 daily operating schedules;
- 811 organisation records in the tenure source;
- ownership, management, occupancy, agreements, utilities, maintenance, security, valuation, lawful-use, lifecycle, title, rights, insurance and facilities-operation collections.

The property-world generator regression verifies unique IDs within entity types, property/building/premises/unit parent relationships, address references, ownership references, access-point/route matching, campus buildings and no person creation. These are meaningful source-generation checks, but they do not prove that every BP04 cross-register acceptance criterion is operationally available through the game.

## 3. Acceptance matrix

| Acceptance group | Result | Audit finding |
|---|---|---|
| A — business registry | PARTIAL | The 10,000-business, 10,000-establishment and operating-schedule source collections exist. The deployed archive acceptance verifies source counts, not the complete AC-A01–A07 identity-quality, duplicate, branch-count and population-interface invariants. |
| B — property and premises | PARTIAL / BLOCKED | The generator tests verify the source hierarchy and generated address/access relationships. BP04 addresses are not yet demonstrated as fully bound to BP-02's authoritative parcel/address identity and operational spatial references. The production source is archived, not query-indexed into the property tables. |
| C — ownership, tenancy and occupancy | PARTIAL | The source archives include ownership, management, 12,500 agreements and 10,000 occupancies. Production archive acceptance does not execute the full temporal, party-role, dispute, subletting and continuity checks in AC-C01–C07. |
| D — organisations and facilities | PARTIAL | Organisation and facility-related source collections exist. Full service-level acceptance for healthcare capability and public transport operator/route/timetable integration (AC-D06/D07) is not evidenced as a tested, playable interface. |
| E — staff, stock, supply and events | PARTIAL | Business profiles and schedules are present. The complete person/employment interfaces, stock reconciliation, causal disruption events and transactional rollback requirements in AC-E01–E07 are not verified end to end. |
| F — police, evidence and information boundaries | BLOCKED | No dedicated police-facing property/business enquiry adapter was found in the current runtime. The archive reader exposes generic dataset/collection loading; it does not itself provide authorised property lookup, role-filtered access-control disclosure or complete evidence-provenance workflows. BP-42/BP-23 remain required cross-division interfaces. |
| G — quality, scale and storage | PARTIAL | Archive integrity, source counts, storage measurement and repeat-import stability pass. The 10,000-business query-performance budget, complete duplicate/reconciliation suite, representative lookup benchmarks and full criterion-to-test traceability are not yet demonstrated. |

## 4. Concrete blockers to full acceptance

1. **Canonical geography binding:** reconcile each property/address reference with BP-02's authoritative parcel/address IDs and spatial identity. The lookup deliberately labels current references `source_geography_reference_only`; do not treat a generated address label as proof of a BP-02 canonical address.
2. **Gameplay lookup layer:** the bounded property/address/building/premises/unit/access-point/business/establishment lookup API is now implemented in `runtime/bp04_lookup.py`, documented in [BP04 gameplay lookup](../BP04-gameplay-lookup.md), and its synthetic contract tests passed on PostgreSQL 16 and 18 in [run 45678245109](https://github.com/Joshuaogri/saltwater/actions/runs/45678245109). The actual imported archive integration check is running in [run 45678573423](https://github.com/Joshuaogri/saltwater/actions/runs/45678573423). The lookup remains process-local and does not duplicate static rows in Neon. It is not yet wired into the player command dispatcher or an authorised police-facing adapter.
3. **Cross-register acceptance:** test uniqueness, parent/child references, temporal relationships, business-versus-establishment identity, 10,000-business quality, organisation/facility links and all 105 collection counts from the pinned source release.
4. **Police-facing access contract:** expose relevant property/business facts to police workflows through an authorised adapter, preserving provenance and uncertainty and respecting restricted keys, locks, layouts and sensitive records. Do not bypass BP-42 or evidence ownership.
5. **Operational interfaces and regression:** verify the applicable healthcare, transport, utility, business-schedule, lifecycle and disruption interfaces; add representative lookup-performance, failure/rollback and recovery tests.

## 5. Final decision

**BP04 production archive release: COMPLETED and VERIFIED.**  
**BP04 full division acceptance: NOT COMPLETED.**

Do not mark the entire BP04 division `COMPLETED` yet. The next bounded implementation tasks are BP-02 identity reconciliation, player/police integration of the lookup API, and their acceptance tests. This can be developed on GitHub `main` and tested on disposable PostgreSQL without any further Neon write.

No Neon writes were made during this audit.
