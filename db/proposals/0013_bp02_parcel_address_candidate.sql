-- BP-02-owned parcel and canonical address candidate foundation for BP04-03 Stage B.
-- Disposable PostgreSQL 16 candidate only. No Neon or operational geography authority.
BEGIN;

CREATE TABLE sw_geo.parcel_profile (
  parcel_spatial_id integer NOT NULL REFERENCES sw_geo.entity(spatial_id),
  version_no smallint NOT NULL CHECK (version_no > 0),
  neighbourhood_spatial_id integer NOT NULL REFERENCES sw_geo.entity(spatial_id),
  land_use_code text NOT NULL CHECK (land_use_code IN
    ('residential','mixed_use','commercial','civic','education','health',
     'industrial','freight_logistics','port_maritime','transport','utility',
     'open_space','waterfront','vacant','conservation','other')),
  development_state text NOT NULL CHECK (development_state IN
    ('developed','partially_developed','vacant','open_space','transport_corridor',
     'water_or_reclamation','restricted','unknown')),
  area_m2 numeric(14,2) NOT NULL CHECK (area_m2 > 0),
  area_basis text NOT NULL CHECK (area_basis IN
    ('derived_geometry','generated_design_value','documented','observed','unknown')),
  geometry_quality text NOT NULL CHECK (geometry_quality IN
    ('candidate_unreviewed','topology_checked','reviewed','approved')),
  source_ref text NOT NULL CHECK (length(btrim(source_ref)) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(btrim(actor_ref)) BETWEEN 1 AND 120),
  confidence_code text NOT NULL CHECK (confidence_code IN
    ('verified','documented','observed','estimated','inferred','unknown')),
  reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240),
  recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  PRIMARY KEY(parcel_spatial_id,version_no),
  FOREIGN KEY(parcel_spatial_id,version_no)
    REFERENCES sw_geo.version(spatial_id,version_no),
  CHECK (geometry_quality <> 'approved')
);
CREATE INDEX parcel_profile_neighbourhood_idx
  ON sw_geo.parcel_profile(neighbourhood_spatial_id,land_use_code);

CREATE TABLE sw_geo.address_profile (
  address_spatial_id integer NOT NULL REFERENCES sw_geo.entity(spatial_id),
  version_no smallint NOT NULL CHECK (version_no > 0),
  parcel_spatial_id integer NOT NULL REFERENCES sw_geo.entity(spatial_id),
  neighbourhood_spatial_id integer NOT NULL REFERENCES sw_geo.entity(spatial_id),
  road_spatial_id integer REFERENCES sw_geo.entity(spatial_id),
  locator_kind text NOT NULL CHECK (locator_kind IN
    ('street_number','compound_locator','campus_locator','waterfront_locator',
     'service_locator','unfronted_locator')),
  locator_value text NOT NULL CHECK (length(btrim(locator_value)) BETWEEN 1 AND 80),
  locator_suffix text NOT NULL DEFAULT '',
  frontage_type text NOT NULL CHECK (frontage_type IN
    ('direct_public_frontage','shared_private_approach','campus_access',
     'waterfront_access','service_access','no_conventional_frontage','unresolved')),
  active boolean NOT NULL DEFAULT true,
  source_ref text NOT NULL CHECK (length(btrim(source_ref)) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(btrim(actor_ref)) BETWEEN 1 AND 120),
  confidence_code text NOT NULL CHECK (confidence_code IN
    ('verified','documented','observed','estimated','inferred','unknown')),
  reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240),
  recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  PRIMARY KEY(address_spatial_id,version_no),
  FOREIGN KEY(address_spatial_id,version_no)
    REFERENCES sw_geo.version(spatial_id,version_no),
  CHECK (
    (locator_kind='street_number' AND road_spatial_id IS NOT NULL
      AND frontage_type IN ('direct_public_frontage','shared_private_approach'))
    OR
    (locator_kind<>'street_number')
  ),
  CHECK (
    (frontage_type='unresolved')
    OR
    (frontage_type='direct_public_frontage' AND road_spatial_id IS NOT NULL)
    OR
    (frontage_type<>'direct_public_frontage')
  )
);
CREATE UNIQUE INDEX address_active_road_locator_uq
  ON sw_geo.address_profile(road_spatial_id,lower(locator_value),lower(locator_suffix))
  WHERE active AND road_spatial_id IS NOT NULL;
