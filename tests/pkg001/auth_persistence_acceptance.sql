-- PKG-001 auth persistence acceptance. Disposable PostgreSQL only.
BEGIN;
DO $$
DECLARE
  pid uuid := '00000000-0000-4000-8000-000000000001';
  sid uuid := '00000000-0000-4000-8000-000000000002';
  rid bigint;
  denied boolean := false;
BEGIN
  INSERT INTO sw_auth.policy_version(policy_version,description,active)
    VALUES ('test-policy-1','Disposable acceptance policy',true);
  INSERT INTO sw_auth.principal(principal_id,issuer,subject,principal_kind)
    VALUES (pid,'saltwater-test','player-1','player');
  INSERT INTO sw_auth.session(session_id,principal_id,credential_digest,issued_at,expires_at,policy_version)
    VALUES (sid,pid,decode(repeat('ab',32),'hex'),now(),now()+interval '1 hour','test-policy-1');
  INSERT INTO sw_auth.principal_role(principal_id,role_code) VALUES(pid,'player');
  INSERT INTO sw_auth.permission_grant(action,resource_pattern,purpose,effect,principal_kind,policy_version)
    VALUES ('read_case','case/*','active_play','allow','player','test-policy-1')
    RETURNING grant_id INTO rid;
  INSERT INTO sw_auth.audit(decided_at,principal_id,session_id,action,resource,purpose,allowed,reason,policy_version)
    VALUES (now(),pid,sid,'read_case','case/test','active_play',true,'explicit_allow','test-policy-1');

  IF (SELECT count(*) FROM sw_auth.principal_role WHERE principal_id=pid AND revoked_at IS NULL)<>1
    THEN RAISE EXCEPTION 'role assignment missing'; END IF;
  IF (SELECT count(*) FROM sw_auth.permission_grant WHERE grant_id=rid AND revoked_at IS NULL)<>1
    THEN RAISE EXCEPTION 'permission grant missing'; END IF;
  IF has_table_privilege('sw_game_command','sw_auth.audit','INSERT')
    OR has_table_privilege('sw_game_command','sw_auth.session','SELECT')
    OR has_table_privilege('sw_game_readonly','sw_auth.principal','SELECT') THEN
    RAISE EXCEPTION 'unexpected direct auth-table privilege';
  END IF;

  BEGIN
    UPDATE sw_auth.audit SET reason='tampered' WHERE principal_id=pid;
  EXCEPTION WHEN raise_exception THEN denied := true;
  END;
  IF NOT denied THEN RAISE EXCEPTION 'audit mutation was not rejected'; END IF;

  UPDATE sw_auth.permission_grant SET revoked_at=now() WHERE grant_id=rid;
  BEGIN
    UPDATE sw_auth.permission_grant SET effect='deny' WHERE grant_id=rid;
    RAISE EXCEPTION 'grant definition mutation unexpectedly succeeded';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='grant definition mutation unexpectedly succeeded' THEN RAISE; END IF;
  END;

  UPDATE sw_auth.session SET status='revoked',revoked_at=now() WHERE session_id=sid;
  BEGIN
    UPDATE sw_auth.session SET status='active',revoked_at=NULL WHERE session_id=sid;
    RAISE EXCEPTION 'revoked session was reactivated';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM='revoked session was reactivated' THEN RAISE; END IF;
  END;
END $$;
ROLLBACK;
