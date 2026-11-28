-- BP04 explicit letting-authority schema and append-only acceptance.
-- Runs after ordered migrations on disposable PostgreSQL only.
BEGIN;

DO $bp04$
DECLARE
  v_trigger_count integer;
  v_function_count integer;
BEGIN
  IF to_regclass('sw_property.letting_authority') IS NULL
     OR to_regclass('sw_property.letting_authority_event') IS NULL THEN
    RAISE EXCEPTION 'letting authority registers are missing';
  END IF;
  SELECT count(*) INTO v_trigger_count
  FROM pg_trigger
  WHERE tgrelid='sw_property.occupancy_agreement'::regclass
    AND tgname='occupancy_agreement_landlord_authority_guard'
    AND NOT tgisinternal;
  IF v_trigger_count<>1 THEN
    RAISE EXCEPTION 'agreement landlord-authority guard is not installed';
  END IF;
  SELECT count(*) INTO v_function_count
  FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
  WHERE n.nspname='sw_property'
    AND p.proname='validate_agreement_landlord_authority';
  IF v_function_count<>1 THEN
    RAISE EXCEPTION 'agreement landlord-authority validator is missing';
  END IF;
END
$bp04$;

INSERT INTO sw_property.organisation(
  organisation_id,display_name,organisation_type,source_dataset
) VALUES
 ('bp04-33-fixture-title-holder','BP04-33 fixture title holder','company','bp04-33-test'),
 ('bp04-33-fixture-head-lessee','BP04-33 fixture head lessee','company','bp04-33-test')
ON CONFLICT(organisation_id) DO NOTHING;

INSERT INTO sw_property.property_site(
  property_id,display_name,source_dataset
) VALUES ('bp04-33-fixture-property','BP04-33 fixture property','bp04-33-test')
ON CONFLICT(property_id) DO NOTHING;

INSERT INTO sw_property.letting_authority(
  letting_authority_id,property_id,grantor_organisation_id,
  grantee_organisation_id,authority_type,authority_status,
  effective_from_year,source_instrument_ref,source_basis
) VALUES (
 'bp04-33-fixture-authority','bp04-33-fixture-property',
 'bp04-33-fixture-title-holder','bp04-33-fixture-head-lessee',
 'head_lease','current',2020,'fixture-instrument-33','generated_fictional_canon'
);

INSERT INTO sw_property.letting_authority_event(
  letting_authority_id,event_type,effective_year,recorded_tick,
  actor_ref,source_ref,idempotency_key,evidence_class
) VALUES (
 'bp04-33-fixture-authority','authority_granted',2020,1,
 'fixture-npc-grantor','fixture-instrument-33','bp04-33-fixture-event',
 'generated_fictional_canon'
);

DO $bp04$
DECLARE v_blocked boolean := false;
BEGIN
  BEGIN
    UPDATE sw_property.letting_authority_event
    SET event_payload='{"tampered":true}'::jsonb
    WHERE idempotency_key='bp04-33-fixture-event';
  EXCEPTION WHEN OTHERS THEN
    v_blocked := true;
  END;
  IF NOT v_blocked THEN
    RAISE EXCEPTION 'letting authority event update was not blocked';
  END IF;

  v_blocked := false;
  BEGIN
    DELETE FROM sw_property.letting_authority_event
    WHERE idempotency_key='bp04-33-fixture-event';
  EXCEPTION WHEN OTHERS THEN
    v_blocked := true;
  END;
  IF NOT v_blocked THEN
    RAISE EXCEPTION 'letting authority event deletion was not blocked';
  END IF;
END
$bp04$;


INSERT INTO sw_property.organisation(
 organisation_id,display_name,organisation_type,registered_city,status,source_dataset
) VALUES
 ('bp04-33-fixture-wrong-grantor','Wrong grantor organisation','company','Saltwater','active','bp04-33-test'),
 ('bp04-33-fixture-tenant','Fixture tenant business identity','company','Saltwater','active','bp04-33-test'),
 ('bp04-33-fixture-wrong-landlord','Wrong landlord organisation','company','Saltwater','active','bp04-33-test');

INSERT INTO sw_property.premises(
 premises_id,property_id,display_name,premises_use,lifecycle_status,source_dataset
) VALUES ('bp04-33-fixture-premises','bp04-33-fixture-property',
 'BP04-33 fixture premises','commercial','active','bp04-33-test');

