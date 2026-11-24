-- SW-DB-001 deterministic, disposable-only 9,500-person / 10,000-business fixture.
-- Run only after proposals 0002-0010 on a fresh PostgreSQL 16 disposable database.
-- The fixed manifest digest hashes the configuration described in SW-DB-001 run 0001.
\set ON_ERROR_STOP on
BEGIN;
SET LOCAL lock_timeout='10s';
SET LOCAL statement_timeout='20min';
SET LOCAL saltwater.source_revision TO :'source_revision';

DO $fixture_guard$
BEGIN
  IF current_database() <> 'saltwater_test' THEN
    RAISE EXCEPTION 'SW-DB-001 fixture is restricted to saltwater_test';
  END IF;
  IF current_setting('server_version_num')::integer / 10000 <> 16 THEN
    RAISE EXCEPTION 'SW-DB-001 fixture requires disposable PostgreSQL 16';
  END IF;
  IF length(current_setting('saltwater.source_revision')) NOT BETWEEN 7 AND 64 THEN
    RAISE EXCEPTION 'source revision must be supplied by the CI checkout';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM sw_runtime.state
    WHERE singleton=1 AND state IN (0,1) AND bootstrap_open=true
      AND world_tick=0 AND player_present=false
  ) THEN
    RAISE EXCEPTION 'world fixture requires stopped/ready bootstrap at tick zero';
  END IF;
END
$fixture_guard$;

CREATE SCHEMA IF NOT EXISTS sw_test;
CREATE OR REPLACE FUNCTION sw_test.synthetic_word(p_seed text)
RETURNS text LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE
AS $fixture_word$
  SELECT string_agg(
    (ARRAY['ba','be','bi','bo','bu','da','de','di',
           'do','du','ka','ke','ki','ko','ku','ra'])
      [strpos('0123456789abcdef',substr(md5(p_seed),g,1))],
    '' ORDER BY g
  )
  FROM generate_series(1,12) AS x(g)
$fixture_word$;

DO $
DECLARE
  v_manifest bytea := decode('0a5f0c1a1f692c33e392ab18d9f346b5d966022525c1f1d95b9e8e76b9e3d798','hex');
  v_revision text := current_setting('saltwater.source_revision');
  v_batch bigint;
  v_name_batch bigint;
  v_event bigint;
  v_person bigint;
  v_count integer;
  v_person_digest bytea;
  v_business_digest bytea;
