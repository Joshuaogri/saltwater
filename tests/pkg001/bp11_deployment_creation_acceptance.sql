\set ON_ERROR_STOP on
DO $bp11$
BEGIN
  IF to_regprocedure('sw_police.create_authorised_unit_deployment(text,integer,uuid[],text,smallint,text,text,text,text,bigint)') IS NULL THEN
    RAISE EXCEPTION 'BP11 authorised deployment creation function missing';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
    WHERE n.nspname='sw_police' AND p.proname='create_authorised_unit_deployment'
      AND p.prosecdef=false
  ) THEN RAISE EXCEPTION 'deployment creation must not be SECURITY DEFINER'; END IF;
END
$bp11$;
SELECT 'BP11 authorised deployment creation acceptance passed' AS result;
