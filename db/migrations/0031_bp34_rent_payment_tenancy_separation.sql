-- BP34 minimal NPC rent, charge, payment and allocation ledger.
-- Tenancy and physical occupancy remain BP04-owned and are never changed here.
BEGIN;
CREATE SCHEMA IF NOT EXISTS sw_finance;

CREATE TABLE sw_finance.rent_schedule (
  schedule_id text PRIMARY KEY,
  agreement_id text NOT NULL REFERENCES sw_property.occupancy_agreement(agreement_id)
    DEFERRABLE INITIALLY DEFERRED,
  payer_business_id text NOT NULL REFERENCES sw_property.business(business_id)
    DEFERRABLE INITIALLY DEFERRED,
  payee_organisation_id text NOT NULL REFERENCES sw_property.organisation(organisation_id)
    DEFERRABLE INITIALLY DEFERRED,
  currency_code char(3) NOT NULL CHECK (currency_code ~ '^[A-Z]{3}$'),
  recurring_amount_minor bigint NOT NULL CHECK (recurring_amount_minor>0),
  frequency text NOT NULL CHECK (frequency IN ('weekly','monthly','quarterly','annual','one_off')),
  period_length_ticks bigint NOT NULL CHECK (period_length_ticks>0),
  effective_from_tick bigint NOT NULL CHECK (effective_from_tick>=0),
  effective_to_tick bigint,
  schedule_status text NOT NULL CHECK (schedule_status IN ('active','superseded','ended')),
  source_ref text NOT NULL CHECK (length(trim(source_ref)) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(trim(actor_ref)) BETWEEN 1 AND 200),
  idempotency_key text NOT NULL UNIQUE,
  supersedes_schedule_id text REFERENCES sw_finance.rent_schedule(schedule_id)
    DEFERRABLE INITIALLY DEFERRED,
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  CHECK (effective_to_tick IS NULL OR effective_to_tick>effective_from_tick),
  CHECK ((schedule_status='active')=(effective_to_tick IS NULL))
);
CREATE INDEX rent_schedule_agreement_idx ON sw_finance.rent_schedule(agreement_id,effective_from_tick);

CREATE FUNCTION sw_finance.guard_rent_schedule()
RETURNS trigger LANGUAGE plpgsql AS $fin$
DECLARE v_agreement sw_property.occupancy_agreement%ROWTYPE;
BEGIN
  IF TG_OP<>'INSERT' THEN RAISE EXCEPTION 'rent schedule versions are append-only; supersede with a new version'; END IF;
  SELECT a.* INTO v_agreement FROM sw_property.occupancy_agreement AS a
  WHERE a.agreement_id=NEW.agreement_id FOR UPDATE;
  IF NOT FOUND OR v_agreement.tenant_business_id<>NEW.payer_business_id
     OR v_agreement.landlord_organisation_id<>NEW.payee_organisation_id THEN
    RAISE EXCEPTION 'BP34 rent schedule payer/payee must match BP04 tenant/landlord parties';
  END IF;
  IF NEW.supersedes_schedule_id IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM sw_finance.rent_schedule old
    WHERE old.schedule_id=NEW.supersedes_schedule_id AND old.agreement_id=NEW.agreement_id
  ) THEN RAISE EXCEPTION 'superseded rent schedule must belong to the same agreement'; END IF;
  IF EXISTS (
    SELECT 1 FROM sw_finance.rent_schedule old
    WHERE old.agreement_id=NEW.agreement_id AND old.schedule_status='active'
      AND old.effective_from_tick<COALESCE(NEW.effective_to_tick,9223372036854775807)
      AND NEW.effective_from_tick<COALESCE(old.effective_to_tick,9223372036854775807)
  ) THEN RAISE EXCEPTION 'active rent schedule intervals cannot overlap'; END IF;
  RETURN NEW;