BEGIN
  IF current_database() <> 'saltwater_test' THEN
    RAISE EXCEPTION 'SW-DB-001 fixture is restricted to saltwater_test; got %',current_database();
  END IF;
  IF current_setting('server_version_num')::integer / 10000 <> 16 THEN
    RAISE EXCEPTION 'SW-DB-001 fixture requires disposable PostgreSQL 16';
  END IF;
  IF v_revision IS NULL OR length(v_revision) NOT BETWEEN 7 AND 64 THEN
    RAISE EXCEPTION 'source revision must be supplied by the CI checkout';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM sw_runtime.state
    WHERE singleton=1 AND state IN (0,1) AND bootstrap_open=true
      AND world_tick=0 AND player_present=false
  ) THEN
    RAISE EXCEPTION 'world fixture requires stopped/ready bootstrap at tick zero';
  END IF;

  INSERT INTO sw_ops.world_provisioning_batch
    (manifest_sha256,generator_version,normalizer_version,config_version,seed,
     source_revision,expected_residents,expected_police_subset,
     expected_living_people,expected_businesses,source_ref,actor_ref,reason)
  VALUES
    (v_manifest,2,1,'saltwater-opening-fixture-v2',20261124,v_revision,
     9000,500,9500,10000,'SW-DB-001:opening-fixture-v2',
     'disposable-ci-generator','deterministic structural and capacity fixture')
  ON CONFLICT (manifest_sha256) DO NOTHING;

  SELECT batch_id INTO v_batch
  FROM sw_ops.world_provisioning_batch WHERE manifest_sha256=v_manifest;
  IF v_batch IS NULL OR NOT EXISTS (
    SELECT 1 FROM sw_ops.world_provisioning_batch
    WHERE batch_id=v_batch AND generator_version=2
      AND config_version='saltwater-opening-fixture-v1'
      AND seed=20261124 AND expected_residents=9000
      AND expected_police_subset=500 AND expected_living_people=9500
      AND expected_businesses=10000 AND source_revision=v_revision
      AND environment_scope='DISPOSABLE_TEST_ONLY'
  ) THEN
    RAISE EXCEPTION 'existing provisioning manifest metadata does not match this fixture';
  END IF;

  v_name_batch := sw_names.record_generation_batch(
    'BUSINESS',2::smallint,1::smallint,'saltwater-opening-fixture-v1',20261124,
    v_manifest,10000,'SW-DB-001:opening-fixture-v1',
    'disposable-ci-generator','business name fixture only; no production canon'
  );

  CREATE TABLE IF NOT EXISTS sw_test.person_cohort (
    fixture_person_key text PRIMARY KEY,
    batch_id bigint NOT NULL REFERENCES sw_ops.world_provisioning_batch(batch_id),
    person_id integer NOT NULL UNIQUE REFERENCES sw_people.person(person_id),
    cohort text NOT NULL CHECK (cohort IN ('RESIDENT','POLICE_SUBSET')),
    fixture_only boolean NOT NULL DEFAULT true CHECK (fixture_only)
  );
  CREATE TABLE IF NOT EXISTS sw_test.business_profile (
    business_id bigint PRIMARY KEY REFERENCES sw_business.business(business_id),
    test_sector_code text NOT NULL CHECK (test_sector_code IN
      ('TEST_TRADE','TEST_FOOD','TEST_MARITIME','TEST_FINANCE','TEST_REPAIR',
       'TEST_LOGISTICS','TEST_CULTURE','TEST_HEALTH','TEST_EDUCATION','TEST_SERVICES')),
    test_legal_form text NOT NULL CHECK (test_legal_form IN
      ('TEST_SOLE','TEST_PARTNERSHIP','TEST_COMPANY')),
    test_operating_basis text NOT NULL DEFAULT 'NON_GEOGRAPHIC_TEST_FIXTURE' CHECK (test_operating_basis='NON_GEOGRAPHIC_TEST_FIXTURE'),
    test_staff_band text NOT NULL CHECK (test_staff_band IN
      ('TEST_1_4','TEST_5_19','TEST_20_49','TEST_50_99','TEST_100_PLUS')),
    fixture_only boolean NOT NULL DEFAULT true CHECK (fixture_only)
  );

  UPDATE sw_runtime.state SET state=1
  WHERE singleton=1 AND state=0 AND bootstrap_open=true
    AND world_tick=0 AND player_present=false;

  INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,source_ref)
  SELECT et.event_type_id,transaction_timestamp(),0,
         'SW-DB-001:person-created:'||g
  FROM generate_series(1,9500) g
  CROSS JOIN sw_core.event_type et
  WHERE et.event_code='PERSON_CREATED'
    AND NOT EXISTS (
      SELECT 1 FROM sw_people.person p
      WHERE p.source_ref='SW-DB-001:person:'||g
    );

  INSERT INTO sw_people.person
    (given_name,family_name,created_tick,source_ref,last_event_id)
  SELECT sw_test.synthetic_word('given:'||g::text),
         sw_test.synthetic_word('family:'||g::text),
         0,'SW-DB-001:person:'||g,e.event_id
  FROM generate_series(1,9500) g
  JOIN sw_core.simulation_event e
    ON e.source_ref='SW-DB-001:person-created:'||g
  WHERE NOT EXISTS (
    SELECT 1 FROM sw_people.person p
    WHERE p.source_ref='SW-DB-001:person:'||g
  );

  INSERT INTO sw_core.simulation_event(event_type_id,occurred_at,world_tick,source_ref)
  SELECT et.event_type_id,transaction_timestamp(),0,
         'SW-DB-001:population-state:'||split_part(p.source_ref,':',3)
  FROM sw_people.person p
  CROSS JOIN sw_core.event_type et
  WHERE p.source_ref LIKE 'SW-DB-001:person:%'
    AND et.event_code='POPULATION_STATE_CHANGED'
    AND NOT EXISTS (
      SELECT 1 FROM sw_people.population_state ps
      WHERE ps.person_id=p.person_id
    );

  INSERT INTO sw_people.population_state
    (person_id,life_status,scope_status,effective_tick,last_event_id)
  SELECT p.person_id,1,1,0,e.event_id
  FROM sw_people.person p
  JOIN sw_core.simulation_event e
    ON e.source_ref='SW-DB-001:population-state:'||split_part(p.source_ref,':',3)
  WHERE p.source_ref LIKE 'SW-DB-001:person:%'
    AND NOT EXISTS (
      SELECT 1 FROM sw_people.population_state ps
      WHERE ps.person_id=p.person_id
    );

  INSERT INTO sw_test.person_cohort
    (fixture_person_key,batch_id,person_id,cohort)
  SELECT 'SWDB001-P-'||lpad(split_part(p.source_ref,':',3),5,'0'),
         v_batch,p.person_id,
         CASE WHEN split_part(p.source_ref,':',3)::integer<=9000
              THEN 'RESIDENT' ELSE 'POLICE_SUBSET' END
  FROM sw_people.person p
  JOIN sw_people.population_state ps USING (person_id)
  WHERE p.source_ref LIKE 'SW-DB-001:person:%'
  ON CONFLICT (fixture_person_key) DO NOTHING;

  SELECT count(*) INTO v_count FROM sw_test.person_cohort
  WHERE batch_id=v_batch;

  INSERT INTO sw_business.business
    (business_code,created_batch_id,operating_status,site_assignment_status,
     primary_spatial_id,created_tick,source_ref)
  SELECT 'SWB-FX-'||lpad(g::text,5,'0'),v_batch,'active','unassigned',
         NULL,0,'SW-DB-001:business:'||g
  FROM generate_series(1,10000) g
  ON CONFLICT (business_code) DO NOTHING;

  PERFORM sw_names.reserve_name(
    'BUSINESS',b.business_id,'canonical',
    sw_test.synthetic_word('business-name:'||b.business_code)||' Trading',
    'SW-DB-001:business-name:'||b.business_code,
    'disposable-ci-generator','unique deterministic test business identity',
    0,v_name_batch
  )
  FROM sw_business.business b
  WHERE b.created_batch_id=v_batch
  ORDER BY b.business_code;

  INSERT INTO sw_test.business_profile
    (business_id,test_sector_code,test_legal_form,test_operating_basis,test_staff_band)
  SELECT b.business_id,
         (ARRAY['TEST_TRADE','TEST_FOOD','TEST_MARITIME','TEST_FINANCE',
                'TEST_REPAIR','TEST_LOGISTICS','TEST_CULTURE','TEST_HEALTH',
                'TEST_EDUCATION','TEST_SERVICES'])[((row_number() OVER (ORDER BY b.business_code)-1)%10)+1],
         (ARRAY['TEST_SOLE','TEST_PARTNERSHIP','TEST_COMPANY'])[((row_number() OVER (ORDER BY b.business_code)-1)%3)+1],
         'NON_GEOGRAPHIC_TEST_FIXTURE',
         (ARRAY['TEST_1_4','TEST_5_19','TEST_20_49','TEST_50_99','TEST_100_PLUS'])[((row_number() OVER (ORDER BY b.business_code)-1)%5)+1]
  FROM sw_business.business b
  WHERE b.created_batch_id=v_batch
  ON CONFLICT (business_id) DO NOTHING;

  SELECT sw_ops.digest(
    convert_to(string_agg(
      concat_ws('|',c.fixture_person_key,c.batch_id::text,c.person_id::text,c.cohort,p.given_name,p.family_name,
                ps.life_status::text,ps.scope_status::text),
      E'\\n' ORDER BY c.fixture_person_key
    ),'UTF8'),'sha256')
  INTO v_person_digest
  FROM sw_test.person_cohort c
  JOIN sw_people.person p USING (person_id)
  JOIN sw_people.population_state ps USING (person_id)
  WHERE c.batch_id=v_batch;

  SELECT sw_ops.digest(
    convert_to(string_agg(
      concat_ws('|',b.business_id::text,b.business_code,b.created_batch_id::text,r.display_name,r.normalized_key,b.operating_status,
                b.site_assignment_status,coalesce(b.primary_spatial_id::text,''),
                p.test_sector_code,p.test_legal_form,p.test_operating_basis,p.test_staff_band),
      E'\\n' ORDER BY b.business_code
    ),'UTF8'),'sha256')
  INTO v_business_digest
  FROM sw_business.business b
  JOIN sw_names.name_reservation r
    ON r.entity_type='BUSINESS' AND r.entity_id=b.business_id
   AND r.name_form='canonical'
  JOIN sw_test.business_profile p USING (business_id)
  WHERE b.created_batch_id=v_batch;

  INSERT INTO sw_ops.provisioning_content_checksum
    (batch_id,entity_type,record_count,content_sha256)
  VALUES (v_batch,'PERSON',9500,v_person_digest),
         (v_batch,'BUSINESS',10000,v_business_digest)
  ON CONFLICT (batch_id,entity_type) DO NOTHING;

  IF NOT EXISTS (SELECT 1 FROM sw_ops.provisioning_content_checksum
                 WHERE batch_id=v_batch AND entity_type='PERSON'
                   AND record_count=9500 AND content_sha256=v_person_digest)
     OR NOT EXISTS (SELECT 1 FROM sw_ops.provisioning_content_checksum
                    WHERE batch_id=v_batch AND entity_type='BUSINESS'
                      AND record_count=10000 AND content_sha256=v_business_digest) THEN
    RAISE EXCEPTION 'same-manifest content checksum or record count changed';
  END IF;

  SELECT count(*) INTO v_count FROM sw_test.person_cohort
  WHERE batch_id=v_batch;
  IF v_count<>9500 THEN RAISE EXCEPTION 'person cohort count %, expected 9500',v_count; END IF;
  IF (SELECT count(*) FROM sw_test.person_cohort WHERE batch_id=v_batch AND cohort='RESIDENT')<>9000
     OR (SELECT count(*) FROM sw_test.person_cohort WHERE batch_id=v_batch AND cohort='POLICE_SUBSET')<>500 THEN
    RAISE EXCEPTION 'resident/police fixture cohorts do not reconcile';
  END IF;
  IF (SELECT living_included FROM sw_people.population_counter WHERE singleton=1)<>9500 THEN
    RAISE EXCEPTION 'population counter does not equal opening target 9500';
  END IF;
  IF (SELECT count(*) FROM sw_business.business WHERE created_batch_id=v_batch)<>10000
     OR (SELECT count(*) FROM sw_test.business_profile p
         JOIN sw_business.business b USING (business_id)
         WHERE b.created_batch_id=v_batch)<>10000 THEN
    RAISE EXCEPTION 'business identity/profile fixture does not reconcile to 10000';
  END IF;
  IF EXISTS (SELECT 1 FROM sw_business.business
             WHERE created_batch_id=v_batch
               AND (site_assignment_status<>'unassigned' OR primary_spatial_id IS NOT NULL)) THEN
    RAISE EXCEPTION 'fixture must not fabricate business geography';
  END IF;
  IF (SELECT count(*) FROM sw_names.name_reservation
      WHERE entity_type='BUSINESS')<>10000 THEN
    RAISE EXCEPTION 'business canonical names do not reconcile to 10000';
  END IF;
END
$$;
COMMIT;
