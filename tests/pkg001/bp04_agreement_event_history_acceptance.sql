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
    'test:renewal:1','gameplay_action',NULL,'SWTEST-AGR-02','{}'::jsonb
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
      'test:bad-renewal:1','gameplay_action',NULL,NULL,'{}'::jsonb
    );
    RAISE EXCEPTION 'renewal without a successor was accepted';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='renewal without a successor was accepted' THEN RAISE; END IF;
  END;
END
$bp04$;

INSERT INTO sw_property.occupancy_agreement(
 agreement_id,property_id,premises_id,unit_id,landlord_organisation_id,
 tenant_business_id,operator_business_id,establishment_id,agreement_type,
 commencement_year,agreement_status,source_dataset
) VALUES
 ('SWTEST-AGR-03','SWTEST-PROP-01','SWTEST-PREM-01','SWTEST-UNIT-01','SWTEST-ORG-OWNER',
  'SWTEST-BUS-01','SWTEST-BUS-01','SWTEST-EST-01','commercial_occupancy_lease',2026,'draft','bp04_agreement_lifecycle_acceptance'),
 ('SWTEST-AGR-04','SWTEST-PROP-01','SWTEST-PREM-01','SWTEST-UNIT-01','SWTEST-ORG-OWNER',
  'SWTEST-BUS-01','SWTEST-BUS-01','SWTEST-EST-01','commercial_occupancy_lease',2027,'draft','bp04_agreement_lifecycle_acceptance');

INSERT INTO sw_property.occupancy(
 occupancy_id,property_id,premises_id,unit_id,occupant_business_id,
 establishment_id,agreement_id,occupant_type,occupancy_status,
 effective_from_year,effective_to_year,source_dataset
) VALUES (
 'SWTEST-OCC-01','SWTEST-PROP-01','SWTEST-PREM-01','SWTEST-UNIT-01',
 'SWTEST-BUS-01','SWTEST-EST-01','SWTEST-AGR-01','business','occupied',
 2025,NULL,'bp04_agreement_lifecycle_acceptance'
);

INSERT INTO sw_property.business(business_id,display_name,sector,status,source_dataset)
VALUES ('SWTEST-BUS-02','Test Subtenant','professional_services','active','bp04_agreement_lifecycle_acceptance');
INSERT INTO sw_property.establishment(establishment_id,business_id,property_id,premises_id,unit_id,display_name,establishment_type,status,source_dataset)
VALUES ('SWTEST-EST-02','SWTEST-BUS-02','SWTEST-PROP-01','SWTEST-PREM-01','SWTEST-UNIT-01','Test Subtenant Establishment','secondary','active','bp04_agreement_lifecycle_acceptance');
INSERT INTO sw_property.occupancy_agreement(
 agreement_id,property_id,premises_id,unit_id,tenant_business_id,
 operator_business_id,establishment_id,agreement_type,commencement_year,
 agreement_status,source_dataset
) VALUES (
 'SWTEST-AGR-05','SWTEST-PROP-01','SWTEST-PREM-01','SWTEST-UNIT-01',
 'SWTEST-BUS-02','SWTEST-BUS-02','SWTEST-EST-02','sublease',2027,'active',
 'bp04_agreement_lifecycle_acceptance'
);
INSERT INTO sw_property.occupancy(
 occupancy_id,property_id,premises_id,unit_id,occupant_business_id,
 establishment_id,agreement_id,occupant_type,occupancy_status,
 effective_from_year,effective_to_year,source_dataset
) VALUES
 ('SWTEST-OCC-02','SWTEST-PROP-01','SWTEST-PREM-01','SWTEST-UNIT-01',
  'SWTEST-BUS-01','SWTEST-EST-01','SWTEST-AGR-04','business','occupied',
  2027,NULL,'bp04_agreement_lifecycle_acceptance'),
 ('SWTEST-OCC-03','SWTEST-PROP-01','SWTEST-PREM-01','SWTEST-UNIT-01',
  'SWTEST-BUS-02','SWTEST-EST-02','SWTEST-AGR-05','business_subtenant','occupied',
  2027,NULL,'bp04_agreement_lifecycle_acceptance');
