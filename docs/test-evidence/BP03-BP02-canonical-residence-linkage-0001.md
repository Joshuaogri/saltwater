# BP03–BP02 Canonical Residence Linkage

## Contract
BP03 residence records reference active BP02 gameplay addresses by stable source ID. One current residence link is maintained per person, with prior assignments retained as effective-dated rows and append-only event history. Assigning or changing residence establishes the person's usual-resident qualification. Ending residence removes only that qualification and preserves physical-presence or police-service qualifications.

## Acceptance
The disposable PostgreSQL test creates two fixture BP02 addresses, verifies idempotent residence assignment, moves the person between addresses, checks closure of the old link and activation of the new link, ends residence while physical presence remains, and finally removes physical presence to reconcile the population total to zero.

## Limits
This tests the BP02 address foreign-key and BP03 residence service against disposable fixture addresses. It does not import the operational city address dataset or create the 9,000-resident cohort. Production Neon remains unchanged.
