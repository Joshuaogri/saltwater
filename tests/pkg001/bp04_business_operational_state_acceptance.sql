\set ON_ERROR_STOP on
BEGIN;
SET CONSTRAINTS ALL DEFERRED;

INSERT INTO sw_property.property_site(
 property_id,display_name,use_class,lifecycle_status,source_dataset
) VALUES ('SWD36-SITE','BP04 D36 Business Operations Site','mixed_use','active','bp04_d36_acceptance');
INSERT INTO sw_property.premises(
 premises_id,property_id,display_name,premises_use,lifecycle_status,source_dataset
) VALUES ('SWD36-PREM','SWD36-SITE','BP04 D36 Business Premises','commercial','active','bp04_d36_acceptance');
INSERT INTO sw_property.unit_space(
 unit_id,property_id,premises_id,display_name,unit_class,use_class,lifecycle_status,source_dataset
) VALUES ('SWD36-UNIT','SWD36-SITE','SWD36-PREM','BP04 D36 Business Unit','commercial','commercial','active','bp04_d36_acceptance');

INSERT INTO sw_property.business(
 business_id,display_name,sector,status,primary_establishment_id,source_dataset
) VALUES
 ('SWD36-BUS-HEALTH','D36 Healthcare Business','healthcare','active','SWD36-EST-HEALTH','bp04_d36_acceptance'),
 ('SWD36-BUS-TRANSPORT','D36 Transport Business','transport_logistics','active','SWD36-EST-TRANSPORT','bp04_d36_acceptance'),
 ('SWD36-BUS-FOOD','D36 Hospitality Business','food_hospitality','active','SWD36-EST-FOOD','bp04_d36_acceptance'),
 ('SWD36-BUS-FINANCE','D36 Finance Business','finance_insurance','active','SWD36-EST-FINANCE','bp04_d36_acceptance'),
 ('SWD36-BUS-MANUFACTURING','D36 Manufacturing Business','manufacturing','active','SWD36-EST-MANUFACTURING','bp04_d36_acceptance'),
 ('SWD36-BUS-MARITIME','D36 Maritime Business','maritime_trade','active','SWD36-EST-MARITIME','bp04_d36_acceptance'),
 ('SWD36-BUS-CREATIVE','D36 Creative Business','creative_entertainment','active','SWD36-EST-CREATIVE','bp04_d36_acceptance');

INSERT INTO sw_property.establishment(
 establishment_id,business_id,property_id,premises_id,unit_id,display_name,
 establishment_type,status,source_dataset
) VALUES
 ('SWD36-EST-HEALTH','SWD36-BUS-HEALTH','SWD36-SITE','SWD36-PREM','SWD36-UNIT','D36 Healthcare Establishment','primary','active','bp04_d36_acceptance'),
 ('SWD36-EST-TRANSPORT','SWD36-BUS-TRANSPORT','SWD36-SITE','SWD36-PREM','SWD36-UNIT','D36 Transport Establishment','primary','active','bp04_d36_acceptance'),
 ('SWD36-EST-FOOD','SWD36-BUS-FOOD','SWD36-SITE','SWD36-PREM','SWD36-UNIT','D36 Hospitality Establishment','primary','active','bp04_d36_acceptance'),
 ('SWD36-EST-FINANCE','SWD36-BUS-FINANCE','SWD36-SITE','SWD36-PREM','SWD36-UNIT','D36 Finance Establishment','primary','active','bp04_d36_acceptance'),
 ('SWD36-EST-MANUFACTURING','SWD36-BUS-MANUFACTURING','SWD36-SITE','SWD36-PREM','SWD36-UNIT','D36 Manufacturing Establishment','primary','active','bp04_d36_acceptance'),
 ('SWD36-EST-MARITIME','SWD36-BUS-MARITIME','SWD36-SITE','SWD36-PREM','SWD36-UNIT','D36 Maritime Establishment','primary','active','bp04_d36_acceptance'),
 ('SWD36-EST-CREATIVE','SWD36-BUS-CREATIVE','SWD36-SITE','SWD36-PREM','SWD36-UNIT','D36 Creative Establishment','primary','active','bp04_d36_acceptance');

INSERT INTO sw_property.business_daily_schedule(
 business_schedule_id,business_id,establishment_id,day_of_week,day_number,
 operating_status,is_open_to_customers,customer_open_time,customer_close_time,
 service_window,staff_shift_pattern,delivery_window_start,delivery_window_end,
 emergency_contact_route,valid_from_tick,valid_to_tick,source_generator,source_dataset
)
SELECT 'SWD36-SCHEDULE-'||business_id,business_id,primary_establishment_id,
 'monday',0,'scheduled_open',true,'08:00','17:00','weekday customer hours',
 'day shift',NULL,NULL,'dispatch contact',0,NULL,'bp04_d36_fixture','bp04_d36_acceptance'
FROM sw_property.business
WHERE business_id LIKE 'SWD36-BUS-%';