END
$fin$;
CREATE TRIGGER rent_schedule_guard
BEFORE INSERT OR UPDATE OR DELETE ON sw_finance.rent_schedule
FOR EACH ROW EXECUTE FUNCTION sw_finance.guard_rent_schedule();

CREATE TABLE sw_finance.rent_charge (
  charge_id text PRIMARY KEY,
  schedule_id text NOT NULL REFERENCES sw_finance.rent_schedule(schedule_id)
    DEFERRABLE INITIALLY DEFERRED,
  agreement_id text NOT NULL REFERENCES sw_property.occupancy_agreement(agreement_id)
    DEFERRABLE INITIALLY DEFERRED,
  period_start_tick bigint NOT NULL CHECK (period_start_tick>=0),
  period_end_tick bigint NOT NULL CHECK (period_end_tick>period_start_tick),
  due_tick bigint NOT NULL CHECK (due_tick>=period_start_tick),
  amount_minor bigint NOT NULL CHECK (amount_minor>0),
  currency_code char(3) NOT NULL CHECK (currency_code ~ '^[A-Z]{3}$'),
  source_ref text NOT NULL CHECK (length(trim(source_ref)) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(trim(actor_ref)) BETWEEN 1 AND 200),
  idempotency_key text NOT NULL UNIQUE,
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  UNIQUE(schedule_id,period_start_tick,period_end_tick)
);
CREATE FUNCTION sw_finance.guard_rent_charge()
RETURNS trigger LANGUAGE plpgsql AS $fin$
DECLARE v_schedule sw_finance.rent_schedule%ROWTYPE;
BEGIN
  IF TG_OP<>'INSERT' THEN RAISE EXCEPTION 'rent charges are immutable financial records'; END IF;
  SELECT s.* INTO v_schedule FROM sw_finance.rent_schedule AS s
  WHERE s.schedule_id=NEW.schedule_id FOR UPDATE;
  IF NOT FOUND OR v_schedule.agreement_id<>NEW.agreement_id
     OR v_schedule.schedule_status<>'active'
     OR NEW.period_start_tick<v_schedule.effective_from_tick
     OR (v_schedule.effective_to_tick IS NOT NULL AND NEW.period_end_tick>v_schedule.effective_to_tick)
     OR NEW.currency_code<>v_schedule.currency_code
     OR NEW.amount_minor<>v_schedule.recurring_amount_minor THEN
    RAISE EXCEPTION 'rent charge must match the active BP34 schedule and agreement period';
  END IF;
  RETURN NEW;
END
$fin$;
CREATE TRIGGER rent_charge_guard
BEFORE INSERT OR UPDATE OR DELETE ON sw_finance.rent_charge
FOR EACH ROW EXECUTE FUNCTION sw_finance.guard_rent_charge();

CREATE TABLE sw_finance.rent_payment (
  payment_id text PRIMARY KEY,
  payer_business_id text NOT NULL REFERENCES sw_property.business(business_id)
    DEFERRABLE INITIALLY DEFERRED,
  payee_organisation_id text NOT NULL REFERENCES sw_property.organisation(organisation_id)
    DEFERRABLE INITIALLY DEFERRED,
  amount_minor bigint NOT NULL CHECK (amount_minor>0),
  currency_code char(3) NOT NULL CHECK (currency_code ~ '^[A-Z]{3}$'),
  paid_tick bigint NOT NULL CHECK (paid_tick>=0),
  payment_method text NOT NULL CHECK (payment_method IN ('cash','bank_transfer','card','internal_transfer','other')),
  payment_reference text,
  source_ref text NOT NULL CHECK (length(trim(source_ref)) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(trim(actor_ref)) BETWEEN 1 AND 200),
  idempotency_key text NOT NULL UNIQUE,
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);
CREATE FUNCTION sw_finance.reject_rent_payment_mutation()
RETURNS trigger LANGUAGE plpgsql AS $fin$
BEGIN RAISE EXCEPTION 'rent payment transactions are append-only'; END
$fin$;
CREATE TRIGGER rent_payment_immutable
BEFORE UPDATE OR DELETE ON sw_finance.rent_payment
FOR EACH ROW EXECUTE FUNCTION sw_finance.reject_rent_payment_mutation();

