\set ON_ERROR_STOP on
DO $bp08$
BEGIN
  IF (SELECT count(*) FROM sw_police.unit_profile)<>31
     OR (SELECT count(*) FROM sw_police.unit_readiness)<>31 THEN
    RAISE EXCEPTION 'all 31 canonical operational units must have a profile and readiness projection';
  END IF;
  IF EXISTS(
    SELECT 1 FROM sw_police.unit_profile u
    JOIN sw_police.organisation_component c ON c.component_id=u.unit_id
    WHERE c.component_type<>'unit' OR u.geographic_scope<>'SALTWATER_CITY_STATE'
       OR cardinality(u.capability_codes)=0
  ) THEN RAISE EXCEPTION 'unit profile identity, geography or capability data invalid'; END IF;
  IF (SELECT count(*) FROM sw_police.unit_establishment)<>31
     OR (SELECT sum(authorised_posts) FROM sw_police.unit_establishment)<>480
     OR (SELECT sum(vacant_posts) FROM sw_police.unit_establishment)<>480
     OR (SELECT sum(filled_posts) FROM sw_police.unit_establishment)<>0 THEN
    RAISE EXCEPTION 'unit establishment does not reconcile to 480 vacant unit posts';
  END IF;
  IF (SELECT count(*) FROM sw_police.unit_profile WHERE dispatchable)<>7 THEN
    RAISE EXCEPTION 'dispatchable unit catalogue count incorrect';
  END IF;
  IF (SELECT count(*) FROM sw_police.unit_membership)<>0
     OR (SELECT count(*) FROM sw_police.unit_deployment)<>0
     OR (SELECT count(*) FROM sw_police.unit_status_event)<>0 THEN
    RAISE EXCEPTION 'unit catalogue seed must not invent memberships, deployments or availability';
  END IF;
  IF (SELECT count(*) FROM sw_police.unit_current_status WHERE operational_status='unavailable')<>31
     OR (SELECT count(*) FROM sw_police.unit_readiness WHERE dispatch_eligible)<>0
     OR (SELECT count(*) FROM sw_police.unit_readiness WHERE staffing_eligible)<>0 THEN
    RAISE EXCEPTION 'unstaffed units must remain unavailable and not dispatch eligible';
  END IF;
  IF NOT EXISTS(
    SELECT 1 FROM pg_trigger
    WHERE tgname='unit_membership_from_career_post' AND NOT tgisinternal
  ) THEN RAISE EXCEPTION 'career post to unit membership integration trigger missing'; END IF;
END
$bp08$;
SELECT 'BP08 unit catalogue and readiness acceptance passed' AS result;
