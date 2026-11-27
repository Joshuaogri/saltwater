# BP03 Household Membership Acceptance — Run 0002

- **Reviewed source commit:** `0d229dacbd467a3cd0d6c5c1ef45b8be1c3e946d`
- **Workflow:** PKG-001 disposable PostgreSQL validation
- **Run:** [46025222368](https://github.com/Joshuaogri/saltwater/actions/runs/46025222368)
- **Execution step:** `Apply foundation and PKG-001 to disposable PostgreSQL` — completed successfully.
- **Scope:** Disposable PostgreSQL only. No production Neon writes.

## Verified

The successful foundation step executes the BP03 population qualification proposal, BP02/BP04 test schema, BP03 residence integration, BP03 household proposal `0035_bp03_household_membership.sql`, and `tests/pkg001/household_membership_acceptance.sql` with `ON_ERROR_STOP=1`.

The household acceptance fixture verifies:
- Exact BP04-to-BP02 parcel/address crosswalk.
- Creation of a household tied to an active residential dwelling.
- Two canonical usual residents assigned to the same canonical residence.
- One household contact and one ordinary member.
- Household summary member/contact counts.
- Population count remains two after one household membership ends, because residence remains active.
- Append-only household creation, member-addition and departure history.

The fixture deliberately leaves `unit_space.use_class` null. Dwelling classification is taken from `unit_space.unit_class`; residential use is taken from the parent `property_site.use_class`, matching the actual BP04 property-world importer contract. This prevents the household service from depending on a unit-level use field that the source importer does not populate.

## Limits

This is a disposable service acceptance, not a live population allocation. It does not assign the 9,000 resident candidates to dwellings, infer household sizes or family relationships, activate property candidates in production, or create production person/household/residence rows. The full PKG-001 workflow and Gemini review remain separate running checks at the time this evidence was recorded.
