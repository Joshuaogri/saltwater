# BP04 ownership and tenancy temporal gap analysis — 2026-11-28

## Scope

Targeted review of the existing BP04 tenure and lifecycle generators after the 20,000-name persistent business-name acceptance passed. This is a gap analysis of existing work, not a replacement property model and not production data authorisation.

## Existing implementation retained

- `runtime/property_tenure_generator.py` generates current ownership interests for all 420 canonical property sites, ownership event chains, historical-owner organisations where applicable, management appointments, 10,000 current business agreements, historical expired agreements, business occupancies and unit occupancy states.
- `tests/pkg001/test_property_tenure_generator.py` verifies current-owner chronology, all-business agreement/occupancy references, business-to-unit links, unique unit states, manager references, non-overlapping historical agreement terms and columnar output.
- `runtime/property_lifecycle_transactions_generator.py` creates title registers, title instruments and transaction indexes that reference the tenure dataset's ownership events. It explicitly avoids creating duplicate ownership events or financial postings.
- `tests/pkg001/test_property_lifecycle_transactions_generator.py` verifies source-event identity, title/instrument references, baseline building/premises lineage, unknown encumbrance treatment, no fabricated physical changes, no financial/person records, identifier uniqueness and determinism.
- `db/proposals/0012_bp04_canonical_property_stack.sql` already defines distinct ownership-interest, occupancy-agreement, occupancy and business-unit-link relations. Do not create parallel copies of these concepts.

## Verified temporal gaps

1. **Agreement execution is not represented.** Current and historical generated agreements contain commencement and (for historical agreements) expiry years, but no execution date/tick or execution event.
2. **Agreement lifecycle events are not a first-class register.** The tenure output stores agreement state snapshots; it does not emit a source-authoritative event sequence for execution, variation, renewal, expiry, termination, assignment or surrender.
3. **Expiry and physical occupancy are not tested independently.** Existing tests prove a historical agreement expires before the current agreement starts. They do not prove that an expired agreement can coexist with continuing physical occupancy, nor that expiry alone does not mark a unit vacant or evict an occupant.
4. **Renewal is descriptive, not event-backed.** `renewal_option` is generated, but no renewal event links old and successor agreements or records changed terms.
5. **Subletting and third-party occupation lack positive/negative acceptance.** The current primary business-unit link deliberately limits one primary business per unit. The model needs a separate, explicit occupancy relationship for lawful subletting/shared occupation rather than weakening that primary-link invariant.
6. **Continuing tenancy after ownership transfer lacks an integrated acceptance case.** Ownership chains and agreements exist separately, but no test proves a transfer preserves the agreement, tenant, operator, unit occupancy and agreement chronology without rewriting prior ownership facts.
7. **Counterparty and execution evidence must not be fabricated.** The existing historic agreement source inventory had unresolved counterparties and no recorded execution dates. Do not fill these gaps with guessed counterparties or inferred execution dates. Keep source-unknown values explicitly unknown; synthetic fictional gameplay agreements may have generated event dates only when clearly marked as generated canon.

## Acceptance work to implement next

- Introduce an append-only agreement-event history with stable event IDs, agreement IDs, event type, effective time, recorded time, actor/source provenance, predecessor/successor links and explicit generated-vs-source evidence classification.
- Preserve existing agreement and occupancy tables as current/temporal projections; do not duplicate the authoritative event stream.
- Add state-transition validation for execution, variation, renewal, expiry, termination, assignment and surrender.
- Add adversarial fixtures:
  - expired agreement + continuing physical occupancy;
  - expiry without automatic vacancy, eviction or population mutation;
  - renewal creates a successor/renewal event without erasing the predecessor;
  - subletting requires an explicit superior agreement/right and does not create a second primary unit link;
  - ownership transfer while a lease continues preserves tenant/operator/occupancy and historical title events;
  - mismatched property/unit/tenant/counterparty and overlapping exclusive occupancy fail closed;
  - replay/idempotency and multi-record rollback leave no partial state.
- Reconcile the existing 1,232 source agreement inventory separately from generated game-world agreements. Retain unresolved counterparty and missing execution-date counts as unresolved until evidence is supplied.
- Benchmark the acceptance queries at representative scale. Correctness is not a substitute for the BP04 query-performance criterion.

## Guardrails

- Work only on GitHub `main`; no branches or pull requests.
- Validate against disposable PostgreSQL only. No production Neon writes or seeding.
- BP02 retains authority for operational parcel/address/geometry; BP03 owns people and population; BP34 owns rent/payment postings; BP35 owns event dispatch.
- Do not infer human tenants or create person/population records from organisation/business occupancy.
- Existing BP04 components and accepted tests remain intact. This gap analysis does not mark BP04 complete.
