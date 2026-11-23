-- PKG-001 security persistence proposal 0003.
-- Disposable PostgreSQL validation only. NEVER apply to Neon under PKG-001.
-- Provider-neutral game identities; no credentials, raw tokens or hidden truth.
CREATE SCHEMA sw_auth;
REVOKE ALL ON SCHEMA sw_auth FROM PUBLIC;
GRANT USAGE ON SCHEMA sw_auth TO sw_game_readonly, sw_game_command;

CREATE TABLE sw_auth.policy_version (
  policy_version text PRIMARY KEY,
  created_at timestamptz NOT NULL DEFAULT now(),
  description text NOT NULL,
  active boolean NOT NULL DEFAULT false
);
CREATE UNIQUE INDEX policy_one_active_idx ON sw_auth.policy_version(active) WHERE active;

CREATE TABLE sw_auth.principal (
  principal_id uuid PRIMARY KEY,
  issuer text NOT NULL CHECK (length(issuer) BETWEEN 1 AND 200),
  subject text NOT NULL CHECK (length(subject) BETWEEN 1 AND 240),
  principal_kind text NOT NULL CHECK (principal_kind IN
    ('player','officer','administrator','operator','developer','service','system','test')),
  status text NOT NULL DEFAULT 'active' CHECK (status IN ('active','suspended','locked','disabled')),
  person_id integer REFERENCES sw_people.person(person_id),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (issuer, subject)
);
CREATE INDEX principal_status_idx ON sw_auth.principal(status) WHERE status <> 'active';

CREATE TABLE sw_auth.session (
  session_id uuid PRIMARY KEY,
  principal_id uuid NOT NULL REFERENCES sw_auth.principal(principal_id),
  credential_digest bytea NOT NULL UNIQUE CHECK (octet_length(credential_digest)=32),
  status text NOT NULL DEFAULT 'active' CHECK (status IN ('active','restricted','expired','revoked','terminated')),
  issued_at timestamptz NOT NULL,
  expires_at timestamptz NOT NULL,
  active_person_id integer REFERENCES sw_people.person(person_id),
  authentication_strength text NOT NULL DEFAULT 'standard' CHECK (authentication_strength IN ('standard','strong','recovery')),
  policy_version text NOT NULL REFERENCES sw_auth.policy_version(policy_version),
  correlation_id uuid,
  revoked_at timestamptz,
  CHECK (expires_at > issued_at),
  CHECK ((status='revoked') = (revoked_at IS NOT NULL))
);
CREATE INDEX session_principal_status_idx ON sw_auth.session(principal_id,status);
CREATE INDEX session_expiry_idx ON sw_auth.session(expires_at) WHERE status='active';

CREATE TABLE sw_auth.principal_role (
  principal_id uuid NOT NULL REFERENCES sw_auth.principal(principal_id),
  role_code text NOT NULL CHECK (length(role_code) BETWEEN 1 AND 80),
  assigned_at timestamptz NOT NULL DEFAULT now(),
  assigned_by uuid REFERENCES sw_auth.principal(principal_id),
  revoked_at timestamptz,
  assignment_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  CHECK (revoked_at IS NULL OR revoked_at >= assigned_at)
);
CREATE UNIQUE INDEX principal_role_one_active_idx
  ON sw_auth.principal_role(principal_id,role_code) WHERE revoked_at IS NULL;
CREATE INDEX principal_role_active_idx ON sw_auth.principal_role(principal_id) WHERE revoked_at IS NULL;

CREATE TABLE sw_auth.permission_grant (
  grant_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  action text NOT NULL CHECK (length(action) BETWEEN 1 AND 120),
  resource_pattern text NOT NULL CHECK (length(resource_pattern) BETWEEN 1 AND 240),
  purpose text NOT NULL CHECK (length(purpose) BETWEEN 1 AND 120),
  effect text NOT NULL CHECK (effect IN ('allow','deny')),
  principal_id uuid REFERENCES sw_auth.principal(principal_id),
  principal_kind text CHECK (principal_kind IS NULL OR principal_kind IN
    ('player','officer','administrator','operator','developer','service','system','test')),
  role_code text,
  valid_from timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz,
  revoked_at timestamptz,
  policy_version text NOT NULL REFERENCES sw_auth.policy_version(policy_version),
  CHECK (principal_id IS NOT NULL OR principal_kind IS NOT NULL OR role_code IS NOT NULL),
  CHECK (expires_at IS NULL OR expires_at > valid_from),
  CHECK (revoked_at IS NULL OR revoked_at >= valid_from)
);
CREATE INDEX permission_match_idx ON sw_auth.permission_grant(action,purpose,effect)
  WHERE revoked_at IS NULL;

CREATE TABLE sw_auth.audit (
  audit_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  decided_at timestamptz NOT NULL,
  principal_id uuid REFERENCES sw_auth.principal(principal_id),
  session_id uuid REFERENCES sw_auth.session(session_id),
  action text NOT NULL,
  resource text NOT NULL,
  purpose text NOT NULL,
  allowed boolean NOT NULL,
  reason text NOT NULL,
  policy_version text NOT NULL,
  correlation_id uuid
);
CREATE INDEX auth_audit_time_idx ON sw_auth.audit(decided_at DESC);

