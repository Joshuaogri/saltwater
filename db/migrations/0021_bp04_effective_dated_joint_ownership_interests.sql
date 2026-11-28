-- BP04 phase 17: effective-dated, share-aware and disputed property interests.
-- Multiple registered co-owners are supported; the title register's current
-- interest pointer remains the lead registered proprietor, not proof of sole ownership.
BEGIN;

ALTER TABLE sw_property.ownership_interest
  ADD COLUMN interest_class text NOT NULL DEFAULT 'registered_ownership'
    CHECK (interest_class IN (
      'registered_ownership','beneficial_ownership','economic_interest',
      'secured_interest','leasehold_interest','other_interest'
    )),
  ADD COLUMN share_numerator bigint DEFAULT 1,
  ADD COLUMN share_denominator bigint DEFAULT 1,
  ADD COLUMN effective_from_tick bigint NOT NULL DEFAULT 0 CHECK (effective_from_tick>=0),
  ADD COLUMN effective_to_tick bigint,
  ADD COLUMN interest_status text NOT NULL DEFAULT 'current'
    CHECK (interest_status IN ('current','historical','pending','terminated')),
  ADD COLUMN dispute_status text NOT NULL DEFAULT 'undisputed'
    CHECK (dispute_status IN ('undisputed','disputed','resolved','unknown')),
  ADD COLUMN dispute_reference text,
  ADD COLUMN recorded_tick bigint NOT NULL DEFAULT 0 CHECK (recorded_tick>=0),
  ADD CONSTRAINT ownership_interest_share_pair_ck CHECK (
    (share_numerator IS NULL AND share_denominator IS NULL)
    OR (share_numerator>0 AND share_denominator>0 AND share_numerator<=share_denominator)
  ),
  ADD CONSTRAINT ownership_interest_effective_interval_ck CHECK (
    effective_to_tick IS NULL OR effective_to_tick>effective_from_tick
  ),
  ADD CONSTRAINT ownership_interest_status_interval_ck CHECK (
    (interest_status IN ('current','pending') AND effective_to_tick IS NULL)
    OR (interest_status IN ('historical','terminated') AND effective_to_tick IS NOT NULL)
  ),
  ADD CONSTRAINT ownership_interest_dispute_reference_ck CHECK (
    dispute_status<>'disputed'
    OR (dispute_reference IS NOT NULL AND length(trim(dispute_reference)) BETWEEN 1 AND 200)
  );

COMMENT ON COLUMN sw_property.ownership_interest.interest_class IS
  'Separates registered title shares from beneficial, economic, secured and other interests.';
COMMENT ON COLUMN sw_property.ownership_interest.share_numerator IS
  'Known share numerator; NULL with denominator NULL means the share is explicitly unknown.';
COMMENT ON COLUMN sw_property.ownership_interest.share_denominator IS
  'Known share denominator; registered joint-owner shares are checked against a maximum of 1.';
COMMENT ON COLUMN sw_property.ownership_interest.dispute_status IS
  'A disputed claim remains visible and is never silently resolved by the title projection.';
COMMENT ON COLUMN sw_property.property_title_register.current_ownership_interest_id IS
  'Lead registered interest reference; it does not imply that no additional co-ownership interests exist.';

CREATE INDEX ownership_interest_effective_property_idx
  ON sw_property.ownership_interest(
    property_id,interest_class,interest_status,effective_from_tick,effective_to_tick
  );

CREATE FUNCTION sw_property.enforce_ownership_interest_share_cap()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
DECLARE
  v_existing_total numeric;
  v_existing_count integer;
  v_unknown_count integer;
  v_new_share numeric;
BEGIN
  IF NEW.interest_class<>'registered_ownership'
     OR NEW.interest_status<>'current'
     OR NEW.effective_to_tick IS NOT NULL THEN
    RETURN NEW;
  END IF;

  -- Serialize share changes for a property, so concurrent inserts cannot
  -- independently pass a stale aggregate check.
  PERFORM 1 FROM sw_property.property_site
  WHERE property_id=NEW.property_id
  FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'ownership interest property does not exist'; END IF;

  SELECT count(*),
         count(*) FILTER (WHERE oi.share_numerator IS NULL OR oi.share_denominator IS NULL),
         COALESCE(sum(oi.share_numerator::numeric/oi.share_denominator),0)
  INTO v_existing_count,v_unknown_count,v_existing_total
  FROM sw_property.ownership_interest AS oi
  WHERE oi.property_id=NEW.property_id
    AND oi.interest_class='registered_ownership'
    AND oi.interest_status='current'
    AND oi.effective_to_tick IS NULL
    AND oi.ownership_interest_id<>NEW.ownership_interest_id;

  IF NEW.share_numerator IS NULL OR NEW.share_denominator IS NULL THEN
    IF v_existing_count>0 THEN
      RAISE EXCEPTION 'joint registered ownership requires known shares for every co-owner';
    END IF;
    RETURN NEW;
  END IF;

  IF v_unknown_count>0 THEN
    RAISE EXCEPTION 'cannot add a known registered share while another current registered share is unknown';
  END IF;

  v_new_share := NEW.share_numerator::numeric/NEW.share_denominator;
  IF v_existing_total+v_new_share>1 THEN
    RAISE EXCEPTION 'registered ownership shares exceed one whole property interest';
  END IF;
  RETURN NEW;
END
$bp04$;

CREATE TRIGGER ownership_interest_share_cap_guard
BEFORE INSERT OR UPDATE OF property_id,interest_class,share_numerator,share_denominator,
  effective_to_tick,interest_status
ON sw_property.ownership_interest
FOR EACH ROW EXECUTE FUNCTION sw_property.enforce_ownership_interest_share_cap();

CREATE FUNCTION sw_property.reject_single_interest_transfer_on_joint_title()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
BEGIN
  IF NEW.owner_organisation_id IS DISTINCT FROM OLD.owner_organisation_id
     AND EXISTS (
       SELECT 1
       FROM sw_property.property_title_register AS ptr
       WHERE ptr.property_id=OLD.property_id
         AND ptr.current_ownership_interest_id=OLD.ownership_interest_id
     )
     AND EXISTS (
       SELECT 1
       FROM sw_property.ownership_interest AS oi
       WHERE oi.property_id=OLD.property_id
         AND oi.interest_class='registered_ownership'
         AND oi.interest_status='current'
         AND oi.effective_to_tick IS NULL
         AND oi.ownership_interest_id<>OLD.ownership_interest_id
     ) THEN
    RAISE EXCEPTION 'single-interest title transfer is not permitted while joint registered ownership interests exist';
  END IF;
  RETURN NEW;
END
$bp04$;

CREATE TRIGGER ownership_interest_joint_title_transfer_guard
BEFORE UPDATE OF owner_organisation_id ON sw_property.ownership_interest
FOR EACH ROW EXECUTE FUNCTION sw_property.reject_single_interest_transfer_on_joint_title();

REVOKE ALL ON FUNCTION sw_property.enforce_ownership_interest_share_cap() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_property.reject_single_interest_transfer_on_joint_title() FROM PUBLIC;
COMMIT;