INSERT INTO sw_property.unit_space(
 unit_id,property_id,premises_id,display_name,unit_class,use_class,lifecycle_status,source_dataset
) VALUES
 ('bp04-33-fixture-unit','bp04-33-fixture-property','bp04-33-fixture-premises',
  'BP04-33 fixture unit','commercial','commercial','active','bp04-33-test'),
 ('bp04-33-fixture-other-unit','bp04-33-fixture-property','bp04-33-fixture-premises',
  'BP04-33 other unit','commercial','commercial','active','bp04-33-test');

INSERT INTO sw_property.business(
 business_id,display_name,sector,status,source_dataset
) VALUES ('bp04-33-fixture-tenant-business','BP04-33 fixture tenant',
 'professional_services','active','bp04-33-test');

INSERT INTO sw_property.ownership_interest(
 ownership_interest_id,property_id,owner_organisation_id,management_model,
 interest_type,source_dataset
) VALUES ('bp04-33-fixture-owner-interest','bp04-33-fixture-property',
 'bp04-33-fixture-title-holder','direct_owner_management','freehold','bp04-33-test');

INSERT INTO sw_property.property_title_register(
 title_register_id,property_id,current_ownership_interest_id,
 registered_proprietor_organisation_id,title_status,tenure_type,
 registration_tick,source_basis,boundary_record_id,active_dispute_count,
 unresolved_title_issue_count,source_dataset
) VALUES ('bp04-33-fixture-title','bp04-33-fixture-property',
 'bp04-33-fixture-owner-interest','bp04-33-fixture-title-holder',
 'registered','freehold',0,'generated_fictional_canon','bp04-33-boundary',
 0,0,'bp04-33-test');

INSERT INTO sw_property.occupancy_agreement(
 agreement_id,property_id,premises_id,unit_id,landlord_organisation_id,
 tenant_business_id,agreement_type,commencement_year,agreement_status,source_dataset
) VALUES ('bp04-33-owner-agreement','bp04-33-fixture-property',
 'bp04-33-fixture-premises','bp04-33-fixture-unit',
 'bp04-33-fixture-title-holder','bp04-33-fixture-tenant-business',
 'commercial_occupancy_lease',2025,'active','bp04-33-test');

INSERT INTO sw_property.letting_authority(
 letting_authority_id,property_id,unit_id,grantor_organisation_id,
 grantee_organisation_id,authority_type,authority_status,effective_from_year,
 source_instrument_ref,source_basis
) VALUES
 ('bp04-33-wrong-grantor','bp04-33-fixture-property',NULL,
  'bp04-33-fixture-wrong-grantor','bp04-33-fixture-head-lessee',
  'head_lease','current',2020,'fixture-wrong-grantor','generated_fictional_canon'),
 ('bp04-33-wrong-unit','bp04-33-fixture-property','bp04-33-fixture-other-unit',
  'bp04-33-fixture-title-holder','bp04-33-fixture-head-lessee',
  'head_lease','current',2020,'fixture-wrong-unit','generated_fictional_canon'),
 ('bp04-33-future-authority','bp04-33-fixture-property',NULL,
  'bp04-33-fixture-title-holder','bp04-33-fixture-head-lessee',
  'head_lease','current',2030,'fixture-future-authority','generated_fictional_canon');

INSERT INTO sw_property.letting_authority_event(
 letting_authority_id,event_type,effective_year,recorded_tick,actor_ref,
 source_ref,idempotency_key,evidence_class
) VALUES
 ('bp04-33-wrong-grantor','authority_granted',2020,1,'fixture-npc',
  'fixture-wrong-grantor','bp04-33-wrong-grantor-event','generated_fictional_canon'),
 ('bp04-33-wrong-unit','authority_granted',2020,1,'fixture-npc',
  'fixture-wrong-unit','bp04-33-wrong-unit-event','generated_fictional_canon'),
 ('bp04-33-future-authority','authority_granted',2030,1,'fixture-npc',
  'fixture-future-authority','bp04-33-future-event','generated_fictional_canon');

INSERT INTO sw_property.occupancy_agreement(
 agreement_id,property_id,premises_id,unit_id,landlord_organisation_id,
 tenant_business_id,agreement_type,commencement_year,agreement_status,source_dataset,
 letting_authority_id
) VALUES ('bp04-33-valid-headlease-agreement','bp04-33-fixture-property',
 'bp04-33-fixture-premises','bp04-33-fixture-unit',
 'bp04-33-fixture-head-lessee','bp04-33-fixture-tenant-business',
 'commercial_occupancy_lease',2025,'active','bp04-33-test',
 'bp04-33-fixture-authority');

