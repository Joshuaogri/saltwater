# SW-DB-001 — Canonical world provisioning candidate model

**Status:** Approved disposable implementation candidate; not production-approved  
**Branch:** main only  
**Neon production authority:** None

## Ownership and boundaries

- sw_people remains authoritative for person identity and population-state counting (BP-03).
- sw_business owns business identity and append-only business lifecycle history (BP-04 candidate; the division specification and distribution canon remain open).
- sw_geo remains the only owner of spatial identity. This package references existing roots only and creates no district, neighbourhood, road, parcel, address or coordinate rows.
- sw_names remains the universal naming authority (SW-UNS-001). Proposal 0010 extends its existing adapter to BUSINESS; it does not create a second naming registry.
- sw_ops.world_provisioning_batch stores immutable cross-domain batch provenance and expected counts only. It does not own person or business facts.

## Opening fixture

The deterministic disposable fixture represents exactly 9,500 distinct living person identities: 9,000 resident cohort and 500 police-subset cohort. The two cohorts are disjoint fixture classifications and reconcile to the same 9,500 person IDs and the authoritative sw_people.population_counter. The 500 headroom is left unused at opening.

The police-subset cohort is a test classification only. No sw_police.personnel row, appointment, rank, unit, supervisor or employment history is created. This keeps the fixture inside SW-DB-001 and avoids fabricating BP-05–BP-08 records.

The fixture creates 10,000 distinct business identities with unique globally reserved names. The varied sector/legal-form/staff-band values are stored in sw_test.business_profile, each value explicitly prefixed TEST_. These are workload assumptions only, not BP-04 business-distribution canon. Each test profile records NON_GEOGRAPHIC_TEST_FIXTURE; business site assignments remain unassigned and no unsupported geography is invented.

## Idempotency and provenance

- The checked-in JSON manifest is canonicalised with sorted keys and compact separators; its SHA-256 is recorded beside it and in the SQL fixture.
- The batch records generator/normalizer versions, configuration, deterministic seed, source revision, exact expected cohort totals, source, actor and reason; its environment scope is constrained to DISPOSABLE_TEST_ONLY.
- Immutable per-domain checksum rows record the 9,500-person and 10,000-business content counts and SHA-256 digests over ordered canonical fixture fields. Replays recompute and compare both digests.
- Stable fixture keys map each person cohort row to one person ID; stable business codes prevent duplicate business identities.
- Replaying the same manifest must not add people, businesses, canonical name reservations, or lifecycle history.
- Provisioning runs in one transaction; any failure rolls back the whole batch.

## Candidate schema and limitations

Proposal 0010 is disposable-only. It adds business identity/history, an immutable world-provisioning manifest and the SW-UNS business adapter. The schema deliberately does not decide BP-04 category/site distribution. It is a structural/capacity candidate, not a completed BP-04 implementation.

The fixture contains structural person identities, population states, business identities, names and test-only cohort/profile data. It does not create full biographies, social graphs, employment histories, police appointments, operational sites, cases, offenders or evidence. The world clock remains at tick zero; provisioning is not a simulation tick.

## Verification to be reported

The dedicated workflow measures raw database bytes before/after proposal 0010, before/after the fixture, and after a repeat run; relation heap/index/TOAST bytes; bytes per person/business; fixture/proposal source bytes; fixture elapsed time; population/headroom, person, business and reconciliation query plans; concurrent final-slot admission; and backup/restore manifest equality. Raw bytes are authoritative; decimal MB and MiB are reported separately.

A green workflow is disposable acceptance only. It does not approve BP-02/BP-03/BP-04/BP-38, G1 narrative quality, G2 Neon capacity, or any production migration/seed.
