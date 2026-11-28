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
| AC-C01 — role separation | PARTIAL | Direct-owner and third-party management appointments and independent tenant/operator pairs cover every generated unit class. The canonical generator now creates 8 independent head-lessee organisations, 8 title-holder-granted property authorities and 8 immutable grant events; 1,821 current agreements use an authorised non-owner landlord. Stable UUIDs and role links passed 19 focused generator tests [46148027844](https://github.com/Joshuaogri/saltwater/actions/runs/46148027844). Migration/schema acceptance passed on disposable PostgreSQL 16/18 [46148246368](https://github.com/Joshuaogri/saltwater/actions/runs/46148246368), and the Python regression suite passed [46148246339](https://github.com/Joshuaogri/saltwater/actions/runs/46148246339). Third-party organisation/person occupancy and BP03/BP33 NPC employment remain covered by [46142915466](https://github.com/Joshuaogri/saltwater/actions/runs/46142915466). Remaining: broad canonical occupant/tenant combinations and typed-import acceptance for the authority collections. |
| AC-C02 — joint, disputed and time-bounded interests | PARTIAL | Migrations 0021–0023 and PostgreSQL 16/18 acceptance now cover two 50% co-owners, disputed beneficial and occupancy claims, effective intervals, share-cap enforcement, fail-closed single-interest transfer and coordinated joint-title transfer. The joint writer closes every outgoing interest historically, creates same-share successor interests, reconciles title/rights/interest records, records all transferor/transferee pairs and preserves continuing tenancy. Remaining: broader overlapping-interest lifecycle cases and adversarial multi-party temporal sequences. |
| AC-C03 — agreement lifecycle and history | PARTIAL | Migrations 0025–0026 and two-session PostgreSQL 16/18 tests now cover exact subletting-start replay versus end and new-start versus prior-end interleavings. The full [110-table workflow 46142915466](https://github.com/Joshuaogri/saltwater/actions/runs/46142915466) passed. Remaining: broader title/tenancy/occupancy transitions across registers, multi-register rollback beyond current writers, and historical source reconciliation. Preserve historic source unknowns (1,232 source agreements include unresolved counterparties and no recorded execution dates); do not invent evidence. |
| AC-C04 — subletting and third-party occupancy | PASS | Migrations 0024–0029 provide authority-bound consent, explicit business/organisation/person third-party occupancy, use types (licence, concession, desk/room share, storage, contractor, service provider, temporary use, event vendor and residential guest), append-only lifecycle events, and unit-first end/start/replay serialization. The complete [110-table PostgreSQL 16/18 workflow 46142915466](https://github.com/Joshuaogri/saltwater/actions/runs/46142915466) passed. |
| AC-C05 — rent/payment separation | PASS | Migrations 0031–0032 create BP34-owned rent schedules, charges, immutable payments/allocations and derived charge/agreement balances. PostgreSQL 16/18 acceptance verifies partial payment, full settlement, exact payment replay, overpayment rejection and unchanged BP04 agreement/physical occupancy states. Evidence: [workflow 46142915466](https://github.com/Joshuaogri/saltwater/actions/runs/46142915466). |
| AC-E01/E02 — staff and person linkage | PASS | Migration 0030 adds BP33 NPC employment records and validates BP04 staff-role references against both the canonical BP03 person and BP33 employment record. Acceptance creates one NPC with two independent employer roles, confirms one population count, and verifies ending one employment does not change identity or occupancy. Evidence: [workflow 46142915466](https://github.com/Joshuaogri/saltwater/actions/runs/46142915466). |

## Remaining work outside the requested NPC integration batch

1. Complete the independent manager appointment and owner/manager/landlord combination matrix across generated property classes.
2. Broaden overlapping ownership-interest lifecycle and adversarial multi-party temporal sequences; extend multi-register rollback beyond the current writers.
3. Reconcile historic source agreements without inventing unresolved counterparties or execution dates.
4. Complete service-availability/closure and dependency-disruption propagation, including verified BP02 route geometry and BP37 operational timetable bindings.
5. Close the remaining unrelated audit criteria: public-authority separation, stock/supplier workflows, police access and hidden-truth leakage, full drift reporting, and database-backed performance/storage evidence.

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


## Requested NPC integration batch — cleared

All five requested workstreams are implemented and accepted on disposable PostgreSQL 16 and 18 in [workflow 46142915466](https://github.com/Joshuaogri/saltwater/actions/runs/46142915466): subletting start/end concurrency; third-party occupancy and independent NPC roles; BP03/BP33 person/employment integration; BP34 rent/payment separation; and organisation/facility/healthcare/transport service interfaces. The complete 110-table schema/archive, lookup, archive import and repeat-import checks also passed. No production Neon write occurred. The wider BP04 48-criterion status remains IN_PROGRESS until the unrelated items above are resolved.


## BP02 parcel/address/access release — accepted 2026-11-28

BP02 full parcel/address/access acceptance [run 46144797735](https://github.com/Joshuaogri/saltwater/actions/runs/46144797735) passed on 2026-11-28. It released 420/420 canonical parcels and addresses, 2,948 operational access points, and 2,984 BP04 access locators with effective dates; all structural checks passed, all five frontage exceptions received geometry dispositions, and zero address-road-access exceptions remain unresolved. The run performed no database or Neon write.

This closes the BP04 spatial prerequisite: AC-B01 and AC-B05 are PASS. Do not recreate parcel, address or access-point generation/binding work. Continue with the remaining BP04 criteria in the strict audit.


## Independent tenant/operator combinations — accepted 2026-11-28

The deterministic property-tenure generator now selects a separate canonical business operator for a portion of current and historical agreements, including at least one such pairing for every generated unit class. Same-tenant/operator cases remain present. All operator references resolve to canonical business IDs. The focused property-tenure workflow passed all 14 tests and persisted the regenerated archive on `main`: [46145870349](https://github.com/Joshuaogri/saltwater/actions/runs/46145870349). This closes the generated tenant/operator pairing subtask only; AC-C01 remains PARTIAL until landlord/title-holder and occupant/tenant combinations are fully covered. No production Neon write occurred.


## Management role coverage by unit class — accepted 2026-11-28

The runtime tenure audit now produces a per-unit-class breakdown of property count, direct-owner management and third-party management appointments. A regression test confirms that every generated unit class is represented in the audit and that each property's current appointment is classified exactly once. The property ownership/occupancy build passed all 15 focused tests in [workflow 46146300199](https://github.com/Joshuaogri/saltwater/actions/runs/46146300199). The canonical tenure archive did not change because this was an audit/test enhancement. This strengthens AC-C01 but does not resolve independent landlord/title-holder or occupant/tenant relationships, which remain open.


## 2026-11-28 non-owner landlord authority — database slice accepted

Migrations 0033–0034 and [disposable PostgreSQL workflow 46147360337](https://github.com/Joshuaogri/saltwater/actions/runs/46147360337) passed. A head-lessee organisation can be a landlord only when the registered proprietor grants a matching authority for the property/unit and agreement term, backed by a recorded grant event. Direct-owner landlord agreements remain valid without an authority record. Missing, wrong-grantor, wrong-unit and out-of-term authority attempts fail; event history is immutable. Next remaining AC-C01 work is to generate and archive independent landlord/title-holder combinations and test the full canonical role graph.


## 2026-11-28 canonical landlord-role extension

The canonical generator now creates eight head-lessee organisations distinct from title holders and property managers, with eight property-scoped authorities and immutable grant events. 1,821 current agreements use these authorised non-owner landlords. The 19-test generator suite passed [46148027844](https://github.com/Joshuaogri/saltwater/actions/runs/46148027844); disposable PostgreSQL 16/18 schema and letting-authority acceptance passed [46148246368](https://github.com/Joshuaogri/saltwater/actions/runs/46148246368). The remaining AC-C01 work is the broader canonical occupant/tenant role matrix and typed-import acceptance.
