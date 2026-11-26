-- Disposable acceptance for the immutable BP-02 SW-GEO-V1 source archive.
DO $$
DECLARE
  v_count integer;
  v_row sw_geo.source_archive%ROWTYPE;
BEGIN
  SELECT count(*) INTO v_count FROM sw_geo.source_archive
  WHERE release_code = 'SW-GEO-V1';
  IF v_count <> 1 THEN
    RAISE EXCEPTION 'expected exactly one SW-GEO-V1 archive, found %', v_count;
  END IF;

  SELECT * INTO v_row FROM sw_geo.source_archive
  WHERE release_code = 'SW-GEO-V1';
  IF v_row.archive_format <> 'tar.gz'
     OR v_row.compressed_bytes <> octet_length(v_row.compressed_payload)
     OR v_row.compressed_bytes <= 0
     OR v_row.uncompressed_bytes <= v_row.compressed_bytes
     OR v_row.source_file_count <> 2
     OR v_row.release_scope <> 'SOURCE_ARCHIVE_ONLY'
     OR v_row.archive_sha256 !~ '^[0-9a-f]{64}$'
     OR jsonb_typeof(v_row.source_manifest) <> 'object'
     OR v_row.source_manifest->>'release_code' <> 'SW-GEO-V1'
     OR v_row.source_manifest->>'operational_geography_promoted' <> 'false'
     OR (v_row.source_manifest->'identity_validation'->>'resolved')::integer <> 100
     OR (v_row.source_manifest->'identity_validation'->>'unresolved')::integer <> 0 THEN
    RAISE EXCEPTION 'SW-GEO-V1 archive metadata or release boundary failed acceptance';
  END IF;
END
$$;

SELECT release_code, archive_format, compressed_bytes, uncompressed_bytes,
       source_file_count, archive_sha256, release_scope
FROM sw_geo.source_archive
WHERE release_code='SW-GEO-V1';
