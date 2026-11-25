-- BP04 phase 7: business operating schedules for time-aware police gameplay.
-- Disposable PostgreSQL benchmark only; never apply to production Neon.
BEGIN;
CREATE TABLE sw_property.business_weekly_profile (
  business_id text PRIMARY KEY REFERENCES sw_property.business(business_id) DEFERRABLE INITIALLY DEFERRED,
  establishment_id text NOT NULL REFERENCES sw_property.establishment(establishment_id) DEFERRABLE INITIALLY DEFERRED,
  weekly_open_days smallint NOT NULL CHECK (weekly_open_days BETWEEN 0 AND 7),
  weekly_closed_days smallint NOT NULL CHECK (weekly_closed_days BETWEEN 0 AND 7),
  has_continuous_service boolean NOT NULL,
  has_appointment_service boolean NOT NULL,
  valid_from_tick bigint NOT NULL,
  source_dataset text NOT NULL
);
CREATE TABLE sw_property.business_daily_schedule (
  business_schedule_id text PRIMARY KEY,
  business_id text NOT NULL REFERENCES sw_property.business(business_id) DEFERRABLE INITIALLY DEFERRED,
  establishment_id text NOT NULL REFERENCES sw_property.establishment(establishment_id) DEFERRABLE INITIALLY DEFERRED,
  day_of_week text NOT NULL CHECK (day_of_week IN ('monday','tuesday','wednesday','thursday','friday','saturday','sunday')),
  day_number smallint NOT NULL CHECK (day_number BETWEEN 0 AND 6),
  operating_status text NOT NULL,
  is_open_to_customers boolean NOT NULL,
  customer_open_time time,
  customer_close_time time,
  service_window text NOT NULL,
  staff_shift_pattern text NOT NULL,
  delivery_window_start time,
  delivery_window_end time,
  emergency_contact_route text NOT NULL,
  valid_from_tick bigint NOT NULL,
  valid_to_tick bigint,
  source_generator text NOT NULL,
  source_dataset text NOT NULL,
  UNIQUE (business_id, day_number),
  CHECK (valid_to_tick IS NULL OR valid_to_tick >= valid_from_tick),
  CHECK ((is_open_to_customers AND customer_open_time IS NOT NULL AND customer_close_time IS NOT NULL)
      OR (NOT is_open_to_customers AND customer_open_time IS NULL AND customer_close_time IS NULL))
);
CREATE INDEX business_daily_schedule_business_day_idx ON sw_property.business_daily_schedule(business_id, day_number);
CREATE INDEX business_daily_schedule_open_idx ON sw_property.business_daily_schedule(day_number, customer_open_time) WHERE is_open_to_customers;
COMMIT;
