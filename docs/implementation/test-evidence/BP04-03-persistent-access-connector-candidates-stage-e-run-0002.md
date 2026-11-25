# BP04-03 persistent access connector candidates — Stage E run 0002

**Implementation commit:** `11d7cb0f69a64252c8fa71a8eabf12ed5d7042f1`  
**Full disposable PostgreSQL workflow:** [45519143869 — successful](https://github.com/Joshuaogri/saltwater/actions/runs/45519143869)  
**Migration validation:** [45519143747 — successful](https://github.com/Joshuaogri/saltwater/actions/runs/45519143747)  
**Generated asset inventory artifact:** `bp04-03-stage-e-complete-assets-45519143869` (1,557,657 bytes; 14-day GitHub Actions artifact)

## Correction before successful import

The first full import attempt exposed incomplete road-segment lineage in ordinary frontage access candidates. The parcel dossier generator now carries the contributing `road_segment_ids` into every frontage access candidate. Regression coverage requires every access candidate to retain at least one road-segment reference, and the importer independently rejects missing road or segment lineage before any insert.

The corrected Stage E run completed the full workflow successfully.

## Persisted connector records

The generated inventory now contains one distinct, stable connector candidate for every building-boundary access-location candidate. The records are stored in the append-only `sw_property.access_connector_candidate` table introduced by proposal 0017.

Each connector record carries:
- stable connector and parent access-point candidate identities;
- road access candidate identity, frontage candidate or road-reserve connection candidate;
- road ID and one or more road-segment IDs;
- connector classification and contact topology;
- two-endpoint GeoJSON LineString, coordinate reference and geometry checksum;
- measured straight-line length;
- source manifest checksum, source reference, generator/actor provenance, confidence and effective tick;
- explicit review status;
- construction, surface, slope, barrier, pedestrian/vehicle suitability, accessibility, legal/public access and emergency-egress knowledge states.

Unknown and not-assessed states are enforced in both Python validation and PostgreSQL constraints. A connector line remains a geometric candidate; it does not prove a constructed driveway/path, usable route, right of access, door/gate, public access, vehicle access or emergency egress.

The four point-contact-only road-reserve relationships remain separate from frontage candidates.

## Successful Stage E results

| Measure | Result |
|---|---:|
| Property identities | 420 |
| Building identities | 384 |
| Premises | 1,327 |
| Units | 15,199 |
| Building-boundary access-location candidates | 768 |
| Persistent connector candidates | 768 |
| Point-contact-only road-reserve connector candidates | 4 |
| Typed profiles | 18,098 |
| Typed detail records | 181,915 |
| Asset geometry candidates | 1,572 |
| Property-to-parcel lineage links | 420 |
| Connector road-segment lineage | Complete |
| Physical defect records fabricated | 0 |

The import manifest checksum is `4d035046c18d2de44043a886cac24e54bdc97bca294bcb19a5840f7a2ed80c3c`.

## Disposable PostgreSQL storage and performance

- Schema growth for proposals 0015 and 0017 combined: **409,600 bytes**.
- Proposal 0015 source size: **9,238 bytes**.
- Proposal 0017 source size: **5,015 bytes**.
- First complete asset/profile/detail/geometry/connector import growth: **130,973,696 bytes** (130.97 MB decimal; approximately 124.93 MiB).
- First import duration: **75,535.073 ms**.
- Connector table total relation size: **1,007,616 bytes** (approximately 1.01 MB).
- Same-manifest repeat import growth: **0 bytes**; duration **7.487 ms**.
- Backup/restore roundtrip: passed; connector table count and generation manifest checksum preserved.
- Representative indexed lookups: property candidate lookup **0.061 ms**, building-to-premises lookup **0.070 ms**, premises-to-unit lookup **0.073 ms**.

Regression suites passed:
- Physical asset generator: 10 tests.
- Physical asset importer: 11 tests.
- Parcel dossier generator: 6 tests.
- Parcel dossier importer: 6 tests.
- Total: **33 tests** across the Stage E regression step.

## Operational boundary

- Canonical addresses created: **0**.
- Operational access points created: **0**.
- Operational spatial IDs assigned: **0**.
- Ownership, tenancy, occupancy or business assignments created: **0**.
- Neon production writes: **none**.
- Neon database remains **9,306,112 bytes** (read-only measurement; PostgreSQL 18.7).
- Disposable Stage E database only; no production migration or activation was performed.

**Next:** add independent connector-to-road topology and route-corridor candidate checks. Keep the generated connector geometries distinct from actual constructed access and operational routing until separately supported by the fictional world model.