CREATE TABLE sw_finance.rent_payment_allocation (
  allocation_id text PRIMARY KEY,
  payment_id text NOT NULL REFERENCES sw_finance.rent_payment(payment_id)
    DEFERRABLE INITIALLY DEFERRED,
  charge_id text NOT NULL REFERENCES sw_finance.rent_charge(charge_id)
    DEFERRABLE INITIALLY DEFERRED,
  amount_minor bigint NOT NULL CHECK (amount_minor>0),
  currency_code char(3) NOT NULL CHECK (currency_code ~ '^[A-Z]{3}$'),
  allocated_tick bigint NOT NULL CHECK (allocated_tick>=0),
  source_ref text NOT NULL CHECK (length(trim(source_ref)) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(trim(actor_ref)) BETWEEN 1 AND 200),
  idempotency_key text NOT NULL UNIQUE,
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);
CREATE FUNCTION sw_finance.guard_rent_payment_allocation()
RETURNS trigger LANGUAGE plpgsql AS $fin$
DECLARE
  v_payment sw_finance.rent_payment%ROWTYPE;
  v_charge sw_finance.rent_charge%ROWTYPE;
  v_schedule sw_finance.rent_schedule%ROWTYPE;
  v_allocated_payment bigint;
  v_allocated_charge bigint;
BEGIN
  IF TG_OP<>'INSERT' THEN RAISE EXCEPTION 'rent payment allocations are immutable'; END IF;
  SELECT p.* INTO v_payment FROM sw_finance.rent_payment AS p
  WHERE p.payment_id=NEW.payment_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'rent payment not found'; END IF;
  SELECT c.* INTO v_charge FROM sw_finance.rent_charge AS c
  WHERE c.charge_id=NEW.charge_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'rent charge not found'; END IF;
  SELECT s.* INTO v_schedule FROM sw_finance.rent_schedule AS s
  WHERE s.schedule_id=v_charge.schedule_id;
  IF v_payment.payer_business_id<>v_schedule.payer_business_id
     OR v_payment.payee_organisation_id<>v_schedule.payee_organisation_id
     OR v_payment.currency_code<>v_charge.currency_code
     OR NEW.currency_code<>v_payment.currency_code THEN
    RAISE EXCEPTION 'rent payment and charge payer/payee/currency do not match';
  END IF;
  SELECT COALESCE(sum(a.amount_minor),0) INTO v_allocated_payment
  FROM sw_finance.rent_payment_allocation AS a WHERE a.payment_id=NEW.payment_id;
  SELECT COALESCE(sum(a.amount_minor),0) INTO v_allocated_charge
  FROM sw_finance.rent_payment_allocation AS a WHERE a.charge_id=NEW.charge_id;
  IF v_allocated_payment+NEW.amount_minor>v_payment.amount_minor THEN
    RAISE EXCEPTION 'rent payment cannot be allocated above its received amount';
  END IF;
  IF v_allocated_charge+NEW.amount_minor>v_charge.amount_minor THEN
    RAISE EXCEPTION 'rent charge cannot be overpaid';
  END IF;
  RETURN NEW;
END
$fin$;
CREATE TRIGGER rent_payment_allocation_guard
BEFORE INSERT OR UPDATE OR DELETE ON sw_finance.rent_payment_allocation
FOR EACH ROW EXECUTE FUNCTION sw_finance.guard_rent_payment_allocation();

CREATE VIEW sw_finance.rent_charge_balance AS
SELECT c.charge_id,c.schedule_id,c.agreement_id,c.period_start_tick,c.period_end_tick,
       c.due_tick,c.amount_minor,c.currency_code,
       COALESCE(sum(a.amount_minor),0)::bigint AS allocated_minor,
       (c.amount_minor-COALESCE(sum(a.amount_minor),0))::bigint AS outstanding_minor,
       CASE WHEN COALESCE(sum(a.amount_minor),0)=0 THEN 'unpaid'
            WHEN COALESCE(sum(a.amount_minor),0)<c.amount_minor THEN 'partially_paid'
            ELSE 'paid' END AS derived_payment_state
