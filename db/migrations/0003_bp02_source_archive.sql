-- Saltwater migration 0003: immutable BP-02 source archive, archive-only release.
-- This stores the verified SW-GEO-V1 source package without promoting any
-- geometry, parcel, address or access point into operational gameplay tables.
-- Production deployment requires a separate measured release approval.

BEGIN;

CREATE SCHEMA IF NOT EXISTS sw_geo;

CREATE TABLE sw_geo.source_archive (
  release_code text PRIMARY KEY
    CHECK (release_code ~ '^SW-GEO-[A-Z0-9-]+$'),
  archive_format text NOT NULL CHECK (archive_format = 'tar.gz'),
  compressed_payload bytea NOT NULL CHECK (octet_length(compressed_payload) > 0),
  compressed_bytes bigint NOT NULL
    CHECK (compressed_bytes = octet_length(compressed_payload)),
  uncompressed_bytes bigint NOT NULL CHECK (uncompressed_bytes > 0),
  source_file_count smallint NOT NULL CHECK (source_file_count = 2),
  source_manifest jsonb NOT NULL
    CHECK (jsonb_typeof(source_manifest) = 'object'),
  archive_sha256 char(64) NOT NULL
    CHECK (rtrim(archive_sha256) ~ '^[0-9a-f]{64}$'),
  source_commit text NOT NULL
    CHECK (length(btrim(source_commit)) BETWEEN 7 AND 64),
  release_scope text NOT NULL DEFAULT 'SOURCE_ARCHIVE_ONLY'
    CHECK (release_scope = 'SOURCE_ARCHIVE_ONLY'),
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);

CREATE FUNCTION sw_geo.reject_source_archive_mutation()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'BP-02 source archives are immutable; publish a new release code';
END
$$;

CREATE TRIGGER source_archive_immutable
BEFORE UPDATE OR DELETE ON sw_geo.source_archive
FOR EACH ROW EXECUTE FUNCTION sw_geo.reject_source_archive_mutation();

REVOKE ALL ON sw_geo.source_archive FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_geo.reject_source_archive_mutation() FROM PUBLIC;

COMMIT;