CREATE FUNCTION sw_auth.reject_immutable_change() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION '% is append-only; record a new version or lifecycle event', TG_TABLE_NAME;
END
$$;
CREATE FUNCTION sw_auth.guard_policy_version_change() RETURNS trigger
LANGUAGE plpgsql AS $
BEGIN
  IF TG_OP='DELETE' THEN RAISE EXCEPTION 'policy versions cannot be deleted'; END IF;
  IF (NEW.policy_version,NEW.created_at,NEW.description)
     IS DISTINCT FROM (OLD.policy_version,OLD.created_at,OLD.description) THEN
    RAISE EXCEPTION 'policy version definitions are immutable';
  END IF;
  IF OLD.active=false OR NEW.active=true THEN
    RAISE EXCEPTION 'a policy version may only be deactivated once';
  END IF;
  RETURN NEW;
END
$;
CREATE TRIGGER policy_version_lifecycle
BEFORE UPDATE OR DELETE ON sw_auth.policy_version
FOR EACH ROW EXECUTE FUNCTION sw_auth.guard_policy_version_change();

CREATE FUNCTION sw_auth.guard_role_assignment_change() RETURNS trigger
LANGUAGE plpgsql AS $
BEGIN
  IF TG_OP='DELETE' THEN RAISE EXCEPTION 'role assignments cannot be deleted'; END IF;
  IF (NEW.assignment_id,NEW.principal_id,NEW.role_code,NEW.assigned_at,NEW.assigned_by)
     IS DISTINCT FROM (OLD.assignment_id,OLD.principal_id,OLD.role_code,OLD.assigned_at,OLD.assigned_by) THEN
    RAISE EXCEPTION 'role assignment facts are immutable';
  END IF;
  IF OLD.revoked_at IS NOT NULL OR NEW.revoked_at IS NULL THEN
    RAISE EXCEPTION 'a role assignment may only be revoked once';
  END IF;
  RETURN NEW;
END
$;
CREATE TRIGGER role_assignment_lifecycle
BEFORE UPDATE OR DELETE ON sw_auth.principal_role
FOR EACH ROW EXECUTE FUNCTION sw_auth.guard_role_assignment_change();
CREATE TRIGGER auth_audit_immutable
BEFORE UPDATE OR DELETE ON sw_auth.audit
FOR EACH ROW EXECUTE FUNCTION sw_auth.reject_immutable_change();

CREATE FUNCTION sw_auth.guard_grant_change() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  IF TG_OP='DELETE' THEN RAISE EXCEPTION 'permission grants cannot be deleted'; END IF;
  IF (NEW.grant_id,NEW.action,NEW.resource_pattern,NEW.purpose,NEW.effect,
      NEW.principal_id,NEW.principal_kind,NEW.role_code,NEW.valid_from,
      NEW.expires_at,NEW.policy_version)
     IS DISTINCT FROM
     (OLD.grant_id,OLD.action,OLD.resource_pattern,OLD.purpose,OLD.effect,
      OLD.principal_id,OLD.principal_kind,OLD.role_code,OLD.valid_from,
      OLD.expires_at,OLD.policy_version) THEN
    RAISE EXCEPTION 'permission grant definition is immutable';
  END IF;
  IF OLD.revoked_at IS NOT NULL OR NEW.revoked_at IS NULL THEN
    RAISE EXCEPTION 'a permission grant may only be revoked once';
  END IF;
  RETURN NEW;
END
$$;
CREATE TRIGGER permission_grant_lifecycle
BEFORE UPDATE OR DELETE ON sw_auth.permission_grant
FOR EACH ROW EXECUTE FUNCTION sw_auth.guard_grant_change();

CREATE FUNCTION sw_auth.guard_session_change() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  IF (NEW.session_id,NEW.principal_id,NEW.credential_digest,NEW.issued_at,
      NEW.expires_at,NEW.active_person_id,NEW.authentication_strength,
      NEW.policy_version,NEW.correlation_id)
     IS DISTINCT FROM
     (OLD.session_id,OLD.principal_id,OLD.credential_digest,OLD.issued_at,
      OLD.expires_at,OLD.active_person_id,OLD.authentication_strength,
      OLD.policy_version,OLD.correlation_id) THEN
    RAISE EXCEPTION 'session identity and issuance facts are immutable';
  END IF;
  IF OLD.status IN ('revoked','terminated','expired') AND NEW.status <> OLD.status THEN
    RAISE EXCEPTION 'terminal session status cannot be reversed';
  END IF;
  IF NEW.status='revoked' AND OLD.status<>'revoked' AND NEW.revoked_at IS NULL THEN
    RAISE EXCEPTION 'revocation timestamp required';
  END IF;
  IF NEW.status<>'revoked' AND NEW.revoked_at IS NOT NULL THEN
    RAISE EXCEPTION 'revocation timestamp/status mismatch';
  END IF;
  RETURN NEW;
END
$$;
CREATE TRIGGER session_lifecycle
BEFORE UPDATE ON sw_auth.session
FOR EACH ROW EXECUTE FUNCTION sw_auth.guard_session_change();

-- No direct DML for ordinary game roles. A future narrow auth API/service owns writes.
REVOKE ALL ON ALL TABLES IN SCHEMA sw_auth FROM PUBLIC, sw_game_readonly, sw_game_command;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA sw_auth FROM PUBLIC, sw_game_readonly, sw_game_command;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA sw_auth FROM PUBLIC, sw_game_readonly, sw_game_command;
