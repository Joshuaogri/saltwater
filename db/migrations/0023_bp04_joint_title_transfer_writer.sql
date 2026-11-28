-- BP04-23 coordinated transfer of all current registered co-ownership interests.
-- Every outgoing interest is closed historically and replaced by a successor
-- interest with the same share. Tenancy, occupancy and operators are untouched.
BEGIN;

CREATE TABLE sw_property.property_title_transfer_interest (
  title_transfer_interest_id text PRIMARY KEY,
  title_instrument_id text NOT NULL REFERENCES sw_property.property_title_instrument(title_instrument_id)
    DEFERRABLE INITIALLY DEFERRED,
  property_id text NOT NULL REFERENCES sw_property.property_site(property_id)
    DEFERRABLE INITIALLY DEFERRED,
  prior_ownership_interest_id text NOT NULL REFERENCES sw_property.ownership_interest(ownership_interest_id)
    DEFERRABLE INITIALLY DEFERRED,
  successor_ownership_interest_id text NOT NULL UNIQUE REFERENCES sw_property.ownership_interest(ownership_interest_id)
    DEFERRABLE INITIALLY DEFERRED,
  prior_owner_organisation_id text NOT NULL REFERENCES sw_property.organisation(organisation_id)
    DEFERRABLE INITIALLY DEFERRED,
  successor_owner_organisation_id text NOT NULL REFERENCES sw_property.organisation(organisation_id)
    DEFERRABLE INITIALLY DEFERRED,
  share_numerator bigint NOT NULL CHECK (share_numerator>0),
  share_denominator bigint NOT NULL CHECK (share_denominator>0 AND share_numerator<=share_denominator),
  effective_tick bigint NOT NULL CHECK (effective_tick>=0),
  recorded_tick bigint NOT NULL CHECK (recorded_tick>=0),
  source_dataset text NOT NULL,
  UNIQUE(title_instrument_id,prior_ownership_interest_id),
  CHECK (prior_owner_organisation_id<>successor_owner_organisation_id)
);
CREATE INDEX property_title_transfer_interest_property_idx
  ON sw_property.property_title_transfer_interest(property_id,effective_tick);

CREATE FUNCTION sw_property.transfer_joint_property_ownership(
  p_property_id text,
  p_interest_transfers jsonb,
  p_effective_tick bigint,
  p_recorded_tick bigint,
  p_effective_year integer,
  p_recorded_year integer,
  p_actor_ref text,
  p_source_ref text,
  p_idempotency_key text,
  p_evidence_class text
) RETURNS TABLE(
  lifecycle_event_id text,
  property_id text,
  lead_registered_proprietor_organisation_id text
)
LANGUAGE plpgsql AS $bp04$
DECLARE
  v_title sw_property.property_title_register%ROWTYPE;
  v_interest sw_property.ownership_interest%ROWTYPE;
  v_interest_record sw_property.property_interest_record%ROWTYPE;
  v_prior sw_property.property_lifecycle_event%ROWTYPE;
  v_item record;
  v_input_count integer;
  v_current_count integer;
  v_matched_count integer;
  v_current_share_total numeric;
  v_transfers jsonb;
  v_completed_transfers jsonb := '[]'::jsonb;
  v_payload jsonb;
  v_event_id text;
  v_instrument_id text;
  v_transaction_id text;
  v_successor_interest_id text;
  v_lead_successor_interest_id text;
  v_lead_new_owner_id text;
  v_lead_prior_owner_id text;
  v_latest_effective bigint;
  v_latest_recorded bigint;
  v_rows integer;
