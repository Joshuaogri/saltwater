# BP-02 address placement review register

**Date:** 2026-11-25  
**Status:** IMPLEMENTED AND TESTED — dedicated GitHub Actions run 45688271976 passed  
**Scope:** Read-only GitHub source and disposable CI validation. No Neon writes.

## Purpose

The BP04-to-BP02 reconciliation now produces a deterministic 420-record review queue from the stable SWP/SWA design identity register and the building-access road reconciliation. It consolidates the original address road, parcel frontage candidate roads, building-access candidate roads, stable design IDs and review priority without changing source facts.

## Review classification

- **P1 — ROAD_REFERENCE_CONFLICT:** source address road differs from the parcel's geometric frontage-road candidate set.
- **P1 — NO_PARCEL_FRONTAGE_EVIDENCE:** the parcel has no geometric frontage-road candidate.
- **P2 — NO_BUILDING_ON_PROPERTY_SITE:** the property site has no candidate building; this is not automatically an address defect.
- **P2 — BUILDING_ACCESS_ROAD_REVIEW:** building-access road evidence exists but does not resolve to the source road.
- **P3 — SOURCE_CONTEXT_COHERENT_CANDIDATE:** source road agrees with available parcel-frontage and building-access candidate evidence.

The register preserves the source road even where a single alternative road is proposed. It never substitutes the alternative, creates a postal number, infers a constructed entrance, or upgrades geometric contact to legal or operational access.

## Fail-closed invariants

- Exactly one review record per source address.
- Every source address resolves to one stable design parcel identity.
- Every review record has a corresponding building-access reconciliation record.
- Duplicate/missing parcel, address or access evidence causes an error.
- Every record remains non-operational and unapproved.
- The output explicitly reports zero operational approvals and no database write.

## Current interpretation

The current source reconciliation baseline has 420 addresses:
- 415 source-road/frontage candidate matches.
- 3 source-road/frontage conflicts, each with a single alternative candidate retained for review.
- 2 addresses with no parcel frontage candidate.
- Building-access evidence covers 1,474 building candidates and 2,948 building-boundary access candidates. It resolves a source-road match for 384/420 property sites with building candidates; 36 sites have no generated building candidates and are classified separately.
- The three frontage-road conflicts occur on sites with no generated building candidates. Their single alternative frontage candidates are preserved for review: `SWR-H17` for two addresses and `SWR-H01` for one.
- The two parcels without boundary-frontage candidates do have building-access road-reserve proximity candidates matching their source roads: `SWR-B2` and `SWR-B1`. Both are `POINT_CONTACT_ONLY`, so they do not establish a driveway, traversable route or legal/operational access.
- The review queue contains 5 P1 records (3 road-reference conflicts and 2 no-frontage cases), 33 P2 records (no-building observations not already classified P1), and 382 P3 source-context-coherent candidates. The 36 no-building sites include the three P1 road conflicts.

The 415 direct parcel-frontage road matches remain coherent. Building presence and access evidence are tracked independently; the two no-frontage cases have separate proximity-only building access candidates.

## Verification

The dedicated BP04 player/police/geography workflow passed in [run 45688271976](https://github.com/Joshuaogri/saltwater/actions/runs/45688271976): 120 tests passed, and the complete 420-address reconciliation plus review-register generation succeeded. The review register is an audit aid only. It does not constitute BP-02 operational geography approval, canonical address promotion, Neon permission provisioning or BP04 full acceptance.
## Geometry-based disposition of the five P1 exceptions

The five exceptions were cross-checked against the actual SW-GEO-V1 road IDs, road classes, parcel frontage candidates and building-access candidate types:

| Source address | Source road | Geometry candidate | Disposition |
|---|---|---|---|
| `SWADDR-BPCSWD03N301701` | Dock Street (`SWR-V16`) | North Coast Road (`SWR-H17`) | Unique parcel frontage candidate; no candidate building, so source address is not corrected |
| `SWADDR-BPCSWD03N301801` | Ropewalk Road (`SWR-V17`) | North Coast Road (`SWR-H17`) | Unique parcel frontage candidate; no candidate building, so source address is not corrected |
| `SWADDR-BPCSWD05N100201` | West Coast Road (`SWR-V01`) | South Coast Road (`SWR-H01`) | Unique parcel frontage candidate; no candidate building, so source address is not corrected |
| `SWADDR-BPCSWD04N100402` | Customs Bridge (`SWR-B2`) | Point-contact bridge-reserve proximity only | Not street frontage; requires an addressable-street connection/design resolution |
| `SWADDR-BPCSWD08N101802` | Harbour Bridge (`SWR-B1`) | Point-contact bridge-reserve proximity only | Not street frontage; requires an addressable-street connection/design resolution |

The first three are resolved to a unique geometric frontage candidate, not to a final address. The last two cannot be promoted as bridge-frontage addresses. All five original road references are retained. No canonical address or operational access point is approved.

## Consolidated BP-02 audit

`runtime/bp02_full_acceptance_audit.py` consolidates the existing independent geometry audits for city/neighbourhood/road topology, parcel polygons/frontages/adjacency, property/building/access-point hierarchy, connector topology and route-corridor candidates, then adds the BP04 address/property reconciliation and exception dispositions. CI runs the audit and publishes a JSON evidence artifact. Structural pass and operational release are separate outcomes. The operational gate remains blocked while SW-GEO-V1 is unapproved, canonical addresses are unmaterialised and no operational access points are approved.

See `runtime/bp02_address_frontage_exception_resolution.py`, `runtime/bp02_full_acceptance_audit.py`, and `.github/workflows/bp02-full-acceptance-audit.yml`.