\set ON_ERROR_STOP on
BEGIN;

INSERT INTO sw_property.organisation(
 organisation_id,display_name,organisation_type,registered_city,status,source_dataset
) VALUES
 ('SWD03-OWNER','BP04 D03 Facility Owner','property_holding_company','Saltwater','active','bp04_d03_acceptance'),
 ('SWD03-OPERATOR','BP04 D03 Multi-service Operator','service_operator','Saltwater','active','bp04_d03_acceptance');

INSERT INTO sw_property.property_site(
 property_id,display_name,use_class,lifecycle_status,source_dataset
) VALUES ('SWD03-SITE','BP04 D03 Multi-service Campus','institutional','active','bp04_d03_acceptance');

INSERT INTO sw_property.facility(
 facility_id,owner_organisation_id,operator_organisation_id,property_id,
 facility_type,facility_status,availability_status,capacity_value,capacity_unit,
 bp37_schedule_ref,source_dataset
) VALUES
 ('SWD03-HEALTH','SWD03-OWNER','SWD03-OPERATOR','SWD03-SITE','healthcare','active','available',80,'beds','BP37-SCHEDULE-HEALTH','bp04_d03_acceptance'),
 ('SWD03-TRANSIT','SWD03-OWNER','SWD03-OPERATOR','SWD03-SITE','transport_terminal','active','available',1200,'passengers_per_hour','BP37-SCHEDULE-TRANSIT','bp04_d03_acceptance'),
 ('SWD03-UTILITY','SWD03-OWNER','SWD03-OPERATOR','SWD03-SITE','utility','active','available',1,'network','BP37-SCHEDULE-UTILITY','bp04_d03_acceptance'),
 ('SWD03-EDUCATION','SWD03-OWNER','SWD03-OPERATOR','SWD03-SITE','education','active','available',900,'learners','BP37-SCHEDULE-EDUCATION','bp04_d03_acceptance'),
 ('SWD03-SHELTER','SWD03-OWNER','SWD03-OPERATOR','SWD03-SITE','shelter','active','available',250,'places','BP37-SCHEDULE-SHELTER','bp04_d03_acceptance'),
 ('SWD03-EMERGENCY','SWD03-OWNER','SWD03-OPERATOR','SWD03-SITE','emergency_service','active','available',20,'response_units','BP37-SCHEDULE-EMERGENCY','bp04_d03_acceptance'),
 ('SWD03-LOGISTICS','SWD03-OWNER','SWD03-OPERATOR','SWD03-SITE','logistics','active','available',40,'loads_per_hour','BP37-SCHEDULE-LOGISTICS','bp04_d03_acceptance');

INSERT INTO sw_property.facility_service(
 service_id,facility_id,service_type,service_status,availability_status,
 capacity_value,capacity_unit,bp37_schedule_ref,source_dataset
) VALUES
 ('SWD03-HEALTH-SVC','SWD03-HEALTH','emergency_care','active','available',20,'patients_per_hour','BP37-TIMETABLE-HEALTH','bp04_d03_acceptance'),
 ('SWD03-TRANSIT-SVC','SWD03-TRANSIT','public_transport','active','available',12,'vehicles','BP37-TIMETABLE-TRANSIT','bp04_d03_acceptance'),
 ('SWD03-UTILITY-SVC','SWD03-UTILITY','utility','active','available',1,'network','BP37-TIMETABLE-UTILITY','bp04_d03_acceptance'),
 ('SWD03-EDUCATION-SVC','SWD03-EDUCATION','education','active','available',900,'learners','BP37-TIMETABLE-EDUCATION','bp04_d03_acceptance'),
 ('SWD03-SHELTER-SVC','SWD03-SHELTER','shelter','active','available',250,'places','BP37-TIMETABLE-SHELTER','bp04_d03_acceptance'),
 ('SWD03-EMERGENCY-SVC','SWD03-EMERGENCY','other','active','available',20,'response_units','BP37-TIMETABLE-EMERGENCY','bp04_d03_acceptance'),
 ('SWD03-LOGISTICS-SVC','SWD03-LOGISTICS','logistics','active','available',40,'loads_per_hour','BP37-TIMETABLE-LOGISTICS','bp04_d03_acceptance');

DO $bp04$
DECLARE v_count integer;
BEGIN
  SELECT count(*) INTO v_count
  FROM sw_property.facility_service_operational_state
  WHERE actual_availability_status='unknown'
    AND declared_service_availability_status='available'
    AND planned_schedule_ref IS NOT NULL
    AND actual_state_source='not_observed';
  IF v_count<>7 THEN
    RAISE EXCEPTION 'planned schedules/profile availability were incorrectly treated as actual service observations; unknown count %',v_count;
  END IF;