BEGIN
  IF p_property_id IS NULL
     OR p_interest_transfers IS NULL OR jsonb_typeof(p_interest_transfers)<>'array'
     OR jsonb_array_length(p_interest_transfers)<2
     OR p_effective_tick IS NULL OR p_effective_tick<0
     OR p_recorded_tick IS NULL OR p_recorded_tick<0
     OR p_effective_year IS NULL OR p_effective_year<1
     OR p_recorded_year IS NULL OR p_recorded_year<p_effective_year
     OR p_actor_ref IS NULL OR length(trim(p_actor_ref)) NOT BETWEEN 1 AND 200
     OR p_source_ref IS NULL OR length(trim(p_source_ref)) NOT BETWEEN 1 AND 200
     OR p_idempotency_key IS NULL OR p_idempotency_key !~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'
     OR p_evidence_class NOT IN ('source_documented','generated_fictional_canon','gameplay_action') THEN
    RAISE EXCEPTION 'invalid joint property ownership transfer request';
  END IF;

  SELECT count(*) INTO v_input_count
  FROM jsonb_to_recordset(p_interest_transfers) AS x(
    ownership_interest_id text,
    expected_owner_organisation_id text,
    new_owner_organisation_id text
  );
  IF v_input_count<>jsonb_array_length(p_interest_transfers)
     OR EXISTS (
       SELECT 1
       FROM jsonb_to_recordset(p_interest_transfers) AS x(
         ownership_interest_id text,
         expected_owner_organisation_id text,
         new_owner_organisation_id text
       )
       WHERE x.ownership_interest_id IS NULL
          OR x.expected_owner_organisation_id IS NULL
          OR x.new_owner_organisation_id IS NULL
          OR x.expected_owner_organisation_id=x.new_owner_organisation_id
     ) THEN
    RAISE EXCEPTION 'each joint transfer entry requires distinct current and successor owner references';
  END IF;

  SELECT jsonb_agg(jsonb_build_object(
    'ownership_interest_id',x.ownership_interest_id,
    'expected_owner_organisation_id',x.expected_owner_organisation_id,
    'new_owner_organisation_id',x.new_owner_organisation_id
  ) ORDER BY x.ownership_interest_id)
  INTO v_transfers
  FROM jsonb_to_recordset(p_interest_transfers) AS x(
    ownership_interest_id text,
    expected_owner_organisation_id text,
    new_owner_organisation_id text
  );

  IF (SELECT count(DISTINCT x.ownership_interest_id)
      FROM jsonb_to_recordset(v_transfers) AS x(
        ownership_interest_id text,
        expected_owner_organisation_id text,
        new_owner_organisation_id text
      ))<>v_input_count THEN
    RAISE EXCEPTION 'joint transfer contains duplicate ownership-interest references';
  END IF;

  PERFORM 1 FROM sw_property.property_site AS p
  WHERE p.property_id=p_property_id
  FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'property site not found'; END IF;

  SELECT t.* INTO v_title
  FROM sw_property.property_title_register AS t
  WHERE t.property_id=p_property_id
  FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'property title register not found'; END IF;

  -- Exact replay is checked before current-title expectations, because a
  -- successful prior transfer has already replaced the original interests.
  SELECT ev.* INTO v_prior
  FROM sw_property.property_lifecycle_event AS ev
  WHERE ev.property_id=p_property_id AND ev.idempotency_key=p_idempotency_key;
  IF FOUND THEN
    IF v_prior.event_type<>'joint_ownership_transferred'
       OR v_prior.effective_tick<>p_effective_tick
       OR v_prior.recorded_tick<>p_recorded_tick
       OR v_prior.effective_year<>p_effective_year
       OR v_prior.recorded_year<>p_recorded_year
       OR v_prior.actor_ref<>p_actor_ref
       OR v_prior.source_ref<>p_source_ref
       OR v_prior.evidence_class<>p_evidence_class
       OR v_prior.event_payload->'interest_transfers' IS DISTINCT FROM v_transfers THEN
      RAISE EXCEPTION 'joint property ownership transfer idempotency key conflicts with prior event';
    END IF;
    RETURN QUERY SELECT v_prior.lifecycle_event_id,p_property_id,
      v_prior.event_payload->>'lead_successor_owner_organisation_id';
    RETURN;
  END IF;

  SELECT count(*),
         COALESCE(sum(oi.share_numerator::numeric/oi.share_denominator),0)
  INTO v_current_count,v_current_share_total
  FROM sw_property.ownership_interest AS oi
  WHERE oi.property_id=p_property_id
    AND oi.interest_class='registered_ownership'
    AND oi.interest_status='current'
    AND oi.effective_to_tick IS NULL;

  IF v_current_count<2 OR v_current_count<>v_input_count OR v_current_share_total<>1 THEN
    RAISE EXCEPTION 'joint transfer must include every current registered interest with known shares totaling one whole property';
  END IF;

  SELECT count(*) INTO v_matched_count
  FROM jsonb_to_recordset(v_transfers) AS x(
    ownership_interest_id text,
    expected_owner_organisation_id text,
    new_owner_organisation_id text
  )
  JOIN sw_property.ownership_interest AS oi
    ON oi.ownership_interest_id=x.ownership_interest_id
   AND oi.property_id=p_property_id
   AND oi.owner_organisation_id=x.expected_owner_organisation_id
   AND oi.interest_class='registered_ownership'
   AND oi.interest_status='current'
   AND oi.effective_to_tick IS NULL
   AND oi.share_numerator IS NOT NULL
   AND oi.share_denominator IS NOT NULL
   AND oi.dispute_status NOT IN ('disputed','unknown');
  IF v_matched_count<>v_input_count THEN
    RAISE EXCEPTION 'joint transfer entries must match every current undisputed registered ownership interest and its expected owner';
  END IF;

  IF EXISTS (
    SELECT 1
    FROM jsonb_to_recordset(v_transfers) AS x(
      ownership_interest_id text,
      expected_owner_organisation_id text,
      new_owner_organisation_id text
    )
    LEFT JOIN sw_property.organisation AS o
      ON o.organisation_id=x.new_owner_organisation_id
    WHERE o.organisation_id IS NULL
  ) THEN
    RAISE EXCEPTION 'every successor owner organisation must exist';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM sw_property.ownership_interest AS oi
    WHERE oi.ownership_interest_id=v_title.current_ownership_interest_id
      AND oi.property_id=p_property_id
      AND oi.interest_class='registered_ownership'
      AND oi.interest_status='current'
      AND oi.effective_to_tick IS NULL
  ) THEN
    RAISE EXCEPTION 'title lead interest must be included among current registered ownership interests';
  END IF;
  SELECT oi.owner_organisation_id INTO v_lead_prior_owner_id
  FROM sw_property.ownership_interest AS oi
  WHERE oi.ownership_interest_id=v_title.current_ownership_interest_id;
  SELECT x.new_owner_organisation_id INTO v_lead_new_owner_id
  FROM jsonb_to_recordset(v_transfers) AS x(
    ownership_interest_id text,
    expected_owner_organisation_id text,
    new_owner_organisation_id text
  )
  WHERE x.ownership_interest_id=v_title.current_ownership_interest_id;
  IF v_title.registered_proprietor_organisation_id IS DISTINCT FROM v_lead_prior_owner_id
     OR v_lead_new_owner_id IS NULL THEN
    RAISE EXCEPTION 'title register lead proprietor must match its current registered interest';
  END IF;

  IF v_title.active_dispute_count>0 OR v_title.unresolved_title_issue_count>0 THEN
    RAISE EXCEPTION 'joint title transfer is blocked by active title disputes or unresolved title issues';
  END IF;

  IF (SELECT count(*) FROM sw_property.property_rights_schedule AS prs
      WHERE prs.property_id=p_property_id
        AND prs.registered_ownership_interest_id=v_title.current_ownership_interest_id
        AND prs.registered_owner_organisation_id=v_lead_prior_owner_id)<>1 THEN
    RAISE EXCEPTION 'joint title transfer requires one matching property-rights schedule';
  END IF;

  FOR v_item IN
    SELECT x.ownership_interest_id,x.expected_owner_organisation_id,x.new_owner_organisation_id
    FROM jsonb_to_recordset(v_transfers) AS x(
      ownership_interest_id text,
      expected_owner_organisation_id text,
      new_owner_organisation_id text
    )
    ORDER BY x.ownership_interest_id
  LOOP
    SELECT oi.* INTO v_interest
    FROM sw_property.ownership_interest AS oi
    WHERE oi.ownership_interest_id=v_item.ownership_interest_id
      AND oi.property_id=p_property_id
    FOR UPDATE;
    IF NOT FOUND THEN RAISE EXCEPTION 'joint transfer interest disappeared during lock acquisition'; END IF;

    SELECT pir.* INTO v_interest_record
    FROM sw_property.property_interest_record AS pir
    WHERE pir.ownership_interest_id=v_interest.ownership_interest_id
      AND pir.interest_status='current'
      AND pir.interest_holder_organisation_id=v_item.expected_owner_organisation_id
    FOR UPDATE;
    IF NOT FOUND OR (SELECT count(*) FROM sw_property.property_interest_record AS pir
       WHERE pir.ownership_interest_id=v_interest.ownership_interest_id
         AND pir.interest_status='current')<>1 THEN
      RAISE EXCEPTION 'each joint registered interest requires exactly one current property-interest record';
    END IF;

    v_successor_interest_id := 'SWOI-GAME-' || replace(gen_random_uuid()::text,'-','');
    UPDATE sw_property.ownership_interest AS oi
    SET interest_status='historical',effective_to_tick=p_effective_tick,
        recorded_tick=p_recorded_tick
    WHERE oi.ownership_interest_id=v_interest.ownership_interest_id
      AND oi.owner_organisation_id=v_item.expected_owner_organisation_id
      AND oi.interest_status='current';
    GET DIAGNOSTICS v_rows=ROW_COUNT;
    IF v_rows<>1 THEN RAISE EXCEPTION 'joint transfer failed to close exactly one prior ownership interest'; END IF;

    INSERT INTO sw_property.ownership_interest(
      ownership_interest_id,property_id,owner_organisation_id,management_model,
      interest_type,source_dataset,interest_class,share_numerator,share_denominator,
      effective_from_tick,effective_to_tick,interest_status,dispute_status,
      dispute_reference,recorded_tick
    ) VALUES (
      v_successor_interest_id,p_property_id,v_item.new_owner_organisation_id,
      v_interest.management_model,v_interest.interest_type,
      'BP04-GAMEPLAY-JOINT-TITLE-TRANSFER','registered_ownership',
      v_interest.share_numerator,v_interest.share_denominator,
      p_effective_tick,NULL,'current','undisputed',NULL,p_recorded_tick
    );

    UPDATE sw_property.property_interest_record AS pir
    SET interest_status='historical'
    WHERE pir.ownership_interest_id=v_interest.ownership_interest_id
      AND pir.interest_status='current';
    GET DIAGNOSTICS v_rows=ROW_COUNT;
    IF v_rows<>1 THEN RAISE EXCEPTION 'joint transfer failed to close exactly one prior property-interest record'; END IF;

    INSERT INTO sw_property.property_interest_record(
      property_interest_record_id,property_id,ownership_interest_id,
      interest_holder_organisation_id,interest_type,interest_status,
      priority_order,source_basis,source_dataset
    ) VALUES (
      'SWPIR-GAME-' || replace(gen_random_uuid()::text,'-',''),
      p_property_id,v_successor_interest_id,v_item.new_owner_organisation_id,
      'registered_ownership','current',v_interest_record.priority_order,
      p_evidence_class,'BP04-GAMEPLAY-JOINT-TITLE-TRANSFER'
    );

    v_completed_transfers:=v_completed_transfers || jsonb_build_array(jsonb_build_object(
      'prior_ownership_interest_id',v_interest.ownership_interest_id,
      'successor_ownership_interest_id',v_successor_interest_id,
      'prior_owner_organisation_id',v_item.expected_owner_organisation_id,
      'successor_owner_organisation_id',v_item.new_owner_organisation_id,
      'share_numerator',v_interest.share_numerator,
      'share_denominator',v_interest.share_denominator
    ));
    IF v_interest.ownership_interest_id=v_title.current_ownership_interest_id THEN
      v_lead_successor_interest_id:=v_successor_interest_id;
    END IF;
  END LOOP;

  IF v_lead_successor_interest_id IS NULL THEN
    RAISE EXCEPTION 'joint transfer did not create the successor lead registered interest';
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

  v_event_id:='SWPLE-GAME-' || replace(gen_random_uuid()::text,'-','');
  v_instrument_id:='SWTI-GAME-' || replace(gen_random_uuid()::text,'-','');
  v_transaction_id:='SWPTX-GAME-' || replace(gen_random_uuid()::text,'-','');
  v_payload:=jsonb_build_object(
    'interest_transfers',v_transfers,
    'completed_interest_transfers',v_completed_transfers,
    'lead_prior_owner_organisation_id',v_lead_prior_owner_id,
    'lead_successor_owner_organisation_id',v_lead_new_owner_id,
    'lead_prior_ownership_interest_id',v_title.current_ownership_interest_id,
    'lead_successor_ownership_interest_id',v_lead_successor_interest_id,
    'title_instrument_id',v_instrument_id,
    'property_transaction_id',v_transaction_id,
    'financial_transaction_created',false,
    'tenancy_and_occupancy_mutated',false
  );

  INSERT INTO sw_property.property_lifecycle_event(
    lifecycle_event_id,property_id,event_type,effective_year,effective_tick,
    event_status,title_register_id,source_record_id,historical_date_known,
    financial_transaction_created,narrative,source_dataset,recorded_tick,recorded_year,
    actor_ref,source_ref,idempotency_key,evidence_class,event_payload
  ) VALUES (
    v_event_id,p_property_id,'joint_ownership_transferred',p_effective_year,p_effective_tick,
    'recorded',v_title.title_register_id,p_source_ref,true,false,
    'All current registered co-ownership interests transferred together; prior interests retained historically; tenancy and physical occupancy remain separate',
    'BP04-GAMEPLAY-JOINT-TITLE-TRANSFER',p_recorded_tick,p_recorded_year,
    p_actor_ref,p_source_ref,p_idempotency_key,p_evidence_class,v_payload
  );

  INSERT INTO sw_property.property_title_instrument(
    title_instrument_id,property_id,title_register_id,ownership_event_id,
    instrument_type,transferor_organisation_id,transferee_organisation_id,
    effective_year,recorded_year,instrument_status,source_basis,
    consideration_recorded_as_band_only,payment_or_settlement_record_created,source_dataset
  ) VALUES (
    v_instrument_id,p_property_id,v_title.title_register_id,v_event_id,
    'joint_ownership_transfer',v_lead_prior_owner_id,v_lead_new_owner_id,
    p_effective_year,p_recorded_year,'registered_current_chain',p_evidence_class,
    false,false,'BP04-GAMEPLAY-JOINT-TITLE-TRANSFER'
  );

  INSERT INTO sw_property.property_transaction_index(
    property_transaction_id,property_id,title_register_id,transaction_type,
    ownership_event_id,title_instrument_id,from_organisation_id,to_organisation_id,
    effective_year,recorded_year,transaction_status,consideration_band,
    financial_settlement_status,source_of_truth,source_dataset
  ) VALUES (
    v_transaction_id,p_property_id,v_title.title_register_id,'joint_ownership_transfer',
    v_event_id,v_instrument_id,v_lead_prior_owner_id,v_lead_new_owner_id,
    p_effective_year,p_recorded_year,'recorded',NULL,'not_created_bp34',
    'SW_PROPERTY_LIFECYCLE_EVENT','BP04-GAMEPLAY-JOINT-TITLE-TRANSFER'
  );

  INSERT INTO sw_property.property_title_transfer_interest(
    title_transfer_interest_id,title_instrument_id,property_id,
    prior_ownership_interest_id,successor_ownership_interest_id,
    prior_owner_organisation_id,successor_owner_organisation_id,
    share_numerator,share_denominator,effective_tick,recorded_tick,source_dataset
  )
  SELECT
    'SWPTI-GAME-' || replace(gen_random_uuid()::text,'-',''),
    v_instrument_id,p_property_id,
    x.prior_ownership_interest_id,x.successor_ownership_interest_id,
    x.prior_owner_organisation_id,x.successor_owner_organisation_id,
    x.share_numerator,x.share_denominator,p_effective_tick,p_recorded_tick,
    'BP04-GAMEPLAY-JOINT-TITLE-TRANSFER'
  FROM jsonb_to_recordset(v_completed_transfers) AS x(
    prior_ownership_interest_id text,
    successor_ownership_interest_id text,
    prior_owner_organisation_id text,
    successor_owner_organisation_id text,
    share_numerator bigint,
    share_denominator bigint
  );

  UPDATE sw_property.property_title_register AS ptr
  SET current_ownership_interest_id=v_lead_successor_interest_id,
      registered_proprietor_organisation_id=v_lead_new_owner_id,
      registration_tick=p_recorded_tick
  WHERE ptr.title_register_id=v_title.title_register_id
    AND ptr.current_ownership_interest_id=v_title.current_ownership_interest_id
    AND ptr.registered_proprietor_organisation_id=v_lead_prior_owner_id;
  GET DIAGNOSTICS v_rows=ROW_COUNT;
  IF v_rows<>1 THEN RAISE EXCEPTION 'joint transfer failed to update exactly one property title register'; END IF;

  UPDATE sw_property.property_rights_schedule AS prs
  SET registered_ownership_interest_id=v_lead_successor_interest_id,
      registered_owner_organisation_id=v_lead_new_owner_id
  WHERE prs.property_id=p_property_id
    AND prs.registered_ownership_interest_id=v_title.current_ownership_interest_id
    AND prs.registered_owner_organisation_id=v_lead_prior_owner_id;
  GET DIAGNOSTICS v_rows=ROW_COUNT;
  IF v_rows<>1 THEN RAISE EXCEPTION 'joint transfer failed to update exactly one property-rights schedule'; END IF;

  RETURN QUERY SELECT v_event_id,p_property_id,v_lead_new_owner_id;
END
$bp04$;

REVOKE ALL ON sw_property.property_title_transfer_interest FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_property.transfer_joint_property_ownership(
  text,jsonb,bigint,bigint,integer,integer,text,text,text,text
) FROM PUBLIC;
COMMIT;
