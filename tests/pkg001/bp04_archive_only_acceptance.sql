-- BP04 archive-only acceptance: all source records remain losslessly available
-- from the compressed archives; no permanent typed-row materialisation is performed.
DO $archive_only$
DECLARE
  v_datasets bigint;
  v_collections bigint;
  v_archives bigint;
  v_loaded bigint;
  v_source bigint;
  v_archive_bytes bigint;
  v_bad bigint;
BEGIN
  SELECT count(*), coalesce(sum(source_record_count),0),
         coalesce(sum(loaded_record_count),0)
    INTO v_datasets, v_source, v_loaded
    FROM sw_property.import_dataset;
  SELECT count(*) INTO v_collections FROM sw_property.source_dataset_collection;
  SELECT count(*), coalesce(sum(compressed_bytes),0)
    INTO v_archives, v_archive_bytes
    FROM sw_property.source_dataset_archive;

  IF v_datasets <> 14 OR v_archives <> 14 THEN
    RAISE EXCEPTION 'Expected 14 archived datasets and ledger entries; got %, %', v_archives, v_datasets;
  END IF;
  IF v_collections <> 105 THEN
    RAISE EXCEPTION 'Expected 105 source collections; got %', v_collections;
  END IF;
  IF v_loaded <> 0 THEN
    RAISE EXCEPTION 'Archive-only mode must not materialise typed rows; loaded count %', v_loaded;
  END IF;
  IF v_source < 1900000 THEN
    RAISE EXCEPTION 'Unexpectedly low source record count: %', v_source;
  END IF;
  IF v_archive_bytes <> (SELECT sum(compressed_bytes) FROM sw_property.source_dataset_archive) THEN
    RAISE EXCEPTION 'Archive byte accounting mismatch';
  END IF;
  SELECT count(*) INTO v_bad
  FROM sw_property.import_dataset d
  WHERE d.mapping_status <> 'archive_only' OR d.loaded_record_count <> 0;
  IF v_bad <> 0 THEN
    RAISE EXCEPTION 'Dataset ledger contains non-archive-only mappings: %', v_bad;
  END IF;
  SELECT count(*) INTO v_bad
  FROM sw_property.source_dataset_collection c
  WHERE c.mapping_status <> 'archive_only' OR c.loaded_record_count <> 0;
  IF v_bad <> 0 THEN
    RAISE EXCEPTION 'Collection ledger contains non-archive-only mappings: %', v_bad;
  END IF;
  IF EXISTS (
    SELECT 1 FROM sw_property.source_dataset_archive a
    WHERE octet_length(a.compressed_payload) <> a.compressed_bytes
       OR length(a.source_sha256) <> 64
  ) THEN
    RAISE EXCEPTION 'Compressed archive length or SHA-256 verification failed';
  END IF;
  RAISE NOTICE 'BP04 archive-only acceptance passed: datasets %, collections %, source records %, archive bytes %, typed rows %',
    v_datasets, v_collections, v_source, v_archive_bytes, v_loaded;
END
$archive_only$;
