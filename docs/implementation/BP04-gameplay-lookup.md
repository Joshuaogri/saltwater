# BP04 gameplay-facing property and business lookup

**Status:** implemented on `main`; dedicated synthetic contract tests and the full archive-only disposable PostgreSQL workflow passed on PostgreSQL 16 and 18 in [run 45678245109](https://github.com/Joshuaogri/saltwater/actions/runs/45678245109).

## Purpose

Provide the game runtime with a small read-only lookup API over the existing compressed BP04 archives. The archives remain the canonical static source. This layer builds process-local indexes for stable identities and common navigation paths; it does not materialise or persist duplicate static rows in Neon.

## Supported identities

- Property ID and stable BP-02 parcel design ID (`SWP-…`)
- Address source ID and stable BP-02 address design ID (`SWA-…`)
- Building ID
- Premises ID
- Unit ID
- Access-point ID
- Business ID
- Establishment ID

## Supported operations

- Exact identity lookup with `get(entity_type, identifier)`, including `get("parcel", SWP_ID)` and `get("address", SWA_ID)` aliases.
- Bounded case-insensitive partial search for addresses, businesses and properties with `search(entity_type, query, limit=20)`. Limit is restricted to 1–100.
- Property dossier with its primary address, buildings and linked business operators using `property_detail(property_id_or_SWP_id)`.
- Address-to-property resolution using `address_detail(address_id_or_SWA_id)`.
- Business dossier with all establishments and their linked address/property using `business_detail(business_id)`.
- Indexed source collection counts through `counts`.

## Runtime use

The application supplies its existing psycopg connection. No new database object or write is required:

```python
from runtime.bp04_lookup import BP04Lookup

lookup = BP04Lookup(connection)

matches = lookup.search("address", "Harbour Avenue", limit=10)
address_id = matches[0]["address_id"] if matches else None
property_dossier = lookup.address_detail(address_id) if address_id else None

businesses = lookup.search("business", "Harbour Bank", limit=10)
business_dossier = (
    lookup.business_detail(businesses[0]["business_id"])
    if businesses else None
)
```

The constructor reads each of the two required compressed datasets once, verifies their SHA-256 digests through `bp04_archive_reader`, and retains only the selected identity/navigation fields. The decoded archive documents are not retained by the lookup object. The object is read-only and process-local; rebuild it when a new static BP04 release is activated. It is not a persistent cache or write model.

## Integrity and safety boundaries

- Missing collections, malformed rows, duplicate indexed identities and dangling core property/business links fail closed during index construction.
- Search is bounded, deterministic and case-insensitive. It is not an unrestricted full-text search engine.
- Stable `SWP-` parcel and `SWA-` address design IDs are derived deterministically from immutable source IDs and exposed in lookup records. They are aliases for linked BP04 property/address records, not separate duplicated records.
- Lookup details report `bp02_design_identity_bound_operational_release_blocked`; each design identity carries an explicit not-approved operational status. A generated address label is not treated as an activated operational address.
- This API does not implement police permissions, role-based disclosure, hidden-truth filtering or evidence provenance. Police-facing callers must use the authorised access contract when that integration is implemented.
- This increment does not index the other BP04 operational registers (tenure, schedules, utilities, maintenance, security, valuation, development control, facilities, insurance, lifecycle, rights or capacity audit). Those remain available in the archive reader and should be added only when a gameplay query requires them.
- No Neon schema, archive or source data was changed.

## Verification

Dedicated tests cover exact ID lookup across all eight BP04 identity types, SWP/SWA design-ID aliases, design-ID search, address/business search, property/address/business dossier joins, missing identities, bounded search, source counts and fail-closed handling of dangling establishment links. The BP04 disposable workflow runs these tests alongside the full archive-only PostgreSQL acceptance on PostgreSQL 16 and 18.
