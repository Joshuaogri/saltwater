-- BP03 household membership and BP04 dwelling / BP02 address bridge.
-- Disposable acceptance first; this proposal is not a production migration.
BEGIN;

CREATE TABLE sw_geo.bp04_bp02_address_link (
  bp04_address_id text PRIMARY KEY REFERENCES sw_property.street_address(address_id),
  bp02_address_source_id text NOT NULL UNIQUE REFERENCES sw_geo.bp02_address(source_id),
  parcel_source_id text NOT NULL,
  source_ref text NOT NULL UNIQUE CHECK(length(btrim(source_ref)) BETWEEN 1 AND 200),
  evidence_ref text NOT NULL CHECK(length(btrim(evidence_ref)) BETWEEN 1 AND 240),
  linked_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  CHECK(length(btrim(parcel_source_id)) BETWEEN 1 AND 160)
);

CREATE FUNCTION sw_geo.link_bp04_bp02_address(
 p_bp04_address_id text,p_bp02_address_source_id text,
 p_source_ref text,p_evidence_ref text
) RETURNS boolean
LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,sw_geo,sw_property
AS $$
DECLARE v_parcel text; v_address_parcel text; v_existing sw_geo.bp04_bp02_address_link%ROWTYPE;
BEGIN
 IF p_bp04_address_id IS NULL OR p_bp02_address_source_id IS NULL
  OR p_source_ref IS NULL OR length(btrim(p_source_ref)) NOT BETWEEN 1 AND 200
  OR p_evidence_ref IS NULL OR length(btrim(p_evidence_ref)) NOT BETWEEN 1 AND 240 THEN
  RAISE EXCEPTION 'both canonical addresses and bounded mapping provenance are required';
 END IF;
 SELECT p.source_record->>'source_candidate_parcel_id',
        substring(a.source_record->>'source_ref' from '^SW-GEO-V1:(.+)
 IF NOT EXISTS(SELECT 1 FROM sw_geo.bp02_address
   WHERE source_id=p_bp02_address_source_id AND parcel_source_id=v_parcel
     AND operational_status='ACTIVE_IN_GAME') THEN
  RAISE EXCEPTION 'BP02 address does not resolve to the same active canonical parcel';
 END IF;
 SELECT * INTO v_existing FROM sw_geo.bp04_bp02_address_link
 WHERE bp04_address_id=p_bp04_address_id OR bp02_address_source_id=p_bp02_address_source_id;
 IF FOUND THEN
  IF v_existing.bp04_address_id=p_bp04_address_id
   AND v_existing.bp02_address_source_id=p_bp02_address_source_id
   AND v_existing.parcel_source_id=v_parcel THEN RETURN true; END IF;
  RAISE EXCEPTION 'address crosswalk source identity conflicts with an existing mapping';
 END IF;
 INSERT INTO sw_geo.bp04_bp02_address_link(
  bp04_address_id,bp02_address_source_id,parcel_source_id,source_ref,evidence_ref
 ) VALUES(p_bp04_address_id,p_bp02_address_source_id,v_parcel,p_source_ref,p_evidence_ref);
 RETURN true;
END $$;

CREATE TABLE sw_people.household (
 household_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 household_ref text NOT NULL UNIQUE CHECK(length(btrim(household_ref)) BETWEEN 1 AND 120),
 unit_id text NOT NULL REFERENCES sw_property.unit_space(unit_id),
 bp04_address_id text NOT NULL REFERENCES sw_property.street_address(address_id),
 address_source_id text NOT NULL REFERENCES sw_geo.bp02_address(source_id),
 household_status text NOT NULL DEFAULT 'current' CHECK(household_status IN ('current','closed')),
 effective_from_tick bigint NOT NULL CHECK(effective_from_tick>=0),
 effective_to_tick bigint,
 source_ref text NOT NULL UNIQUE CHECK(length(btrim(source_ref)) BETWEEN 1 AND 200),
 last_event_id bigint NOT NULL UNIQUE REFERENCES sw_core.simulation_event(event_id),
 CHECK((household_status='current' AND effective_to_tick IS NULL)
   OR (household_status='closed' AND effective_to_tick IS NOT NULL
       AND effective_to_tick>=effective_from_tick))
);
CREATE UNIQUE INDEX household_one_current_per_dwelling
 ON sw_people.household(unit_id) WHERE household_status='current';
CREATE INDEX household_address_idx ON sw_people.household(address_source_id);

CREATE TABLE sw_people.household_member (
 household_member_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 household_id integer NOT NULL REFERENCES sw_people.household(household_id),
 person_id integer NOT NULL REFERENCES sw_people.person(person_id),
 member_role text NOT NULL DEFAULT 'member'
  CHECK(member_role IN ('member','household_contact','other')),
 membership_status text NOT NULL DEFAULT 'current'
  CHECK(membership_status IN ('current','ended')),
 effective_from_tick bigint NOT NULL CHECK(effective_from_tick>=0),
 effective_to_tick bigint,
 source_ref text NOT NULL UNIQUE CHECK(length(btrim(source_ref)) BETWEEN 1 AND 200),
 last_event_id bigint NOT NULL UNIQUE REFERENCES sw_core.simulation_event(event_id),
 CHECK((membership_status='current' AND effective_to_tick IS NULL)
   OR (membership_status='ended' AND effective_to_tick IS NOT NULL
       AND effective_to_tick>=effective_from_tick))
);
CREATE UNIQUE INDEX household_one_current_membership_per_person
 ON sw_people.household_member(person_id) WHERE membership_status='current';
CREATE UNIQUE INDEX household_one_current_contact
 ON sw_people.household_member(household_id)
 WHERE membership_status='current' AND member_role='household_contact';
CREATE INDEX household_member_household_idx
 ON sw_people.household_member(household_id,membership_status);

CREATE TABLE sw_people.household_history (
 event_id bigint PRIMARY KEY REFERENCES sw_core.simulation_event(event_id),
 household_id integer NOT NULL REFERENCES sw_people.household(household_id),
 person_id integer REFERENCES sw_people.person(person_id),
 event_kind text NOT NULL CHECK(event_kind IN ('household_created','member_added','member_ended')),
 prior_role text,new_role text,effective_tick bigint NOT NULL,
 source_ref text NOT NULL,actor_ref text NOT NULL,reason text NOT NULL,
 recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);
CREATE FUNCTION sw_people.reject_household_history_mutation()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN RAISE EXCEPTION 'household history is append-only'; END $$;
CREATE TRIGGER household_history_immutable
 BEFORE UPDATE OR DELETE ON sw_people.household_history
 FOR EACH ROW EXECUTE FUNCTION sw_people.reject_household_history_mutation();

INSERT INTO sw_core.event_type(event_code,description) VALUES
 ('HOUSEHOLD_CREATED','A dwelling household was established'),
 ('HOUSEHOLD_MEMBER_ADDED','A canonical person joined a dwelling household'),
 ('HOUSEHOLD_MEMBER_ENDED','A canonical person left a dwelling household')
ON CONFLICT(event_code) DO NOTHING;

CREATE FUNCTION sw_people.create_household(
 p_household_ref text,p_unit_id text,p_bp04_address_id text,
 p_address_source_id text,p_source_ref text,p_actor_ref text,p_reason text
) RETURNS integer
LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,sw_people,sw_geo,sw_property,sw_runtime,sw_core
AS $$
DECLARE v_tick bigint; v_event bigint; v_id integer; v_existing sw_people.household%ROWTYPE;
 v_property text; v_address text;
BEGIN
 IF p_household_ref IS NULL OR length(btrim(p_household_ref)) NOT BETWEEN 1 AND 120
  OR p_unit_id IS NULL OR p_bp04_address_id IS NULL OR p_address_source_id IS NULL
  OR p_source_ref IS NULL OR length(btrim(p_source_ref)) NOT BETWEEN 1 AND 200
  OR p_actor_ref IS NULL OR length(btrim(p_actor_ref)) NOT BETWEEN 1 AND 120
  OR p_reason IS NULL OR length(btrim(p_reason)) NOT BETWEEN 1 AND 240 THEN
  RAISE EXCEPTION 'household, dwelling, address and bounded provenance are required';
 END IF;
 SELECT u.property_id,p.address_id INTO v_property,v_address
 FROM sw_property.unit_space u
 JOIN sw_property.property_site p ON p.property_id=u.property_id
 WHERE u.unit_id=p_unit_id AND u.unit_class='dwelling' AND u.use_class='residential'
   AND u.lifecycle_status='active';
 IF NOT FOUND OR v_address IS DISTINCT FROM p_bp04_address_id THEN
  RAISE EXCEPTION 'household unit must be an active residential dwelling at the supplied BP04 address';
 END IF;
 IF NOT EXISTS(SELECT 1 FROM sw_geo.bp04_bp02_address_link
  WHERE bp04_address_id=p_bp04_address_id
    AND bp02_address_source_id=p_address_source_id) THEN
  RAISE EXCEPTION 'BP04 dwelling address has no verified BP02 address crosswalk';
 END IF;
 SELECT * INTO v_existing FROM sw_people.household WHERE source_ref=p_source_ref;
 IF FOUND THEN
  IF v_existing.household_ref=p_household_ref AND v_existing.unit_id=p_unit_id
   AND v_existing.bp04_address_id=p_bp04_address_id
   AND v_existing.address_source_id=p_address_source_id THEN RETURN v_existing.household_id; END IF;
  RAISE EXCEPTION 'household source_ref replay conflicts with its original identity';
 END IF;
 SELECT world_tick INTO STRICT v_tick FROM sw_runtime.state WHERE singleton=1;
 INSERT INTO sw_core.simulation_event(
  event_type_id,occurred_at,world_tick,subject_kind,source_ref,attributes,idempotency_key
 ) SELECT event_type_id,clock_timestamp(),v_tick,'household',p_source_ref,
  jsonb_build_object('household_ref',p_household_ref,'unit_id',p_unit_id,
   'bp04_address_id',p_bp04_address_id,'address_source_id',p_address_source_id,
   'actor_ref',p_actor_ref,'reason',p_reason),
  'SW-BP03:HOUSEHOLD:'||p_source_ref
 FROM sw_core.event_type WHERE event_code='HOUSEHOLD_CREATED'
 RETURNING event_id INTO v_event;
 IF v_event IS NULL THEN RAISE EXCEPTION 'HOUSEHOLD_CREATED event type is missing'; END IF;
 INSERT INTO sw_people.household(
  household_ref,unit_id,bp04_address_id,address_source_id,effective_from_tick,source_ref,last_event_id
 ) VALUES(p_household_ref,p_unit_id,p_bp04_address_id,p_address_source_id,v_tick,p_source_ref,v_event)
 RETURNING household_id INTO v_id;
 INSERT INTO sw_people.household_history(
  event_id,household_id,event_kind,effective_tick,source_ref,actor_ref,reason
 ) VALUES(v_event,v_id,'household_created',v_tick,p_source_ref,p_actor_ref,p_reason);
 RETURN v_id;
END $$;

CREATE FUNCTION sw_people.add_household_member(
 p_household_id integer,p_person_id integer,p_member_role text,
 p_source_ref text,p_actor_ref text,p_reason text
) RETURNS bigint
LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,sw_people,sw_geo,sw_runtime,sw_core
AS $$
DECLARE v_household sw_people.household%ROWTYPE; v_state sw_people.population_state%ROWTYPE;
 v_tick bigint; v_event bigint; v_member bigint; v_existing sw_people.household_member%ROWTYPE;
BEGIN
 IF p_household_id IS NULL OR p_person_id IS NULL
  OR p_member_role IS NULL OR p_member_role NOT IN ('member','household_contact','other')
  OR p_source_ref IS NULL OR length(btrim(p_source_ref)) NOT BETWEEN 1 AND 200
  OR p_actor_ref IS NULL OR length(btrim(p_actor_ref)) NOT BETWEEN 1 AND 120
  OR p_reason IS NULL OR length(btrim(p_reason)) NOT BETWEEN 1 AND 240 THEN
  RAISE EXCEPTION 'household, person, role and bounded provenance are required';
 END IF;
 SELECT * INTO v_household FROM sw_people.household WHERE household_id=p_household_id FOR UPDATE;
 IF NOT FOUND OR v_household.household_status<>'current' THEN
  RAISE EXCEPTION 'current household does not exist';
 END IF;
 SELECT * INTO v_state FROM sw_people.population_state WHERE person_id=p_person_id FOR UPDATE;
 IF NOT FOUND OR v_state.life_status<>1 OR NOT v_state.usual_resident THEN
  RAISE EXCEPTION 'household members must be living usual residents';
 END IF;
 IF NOT EXISTS(SELECT 1 FROM sw_people.person_residence
   WHERE person_id=p_person_id AND residence_status='current'
     AND address_source_id=v_household.address_source_id) THEN
  RAISE EXCEPTION 'person current residence does not match household BP02 address';
 END IF;
 SELECT * INTO v_existing FROM sw_people.household_member WHERE source_ref=p_source_ref;
 IF FOUND THEN
  IF v_existing.household_id=p_household_id AND v_existing.person_id=p_person_id
   AND v_existing.member_role=p_member_role THEN RETURN v_existing.household_member_id; END IF;
  RAISE EXCEPTION 'household membership source_ref replay conflicts with its original assignment';
 END IF;
 IF EXISTS(SELECT 1 FROM sw_people.household_member
   WHERE person_id=p_person_id AND membership_status='current') THEN
  RAISE EXCEPTION 'person already belongs to a current household';
 END IF;
 SELECT world_tick INTO STRICT v_tick FROM sw_runtime.state WHERE singleton=1;
 INSERT INTO sw_core.simulation_event(
  event_type_id,occurred_at,world_tick,subject_kind,subject_id,source_ref,attributes,idempotency_key
 ) SELECT event_type_id,clock_timestamp(),v_tick,'person',p_person_id,p_source_ref,
  jsonb_build_object('household_id',p_household_id,'member_role',p_member_role,
   'actor_ref',p_actor_ref,'reason',p_reason),
  'SW-BP03:HOUSEHOLD-MEMBER:'||p_person_id||':'||p_source_ref
 FROM sw_core.event_type WHERE event_code='HOUSEHOLD_MEMBER_ADDED'
 RETURNING event_id INTO v_event;
 IF v_event IS NULL THEN RAISE EXCEPTION 'HOUSEHOLD_MEMBER_ADDED event type is missing'; END IF;
 INSERT INTO sw_people.household_member(
  household_id,person_id,member_role,effective_from_tick,source_ref,last_event_id
 ) VALUES(p_household_id,p_person_id,p_member_role,v_tick,p_source_ref,v_event)
 RETURNING household_member_id INTO v_member;
 INSERT INTO sw_people.household_history(
  event_id,household_id,person_id,event_kind,new_role,effective_tick,source_ref,actor_ref,reason
 ) VALUES(v_event,p_household_id,p_person_id,'member_added',p_member_role,v_tick,p_source_ref,p_actor_ref,p_reason);
 RETURN v_member;
END $$;

CREATE FUNCTION sw_people.end_household_membership(
 p_person_id integer,p_source_ref text,p_actor_ref text,p_reason text
) RETURNS boolean
LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,sw_people,sw_runtime,sw_core
AS $$
DECLARE v_member sw_people.household_member%ROWTYPE; v_tick bigint; v_event bigint;
BEGIN
 IF p_person_id IS NULL OR p_source_ref IS NULL OR length(btrim(p_source_ref)) NOT BETWEEN 1 AND 200
  OR p_actor_ref IS NULL OR length(btrim(p_actor_ref)) NOT BETWEEN 1 AND 120
  OR p_reason IS NULL OR length(btrim(p_reason)) NOT BETWEEN 1 AND 240 THEN
  RAISE EXCEPTION 'person and bounded provenance are required';
 END IF;
 SELECT * INTO v_member FROM sw_people.household_member
  WHERE person_id=p_person_id AND membership_status='current' FOR UPDATE;
 IF NOT FOUND THEN RETURN false; END IF;
 SELECT world_tick INTO STRICT v_tick FROM sw_runtime.state WHERE singleton=1;
 INSERT INTO sw_core.simulation_event(
  event_type_id,occurred_at,world_tick,subject_kind,subject_id,source_ref,attributes,idempotency_key
 ) SELECT event_type_id,clock_timestamp(),v_tick,'person',p_person_id,p_source_ref,
  jsonb_build_object('household_id',v_member.household_id,'prior_role',v_member.member_role,
   'actor_ref',p_actor_ref,'reason',p_reason),
  'SW-BP03:HOUSEHOLD-MEMBER-END:'||p_person_id||':'||p_source_ref
 FROM sw_core.event_type WHERE event_code='HOUSEHOLD_MEMBER_ENDED'
 RETURNING event_id INTO v_event;
 IF v_event IS NULL THEN RAISE EXCEPTION 'HOUSEHOLD_MEMBER_ENDED event type is missing'; END IF;
 UPDATE sw_people.household_member SET membership_status='ended',
  effective_to_tick=GREATEST(v_tick,effective_from_tick)
 WHERE household_member_id=v_member.household_member_id;
 INSERT INTO sw_people.household_history(
  event_id,household_id,person_id,event_kind,prior_role,effective_tick,source_ref,actor_ref,reason
 ) VALUES(v_event,v_member.household_id,p_person_id,'member_ended',v_member.member_role,
  v_tick,p_source_ref,p_actor_ref,p_reason);
 RETURN true;
END $$;

CREATE VIEW sw_people.household_summary AS
SELECT h.household_id,h.household_ref,h.unit_id,h.address_source_id,
 count(m.household_member_id) FILTER(WHERE m.membership_status='current')::integer AS current_member_count,
 count(m.household_member_id) FILTER(WHERE m.membership_status='current' AND m.member_role='household_contact')::integer AS contact_count
FROM sw_people.household h LEFT JOIN sw_people.household_member m USING(household_id)
WHERE h.household_status='current'
GROUP BY h.household_id,h.household_ref,h.unit_id,h.address_source_id;

REVOKE ALL ON sw_geo.bp04_bp02_address_link FROM PUBLIC;
GRANT SELECT ON sw_geo.bp04_bp02_address_link TO sw_game_readonly;
REVOKE ALL ON sw_people.household,sw_people.household_member,sw_people.household_history FROM PUBLIC;
GRANT SELECT ON sw_people.household,sw_people.household_member,sw_people.household_history,sw_people.household_summary TO sw_game_readonly;
REVOKE ALL ON FUNCTION sw_geo.link_bp04_bp02_address(text,text,text,text) FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_people.reject_household_history_mutation() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_people.create_household(text,text,text,text,text,text,text) FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_people.add_household_member(integer,integer,text,text,text,text) FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_people.end_household_membership(integer,text,text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION sw_geo.link_bp04_bp02_address(text,text,text,text) TO sw_game_command;
GRANT EXECUTE ON FUNCTION sw_people.create_household(text,text,text,text,text,text,text) TO sw_game_command;
GRANT EXECUTE ON FUNCTION sw_people.add_household_member(integer,integer,text,text,text,text) TO sw_game_command;
GRANT EXECUTE ON FUNCTION sw_people.end_household_membership(integer,text,text,text) TO sw_game_command;
COMMIT;
)
 INTO v_parcel,v_address_parcel
 FROM sw_property.street_address a
 JOIN sw_property.property_site p ON p.property_id=a.property_id
 WHERE a.address_id=p_bp04_address_id;
 IF NOT FOUND THEN RAISE EXCEPTION 'BP04 address identity does not exist'; END IF;
 IF v_parcel IS NULL OR v_address_parcel IS NULL OR v_parcel<>v_address_parcel THEN
  RAISE EXCEPTION 'BP04 address and property source parcel identity are inconsistent';
 END IF;
 IF NOT EXISTS(SELECT 1 FROM sw_geo.bp02_address
   WHERE source_id=p_bp02_address_source_id AND parcel_source_id=v_parcel
     AND operational_status='ACTIVE_IN_GAME') THEN
  RAISE EXCEPTION 'BP02 address does not resolve to the same active canonical parcel';
 END IF;
 SELECT * INTO v_existing FROM sw_geo.bp04_bp02_address_link
 WHERE bp04_address_id=p_bp04_address_id OR bp02_address_source_id=p_bp02_address_source_id;
 IF FOUND THEN
  IF v_existing.bp04_address_id=p_bp04_address_id
   AND v_existing.bp02_address_source_id=p_bp02_address_source_id
   AND v_existing.parcel_source_id=v_parcel THEN RETURN true; END IF;
  RAISE EXCEPTION 'address crosswalk source identity conflicts with an existing mapping';
 END IF;
 INSERT INTO sw_geo.bp04_bp02_address_link(
  bp04_address_id,bp02_address_source_id,parcel_source_id,source_ref,evidence_ref
 ) VALUES(p_bp04_address_id,p_bp02_address_source_id,v_parcel,p_source_ref,p_evidence_ref);
 RETURN true;
END $$;

CREATE TABLE sw_people.household (
 household_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 household_ref text NOT NULL UNIQUE CHECK(length(btrim(household_ref)) BETWEEN 1 AND 120),
 unit_id text NOT NULL REFERENCES sw_property.unit_space(unit_id),
 bp04_address_id text NOT NULL REFERENCES sw_property.street_address(address_id),
 address_source_id text NOT NULL REFERENCES sw_geo.bp02_address(source_id),
 household_status text NOT NULL DEFAULT 'current' CHECK(household_status IN ('current','closed')),
 effective_from_tick bigint NOT NULL CHECK(effective_from_tick>=0),
 effective_to_tick bigint,
 source_ref text NOT NULL UNIQUE CHECK(length(btrim(source_ref)) BETWEEN 1 AND 200),
 last_event_id bigint NOT NULL UNIQUE REFERENCES sw_core.simulation_event(event_id),
 CHECK((household_status='current' AND effective_to_tick IS NULL)
   OR (household_status='closed' AND effective_to_tick IS NOT NULL
       AND effective_to_tick>=effective_from_tick))
);
CREATE UNIQUE INDEX household_one_current_per_dwelling
 ON sw_people.household(unit_id) WHERE household_status='current';
CREATE INDEX household_address_idx ON sw_people.household(address_source_id);

CREATE TABLE sw_people.household_member (
 household_member_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 household_id integer NOT NULL REFERENCES sw_people.household(household_id),
 person_id integer NOT NULL REFERENCES sw_people.person(person_id),
 member_role text NOT NULL DEFAULT 'member'
  CHECK(member_role IN ('member','household_contact','other')),
 membership_status text NOT NULL DEFAULT 'current'
  CHECK(membership_status IN ('current','ended')),
 effective_from_tick bigint NOT NULL CHECK(effective_from_tick>=0),
 effective_to_tick bigint,
 source_ref text NOT NULL UNIQUE CHECK(length(btrim(source_ref)) BETWEEN 1 AND 200),
 last_event_id bigint NOT NULL UNIQUE REFERENCES sw_core.simulation_event(event_id),
 CHECK((membership_status='current' AND effective_to_tick IS NULL)
   OR (membership_status='ended' AND effective_to_tick IS NOT NULL
       AND effective_to_tick>=effective_from_tick))
);
CREATE UNIQUE INDEX household_one_current_membership_per_person
 ON sw_people.household_member(person_id) WHERE membership_status='current';
CREATE UNIQUE INDEX household_one_current_contact
 ON sw_people.household_member(household_id)
 WHERE membership_status='current' AND member_role='household_contact';
CREATE INDEX household_member_household_idx
 ON sw_people.household_member(household_id,membership_status);

CREATE TABLE sw_people.household_history (
 event_id bigint PRIMARY KEY REFERENCES sw_core.simulation_event(event_id),
 household_id integer NOT NULL REFERENCES sw_people.household(household_id),
 person_id integer REFERENCES sw_people.person(person_id),
 event_kind text NOT NULL CHECK(event_kind IN ('household_created','member_added','member_ended')),
 prior_role text,new_role text,effective_tick bigint NOT NULL,
 source_ref text NOT NULL,actor_ref text NOT NULL,reason text NOT NULL,
 recorded_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);
CREATE FUNCTION sw_people.reject_household_history_mutation()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN RAISE EXCEPTION 'household history is append-only'; END $$;
CREATE TRIGGER household_history_immutable
 BEFORE UPDATE OR DELETE ON sw_people.household_history
 FOR EACH ROW EXECUTE FUNCTION sw_people.reject_household_history_mutation();

INSERT INTO sw_core.event_type(event_code,description) VALUES
 ('HOUSEHOLD_CREATED','A dwelling household was established'),
 ('HOUSEHOLD_MEMBER_ADDED','A canonical person joined a dwelling household'),
 ('HOUSEHOLD_MEMBER_ENDED','A canonical person left a dwelling household')
ON CONFLICT(event_code) DO NOTHING;

CREATE FUNCTION sw_people.create_household(
 p_household_ref text,p_unit_id text,p_bp04_address_id text,
 p_address_source_id text,p_source_ref text,p_actor_ref text,p_reason text
) RETURNS integer
LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,sw_people,sw_geo,sw_property,sw_runtime,sw_core
AS $$
DECLARE v_tick bigint; v_event bigint; v_id integer; v_existing sw_people.household%ROWTYPE;
 v_property text; v_address text;
BEGIN
 IF p_household_ref IS NULL OR length(btrim(p_household_ref)) NOT BETWEEN 1 AND 120
  OR p_unit_id IS NULL OR p_bp04_address_id IS NULL OR p_address_source_id IS NULL
  OR p_source_ref IS NULL OR length(btrim(p_source_ref)) NOT BETWEEN 1 AND 200
  OR p_actor_ref IS NULL OR length(btrim(p_actor_ref)) NOT BETWEEN 1 AND 120
  OR p_reason IS NULL OR length(btrim(p_reason)) NOT BETWEEN 1 AND 240 THEN
  RAISE EXCEPTION 'household, dwelling, address and bounded provenance are required';
 END IF;
 SELECT u.property_id,p.address_id INTO v_property,v_address
 FROM sw_property.unit_space u
 JOIN sw_property.property_site p ON p.property_id=u.property_id
 WHERE u.unit_id=p_unit_id AND u.unit_class='dwelling' AND u.use_class='residential'
   AND u.lifecycle_status='active';
 IF NOT FOUND OR v_address IS DISTINCT FROM p_bp04_address_id THEN
  RAISE EXCEPTION 'household unit must be an active residential dwelling at the supplied BP04 address';
 END IF;
 IF NOT EXISTS(SELECT 1 FROM sw_geo.bp04_bp02_address_link
  WHERE bp04_address_id=p_bp04_address_id
    AND bp02_address_source_id=p_address_source_id) THEN
  RAISE EXCEPTION 'BP04 dwelling address has no verified BP02 address crosswalk';
 END IF;
 SELECT * INTO v_existing FROM sw_people.household WHERE source_ref=p_source_ref;
 IF FOUND THEN
  IF v_existing.household_ref=p_household_ref AND v_existing.unit_id=p_unit_id
   AND v_existing.bp04_address_id=p_bp04_address_id
   AND v_existing.address_source_id=p_address_source_id THEN RETURN v_existing.household_id; END IF;
  RAISE EXCEPTION 'household source_ref replay conflicts with its original identity';
 END IF;
 SELECT world_tick INTO STRICT v_tick FROM sw_runtime.state WHERE singleton=1;
 INSERT INTO sw_core.simulation_event(
  event_type_id,occurred_at,world_tick,subject_kind,source_ref,attributes,idempotency_key
 ) SELECT event_type_id,clock_timestamp(),v_tick,'household',p_source_ref,
  jsonb_build_object('household_ref',p_household_ref,'unit_id',p_unit_id,
   'bp04_address_id',p_bp04_address_id,'address_source_id',p_address_source_id,
   'actor_ref',p_actor_ref,'reason',p_reason),
  'SW-BP03:HOUSEHOLD:'||p_source_ref
 FROM sw_core.event_type WHERE event_code='HOUSEHOLD_CREATED'
 RETURNING event_id INTO v_event;
 IF v_event IS NULL THEN RAISE EXCEPTION 'HOUSEHOLD_CREATED event type is missing'; END IF;
 INSERT INTO sw_people.household(
  household_ref,unit_id,bp04_address_id,address_source_id,effective_from_tick,source_ref,last_event_id
 ) VALUES(p_household_ref,p_unit_id,p_bp04_address_id,p_address_source_id,v_tick,p_source_ref,v_event)
 RETURNING household_id INTO v_id;
 INSERT INTO sw_people.household_history(
  event_id,household_id,event_kind,effective_tick,source_ref,actor_ref,reason
 ) VALUES(v_event,v_id,'household_created',v_tick,p_source_ref,p_actor_ref,p_reason);
 RETURN v_id;
END $$;

CREATE FUNCTION sw_people.add_household_member(
 p_household_id integer,p_person_id integer,p_member_role text,
 p_source_ref text,p_actor_ref text,p_reason text
) RETURNS bigint
LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,sw_people,sw_geo,sw_runtime,sw_core
AS $$
DECLARE v_household sw_people.household%ROWTYPE; v_state sw_people.population_state%ROWTYPE;
 v_tick bigint; v_event bigint; v_member bigint; v_existing sw_people.household_member%ROWTYPE;
BEGIN
 IF p_household_id IS NULL OR p_person_id IS NULL
  OR p_member_role IS NULL OR p_member_role NOT IN ('member','household_contact','other')
  OR p_source_ref IS NULL OR length(btrim(p_source_ref)) NOT BETWEEN 1 AND 200
  OR p_actor_ref IS NULL OR length(btrim(p_actor_ref)) NOT BETWEEN 1 AND 120
  OR p_reason IS NULL OR length(btrim(p_reason)) NOT BETWEEN 1 AND 240 THEN
  RAISE EXCEPTION 'household, person, role and bounded provenance are required';
 END IF;
 SELECT * INTO v_household FROM sw_people.household WHERE household_id=p_household_id FOR UPDATE;
 IF NOT FOUND OR v_household.household_status<>'current' THEN
  RAISE EXCEPTION 'current household does not exist';
 END IF;
 SELECT * INTO v_state FROM sw_people.population_state WHERE person_id=p_person_id FOR UPDATE;
 IF NOT FOUND OR v_state.life_status<>1 OR NOT v_state.usual_resident THEN
  RAISE EXCEPTION 'household members must be living usual residents';
 END IF;
 IF NOT EXISTS(SELECT 1 FROM sw_people.person_residence
   WHERE person_id=p_person_id AND residence_status='current'
     AND address_source_id=v_household.address_source_id) THEN
  RAISE EXCEPTION 'person current residence does not match household BP02 address';
 END IF;
 SELECT * INTO v_existing FROM sw_people.household_member WHERE source_ref=p_source_ref;
 IF FOUND THEN
  IF v_existing.household_id=p_household_id AND v_existing.person_id=p_person_id
   AND v_existing.member_role=p_member_role THEN RETURN v_existing.household_member_id; END IF;
  RAISE EXCEPTION 'household membership source_ref replay conflicts with its original assignment';
 END IF;
 IF EXISTS(SELECT 1 FROM sw_people.household_member
   WHERE person_id=p_person_id AND membership_status='current') THEN
  RAISE EXCEPTION 'person already belongs to a current household';
 END IF;
 SELECT world_tick INTO STRICT v_tick FROM sw_runtime.state WHERE singleton=1;
 INSERT INTO sw_core.simulation_event(
  event_type_id,occurred_at,world_tick,subject_kind,subject_id,source_ref,attributes,idempotency_key
 ) SELECT event_type_id,clock_timestamp(),v_tick,'person',p_person_id,p_source_ref,
  jsonb_build_object('household_id',p_household_id,'member_role',p_member_role,
   'actor_ref',p_actor_ref,'reason',p_reason),
  'SW-BP03:HOUSEHOLD-MEMBER:'||p_person_id||':'||p_source_ref
 FROM sw_core.event_type WHERE event_code='HOUSEHOLD_MEMBER_ADDED'
 RETURNING event_id INTO v_event;
 IF v_event IS NULL THEN RAISE EXCEPTION 'HOUSEHOLD_MEMBER_ADDED event type is missing'; END IF;
 INSERT INTO sw_people.household_member(
  household_id,person_id,member_role,effective_from_tick,source_ref,last_event_id
 ) VALUES(p_household_id,p_person_id,p_member_role,v_tick,p_source_ref,v_event)
 RETURNING household_member_id INTO v_member;
 INSERT INTO sw_people.household_history(
  event_id,household_id,person_id,event_kind,new_role,effective_tick,source_ref,actor_ref,reason
 ) VALUES(v_event,p_household_id,p_person_id,'member_added',p_member_role,v_tick,p_source_ref,p_actor_ref,p_reason);
 RETURN v_member;
END $$;

CREATE FUNCTION sw_people.end_household_membership(
 p_person_id integer,p_source_ref text,p_actor_ref text,p_reason text
) RETURNS boolean
LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,sw_people,sw_runtime,sw_core
AS $$
DECLARE v_member sw_people.household_member%ROWTYPE; v_tick bigint; v_event bigint;
BEGIN
 IF p_person_id IS NULL OR p_source_ref IS NULL OR length(btrim(p_source_ref)) NOT BETWEEN 1 AND 200
  OR p_actor_ref IS NULL OR length(btrim(p_actor_ref)) NOT BETWEEN 1 AND 120
  OR p_reason IS NULL OR length(btrim(p_reason)) NOT BETWEEN 1 AND 240 THEN
  RAISE EXCEPTION 'person and bounded provenance are required';
 END IF;
 SELECT * INTO v_member FROM sw_people.household_member
  WHERE person_id=p_person_id AND membership_status='current' FOR UPDATE;
 IF NOT FOUND THEN RETURN false; END IF;
 SELECT world_tick INTO STRICT v_tick FROM sw_runtime.state WHERE singleton=1;
 INSERT INTO sw_core.simulation_event(
  event_type_id,occurred_at,world_tick,subject_kind,subject_id,source_ref,attributes,idempotency_key
 ) SELECT event_type_id,clock_timestamp(),v_tick,'person',p_person_id,p_source_ref,
  jsonb_build_object('household_id',v_member.household_id,'prior_role',v_member.member_role,
   'actor_ref',p_actor_ref,'reason',p_reason),
  'SW-BP03:HOUSEHOLD-MEMBER-END:'||p_person_id||':'||p_source_ref
 FROM sw_core.event_type WHERE event_code='HOUSEHOLD_MEMBER_ENDED'
 RETURNING event_id INTO v_event;
 IF v_event IS NULL THEN RAISE EXCEPTION 'HOUSEHOLD_MEMBER_ENDED event type is missing'; END IF;
 UPDATE sw_people.household_member SET membership_status='ended',
  effective_to_tick=GREATEST(v_tick,effective_from_tick)
 WHERE household_member_id=v_member.household_member_id;
 INSERT INTO sw_people.household_history(
  event_id,household_id,person_id,event_kind,prior_role,effective_tick,source_ref,actor_ref,reason
 ) VALUES(v_event,v_member.household_id,p_person_id,'member_ended',v_member.member_role,
  v_tick,p_source_ref,p_actor_ref,p_reason);
 RETURN true;
END $$;

CREATE VIEW sw_people.household_summary AS
SELECT h.household_id,h.household_ref,h.unit_id,h.address_source_id,
 count(m.household_member_id) FILTER(WHERE m.membership_status='current')::integer AS current_member_count,
 count(m.household_member_id) FILTER(WHERE m.membership_status='current' AND m.member_role='household_contact')::integer AS contact_count
FROM sw_people.household h LEFT JOIN sw_people.household_member m USING(household_id)
WHERE h.household_status='current'
GROUP BY h.household_id,h.household_ref,h.unit_id,h.address_source_id;

REVOKE ALL ON sw_geo.bp04_bp02_address_link FROM PUBLIC;
GRANT SELECT ON sw_geo.bp04_bp02_address_link TO sw_game_readonly;
REVOKE ALL ON sw_people.household,sw_people.household_member,sw_people.household_history FROM PUBLIC;
GRANT SELECT ON sw_people.household,sw_people.household_member,sw_people.household_history,sw_people.household_summary TO sw_game_readonly;
REVOKE ALL ON FUNCTION sw_geo.link_bp04_bp02_address(text,text,text,text) FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_people.reject_household_history_mutation() FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_people.create_household(text,text,text,text,text,text,text) FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_people.add_household_member(integer,integer,text,text,text,text) FROM PUBLIC;
REVOKE ALL ON FUNCTION sw_people.end_household_membership(integer,text,text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION sw_geo.link_bp04_bp02_address(text,text,text,text) TO sw_game_command;
GRANT EXECUTE ON FUNCTION sw_people.create_household(text,text,text,text,text,text,text) TO sw_game_command;
GRANT EXECUTE ON FUNCTION sw_people.add_household_member(integer,integer,text,text,text,text) TO sw_game_command;
GRANT EXECUTE ON FUNCTION sw_people.end_household_membership(integer,text,text,text) TO sw_game_command;
COMMIT;
