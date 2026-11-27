# BP03 opening 9,500 identity name-registry preflight

**Date:** 2026-11-27  
**Blueprint:** BP03 — Population and Individual Simulation  
**Workflow:** [BP03 Opening Identity Registry Acceptance](https://github.com/Joshuaogri/saltwater/actions/runs/46040287960)  
**Result:** PASS  
**PostgreSQL:** Disposable PostgreSQL 16.16  
**Main commit under test:** `0ce55435a68bfa33f81b23b6a55a06cc587409a`

## Results

- All **500** opening police candidate names were inserted as temporary canonical person identities and reserved through the authoritative SW-UNS registry. The test confirmed 500 unique person IDs, 500 unique name reservation IDs and no duplicate normalized keys within the cohort.
- All **9,000** opening civilian candidate names were inserted as temporary canonical person identities and reserved through SW-UNS. The test confirmed 9,000 reservations, 9,000 distinct identities and 9,000 distinct normalized names, with every candidate linked to its canonical reservation.
- The civilian test verified the seed manifest checksum and exact opening reconciliation: 9,000 civilian residents + 500 police people = 9,500 distinct opening people; 10,000 hard cap; 500 unused headroom.
- Civilian names were checked for exact normalized overlap with the 500 police candidate names before database reservation.
- Both tests ran in disposable transactions and rolled back. No person or reservation rows were retained.

## Important boundary

This validates candidate-name uniqueness against the current disposable SW-UNS registry, not production person creation or population membership. It does not create canonical opening people, assign population qualifications, residences or households, create BP06 personnel dossiers, or seed Neon. No production write was performed.
