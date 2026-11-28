-- BP04-35: separate published schedules/capacity from observed service availability.
-- Operational state is event-derived; a timetable or profile is not proof of service.
BEGIN;

CREATE FUNCTION sw_property.validate_facility_service_event_payload()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
DECLARE
  v_availability text;
  v_temporary_closure boolean;
  v_capacity numeric;
  v_capacity_unit text;
BEGIN
  IF NEW.event_type IN (
    'service_activated','service_suspended','service_disrupted',
    'service_restored','service_withdrawn','availability_changed'
  ) THEN
    v_availability := NEW.event_payload->>'availability_status';
    IF v_availability IS NULL OR v_availability NOT IN
       ('available','limited','unavailable','unknown') THEN
      RAISE EXCEPTION 'operational availability events require an explicit availability_status';
    END IF;
    IF jsonb_typeof(NEW.event_payload->'temporary_closure') IS DISTINCT FROM 'boolean' THEN
      RAISE EXCEPTION 'operational availability events require an explicit temporary_closure boolean';
    END IF;
    v_temporary_closure := (NEW.event_payload->>'temporary_closure')::boolean;
    IF NEW.event_type IN ('service_activated','service_restored')
       AND v_temporary_closure THEN
      RAISE EXCEPTION 'activation/restoration cannot leave a temporary closure active';
    END IF;
    IF NEW.event_type='service_suspended'
       AND (v_availability<>'unavailable' OR NOT v_temporary_closure) THEN
      RAISE EXCEPTION 'service suspension must record unavailable status and temporary closure';
    END IF;
    IF NEW.event_type='service_withdrawn'
       AND (v_availability<>'unavailable' OR v_temporary_closure) THEN
      RAISE EXCEPTION 'service withdrawal must be unavailable and not marked temporary';
    END IF;
  ELSIF NEW.event_type='capacity_changed' THEN
    IF jsonb_typeof(NEW.event_payload->'capacity_value') IS DISTINCT FROM 'number'
       OR jsonb_typeof(NEW.event_payload->'capacity_unit') IS DISTINCT FROM 'string'
       OR length(trim(NEW.event_payload->>'capacity_unit'))=0 THEN
      RAISE EXCEPTION 'capacity changes require a numeric value and explicit unit';
    END IF;
    v_capacity := (NEW.event_payload->>'capacity_value')::numeric;
    v_capacity_unit := NEW.event_payload->>'capacity_unit';
    IF v_capacity<0 THEN RAISE EXCEPTION 'service capacity cannot be negative'; END IF;
  END IF;
  RETURN NEW;
END
$bp04$;

CREATE TRIGGER facility_service_event_payload_guard
BEFORE INSERT ON sw_property.facility_service_event
FOR EACH ROW EXECUTE FUNCTION sw_property.validate_facility_service_event_payload();

CREATE VIEW sw_property.facility_service_operational_state AS
SELECT
  f.facility_id,
  f.facility_type,
  f.facility_status,
  f.availability_status AS declared_facility_availability_status,
  f.capacity_value AS declared_facility_capacity_value,
  f.capacity_unit AS declared_facility_capacity_unit,
  s.service_id,
  s.service_type,
  s.service_status,
  s.availability_status AS declared_service_availability_status,
  s.bp37_schedule_ref AS planned_schedule_ref,
  CASE
    WHEN f.facility_status IN ('planned','temporarily_closed','closed','under_construction')
      OR s.service_status IN ('planned','suspended','withdrawn') THEN 'unavailable'
    WHEN availability_event.event_id IS NULL THEN 'unknown'
    ELSE availability_event.event_payload->>'availability_status'
  END AS actual_availability_status,
  CASE
    WHEN f.facility_status='temporarily_closed' OR s.service_status='suspended' THEN true
    WHEN f.facility_status IN ('planned','closed','under_construction')
      OR s.service_status IN ('planned','withdrawn') THEN false
    WHEN availability_event.event_id IS NULL THEN NULL
    ELSE (availability_event.event_payload->>'temporary_closure')::boolean
  END AS temporary_closure,
  CASE
    WHEN f.facility_status IN ('planned','temporarily_closed','closed','under_construction')
      OR s.service_status IN ('planned','suspended','withdrawn') THEN 'facility_or_service_status'
    WHEN availability_event.event_id IS NULL THEN 'not_observed'
    ELSE 'service_event'
  END AS actual_state_source,
  availability_event.event_type AS latest_availability_event_type,
  availability_event.event_id AS latest_availability_event_id,
  availability_event.effective_tick AS latest_availability_effective_tick,
  availability_event.recorded_tick AS latest_availability_recorded_tick,
  availability_event.source_ref AS latest_availability_source_ref,
  COALESCE((capacity_event.event_payload->>'capacity_value')::numeric,s.capacity_value)
    AS current_capacity_value,
  COALESCE(capacity_event.event_payload->>'capacity_unit',s.capacity_unit)
    AS current_capacity_unit,
  capacity_event.event_id AS latest_capacity_event_id,
  capacity_event.effective_tick AS latest_capacity_effective_tick
FROM sw_property.facility_service AS s
JOIN sw_property.facility AS f ON f.facility_id=s.facility_id
LEFT JOIN LATERAL (
  SELECT e.* FROM sw_property.facility_service_event AS e
  WHERE e.service_id=s.service_id
    AND e.event_type IN (
      'service_activated','service_suspended','service_disrupted',
      'service_restored','service_withdrawn','availability_changed'
    )
  ORDER BY e.effective_tick DESC,e.recorded_tick DESC,e.created_at DESC,e.event_id DESC
  LIMIT 1
) AS availability_event ON true
LEFT JOIN LATERAL (
  SELECT e.* FROM sw_property.facility_service_event AS e
  WHERE e.service_id=s.service_id AND e.event_type='capacity_changed'
  ORDER BY e.effective_tick DESC,e.recorded_tick DESC,e.created_at DESC,e.event_id DESC
  LIMIT 1
) AS capacity_event ON true;

COMMENT ON VIEW sw_property.facility_service_operational_state IS
  'Separates planned BP37 timetable references and declared capacity/availability from event-observed operational state. No observation means actual availability is unknown.';

INSERT INTO sw_ops.schema_migration(version,migration_name)
VALUES (35,'bp04_facility_operational_state')
ON CONFLICT(version) DO NOTHING;

COMMIT;
