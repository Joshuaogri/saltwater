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
INSERT INTO sw_property.organisation(organisation_id,display_name,organisation_type,registered_city,status,source_dataset)
VALUES ('SWTEST-ORG-NEW','Test Successor Property Owner','property_holding_company','Saltwater','active','bp04_agreement_lifecycle_acceptance');
INSERT INTO sw_property.ownership_interest(
 ownership_interest_id,property_id,owner_organisation_id,management_model,interest_type,source_dataset
) VALUES (
 'SWTEST-OWN-01','SWTEST-PROP-01','SWTEST-ORG-OWNER','direct_owner','freehold','bp04_agreement_lifecycle_acceptance'
);
INSERT INTO sw_property.property_title_register(
 title_register_id,property_id,current_ownership_interest_id,registered_proprietor_organisation_id,
 title_status,tenure_type,registration_tick,source_basis,boundary_record_id,
 active_dispute_count,unresolved_title_issue_count,source_dataset
) VALUES (
 'SWTEST-TITLE-01','SWTEST-PROP-01','SWTEST-OWN-01','SWTEST-ORG-OWNER',
 'registered_current','freehold',0,'test_fixture','SWTEST-BOUNDARY-01',0,0,
 'bp04_agreement_lifecycle_acceptance'
);
INSERT INTO sw_property.property_interest_record(
 property_interest_record_id,property_id,ownership_interest_id,interest_holder_organisation_id,
 interest_type,interest_status,priority_order,source_basis,source_dataset
) VALUES (
 'SWTEST-INTEREST-01','SWTEST-PROP-01','SWTEST-OWN-01','SWTEST-ORG-OWNER',
 'registered_ownership','current',1,'test_fixture','bp04_agreement_lifecycle_acceptance'
);
INSERT INTO sw_property.property_rights_schedule(
 property_rights_schedule_id,property_id,title_register_id,registered_ownership_interest_id,
 registered_owner_organisation_id,current_contractual_right_count,historical_contractual_right_count,
 right_class_coverage,unverified_right_classes,schedule_status,
 legal_search_required_before_disposition_or_works,source_dataset
) VALUES (
 'SWTEST-RIGHTS-SCHEDULE-01','SWTEST-PROP-01','SWTEST-TITLE-01','SWTEST-OWN-01',
 'SWTEST-ORG-OWNER',1,0,ARRAY['ownership','leasehold_or_occupancy']::text[],
 ARRAY['easement','wayleave']::text[],'test_fixture',true,
 'bp04_agreement_lifecycle_acceptance'
);
INSERT INTO sw_property.business_unit_link(
 business_unit_link_id,business_id,establishment_id,unit_id,premises_id,
 valid_from_tick,valid_to_tick,occupancy_relationship,occupancy_status,source_dataset
) VALUES (
 'SWTEST-LINK-PRIMARY','SWTEST-BUS-01','SWTEST-EST-01','SWTEST-UNIT-01','SWTEST-PREM-01',
 0,NULL,'primary_tenant','occupied','bp04_agreement_lifecycle_acceptance'
);
INSERT INTO sw_property.premises(
 premises_id,property_id,display_name,premises_use,lifecycle_status,source_dataset
) VALUES (
 'SWTEST-PREM-02','SWTEST-PROP-01','Test Handover Premises','commercial','active',
 'bp04_agreement_lifecycle_acceptance'
);
INSERT INTO sw_property.unit_space(
 unit_id,property_id,premises_id,display_name,unit_class,use_class,lifecycle_status,source_dataset
) VALUES (
 'SWTEST-UNIT-02','SWTEST-PROP-01','SWTEST-PREM-02','Test Handover Unit',
 'commercial','commercial','active','bp04_agreement_lifecycle_acceptance'
);
INSERT INTO sw_property.establishment(
 establishment_id,business_id,property_id,premises_id,unit_id,display_name,
 establishment_type,status,source_dataset
) VALUES
 ('SWTEST-EST-03','SWTEST-BUS-01','SWTEST-PROP-01','SWTEST-PREM-02','SWTEST-UNIT-02',
  'Handover Outgoing Establishment','primary','active','bp04_agreement_lifecycle_acceptance'),
 ('SWTEST-EST-04','SWTEST-BUS-02','SWTEST-PROP-01','SWTEST-PREM-02','SWTEST-UNIT-02',
  'Handover Incoming Establishment','primary','active','bp04_agreement_lifecycle_acceptance');
