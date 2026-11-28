-- BP04-36: distinguish business opening schedules from observed operating state.
-- A published schedule never proves that an establishment is currently open.
BEGIN;

CREATE TABLE sw_property.business_operational_event (
  event_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id text NOT NULL REFERENCES sw_property.business(business_id)
    DEFERRABLE INITIALLY DEFERRED,
  establishment_id text NOT NULL REFERENCES sw_property.establishment(establishment_id)
    DEFERRABLE INITIALLY DEFERRED,
  event_type text NOT NULL CHECK (event_type IN (
    'business_opened','business_closed','business_temporarily_closed',
    'business_reopened','availability_changed','capacity_changed'
  )),
  effective_tick bigint NOT NULL CHECK (effective_tick>=0),
  recorded_tick bigint NOT NULL CHECK (recorded_tick>=0),
  actor_ref text NOT NULL CHECK (length(trim(actor_ref)) BETWEEN 1 AND 200),
  source_ref text NOT NULL CHECK (length(trim(source_ref)) BETWEEN 1 AND 200),
  idempotency_key text NOT NULL UNIQUE
    CHECK (idempotency_key ~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'),
  event_payload jsonb NOT NULL DEFAULT '{}'::jsonb
    CHECK (jsonb_typeof(event_payload)='object'),
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);
CREATE INDEX business_operational_event_history_idx
  ON sw_property.business_operational_event(establishment_id,effective_tick,recorded_tick,event_id);

CREATE FUNCTION sw_property.validate_business_operational_event()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
DECLARE
  v_actual_status text;
  v_temporary_closure boolean;
  v_capacity numeric;
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM sw_property.establishment e
    WHERE e.establishment_id=NEW.establishment_id
      AND e.business_id=NEW.business_id
  ) THEN
    RAISE EXCEPTION 'business operational event must match the establishment owner';
  END IF;

  IF NEW.event_type IN (
    'business_opened','business_closed','business_temporarily_closed',
    'business_reopened','availability_changed'
  ) THEN
    v_actual_status := NEW.event_payload->>'actual_status';
    IF v_actual_status IS NULL OR v_actual_status NOT IN
       ('open','limited','closed','temporarily_closed','unavailable','unknown') THEN
      RAISE EXCEPTION 'business operational event requires an explicit actual_status';
    END IF;
    IF jsonb_typeof(NEW.event_payload->'temporary_closure') IS DISTINCT FROM 'boolean' THEN
      RAISE EXCEPTION 'business operational event requires an explicit temporary_closure boolean';
    END IF;
    v_temporary_closure := (NEW.event_payload->>'temporary_closure')::boolean;

    IF NEW.event_type='business_opened'
       AND (v_actual_status<>'open' OR v_temporary_closure) THEN
      RAISE EXCEPTION 'business_opened must record open status without a temporary closure';
    ELSIF NEW.event_type='business_closed'
       AND (v_actual_status<>'closed' OR v_temporary_closure) THEN
      RAISE EXCEPTION 'business_closed must record closed status without a temporary closure';
    ELSIF NEW.event_type='business_temporarily_closed'
       AND (v_actual_status<>'temporarily_closed' OR NOT v_temporary_closure) THEN
      RAISE EXCEPTION 'temporary business closure must be explicitly identified';
    ELSIF NEW.event_type='business_reopened'
       AND (v_actual_status<>'open' OR v_temporary_closure) THEN
      RAISE EXCEPTION 'business_reopened must record open status and clear temporary closure';
    END IF;
  ELSIF NEW.event_type='capacity_changed' THEN
    IF jsonb_typeof(NEW.event_payload->'capacity_value') IS DISTINCT FROM 'number'
       OR jsonb_typeof(NEW.event_payload->'capacity_unit') IS DISTINCT FROM 'string'
       OR length(trim(NEW.event_payload->>'capacity_unit'))=0 THEN
      RAISE EXCEPTION 'business capacity change requires a numeric value and explicit unit';
    END IF;
    v_capacity := (NEW.event_payload->>'capacity_value')::numeric;
    IF v_capacity<0 THEN RAISE EXCEPTION 'business capacity cannot be negative'; END IF;
  END IF;
  RETURN NEW;
END
$bp04$;
CREATE TRIGGER business_operational_event_guard
BEFORE INSERT ON sw_property.business_operational_event
FOR EACH ROW EXECUTE FUNCTION sw_property.validate_business_operational_event();

CREATE FUNCTION sw_property.reject_business_operational_event_mutation()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
BEGIN
  RAISE EXCEPTION 'business operational event history is append-only';
END
$bp04$;
CREATE TRIGGER business_operational_event_immutable
BEFORE UPDATE OR DELETE ON sw_property.business_operational_event
FOR EACH ROW EXECUTE FUNCTION sw_property.reject_business_operational_event_mutation();

CREATE VIEW sw_property.business_operational_state AS
SELECT
  s.business_id,
  s.establishment_id,
  s.day_number,
  s.day_of_week,
  s.is_open_to_customers AS scheduled_open_to_customers,
  s.customer_open_time AS scheduled_customer_open_time,
  s.customer_close_time AS scheduled_customer_close_time,
  s.service_window AS scheduled_service_window,
  s.delivery_window_start AS scheduled_delivery_window_start,
  s.delivery_window_end AS scheduled_delivery_window_end,
  CASE
    WHEN operational_event.event_id IS NULL THEN 'unknown'
    ELSE operational_event.event_payload->>'actual_status'
  END AS actual_operating_status,
  CASE
    WHEN operational_event.event_id IS NULL THEN NULL
    ELSE (operational_event.event_payload->>'temporary_closure')::boolean
  END AS temporary_closure,
  CASE WHEN operational_event.event_id IS NULL THEN 'not_observed' ELSE 'business_event' END
    AS actual_state_source,
  operational_event.event_type AS latest_operational_event_type,
  operational_event.event_id AS latest_operational_event_id,
  operational_event.effective_tick AS latest_operational_effective_tick,
  operational_event.recorded_tick AS latest_operational_recorded_tick,
  operational_event.source_ref AS latest_operational_source_ref,
  (capacity_event.event_payload->>'capacity_value')::numeric AS current_capacity_value,
  capacity_event.event_payload->>'capacity_unit' AS current_capacity_unit,
  capacity_event.event_id AS latest_capacity_event_id,
  capacity_event.effective_tick AS latest_capacity_effective_tick
FROM sw_property.business_daily_schedule AS s
LEFT JOIN LATERAL (
  SELECT e.* FROM sw_property.business_operational_event AS e
  WHERE e.establishment_id=s.establishment_id
    AND e.event_type<>'capacity_changed'
  ORDER BY e.effective_tick DESC,e.recorded_tick DESC,e.created_at DESC,e.event_id DESC
  LIMIT 1
) AS operational_event ON true
LEFT JOIN LATERAL (
  SELECT e.* FROM sw_property.business_operational_event AS e
  WHERE e.establishment_id=s.establishment_id
    AND e.event_type='capacity_changed'
  ORDER BY e.effective_tick DESC,e.recorded_tick DESC,e.created_at DESC,e.event_id DESC
  LIMIT 1
) AS capacity_event ON true;

COMMENT ON VIEW sw_property.business_operational_state IS
  'Separates published opening/delivery schedules from event-observed business operating state and independently event-recorded capacity. No observation means actual status is unknown.';

COMMIT;
