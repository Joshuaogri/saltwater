-- PKG-004 accepted-player identity binding.
-- Disposable PostgreSQL validation only. Neon production is NOT authorised.
-- Depends on proposals 0002, 0003 and 0004.
BEGIN;

CREATE TABLE sw_player.identity_binding (
  binding_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  principal_id uuid NOT NULL UNIQUE REFERENCES sw_auth.principal(principal_id),
  player_id uuid NOT NULL UNIQUE REFERENCES sw_player.profile(player_id),
  person_id integer NOT NULL UNIQUE REFERENCES sw_people.person(person_id),
  bound_at timestamptz NOT NULL DEFAULT now(),
  source_code text NOT NULL CHECK (source_code='accepted_recruit_career'),
  UNIQUE (principal_id,player_id,person_id)
);

CREATE FUNCTION sw_player.reject_identity_binding_mutation() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'player identity bindings are immutable and append-only';
END
$$;
CREATE TRIGGER player_identity_binding_immutable
BEFORE UPDATE OR DELETE ON sw_player.identity_binding
FOR EACH ROW EXECUTE FUNCTION sw_player.reject_identity_binding_mutation();

CREATE FUNCTION sw_auth.guard_principal_person_link() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  IF OLD.person_id IS NOT NULL AND NEW.person_id IS DISTINCT FROM OLD.person_id THEN
    RAISE EXCEPTION 'principal canonical-person link cannot be reassigned';
  END IF;
  RETURN NEW;
END
$$;
CREATE TRIGGER principal_person_link_immutable
BEFORE UPDATE OF person_id ON sw_auth.principal
FOR EACH ROW EXECUTE FUNCTION sw_auth.guard_principal_person_link();

-- Called inside the same transaction that issues the initial session.
-- Returns the canonical person resolved exclusively through accepted career/personnel.
CREATE FUNCTION sw_player.bind_accepted_identity(
  p_principal_id uuid,
  p_player_id uuid
) RETURNS integer
LANGUAGE plpgsql AS $$
DECLARE
  v_principal sw_auth.principal%ROWTYPE;
  v_person_id integer;
  v_existing sw_player.identity_binding%ROWTYPE;
  v_binding_count integer;
BEGIN
  IF p_principal_id IS NULL OR p_player_id IS NULL THEN
    RAISE EXCEPTION 'principal and player identifiers are required';
  END IF;

  SELECT * INTO v_principal
  FROM sw_auth.principal
  WHERE principal_id=p_principal_id
  FOR UPDATE;
  IF NOT FOUND OR v_principal.status <> 'active' OR v_principal.principal_kind <> 'player' THEN
    RAISE EXCEPTION 'principal must exist, be active and have player kind';
  END IF;

  PERFORM 1 FROM sw_player.profile WHERE player_id=p_player_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'player profile does not exist'; END IF;

  PERFORM 1
  FROM sw_police.career_episode c
  JOIN sw_police.recruit_intake i ON i.player_id=c.player_id AND i.status='accepted'
  JOIN sw_police.personnel p ON p.personnel_id=c.personnel_id
  JOIN sw_people.person person ON person.person_id=p.person_id
  JOIN sw_people.population_state pop ON pop.person_id=person.person_id
  WHERE c.player_id=p_player_id
    AND c.career_stage='recruit'
    AND c.career_status='active'
    AND p.service_standing='recruit'
    AND p.service_status='active'
    AND pop.life_status=1
    AND pop.scope_status=1
  FOR SHARE OF c,i,p,person,pop;
  GET DIAGNOSTICS v_binding_count = ROW_COUNT;

  SELECT person.person_id INTO v_person_id
  FROM sw_police.career_episode c
  JOIN sw_police.recruit_intake i ON i.player_id=c.player_id AND i.status='accepted'
  JOIN sw_police.personnel p ON p.personnel_id=c.personnel_id
  JOIN sw_people.person person ON person.person_id=p.person_id
  JOIN sw_people.population_state pop ON pop.person_id=person.person_id
  WHERE c.player_id=p_player_id
    AND c.career_stage='recruit'
    AND c.career_status='active'
    AND p.service_standing='recruit'
    AND p.service_status='active'
    AND pop.life_status=1
    AND pop.scope_status=1
  LIMIT 1;

  IF v_binding_count <> 1 OR v_person_id IS NULL THEN
    RAISE EXCEPTION 'exactly one accepted active recruit career with active personnel and living canonical person is required';
  END IF;

  IF v_principal.person_id IS NOT NULL AND v_principal.person_id <> v_person_id THEN
    RAISE EXCEPTION 'principal is already linked to a different canonical person';
  END IF;

  SELECT * INTO v_existing FROM sw_player.identity_binding
  WHERE principal_id=p_principal_id OR player_id=p_player_id OR person_id=v_person_id
  FOR UPDATE;
  IF FOUND THEN
    IF v_existing.principal_id=p_principal_id
       AND v_existing.player_id=p_player_id
       AND v_existing.person_id=v_person_id THEN
      RETURN v_person_id;
    END IF;
    RAISE EXCEPTION 'principal, player or person is already bound to a different identity';
  END IF;

  INSERT INTO sw_player.identity_binding
    (principal_id,player_id,person_id,source_code)
  VALUES (p_principal_id,p_player_id,v_person_id,'accepted_recruit_career');

  UPDATE sw_auth.principal SET person_id=v_person_id, updated_at=now()
  WHERE principal_id=p_principal_id AND person_id IS NULL;

  RETURN v_person_id;
END
$$;

REVOKE ALL ON sw_player.identity_binding FROM PUBLIC, sw_game_readonly, sw_game_command;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA sw_player FROM PUBLIC, sw_game_readonly, sw_game_command;
REVOKE ALL ON FUNCTION sw_player.bind_accepted_identity(uuid,uuid) FROM PUBLIC, sw_game_readonly, sw_game_command;
REVOKE ALL ON FUNCTION sw_player.reject_identity_binding_mutation() FROM PUBLIC, sw_game_readonly, sw_game_command;
COMMIT;
