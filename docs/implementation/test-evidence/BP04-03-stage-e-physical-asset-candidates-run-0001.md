# BP04-03 Stage E physical-asset candidate generation — run 0001

Date: 2026-11-24  
Workflow: [BP04-03 Stage E Physical Asset Candidates](https://github.com/Joshuaogri/saltwater/actions/runs/45502416189)  
Workflow commit: `d5791b394b4a8de8e12b4bd0a6fad6f6c2ad1fdd`  
Current implementation subsequently bounded the footprint search and reused immutable geography fixtures in tests; the successful run above is the first end-to-end candidate-generation proof.

## Result

The dedicated GitHub Actions job completed successfully. Seven Python regression tests passed. The deterministic generator created a complete candidate hierarchy from the 420 geometry-derived parcel candidates:

| Record class | Generated count |
|---|---:|
| Property-site candidates | 420 |
| Building-footprint candidates | 384 |
| Premises candidates | 1,327 |
| Unit-space candidates | 15,199 |
| Unreviewed access-location candidates | 768 |
| Properties without a building candidate | 36 |

Each building has two boundary access-location candidates. Building footprints are checked to be valid and wholly contained by their candidate property polygon. Premises are separated by floor; units are subordinate to premises. All records have deterministic identifiers, unique generated names, source references, actor references, confidence and effective tick.

## Reproducibility and artifact

- Candidate manifest SHA-256: `b710fcc3f5d08d24154ede08ebf99ec6a2f099a08c7f9c5d310c93ddb8aa30fe`
- Source parcel manifest SHA-256: `9b9bf26f756a74a8607d36a48c504879d12fd8ef9c188e34bda846bc71b11b9a`
- Uncompressed JSON source size: 10,981,615 bytes.
- Compressed GitHub Actions artifact: 356,640 bytes.
- [Download the preserved candidate manifest](https://github.com/Joshuaogri/saltwater/actions/runs/45502416189/artifacts/14970964187).

## Boundaries and unresolved work

This run proves deterministic candidate generation and geometry containment; it does not import the asset records into PostgreSQL. Building footprints and access locations are generated design candidates, not surveyed or operational facts. Physical materials, installed utilities, defects, condition, detailed room inventories and actual capacity are not fabricated. Unknown and not-assessed states remain explicit.

The run created zero operational spatial IDs, canonical addresses, operational access points, ownership records, tenancy records, occupancy records or business assignments. All 100 source-to-spatial-ID mappings remain unresolved. No Neon connection, migration, seed, upload or production activation occurred.

## Next implementation

Extend the manifest with the complete BP04-02 profile and typed child-record depth, add candidate geometry and generation-batch persistence to a new disposable-only proposal, then implement an idempotent PostgreSQL 16 importer with schema, storage, query, rollback and backup/restore acceptance.
