\set ON_ERROR_STOP on
DO $bp04$
DECLARE
  v_count integer;
BEGIN
  SELECT count(*) INTO v_count
  FROM information_schema.tables
  WHERE table_schema='sw_property' AND table_type='BASE TABLE';
  IF v_count <> 85 THEN
    RAISE EXCEPTION 'expected 85 BP04 phase-1 through phase-9 tables, found %', v_count;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema='sw_property' AND table_name='property_site'
      AND column_name='source_dataset' AND data_type='text'
  ) OR NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema='sw_property' AND table_name='source_dataset_archive'
      AND column_name='compressed_payload' AND data_type='bytea'
  ) THEN RAISE EXCEPTION 'compressed source archive preservation missing'; END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns WHERE table_schema='sw_property' AND table_name='meter' AND column_name='reading_value' AND data_type='numeric'
  ) OR NOT EXISTS (
    SELECT 1 FROM information_schema.columns WHERE table_schema='sw_property' AND table_name='source_dataset_archive' AND column_name='compressed_payload' AND data_type='bytea'
  ) THEN RAISE EXCEPTION 'typed meter reading or compressed source archive missing'; END IF;

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
    SELECT 1 FROM information_schema.columns WHERE table_schema='sw_property' AND table_name='maintenance_work_order'
      AND column_name='verification_required' AND data_type='boolean'
  ) OR NOT EXISTS (
    SELECT 1 FROM information_schema.columns WHERE table_schema='sw_property' AND table_name='maintenance_defect'
      AND column_name='repair_urgency' AND data_type='text'
  ) OR NOT EXISTS (
    SELECT 1 FROM information_schema.columns WHERE table_schema='sw_property' AND table_name='equipment_replacement_forecast'
      AND column_name='financial_commitment_created' AND data_type='boolean'
  ) THEN RAISE EXCEPTION 'typed maintenance, repair or replacement fields missing'; END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE connamespace='sw_property'::regnamespace
      AND conname='maintenance_work_order_work_request_id_fkey' AND condeferrable
  ) THEN RAISE EXCEPTION 'maintenance work-order lineage foreign key missing'; END IF;


  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns WHERE table_schema='sw_property' AND table_name='security_door'
      AND column_name='access_point_id' AND data_type='text'
  ) OR NOT EXISTS (
    SELECT 1 FROM information_schema.columns WHERE table_schema='sw_property' AND table_name='access_zone'
      AND column_name='parent_zone_id' AND data_type='text'
  ) OR NOT EXISTS (
    SELECT 1 FROM information_schema.columns WHERE table_schema='sw_property' AND table_name='permission_zone_grant'
      AND column_name='grant_id' AND data_type='text'
  ) THEN RAISE EXCEPTION 'typed security door, zone or permission grant fields missing'; END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE connamespace='sw_property'::regnamespace
      AND conname='physical_key_no_person_credential' AND convalidated
  ) OR NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE connamespace='sw_property'::regnamespace
      AND conname='access_group_no_person_members' AND convalidated
  ) THEN RAISE EXCEPTION 'person credential exclusion checks missing'; END IF;


  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns WHERE table_schema='sw_property' AND table_name='asset_valuation'
      AND column_name='assessed_value_swc' AND data_type='bigint'
  ) OR NOT EXISTS (
    SELECT 1 FROM information_schema.columns WHERE table_schema='sw_property' AND table_name='insurance_policy'
      AND column_name='insurer_organisation_id' AND data_type='text'
  ) OR NOT EXISTS (
    SELECT 1 FROM information_schema.columns WHERE table_schema='sw_property' AND table_name='property_tax_assessment'
      AND column_name='assessment_status' AND data_type='text'
  ) THEN RAISE EXCEPTION 'typed valuation, insurance or tax fields missing'; END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE connamespace='sw_property'::regnamespace
      AND conname='asset_valuation_land_valuation_id_fkey' AND condeferrable
  ) OR NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE connamespace='sw_property'::regnamespace
      AND conname='insurance_coverage_insurance_policy_id_fkey' AND condeferrable
  ) THEN RAISE EXCEPTION 'valuation and insurance lineage foreign keys missing'; END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns WHERE table_schema='sw_property' AND table_name='lawful_use_certificate'
      AND column_name='lawful_use_class' AND data_type='text'
  ) OR NOT EXISTS (
    SELECT 1 FROM information_schema.columns WHERE table_schema='sw_property' AND table_name='building_inspection_schedule'
      AND column_name='inspection_visit_created' AND data_type='boolean'
  ) OR NOT EXISTS (
    SELECT 1 FROM information_schema.columns WHERE table_schema='sw_property' AND table_name='business_daily_schedule'
      AND column_name='customer_open_time' AND data_type='time without time zone'
  ) OR NOT EXISTS (
    SELECT 1 FROM information_schema.columns WHERE table_schema='sw_property' AND table_name='business_weekly_profile'
      AND column_name='has_continuous_service' AND data_type='boolean'
  ) THEN RAISE EXCEPTION 'typed business operating schedule fields missing'; END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns WHERE table_schema='sw_property' AND table_name='import_dataset'
      AND column_name='mapping_status' AND data_type='text'
  ) OR NOT EXISTS (
    SELECT 1 FROM information_schema.tables WHERE table_schema='sw_property'
      AND table_name='source_dataset_collection'
  ) THEN RAISE EXCEPTION 'source collection mapping ledger missing'; END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_schema='sw_property' AND table_name='import_release'
  ) OR NOT EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_schema='sw_property' AND table_name='import_dataset'
  ) THEN RAISE EXCEPTION 'import release ledger missing'; END IF;

  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='sw_property' AND table_name='property_title_register' AND column_name='registered_proprietor_organisation_id' AND data_type='text')
     OR NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='sw_property' AND table_name='property_transaction_index' AND column_name='ownership_event_id' AND data_type='text')
     OR NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='sw_property' AND table_name='premises_lifecycle_event' AND column_name='lawful_use_certificate_id' AND data_type='text')
  THEN RAISE EXCEPTION 'typed property title, transaction or lifecycle fields missing'; END IF;
END $bp04$;

SELECT 'BP04 phase-1 through phase-9 schema acceptance passed' AS result;
