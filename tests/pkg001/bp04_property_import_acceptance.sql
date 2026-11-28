\set ON_ERROR_STOP on
DO $bp04$
DECLARE
  v_datasets integer;
  v_collections integer;
  v_source_rows bigint;
  v_loaded bigint;
  v_daily integer;
  v_weekly integer;
  v_count bigint;
  v_status text;
  v_development_rows bigint;
BEGIN
  SELECT count(*) INTO v_datasets FROM sw_property.import_dataset;
  SELECT count(*), coalesce(sum(source_record_count),0), coalesce(sum(loaded_record_count),0)
    INTO v_collections, v_source_rows, v_loaded
  FROM sw_property.source_dataset_collection;
  IF v_datasets <> 14 THEN RAISE EXCEPTION 'expected 14 archived source datasets, found %', v_datasets; END IF;
  IF v_collections <> 109 THEN RAISE EXCEPTION 'expected 109 source collection ledger rows, found %', v_collections; END IF;
  IF v_source_rows <> 1979290 THEN RAISE EXCEPTION 'expected 1979290 source records, found %', v_source_rows; END IF;

  SELECT count(*) INTO v_count FROM sw_property.letting_authority;
  IF v_count <> 9 THEN RAISE EXCEPTION 'expected 9 canonical letting authorities, found %', v_count; END IF;
  SELECT count(*) INTO v_count FROM sw_property.letting_authority_event;
  IF v_count <> 9 THEN RAISE EXCEPTION 'expected 9 immutable letting authority events, found %', v_count; END IF;
  SELECT count(*) INTO v_count FROM sw_property.occupancy_agreement
  WHERE letting_authority_id IS NOT NULL;
  IF v_count <> 1822 THEN RAISE EXCEPTION 'expected 1822 current non-owner landlord agreements, found %', v_count; END IF;
  SELECT count(*) INTO v_count FROM sw_property.third_party_occupancy_relationship;
  IF v_count <> 420 THEN RAISE EXCEPTION 'expected 420 canonical third-party occupancy relationships, found %', v_count; END IF;
  SELECT count(*) INTO v_count FROM sw_property.occupancy
  WHERE occupant_type='organisation' AND occupant_organisation_id IS NOT NULL;
  IF v_count <> 420 THEN RAISE EXCEPTION 'expected 420 secondary organisation occupancy records, found %', v_count; END IF;
  IF EXISTS (
    SELECT 1
    FROM sw_property.third_party_occupancy_relationship r
    JOIN sw_property.occupancy o USING (occupancy_id)
    JOIN sw_property.occupancy_agreement a ON a.agreement_id=r.underlying_agreement_id
    LEFT JOIN sw_property.organisation receiving ON receiving.organisation_id=r.receiving_organisation_id
    LEFT JOIN sw_property.business granting ON granting.business_id=r.granting_business_id
    WHERE o.occupant_type<>'organisation'
       OR o.occupant_organisation_id IS DISTINCT FROM r.receiving_organisation_id
       OR receiving.organisation_id IS NULL OR granting.business_id IS NULL
       OR r.property_id<>a.property_id OR r.unit_id<>a.unit_id
       OR r.granting_business_id NOT IN (a.tenant_business_id,a.operator_business_id)
       OR r.relationship_status<>'active' OR r.permission_status<>'not_required'
       OR r.evidence_class<>'generated_fictional_canon'
  ) THEN RAISE EXCEPTION 'third-party occupancy relationship does not match its canonical parties, unit or agreement'; END IF;

  IF EXISTS (
    SELECT 1
    FROM sw_property.occupancy_agreement a
    JOIN sw_property.letting_authority l USING (letting_authority_id)
    LEFT JOIN sw_property.property_title_register t ON t.property_id=a.property_id
    LEFT JOIN sw_property.organisation grantor ON grantor.organisation_id=l.grantor_organisation_id
    LEFT JOIN sw_property.organisation grantee ON grantee.organisation_id=l.grantee_organisation_id
    WHERE a.letting_authority_id IS NOT NULL
      AND (l.property_id <> a.property_id
        OR l.grantor_organisation_id <> t.registered_proprietor_organisation_id
        OR l.grantee_organisation_id <> a.landlord_organisation_id
        OR l.grantor_organisation_id = l.grantee_organisation_id
        OR grantor.organisation_id IS NULL OR grantee.organisation_id IS NULL
        OR (l.unit_id IS NOT NULL AND l.unit_id <> a.unit_id)
        OR a.commencement_year < l.effective_from_year
        OR (l.effective_to_year IS NOT NULL AND a.commencement_year > l.effective_to_year))
  ) THEN RAISE EXCEPTION 'imported non-owner landlord authority does not match title, organisation, unit scope or term'; END IF;
  IF EXISTS (
    SELECT 1
    FROM sw_property.letting_authority l
    LEFT JOIN sw_property.letting_authority_event e
      ON e.letting_authority_id=l.letting_authority_id AND e.event_type='authority_granted'
    WHERE e.letting_authority_event_id IS NULL
       OR e.effective_year <> l.effective_from_year
  ) THEN RAISE EXCEPTION 'imported letting authority lacks its matching immutable grant event'; END IF;

  SELECT mapping_status, loaded_record_count INTO v_status, v_count
  FROM sw_property.source_dataset_collection
  WHERE dataset_id='SW-PROPERTY-WORLD-V1' AND collection_name='properties';
  IF v_status <> 'mapped' OR v_count <> 420 THEN
    RAISE EXCEPTION 'source collection identity mismatch for property-world properties: status %, loaded %', v_status, v_count;
  END IF;

  SELECT mapping_status, loaded_record_count INTO v_status, v_count
  FROM sw_property.import_dataset WHERE dataset_id='SW-BUSINESS-OPERATIONS-V1';
  IF v_status <> 'fully_mapped' OR v_count <> 80000 THEN
    RAISE EXCEPTION 'business operations source mapping mismatch: status %, loaded %', v_status, v_count;
  END IF;

  SELECT count(*) INTO v_daily FROM sw_property.business_daily_schedule;
  SELECT count(*) INTO v_weekly FROM sw_property.business_weekly_profile;
  IF v_daily <> 70000 OR v_weekly <> 10000 THEN
    RAISE EXCEPTION 'business operations row counts incorrect: daily %, weekly %', v_daily, v_weekly;
  END IF;

  SELECT mapping_status, loaded_record_count INTO v_status, v_development_rows
  FROM sw_property.import_dataset WHERE dataset_id='SW-PROPERTY-DEVELOPMENT-CONTROL-V1';
  IF v_status <> 'partially_mapped' OR v_development_rows <> 34308 THEN
    RAISE EXCEPTION 'development-control mapping mismatch: status %, loaded %', v_status, v_development_rows;
  END IF;
  IF (SELECT count(*) FROM sw_property.lawful_use_certificate) <> 27730
     OR (SELECT count(*) FROM sw_property.building_inspection_schedule) <> 1474
     OR (SELECT count(*) FROM sw_property.development_project) <> 258 THEN
    RAISE EXCEPTION 'development-control typed row counts incorrect';
  END IF;
  IF EXISTS (
    SELECT 1 FROM sw_property.lawful_use_certificate l
    LEFT JOIN sw_property.premises p USING (premises_id)
    LEFT JOIN sw_property.completion_certificate c USING (completion_certificate_id)
    WHERE p.premises_id IS NULL OR c.completion_certificate_id IS NULL
  ) THEN RAISE EXCEPTION 'lawful-use certificate cross-reference failure'; END IF;

  IF EXISTS (
    SELECT 1 FROM sw_property.business_daily_schedule s
    LEFT JOIN sw_property.business b USING (business_id)
    LEFT JOIN sw_property.establishment e USING (establishment_id)
    WHERE b.business_id IS NULL OR e.establishment_id IS NULL
  ) THEN RAISE EXCEPTION 'business schedule cross-reference failure'; END IF;

  SELECT mapping_status, loaded_record_count INTO v_status, v_count
  FROM sw_property.import_dataset WHERE dataset_id='SW-PROPERTY-LIFECYCLE-TRANSACTIONS-V1';
  IF v_status <> 'fully_mapped' OR v_count <> 31956 THEN
    RAISE EXCEPTION 'property lifecycle mapping mismatch: status %, loaded %', v_status, v_count;
  END IF;
  IF (SELECT count(*) FROM sw_property.property_title_register) <> 420
     OR (SELECT count(*) FROM sw_property.property_title_instrument) <> 531
     OR (SELECT count(*) FROM sw_property.property_transaction_index) <> 531
     OR (SELECT count(*) FROM sw_property.building_lifecycle_event) <> 1474
     OR (SELECT count(*) FROM sw_property.premises_lifecycle_event) <> 27730 THEN
    RAISE EXCEPTION 'property lifecycle typed row counts incorrect';
  END IF;
  IF EXISTS (
    SELECT 1 FROM sw_property.property_transaction_index t
    LEFT JOIN sw_property.property_title_instrument i ON i.title_instrument_id=t.title_instrument_id
    LEFT JOIN sw_property.property_title_register r ON r.title_register_id=t.title_register_id
    WHERE i.title_instrument_id IS NULL OR r.title_register_id IS NULL
  ) THEN RAISE EXCEPTION 'property transaction/title lineage failure'; END IF;

  SELECT mapping_status, loaded_record_count INTO v_status, v_count
  FROM sw_property.import_dataset WHERE dataset_id='SW-PROPERTY-RIGHTS-AND-BOUNDARIES-V1';
  IF v_status <> 'fully_mapped' OR v_count <> 18013 THEN
    RAISE EXCEPTION 'property rights mapping mismatch: status %, loaded %', v_status, v_count;
  END IF;
  IF (SELECT count(*) FROM sw_property.property_rights_schedule) <> 420
     OR (SELECT count(*) FROM sw_property.contractual_rights_index) <> 12500
     OR (SELECT count(*) FROM sw_property.boundary_evidence_register) <> 420
     OR (SELECT count(*) FROM sw_property.physical_access_evidence_register) <> 2984
     OR (SELECT count(*) FROM sw_property.utility_wayleave_requirement) <> 1680
     OR (SELECT count(*) FROM sw_property.registered_property_instrument) <> 0
     OR (SELECT count(*) FROM sw_property.future_instrument_template) <> 9 THEN
    RAISE EXCEPTION 'property rights typed row counts incorrect';
  END IF;
  IF EXISTS (
    SELECT 1 FROM sw_property.contractual_rights_index r
    LEFT JOIN sw_property.occupancy_agreement a ON a.agreement_id=r.source_agreement_id
    WHERE a.agreement_id IS NULL
  ) THEN RAISE EXCEPTION 'contractual rights agreement lineage failure'; END IF;
  IF EXISTS (
    SELECT 1 FROM sw_property.physical_access_evidence_register a
    LEFT JOIN sw_property.access_point p ON p.access_point_id=a.access_point_id
    LEFT JOIN sw_property.property_site s ON s.property_id=a.property_id
    WHERE p.access_point_id IS NULL OR s.property_id IS NULL
  ) THEN RAISE EXCEPTION 'physical access evidence linkage failure'; END IF;
END $bp04$;
SELECT mapping_status, count(*) AS dataset_count, sum(source_record_count) AS source_rows, sum(loaded_record_count) AS loaded_rows FROM sw_property.import_dataset GROUP BY mapping_status ORDER BY mapping_status;
SELECT mapping_status, count(*) AS collection_count, sum(source_record_count) AS source_rows, sum(loaded_record_count) AS loaded_rows FROM sw_property.source_dataset_collection GROUP BY mapping_status ORDER BY mapping_status;
SELECT 'BP04 imported source ledger and business operations acceptance passed' AS result;
