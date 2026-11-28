\set ON_ERROR_STOP on
BEGIN;

INSERT INTO sw_property.organisation(
  organisation_id,display_name,organisation_type,registered_city,status,source_dataset,source_record
) VALUES
  ('SWC22-LANDLORD','C22 Fictional Landlord','property_holding_company','Saltwater','active','bp04_occupancy_dispute_acceptance','{}'::jsonb),
  ('SWC22-CLAIMANT','C22 Fictional Claimant','property_holding_company','Saltwater','active','bp04_occupancy_dispute_acceptance','{}'::jsonb);

INSERT INTO sw_property.business(
  business_id,display_name,sector,primary_activity,status,source_dataset,source_record
) VALUES
  ('SWC22-TENANT','C22 Fictional Occupant','retail','shop','active','bp04_occupancy_dispute_acceptance','{}'::jsonb),
  ('SWC22-OTHER','C22 Other Occupant','retail','shop','active','bp04_occupancy_dispute_acceptance','{}'::jsonb);

INSERT INTO sw_property.property_site(
  property_id,display_name,use_class,lifecycle_status,source_dataset,source_record
) VALUES ('SWC22-PROPERTY','C22 Dispute Test Property','commercial','active','bp04_occupancy_dispute_acceptance','{}'::jsonb);

INSERT INTO sw_property.building(
  building_id,property_id,display_name,building_use,lifecycle_status,source_dataset,source_record
) VALUES ('SWC22-BUILDING','SWC22-PROPERTY','C22 Test Building','retail','active','bp04_occupancy_dispute_acceptance','{}'::jsonb);

INSERT INTO sw_property.premises(
  premises_id,property_id,building_id,display_name,premises_use,lifecycle_status,source_dataset,source_record
) VALUES
  ('SWC22-PREMISES-A','SWC22-PROPERTY','SWC22-BUILDING','C22 Unit A Premises','retail','active','bp04_occupancy_dispute_acceptance','{}'::jsonb),
  ('SWC22-PREMISES-B','SWC22-PROPERTY','SWC22-BUILDING','C22 Unit B Premises','retail','active','bp04_occupancy_dispute_acceptance','{}'::jsonb);

INSERT INTO sw_property.unit_space(
  unit_id,property_id,building_id,premises_id,display_name,unit_class,use_class,lifecycle_status,source_dataset,source_record
) VALUES
  ('SWC22-UNIT-A','SWC22-PROPERTY','SWC22-BUILDING','SWC22-PREMISES-A','C22 Unit A','shop','retail','active','bp04_occupancy_dispute_acceptance','{}'::jsonb),
  ('SWC22-UNIT-B','SWC22-PROPERTY','SWC22-BUILDING','SWC22-PREMISES-B','C22 Unit B','shop','retail','active','bp04_occupancy_dispute_acceptance','{}'::jsonb);

INSERT INTO sw_property.occupancy_agreement(
  agreement_id,property_id,building_id,premises_id,unit_id,landlord_organisation_id,
  tenant_business_id,agreement_type,commencement_year,expiry_year,agreement_status,
  source_dataset,source_record
) VALUES
  ('SWC22-AGREEMENT-A','SWC22-PROPERTY','SWC22-BUILDING','SWC22-PREMISES-A','SWC22-UNIT-A',
   'SWC22-LANDLORD','SWC22-TENANT','lease',2027,2030,'active','bp04_occupancy_dispute_acceptance','{}'::jsonb),
  ('SWC22-AGREEMENT-B','SWC22-PROPERTY','SWC22-BUILDING','SWC22-PREMISES-B','SWC22-UNIT-B',
   'SWC22-LANDLORD','SWC22-OTHER','lease',2027,2030,'active','bp04_occupancy_dispute_acceptance','{}'::jsonb);

INSERT INTO sw_property.occupancy(
  occupancy_id,property_id,building_id,premises_id,unit_id,occupant_business_id,
  agreement_id,occupant_type,occupancy_status,effective_from_year,effective_to_year,
  source_dataset,source_record
) VALUES
  ('SWC22-OCCUPANCY-A','SWC22-PROPERTY','SWC22-BUILDING','SWC22-PREMISES-A','SWC22-UNIT-A',
   'SWC22-TENANT','SWC22-AGREEMENT-A','business_tenant','current',2027,NULL,
   'bp04_occupancy_dispute_acceptance','{}'::jsonb),
  ('SWC22-OCCUPANCY-B','SWC22-PROPERTY','SWC22-BUILDING','SWC22-PREMISES-B','SWC22-UNIT-B',
   'SWC22-OTHER','SWC22-AGREEMENT-B','business_tenant','current',2027,NULL,
   'bp04_occupancy_dispute_acceptance','{}'::jsonb);

