\set ON_ERROR_STOP on
BEGIN;

INSERT INTO sw_property.organisation(
  organisation_id,display_name,organisation_type,registered_city,status,source_dataset
) VALUES
  ('SWC02-OWNER-A','C02 Joint Owner A','property_holding_company','Saltwater','active','bp04_ownership_interest_acceptance'),
  ('SWC02-OWNER-B','C02 Joint Owner B','property_holding_company','Saltwater','active','bp04_ownership_interest_acceptance'),
  ('SWC02-OWNER-C','C02 Proposed Owner C','property_holding_company','Saltwater','active','bp04_ownership_interest_acceptance'),
  ('SWC02-BENEFICIAL','C02 Beneficial Claimant','investment_holding_company','Saltwater','active','bp04_ownership_interest_acceptance'),
  ('SWC02-HISTORIC','C02 Former Interest Holder','property_holding_company','Saltwater','historical','bp04_ownership_interest_acceptance');

INSERT INTO sw_property.property_site(
  property_id,display_name,use_class,lifecycle_status,source_dataset
) VALUES ('SWC02-PROPERTY','C02 Joint Ownership Test Property','commercial','active','bp04_ownership_interest_acceptance');

INSERT INTO sw_property.ownership_interest(
  ownership_interest_id,property_id,owner_organisation_id,management_model,interest_type,
  source_dataset,interest_class,share_numerator,share_denominator,
  effective_from_tick,effective_to_tick,interest_status,dispute_status,dispute_reference,recorded_tick
) VALUES
  ('SWC02-INTEREST-A','SWC02-PROPERTY','SWC02-OWNER-A','direct_owner_management','freehold',
   'bp04_ownership_interest_acceptance',
   'registered_ownership',1,2,0,NULL,'current','undisputed',NULL,0),
  ('SWC02-INTEREST-B','SWC02-PROPERTY','SWC02-OWNER-B','direct_owner_management','freehold',
   'bp04_ownership_interest_acceptance',
   'registered_ownership',1,2,0,NULL,'current','undisputed',NULL,0),
  ('SWC02-INTEREST-BENEFICIAL','SWC02-PROPERTY','SWC02-BENEFICIAL',NULL,'beneficial',
   'bp04_ownership_interest_acceptance',
   'beneficial_ownership',1,3,2,NULL,'current','disputed','claim:SWC02:beneficial:01',2),
  ('SWC02-INTEREST-HISTORIC','SWC02-PROPERTY','SWC02-HISTORIC',NULL,'freehold',
   'bp04_ownership_interest_acceptance',
   'registered_ownership',1,2,0,10,'historical','resolved','claim:SWC02:historic:resolved',10);

DO $bp04$
DECLARE
  v_share_total numeric;
  v_count integer;
