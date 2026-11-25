\set ON_ERROR_STOP on
DO $$
DECLARE
  v_count integer;
BEGIN
  SELECT count(*) INTO v_count
  FROM information_schema.tables
  WHERE table_schema='sw_property' AND table_type='BASE TABLE';
  IF v_count <> 19 THEN
    RAISE EXCEPTION 'expected 19 BP04 phase-1 tables, found %', v_count;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema='sw_property' AND table_name='property_site'
      AND column_name='source_record' AND data_type='jsonb'
  ) THEN RAISE EXCEPTION 'property source-record preservation missing'; END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE connamespace='sw_property'::regnamespace
      AND conname='business_primary_establishment_fk' AND condeferrable
  ) THEN RAISE EXCEPTION 'business/establishment deferred relationship missing'; END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes
    WHERE schemaname='sw_property' AND indexname='business_unit_link_current_unit_uq'
  ) THEN RAISE EXCEPTION 'current business occupancy uniqueness missing'; END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_schema='sw_property' AND table_name='import_release'
  ) OR NOT EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_schema='sw_property' AND table_name='import_dataset'
  ) THEN RAISE EXCEPTION 'import release ledger missing'; END IF;
END $$;

SELECT 'BP04 phase-1 schema acceptance passed' AS result;
