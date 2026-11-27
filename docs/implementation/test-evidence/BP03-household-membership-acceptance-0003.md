# BP03 Household Membership Acceptance — Run 0003

- **Source commit:** `465034d553b45a2152437f23c8c91dfd99ee88a4`
- **Workflow:** PKG-001 disposable PostgreSQL validation
- **Run:** [46025839757](https://github.com/Joshuaogri/saltwater/actions/runs/46025839757)
- **Successful execution step:** `Apply foundation and PKG-001 to disposable PostgreSQL`
- **Scope:** Disposable PostgreSQL 16 only; no production Neon writes.

## Verified

The successful foundation step applies BP03 proposal `0035_bp03_household_membership.sql` and runs `tests/pkg001/household_membership_acceptance.sql` with `psql -v ON_ERROR_STOP=1`.

This run uses the corrected BP04 source contract:
- Property-world generator sets source `primary_use='dwelling'` for pure-residential properties.
- BP04 importer maps `primary_use` into `sw_property.property_site.use_class`.
- Dwelling units carry `unit_class='dwelling'`.
- Household creation requires active `unit_class='dwelling'` and parent `property_site.use_class='dwelling'`.

The fixture verifies exact parcel crosswalk, household creation, two resident members, one household contact, member departure history, and unchanged population count while residence remains active.

## Scope boundary

The household service is now tested against the actual BP04 importer values, not a fabricated `residential` label. This does not assign any of the 9,000 opening resident candidates to a dwelling, infer household composition or occupancy capacity, or write production person/residence/household records. The property-world residential dwelling inventory build is a separate workflow and its exact count is pending.
