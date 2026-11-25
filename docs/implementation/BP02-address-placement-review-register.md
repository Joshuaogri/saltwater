# BP-02 address placement review register

**Date:** 2026-11-25  
**Status:** Implemented; deterministic tests pending CI execution  
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
- Building-access evidence resolves the source road for 384 addresses; 36 properties have no building on the property site. Those 36 are classified separately and are not automatically treated as incorrect addresses.

The P1 queue therefore contains five address/frontage exceptions. The other 415 have coherent parcel-frontage source context, while building presence/access remains a separate review dimension.

## Verification

The dedicated BP04 player/police/geography workflow runs the new unit suite and emits the expanded reconciliation report. The review register is an audit aid only. It does not constitute BP-02 operational geography approval, canonical address promotion, Neon permission provisioning or BP04 full acceptance.