END
$bp04$;

INSERT INTO sw_property.facility_service_event(
 service_id,event_type,effective_tick,recorded_tick,actor_ref,source_ref,
 idempotency_key,event_payload
) VALUES (
 'SWD03-TRANSIT-SVC','service_suspended',10,10,'npc:transit-operations',
 'generated:d03-temporary-closure','swd03:transit:suspend:01',
 '{"availability_status":"unavailable","temporary_closure":true,"reason":"temporary operational closure"}'::jsonb
);

DO $bp04$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM sw_property.facility_service_operational_state
    WHERE service_id='SWD03-TRANSIT-SVC'
      AND actual_availability_status='unavailable'
      AND temporary_closure IS TRUE
      AND latest_availability_event_type='service_suspended'
      AND actual_state_source='service_event'
  ) THEN RAISE EXCEPTION 'temporary service closure was not reflected in observed operational state'; END IF;
END
$bp04$;

INSERT INTO sw_property.facility_service_event(
 service_id,event_type,effective_tick,recorded_tick,actor_ref,source_ref,
 idempotency_key,event_payload
) VALUES (
 'SWD03-TRANSIT-SVC','service_restored',20,20,'npc:transit-operations',
 'generated:d03-service-restoration','swd03:transit:restore:01',
 '{"availability_status":"available","temporary_closure":false,"reason":"service restored"}'::jsonb
);

INSERT INTO sw_property.facility_service_event(
 service_id,event_type,effective_tick,recorded_tick,actor_ref,source_ref,
 idempotency_key,event_payload
) VALUES (
 'SWD03-TRANSIT-SVC','capacity_changed',21,21,'npc:transit-operations',
 'generated:d03-capacity-change','swd03:transit:capacity:01',
 '{"capacity_value":6,"capacity_unit":"vehicles"}'::jsonb
);

DO $bp04$
DECLARE v_blocked boolean:=false;
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM sw_property.facility_service_operational_state
    WHERE service_id='SWD03-TRANSIT-SVC'
      AND actual_availability_status='available'
      AND temporary_closure IS FALSE
      AND current_capacity_value=6
      AND current_capacity_unit='vehicles'
      AND latest_availability_event_type='service_restored'
  ) THEN RAISE EXCEPTION 'restored availability and updated capacity were not independently resolved'; END IF;

  IF (SELECT capacity_value FROM sw_property.facility_service WHERE service_id='SWD03-TRANSIT-SVC')<>12 THEN
    RAISE EXCEPTION 'capacity event mutated the declared profile instead of preserving event history';
  END IF;

  BEGIN
    INSERT INTO sw_property.facility_service_event(
      service_id,event_type,effective_tick,recorded_tick,actor_ref,source_ref,
      idempotency_key,event_payload
    ) VALUES (
      'SWD03-TRANSIT-SVC','service_disrupted',30,30,'npc:transit-operations',
      'generated:d03-invalid-event','swd03:transit:invalid:01',
      '{"reason":"missing observed availability"}'::jsonb
    );
  EXCEPTION WHEN raise_exception THEN
    v_blocked:=true;
  END;
  IF NOT v_blocked THEN RAISE EXCEPTION 'availability event without explicit actual status was accepted'; END IF;

  v_blocked:=false;
  BEGIN
    INSERT INTO sw_property.facility_service_event(
      service_id,event_type,effective_tick,recorded_tick,actor_ref,source_ref,
      idempotency_key,event_payload
    ) VALUES (
      'SWD03-TRANSIT-SVC','capacity_changed',31,31,'npc:transit-operations',
      'generated:d03-invalid-capacity','swd03:transit:invalid-capacity:01',
      '{"capacity_value":-1,"capacity_unit":"vehicles"}'::jsonb
    );
  EXCEPTION WHEN raise_exception THEN
    v_blocked:=true;
  END;
  IF NOT v_blocked THEN RAISE EXCEPTION 'negative capacity event was accepted'; END IF;

  v_blocked:=false;
  BEGIN
    UPDATE sw_property.facility_service_event
    SET event_type='service_disrupted'
    WHERE idempotency_key='swd03:transit:restore:01';
  EXCEPTION WHEN raise_exception THEN
    v_blocked:=true;
  END;
  IF NOT v_blocked THEN RAISE EXCEPTION 'facility operational event history was mutable'; END IF;
END
$bp04$;

ROLLBACK;
SELECT 'BP04 actual availability, capacity, schedule and temporary closure acceptance passed' AS result;
