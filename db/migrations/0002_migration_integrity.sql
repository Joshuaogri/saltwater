-- Saltwater migration 0002: enforce migration checksum integrity.
-- The migration runner records the checksum for 0001 before this migration.
BEGIN;

ALTER TABLE sw_ops.schema_migration
    ALTER COLUMN checksum_sha256 SET NOT NULL;

ALTER TABLE sw_ops.schema_migration
    ADD CONSTRAINT schema_migration_checksum_sha256_check
    CHECK (checksum_sha256 ~ '^[0-9a-f]{64}$');

COMMIT;
