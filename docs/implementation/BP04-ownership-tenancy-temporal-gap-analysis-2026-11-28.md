# BP04 ownership, tenancy and temporal acceptance — current gap register

**Current baseline:** GitHub `main`, 2026-11-28. This document supersedes the earlier gap list in this file. Use the [BP04 strict acceptance audit](BP04-strict-acceptance-audit-2026-11-26.md) as the authoritative 48-criterion matrix. Do not recreate features listed below as implemented.

## Already implemented and verified

- **Agreement event history:** migration 0013 provides append-only agreement events with actor/source/evidence provenance, effective and recorded ticks, predecessor/successor references and idempotency.
- **Agreement lifecycle:** migration 0014 validates execution, variation, renewal, expiry, termination and surrender transitions. Renewal preserves the predecessor and links a successor. Expiry/termination/surrender do not automatically evict occupants.
- **Subletting and secondary occupancy:** migration 0015 records explicit superior/sub-agreements, superior and subtenant occupancy, and a current subletting right. A subtenant does not receive a second primary business-unit link. Ending the legal relationship does not silently end physical occupancy.
- **Contractual tenant assignment:** migration 0016 changes the legal tenant and associated contractual right while preserving operator and physical occupant. Active subletting must be ended first.
- **Property title transfer:** migration 0017 updates the ownership interest, title register, current property-interest record and property-rights schedule; creates a title instrument and transaction-index record; and does not create BP34 settlement or mutate tenancy/occupancy.
- **Physical occupancy handover:** migration 0018 explicitly closes the outgoing occupancy and primary unit link and creates the incoming records. It preserves legal agreements and rejects unresolved additional occupants or active subletting.
- **Concurrency and replay:** migrations 0019–0020 close the concurrent exact-subletting replay race and align unit/agreement lock order. Real two-session tests pass for exact subletting replay, subletting versus tenant assignment, competing handovers and concurrent exact handover replay.
- **Title-transfer race:** a new two-session test races two different transfers from the same expected owner. Exactly one succeeds; all title projections agree; landlord, tenant, operator, occupant and primary unit link remain unchanged. It passed on PostgreSQL 16 and 18 in [95-table disposable workflow 46138418805](https://github.com/Joshuaogri/saltwater/actions/runs/46138418805).
- **Full disposable acceptance:** workflow 46138418805 passed both PostgreSQL 16 and 18, including schema, agreement history, lifecycle transitions, concurrency, 10k lookup benchmark, 14 archive imports, gameplay lookup, repeat-import idempotency and storage stability.

All database acceptance above used disposable PostgreSQL. No production Neon migration, typed-row import or seed was performed.

## Remaining ownership/tenancy acceptance work

| Acceptance area | Current status | Remaining work |
|---|---|---|
| AC-C01 — role separation | PARTIAL | Complete the independent NPC role-combination matrix across owner, landlord, manager, tenant, operator and occupant, including third-party occupiers; keep all identities within their BP03/BP04 domains. |
| AC-C02 — joint, disputed and time-bounded interests | PARTIAL | Migrations 0021–0023 and PostgreSQL 16/18 acceptance now cover two 50% co-owners, disputed beneficial and occupancy claims, effective intervals, share-cap enforcement, fail-closed single-interest transfer and coordinated joint-title transfer. The joint writer closes every outgoing interest historically, creates same-share successor interests, reconciles title/rights/interest records, records all transferor/transferee pairs and preserves continuing tenancy. Remaining: broader overlapping-interest lifecycle cases and adversarial multi-party temporal sequences. |
| AC-C03 — agreement lifecycle and history | PARTIAL | Joint-title transfer now has PostgreSQL 16/18 acceptance proving the existing agreement and physical occupancy remain unchanged. Remaining: subletting start/end interleavings under concurrency, broader title/tenancy/occupancy transitions across registers and multi-register rollback. Preserve historic source unknowns (1,232 source agreements include unresolved counterparties and no recorded execution dates); do not invent evidence. |
| AC-C04 — subletting and third-party occupancy | PARTIAL | Migration 0024 provides the NPC consent lifecycle and named-authority enforcement. Migrations 0025–0026 serialize end transitions and exact replays with starts; two-session interleavings passed on PostgreSQL 16/18 in [workflow 46141933273](https://github.com/Joshuaogri/saltwater/actions/runs/46141933273). Remaining: broader third-party occupancy types and independent NPC role combinations. |
| AC-C05 — rent/payment separation | NOT VERIFIED | Prove BP04 agreement and occupancy events remain separate from BP34 rent, arrears, deposits, payments and settlement postings. |
| AC-E01/E02 — staff and person linkage | NOT VERIFIED | Verify BP03 person and BP33 employment references, deduplication and population-cap behaviour without BP04 creating people. |

## Execution order

1. Implement the missing subletting end/start concurrency cases using disposable PostgreSQL and real independent sessions.
2. Add joint/disputed/time-bounded ownership-interest fixtures and acceptance.
3. Complete the independent NPC owner/landlord/manager/tenant/operator/occupant matrix.
4. Add BP03/BP33/BP34 cross-register acceptance and rollback coverage.
5. Update the strict 48-criterion audit only when each criterion has direct repeatable evidence.

## Guardrails

- Work directly in this chat against GitHub `main` only. No branches or pull requests.
- All Saltwater people, businesses, organisations and counterparties are fictional NPCs. Generate coherent NPC roles and fictional gameplay agreements without external approval gates.
- Keep BP02 authoritative for operational parcel/address/geometry; BP03 for people/population; BP33 for employment; BP34 for financial postings; BP35 for event dispatch.
- Do not fabricate historical source facts or execution dates. Generated fictional canon must be explicitly classified as generated.
- Do not write to production Neon or seed production records without the user's explicit release instruction.
- Keep the BP04 completion status IN_PROGRESS until every one of the 48 acceptance criteria is passed with evidence.


### BP04 subletting end/start serialization — implementation added on main (2026-11-28)

Migration `0025_bp04_subletting_end_start_serialization.sql` changes the subletting end writer to acquire the physical unit lock before the relationship row, matching the start writer's unit-first lock order. This makes an end transition serialize with both an exact start replay and a new subletting start on the same unit. The new two-session tests cover both interleavings and assert that ending the legal relationship does not terminate the subtenant's physical occupancy. The 100-table PostgreSQL 16/18 disposable workflow now includes the migration and tests. **Validation is pending; no pass is claimed yet.** No production Neon write was made.


## BP04 subletting end/start serialization — disposable acceptance passed (2026-11-28)

Migration 0025 makes subletting termination lock the physical unit before the relationship row. Migration 0026 also makes exact start replays acquire that same unit lock before returning prior state, preventing a stale `active` replay from racing a concurrent end. Two-session tests cover (1) exact start replay versus end and (2) new start versus prior relationship end at the same effective tick, on both PostgreSQL 16 and 18. Both versions passed the complete 100-table schema/archive workflow, including the new interleavings, 10k lookup benchmark, archive import, gameplay lookup and repeat-import storage stability: [workflow https://github.com/Joshuaogri/saltwater/actions/runs/46141933273]. No production Neon write occurred. AC-C03/C04 remain PARTIAL because broader third-party occupancy types and the independent NPC role matrix are still outstanding.