INSERT INTO sw_property.occupancy_agreement(
 agreement_id,property_id,premises_id,unit_id,landlord_organisation_id,
 tenant_business_id,operator_business_id,establishment_id,agreement_type,
 commencement_year,agreement_status,source_dataset
) VALUES
 ('SWTEST-AGR-06','SWTEST-PROP-01','SWTEST-PREM-02','SWTEST-UNIT-02','SWTEST-ORG-OWNER',
  'SWTEST-BUS-01','SWTEST-BUS-01','SWTEST-EST-03','commercial_occupancy_lease',
  2027,'active','bp04_agreement_lifecycle_acceptance'),
 ('SWTEST-AGR-07','SWTEST-PROP-01','SWTEST-PREM-02','SWTEST-UNIT-02','SWTEST-ORG-OWNER',
  'SWTEST-BUS-02','SWTEST-BUS-02','SWTEST-EST-04','commercial_occupancy_lease',
  2028,'active','bp04_agreement_lifecycle_acceptance');
INSERT INTO sw_property.occupancy(
 occupancy_id,property_id,premises_id,unit_id,occupant_business_id,
 establishment_id,agreement_id,occupant_type,occupancy_status,
 effective_from_year,effective_to_year,source_dataset
) VALUES (
 'SWTEST-OCC-04','SWTEST-PROP-01','SWTEST-PREM-02','SWTEST-UNIT-02',
 'SWTEST-BUS-01','SWTEST-EST-03','SWTEST-AGR-06','business','occupied',
 2027,NULL,'bp04_agreement_lifecycle_acceptance'
);
INSERT INTO sw_property.business_unit_link(
 business_unit_link_id,business_id,establishment_id,unit_id,premises_id,
 valid_from_tick,valid_to_tick,occupancy_relationship,occupancy_status,source_dataset
) VALUES (
 'SWTEST-LINK-HANDOVER-OLD','SWTEST-BUS-01','SWTEST-EST-03','SWTEST-UNIT-02','SWTEST-PREM-02',
 0,NULL,'primary_occupant','occupied','bp04_agreement_lifecycle_acceptance'
);


CREATE OR REPLACE FUNCTION sw_property.bp04_test_fail_handover_event_insert()
RETURNS trigger LANGUAGE plpgsql AS $test$
BEGIN
  IF NEW.source_ref='source:test:rollback' THEN
    RAISE EXCEPTION 'injected handover event insert failure';
  END IF;
  RETURN NEW;
END
$test$;
CREATE TRIGGER bp04_test_fail_handover_event_insert
BEFORE INSERT ON sw_property.occupancy_handover_event
FOR EACH ROW EXECUTE FUNCTION sw_property.bp04_test_fail_handover_event_insert();

