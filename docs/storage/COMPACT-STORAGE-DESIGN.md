# Saltwater compact-storage design standard

**Status:** Binding design standard for new implementation work; no schema or production write authorised.  
**Owner:** BP-38. **Applies to:** all 44 divisions.  
**Objective:** smallest practical storage footprint per entity, event and lifecycle while preserving complete simulation meaning.

## 1. Priority

Correctness, canon, evidential integrity and player agency first; minimum lossless storage second; recoverability/queryability third; performance optimised from measurements.

Never trade away meaningful facts, uncertainty, source originals, chronology, provenance, relationships or required history for smaller rows.

## 2. Storage rules

| Data | Required pattern |
|---|---|
| People/businesses/properties/cases/exhibits | One canonical identity row; stable compact ID |
| Cross-domain links | Typed references; no copied profile |
| Mutable state | Current state plus attributable compact transitions where history requires |
| Immutable source | Store once; link by ID/hash/object reference |
| Events | Compact typed envelope; variable payload only where needed |
| Repeated text | Shared template only for genuinely identical boilerplate; preserve individual variation |
| Narrative/interviews/reports | Complete text; no semantic truncation |
| Images/audio/video/documents | Object storage where suitable; DB stores reference, hash, size, media type and provenance |
| Counts/search/reporting | Rebuildable projections; never a second source of truth |
| Cache | Disposable and rebuildable |

## 3. Schema design

- Prefer narrow typed columns for queried fields and invariants.
- Use small integer enums only for stable, versioned code lists.
- Use compact stable IDs, not names or mutable attributes as keys.
- Do not store derived age, totals, display labels, formatted dates, duplicate names/addresses or repeated role descriptions.
- Use JSONB only for bounded, validated, genuinely variable attributes; keep identity, status, relationships, custody and population invariants relational.
- Split rare optional detail into extension tables only when measured savings justify join cost.
- Store only required timestamps: distinguish event, effective, recorded and source time where semantically needed.
- Add indexes only for demonstrated queries; record size and write amplification.
- Do not partition until measured volume/query patterns justify it.
- Keep raw binaries out of PostgreSQL unless a measured requirement justifies in-row storage.
- Measure PostgreSQL/TOAST compression; assume no fixed ratio.
- Exact-content deduplication is allowed only if identity, access, retention and provenance remain independent.

## 4. Event and history

- Canonical domain record owns current authoritative state.
- Immutable source/event records preserve original claims and transitions.
- Store changed fields/compact deltas when safe; do not duplicate full entity snapshots per event.
- Checkpoints require measured replay/query justification and must be reproducible.
- Event payloads reference canonical IDs; never embed repeated person/business profiles.
- Keep actor, authority, source, type/version, causal/correlation references and required time.
- Corrections append linked correction/supersession; never silently overwrite evidential history.
- Derived narratives/summaries link to source and identify themselves as derived.

## 5. Text and compression

- Preserve full meaningful narrative and exact source material.
- Use compact serialization and field names internally; expand labels only at the interface.
- Avoid repeated boilerplate using versioned templates only when exact wording is genuinely shared.
- Compress large text/blobs only after benchmarking CPU, query, update and backup costs.
- Never replace a source with a summary, hash or embedding. A hash verifies; it does not replace content.

## 6. Measurement

Measure heap bytes/row and table totals; index bytes; TOAST; WAL/backup impact; external object bytes; bytes per person/business/case/exhibit and per transition; query cost and write amplification.

Benchmark low/median/high detail, especially long interviews, reports, source documents and evidence manifests. Include realistic distributions and high-entropy text. Report bytes, decimal MB and binary MiB. Keep PostgreSQL size separate from provider billing/logical-size metrics.

## 7. Acceptance criteria

- No duplicate canonical identities or copied profile payloads.
- Every foreign key has an owner and lifecycle.
- Every field has purpose, type, nullability, source and retention rule.
- Every index has query justification and measured size.
- Required history/provenance survives correction, replay, restore and export.
- Estimates include heap, indexes, TOAST and material external objects.
- Disposable PostgreSQL benchmark proves bytes per representative record and lifecycle growth.
- No production Neon operation without fresh estimate and explicit approval.

## 8. Current baseline and gate

Read-only production measurement on 2026-11-23: `pg_database_size` **9,306,112 bytes** (9.306 MB decimal; 8.875 MiB); user relations **188,416 bytes**; five user tables; one world configuration row; no domain simulation tables or seed data.

Provider logical-size metadata of 33,611,776 bytes from 2026-11-22 is a different metric and is not comparable to `pg_database_size`.

**No production domain migration or seed is authorised.** Every proposed Neon write requires a fresh baseline, incremental byte estimate, assumptions/range, projected total and explicit user approval.

## 9. Cross-division application

BP-03: one canonical person row; role/employment/relationship references; no repeated biographies; permanent detail promotion when relevant.  
BP-04: one canonical business/property/premises identity; separate establishments and time-valid relationships; at least 10,000 genuine businesses without placeholders.  
BP-35: compact event envelopes and causality references; no duplicate domain payloads or routine full snapshots.  
BP-38: schema, compression, index and measurement authority. BP-39: backup/restore/retention. BP-43: disposable byte-level tests. All other divisions apply this standard to schemas, logs, events, reports and attachments.
