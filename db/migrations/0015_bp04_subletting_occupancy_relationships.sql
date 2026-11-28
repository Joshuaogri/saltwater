-- BP04-13 explicit subletting relationships.
-- A subtenant is a secondary occupancy relationship, never a second primary
-- business_unit_link. No permission is inferred: an explicit current right is required.
BEGIN;

CREATE TABLE sw_property.occupancy_relationship (
  relationship_id text PRIMARY KEY,
  property_id text NOT NULL REFERENCES sw_property.property_site(property_id)
    DEFERRABLE INITIALLY DEFERRED,
  unit_id text NOT NULL REFERENCES sw_property.unit_space(unit_id)
    DEFERRABLE INITIALLY DEFERRED,
  superior_agreement_id text NOT NULL REFERENCES sw_property.occupancy_agreement(agreement_id)
    DEFERRABLE INITIALLY DEFERRED,
  sub_agreement_id text NOT NULL REFERENCES sw_property.occupancy_agreement(agreement_id)
    DEFERRABLE INITIALLY DEFERRED,
  superior_occupancy_id text NOT NULL REFERENCES sw_property.occupancy(occupancy_id)
    DEFERRABLE INITIALLY DEFERRED,
  sub_occupancy_id text NOT NULL UNIQUE REFERENCES sw_property.occupancy(occupancy_id)
    DEFERRABLE INITIALLY DEFERRED,
  subletting_right_id text NOT NULL REFERENCES sw_property.contractual_rights_index(property_right_id)
    DEFERRABLE INITIALLY DEFERRED,
  granting_business_id text NOT NULL REFERENCES sw_property.business(business_id)
    DEFERRABLE INITIALLY DEFERRED,
  subtenant_business_id text NOT NULL REFERENCES sw_property.business(business_id)
    DEFERRABLE INITIALLY DEFERRED,
  effective_from_tick bigint NOT NULL CHECK (effective_from_tick>=0),
  recorded_tick bigint NOT NULL CHECK (recorded_tick>=0),
  effective_to_tick bigint,
  relationship_status text NOT NULL DEFAULT 'active'
    CHECK (relationship_status IN ('active','ended')),
  actor_ref text NOT NULL CHECK (length(trim(actor_ref)) BETWEEN 1 AND 200),
  source_ref text NOT NULL CHECK (length(trim(source_ref)) BETWEEN 1 AND 200),
  idempotency_key text NOT NULL UNIQUE
    CHECK (idempotency_key ~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'),
  end_idempotency_key text UNIQUE,
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  CHECK (superior_agreement_id<>sub_agreement_id),
  CHECK (granting_business_id<>subtenant_business_id),
  CHECK (effective_to_tick IS NULL OR effective_to_tick>effective_from_tick),
  CHECK ((relationship_status='active')=(effective_to_tick IS NULL)),
  CHECK ((relationship_status='ended')=(end_idempotency_key IS NOT NULL))
);
CREATE INDEX occupancy_relationship_superior_idx
  ON sw_property.occupancy_relationship(superior_agreement_id,relationship_status);
CREATE INDEX occupancy_relationship_subtenant_idx
  ON sw_property.occupancy_relationship(subtenant_business_id,relationship_status);

CREATE FUNCTION sw_property.guard_occupancy_relationship_history()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
BEGIN
  IF TG_OP='DELETE' THEN
    RAISE EXCEPTION 'occupancy relationship history cannot be deleted';
  END IF;
  IF ROW(NEW.relationship_id,NEW.property_id,NEW.unit_id,NEW.superior_agreement_id,
         NEW.sub_agreement_id,NEW.superior_occupancy_id,NEW.sub_occupancy_id,
         NEW.subletting_right_id,NEW.granting_business_id,NEW.subtenant_business_id,
         NEW.effective_from_tick,NEW.recorded_tick,NEW.actor_ref,NEW.source_ref,NEW.idempotency_key,NEW.created_at)
     IS DISTINCT FROM
     ROW(OLD.relationship_id,OLD.property_id,OLD.unit_id,OLD.superior_agreement_id,
         OLD.sub_agreement_id,OLD.superior_occupancy_id,OLD.sub_occupancy_id,
         OLD.subletting_right_id,OLD.granting_business_id,OLD.subtenant_business_id,
         OLD.effective_from_tick,OLD.recorded_tick,OLD.actor_ref,OLD.source_ref,OLD.idempotency_key,OLD.created_at)
     OR OLD.relationship_status<>'active'
     OR NEW.relationship_status<>'ended'
     OR NEW.effective_to_tick IS NULL
     OR NEW.end_idempotency_key IS NULL
     OR NEW.effective_to_tick<=OLD.effective_from_tick THEN
    RAISE EXCEPTION 'occupancy relationship permits only one append-backed end transition';
  END IF;
  RETURN NEW;
END
$bp04$;

CREATE TRIGGER occupancy_relationship_history_guard
BEFORE UPDATE OR DELETE ON sw_property.occupancy_relationship
FOR EACH ROW EXECUTE FUNCTION sw_property.guard_occupancy_relationship_history();

CREATE FUNCTION sw_property.record_subletting_relationship(
  p_relationship_id text,
  p_superior_agreement_id text,
  p_sub_agreement_id text,
  p_superior_occupancy_id text,
  p_sub_occupancy_id text,
  p_subletting_right_id text,
  p_effective_tick bigint,
  p_recorded_tick bigint,
  p_actor_ref text,
  p_source_ref text,
  p_idempotency_key text
) RETURNS TABLE(relationship_id text,relationship_status text)
LANGUAGE plpgsql AS $bp04$
DECLARE
  v_superior sw_property.occupancy_agreement%ROWTYPE;
  v_sub sw_property.occupancy_agreement%ROWTYPE;
  v_right sw_property.contractual_rights_index%ROWTYPE;
  v_superior_occupancy sw_property.occupancy%ROWTYPE;
  v_sub_occupancy sw_property.occupancy%ROWTYPE;
  v_prior sw_property.occupancy_relationship%ROWTYPE;
BEGIN
  IF p_relationship_id IS NULL OR length(trim(p_relationship_id)) NOT BETWEEN 1 AND 128
     OR p_effective_tick IS NULL OR p_effective_tick<0
     OR p_recorded_tick IS NULL OR p_recorded_tick<0
     OR p_actor_ref IS NULL OR length(trim(p_actor_ref)) NOT BETWEEN 1 AND 200
     OR p_source_ref IS NULL OR length(trim(p_source_ref)) NOT BETWEEN 1 AND 200
     OR p_idempotency_key IS NULL OR p_idempotency_key !~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$' THEN
    RAISE EXCEPTION 'invalid subletting relationship request';
  END IF;

  SELECT * INTO v_prior FROM sw_property.occupancy_relationship
  WHERE idempotency_key=p_idempotency_key;
  IF FOUND THEN
    IF v_prior.relationship_id<>p_relationship_id
       OR v_prior.superior_agreement_id<>p_superior_agreement_id
       OR v_prior.sub_agreement_id<>p_sub_agreement_id
       OR v_prior.superior_occupancy_id<>p_superior_occupancy_id
       OR v_prior.sub_occupancy_id<>p_sub_occupancy_id
       OR v_prior.subletting_right_id<>p_subletting_right_id
       OR v_prior.effective_from_tick<>p_effective_tick
       OR v_prior.recorded_tick<>p_recorded_tick
       OR v_prior.actor_ref<>p_actor_ref OR v_prior.source_ref<>p_source_ref THEN
      RAISE EXCEPTION 'subletting relationship idempotency key conflicts with prior definition';
    END IF;
    RETURN QUERY SELECT v_prior.relationship_id,v_prior.relationship_status;
    RETURN;
  END IF;

  -- Lock both agreements in a stable order to avoid reversed-pair deadlocks.
  PERFORM 1 FROM sw_property.occupancy_agreement
  WHERE agreement_id IN (p_superior_agreement_id,p_sub_agreement_id)
  ORDER BY agreement_id FOR UPDATE;
  SELECT * INTO v_superior FROM sw_property.occupancy_agreement
  WHERE agreement_id=p_superior_agreement_id;
  SELECT * INTO v_sub FROM sw_property.occupancy_agreement
  WHERE agreement_id=p_sub_agreement_id;
  IF v_superior.agreement_id IS NULL OR v_sub.agreement_id IS NULL THEN
    RAISE EXCEPTION 'superior and sub-agreements must both exist';
  END IF;
  IF v_superior.agreement_status NOT IN ('active','seasonal','temporarily_inactive')
     OR v_sub.agreement_status NOT IN ('active','seasonal','temporarily_inactive')
     OR v_sub.agreement_type NOT IN ('sublease','underlease') THEN
    RAISE EXCEPTION 'superior agreement must be current and secondary agreement must be an active sublease';
  END IF;
  IF v_superior.property_id<>v_sub.property_id OR v_superior.unit_id<>v_sub.unit_id
     OR v_superior.tenant_business_id IS NULL
     OR v_superior.tenant_business_id=v_sub.tenant_business_id THEN
    RAISE EXCEPTION 'sublease must preserve property/unit and identify a distinct subtenant';
  END IF;

  SELECT * INTO v_right FROM sw_property.contractual_rights_index
  WHERE property_right_id=p_subletting_right_id;
  IF NOT FOUND OR v_right.right_type<>'subletting'
     OR v_right.right_status<>'current'
     OR v_right.source_agreement_id<>p_superior_agreement_id
     OR v_right.property_id<>v_superior.property_id
     OR v_right.unit_id<>v_superior.unit_id
     OR v_right.holder_business_id IS DISTINCT FROM v_superior.tenant_business_id THEN
    RAISE EXCEPTION 'explicit current subletting right for this superior agreement, tenant and unit is required';
  END IF;

  SELECT * INTO v_superior_occupancy FROM sw_property.occupancy
  WHERE occupancy_id=p_superior_occupancy_id;
  SELECT * INTO v_sub_occupancy FROM sw_property.occupancy
  WHERE occupancy_id=p_sub_occupancy_id;
  IF NOT FOUND THEN RAISE EXCEPTION 'subtenant occupancy record not found'; END IF;
  IF v_superior_occupancy.occupancy_id IS NULL
     OR v_superior_occupancy.agreement_id<>p_superior_agreement_id
     OR v_superior_occupancy.unit_id<>v_superior.unit_id
     OR v_superior_occupancy.occupant_business_id<>v_superior.tenant_business_id
     OR v_superior_occupancy.effective_to_year IS NOT NULL THEN
    RAISE EXCEPTION 'superior occupancy must be current and match the superior tenant';
  END IF;
  IF v_sub_occupancy.occupancy_id IS NULL
     OR v_sub_occupancy.agreement_id<>p_sub_agreement_id
     OR v_sub_occupancy.unit_id<>v_sub.unit_id
     OR v_sub_occupancy.occupant_business_id<>v_sub.tenant_business_id
     OR v_sub_occupancy.occupant_type<>'business_subtenant'
     OR v_sub_occupancy.effective_to_year IS NOT NULL THEN
    RAISE EXCEPTION 'secondary occupancy must explicitly identify the subtenant and sublease';
  END IF;
  IF EXISTS (
    SELECT 1 FROM sw_property.business_unit_link
    WHERE business_id=v_sub.tenant_business_id
      AND unit_id=v_sub.unit_id AND valid_to_tick IS NULL
  ) THEN
    RAISE EXCEPTION 'subtenant cannot acquire a second primary business-unit link';
  END IF;

  INSERT INTO sw_property.occupancy_relationship(
    relationship_id,property_id,unit_id,superior_agreement_id,sub_agreement_id,
    superior_occupancy_id,sub_occupancy_id,subletting_right_id,
    granting_business_id,subtenant_business_id,effective_from_tick,
    actor_ref,source_ref,idempotency_key
  ) VALUES (
    p_relationship_id,v_superior.property_id,v_superior.unit_id,
    p_superior_agreement_id,p_sub_agreement_id,p_superior_occupancy_id,
    p_sub_occupancy_id,p_subletting_right_id,v_superior.tenant_business_id,
    v_sub.tenant_business_id,p_effective_tick,p_recorded_tick,p_actor_ref,p_source_ref,p_idempotency_key
  );

  PERFORM sw_property.append_occupancy_agreement_event(
    p_superior_agreement_id,'subletting_authorised',p_effective_tick,p_recorded_tick,
    p_actor_ref,p_source_ref,p_idempotency_key,'gameplay_action',NULL,p_sub_agreement_id,
    jsonb_build_object('relationship_id',p_relationship_id,
      'subletting_right_id',p_subletting_right_id,
      'granting_business_id',v_superior.tenant_business_id,
      'subtenant_business_id',v_sub.tenant_business_id)
  );
  RETURN QUERY SELECT p_relationship_id,'active'::text;
END
$bp04$;

CREATE FUNCTION sw_property.end_subletting_relationship(
  p_relationship_id text,
  p_effective_tick bigint,
  p_recorded_tick bigint,
  p_actor_ref text,
  p_source_ref text,
  p_idempotency_key text
) RETURNS TABLE(relationship_id text,relationship_status text)
LANGUAGE plpgsql AS $bp04$
DECLARE
  v_relationship sw_property.occupancy_relationship%ROWTYPE;
  v_prior_event sw_property.occupancy_agreement_event%ROWTYPE;
BEGIN
  IF p_relationship_id IS NULL OR p_effective_tick IS NULL OR p_effective_tick<0
     OR p_recorded_tick IS NULL OR p_recorded_tick<0
     OR p_actor_ref IS NULL OR length(trim(p_actor_ref)) NOT BETWEEN 1 AND 200
     OR p_source_ref IS NULL OR length(trim(p_source_ref)) NOT BETWEEN 1 AND 200
     OR p_idempotency_key IS NULL OR p_idempotency_key !~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$' THEN
    RAISE EXCEPTION 'invalid subletting end request';
  END IF;
  SELECT * INTO v_relationship FROM sw_property.occupancy_relationship
  WHERE relationship_id=p_relationship_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'occupancy relationship not found'; END IF;

  IF v_relationship.relationship_status='ended' THEN
    SELECT * INTO v_prior_event
    FROM sw_property.occupancy_agreement_event
    WHERE agreement_id=v_relationship.superior_agreement_id
      AND idempotency_key=p_idempotency_key;
    IF v_relationship.end_idempotency_key<>p_idempotency_key
       OR v_relationship.effective_to_tick<>p_effective_tick
       OR NOT FOUND
       OR v_prior_event.event_type<>'subletting_ended'
       OR v_prior_event.recorded_tick<>p_recorded_tick
       OR v_prior_event.actor_ref<>p_actor_ref
       OR v_prior_event.source_ref<>p_source_ref
       OR v_prior_event.event_payload->>'relationship_id' IS DISTINCT FROM p_relationship_id
       OR v_prior_event.event_payload->>'subtenant_business_id' IS DISTINCT FROM v_relationship.subtenant_business_id THEN
      RAISE EXCEPTION 'subletting end conflicts with prior terminal event';
    END IF;
    RETURN QUERY SELECT v_relationship.relationship_id,'ended'::text;
    RETURN;
  END IF;
  IF p_effective_tick<=v_relationship.effective_from_tick THEN
    RAISE EXCEPTION 'subletting end tick must follow relationship start';
  END IF;

  PERFORM sw_property.append_occupancy_agreement_event(
    v_relationship.superior_agreement_id,'subletting_ended',
    p_effective_tick,p_recorded_tick,p_actor_ref,p_source_ref,p_idempotency_key,
    'gameplay_action',NULL,v_relationship.sub_agreement_id,
    jsonb_build_object('relationship_id',p_relationship_id,
      'subtenant_business_id',v_relationship.subtenant_business_id)
  );
  UPDATE sw_property.occupancy_relationship
  SET relationship_status='ended',effective_to_tick=p_effective_tick,
      end_idempotency_key=p_idempotency_key
  WHERE relationship_id=p_relationship_id;
  -- The subtenant's physical occupancy is not ended by ending the legal
  -- relationship; a separate explicit occupancy action is required.
  RETURN QUERY SELECT p_relationship_id,'ended'::text;
END
$bp04$;

REVOKE ALL ON sw_property.occupancy_relationship FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_property.record_subletting_relationship(
  text,text,text,text,text,text,bigint,bigint,text,text,text
) FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_property.end_subletting_relationship(
  text,bigint,bigint,text,text,text
) FROM PUBLIC;
COMMIT;
