-- Saltwater migration 0002: enforce migration ledger integrity and drift evidence.
-- The migration runner records the SHA-256 checksum and live schema fingerprint.
BEGIN;

ALTER TABLE sw_ops.schema_migration
    ALTER COLUMN checksum_sha256 SET NOT NULL;

ALTER TABLE sw_ops.schema_migration
    ADD CONSTRAINT schema_migration_checksum_sha256_check
    CHECK (checksum_sha256 ~ '^[0-9a-f]{64}$');

ALTER TABLE sw_ops.schema_migration
    ADD COLUMN schema_fingerprint_sha256 char(64);

ALTER TABLE sw_ops.schema_migration
    ADD CONSTRAINT schema_migration_schema_fingerprint_check
    CHECK (
        schema_fingerprint_sha256 IS NULL
        OR schema_fingerprint_sha256 ~ '^[0-9a-f]{64}$'
    );

COMMIT;