INSERT INTO sw_property.contractual_rights_index(
  property_right_id,property_id,building_id,premises_id,unit_id,right_type,
  holder_business_id,grantor_organisation_id,source_agreement_id,
  commencement_year,expiry_year,right_status,permitted_use,source_of_truth,
  new_legal_instrument_created,source_dataset
) VALUES
  ('SWC22-RIGHT-A','SWC22-PROPERTY','SWC22-BUILDING','SWC22-PREMISES-A','SWC22-UNIT-A',
   'consent_to_sublet','SWC22-TENANT','SWC22-LANDLORD','SWC22-AGREEMENT-A',
   2027,2030,'current','subject to recorded consent','generated_fixture',false,'bp04_occupancy_dispute_acceptance'),
  ('SWC22-RIGHT-B','SWC22-PROPERTY','SWC22-BUILDING','SWC22-PREMISES-B','SWC22-UNIT-B',
   'consent_to_sublet','SWC22-OTHER','SWC22-LANDLORD','SWC22-AGREEMENT-B',
   2027,2030,'current','subject to recorded consent','generated_fixture',false,'bp04_occupancy_dispute_acceptance');

DO $bp04$
DECLARE
  v_status text;
  v_event_count integer;
BEGIN
  SELECT dispute_status INTO v_status
  FROM sw_property.record_occupancy_dispute(
    'SWC22-DISPUTE-A','SWC22-OCCUPANCY-A',
    'SWC22-CLAIMANT',NULL,NULL,'SWC22-TENANT',
    'consent_revoked','Claim that consent to the tenant occupancy was revoked.',
    10,10,'npc:claims-officer','fixture:SWC22:consent-revoked',
    'SWC22:dispute:open:001','generated_fictional_canon',
    'SWC22-AGREEMENT-A','SWC22-RIGHT-A',NULL
  );
  IF v_status<>'open' THEN RAISE EXCEPTION 'new occupancy dispute did not open'; END IF;

  SELECT dispute_status INTO v_status
  FROM sw_property.record_occupancy_dispute(
    'SWC22-DISPUTE-A','SWC22-OCCUPANCY-A',
    'SWC22-CLAIMANT',NULL,NULL,'SWC22-TENANT',
    'consent_revoked','Claim that consent to the tenant occupancy was revoked.',
    10,10,'npc:claims-officer','fixture:SWC22:consent-revoked',
    'SWC22:dispute:open:001','generated_fictional_canon',
    'SWC22-AGREEMENT-A','SWC22-RIGHT-A',NULL
  );
  IF v_status<>'open' THEN RAISE EXCEPTION 'exact dispute replay was not idempotent'; END IF;

  BEGIN
    PERFORM * FROM sw_property.record_occupancy_dispute(
      'SWC22-DISPUTE-B','SWC22-OCCUPANCY-A',
      'SWC22-CLAIMANT',NULL,NULL,'SWC22-TENANT',
      'consent_revoked','Conflicting reuse of idempotency key.',
      10,10,'npc:claims-officer','fixture:SWC22:consent-revoked',
      'SWC22:dispute:open:001','generated_fictional_canon',
      'SWC22-AGREEMENT-A','SWC22-RIGHT-A',NULL
    );
    RAISE EXCEPTION 'conflicting dispute idempotency key reuse was accepted';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='conflicting dispute idempotency key reuse was accepted' THEN RAISE; END IF;
    IF SQLERRM NOT LIKE '%idempotency key conflicts with prior definition%' THEN RAISE; END IF;
  END;

  BEGIN
    PERFORM * FROM sw_property.record_occupancy_dispute(
      'SWC22-DISPUTE-WRONG-UNIT','SWC22-OCCUPANCY-A',
      'SWC22-CLAIMANT',NULL,NULL,'SWC22-TENANT',
      'consent_revoked','Wrong-unit right must fail closed.',
      11,11,'npc:claims-officer','fixture:SWC22:wrong-unit',
      'SWC22:dispute:wrong-unit','generated_fictional_canon',
      'SWC22-AGREEMENT-A','SWC22-RIGHT-B',NULL
    );
    RAISE EXCEPTION 'dispute accepted a contractual right from another unit';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='dispute accepted a contractual right from another unit' THEN RAISE; END IF;
    IF SQLERRM NOT LIKE '%must match the target occupancy property, unit and agreement%' THEN RAISE; END IF;
  END;

  IF (SELECT occupancy_status FROM sw_property.occupancy WHERE occupancy_id='SWC22-OCCUPANCY-A')<>'current'
     OR (SELECT agreement_status FROM sw_property.occupancy_agreement WHERE agreement_id='SWC22-AGREEMENT-A')<>'active'
     OR (SELECT right_status FROM sw_property.contractual_rights_index WHERE property_right_id='SWC22-RIGHT-A')<>'current' THEN
    RAISE EXCEPTION 'opening a dispute changed occupancy, agreement or contractual right state';
  END IF;

  SELECT dispute_status INTO v_status
  FROM sw_property.transition_occupancy_dispute(
    'SWC22-DISPUTE-A','open','upheld',20,20,
    'npc:dispute-adjudicator','fixture:SWC22:resolution',
    'SWC22:dispute:resolve:001','generated_fictional_canon',
    'NPC adjudicator upheld the consent-revocation claim.'
  );
  IF v_status<>'upheld' THEN RAISE EXCEPTION 'occupancy dispute was not resolved as upheld'; END IF;

  SELECT dispute_status INTO v_status
  FROM sw_property.transition_occupancy_dispute(
    'SWC22-DISPUTE-A','open','upheld',20,20,
    'npc:dispute-adjudicator','fixture:SWC22:resolution',
    'SWC22:dispute:resolve:001','generated_fictional_canon',
    'NPC adjudicator upheld the consent-revocation claim.'
  );
  IF v_status<>'upheld' THEN RAISE EXCEPTION 'exact dispute resolution replay was not idempotent'; END IF;

  SELECT count(*) INTO v_event_count
  FROM sw_property.occupancy_dispute_event WHERE dispute_id='SWC22-DISPUTE-A';
  IF v_event_count<>2 THEN RAISE EXCEPTION 'dispute event history should contain open and upheld events only'; END IF;

  IF (SELECT occupancy_status FROM sw_property.occupancy WHERE occupancy_id='SWC22-OCCUPANCY-A')<>'current'
     OR (SELECT agreement_status FROM sw_property.occupancy_agreement WHERE agreement_id='SWC22-AGREEMENT-A')<>'active'
     OR (SELECT right_status FROM sw_property.contractual_rights_index WHERE property_right_id='SWC22-RIGHT-A')<>'current' THEN
    RAISE EXCEPTION 'resolving a dispute silently changed occupancy, agreement or contractual right state';
  END IF;

  BEGIN
    UPDATE sw_property.occupancy_dispute
    SET claim_summary='tampered claim'
    WHERE dispute_id='SWC22-DISPUTE-A';
    RAISE EXCEPTION 'occupancy dispute claim details were mutable';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='occupancy dispute claim details were mutable' THEN RAISE; END IF;
    IF SQLERRM NOT LIKE '%controlled terminal transition only%' THEN RAISE; END IF;
  END;

  BEGIN
    DELETE FROM sw_property.occupancy_dispute_event
    WHERE dispute_id='SWC22-DISPUTE-A';
    RAISE EXCEPTION 'occupancy dispute event history was deletable';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='occupancy dispute event history was deletable' THEN RAISE; END IF;
    IF SQLERRM NOT LIKE '%append-only%' THEN RAISE; END IF;
  END;

  BEGIN
    PERFORM * FROM sw_property.transition_occupancy_dispute(
      'SWC22-DISPUTE-A','open','rejected',21,21,
      'npc:dispute-adjudicator','fixture:SWC22:reopen',
      'SWC22:dispute:reopen:001','generated_fictional_canon',
      'A closed dispute cannot be reopened.'
    );
    RAISE EXCEPTION 'terminal occupancy dispute was reopened';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='terminal occupancy dispute was reopened' THEN RAISE; END IF;
    IF SQLERRM NOT LIKE '%status conflict%' THEN RAISE; END IF;
  END;
END
$bp04$;

ROLLBACK;
SELECT 'BP04 occupancy dispute register acceptance passed' AS result;
