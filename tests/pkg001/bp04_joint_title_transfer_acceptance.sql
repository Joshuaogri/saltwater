\set ON_ERROR_STOP on
BEGIN;

INSERT INTO sw_property.organisation(
  organisation_id,display_name,organisation_type,registered_city,status,source_dataset
) VALUES
  ('SWC23-OWNER-A','C23 Joint Owner A','property_holding_company','Saltwater','active','bp04_joint_title_transfer_acceptance'),
  ('SWC23-OWNER-B','C23 Joint Owner B','property_holding_company','Saltwater','active','bp04_joint_title_transfer_acceptance'),
  ('SWC23-BUYER-A','C23 Incoming Owner A','property_holding_company','Saltwater','active','bp04_joint_title_transfer_acceptance'),
  ('SWC23-BUYER-B','C23 Incoming Owner B','property_holding_company','Saltwater','active','bp04_joint_title_transfer_acceptance'),
  ('SWC23-LANDLORD','C23 Continuing Landlord','property_holding_company','Saltwater','active','bp04_joint_title_transfer_acceptance');

INSERT INTO sw_property.business(
  business_id,display_name,sector,primary_activity,status,source_dataset
) VALUES ('SWC23-TENANT','C23 Continuing Tenant','retail','shop','active','bp04_joint_title_transfer_acceptance');

INSERT INTO sw_property.property_site(
  property_id,display_name,use_class,lifecycle_status,source_dataset
) VALUES ('SWC23-PROPERTY','C23 Joint Transfer Property','commercial','active','bp04_joint_title_transfer_acceptance');

INSERT INTO sw_property.building(
  building_id,property_id,display_name,building_use,lifecycle_status,source_dataset
) VALUES ('SWC23-BUILDING','SWC23-PROPERTY','C23 Building','retail','active','bp04_joint_title_transfer_acceptance');

INSERT INTO sw_property.premises(
  premises_id,property_id,building_id,display_name,premises_use,lifecycle_status,source_dataset
) VALUES ('SWC23-PREMISES','SWC23-PROPERTY','SWC23-BUILDING','C23 Premises','retail','active','bp04_joint_title_transfer_acceptance');

INSERT INTO sw_property.unit_space(
  unit_id,property_id,building_id,premises_id,display_name,unit_class,use_class,lifecycle_status,source_dataset
) VALUES ('SWC23-UNIT','SWC23-PROPERTY','SWC23-BUILDING','SWC23-PREMISES','C23 Unit','shop','retail','active','bp04_joint_title_transfer_acceptance');

INSERT INTO sw_property.occupancy_agreement(
  agreement_id,property_id,building_id,premises_id,unit_id,landlord_organisation_id,
  tenant_business_id,agreement_type,commencement_year,expiry_year,agreement_status,source_dataset
) VALUES (
  'SWC23-AGREEMENT','SWC23-PROPERTY','SWC23-BUILDING','SWC23-PREMISES','SWC23-UNIT',
  'SWC23-LANDLORD','SWC23-TENANT','lease',2027,2030,'active','bp04_joint_title_transfer_acceptance'
);

INSERT INTO sw_property.occupancy(
  occupancy_id,property_id,building_id,premises_id,unit_id,occupant_business_id,
  agreement_id,occupant_type,occupancy_status,effective_from_year,effective_to_year,source_dataset
) VALUES (
  'SWC23-OCCUPANCY','SWC23-PROPERTY','SWC23-BUILDING','SWC23-PREMISES','SWC23-UNIT',
  'SWC23-TENANT','SWC23-AGREEMENT','business_tenant','current',2027,NULL,
  'bp04_joint_title_transfer_acceptance'
);

INSERT INTO sw_property.ownership_interest(
  ownership_interest_id,property_id,owner_organisation_id,management_model,interest_type,
  source_dataset,interest_class,share_numerator,share_denominator,effective_from_tick,
  effective_to_tick,interest_status,dispute_status,dispute_reference,recorded_tick
) VALUES
  ('SWC23-INTEREST-A','SWC23-PROPERTY','SWC23-OWNER-A','direct_owner_management','freehold',
   'bp04_joint_title_transfer_acceptance','registered_ownership',1,2,0,NULL,'current','undisputed',NULL,0),
  ('SWC23-INTEREST-B','SWC23-PROPERTY','SWC23-OWNER-B','third_party_management','freehold',
   'bp04_joint_title_transfer_acceptance','registered_ownership',1,2,0,NULL,'current','undisputed',NULL,0);