INSERT INTO sw_property.contractual_rights_index(
 property_right_id,property_id,premises_id,unit_id,right_type,holder_business_id,
 source_agreement_id,commencement_year,right_status,permitted_use,source_of_truth,
 new_legal_instrument_created,source_dataset
) VALUES (
 'SWTEST-RIGHT-SUBLET-01','SWTEST-PROP-01','SWTEST-PREM-01','SWTEST-UNIT-01',
 'subletting','SWTEST-BUS-01','SWTEST-AGR-04',2027,'current','commercial',
 'bp04_agreement_lifecycle_acceptance',false,'bp04_agreement_lifecycle_acceptance'
);
INSERT INTO sw_property.contractual_rights_index(
 property_right_id,property_id,premises_id,unit_id,right_type,holder_business_id,
 source_agreement_id,commencement_year,right_status,permitted_use,source_of_truth,
 new_legal_instrument_created,source_dataset
) VALUES (
 'SWTEST-RIGHT-LEASE-01','SWTEST-PROP-01','SWTEST-PREM-01','SWTEST-UNIT-01',
 'contractual_lease_licence_or_concession','SWTEST-BUS-01','SWTEST-AGR-04',2027,'current','commercial',
 'bp04_agreement_lifecycle_acceptance',false,'bp04_agreement_lifecycle_acceptance'
);
INSERT INTO sw_property.business_unit_link(
 business_unit_link_id,business_id,establishment_id,unit_id,premises_id,
 valid_from_tick,valid_to_tick,occupancy_relationship,occupancy_status,source_dataset
) VALUES (
 'SWTEST-LINK-PRIMARY','SWTEST-BUS-01','SWTEST-EST-01','SWTEST-UNIT-01','SWTEST-PREM-01',
 0,NULL,'primary_tenant','occupied','bp04_agreement_lifecycle_acceptance'
);

DO $bp04$
DECLARE
  v_first uuid;
  v_replay uuid;
  v_status text;
  v_relationship text;
