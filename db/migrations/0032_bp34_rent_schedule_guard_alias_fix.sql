-- BP34-32: avoid PL/pgSQL OLD-record name collision in rent schedule overlap validation.
BEGIN;
CREATE OR REPLACE FUNCTION sw_finance.guard_rent_schedule()
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
    SELECT 1 FROM sw_finance.rent_schedule AS prior_schedule
    WHERE prior_schedule.schedule_id=NEW.supersedes_schedule_id
      AND prior_schedule.agreement_id=NEW.agreement_id
  ) THEN RAISE EXCEPTION 'superseded rent schedule must belong to the same agreement'; END IF;
  IF EXISTS (
    SELECT 1 FROM sw_finance.rent_schedule AS prior_schedule
    WHERE prior_schedule.agreement_id=NEW.agreement_id
      AND prior_schedule.schedule_status='active'
      AND prior_schedule.effective_from_tick<COALESCE(NEW.effective_to_tick,9223372036854775807)
      AND NEW.effective_from_tick<COALESCE(prior_schedule.effective_to_tick,9223372036854775807)
  ) THEN RAISE EXCEPTION 'active rent schedule intervals cannot overlap'; END IF;
  RETURN NEW;
END
$fin$;
REVOKE ALL ON FUNCTION sw_finance.guard_rent_schedule() FROM PUBLIC;
COMMIT;