CREATE UNIQUE INDEX address_active_parcel_locator_uq
  ON sw_geo.address_profile(parcel_spatial_id,lower(locator_value),lower(locator_suffix))
  WHERE active AND road_spatial_id IS NULL;
CREATE INDEX address_parcel_lookup_idx
  ON sw_geo.address_profile(parcel_spatial_id,active);
CREATE INDEX address_neighbourhood_lookup_idx
  ON sw_geo.address_profile(neighbourhood_spatial_id,active);

CREATE TABLE sw_geo.parcel_lineage (
  lineage_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  predecessor_parcel_spatial_id integer NOT NULL REFERENCES sw_geo.entity(spatial_id),
  successor_parcel_spatial_id integer NOT NULL REFERENCES sw_geo.entity(spatial_id),
  relationship_code text NOT NULL CHECK (relationship_code IN
    ('split_into','merged_into','boundary_replaced','retired')),
  effective_from_tick bigint NOT NULL CHECK (effective_from_tick>=0),
  source_ref text NOT NULL CHECK (length(btrim(source_ref)) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(btrim(actor_ref)) BETWEEN 1 AND 120),
  reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240),
  recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  CHECK (predecessor_parcel_spatial_id <> successor_parcel_spatial_id)
);
CREATE INDEX parcel_lineage_predecessor_idx
  ON sw_geo.parcel_lineage(predecessor_parcel_spatial_id,lineage_id);
CREATE INDEX parcel_lineage_successor_idx
  ON sw_geo.parcel_lineage(successor_parcel_spatial_id,lineage_id);

CREATE FUNCTION sw_geo.guard_parcel_lineage_kind()
RETURNS trigger LANGUAGE plpgsql AS $bp04$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM sw_geo.entity WHERE spatial_id=NEW.predecessor_parcel_spatial_id AND kind=6)
     OR NOT EXISTS (SELECT 1 FROM sw_geo.entity WHERE spatial_id=NEW.successor_parcel_spatial_id AND kind=6) THEN
    RAISE EXCEPTION 'parcel lineage endpoints must both identify parcel kind 6';
  END IF;
  RETURN NEW;
END
$bp04$;
CREATE TRIGGER parcel_lineage_kind_guard
BEFORE INSERT ON sw_geo.parcel_lineage
FOR EACH ROW EXECUTE FUNCTION sw_geo.guard_parcel_lineage_kind();

CREATE TABLE sw_geo.address_alias (
  address_alias_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  address_spatial_id integer NOT NULL REFERENCES sw_geo.entity(spatial_id),
  alias_value text NOT NULL CHECK (length(btrim(alias_value)) BETWEEN 1 AND 160),
  alias_type text NOT NULL CHECK (alias_type IN
    ('former_locator','common_locator','local_description','delivery_description')),
  valid_from_tick bigint NOT NULL CHECK (valid_from_tick>=0),
  valid_to_tick bigint CHECK (valid_to_tick IS NULL OR valid_to_tick>valid_from_tick),
  source_ref text NOT NULL CHECK (length(btrim(source_ref)) BETWEEN 1 AND 200),
  actor_ref text NOT NULL CHECK (length(btrim(actor_ref)) BETWEEN 1 AND 120),
  reason text NOT NULL CHECK (length(btrim(reason)) BETWEEN 1 AND 240),
  recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);
CREATE INDEX address_alias_lookup_idx
  ON sw_geo.address_alias(address_spatial_id,valid_from_tick);

CREATE FUNCTION sw_geo.guard_parcel_profile_kind()
RETURNS trigger LANGUAGE plpgsql AS $
DECLARE
  v_payload bytea;
  v_hash bytea;
