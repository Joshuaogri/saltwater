# Synthetic lifecycle storage benchmark — run 1

Date: 2026-11-22  
Workflow run: https://github.com/Joshuaogri/saltwater/actions/runs/45048572631  
Result: successful  
Benchmark commit: 40be822f49ff07b1a0fc46507155bcf7ff5e3982

## Dataset generated

| Dataset | Rows |
|---|---:|
| Synthetic residents | 10,000 |
| Synthetic businesses | 10,000 |
| Relationships | 30,000 |
| Employment records | 20,000 |
| Cases | 2,000 |
| Incidents | 10,000 |
| Evidence metadata | 10,000 |
| Historical events | 150,000 |
| **Total** | **232,000** |

## Measured temporary relation footprint

All figures are decimal MB (1 MB = 1,000,000 bytes). The benchmark relations were temporary tables in a single PostgreSQL session.

| Relation | Heap MB | Index MB | Total MB |
|---|---:|---:|---:|
| Historical events | 47.194 | 7.905 | 55.140 |
| Relationships | 3.277 | 1.704 | 5.014 |
| Businesses | 2.564 | 1.180 | 3.777 |
| Residents | 2.703 | 0.852 | 3.588 |
| Evidence metadata | 2.490 | 0.631 | 3.154 |
| Incidents | 2.154 | 0.590 | 2.777 |
| Employment | 1.221 | 1.319 | 2.572 |
| Cases | 0.426 | 0.229 | 0.688 |
| **Total** | **62.030** | **14.410** | **76.710** |

The event relation accounts for approximately 71.9% of this benchmark footprint. Indexes account for approximately 18.8% overall. These results support prioritising event schema design, compact event payloads, retention/archive policy and index discipline.

## Database size observations

- Database before benchmark session: 8,134,656 bytes (8.135 MB).
- Database after benchmark session ended: 8,298,496 bytes (8.298 MB).
- Observed database-size difference: 163,840 bytes (0.164 MB).

The 76.710 MB relation footprint is measured while the temporary relations exist. Temporary relations are removed when the connection closes, so that footprint is not a persistent database growth measurement. The 0.164 MB post-session difference is not the dataset footprint and must not be treated as such.

## What this test proves

- Neon successfully executed the synthetic workload.
- The test generated the specified resident, business, relationship, employment, case, incident, evidence-metadata and event row counts.
- The measured temporary table and index footprint for this particular row mix is 76.710 MB.
- The event table dominates this sample.

## What it does not prove

This is not a complete lifecycle capacity test and does not approve the 1 GB limit. The test does not yet model sufficient detail or volume for every subsystem, including full address/property/geography records, institution and government structures, police staff and duty histories, dispatch/radio/CAD records, interviews and transcripts, intelligence linkages, surveillance metadata, forensic examination data, legal/court/custody records, financial and commercial transactions, family/household histories, and multi-decade event accumulation.

It also stores evidence metadata only, not original photographs, video, audio, scans or other binary exhibits. Those require a separately measured storage strategy and must be included in lifecycle capacity planning if hosted in Neon.

## Required next benchmark iteration

1. Expand the relational model to include all omitted operational and institutional subsystems.
2. Use explicit lifecycle assumptions (years simulated, events per resident/business/officer, average text lengths, case volume and evidence volume).
3. Test both ordinary and high-activity scenarios.
4. Measure persistent relation growth in an isolated benchmark database/branch or a carefully reversible transaction, including heap, indexes, TOAST and database overhead.
5. Measure archival/compression and binary-object storage separately.
6. Produce conservative and stress-case projections with a safety reserve.

**Capacity status: NOT APPROVED.** No production population, business, case or evidence seeding is authorised by this benchmark result.
