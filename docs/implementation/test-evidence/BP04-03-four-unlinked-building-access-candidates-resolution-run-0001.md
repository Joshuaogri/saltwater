# BP04-03 — Resolve the four building access candidates without parcel frontage

**Status:** Completed and validated  
**Latest main commit:** `00d7e781646b195553c1dc6afaf1e9d601c4bfbc`

## Root cause

Two parcel candidates touch the dissolved road reserve at a single point rather than along a measurable frontage edge:

| Parcel candidate | Building | Nearest road | Segment | Relationship |
|---|---|---|---|---|
| `BPC-SWD04N1-004-02` | `SWB-STR-BPCSWD04N100402-B01` | `SWR-B2` | `SWS-0685` | Point contact only |
| `BPC-SWD08N1-018-02` | `SWB-STR-BPCSWD08N101802-B01` | `SWR-B1` | `SWS-0684` | Point contact only |

The four building-boundary access-location candidates are A01 and A02 on each building. The previous generator left them without a road link because it required a linear frontage candidate. Treating the point contact as a conventional frontage would have been incorrect.

## Resolution

The parcel dossier generator now creates one separate `road_reserve_proximity_connection` candidate for each no-frontage parcel. The records include:
- Stable candidate ID and parcel lineage.
- Road ID and exact source road-segment ID.
- Parcel-boundary and road-reserve candidate coordinates.
- Measured parcel-to-road-reserve distance.
- `POINT_CONTACT_ONLY` classification.
- Explicit unreviewed status and source provenance.

The two proximity candidates are:
- `PAC-BPC-SWD04N1-004-02-PROX-SWS-0685`
- `PAC-BPC-SWD08N1-018-02-PROX-SWS-0684`

The Stage E asset generator now links each of the four building-boundary candidates to its nearest same-parcel road candidate. The links are labelled `NEAREST_ROAD_RESERVE_PROXIMITY_CANDIDATE`, not frontage links. They remain unreviewed proximity-only candidates.

## Validated results

| Measure | Result |
|---|---:|
| Parcel candidates | 420 |
| Genuine linear frontage candidates | 1,374 |
| Parcel access-location candidates | 1,376 |
| Separate point-contact proximity candidates | 2 |
| Building candidates | 384 |
| Building-boundary access candidates | 768 |
| Building candidates without a road-connection candidate | **0** |
| Building access candidates linked to point-contact candidates | 4 |
| Direct connector lines geometrically tested | 768 |
| Geometrically feasible, unreviewed connector lines | 768 |
| Blocked connector lines | 0 |
| Failed connector audit checks | 0 |

The 768 direct connector lines are feasible only under the geometric checks: each line is contained within its parent property and avoids mapped building interiors and mapped water. This does not prove a constructed path or a traversable route.

### Successful validation runs

- [Parcel dossier geometry QA — run 45516792963](https://github.com/Joshuaogri/saltwater/actions/runs/45516792963): 9 regression tests; 10/10 audit checks; 420 parcels; 1,374 frontage candidates; 1,376 access-location candidates.
- [Building access reconciliation — run 45516972156](https://github.com/Joshuaogri/saltwater/actions/runs/45516972156): 7 regression tests; 8/8 audit checks; 768 building-boundary candidates; 4 point-contact road-reserve candidates; zero unlinked candidates.
- [Direct connector feasibility — run 45516793015](https://github.com/Joshuaogri/saltwater/actions/runs/45516793015): 6 regression tests; 7/7 audit checks; 768 lines tested; 768 geometrically feasible; zero blocked; zero unlinked.
- [Stage B and Stage D disposable PostgreSQL — run 45517627917](https://github.com/Joshuaogri/saltwater/actions/runs/45517627917): all tests, schema acceptance, dossier import and repeat-import idempotency passed.
- [Stage E disposable PostgreSQL — run 45516793086](https://github.com/Joshuaogri/saltwater/actions/runs/45516793086): generator/importer tests, dossier and asset import, full acceptance, repeat-import idempotency, storage measurement and backup/restore all passed.

## Database and storage measurements

The new disposable-only proposal `db/proposals/0016_bp04_road_reserve_proximity_candidates.sql` extends the parcel access-location candidate table to distinguish frontage candidates from point-contact/nearest-edge proximity candidates. It does not promote either type to operational access.

- Proposal source: **2,586 bytes**.
- Disposable schema growth for proposal 0016: **24,576 bytes**.
- Dossier import growth: **1,933,312 bytes**.
- Dossier repeat import growth: **0 bytes**.
- Stage E physical asset import growth: **130,744,320 bytes**.
- Stage E repeat import growth: **0 bytes**.
- Stage E manifest SHA-256: `c4950c5b56d2996f3da56a89bd077a3213407491c5ca9c1a33e061b76adaa38b`.
- Stage E import: 18,098 identities, 18,098 profiles, 181,915 typed detail records, 1,572 geometry candidates, 420 candidate site links and 16,910 relationships.
- Stable source identity mappings: **100 resolved, 0 unresolved**.

## Restrictions preserved

No canonical addresses, operational spatial IDs, operational access points, driveways, entrances, access rights, emergency egress or actual traversable routes were invented. The point-contact records remain unreviewed geometric candidates.

No production Neon migration, seed or write was performed. The read-only Neon database-size check remained **9,306,112 bytes** (9.31 MB decimal; approximately 8.87 MiB), PostgreSQL 18.7.

## Continuing work

Keep the distinction between true frontage and point-contact road-reserve proximity in all future parcel, building, dispatch, patrol and routing work. Any later access-path design must remain a separate candidate with its own geometry and review status; never silently promote these point contacts into confirmed entrances or usable routes.
