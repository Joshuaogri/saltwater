\set ON_ERROR_STOP on
BEGIN;

INSERT INTO sw_property.organisation(
 organisation_id,display_name,organisation_type,registered_city,status,source_dataset
) VALUES
 ('SWX-OWNER','NPC Property Owner','property_holding_company','Saltwater','active','bp04_cross_domain_acceptance'),
 ('SWX-HEALTH-OP','NPC Health Operator','healthcare_provider','Saltwater','active','bp04_cross_domain_acceptance'),
 ('SWX-TRANSIT-OP','NPC Transit Operator','transport_operator','Saltwater','active','bp04_cross_domain_acceptance'),
 ('SWX-THIRD-PARTY','NPC Third Party Institution','public_institution','Saltwater','active','bp04_cross_domain_acceptance'),
 ('SWX-UTILITY','NPC Utility Provider','utility_provider','Saltwater','active','bp04_cross_domain_acceptance'),
 ('SWX-EMPLOYER-ORG','NPC Second Employer','public_institution','Saltwater','active','bp04_cross_domain_acceptance');

INSERT INTO sw_property.property_site(property_id,display_name,use_class,lifecycle_status,source_dataset)
VALUES ('SWX-PROPERTY','Cross Domain Acceptance Property','mixed_use','active','bp04_cross_domain_acceptance');
INSERT INTO sw_property.premises(premises_id,property_id,display_name,premises_use,lifecycle_status,source_dataset)
VALUES ('SWX-PREMISES','Cross Domain Acceptance Premises','SWX-PROPERTY','commercial','active','bp04_cross_domain_acceptance');
INSERT INTO sw_property.unit_space(unit_id,property_id,premises_id,display_name,unit_class,use_class,lifecycle_status,source_dataset)
VALUES ('SWX-UNIT','SWX-PROPERTY','SWX-PREMISES','Cross Domain Unit','commercial','commercial','active','bp04_cross_domain_acceptance');

INSERT INTO sw_property.business(business_id,display_name,sector,status,source_dataset)
VALUES
 ('SWX-TENANT','NPC Tenant Business','professional_services','active','bp04_cross_domain_acceptance'),
 ('SWX-OPERATOR','NPC Independent Operator','professional_services','active','bp04_cross_domain_acceptance');
INSERT INTO sw_property.establishment(
 establishment_id,business_id,property_id,premises_id,unit_id,display_name,establishment_type,status,source_dataset
) VALUES
 ('SWX-EST-TENANT','SWX-TENANT','SWX-PROPERTY','SWX-PREMISES','SWX-UNIT','Tenant Establishment','primary','active','bp04_cross_domain_acceptance');
INSERT INTO sw_property.occupancy_agreement(
 agreement_id,property_id,premises_id,unit_id,landlord_organisation_id,tenant_business_id,
 operator_business_id,establishment_id,agreement_type,commencement_year,agreement_status,source_dataset
) VALUES (
 'SWX-AGREEMENT','SWX-PROPERTY','SWX-PREMISES','SWX-UNIT','SWX-OWNER',
 'SWX-TENANT','SWX-OPERATOR','SWX-EST-TENANT','commercial_occupancy_lease',2026,'active',
 'bp04_cross_domain_acceptance'
);
INSERT INTO sw_property.occupancy(
 occupancy_id,property_id,premises_id,unit_id,occupant_organisation_id,
 agreement_id,occupant_type,occupancy_status,effective_from_year,effective_to_year,source_dataset
) VALUES (
 'SWX-OCCUPANCY','SWX-PROPERTY','SWX-PREMISES','SWX-UNIT','SWX-THIRD-PARTY',
 'SWX-AGREEMENT','organisation','occupied',2026,NULL,'bp04_cross_domain_acceptance'
);

INSERT INTO sw_property.third_party_occupancy_relationship(
 relationship_id,occupancy_id,property_id,unit_id,underlying_agreement_id,use_type,
 granting_business_id,receiving_organisation_id,permitted_purpose,access_scope,
 permission_status,relationship_status,effective_from_tick,recorded_tick,
 actor_ref,source_ref,evidence_class,idempotency_key
) VALUES (
 'SWX-THIRD-PARTY-REL','SWX-OCCUPANCY','SWX-PROPERTY','SWX-UNIT','SWX-AGREEMENT',
 'service_provider','SWX-TENANT','SWX-THIRD-PARTY','Institutional service provision',
 'Named unit and agreed common access','not_required','active',10,10,
 'npc:tenant','generated:third-party-use','generated_fictional_canon','swx:third-party:01'
);

