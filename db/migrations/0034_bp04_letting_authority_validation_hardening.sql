-- BP04-34: require a current title-holder grant and recorded authority event.
-- Historical expired authority may support an agreement only within its recorded term.
BEGIN;

CREATE OR REPLACE FUNCTION sw_property.validate_agreement_landlord_authority()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
DECLARE
  v_authority sw_property.letting_authority%ROWTYPE;
  v_title_owner text;
BEGIN
  SELECT registered_proprietor_organisation_id INTO v_title_owner
  FROM sw_property.property_title_register
  WHERE property_id=NEW.property_id;

  IF NEW.letting_authority_id IS NOT NULL THEN
    SELECT * INTO v_authority
    FROM sw_property.letting_authority
    WHERE letting_authority_id=NEW.letting_authority_id;

    IF NOT FOUND
       OR v_authority.property_id<>NEW.property_id
       OR (v_authority.unit_id IS NOT NULL AND v_authority.unit_id<>NEW.unit_id)
       OR v_authority.grantee_organisation_id IS DISTINCT FROM NEW.landlord_organisation_id
       OR v_authority.grantor_organisation_id IS DISTINCT FROM v_title_owner
       OR NEW.commencement_year<v_authority.effective_from_year
       OR (v_authority.effective_to_year IS NOT NULL
           AND NEW.commencement_year>v_authority.effective_to_year)
       OR v_authority.authority_status IN ('revoked','superseded')
       OR NOT EXISTS (
         SELECT 1 FROM sw_property.letting_authority_event e
         WHERE e.letting_authority_id=v_authority.letting_authority_id
           AND e.event_type='authority_granted'
           AND e.effective_year=v_authority.effective_from_year
       ) THEN
      RAISE EXCEPTION 'agreement landlord does not match a title-holder-granted, evidenced, in-term letting authority';
    END IF;
  ELSIF v_title_owner IS NOT NULL
        AND NEW.landlord_organisation_id IS DISTINCT FROM v_title_owner THEN
    RAISE EXCEPTION 'non-owner landlord requires an explicit letting authority';
  END IF;

  RETURN NEW;
END
$bp04$;

COMMIT;
