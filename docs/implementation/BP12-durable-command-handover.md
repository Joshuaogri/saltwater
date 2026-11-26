# BP12 durable incident command handover

## Authority and ownership

BP12 owns the authoritative, append-only incident command handover record and its event history. BP08/BP10 remain authoritative for deployment and field-activity assignments. The handover projection reconciles those owner snapshots with BP12 dispatch acknowledgement and unit-arrival events; it does not replace either source.

## Record contract

`sw_incident.record_command_handover(...)` persists only a handover projection that is marked ready, includes an outgoing-to-incoming responsibility transfer, contains the incoming commander's `ACCEPTED` acknowledgement, and contains no `DECLINED` acknowledgement. It stores the full document, identity, effective world tick, actor, authority, source provenance, and idempotency key. The corresponding `INCIDENT_COMMAND_HANDOVER_RECORDED` simulation event is the durable event anchor.

The SQL function enforces:
- active, player-present simulation state and a non-future effective tick;
- existing, non-terminal incident identity;
- distinct outgoing and incoming commander references;
- document/register shape and identity reconciliation;
- ready-state, transfer and acceptance requirements;
- idempotent replay only when the original handover identity, source and document match;
- append-only history (updates and deletes are rejected).

`sw_incident.command_handover_history(incident_id)` returns the immutable register in effective-tick and record-ID order. The Python PostgreSQL writer accepts only the existing read-only projection and the history reader validates incident identity, timestamps, ordering and persisted provenance. Both are data adapters; callers must first complete the separate audited BP12 command-handover, BP08 assignment and BP12 operational-timeline permissions.

## Persistence boundary

Migration `0029_bp12_command_handover.sql` and its acceptance coverage are repository/disposable-PostgreSQL assets. They have not been applied to production Neon. No production write is authorised by this implementation. The migration is added to the disposable PKG-001 workflow only.

## Acceptance coverage

The SQL acceptance test covers creation, complete provenance, chronological history, idempotent replay, immutable update rejection and rejection of an unready handover. Python adapter contract tests cover parameterised writes, projection gating, history validation and cross-incident rejection.
