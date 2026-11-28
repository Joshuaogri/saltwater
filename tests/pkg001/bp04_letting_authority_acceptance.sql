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

ROLLBACK;
