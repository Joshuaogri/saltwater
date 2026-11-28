\set ON_ERROR_STOP on
BEGIN;
INSERT INTO sw_property.organisation(
 organisation_id,display_name,organisation_type,registered_city,status,source_dataset
) VALUES
 ('SWF-OWNER','NPC Facility Owner','property_holding_company','Saltwater','active','bp04_facility_service_acceptance'),
 ('SWF-HEALTH','NPC Healthcare Operator','healthcare_provider','Saltwater','active','bp04_facility_service_acceptance'),
 ('SWF-TRANSIT','NPC Transport Operator','transport_operator','Saltwater','active','bp04_facility_service_acceptance'),
 ('SWF-UTILITY','NPC Power Provider','utility_provider','Saltwater','active','bp04_facility_service_acceptance');
INSERT INTO sw_property.property_site(property_id,display_name,use_class,lifecycle_status,source_dataset)
VALUES ('SWF-SITE','NPC Service Campus','institutional','active','bp04_facility_service_acceptance');

INSERT INTO sw_property.facility(
 facility_id,owner_organisation_id,operator_organisation_id,property_id,
 facility_type,facility_status,availability_status,capacity_value,capacity_unit,source_dataset
) VALUES
 ('SWF-CLINIC','SWF-OWNER','SWF-HEALTH','SWF-SITE','healthcare','active','available',80,'beds','bp04_facility_service_acceptance'),
 ('SWF-TERMINAL','SWF-OWNER','SWF-TRANSIT','SWF-SITE','transport_terminal','active','available',1200,'passengers_per_hour','bp04_facility_service_acceptance');

INSERT INTO sw_property.facility_service(
 service_id,facility_id,service_type,service_status,availability_status,
 capacity_value,capacity_unit,bp37_schedule_ref,source_dataset
) VALUES
 ('SWF-EMERGENCY-CARE','SWF-CLINIC','emergency_care','active','available',20,'patients_per_hour','SW37-HEALTH-SCHEDULE','bp04_facility_service_acceptance'),
 ('SWF-BUS-SERVICE','SWF-TERMINAL','public_transport','active','limited',12,'vehicles','SW37-TRANSIT-SCHEDULE','bp04_facility_service_acceptance');

INSERT INTO sw_property.healthcare_service_profile(
 service_id,emergency_care_capability,appointment_availability,referral_availability,
 practitioner_role_profile,public_health_alert_ref,treatment_event_metadata_only,source_dataset
) VALUES (
 'SWF-EMERGENCY-CARE','full_emergency','available','available',
 '{"roles":["emergency_physician","nurse","paramedic"]}'::jsonb,
 'SW35-HEALTH-ALERT-REF-01',true,'bp04_facility_service_acceptance'
);

INSERT INTO sw_property.transport_service_profile(
 service_id,bp02_route_ref,ordered_stop_refs,bp37_timetable_ref,fleet_profile,
 accessibility_profile,service_restrictions,disruption_status,source_dataset
) VALUES (
 'SWF-BUS-SERVICE','SW02-ROUTE-REF-01',
 ARRAY['SW02-STOP-001','SW02-STOP-002','SW02-STOP-003'],
 'SW37-TIMETABLE-REF-01',
 '{"vehicle_class":"city_bus","available_vehicles":8}'::jsonb,
 '{"wheelchair_accessible":true,"step_free":true}'::jsonb,
 ARRAY['heavy_goods_prohibited'],'normal','bp04_facility_service_acceptance'
);

INSERT INTO sw_property.facility_dependency(
 dependency_id,facility_id,provider_organisation_id,dependency_type,
 provider_service_ref,dependency_status,effective_from_tick,source_dataset
) VALUES (
 'SWF-CLINIC-POWER','SWF-CLINIC','SWF-UTILITY','power',
 'SW04-UTILITY-SERVICE-REF','active',0,'bp04_facility_service_acceptance'
);

INSERT INTO sw_property.facility_service_event(
 service_id,event_type,effective_tick,recorded_tick,actor_ref,source_ref,idempotency_key,event_payload
) VALUES (
 'SWF-BUS-SERVICE','service_disrupted',10,10,'npc:transit-operations',
 'generated:transit-disruption','swf:transit:disruption:01',
 '{"reason":"NPC operational disruption","service_impact":"reduced_frequency"}'::jsonb
);

DO $bp04$
DECLARE v_count integer;
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM sw_property.facility
    WHERE facility_id='SWF-CLINIC' AND owner_organisation_id='SWF-OWNER'
      AND operator_organisation_id='SWF-HEALTH'
  ) THEN RAISE EXCEPTION 'facility owner/operator roles were conflated'; END IF;
  IF NOT EXISTS (
    SELECT 1 FROM sw_property.healthcare_service_profile
    WHERE service_id='SWF-EMERGENCY-CARE' AND treatment_event_metadata_only
      AND emergency_care_capability='full_emergency'
  ) THEN RAISE EXCEPTION 'healthcare service profile is incomplete'; END IF;
  IF NOT EXISTS (
    SELECT 1 FROM sw_property.transport_service_profile
    WHERE service_id='SWF-BUS-SERVICE' AND bp02_route_ref='SW02-ROUTE-REF-01'
      AND bp37_timetable_ref='SW37-TIMETABLE-REF-01'
      AND cardinality(ordered_stop_refs)=3
  ) THEN RAISE EXCEPTION 'transport profile does not link BP02 route/stops and BP37 timetable'; END IF;
  IF NOT EXISTS (
    SELECT 1 FROM sw_property.facility_dependency
    WHERE facility_id='SWF-CLINIC' AND provider_organisation_id='SWF-UTILITY'
      AND dependency_type='power'
  ) THEN RAISE EXCEPTION 'facility essential-service dependency missing'; END IF;
  SELECT count(*) INTO v_count FROM sw_property.facility_service_event
  WHERE service_id='SWF-BUS-SERVICE' AND event_type='service_disrupted';
  IF v_count<>1 THEN RAISE EXCEPTION 'transport disruption event missing'; END IF;
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema='sw_property' AND table_name='healthcare_service_profile'
      AND column_name IN ('patient_name','diagnosis','clinical_notes','medical_record')
  ) THEN RAISE EXCEPTION 'BP04 healthcare profile duplicated BP03/clinical chart data'; END IF;
  BEGIN
    UPDATE sw_property.facility_service_event SET event_type='service_restored'
    WHERE service_id='SWF-BUS-SERVICE';
    RAISE EXCEPTION 'facility service event history allowed mutation';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='facility service event history allowed mutation' THEN RAISE; END IF;
    IF SQLERRM NOT LIKE '%append-only%' THEN RAISE; END IF;
  END;
END
$bp04$;
ROLLBACK;
SELECT 'BP04 organisation, facility, healthcare, transport and dependency acceptance passed' AS result;
