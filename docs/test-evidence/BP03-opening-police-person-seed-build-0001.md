# BP03 Opening Police Person Identity Candidate Seed — Build 0001

**Dataset:** `SW-OPENING-POLICE-PERSON-SEED-V1`  
**Build workflow:** [45869474392 — success](https://github.com/Joshuaogri/saltwater/actions/runs/45869474392)  
**Build source commit:** `3018360c78feb4c8200f8aaa5d8c8152fcf1e910`  
**Generated data commit:** `83c7bccad39b8f9b1906a92d0c10cde3f5b59c03`  
**Branch:** `main`  
**Date:** 2026-11-26

## Result

- 500 deterministic three-part full-name candidates.
- 119 curated given-name components, 98 middle-name components and 162 family-name components.
- 500 unique normalized full names.
- Internal PostgreSQL-compatible trigram near-duplicate screen passed at threshold 0.90.
- Five generator regression tests passed.
- JSON output: 221,643 bytes.
- Gzip output: 14,044 bytes (approximately 93.7% smaller than JSON).
- Manifest SHA-256: `18288827707e7fce9e3d11eaee0f62b8219812396615bf8a2cabac317ff2c270`.

## Data boundary

This is a deterministic identity-candidate seed, not yet canonical BP03 person rows. Every row has a stable `candidate_ref` and `source_ref`, but `person_id` and `personnel_category` remain null. Names have not yet been reserved against the authoritative SW-UNS database registry. No date of birth, age, gender, ethnicity, nationality, citizenship, address, residence, rank, post, unit or personal history has been inferred.

The 500-person opening target remains binding. The precise sworn/civilian category allocation and post assignments are separate BP05–BP08 staffing work; the seed does not silently decide them.

No population rows were inserted, no personnel appointments were created, and no Neon production write or import was performed. The manifest explicitly records `production_import_authorized=false`.