DO $bp04$
DECLARE v_count integer;
BEGIN
  SELECT count(*) INTO v_count
  FROM sw_property.business_operational_state
  WHERE scheduled_open_to_customers IS TRUE
    AND scheduled_customer_open_time='08:00'
    AND scheduled_customer_close_time='17:00'
    AND actual_operating_status='unknown'
    AND actual_state_source='not_observed';
  IF v_count<>7 THEN
    RAISE EXCEPTION 'planned business schedules were incorrectly treated as actual opening; unknown count %',v_count;
  END IF;
END
$bp04$;

INSERT INTO sw_property.business_operational_event(
 business_id,establishment_id,event_type,effective_tick,recorded_tick,
 actor_ref,source_ref,idempotency_key,event_payload
) VALUES (
 'SWD36-BUS-FOOD','SWD36-EST-FOOD','business_temporarily_closed',10,10,
 'npc:food-business-manager','generated:d36-temporary-closure','swd36:food:closure:01',
 '{"actual_status":"temporarily_closed","temporary_closure":true,"reason":"temporary premises closure"}'::jsonb
);

DO $bp04$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM sw_property.business_operational_state
    WHERE business_id='SWD36-BUS-FOOD'
      AND scheduled_open_to_customers IS TRUE
      AND actual_operating_status='temporarily_closed'
      AND temporary_closure IS TRUE
      AND latest_operational_event_type='business_temporarily_closed'
  ) THEN RAISE EXCEPTION 'temporary business closure did not override schedule as actual state'; END IF;
END
$bp04$;

INSERT INTO sw_property.business_operational_event(
 business_id,establishment_id,event_type,effective_tick,recorded_tick,
 actor_ref,source_ref,idempotency_key,event_payload
) VALUES (
 'SWD36-BUS-FOOD','SWD36-EST-FOOD','business_reopened',20,20,
 'npc:food-business-manager','generated:d36-business-reopened','swd36:food:reopen:01',
 '{"actual_status":"open","temporary_closure":false,"reason":"business reopened"}'::jsonb
);

INSERT INTO sw_property.business_operational_event(
 business_id,establishment_id,event_type,effective_tick,recorded_tick,
 actor_ref,source_ref,idempotency_key,event_payload
) VALUES (
 'SWD36-BUS-FOOD','SWD36-EST-FOOD','capacity_changed',21,21,
 'npc:food-business-manager','generated:d36-capacity-change','swd36:food:capacity:01',
 '{"capacity_value":45,"capacity_unit":"seats"}'::jsonb
);

DO $bp04$
DECLARE v_blocked boolean:=false;
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM sw_property.business_operational_state
    WHERE business_id='SWD36-BUS-FOOD'
      AND scheduled_open_to_customers IS TRUE
      AND actual_operating_status='open'
      AND temporary_closure IS FALSE
      AND current_capacity_value=45
      AND current_capacity_unit='seats'
      AND latest_operational_event_type='business_reopened'
  ) THEN RAISE EXCEPTION 'business reopening and capacity were not independently reflected'; END IF;

  BEGIN
    INSERT INTO sw_property.business_operational_event(
      business_id,establishment_id,event_type,effective_tick,recorded_tick,
      actor_ref,source_ref,idempotency_key,event_payload
    ) VALUES (
      'SWD36-BUS-FOOD','SWD36-EST-FOOD','availability_changed',30,30,
      'npc:food-business-manager','generated:d36-invalid-state','swd36:food:invalid:01',
      '{"temporary_closure":false}'::jsonb
    );
  EXCEPTION WHEN raise_exception THEN v_blocked:=true;
  END;
  IF NOT v_blocked THEN RAISE EXCEPTION 'business availability event without actual status was accepted'; END IF;

  v_blocked:=false;
  BEGIN
    INSERT INTO sw_property.business_operational_event(
      business_id,establishment_id,event_type,effective_tick,recorded_tick,
      actor_ref,source_ref,idempotency_key,event_payload
    ) VALUES (
      'SWD36-BUS-FOOD','SWD36-EST-FOOD','capacity_changed',31,31,
      'npc:food-business-manager','generated:d36-invalid-capacity','swd36:food:invalid-capacity:01',
      '{"capacity_value":-1,"capacity_unit":"seats"}'::jsonb
    );
  EXCEPTION WHEN raise_exception THEN v_blocked:=true;
  END;
  IF NOT v_blocked THEN RAISE EXCEPTION 'negative business capacity was accepted'; END IF;

  v_blocked:=false;
  BEGIN
    UPDATE sw_property.business_operational_event
    SET event_type='business_closed'
    WHERE idempotency_key='swd36:food:reopen:01';
  EXCEPTION WHEN raise_exception THEN v_blocked:=true;
  END;
  IF NOT v_blocked THEN RAISE EXCEPTION 'business operational event history was mutable'; END IF;
END
$bp04$;

ROLLBACK;
SELECT 'BP04 business schedule, actual opening, temporary closure and capacity acceptance passed' AS result;
