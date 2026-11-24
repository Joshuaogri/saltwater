# Saltwater master map — SW-GEO-V1

**Status:** first detailed planning-grade map and connected road-graph baseline  
**Coordinate system:** `SW-LOCAL-01`, fictional metres, X east / Y north, origin south-west, extent 12,000 × 9,000 m  
**Source data:** `data/geography/saltwater-geography-v1.json`  
**Map sheet:** `docs/maps/saltwater-master-map-v1.svg`

## Contents

The vector map sheet shows the city-state outline, administrative districts and neighbourhoods, the eastern sheltered harbour, central-western ridge, Southworks constructed freight basin, major civic/transport/port/health landmarks, road hierarchy, two harbour bridges, coordinate grid, north arrow, scale bar and legend.

The data file contains stable IDs and geometry for the city-state boundary, all 8 districts and 24 neighbourhoods, water and terrain features, 18 landmarks, 42 named roads, 367 junction nodes, 685 road/bridge segments and 5 named routes. The road graph is represented explicitly through node references and segment endpoints; route records contain ordered node and segment references.

## Road classes and route semantics

- `primary_arterial`: principal city movement corridors.
- `orbital_distributor`: the central orbital distributor.
- `district_connector`: district-level connectors.
- `local_street`: local street grid.
- `bridge`: named harbour crossing, represented as a water-crossing segment.

The baseline is two-way. Modes listed on segments are baseline permitted modes, not a claim that every vehicle type is suitable for every segment. No calibrated speed, travel time, traffic, live closure, weight/height restriction, road condition or surface has been invented. The two harbour bridges are explicit graph links. The graph is one connected component.

## Geometry and validation

- Districts and neighbourhoods use polygon geometry in the adopted local grid.
- Roads are split into routable segments between stable junction nodes.
- Segment lengths are derived from the fictional grid coordinates.
- The dataset embeds structural validation counts and checks.
- The generation-time checks confirmed: 8 districts; 24 neighbourhoods; 367 nodes; 685 segments; 42 named roads; 5 route definitions; all segment endpoints resolve; all nodes have incident edges; all segments are listed by their parent road; and the graph has one connected component.

These checks validate graph structure only. Full geometry QA, route-profile acceptance, dispatch/patrol workflow tests and manual cartographic review remain necessary before treating the map as a released operational authority.

## Deliberate exclusions

This first baseline does not yet contain a parcel fabric, building footprints, property records, canonical numbered addresses, building entrances, complete footpath network, rail geometry, ferry service routes/timetables, public transport schedules, speed/ETA calibration, live traffic or closure overlays. These must be added as versioned layers without changing the fixed 8-district/24-neighbourhood canon.

## Authority and safe use

SW-GEO-V1 is a committed source-data baseline for continued BP-02 implementation. It is fictional planning geometry, not survey-grade. It does not authorize a Neon migration, seed or production write. Do not infer missing access or speed attributes. Future corrections must create a new geography version and preserve the history of prior spatial references.


## Approved canonical-name corrections — 2026-11-24

The user approved two neighbourhood-only renames to resolve global canonical-name collisions while preserving all entity IDs:

- `SW-D01-N1`: **Westgate** → **Westgate Gardens**. District `SW-D01` remains **Westgate**.
- `SW-D03-N2`: **Government Square** → **Civic Terrace**. Landmark `SW-POI-002` remains **Government Square**.

The source JSON and SVG labels reflect these approved names. The SW-GEO-V1 dataset remains `DESIGN_BASELINE_NOT_YET_USER_APPROVED_FOR_OPERATIONAL_SEED`; no import or Neon write was performed. The 100 unresolved source-to-spatial-ID mappings remain an independent blocker.