BEGIN
  SELECT t.agreement_event_id INTO v_first
  FROM sw_property.transition_occupancy_agreement(
    'SWTEST-AGR-03','agreement_executed','draft',1,1,'actor:test','source:test:execute',
    'test:transition:execute','gameplay_action',NULL,'{}'::jsonb
  ) t;
  SELECT t.agreement_event_id INTO v_replay
  FROM sw_property.transition_occupancy_agreement(
    'SWTEST-AGR-03','agreement_executed','draft',1,1,'actor:test','source:test:execute',
    'test:transition:execute','gameplay_action',NULL,'{}'::jsonb
  ) t;
  IF v_first<>v_replay THEN RAISE EXCEPTION 'transition replay did not return original event'; END IF;
  IF (SELECT agreement_status FROM sw_property.occupancy_agreement WHERE agreement_id='SWTEST-AGR-03')<>'active' THEN
    RAISE EXCEPTION 'execution did not activate the agreement';
  END IF;

  PERFORM * FROM sw_property.transition_occupancy_agreement(
    'SWTEST-AGR-03','agreement_varied','active',2,2,'actor:test','source:test:variation',
    'test:transition:variation','gameplay_action',NULL,'{"rent_band":"B3"}'::jsonb
  );
  PERFORM * FROM sw_property.transition_occupancy_agreement(
    'SWTEST-AGR-03','agreement_renewed','active',3,3,'actor:test','source:test:renewal',
    'test:transition:renewal','gameplay_action','SWTEST-AGR-04','{}'::jsonb
  );
  IF (SELECT agreement_status FROM sw_property.occupancy_agreement WHERE agreement_id='SWTEST-AGR-03')<>'renewed'
     OR (SELECT agreement_status FROM sw_property.occupancy_agreement WHERE agreement_id='SWTEST-AGR-04')<>'active' THEN
    RAISE EXCEPTION 'renewal did not close predecessor and activate successor';
  END IF;

  SELECT t.agreement_status INTO v_status
  FROM sw_property.transition_occupancy_agreement(
    'SWTEST-AGR-01','agreement_expired','active',30,30,'actor:test','source:test:expiry',
    'test:transition:expiry','gameplay_action',NULL,'{}'::jsonb
  ) t;
  IF v_status<>'expired' THEN RAISE EXCEPTION 'expiry transition did not return expired state'; END IF;
  IF (SELECT occupancy_status FROM sw_property.occupancy WHERE occupancy_id='SWTEST-OCC-01')<>'occupied'
     OR (SELECT effective_to_year FROM sw_property.occupancy WHERE occupancy_id='SWTEST-OCC-01') IS NOT NULL THEN
    RAISE EXCEPTION 'agreement expiry automatically changed physical occupancy';
  END IF;

  BEGIN
    PERFORM * FROM sw_property.transition_occupancy_agreement(
      'SWTEST-AGR-01','agreement_varied','active',31,31,'actor:test','source:test:bad',
      'test:transition:bad-state','gameplay_action',NULL,'{}'::jsonb
    );
    RAISE EXCEPTION 'transition accepted an incorrect expected state';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='transition accepted an incorrect expected state' THEN RAISE; END IF;
  END;

  PERFORM * FROM sw_property.transition_occupancy_agreement(
    'SWTEST-AGR-03','agreement_renewed','active',3,3,'actor:test','source:test:renewal',
    'test:transition:renewal','gameplay_action','SWTEST-AGR-04','{}'::jsonb
  );
  IF (SELECT count(*) FROM sw_property.occupancy_agreement_event
      WHERE agreement_id='SWTEST-AGR-03' AND idempotency_key='test:transition:renewal')<>1 THEN
    RAISE EXCEPTION 'renewal replay created duplicate events';
  END IF;

  SELECT r.relationship_id INTO v_relationship
  FROM sw_property.record_subletting_relationship(
    'SWTEST-REL-01','SWTEST-AGR-04','SWTEST-AGR-05',
    'SWTEST-OCC-02','SWTEST-OCC-03','SWTEST-RIGHT-SUBLET-01',
    5,5,'actor:test','source:test:sublet','test:sublet:start'
  ) r;
  PERFORM * FROM sw_property.record_subletting_relationship(
    'SWTEST-REL-01','SWTEST-AGR-04','SWTEST-AGR-05',
    'SWTEST-OCC-02','SWTEST-OCC-03','SWTEST-RIGHT-SUBLET-01',
    5,5,'actor:test','source:test:sublet','test:sublet:start'
  );
  IF (SELECT count(*) FROM sw_property.business_unit_link
      WHERE unit_id='SWTEST-UNIT-01' AND valid_to_tick IS NULL)<>1 THEN
    RAISE EXCEPTION 'subletting created a second primary business-unit link';
  END IF;

  BEGIN
    PERFORM * FROM sw_property.assign_occupancy_agreement_tenant(
      'SWTEST-AGR-04','SWTEST-BUS-01','SWTEST-BUS-02',6,6,
      'actor:test','source:test:assignment','test:assignment:blocked','gameplay_action'
    );
    RAISE EXCEPTION 'assignment proceeded while a subletting relationship was active';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='assignment proceeded while a subletting relationship was active' THEN RAISE; END IF;
  END;

  PERFORM * FROM sw_property.end_subletting_relationship(
    'SWTEST-REL-01',6,6,'actor:test','source:test:sublet-end','test:sublet:end'
  );
  PERFORM * FROM sw_property.end_subletting_relationship(
    'SWTEST-REL-01',6,6,'actor:test','source:test:sublet-end','test:sublet:end'
  );
  IF (SELECT relationship_status FROM sw_property.occupancy_relationship
      WHERE relationship_id='SWTEST-REL-01')<>'ended' THEN
    RAISE EXCEPTION 'subletting relationship was not ended';
  END IF;
  IF (SELECT occupancy_status FROM sw_property.occupancy WHERE occupancy_id='SWTEST-OCC-03')<>'occupied'
     OR (SELECT effective_to_year FROM sw_property.occupancy WHERE occupancy_id='SWTEST-OCC-03') IS NOT NULL THEN
    RAISE EXCEPTION 'ending subletting automatically evicted the physical occupant';
  END IF;

  BEGIN
    PERFORM * FROM sw_property.record_subletting_relationship(
      'SWTEST-REL-NORIGHT','SWTEST-AGR-04','SWTEST-AGR-05',
      'SWTEST-OCC-02','SWTEST-OCC-03','SWTEST-RIGHT-MISSING',
      7,7,'actor:test','source:test:sublet','test:sublet:no-right'
    );
    RAISE EXCEPTION 'subletting without an explicit right was accepted';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='subletting without an explicit right was accepted' THEN RAISE; END IF;
  END;

  BEGIN
    INSERT INTO sw_property.business_unit_link(
      business_unit_link_id,business_id,establishment_id,unit_id,premises_id,
      valid_from_tick,occupancy_relationship,occupancy_status,source_dataset
    ) VALUES (
      'SWTEST-LINK-SUB','SWTEST-BUS-02','SWTEST-EST-02','SWTEST-UNIT-01','SWTEST-PREM-01',
      5,'primary_tenant','occupied','bp04_agreement_lifecycle_acceptance'
    );
    RAISE EXCEPTION 'second current primary unit link was accepted';
  EXCEPTION WHEN unique_violation THEN
    NULL;
  END;

  PERFORM * FROM sw_property.assign_occupancy_agreement_tenant(
    'SWTEST-AGR-04','SWTEST-BUS-01','SWTEST-BUS-02',7,7,
    'actor:test','source:test:assignment','test:assignment:1','gameplay_action'
  );
  PERFORM * FROM sw_property.assign_occupancy_agreement_tenant(
    'SWTEST-AGR-04','SWTEST-BUS-01','SWTEST-BUS-02',7,7,
    'actor:test','source:test:assignment','test:assignment:1','gameplay_action'
  );
  IF (SELECT tenant_business_id FROM sw_property.occupancy_agreement
      WHERE agreement_id='SWTEST-AGR-04')<>'SWTEST-BUS-02'
     OR (SELECT operator_business_id FROM sw_property.occupancy_agreement
         WHERE agreement_id='SWTEST-AGR-04')<>'SWTEST-BUS-01' THEN
    RAISE EXCEPTION 'assignment did not preserve separate operator identity';
  END IF;
  IF (SELECT occupant_business_id FROM sw_property.occupancy
      WHERE occupancy_id='SWTEST-OCC-02')<>'SWTEST-BUS-01'
     OR (SELECT business_id FROM sw_property.business_unit_link
         WHERE business_unit_link_id='SWTEST-LINK-PRIMARY')<>'SWTEST-BUS-01' THEN
    RAISE EXCEPTION 'legal assignment silently changed physical occupancy or primary unit link';
  END IF;
  IF (SELECT holder_business_id FROM sw_property.contractual_rights_index
      WHERE property_right_id='SWTEST-RIGHT-LEASE-01')<>'SWTEST-BUS-02'
     OR (SELECT right_status FROM sw_property.contractual_rights_index
         WHERE property_right_id='SWTEST-RIGHT-SUBLET-01')<>'historical_expired' THEN
    RAISE EXCEPTION 'assignment did not update contractual right holder or expire former tenant subletting permission';
  END IF;
  IF (SELECT count(*) FROM sw_property.occupancy_agreement_event
      WHERE agreement_id='SWTEST-AGR-04' AND idempotency_key='test:assignment:1')<>1 THEN
    RAISE EXCEPTION 'assignment replay created duplicate events';
  END IF;
END
$bp04$;

ROLLBACK;
SELECT 'BP04 agreement event history acceptance passed' AS result;
