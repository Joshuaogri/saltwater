-- PROPOSAL ONLY — BP38-02 legacy checksum adoption.
-- Do not execute against Neon until the read-only replay comparison and
-- supplementary production review both pass and the user separately approves
-- this exact one-row production operation.
--
-- Expected exact SHA-256 of committed db/migrations/0001_foundation.sql:
-- d4f874f71eb53a961fd3abe87a9342d0354a006ef04575158d2c72937dbe6aa8
--
-- Preconditions: version 1, migration_name 'foundation', checksum NULL,
-- exactly one matching ledger row. Any other state aborts the transaction.
-- This changes one metadata field in one existing ledger row only.

BEGIN;

DO $adoption$
DECLARE
    changed_rows integer;
    adopted_checksum text;
BEGIN
    UPDATE sw_ops.schema_migration
       SET checksum_sha256 =
           'd4f874f71eb53a961fd3abe87a9342d0354a006ef04575158d2c72937dbe6aa8'
     WHERE version = 1
       AND migration_name = 'foundation'
       AND checksum_sha256 IS NULL;

    GET DIAGNOSTICS changed_rows = ROW_COUNT;
    IF changed_rows <> 1 THEN
        RAISE EXCEPTION
            'BP38-02 adoption aborted: expected exactly 1 eligible row, updated %',
            changed_rows;
    END IF;

    SELECT checksum_sha256
      INTO adopted_checksum
      FROM sw_ops.schema_migration
     WHERE version = 1
       AND migration_name = 'foundation';

    IF adopted_checksum <>
       'd4f874f71eb53a961fd3abe87a9342d0354a006ef04575158d2c72937dbe6aa8' THEN
        RAISE EXCEPTION 'BP38-02 adoption aborted: post-update checksum mismatch';
    END IF;
END
$adoption$;

COMMIT;
