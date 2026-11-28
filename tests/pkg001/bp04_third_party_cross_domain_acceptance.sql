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

  INSERT INTO sw_finance.rent_schedule(
    schedule_id,agreement_id,payer_business_id,payee_organisation_id,currency_code,
    recurring_amount_minor,frequency,period_length_ticks,effective_from_tick,
    schedule_status,source_ref,actor_ref,idempotency_key
  ) VALUES (
    'SW34-RENT-01','SWX-AGREEMENT','SWX-TENANT','SWX-OWNER','SWC',
    50000,'monthly',100,0,'active','generated:rent-schedule','npc:landlord','sw34:schedule:01'
  );
  INSERT INTO sw_finance.rent_charge(
    charge_id,schedule_id,agreement_id,period_start_tick,period_end_tick,due_tick,
    amount_minor,currency_code,source_ref,actor_ref,idempotency_key
  ) VALUES (
    'SW34-CHARGE-01','SW34-RENT-01','SWX-AGREEMENT',0,100,80,
    50000,'SWC','generated:rent-charge','npc:finance','sw34:charge:01'
  );
  PERFORM sw_finance.record_rent_payment(
    'SW34-PAYMENT-01','SWX-TENANT','SWX-OWNER',20000,'SWC',80,
    'bank_transfer','NPC-PAYMENT-01','generated:rent-payment-01','npc:tenant','sw34:payment:01'
  );
  PERFORM sw_finance.record_rent_payment(
    'SW34-PAYMENT-01','SWX-TENANT','SWX-OWNER',20000,'SWC',80,
    'bank_transfer','NPC-PAYMENT-01','generated:rent-payment-01','npc:tenant','sw34:payment:01'
  );
  PERFORM sw_finance.allocate_rent_payment(
    'SW34-ALLOCATION-01','SW34-PAYMENT-01','SW34-CHARGE-01',20000,80,
    'generated:rent-allocation-01','npc:finance','sw34:allocation:01'
  );
  IF (SELECT outstanding_minor FROM sw_finance.rent_charge_balance WHERE charge_id='SW34-CHARGE-01')<>30000
     OR (SELECT derived_payment_state FROM sw_finance.rent_charge_balance WHERE charge_id='SW34-CHARGE-01')<>'partially_paid' THEN
    RAISE EXCEPTION 'BP34 partial NPC rent payment did not produce the correct outstanding balance';
  END IF;
  IF (SELECT agreement_status FROM sw_property.occupancy_agreement WHERE agreement_id='SWX-AGREEMENT')<>'active'
     OR (SELECT occupancy_status FROM sw_property.occupancy WHERE occupancy_id='SWX-OCCUPANCY')<>'occupied' THEN
    RAISE EXCEPTION 'partial rent payment or arrears changed BP04 tenancy/occupancy state';
  END IF;
  PERFORM sw_finance.record_rent_payment(
    'SW34-PAYMENT-02','SWX-TENANT','SWX-OWNER',30000,'SWC',90,
    'bank_transfer','NPC-PAYMENT-02','generated:rent-payment-02','npc:tenant','sw34:payment:02'
  );
  PERFORM sw_finance.allocate_rent_payment(
    'SW34-ALLOCATION-02','SW34-PAYMENT-02','SW34-CHARGE-01',30000,90,
    'generated:rent-allocation-02','npc:finance','sw34:allocation:02'
  );
  IF (SELECT outstanding_minor FROM sw_finance.rent_charge_balance WHERE charge_id='SW34-CHARGE-01')<>0
     OR (SELECT derived_payment_state FROM sw_finance.rent_charge_balance WHERE charge_id='SW34-CHARGE-01')<>'paid' THEN
    RAISE EXCEPTION 'BP34 full NPC rent settlement did not close the charge balance';
  END IF;
  IF (SELECT agreement_status FROM sw_property.occupancy_agreement WHERE agreement_id='SWX-AGREEMENT')<>'active'
     OR (SELECT occupancy_status FROM sw_property.occupancy WHERE occupancy_id='SWX-OCCUPANCY')<>'occupied' THEN
    RAISE EXCEPTION 'rent settlement changed BP04 tenancy/occupancy state';
  END IF;
  BEGIN
    PERFORM sw_finance.record_rent_payment(
      'SW34-OVERPAY','SWX-TENANT','SWX-OWNER',1000,'SWC',91,
      'cash','NPC-OVERPAY','generated:rent-overpay','npc:tenant','sw34:payment:overpay'
    );
    PERFORM sw_finance.allocate_rent_payment(
      'SW34-OVERALLOC','SW34-OVERPAY','SW34-CHARGE-01',1000,91,
      'generated:over-allocation','npc:finance','sw34:allocation:overpay'
    );
    RAISE EXCEPTION 'BP34 accepted an overpayment allocation';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='BP34 accepted an overpayment allocation' THEN RAISE; END IF;
    IF SQLERRM NOT LIKE '%rent charge cannot be overpaid%' THEN RAISE; END IF;
  END;
  BEGIN
    UPDATE sw_finance.rent_payment SET amount_minor=1 WHERE payment_id='SW34-PAYMENT-01';
    RAISE EXCEPTION 'BP34 rent payment allowed mutation';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='BP34 rent payment allowed mutation' THEN RAISE; END IF;
    IF SQLERRM NOT LIKE '%append-only%' THEN RAISE; END IF;
  END;
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema='sw_property' AND table_name='occupancy_financial_reference'
      AND column_name IN ('rent_amount','payment_amount','payment_status','arrears_balance','deposit_balance')
  ) THEN
    RAISE EXCEPTION 'BP04 financial reference duplicated BP34-owned amounts or payment state';
  END IF;

  BEGIN
    INSERT INTO sw_property.staff_role_link(
      staff_role_link_id,person_id,employer_business_id,bp33_employment_ref,
      effective_from_tick,source_ref,actor_ref,evidence_class
    ) VALUES (
      'SWX-STAFF-ROLE',-999999,'SWX-TENANT','SW33-EMPLOYMENT-UNKNOWN',
      0,'generated:staff-link','npc:hr',
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
  INSERT INTO sw_hr.employment(
    employment_id,person_id,employer_business_id,establishment_id,role_title,
    employment_status,effective_from_tick,recorded_tick,source_ref,actor_ref,
    evidence_class,idempotency_key
  ) VALUES (
    'SW33-EMPLOYMENT-01',v_person_id,'SWX-TENANT','SWX-EST-TENANT','Service Technician',
    'active',0,0,'generated:employment-01','npc:hr','generated_fictional_canon','swx:employment:01'
  );
  INSERT INTO sw_hr.employment(
    employment_id,person_id,employer_organisation_id,role_title,
    employment_status,effective_from_tick,recorded_tick,source_ref,actor_ref,
    evidence_class,idempotency_key
  ) VALUES (
    'SW33-EMPLOYMENT-02',v_person_id,'SWX-EMPLOYER-ORG','Part-time Coordinator',
    'active',0,0,'generated:employment-02','npc:hr','generated_fictional_canon','swx:employment:02'
  );
  INSERT INTO sw_property.staff_role_link(
    staff_role_link_id,person_id,employer_business_id,establishment_id,
    bp33_employment_ref,effective_from_tick,source_ref,actor_ref,evidence_class
  ) VALUES (
    'SWX-STAFF-ROLE-VALID-1',v_person_id,'SWX-TENANT','SWX-EST-TENANT',
    'SW33-EMPLOYMENT-01',0,'generated:staff-link-01','npc:hr','generated_fictional_canon'
  );
  INSERT INTO sw_property.staff_role_link(
    staff_role_link_id,person_id,employer_organisation_id,bp33_employment_ref,
    effective_from_tick,source_ref,actor_ref,evidence_class
  ) VALUES (
    'SWX-STAFF-ROLE-VALID-2',v_person_id,'SWX-EMPLOYER-ORG',
    'SW33-EMPLOYMENT-02',0,'generated:staff-link-02','npc:hr','generated_fictional_canon'
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
  PERFORM * FROM sw_hr.end_employment(
    'SW33-EMPLOYMENT-02',20,20,'npc:hr','generated:employment-end','swx:employment:end:02'
  );
  IF (SELECT employment_status FROM sw_hr.employment WHERE employment_id='SW33-EMPLOYMENT-02')<>'ended'
     OR (SELECT living_included FROM sw_people.population_counter WHERE singleton=1)<>1 THEN
    RAISE EXCEPTION 'employment end changed person identity or population count';
  END IF;
  IF (SELECT occupancy_status FROM sw_property.occupancy WHERE occupancy_id='SWX-PERSON-OCCUPANCY')<>'occupied' THEN
    RAISE EXCEPTION 'employment end silently changed physical occupancy';
  END IF;
  SELECT count(DISTINCT person_id) INTO v_count FROM sw_property.staff_role_link
  WHERE person_id=v_person_id;
  IF v_count<>1 OR (SELECT count(*) FROM sw_property.staff_role_link WHERE person_id=v_person_id)<>2 THEN
    RAISE EXCEPTION 'BP33 employment roles did not reuse one BP03 person identity';
  END IF;
END
$bp04$;

ROLLBACK;
SELECT 'BP04 third-party occupancy, BP03/BP33 and BP34 boundary acceptance passed' AS result;
