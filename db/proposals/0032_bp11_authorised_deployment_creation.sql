-- BP11 authorised deployment creation and crew assignment over canonical BP08.
-- Applied only by disposable CI until separately approved for production.
BEGIN;

CREATE OR REPLACE FUNCTION sw_police.create_authorised_unit_deployment(
  p_unit_id text,
  p_incident_id integer,
  p_membership_ids uuid[],
  p_objective text,
  p_priority smallint,
  p_actor_ref text,
  p_authority_ref text,
  p_source_ref text,
  p_idempotency_key text,
  p_effective_tick bigint
) RETURNS TABLE(deployment_id uuid,status text,unit_id text,assigned_members integer,event_id bigint)
LANGUAGE plpgsql AS $bp11$
DECLARE
  v_runtime sw_runtime.state%ROWTYPE;
  v_incident sw_incident.incident%ROWTYPE;
  v_readiness sw_police.unit_readiness%ROWTYPE;
  v_profile sw_police.unit_profile%ROWTYPE;
  v_deployment_id uuid;
  v_event_id bigint;
  v_existing sw_police.unit_deployment%ROWTYPE;
  v_member_count integer;
BEGIN
  IF p_unit_id IS NULL OR length(trim(p_unit_id))=0
     OR p_incident_id IS NULL OR p_incident_id<1
     OR p_membership_ids IS NULL
     OR cardinality(p_membership_ids)=0
     OR cardinality(p_membership_ids)<>(SELECT count(DISTINCT x) FROM unnest(p_membership_ids) x)
     OR p_objective IS NULL OR length(trim(p_objective))=0 OR length(p_objective)>1000
     OR p_priority IS NULL OR p_priority NOT BETWEEN 1 AND 5
     OR p_actor_ref IS NULL OR p_actor_ref !~ '^officer-person:[1-9][0-9]*$'
     OR p_authority_ref IS NULL OR length(trim(p_authority_ref))=0 OR length(p_authority_ref)>200
     OR p_source_ref IS NULL OR length(trim(p_source_ref))=0 OR length(p_source_ref)>200
     OR p_idempotency_key IS NULL OR p_idempotency_key !~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'
     OR p_effective_tick IS NULL OR p_effective_tick<0 THEN
    RAISE EXCEPTION 'invalid authorised deployment definition';
  END IF;

  SELECT * INTO v_runtime FROM sw_runtime.state WHERE singleton=1 FOR UPDATE;
  IF NOT FOUND OR v_runtime.state<>2 OR NOT v_runtime.player_present THEN
    RAISE EXCEPTION 'deployment creation requires running player-present simulation';
  END IF;
  IF p_effective_tick<v_runtime.world_tick THEN
    RAISE EXCEPTION 'deployment effective tick is behind world clock';
  END IF;

  SELECT * INTO v_existing FROM sw_police.unit_deployment
  WHERE idempotency_key=p_idempotency_key;
  IF FOUND THEN
    IF v_existing.unit_id<>p_unit_id OR v_existing.task_ref<>(
        SELECT incident_ref FROM sw_incident.incident WHERE incident_id=p_incident_id)
       OR v_existing.objective<>p_objective OR v_existing.priority<>p_priority
       OR v_existing.issuing_personnel_id IS DISTINCT FROM
          (SELECT personnel_id FROM sw_police.personnel_service_current
           WHERE person_id=substring(p_actor_ref from 16)::integer LIMIT 1) THEN
      RAISE EXCEPTION 'deployment idempotency key conflicts with prior definition';
    END IF;
    RETURN QUERY SELECT v_existing.deployment_id,v_existing.status,v_existing.unit_id,
      (SELECT count(*)::integer FROM sw_police.unit_deployment_member m
       WHERE m.deployment_id=v_existing.deployment_id),v_existing.source_event_id;
    RETURN;
  END IF;

  SELECT * INTO v_incident FROM sw_incident.incident
  WHERE incident_id=p_incident_id FOR UPDATE;
  IF NOT FOUND OR v_incident.status NOT IN ('ASSESSED','ALLOCATED') THEN
    RAISE EXCEPTION 'incident must be assessed or allocated before deployment';
  END IF;

  SELECT * INTO v_profile FROM sw_police.unit_profile
  WHERE unit_id=p_unit_id FOR SHARE;
  IF NOT FOUND OR v_profile.lifecycle_state<>'active' OR NOT v_profile.dispatchable THEN
    RAISE EXCEPTION 'unit is not an active dispatch unit';
  END IF;
  SELECT * INTO v_readiness FROM sw_police.unit_readiness
  WHERE unit_id=p_unit_id;
  IF NOT FOUND OR v_readiness.dispatch_eligible IS DISTINCT FROM true
     OR v_readiness.operational_status<>'available'
     OR v_readiness.resources_ready IS DISTINCT FROM true THEN
    RAISE EXCEPTION 'unit is not dispatch eligible: %',coalesce(v_readiness.readiness_reason,'readiness_unknown');
  END IF;

  SELECT count(*)::integer INTO v_member_count
  FROM sw_police.unit_membership m
  JOIN sw_police.personnel_service_current p USING(personnel_id)
  WHERE m.membership_id=ANY(p_membership_ids)
    AND m.unit_id=p_unit_id AND m.actual_end_tick IS NULL
    AND p.service_state IN ('active','probationary');
  IF v_member_count<>cardinality(p_membership_ids)
     OR v_member_count<v_profile.minimum_crew_size THEN
    RAISE EXCEPTION 'crew membership is invalid or below minimum staffing';
  END IF;
  IF EXISTS (
    SELECT 1 FROM sw_police.unit_deployment d
    WHERE d.unit_id=p_unit_id AND d.status IN
      ('authorised','issued','acknowledged','mobilising','active','paused')
  ) THEN RAISE EXCEPTION 'unit already has an active deployment'; END IF;

  v_deployment_id:=gen_random_uuid();
  v_event_id:=sw_runtime.submit_event_work(
    'UNIT_DEPLOYMENT_AUTHORISED','police','bp08:deployment:create',1,1,
    p_effective_tick,p_priority,p_idempotency_key,p_actor_ref,'bp08',
    p_source_ref,NULL,v_deployment_id,'police_operational',5
  );

  INSERT INTO sw_police.unit_deployment(
    deployment_id,unit_id,deployment_type,task_ref,location_ref,geographic_scope,
    objective,issuing_personnel_id,authority_ref,start_tick,status,priority,
    source_event_id,idempotency_key,source_ref
  ) VALUES (
    v_deployment_id,p_unit_id,'incident',v_incident.incident_ref,
    (SELECT location_ref FROM sw_incident.incident_location
     WHERE incident_id=p_incident_id AND location_role='primary'
     ORDER BY effective_tick DESC,incident_location_id DESC LIMIT 1),
    'SALTWATER_CITY_STATE',p_objective,
    (SELECT personnel_id FROM sw_police.personnel_service_current
     WHERE person_id=substring(p_actor_ref from 16)::integer LIMIT 1),
    p_authority_ref,p_effective_tick,'authorised',p_priority,v_event_id,
    p_idempotency_key,p_source_ref
  );

  INSERT INTO sw_police.unit_deployment_event(
    deployment_id,source_event_id,event_kind,prior_status,resulting_status,
    effective_tick,actor_ref,authority_ref,reason,source_ref
  ) VALUES (
    v_deployment_id,v_event_id,'authorised',NULL,'authorised',
    p_effective_tick,p_actor_ref,p_authority_ref,p_objective,p_source_ref
  );

  INSERT INTO sw_police.unit_deployment_member(
    deployment_id,membership_id,assigned_tick,role_code,source_ref
  )
  SELECT v_deployment_id,m.membership_id,p_effective_tick,'incident_response',p_source_ref
  FROM sw_police.unit_membership m
  WHERE m.membership_id=ANY(p_membership_ids);

  RETURN QUERY SELECT v_deployment_id,'authorised'::text,p_unit_id,v_member_count,v_event_id;
END
$bp11$;

COMMIT;