DO $bp04$
DECLARE v_blocked boolean;
BEGIN
  v_blocked:=false;
  BEGIN
    INSERT INTO sw_property.occupancy_agreement(
      agreement_id,property_id,unit_id,landlord_organisation_id,tenant_business_id,
      agreement_type,commencement_year,agreement_status,source_dataset,letting_authority_id
    ) VALUES ('bp04-33-no-authority','bp04-33-fixture-property',
      'bp04-33-fixture-unit','bp04-33-fixture-head-lessee',
      'bp04-33-fixture-tenant-business','commercial_occupancy_lease',
      2025,'active','bp04-33-test',NULL);
  EXCEPTION WHEN OTHERS THEN v_blocked:=true; END;
  IF NOT v_blocked THEN RAISE EXCEPTION 'non-owner landlord without authority was accepted'; END IF;

  v_blocked:=false;
  BEGIN
    INSERT INTO sw_property.occupancy_agreement(
      agreement_id,property_id,unit_id,landlord_organisation_id,tenant_business_id,
      agreement_type,commencement_year,agreement_status,source_dataset,letting_authority_id
    ) VALUES ('bp04-33-wrong-grantor-agreement','bp04-33-fixture-property',
      'bp04-33-fixture-unit','bp04-33-fixture-head-lessee',
      'bp04-33-fixture-tenant-business','commercial_occupancy_lease',
      2025,'active','bp04-33-test','bp04-33-wrong-grantor');
  EXCEPTION WHEN OTHERS THEN v_blocked:=true; END;
  IF NOT v_blocked THEN RAISE EXCEPTION 'authority from a non-title-holder grantor was accepted'; END IF;

  v_blocked:=false;
  BEGIN
    INSERT INTO sw_property.occupancy_agreement(
      agreement_id,property_id,unit_id,landlord_organisation_id,tenant_business_id,
      agreement_type,commencement_year,agreement_status,source_dataset,letting_authority_id
    ) VALUES ('bp04-33-wrong-unit-agreement','bp04-33-fixture-property',
      'bp04-33-fixture-unit','bp04-33-fixture-head-lessee',
      'bp04-33-fixture-tenant-business','commercial_occupancy_lease',
      2025,'active','bp04-33-test','bp04-33-wrong-unit');
  EXCEPTION WHEN OTHERS THEN v_blocked:=true; END;
  IF NOT v_blocked THEN RAISE EXCEPTION 'unit-scoped authority was accepted for another unit'; END IF;

  v_blocked:=false;
  BEGIN
    INSERT INTO sw_property.occupancy_agreement(
      agreement_id,property_id,unit_id,landlord_organisation_id,tenant_business_id,
      agreement_type,commencement_year,agreement_status,source_dataset,letting_authority_id
    ) VALUES ('bp04-33-future-agreement','bp04-33-fixture-property',
      'bp04-33-fixture-unit','bp04-33-fixture-head-lessee',
      'bp04-33-fixture-tenant-business','commercial_occupancy_lease',
      2025,'active','bp04-33-test','bp04-33-future-authority');
  EXCEPTION WHEN OTHERS THEN v_blocked:=true; END;
  IF NOT v_blocked THEN RAISE EXCEPTION 'agreement outside authority term was accepted'; END IF;

  IF NOT EXISTS (
    SELECT 1 FROM sw_property.occupancy_agreement
    WHERE agreement_id='bp04-33-owner-agreement'
      AND landlord_organisation_id='bp04-33-fixture-title-holder'
      AND letting_authority_id IS NULL
  ) THEN RAISE EXCEPTION 'title-holder landlord without a letting authority was rejected'; END IF;
  IF NOT EXISTS (
    SELECT 1 FROM sw_property.occupancy_agreement
    WHERE agreement_id='bp04-33-valid-headlease-agreement'
      AND landlord_organisation_id='bp04-33-fixture-head-lessee'
      AND letting_authority_id='bp04-33-fixture-authority'
  ) THEN RAISE EXCEPTION 'valid evidenced head-lessee landlord was rejected'; END IF;
END
$bp04$;


ROLLBACK;
