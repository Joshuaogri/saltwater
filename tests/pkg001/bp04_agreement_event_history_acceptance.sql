\set ON_ERROR_STOP on
BEGIN;

INSERT INTO sw_property.organisation(organisation_id,display_name,organisation_type,registered_city,status,source_dataset)
VALUES ('SWTEST-ORG-OWNER','Test Property Owner','property_holding_company','Saltwater','active','bp04_agreement_lifecycle_acceptance');
INSERT INTO sw_property.property_site(property_id,display_name,use_class,lifecycle_status,source_dataset)
VALUES ('SWTEST-PROP-01','Test Agreement Property','commercial','active','bp04_agreement_lifecycle_acceptance');
INSERT INTO sw_property.premises(premises_id,property_id,display_name,premises_use,lifecycle_status,source_dataset)
VALUES ('SWTEST-PREM-01','SWTEST-PROP-01','Test Premises','commercial','active','bp04_agreement_lifecycle_acceptance');
INSERT INTO sw_property.unit_space(unit_id,property_id,premises_id,display_name,unit_class,use_class,lifecycle_status,source_dataset)
VALUES ('SWTEST-UNIT-01','SWTEST-PROP-01','SWTEST-PREM-01','Test Unit','commercial','commercial','active','bp04_agreement_lifecycle_acceptance');
INSERT INTO sw_property.business(business_id,display_name,sector,status,source_dataset)
VALUES ('SWTEST-BUS-01','Test Tenant','professional_services','active','bp04_agreement_lifecycle_acceptance');
INSERT INTO sw_property.establishment(establishment_id,business_id,property_id,premises_id,unit_id,display_name,establishment_type,status,source_dataset)
VALUES ('SWTEST-EST-01','SWTEST-BUS-01','SWTEST-PROP-01','SWTEST-PREM-01','SWTEST-UNIT-01','Test Establishment','primary','active','bp04_agreement_lifecycle_acceptance');
INSERT INTO sw_property.occupancy_agreement(
 agreement_id,property_id,premises_id,unit_id,landlord_organisation_id,
 tenant_business_id,operator_business_id,establishment_id,agreement_type,
 commencement_year,agreement_status,source_dataset
) VALUES
 ('SWTEST-AGR-01','SWTEST-PROP-01','SWTEST-PREM-01','SWTEST-UNIT-01','SWTEST-ORG-OWNER',
  'SWTEST-BUS-01','SWTEST-BUS-01','SWTEST-EST-01','commercial_occupancy_lease',2025,'active','bp04_agreement_lifecycle_acceptance'),
 ('SWTEST-AGR-02','SWTEST-PROP-01','SWTEST-PREM-01','SWTEST-UNIT-01','SWTEST-ORG-OWNER',
  'SWTEST-BUS-01','SWTEST-BUS-01','SWTEST-EST-01','commercial_occupancy_lease',2026,'active','bp04_agreement_lifecycle_acceptance');

DO $bp04$
DECLARE
  first_id uuid;
  replay_id uuid;
BEGIN
  first_id := sw_property.append_occupancy_agreement_event(
    'SWTEST-AGR-01','agreement_executed',10,10,'actor:test','source:test:execution',
    'test:execution:1','source_documented',NULL,NULL,'{"execution_date_status":"not_recorded"}'::jsonb
  );
  replay_id := sw_property.append_occupancy_agreement_event(
    'SWTEST-AGR-01','agreement_executed',10,10,'actor:test','source:test:execution',
    'test:execution:1','source_documented',NULL,NULL,'{"execution_date_status":"not_recorded"}'::jsonb
  );
  IF first_id<>replay_id THEN RAISE EXCEPTION 'idempotent replay did not return the original event'; END IF;

  PERFORM sw_property.append_occupancy_agreement_event(
    'SWTEST-AGR-01','agreement_renewed',20,20,'actor:test','source:test:renewal',
    'test:renewal:1','gameplay_action','SWTEST-AGR-01','SWTEST-AGR-02','{}'::jsonb
  );
  IF (SELECT count(*) FROM sw_property.occupancy_agreement_event WHERE agreement_id='SWTEST-AGR-01')<>2 THEN
    RAISE EXCEPTION 'agreement event history count is incorrect';
  END IF;
  IF (SELECT agreement_status FROM sw_property.occupancy_agreement WHERE agreement_id='SWTEST-AGR-01')<>'active' THEN
    RAISE EXCEPTION 'append-only event intake unexpectedly mutated the agreement projection';
  END IF;

  BEGIN
    PERFORM sw_property.append_occupancy_agreement_event(
      'SWTEST-AGR-01','agreement_varied',10,21,'actor:test','source:test:variation',
      'test:backwards:1','gameplay_action',NULL,NULL,'{}'::jsonb
    );
    RAISE EXCEPTION 'backwards effective tick was accepted';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='backwards effective tick was accepted' THEN RAISE; END IF;
  END;

  BEGIN
    PERFORM sw_property.append_occupancy_agreement_event(
      'SWTEST-AGR-01','agreement_executed',10,10,'actor:other','source:test:execution',
      'test:execution:1','source_documented',NULL,NULL,'{}'::jsonb
    );
    RAISE EXCEPTION 'conflicting idempotency replay was accepted';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='conflicting idempotency replay was accepted' THEN RAISE; END IF;
  END;

  BEGIN
    UPDATE sw_property.occupancy_agreement_event
    SET event_type='agreement_varied'
    WHERE agreement_id='SWTEST-AGR-01';
    RAISE EXCEPTION 'event update was accepted';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='event update was accepted' THEN RAISE; END IF;
  END;

  BEGIN
    DELETE FROM sw_property.occupancy_agreement_event WHERE agreement_id='SWTEST-AGR-01';
    RAISE EXCEPTION 'event deletion was accepted';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='event deletion was accepted' THEN RAISE; END IF;
  END;

  BEGIN
    PERFORM sw_property.append_occupancy_agreement_event(
      'SWTEST-AGR-01','agreement_renewed',30,30,'actor:test','source:test:bad-renewal',
      'test:bad-renewal:1','gameplay_action',NULL,'SWTEST-AGR-02','{}'::jsonb
    );
    RAISE EXCEPTION 'renewal without matching predecessor was accepted';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='renewal without matching predecessor was accepted' THEN RAISE; END IF;
  END;
END
$bp04$;

ROLLBACK;
SELECT 'BP04 agreement event history acceptance passed' AS result;
