-- Assertions run against a pg_restore copy of the opening SW-DB-001 fixture.
DO $$
DECLARE
  v_batch bigint;
BEGIN
  SELECT batch_id INTO v_batch FROM sw_ops.world_provisioning_batch
  WHERE config_version='saltwater-opening-fixture-v1';
  IF v_batch IS NULL THEN RAISE EXCEPTION 'restored provisioning manifest missing'; END IF;
  IF (SELECT count(*) FROM sw_people.person)<>9500
     OR (SELECT living_included FROM sw_people.population_counter WHERE singleton=1)<>9500
     OR (SELECT count(*) FROM sw_test.person_cohort WHERE batch_id=v_batch)<>9500 THEN
    RAISE EXCEPTION 'restored people/cohort/counter manifest mismatch';
  END IF;
  IF (SELECT count(*) FROM sw_test.person_cohort WHERE batch_id=v_batch AND cohort='RESIDENT')<>9000
     OR (SELECT count(*) FROM sw_test.person_cohort WHERE batch_id=v_batch AND cohort='POLICE_SUBSET')<>500 THEN
    RAISE EXCEPTION 'restored population cohorts mismatch';
  END IF;
  IF (SELECT count(*) FROM sw_business.business WHERE created_batch_id=v_batch)<>10000
     OR (SELECT count(*) FROM sw_business.business_history WHERE event_code='registered')<>10000
     OR (SELECT count(*) FROM sw_test.business_profile WHERE fixture_only)<>10000 THEN
    RAISE EXCEPTION 'restored business identity/history/profile mismatch';
  END IF;
  IF (SELECT count(*) FROM sw_names.name_reservation WHERE entity_type='BUSINESS')<>10000 THEN
    RAISE EXCEPTION 'restored business name registry mismatch';
  END IF;
  IF (SELECT encode(manifest_sha256,'hex') FROM sw_ops.world_provisioning_batch WHERE batch_id=v_batch)
     <>'9b8b4603031aa3516b6c18ae818b38ff6bbfa32a563da89bd70ab9b3537de348' THEN
    RAISE EXCEPTION 'restored manifest checksum mismatch';
  END IF;
  IF EXISTS (SELECT 1 FROM sw_business.business
             WHERE created_batch_id=v_batch AND primary_spatial_id IS NOT NULL) THEN
    RAISE EXCEPTION 'restored fixture unexpectedly contains geographic business assignments';
  END IF;
END
$$;
SELECT 'SW_DB_001_RESTORE_PASS' AS result;
