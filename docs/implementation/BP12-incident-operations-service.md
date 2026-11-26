# BP12 Incident Operations Service

**Status:** Implemented on `main`; automated adapter tests running  
**Owner:** BP12 — Incident Management  
**Database owner:** `sw_incident`  
**Production Neon:** unchanged

## Delivered

`runtime/bp12_incident_service.py` exposes a bounded officer-facing service over the canonical BP12 incident records:

- `list_open` reads the active incident queue with deterministic priority/creation ordering and a caller-bounded result limit (1–100).
- `inspect` reads one incident and its ordered location history.
- `create` creates an incident through `sw_incident.create_incident`, preserving source identity, caller identity state, narrative, classification, priority/severity and any supplied raw/property/road-style location reference.

Every operation checks the current session and a specific BP12 grant through the shared `AuthorizationService`, requires an officer principal, and records the decision through the configured audit sink. Incident creation derives its actor reference from the verified session's active person ID; caller-supplied actor identity is not accepted. Missing active person identity, missing grants, revoked sessions or audit failure deny the action before the database operation.

The service uses the existing BP12 schema and stored function. It creates no parallel incident store and does not assign units, claim dispatch acknowledgement, report arrival or change the operational clock.

## Example composition

```python
service = PostgresIncidentService(
    connect,
    authorization,
    officer_principal_id,
)

open_incidents = service.list_open(
    officer_credential,
    limit=25,
)

incident_id = service.create(
    officer_credential,
    source_type="police_call",
    source_record_id="CALL-REFERENCE",
    narrative="Caller reports an incident near the terminal.",
    idempotency_key="incident:CALL-REFERENCE",
    caller_identity_state="anonymous",
    location_raw="Near the terminal entrance",
    location_confidence="unverified",
)
```

The example reference is illustrative; actual calls must use the live source record and a unique idempotency key.

## Next operational connection

This service supplies the incident record surface needed by the dispatch workflow. The next increment is the BP11 dispatch assignment lifecycle, connected to BP08's authoritative unit/readiness/deployment records and BP12's existing acknowledgement/arrival timeline mirrors. Until that integration is delivered, this service does not claim a complete CAD or dispatch workflow.

## Test coverage

`tests/pkg001/test_bp12_incident_service.py` covers authorised queue reads, incident inspection with location history, incident creation through the BP12 function, verified officer attribution, default-deny behaviour, principal-kind separation, invalid identifiers/limits and invalid intake rejection.

The suite is included in the PKG-001 Python workflow. This is an adapter-level delivery; it does not claim production deployment or full BP12 division acceptance.
