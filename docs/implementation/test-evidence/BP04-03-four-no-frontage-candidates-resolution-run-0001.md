# BP04-03 four no-frontage candidates — resolution evidence

**Status: resolved as road-reserve point-contact candidates, not frontage.**

The earlier building-access reconciliation identified four building-boundary candidates with no identified parcel frontage. These were retained as unresolved because the parcel geometries touch the road-reserve network only at a point, rather than along a frontage edge.

The resolution was implemented in the parcel dossier generator and the non-operational schema extension `db/proposals/0016_bp04_road_reserve_proximity_candidates.sql`. For parcels with no frontage edge, the generator now records a deterministic nearest road-reserve relationship candidate with:
- stable road-connection candidate ID;
- road and road-segment identity;
- parcel-boundary and road-reserve nearest points;
- measured distance to the road reserve;
- contact classification `POINT_CONTACT_ONLY` or `NEAREST_EDGE_PROXIMITY_NOT_FRONTAGE`;
- explicit unreviewed proximity-only status and source provenance.

The four prior exceptions are now linked to point-contact-only road-reserve candidates. They are **not reclassified as frontage**, and no driveway, entrance, gate, legal access, public access right, traversable path, vehicle access or emergency egress is asserted.

## Revalidation

- Direct connector workflow: [45516793015 — successful](https://github.com/Joshuaogri/saltwater/actions/runs/45516793015)
- Stage E disposable PostgreSQL: [45516793086 — successful](https://github.com/Joshuaogri/saltwater/actions/runs/45516793086)
- Connector regression tests: 6 passed.
- Building-access reconciliation tests: 7 passed.
- All building-boundary candidates: 768.
- Direct connector candidates tested: 768.
- Geometrically feasible, unreviewed candidates: 768.
- Blocked candidates: 0.
- Unlinked road-connection candidates: **0**.
- Point-contact-only road-reserve candidates: **4**.
- Missing parent/road-connection references: 0.
- Outside-parent-property connector geometries: 0.
- Origin-building, other-building and mapped-water crossings among feasible connectors: 0.
- Connector audit checks: 7/7 passed.

These are geometry-only design candidates. Their straight-line feasibility does not prove a physical or legally usable access route. The four point contacts remain distinctly typed and unreviewed.

No operational access points or canonical addresses were created. No Neon production write or activation occurred. The Stage E PostgreSQL run used a disposable database only.
