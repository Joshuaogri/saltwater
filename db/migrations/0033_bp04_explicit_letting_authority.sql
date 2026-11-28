-- BP04-33 explicit non-owner landlord / head-letting authority.
-- A managing agent is not a landlord. A non-owner organisation may be named
-- as landlord only where a property/unit-scoped letting authority is recorded.
-- This migration is source-only until separately validated and applied.
BEGIN;

CREATE TABLE sw_property.letting_authority (
  letting_authority_id text PRIMARY KEY,
  property_id text NOT NULL REFERENCES sw_property.property_site(property_id)
    DEFERRABLE INITIALLY DEFERRED,
  unit_id text REFERENCES sw_property.unit_space(unit_id)
    DEFERRABLE INITIALLY DEFERRED,
  grantor_organisation_id text NOT NULL
    REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
  grantee_organisation_id text NOT NULL
    REFERENCES sw_property.organisation(organisation_id) DEFERRABLE INITIALLY DEFERRED,
  authority_type text NOT NULL CHECK (authority_type IN (
    'head_lease','leasehold_estate','estate_concession','contractual_letting_right'
  )),
  authority_status text NOT NULL CHECK (authority_status IN (
    'current','expired','revoked','superseded'
  )),
  effective_from_year integer NOT NULL,
  effective_to_year integer,
  source_instrument_ref text NOT NULL CHECK (length(trim(source_instrument_ref)) BETWEEN 1 AND 200),
  source_basis text NOT NULL CHECK (source_basis IN (
    'source_documented','generated_fictional_canon','gameplay_action'
  )),
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  CHECK (grantor_organisation_id<>grantee_organisation_id),
  CHECK (effective_to_year IS NULL OR effective_to_year>=effective_from_year),
  CHECK ((authority_status='current' AND effective_to_year IS NULL)
      OR (authority_status<>'current' AND effective_to_year IS NOT NULL))
);
CREATE INDEX letting_authority_property_period_idx
  ON sw_property.letting_authority(property_id,unit_id,effective_from_year,effective_to_year);
CREATE INDEX letting_authority_grantee_idx
  ON sw_property.letting_authority(grantee_organisation_id,authority_status);

CREATE TABLE sw_property.letting_authority_event (
  letting_authority_event_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  letting_authority_id text NOT NULL
    REFERENCES sw_property.letting_authority(letting_authority_id)
    DEFERRABLE INITIALLY DEFERRED,
  event_type text NOT NULL CHECK (event_type IN (
    'authority_granted','authority_expired','authority_revoked','authority_superseded'
  )),
  effective_year integer NOT NULL,
  recorded_tick bigint NOT NULL CHECK (recorded_tick>=0),
  actor_ref text NOT NULL CHECK (length(trim(actor_ref)) BETWEEN 1 AND 200),
  source_ref text NOT NULL CHECK (length(trim(source_ref)) BETWEEN 1 AND 200),
  idempotency_key text NOT NULL UNIQUE
    CHECK (idempotency_key ~ '^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$'),
  evidence_class text NOT NULL CHECK (evidence_class IN (
    'source_documented','generated_fictional_canon','gameplay_action'
  )),
  event_payload jsonb NOT NULL DEFAULT '{}'::jsonb
    CHECK (jsonb_typeof(event_payload)='object'),
  created_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);
CREATE INDEX letting_authority_event_history_idx
  ON sw_property.letting_authority_event(letting_authority_id,effective_year,letting_authority_event_id);

CREATE FUNCTION sw_property.reject_letting_authority_event_mutation()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
BEGIN
  RAISE EXCEPTION 'letting authority event history is append-only';
END
$bp04$;
CREATE TRIGGER letting_authority_event_immutable
BEFORE UPDATE OR DELETE ON sw_property.letting_authority_event
FOR EACH ROW EXECUTE FUNCTION sw_property.reject_letting_authority_event_mutation();

ALTER TABLE sw_property.occupancy_agreement
  ADD COLUMN letting_authority_id text
    REFERENCES sw_property.letting_authority(letting_authority_id)
    DEFERRABLE INITIALLY DEFERRED;

CREATE FUNCTION sw_property.validate_agreement_landlord_authority()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
DECLARE
  v_authority sw_property.letting_authority%ROWTYPE;
  v_title_owner text;
BEGIN
  IF NEW.letting_authority_id IS NOT NULL THEN
    SELECT * INTO v_authority
    FROM sw_property.letting_authority
    WHERE letting_authority_id=NEW.letting_authority_id;
    IF NOT FOUND
       OR v_authority.property_id<>NEW.property_id
       OR (v_authority.unit_id IS NOT NULL AND v_authority.unit_id<>NEW.unit_id)
       OR v_authority.grantee_organisation_id IS DISTINCT FROM NEW.landlord_organisation_id
       OR NEW.commencement_year<v_authority.effective_from_year
       OR (v_authority.effective_to_year IS NOT NULL
           AND NEW.commencement_year>v_authority.effective_to_year) THEN
      RAISE EXCEPTION 'agreement landlord does not match its property-scoped letting authority';
    END IF;
  ELSE
    SELECT registered_proprietor_organisation_id INTO v_title_owner
    FROM sw_property.property_title_register
    WHERE property_id=NEW.property_id;
    IF v_title_owner IS NOT NULL
       AND NEW.landlord_organisation_id IS DISTINCT FROM v_title_owner THEN
      RAISE EXCEPTION 'non-owner landlord requires an explicit letting authority';
    END IF;
  END IF;
  RETURN NEW;
END
$bp04$;
CREATE TRIGGER occupancy_agreement_landlord_authority_guard
BEFORE INSERT OR UPDATE OF property_id,unit_id,landlord_organisation_id,
  commencement_year,letting_authority_id
ON sw_property.occupancy_agreement
FOR EACH ROW EXECUTE FUNCTION sw_property.validate_agreement_landlord_authority();

INSERT INTO sw_ops.schema_migration(version,migration_name)
VALUES (33,'bp04_explicit_letting_authority')
ON CONFLICT(version) DO NOTHING;
COMMIT;