FROM sw_finance.rent_charge AS c
LEFT JOIN sw_finance.rent_payment_allocation AS a ON a.charge_id=c.charge_id
GROUP BY c.charge_id,c.schedule_id,c.agreement_id,c.period_start_tick,c.period_end_tick,
         c.due_tick,c.amount_minor,c.currency_code;

CREATE VIEW sw_finance.agreement_rent_balance AS
SELECT agreement_id,currency_code,sum(amount_minor)::bigint AS charged_minor,
       sum(allocated_minor)::bigint AS allocated_minor,
       sum(outstanding_minor)::bigint AS outstanding_minor
FROM sw_finance.rent_charge_balance
GROUP BY agreement_id,currency_code;

CREATE FUNCTION sw_finance.record_rent_payment(
  p_payment_id text,p_payer_business_id text,p_payee_organisation_id text,
  p_amount_minor bigint,p_currency_code char(3),p_paid_tick bigint,
  p_payment_method text,p_payment_reference text,p_source_ref text,p_actor_ref text,
  p_idempotency_key text
) RETURNS text LANGUAGE plpgsql AS $fin$
DECLARE v_existing sw_finance.rent_payment%ROWTYPE;
BEGIN
  IF p_payment_id IS NULL OR p_payer_business_id IS NULL OR p_payee_organisation_id IS NULL
     OR p_amount_minor IS NULL OR p_amount_minor<=0 OR p_currency_code !~ '^[A-Z]{3}$'
     OR p_paid_tick IS NULL OR p_paid_tick<0 OR p_payment_method NOT IN ('cash','bank_transfer','card','internal_transfer','other')
     OR p_source_ref IS NULL OR length(trim(p_source_ref)) NOT BETWEEN 1 AND 200
     OR p_actor_ref IS NULL OR length(trim(p_actor_ref)) NOT BETWEEN 1 AND 200
     OR p_idempotency_key IS NULL OR length(trim(p_idempotency_key)) NOT BETWEEN 1 AND 128 THEN
    RAISE EXCEPTION 'invalid rent payment request';
  END IF;
  SELECT p.* INTO v_existing FROM sw_finance.rent_payment AS p
  WHERE p.idempotency_key=p_idempotency_key;
  IF FOUND THEN
    IF ROW(v_existing.payment_id,v_existing.payer_business_id,v_existing.payee_organisation_id,
      v_existing.amount_minor,v_existing.currency_code,v_existing.paid_tick,v_existing.payment_method,
      v_existing.payment_reference,v_existing.source_ref,v_existing.actor_ref)
      IS DISTINCT FROM
      ROW(p_payment_id,p_payer_business_id,p_payee_organisation_id,p_amount_minor,p_currency_code,
      p_paid_tick,p_payment_method,p_payment_reference,p_source_ref,p_actor_ref) THEN
      RAISE EXCEPTION 'rent payment idempotency key conflicts with prior payment';
    END IF;
    RETURN v_existing.payment_id;
  END IF;
  INSERT INTO sw_finance.rent_payment(
    payment_id,payer_business_id,payee_organisation_id,amount_minor,currency_code,
    paid_tick,payment_method,payment_reference,source_ref,actor_ref,idempotency_key
  ) VALUES (
    p_payment_id,p_payer_business_id,p_payee_organisation_id,p_amount_minor,p_currency_code,
    p_paid_tick,p_payment_method,p_payment_reference,p_source_ref,p_actor_ref,p_idempotency_key
  );
  RETURN p_payment_id;