INSERT INTO sw_property.property_title_register(
  title_register_id,property_id,current_ownership_interest_id,
  registered_proprietor_organisation_id,title_status,tenure_type,
  registration_tick,source_basis,boundary_record_id,active_dispute_count,
  unresolved_title_issue_count,source_dataset
) VALUES (
  'SWC23-TITLE','SWC23-PROPERTY','SWC23-INTEREST-A','SWC23-OWNER-A',
  'registered_current','freehold',0,'generated_fixture','SWC23-BOUNDARY',0,0,
  'bp04_joint_title_transfer_acceptance'
);

INSERT INTO sw_property.property_interest_record(
  property_interest_record_id,property_id,ownership_interest_id,
  interest_holder_organisation_id,interest_type,interest_status,
  priority_order,source_basis,source_dataset
) VALUES
  ('SWC23-RECORD-A','SWC23-PROPERTY','SWC23-INTEREST-A','SWC23-OWNER-A',
   'registered_ownership','current',1,'generated_fixture','bp04_joint_title_transfer_acceptance'),
  ('SWC23-RECORD-B','SWC23-PROPERTY','SWC23-INTEREST-B','SWC23-OWNER-B',
   'registered_ownership','current',2,'generated_fixture','bp04_joint_title_transfer_acceptance');

INSERT INTO sw_property.property_rights_schedule(
  property_rights_schedule_id,property_id,title_register_id,
  registered_ownership_interest_id,registered_owner_organisation_id,
  current_contractual_right_count,historical_contractual_right_count,
  right_class_coverage,unverified_right_classes,schedule_status,
  legal_search_required_before_disposition_or_works,source_dataset
) VALUES (
  'SWC23-RIGHTS','SWC23-PROPERTY','SWC23-TITLE','SWC23-INTEREST-A',
  'SWC23-OWNER-A',0,0,ARRAY['ownership']::text[],ARRAY[]::text[],
  'generated_fixture',true,'bp04_joint_title_transfer_acceptance'
);

DO $bp04$
DECLARE
  v_event_id text;
  v_replay_event_id text;
  v_lead_owner text;
  v_new_lead_interest text;
  v_current_count integer;
  v_historical_count integer;
  v_share_total numeric;
  v_transfer_count integer;