DO $bp04$
DECLARE
  v_first uuid;
  v_replay uuid;
  v_status text;
  v_relationship text;
  v_transfer_event text;
  v_transfer_replay text;
  v_handover_event uuid;
  v_handover_replay uuid;
  v_handover_occupancy text;
  v_handover_link text;
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

  BEGIN
    PERFORM * FROM sw_property.handover_business_occupancy(
      'SWTEST-PROP-01','SWTEST-UNIT-01','SWTEST-OCC-02','SWTEST-AGR-04',
      'SWTEST-BUS-02',2028,6,6,'actor:test','source:test:handover',
      'test:handover:blocked-active-sublet','gameplay_action'
    );
    RAISE EXCEPTION 'physical handover proceeded during active subletting';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='physical handover proceeded during active subletting' THEN RAISE; END IF;
  END;
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

  UPDATE sw_property.occupancy_agreement
  SET operator_business_id='SWTEST-BUS-02'
  WHERE agreement_id='SWTEST-AGR-04';
  PERFORM * FROM sw_property.assign_occupancy_agreement_tenant(
    'SWTEST-AGR-04','SWTEST-BUS-01','SWTEST-BUS-02',7,7,
    'actor:test','source:test:assignment','test:assignment:1','gameplay_action'
  );
  IF (SELECT operator_business_id FROM sw_property.occupancy_agreement
      WHERE agreement_id='SWTEST-AGR-04')<>'SWTEST-BUS-02' THEN
    RAISE EXCEPTION 'assignment replay rewrote a later operator change';
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

  SELECT t.lifecycle_event_id INTO v_transfer_event
  FROM sw_property.transfer_property_ownership(
    'SWTEST-PROP-01','SWTEST-ORG-OWNER','SWTEST-ORG-NEW',
    8,8,2027,2027,'actor:test','source:test:title-transfer',
    'test:title-transfer:1','gameplay_action'
  ) t;
  SELECT t.lifecycle_event_id INTO v_transfer_replay
  FROM sw_property.transfer_property_ownership(
    'SWTEST-PROP-01','SWTEST-ORG-OWNER','SWTEST-ORG-NEW',
    8,8,2027,2027,'actor:test','source:test:title-transfer',
    'test:title-transfer:1','gameplay_action'
  ) t;
  IF v_transfer_event<>v_transfer_replay THEN
    RAISE EXCEPTION 'property ownership transfer replay did not return original lifecycle event';
  END IF;
  IF (SELECT owner_organisation_id FROM sw_property.ownership_interest
      WHERE ownership_interest_id='SWTEST-OWN-01')<>'SWTEST-ORG-NEW'
     OR (SELECT registered_proprietor_organisation_id FROM sw_property.property_title_register
         WHERE title_register_id='SWTEST-TITLE-01')<>'SWTEST-ORG-NEW'
     OR (SELECT interest_holder_organisation_id FROM sw_property.property_interest_record
         WHERE property_interest_record_id='SWTEST-INTEREST-01')<>'SWTEST-ORG-NEW'
     OR (SELECT registered_owner_organisation_id FROM sw_property.property_rights_schedule
         WHERE property_rights_schedule_id='SWTEST-RIGHTS-SCHEDULE-01')<>'SWTEST-ORG-NEW' THEN
    RAISE EXCEPTION 'property title/ownership projections were not transferred consistently';
  END IF;
  IF (SELECT landlord_organisation_id FROM sw_property.occupancy_agreement
      WHERE agreement_id='SWTEST-AGR-04')<>'SWTEST-ORG-OWNER'
     OR (SELECT tenant_business_id FROM sw_property.occupancy_agreement
         WHERE agreement_id='SWTEST-AGR-04')<>'SWTEST-BUS-02'
     OR (SELECT operator_business_id FROM sw_property.occupancy_agreement
         WHERE agreement_id='SWTEST-AGR-04')<>'SWTEST-BUS-02'
     OR (SELECT occupant_business_id FROM sw_property.occupancy
         WHERE occupancy_id='SWTEST-OCC-02')<>'SWTEST-BUS-01'
     OR (SELECT occupancy_status FROM sw_property.occupancy
         WHERE occupancy_id='SWTEST-OCC-02')<>'occupied'
     OR (SELECT business_id FROM sw_property.business_unit_link
         WHERE business_unit_link_id='SWTEST-LINK-PRIMARY')<>'SWTEST-BUS-01' THEN
    RAISE EXCEPTION 'property title transfer silently changed continuing tenancy or physical occupancy';
  END IF;
  IF (SELECT count(*) FROM sw_property.property_title_instrument
      WHERE ownership_event_id=v_transfer_event AND payment_or_settlement_record_created=false)<>1
     OR (SELECT count(*) FROM sw_property.property_transaction_index
         WHERE ownership_event_id=v_transfer_event AND financial_settlement_status='not_created_bp34')<>1
     OR (SELECT financial_transaction_created FROM sw_property.property_lifecycle_event
         WHERE lifecycle_event_id=v_transfer_event) IS DISTINCT FROM false THEN
    RAISE EXCEPTION 'ownership transfer created or omitted its non-financial title evidence';
  END IF;

  BEGIN
    UPDATE sw_property.property_lifecycle_event
    SET narrative='tampered'
    WHERE lifecycle_event_id=v_transfer_event;
    RAISE EXCEPTION 'property lifecycle event update was accepted';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='property lifecycle event update was accepted' THEN RAISE; END IF;
  END;

  -- The first unit still has a current subtenant occupancy. Exclusive handover
  -- must fail closed until that separate physical occupancy is explicitly ended.
  BEGIN
    PERFORM * FROM sw_property.handover_business_occupancy(
      'SWTEST-PROP-01','SWTEST-UNIT-01','SWTEST-OCC-02','SWTEST-AGR-04',
      'SWTEST-BUS-02',2028,9,9,'actor:test','source:test:handover',
      'test:handover:blocked-shared','gameplay_action'
    );
    RAISE EXCEPTION 'exclusive handover proceeded while a second occupant remained current';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='exclusive handover proceeded while a second occupant remained current' THEN RAISE; END IF;
  END;

  BEGIN
    PERFORM * FROM sw_property.handover_business_occupancy(
      'SWTEST-PROP-01','SWTEST-UNIT-02','SWTEST-OCC-04','SWTEST-AGR-07',
      'SWTEST-BUS-02',2028,9,9,'actor:test','source:test:rollback',
      'test:handover:rollback','gameplay_action'
    );
    RAISE EXCEPTION 'injected handover event failure did not abort the transaction';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='injected handover event failure did not abort the transaction' THEN RAISE; END IF;
    IF SQLERRM<>'injected handover event insert failure' THEN RAISE; END IF;
  END;
  IF (SELECT occupancy_status FROM sw_property.occupancy WHERE occupancy_id='SWTEST-OCC-04')<>'occupied'
     OR (SELECT effective_to_year FROM sw_property.occupancy WHERE occupancy_id='SWTEST-OCC-04') IS NOT NULL
     OR (SELECT valid_to_tick FROM sw_property.business_unit_link
         WHERE business_unit_link_id='SWTEST-LINK-HANDOVER-OLD') IS NOT NULL
     OR EXISTS (SELECT 1 FROM sw_property.occupancy
                WHERE unit_id='SWTEST-UNIT-02'
                  AND source_dataset='BP04-GAMEPLAY-OCCUPANCY-HANDOVER')
     OR EXISTS (SELECT 1 FROM sw_property.occupancy_handover_event
                WHERE property_id='SWTEST-PROP-01'
                  AND idempotency_key='test:handover:rollback') THEN
    RAISE EXCEPTION 'failed multi-record occupancy handover left partial state';
  END IF;

  SELECT h.handover_event_id,h.new_occupancy_id,h.new_business_unit_link_id
  INTO v_handover_event,v_handover_occupancy,v_handover_link
  FROM sw_property.handover_business_occupancy(
    'SWTEST-PROP-01','SWTEST-UNIT-02','SWTEST-OCC-04','SWTEST-AGR-07',
    'SWTEST-BUS-02',2028,9,9,'actor:test','source:test:handover',
    'test:handover:1','gameplay_action'
  ) h;
  SELECT h.handover_event_id INTO v_handover_replay
  FROM sw_property.handover_business_occupancy(
    'SWTEST-PROP-01','SWTEST-UNIT-02','SWTEST-OCC-04','SWTEST-AGR-07',
    'SWTEST-BUS-02',2028,9,9,'actor:test','source:test:handover',
    'test:handover:1','gameplay_action'
  ) h;
  IF v_handover_event<>v_handover_replay THEN
    RAISE EXCEPTION 'occupancy handover replay did not return original event';
  END IF;
  IF (SELECT occupancy_status FROM sw_property.occupancy WHERE occupancy_id='SWTEST-OCC-04')<>'vacated'
     OR (SELECT effective_to_year FROM sw_property.occupancy WHERE occupancy_id='SWTEST-OCC-04')<>2028
     OR (SELECT occupant_business_id FROM sw_property.occupancy WHERE occupancy_id=v_handover_occupancy)<>'SWTEST-BUS-02'
     OR (SELECT occupancy_status FROM sw_property.occupancy WHERE occupancy_id=v_handover_occupancy)<>'occupied'
     OR (SELECT business_id FROM sw_property.business_unit_link WHERE business_unit_link_id=v_handover_link)<>'SWTEST-BUS-02'
     OR (SELECT valid_to_tick FROM sw_property.business_unit_link WHERE business_unit_link_id='SWTEST-LINK-HANDOVER-OLD')<>9
     OR (SELECT valid_to_tick FROM sw_property.business_unit_link WHERE business_unit_link_id=v_handover_link) IS NOT NULL THEN
    RAISE EXCEPTION 'explicit occupancy handover did not close old and create new occupancy/link';
  END IF;
  IF (SELECT tenant_business_id FROM sw_property.occupancy_agreement WHERE agreement_id='SWTEST-AGR-06')<>'SWTEST-BUS-01'
     OR (SELECT tenant_business_id FROM sw_property.occupancy_agreement WHERE agreement_id='SWTEST-AGR-07')<>'SWTEST-BUS-02'
     OR (SELECT count(*) FROM sw_property.business_unit_link
         WHERE unit_id='SWTEST-UNIT-02' AND valid_to_tick IS NULL)<>1
     OR (SELECT count(*) FROM sw_property.occupancy_handover_event
         WHERE handover_event_id=v_handover_event)<>1 THEN
    RAISE EXCEPTION 'physical handover changed legal agreements or left duplicate primary links';
  END IF;
  BEGIN
    UPDATE sw_property.occupancy_handover_event
    SET event_payload='{}'::jsonb
    WHERE handover_event_id=v_handover_event;
    RAISE EXCEPTION 'occupancy handover event update was accepted';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='occupancy handover event update was accepted' THEN RAISE; END IF;
  END;
END
$bp04$;

DROP TRIGGER bp04_test_fail_handover_event_insert ON sw_property.occupancy_handover_event;
DROP FUNCTION sw_property.bp04_test_fail_handover_event_insert();

ROLLBACK;
SELECT 'BP04 agreement event history acceptance passed' AS result;