BEGIN
  SELECT count(*),sum(share_numerator::numeric/share_denominator)
  INTO v_count,v_share_total
  FROM sw_property.ownership_interest
  WHERE property_id='SWC02-PROPERTY'
    AND interest_class='registered_ownership'
    AND interest_status='current'
    AND effective_to_tick IS NULL;
  IF v_count<>2 OR v_share_total<>1 THEN
    RAISE EXCEPTION 'joint ownership did not retain two current co-owners with exactly one whole share';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM sw_property.ownership_interest
    WHERE ownership_interest_id='SWC02-INTEREST-BENEFICIAL'
      AND dispute_status='disputed'
      AND dispute_reference='claim:SWC02:beneficial:01'
      AND interest_class='beneficial_ownership'
  ) THEN
    RAISE EXCEPTION 'disputed beneficial interest lost its explicit claim state or provenance';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM sw_property.ownership_interest
    WHERE ownership_interest_id='SWC02-INTEREST-HISTORIC'
      AND interest_status='historical'
      AND effective_from_tick=0 AND effective_to_tick=10
  ) THEN
    RAISE EXCEPTION 'historical time-bounded ownership interest was not retained';
  END IF;

  BEGIN
    INSERT INTO sw_property.ownership_interest(
      ownership_interest_id,property_id,owner_organisation_id,interest_type,
      source_dataset,interest_class,share_numerator,share_denominator,
      effective_from_tick,interest_status
    ) VALUES (
      'SWC02-OVERALLOCATED','SWC02-PROPERTY','SWC02-OWNER-C','freehold',
      'bp04_ownership_interest_acceptance',
      'registered_ownership',1,4,0,'current'
    );
    RAISE EXCEPTION 'registered ownership share over-allocation was accepted';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='registered ownership share over-allocation was accepted' THEN RAISE; END IF;
    IF SQLERRM NOT LIKE '%registered ownership shares exceed one whole property interest%' THEN RAISE; END IF;
  END;

  BEGIN
    INSERT INTO sw_property.ownership_interest(
      ownership_interest_id,property_id,owner_organisation_id,interest_type,
      source_dataset,interest_class,share_numerator,share_denominator,
      effective_from_tick,effective_to_tick,interest_status
    ) VALUES (
      'SWC02-BAD-INTERVAL','SWC02-PROPERTY','SWC02-OWNER-C','freehold',
      'bp04_ownership_interest_acceptance',
      'other_interest',1,1,10,10,'historical'
    );
    RAISE EXCEPTION 'zero-length ownership interest interval was accepted';
  EXCEPTION WHEN check_violation THEN NULL;
  END;

  BEGIN
    INSERT INTO sw_property.ownership_interest(
      ownership_interest_id,property_id,owner_organisation_id,interest_type,
      source_dataset,interest_class,share_numerator,share_denominator,
      effective_from_tick,interest_status,dispute_status
    ) VALUES (
      'SWC02-BAD-DISPUTE','SWC02-PROPERTY','SWC02-OWNER-C','beneficial',
      'bp04_ownership_interest_acceptance',
      'beneficial_ownership',1,4,0,'current','disputed'
    );
    RAISE EXCEPTION 'disputed ownership claim without a reference was accepted';
  EXCEPTION WHEN check_violation THEN NULL;
  END;

  INSERT INTO sw_property.property_title_register(
    title_register_id,property_id,current_ownership_interest_id,
    registered_proprietor_organisation_id,title_status,tenure_type,
    registration_tick,source_basis,boundary_record_id,active_dispute_count,
    unresolved_title_issue_count,source_dataset
  ) VALUES (
    'SWC02-TITLE','SWC02-PROPERTY','SWC02-INTEREST-A','SWC02-OWNER-A',
    'registered_current','freehold',0,'generated_fixture','SWC02-BOUNDARY',0,0,
    'bp04_ownership_interest_acceptance'
  );

  INSERT INTO sw_property.property_interest_record(
    property_interest_record_id,property_id,ownership_interest_id,
    interest_holder_organisation_id,interest_type,interest_status,
    priority_order,source_basis,source_dataset
  ) VALUES
    ('SWC02-RECORD-A','SWC02-PROPERTY','SWC02-INTEREST-A','SWC02-OWNER-A',
     'registered_ownership','current',1,'generated_fixture','bp04_ownership_interest_acceptance'),
    ('SWC02-RECORD-B','SWC02-PROPERTY','SWC02-INTEREST-B','SWC02-OWNER-B',
     'registered_ownership','current',2,'generated_fixture','bp04_ownership_interest_acceptance');

  INSERT INTO sw_property.property_rights_schedule(
    property_rights_schedule_id,property_id,title_register_id,
    registered_ownership_interest_id,registered_owner_organisation_id,
    current_contractual_right_count,historical_contractual_right_count,
    right_class_coverage,unverified_right_classes,schedule_status,
    legal_search_required_before_disposition_or_works,source_dataset
  ) VALUES (
    'SWC02-RIGHTS','SWC02-PROPERTY','SWC02-TITLE','SWC02-INTEREST-A',
    'SWC02-OWNER-A',0,0,ARRAY['ownership']::text[],ARRAY['easement']::text[],
    'generated_fixture',true,'bp04_ownership_interest_acceptance'
  );

  BEGIN
    PERFORM * FROM sw_property.transfer_property_ownership(
      'SWC02-PROPERTY','SWC02-OWNER-A','SWC02-OWNER-C',
      20,20,2028,2028,'actor:test','source:test:joint-title',
      'test:joint-title:single-transfer','gameplay_action'
    );
    RAISE EXCEPTION 'single-owner title transfer silently transferred only one joint interest';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='single-owner title transfer silently transferred only one joint interest' THEN RAISE; END IF;
    IF SQLERRM NOT LIKE '%single-interest title transfer is not permitted while joint registered ownership interests exist%' THEN RAISE; END IF;
  END;

  IF (SELECT registered_proprietor_organisation_id FROM sw_property.property_title_register
      WHERE title_register_id='SWC02-TITLE')<>'SWC02-OWNER-A'
     OR (SELECT owner_organisation_id FROM sw_property.ownership_interest
         WHERE ownership_interest_id='SWC02-INTEREST-A')<>'SWC02-OWNER-A'
     OR (SELECT count(*) FROM sw_property.property_lifecycle_event
         WHERE property_id='SWC02-PROPERTY')<>0 THEN
    RAISE EXCEPTION 'blocked single-owner transfer changed joint title or left partial lifecycle events';
  END IF;
END
$bp04$;

ROLLBACK;
SELECT 'BP04 joint, disputed and time-bounded ownership interest acceptance passed' AS result;