EXCEPTION WHEN unique_violation THEN
  SELECT p.* INTO v_existing FROM sw_finance.rent_payment AS p
  WHERE p.idempotency_key=p_idempotency_key;
  IF FOUND AND ROW(v_existing.payment_id,v_existing.amount_minor,v_existing.payer_business_id,
     v_existing.payee_organisation_id,v_existing.currency_code,v_existing.paid_tick)
     IS NOT DISTINCT FROM ROW(p_payment_id,p_amount_minor,p_payer_business_id,
     p_payee_organisation_id,p_currency_code,p_paid_tick) THEN
    RETURN v_existing.payment_id;
  END IF;
  RAISE;
END
$fin$;

CREATE FUNCTION sw_finance.allocate_rent_payment(
  p_allocation_id text,p_payment_id text,p_charge_id text,p_amount_minor bigint,
  p_allocated_tick bigint,p_source_ref text,p_actor_ref text,p_idempotency_key text
) RETURNS text LANGUAGE plpgsql AS $fin$
DECLARE v_existing sw_finance.rent_payment_allocation%ROWTYPE;
BEGIN
  IF p_allocation_id IS NULL OR p_payment_id IS NULL OR p_charge_id IS NULL
     OR p_amount_minor IS NULL OR p_amount_minor<=0 OR p_allocated_tick IS NULL OR p_allocated_tick<0
     OR p_source_ref IS NULL OR length(trim(p_source_ref)) NOT BETWEEN 1 AND 200
     OR p_actor_ref IS NULL OR length(trim(p_actor_ref)) NOT BETWEEN 1 AND 200
     OR p_idempotency_key IS NULL OR length(trim(p_idempotency_key)) NOT BETWEEN 1 AND 128 THEN
    RAISE EXCEPTION 'invalid rent payment allocation request';
  END IF;
  -- Stable parent lock order: payment first, then charge. Recheck idempotency after locks.
  PERFORM 1 FROM sw_finance.rent_payment AS p WHERE p.payment_id=p_payment_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'rent payment not found'; END IF;
  PERFORM 1 FROM sw_finance.rent_charge AS c WHERE c.charge_id=p_charge_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'rent charge not found'; END IF;
  SELECT a.* INTO v_existing FROM sw_finance.rent_payment_allocation AS a
  WHERE a.idempotency_key=p_idempotency_key;
  IF FOUND THEN
    IF ROW(v_existing.allocation_id,v_existing.payment_id,v_existing.charge_id,
      v_existing.amount_minor,v_existing.allocated_tick,v_existing.source_ref,v_existing.actor_ref)
      IS DISTINCT FROM ROW(p_allocation_id,p_payment_id,p_charge_id,p_amount_minor,
      p_allocated_tick,p_source_ref,p_actor_ref) THEN
      RAISE EXCEPTION 'rent allocation idempotency key conflicts with prior allocation';
    END IF;
    RETURN v_existing.allocation_id;
  END IF;
  INSERT INTO sw_finance.rent_payment_allocation(
    allocation_id,payment_id,charge_id,amount_minor,currency_code,allocated_tick,
    source_ref,actor_ref,idempotency_key
  )
  SELECT p_allocation_id,p.payment_id,c.charge_id,p_amount_minor,p.currency_code,
         p_allocated_tick,p_source_ref,p_actor_ref,p_idempotency_key
  FROM sw_finance.rent_payment AS p
  CROSS JOIN sw_finance.rent_charge AS c
  WHERE p.payment_id=p_payment_id AND c.charge_id=p_charge_id;
  RETURN p_allocation_id;
END
$fin$;

REVOKE ALL ON FUNCTION sw_finance.guard_rent_schedule() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_finance.guard_rent_charge() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_finance.reject_rent_payment_mutation() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_finance.guard_rent_payment_allocation() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_finance.record_rent_payment(text,text,text,bigint,char,bigint,text,text,text,text,text) FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_finance.allocate_rent_payment(text,text,text,bigint,bigint,text,text,text) FROM PUBLIC;
COMMIT;
