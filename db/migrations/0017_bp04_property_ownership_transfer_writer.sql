-- BP04-15 property ownership transfer with continuing tenancy preserved.
-- Reuses property_lifecycle_event as the single lifecycle event register.
BEGIN;

ALTER TABLE sw_property.property_lifecycle_event
  ADD COLUMN recorded_tick bigint CHECK (recorded_tick IS NULL OR recorded_tick>=0),
  ADD COLUMN actor_ref text,
  ADD COLUMN source_ref text,
  ADD COLUMN idempotency_key text,
  ADD COLUMN evidence_class text CHECK (
    evidence_class IS NULL OR evidence_class IN (
      'source_documented','generated_fictional_canon','gameplay_action'
    )
  ),
  ADD COLUMN event_payload jsonb NOT NULL DEFAULT '{}'::jsonb
    CHECK (jsonb_typeof(event_payload)='object');

CREATE UNIQUE INDEX property_lifecycle_event_idempotency_uq
  ON sw_property.property_lifecycle_event(property_id,idempotency_key)
  WHERE idempotency_key IS NOT NULL;

CREATE FUNCTION sw_property.reject_property_lifecycle_event_mutation()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
BEGIN
  RAISE EXCEPTION 'property lifecycle event history is append-only';
END
$bp04$;

CREATE TRIGGER property_lifecycle_event_immutable
BEFORE UPDATE OR DELETE ON sw_property.property_lifecycle_event
FOR EACH ROW EXECUTE FUNCTION sw_property.reject_property_lifecycle_event_mutation();

CREATE FUNCTION sw_property.transfer_property_ownership(
  p_property_id text,
  p_expected_owner_organisation_id text,
  p_new_owner_organisation_id text,
  p_effective_tick bigint,
  p_recorded_tick bigint,
  p_effective_year integer,
  p_recorded_year integer,
  p_actor_ref text,
  p_source_ref text,
  p_idempotency_key text,
  p_evidence_class text
) RETURNS TABLE(lifecycle_event_id text,property_id text,registered_proprietor_organisation_id text)
LANGUAGE plpgsql AS $bp04$
DECLARE
  v_title sw_property.property_title_register%ROWTYPE;
  v_interest sw_property.ownership_interest%ROWTYPE;
  v_prior sw_property.property_lifecycle_event%ROWTYPE;
  v_event_id text;
  v_instrument_id text;
  v_transaction_id text;
  v_payload jsonb;
  v_rows integer;
  v_latest_effective bigint;
  v_latest_recorded bigint;