BEGIN
  -- A partial transfer must fail closed and leave every current title interest intact.
  BEGIN
    PERFORM * FROM sw_property.transfer_joint_property_ownership(
      'SWC23-PROPERTY',
      '[{"ownership_interest_id":"SWC23-INTEREST-A","expected_owner_organisation_id":"SWC23-OWNER-A","new_owner_organisation_id":"SWC23-BUYER-A"}]'::jsonb,
      20,20,2028,2028,'npc:title-agent','fixture:SWC23:partial',
      'SWC23:joint-transfer:partial','generated_fictional_canon'
    );
    RAISE EXCEPTION 'partial joint-title transfer was accepted';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='partial joint-title transfer was accepted' THEN RAISE; END IF;
    IF SQLERRM NOT LIKE '%must include every current registered interest%' THEN RAISE; END IF;
  END;

  SELECT lifecycle_event_id,lead_registered_proprietor_organisation_id
  INTO v_event_id,v_lead_owner
  FROM sw_property.transfer_joint_property_ownership(
    'SWC23-PROPERTY',
    '[
      {"ownership_interest_id":"SWC23-INTEREST-A","expected_owner_organisation_id":"SWC23-OWNER-A","new_owner_organisation_id":"SWC23-BUYER-A"},
      {"ownership_interest_id":"SWC23-INTEREST-B","expected_owner_organisation_id":"SWC23-OWNER-B","new_owner_organisation_id":"SWC23-BUYER-B"}
    ]'::jsonb,
    20,20,2028,2028,'npc:title-agent','fixture:SWC23:joint-transfer',
    'SWC23:joint-transfer:001','generated_fictional_canon'
  );
  IF v_lead_owner<>'SWC23-BUYER-A' THEN
    RAISE EXCEPTION 'title register did not identify the successor of the prior lead interest';
  END IF;

  SELECT current_ownership_interest_id INTO v_new_lead_interest
  FROM sw_property.property_title_register WHERE title_register_id='SWC23-TITLE';
  IF v_new_lead_interest IS NULL
     OR (SELECT registered_proprietor_organisation_id FROM sw_property.property_title_register
         WHERE title_register_id='SWC23-TITLE')<>'SWC23-BUYER-A'
     OR (SELECT registered_ownership_interest_id FROM sw_property.property_rights_schedule
         WHERE property_rights_schedule_id='SWC23-RIGHTS')<>v_new_lead_interest
     OR (SELECT registered_owner_organisation_id FROM sw_property.property_rights_schedule
         WHERE property_rights_schedule_id='SWC23-RIGHTS')<>'SWC23-BUYER-A' THEN
    RAISE EXCEPTION 'title register and property-rights schedule did not move to the successor lead interest';
  END IF;

  SELECT count(*),sum(share_numerator::numeric/share_denominator)
  INTO v_current_count,v_share_total
  FROM sw_property.ownership_interest
  WHERE property_id='SWC23-PROPERTY'
    AND interest_class='registered_ownership'
    AND interest_status='current' AND effective_to_tick IS NULL;
  SELECT count(*) INTO v_historical_count
  FROM sw_property.ownership_interest
  WHERE property_id='SWC23-PROPERTY'
    AND interest_class='registered_ownership'
    AND interest_status='historical' AND effective_to_tick=20;
  IF v_current_count<>2 OR v_historical_count<>2 OR v_share_total<>1 THEN
    RAISE EXCEPTION 'joint transfer did not preserve two historical and two current successor shares totalling one';
  END IF;

  SELECT count(*) INTO v_transfer_count
  FROM sw_property.property_title_transfer_interest
  WHERE property_id='SWC23-PROPERTY'
    AND title_instrument_id IN (
      SELECT title_instrument_id FROM sw_property.property_title_instrument
      WHERE ownership_event_id=v_event_id
    );
  IF v_transfer_count<>2 THEN RAISE EXCEPTION 'joint title transfer did not retain both outgoing-to-successor interest mappings'; END IF;

  IF (SELECT count(*) FROM sw_property.property_interest_record
      WHERE property_id='SWC23-PROPERTY' AND interest_status='current')<>2
     OR (SELECT count(*) FROM sw_property.property_interest_record
         WHERE property_id='SWC23-PROPERTY' AND interest_status='historical')<>2 THEN
    RAISE EXCEPTION 'current and historical property-interest records did not reconcile after transfer';
  END IF;

  IF (SELECT agreement_status FROM sw_property.occupancy_agreement
      WHERE agreement_id='SWC23-AGREEMENT')<>'active'
     OR (SELECT occupant_business_id FROM sw_property.occupancy
         WHERE occupancy_id='SWC23-OCCUPANCY')<>'SWC23-TENANT'
     OR (SELECT occupancy_status FROM sw_property.occupancy
         WHERE occupancy_id='SWC23-OCCUPANCY')<>'current' THEN
    RAISE EXCEPTION 'joint title transfer changed the continuing tenancy or physical occupancy';
  END IF;

  SELECT lifecycle_event_id INTO v_replay_event_id
  FROM sw_property.transfer_joint_property_ownership(
    'SWC23-PROPERTY',
    '[
      {"ownership_interest_id":"SWC23-INTEREST-B","expected_owner_organisation_id":"SWC23-OWNER-B","new_owner_organisation_id":"SWC23-BUYER-B"},
      {"ownership_interest_id":"SWC23-INTEREST-A","expected_owner_organisation_id":"SWC23-OWNER-A","new_owner_organisation_id":"SWC23-BUYER-A"}
    ]'::jsonb,
    20,20,2028,2028,'npc:title-agent','fixture:SWC23:joint-transfer',
    'SWC23:joint-transfer:001','generated_fictional_canon'
  );
  IF v_replay_event_id<>v_event_id THEN
    RAISE EXCEPTION 'exact joint title transfer replay did not return original lifecycle event';
  END IF;
  IF (SELECT count(*) FROM sw_property.property_lifecycle_event
      WHERE property_id='SWC23-PROPERTY')<>1
     OR (SELECT count(*) FROM sw_property.property_title_transfer_interest
         WHERE property_id='SWC23-PROPERTY')<>2 THEN
    RAISE EXCEPTION 'joint transfer replay created duplicate lifecycle or transfer mapping rows';
  END IF;
END
$bp04$;

ROLLBACK;
SELECT 'BP04 coordinated joint-title transfer acceptance passed' AS result;
