\set ON_ERROR_STOP on
DO $$
DECLARE
  v_datasets integer;
  v_collections integer;
  v_source_rows bigint;
  v_loaded bigint;
  v_daily integer;
  v_weekly integer;
  v_count bigint;
  v_status text;
BEGIN
  SELECT count(*) INTO v_datasets FROM sw_property.import_dataset;
  SELECT count(*), coalesce(sum(source_record_count),0), coalesce(sum(loaded_record_count),0)
    INTO v_collections, v_source_rows, v_loaded
  FROM sw_property.source_dataset_collection;
  IF v_datasets <> 14 THEN RAISE EXCEPTION 'expected 14 archived source datasets, found %', v_datasets; END IF;
  IF v_collections <> 105 THEN RAISE EXCEPTION 'expected 105 source collection ledger rows, found %', v_collections; END IF;
  IF v_source_rows <> 1950947 THEN RAISE EXCEPTION 'expected 1950947 source records, found %', v_source_rows; END IF;

  SELECT mapping_status, loaded_record_count INTO v_status, v_count
  FROM sw_property.source_dataset_collection
  WHERE dataset_id='SW-PROPERTY-WORLD-V1' AND collection_name='properties';
  IF v_status <> 'mapped' OR v_count <> 420 THEN
    RAISE EXCEPTION 'source collection identity mismatch for property-world properties: status %, loaded %', v_status, v_count;
  END IF;

  SELECT mapping_status, loaded_record_count INTO v_status, v_count
  FROM sw_property.import_dataset WHERE dataset_id='SW-BUSINESS-OPERATIONS-V1';
  IF v_status <> 'fully_mapped' OR v_count <> 80000 THEN
    RAISE EXCEPTION 'business operations source mapping mismatch: status %, loaded %', v_status, v_count;
  END IF;

  SELECT count(*) INTO v_daily FROM sw_property.business_daily_schedule;
  SELECT count(*) INTO v_weekly FROM sw_property.business_weekly_profile;
  IF v_daily <> 70000 OR v_weekly <> 10000 THEN
    RAISE EXCEPTION 'business operations row counts incorrect: daily %, weekly %', v_daily, v_weekly;
  END IF;

  IF EXISTS (
    SELECT 1 FROM sw_property.business_daily_schedule s
    LEFT JOIN sw_property.business b USING (business_id)
    LEFT JOIN sw_property.establishment e USING (establishment_id)
    WHERE b.business_id IS NULL OR e.establishment_id IS NULL
  ) THEN RAISE EXCEPTION 'business schedule cross-reference failure'; END IF;
END $$;
SELECT 'BP04 imported source ledger and business operations acceptance passed' AS result;