BEGIN
  IF NOT EXISTS (SELECT 1 FROM sw_geo.entity WHERE spatial_id=NEW.parcel_spatial_id AND kind=6) THEN
    RAISE EXCEPTION 'parcel profile identity must reference geography kind 6';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM sw_geo.entity WHERE spatial_id=NEW.neighbourhood_spatial_id AND kind=4) THEN
    RAISE EXCEPTION 'parcel neighbourhood must reference geography kind 4';
  END IF;
  SELECT geometry_payload,geometry_sha256 INTO v_payload,v_hash
    FROM sw_geo.version
    WHERE spatial_id=NEW.parcel_spatial_id AND version_no=NEW.version_no
      AND geometry_format IS NOT NULL;
  IF NOT FOUND OR v_payload IS NULL OR v_hash IS NULL THEN
    RAISE EXCEPTION 'parcel profile requires a versioned geometry payload and checksum';
  END IF;
  IF v_hash IS DISTINCT FROM sw_ops.digest(v_payload,'sha256') THEN
    RAISE EXCEPTION 'parcel geometry checksum does not match its payload';
  END IF;
  RETURN NEW;
END
$$;
CREATE TRIGGER parcel_profile_kind_guard
BEFORE INSERT ON sw_geo.parcel_profile
FOR EACH ROW EXECUTE FUNCTION sw_geo.guard_parcel_profile_kind();

CREATE FUNCTION sw_geo.guard_address_profile_kind()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM sw_geo.entity WHERE spatial_id=NEW.address_spatial_id AND kind=11) THEN
    RAISE EXCEPTION 'address profile identity must reference geography kind 11';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM sw_geo.entity WHERE spatial_id=NEW.parcel_spatial_id AND kind=6) THEN
    RAISE EXCEPTION 'address parcel reference must identify geography kind 6';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM sw_geo.entity WHERE spatial_id=NEW.neighbourhood_spatial_id AND kind=4) THEN
    RAISE EXCEPTION 'address locality reference must identify geography kind 4';
  END IF;
  IF NEW.road_spatial_id IS NOT NULL AND NOT EXISTS
    (SELECT 1 FROM sw_geo.entity WHERE spatial_id=NEW.road_spatial_id AND kind=7) THEN
    RAISE EXCEPTION 'address road reference must identify geography kind 7';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM sw_geo.version WHERE spatial_id=NEW.address_spatial_id AND version_no=NEW.version_no) THEN
    RAISE EXCEPTION 'address profile requires its matching spatial version';
  END IF;
  RETURN NEW;
END
$$;
CREATE TRIGGER address_profile_kind_guard
BEFORE INSERT ON sw_geo.address_profile
FOR EACH ROW EXECUTE FUNCTION sw_geo.guard_address_profile_kind();

CREATE FUNCTION sw_geo.reject_candidate_record_mutation()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'geography candidate history is append-only; add a new version or event';
END
$$;
CREATE TRIGGER parcel_profile_immutable
BEFORE UPDATE OR DELETE ON sw_geo.parcel_profile
FOR EACH ROW EXECUTE FUNCTION sw_geo.reject_candidate_record_mutation();
CREATE TRIGGER address_profile_immutable
BEFORE UPDATE OR DELETE ON sw_geo.address_profile
FOR EACH ROW EXECUTE FUNCTION sw_geo.reject_candidate_record_mutation();
CREATE TRIGGER parcel_lineage_immutable
BEFORE UPDATE OR DELETE ON sw_geo.parcel_lineage
FOR EACH ROW EXECUTE FUNCTION sw_geo.reject_candidate_record_mutation();
CREATE TRIGGER address_alias_immutable
BEFORE UPDATE OR DELETE ON sw_geo.address_alias
FOR EACH ROW EXECUTE FUNCTION sw_geo.reject_candidate_record_mutation();

REVOKE INSERT,UPDATE,DELETE,TRUNCATE ON
  sw_geo.parcel_profile,sw_geo.address_profile,sw_geo.parcel_lineage,sw_geo.address_alias
FROM PUBLIC;
GRANT SELECT ON
  sw_geo.parcel_profile,sw_geo.address_profile,sw_geo.parcel_lineage,sw_geo.address_alias
TO PUBLIC;

COMMIT;