DO $bp04$
DECLARE v_count integer; v_status text; v_person_id integer; v_population_count integer;
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM sw_property.occupancy_agreement
    WHERE agreement_id='SWX-AGREEMENT'
      AND landlord_organisation_id='SWX-OWNER'
      AND tenant_business_id='SWX-TENANT'
      AND operator_business_id='SWX-OPERATOR'
  ) THEN RAISE EXCEPTION 'landlord, tenant and operator role separation failed'; END IF;
  IF NOT EXISTS (
    SELECT 1 FROM sw_property.occupancy
    WHERE occupancy_id='SWX-OCCUPANCY' AND occupant_organisation_id='SWX-THIRD-PARTY'
      AND occupant_business_id IS NULL AND occupant_person_id IS NULL
  ) THEN RAISE EXCEPTION 'organisation occupancy did not resolve to the canonical organisation'; END IF;
  SELECT count(*) INTO v_count FROM sw_property.third_party_occupancy_event
  WHERE relationship_id='SWX-THIRD-PARTY-REL';
  IF v_count<>1 THEN RAISE EXCEPTION 'third-party occupancy start event was not recorded'; END IF;

  BEGIN
    INSERT INTO sw_property.third_party_occupancy_relationship(
      relationship_id,occupancy_id,property_id,unit_id,underlying_agreement_id,use_type,
      granting_business_id,receiving_organisation_id,permitted_purpose,access_scope,
      permission_status,relationship_status,effective_from_tick,recorded_tick,
      actor_ref,source_ref,evidence_class,idempotency_key
    ) VALUES (
      'SWX-INVALID-REL','SWX-OCCUPANCY','SWX-PROPERTY','SWX-UNIT','SWX-AGREEMENT',
      'contractor_access','SWX-TENANT','SWX-THIRD-PARTY','Unapproved access',
      'Unrestricted','unknown','active',11,11,'npc:tenant','generated:unknown',
      'generated_fictional_canon','swx:third-party:invalid'
    );
    RAISE EXCEPTION 'unknown permission was accepted as active third-party occupancy';
  EXCEPTION WHEN check_violation OR raise_exception THEN
    IF SQLERRM='unknown permission was accepted as active third-party occupancy' THEN RAISE; END IF;
  END;

  PERFORM * FROM sw_property.end_third_party_occupancy_relationship(
    'SWX-THIRD-PARTY-REL',20,20,'npc:tenant','generated:end','swx:third-party:end:01'
  );
  SELECT relationship_status INTO v_status FROM sw_property.third_party_occupancy_relationship
  WHERE relationship_id='SWX-THIRD-PARTY-REL';
  IF v_status<>'ended' THEN RAISE EXCEPTION 'third-party relationship did not end'; END IF;
  SELECT count(*) INTO v_count FROM sw_property.third_party_occupancy_event
  WHERE relationship_id='SWX-THIRD-PARTY-REL';
  IF v_count<>2 THEN RAISE EXCEPTION 'third-party end event was not recorded'; END IF;
  IF (SELECT effective_to_year FROM sw_property.occupancy WHERE occupancy_id='SWX-OCCUPANCY') IS NOT NULL THEN
    RAISE EXCEPTION 'ending a legal third-party use relationship silently ended physical occupancy';
  END IF;

  INSERT INTO sw_property.occupancy_financial_reference(
    reference_id,agreement_id,bp34_financial_agreement_ref,bp34_rent_schedule_ref,
    bp34_deposit_reference,bp34_receivable_reference,effective_from_tick,recorded_tick,
    actor_ref,source_ref,idempotency_key
  ) VALUES (
    'SWX-BP34-REF','SWX-AGREEMENT','SW34-AGREEMENT-01','SW34-RENT-01',
    'SW34-DEPOSIT-01','SW34-RECEIVABLE-01',0,0,'npc:finance-interface',
    'generated:bp34-reference','swx:bp34:agreement:01'
  );
  IF (SELECT agreement_status FROM sw_property.occupancy_agreement WHERE agreement_id='SWX-AGREEMENT')<>'active'
     OR (SELECT occupancy_status FROM sw_property.occupancy WHERE occupancy_id='SWX-OCCUPANCY')<>'occupied' THEN
    RAISE EXCEPTION 'BP34 reference link mutated agreement or physical occupancy state';
  END IF;
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema='sw_property' AND table_name='occupancy_financial_reference'
      AND column_name IN ('rent_amount','payment_amount','payment_status','arrears_balance','deposit_balance')
  ) THEN
    RAISE EXCEPTION 'BP04 financial reference duplicated BP34-owned amounts or payment state';
  END IF;

  BEGIN
    INSERT INTO sw_property.staff_role_link(
      staff_role_link_id,person_id,employer_business_id,bp33_employment_ref,role_title,
      effective_from_tick,source_ref,actor_ref,evidence_class
    ) VALUES (
      'SWX-STAFF-ROLE',-999999,'SWX-TENANT','SW33-EMPLOYMENT-UNKNOWN',
      'NPC Service Technician',0,'generated:staff-link','npc:hr',
      'generated_fictional_canon'
    );
    RAISE EXCEPTION 'staff role link accepted a person not registered by BP03';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='staff role link accepted a person not registered by BP03' THEN RAISE; END IF;
    IF SQLERRM NOT LIKE '%BP03%' AND SQLERRM NOT LIKE '%person_id does not resolve%' THEN RAISE; END IF;
  END;

  BEGIN
    INSERT INTO sw_property.occupancy(
      occupancy_id,property_id,premises_id,unit_id,occupant_person_id,agreement_id,
      occupant_type,occupancy_status,effective_from_year,source_dataset
    ) VALUES (
      'SWX-PERSON-OCCUPANCY','SWX-PROPERTY','SWX-PREMISES','SWX-UNIT',-999999,
      'SWX-AGREEMENT','person','occupied',2026,'bp04_cross_domain_acceptance'
    );
    RAISE EXCEPTION 'occupancy accepted a person identity not registered by BP03';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='occupancy accepted a person identity not registered by BP03' THEN RAISE; END IF;
    IF SQLERRM NOT LIKE '%BP03%' AND SQLERRM NOT LIKE '%does not resolve%' THEN RAISE; END IF;
  END;

  -- Create one real canonical BP03 NPC, then reference that same identity in
  -- multiple BP33 employment roles and BP04 occupancy without incrementing
  -- the population more than once.
  v_person_id:=sw_people.create_person(
    'NPC','CrossDomain','bp04-cross-domain-person-01','npc:hr',
    'BP03/BP33/BP04 integration acceptance'
  );
  PERFORM sw_people.set_population_qualifications(
    v_person_id,false,true,false,'bp04-cross-domain-person-present',
    'npc:hr','NPC employee is physically present in Saltwater'
  );
  INSERT INTO sw_property.staff_role_link(
    staff_role_link_id,person_id,employer_business_id,bp33_employment_ref,role_title,
    effective_from_tick,source_ref,actor_ref,evidence_class
  ) VALUES (
    'SWX-STAFF-ROLE-VALID-1',v_person_id,'SWX-TENANT','SW33-EMPLOYMENT-01',
    'Service Technician',0,'generated:staff-link-01','npc:hr','generated_fictional_canon'
  );
  INSERT INTO sw_property.staff_role_link(
    staff_role_link_id,person_id,employer_organisation_id,bp33_employment_ref,role_title,
    effective_from_tick,source_ref,actor_ref,evidence_class
  ) VALUES (
    'SWX-STAFF-ROLE-VALID-2',v_person_id,'SWX-EMPLOYER-ORG','SW33-EMPLOYMENT-02',
    'Part-time Coordinator',0,'generated:staff-link-02','npc:hr','generated_fictional_canon'
  );
  INSERT INTO sw_property.occupancy(
    occupancy_id,property_id,premises_id,unit_id,occupant_person_id,agreement_id,
    occupant_type,occupancy_status,effective_from_year,source_dataset
  ) VALUES (
    'SWX-PERSON-OCCUPANCY','SWX-PROPERTY','SWX-PREMISES','SWX-UNIT',v_person_id,
    'SWX-AGREEMENT','person','occupied',2026,'bp04_cross_domain_acceptance'
  );
  INSERT INTO sw_property.third_party_occupancy_relationship(
    relationship_id,occupancy_id,property_id,unit_id,underlying_agreement_id,use_type,
    granting_business_id,receiving_person_id,permitted_purpose,access_scope,
    permission_status,relationship_status,effective_from_tick,recorded_tick,
    actor_ref,source_ref,evidence_class,idempotency_key
  ) VALUES (
    'SWX-PERSON-THIRD-PARTY-REL','SWX-PERSON-OCCUPANCY','SWX-PROPERTY','SWX-UNIT',
    'SWX-AGREEMENT','contractor_access','SWX-TENANT',v_person_id,
    'NPC contractor service','Specified work area','not_required','active',12,12,
    'npc:tenant','generated:person-third-party-use','generated_fictional_canon',
    'swx:person-third-party:01'
  );
  SELECT living_included INTO v_population_count FROM sw_people.population_counter WHERE singleton=1;
  IF v_population_count<>1 THEN RAISE EXCEPTION 'one canonical person with multiple roles must count exactly once'; END IF;
  SELECT count(DISTINCT person_id) INTO v_count FROM sw_property.staff_role_link
  WHERE person_id=v_person_id;
  IF v_count<>1 OR (SELECT count(*) FROM sw_property.staff_role_link WHERE person_id=v_person_id)<>2 THEN
    RAISE EXCEPTION 'BP33 employment roles did not reuse one BP03 person identity';
  END IF;
END
$bp04$;

ROLLBACK;
SELECT 'BP04 third-party occupancy, BP03/BP33 and BP34 boundary acceptance passed' AS result;
