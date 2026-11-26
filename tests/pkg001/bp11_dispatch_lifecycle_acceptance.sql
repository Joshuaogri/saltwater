DO $bp11$
BEGIN
  IF to_regprocedure('sw_police.transition_unit_deployment(uuid,text,text,text,text,text,text,text,bigint)') IS NULL THEN
    RAISE EXCEPTION 'BP11 deployment transition writer missing';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM pg_proc p
    JOIN pg_namespace n ON n.oid=p.pronamespace
    WHERE n.nspname='sw_police' AND p.proname='transition_unit_deployment'
      AND p.prosecdef=false
  ) THEN RAISE EXCEPTION 'BP11 transition writer must not be SECURITY DEFINER'; END IF;
END
$bp11$;
SELECT 'BP11 deployment transition writer acceptance passed' AS result;