BEGIN
  IF p_property_id IS NULL OR p_expected_owner_organisation_id IS NULL
     OR p_new_owner_organisation_id IS NULL
     OR p_expected_owner_organisation_id=p_new_owner_organisation_id
     OR p_effective_tick IS NULL OR p_effective_tick<0
     OR p_recorded_tick IS NULL OR p_recorded_tick<0
     OR p_effective_year IS NULL OR p_effective_year<1
     OR p_recorded_year IS NULL OR p_recorded_year<p_effective_year
     OR p_actor_ref IS NULL OR length(trim(p_actor_ref)) NOT BETWEEN 1 AND 200
     OR p_source_ref IS NULL OR length(trim(p_source_ref)) NOT BETWEEN 1 AND 200
     OR p_idempotency_key IS NULL OR p_idempotency_key !~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'
     OR p_evidence_class IS NULL
     OR p_evidence_class NOT IN ('source_documented','generated_fictional_canon','gameplay_action') THEN
    RAISE EXCEPTION 'invalid property ownership transfer request';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM sw_property.organisation
                 WHERE organisation_id=p_new_owner_organisation_id) THEN
    RAISE EXCEPTION 'new property owner organisation does not exist';
  END IF;

  SELECT t.* INTO v_title
  FROM sw_property.property_title_register AS t
  WHERE t.property_id=p_property_id
  FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'property title register not found'; END IF;

  SELECT oi.* INTO v_interest
  FROM sw_property.ownership_interest AS oi
  WHERE oi.ownership_interest_id=v_title.current_ownership_interest_id
    AND oi.property_id=p_property_id
  FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'current property ownership interest not found'; END IF;

  v_payload := jsonb_build_object(
    'prior_owner_organisation_id',p_expected_owner_organisation_id,
    'new_owner_organisation_id',p_new_owner_organisation_id,
    'ownership_interest_id',v_interest.ownership_interest_id,
    'financial_transaction_created',false,
    'tenancy_and_occupancy_mutated',false
  );

  SELECT ev.* INTO v_prior
  FROM sw_property.property_lifecycle_event AS ev
  WHERE ev.property_id=p_property_id AND ev.idempotency_key=p_idempotency_key;
  IF FOUND THEN
    IF v_prior.event_type<>'ownership_transferred'
       OR v_prior.effective_tick<>p_effective_tick
       OR v_prior.recorded_tick<>p_recorded_tick
       OR v_prior.effective_year<>p_effective_year
       OR v_prior.recorded_year<>p_recorded_year
       OR v_prior.actor_ref<>p_actor_ref
       OR v_prior.source_ref<>p_source_ref
       OR v_prior.evidence_class<>p_evidence_class
       OR v_prior.event_payload->>'prior_owner_organisation_id' IS DISTINCT FROM p_expected_owner_organisation_id
       OR v_prior.event_payload->>'new_owner_organisation_id' IS DISTINCT FROM p_new_owner_organisation_id
       OR v_prior.event_payload->>'ownership_interest_id' IS DISTINCT FROM v_interest.ownership_interest_id
       OR v_prior.event_payload->>'financial_transaction_created' IS DISTINCT FROM 'false'
       OR v_prior.event_payload->>'tenancy_and_occupancy_mutated' IS DISTINCT FROM 'false' THEN
      RAISE EXCEPTION 'property ownership transfer idempotency key conflicts with prior event';
    END IF;
    RETURN QUERY SELECT v_prior.lifecycle_event_id,p_property_id,p_new_owner_organisation_id;
    RETURN;
  END IF;

  IF v_title.current_ownership_interest_id<>v_interest.ownership_interest_id
     OR v_title.registered_proprietor_organisation_id<>p_expected_owner_organisation_id
     OR v_interest.owner_organisation_id<>p_expected_owner_organisation_id THEN
    RAISE EXCEPTION 'current title and ownership-interest owner do not match expected transferor';
  END IF;

  SELECT max(ev.effective_tick),max(ev.recorded_tick)
  INTO v_latest_effective,v_latest_recorded
  FROM sw_property.property_lifecycle_event AS ev
  WHERE ev.property_id=p_property_id;
  IF v_latest_effective IS NOT NULL AND p_effective_tick<v_latest_effective THEN
    RAISE EXCEPTION 'property lifecycle effective tick cannot move backwards';
  END IF;
  IF v_latest_recorded IS NOT NULL AND p_recorded_tick<v_latest_recorded THEN
    RAISE EXCEPTION 'property lifecycle recorded tick cannot move backwards';
  END IF;

  v_event_id := 'SWPLE-GAME-' || replace(gen_random_uuid()::text,'-','');
  v_instrument_id := 'SWTI-GAME-' || replace(gen_random_uuid()::text,'-','');
  v_transaction_id := 'SWPTX-GAME-' || replace(gen_random_uuid()::text,'-','');
  v_payload := v_payload || jsonb_build_object(
    'title_instrument_id',v_instrument_id,
    'property_transaction_id',v_transaction_id
  );

  INSERT INTO sw_property.property_lifecycle_event(
    lifecycle_event_id,property_id,event_type,effective_year,effective_tick,
    event_status,title_register_id,source_record_id,historical_date_known,
    financial_transaction_created,narrative,source_dataset,recorded_tick,
    actor_ref,source_ref,idempotency_key,evidence_class,event_payload
  ) VALUES (
    v_event_id,p_property_id,'ownership_transferred',p_effective_year,p_effective_tick,
    'recorded',v_title.title_register_id,p_source_ref,true,false,
    'Property title transferred; occupancy agreements and physical occupancy remain separate',
    'BP04-GAMEPLAY-PROPERTY-OWNERSHIP-TRANSFER',p_recorded_tick,
    p_actor_ref,p_source_ref,p_idempotency_key,p_evidence_class,v_payload
  );

  INSERT INTO sw_property.property_title_instrument(
    title_instrument_id,property_id,title_register_id,ownership_event_id,
    instrument_type,transferor_organisation_id,transferee_organisation_id,
    effective_year,recorded_year,instrument_status,source_basis,
    consideration_recorded_as_band_only,payment_or_settlement_record_created,source_dataset
  ) VALUES (
    v_instrument_id,p_property_id,v_title.title_register_id,v_event_id,
    'ownership_transfer',p_expected_owner_organisation_id,p_new_owner_organisation_id,
    p_effective_year,p_recorded_year,'registered_current_chain',p_evidence_class,
    false,false,'BP04-GAMEPLAY-PROPERTY-OWNERSHIP-TRANSFER'
  );

  INSERT INTO sw_property.property_transaction_index(
    property_transaction_id,property_id,title_register_id,transaction_type,
    ownership_event_id,title_instrument_id,from_organisation_id,to_organisation_id,
    effective_year,recorded_year,transaction_status,consideration_band,
    financial_settlement_status,source_of_truth,source_dataset
  ) VALUES (
    v_transaction_id,p_property_id,v_title.title_register_id,'ownership_transfer',
    v_event_id,v_instrument_id,p_expected_owner_organisation_id,p_new_owner_organisation_id,
    p_effective_year,p_recorded_year,'recorded',NULL,'not_created_bp34',
    'SW_PROPERTY_LIFECYCLE_EVENT','BP04-GAMEPLAY-PROPERTY-OWNERSHIP-TRANSFER'
  );

  UPDATE sw_property.ownership_interest
  SET owner_organisation_id=p_new_owner_organisation_id
  WHERE ownership_interest_id=v_interest.ownership_interest_id
    AND owner_organisation_id=p_expected_owner_organisation_id;
  GET DIAGNOSTICS v_rows = ROW_COUNT;
  IF v_rows<>1 THEN RAISE EXCEPTION 'ownership transfer did not update exactly one ownership interest'; END IF;

  UPDATE sw_property.property_title_register AS ptr
  SET registered_proprietor_organisation_id=p_new_owner_organisation_id,
      registration_tick=p_recorded_tick
  WHERE ptr.title_register_id=v_title.title_register_id
    AND ptr.registered_proprietor_organisation_id=p_expected_owner_organisation_id;
  GET DIAGNOSTICS v_rows = ROW_COUNT;
  IF v_rows<>1 THEN RAISE EXCEPTION 'ownership transfer did not update exactly one title register'; END IF;

  UPDATE sw_property.property_interest_record
  SET interest_holder_organisation_id=p_new_owner_organisation_id
  WHERE ownership_interest_id=v_interest.ownership_interest_id
    AND interest_holder_organisation_id=p_expected_owner_organisation_id
    AND interest_status='current';
  GET DIAGNOSTICS v_rows = ROW_COUNT;
  IF v_rows<>1 THEN RAISE EXCEPTION 'ownership transfer requires exactly one current property-interest record'; END IF;

  UPDATE sw_property.property_rights_schedule AS prs
  SET registered_owner_organisation_id=p_new_owner_organisation_id
  WHERE prs.property_id=p_property_id
    AND prs.registered_owner_organisation_id=p_expected_owner_organisation_id;
  GET DIAGNOSTICS v_rows = ROW_COUNT;
  IF v_rows<>1 THEN RAISE EXCEPTION 'ownership transfer requires exactly one property-rights schedule'; END IF;

  -- Occupancy agreements, occupants, operators, rights grantors and primary
  -- business-unit links are intentionally not rewritten by title transfer.
  RETURN QUERY SELECT v_event_id,p_property_id,p_new_owner_organisation_id;
END
$bp04$;

REVOKE ALL ON FUNCTION sw_property.transfer_property_ownership(
  text,text,text,bigint,bigint,integer,integer,text,text,text,text
) FROM PUBLIC;
COMMIT;
