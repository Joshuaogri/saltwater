\set ON_ERROR_STOP on
DO $bp05$
DECLARE
  v_components integer;
  v_posts integer;
  v_positions integer;
  v_reporting integer;
BEGIN
  SELECT count(*) INTO v_components FROM sw_police.organisation_component;
  IF v_components<>48 THEN RAISE EXCEPTION 'expected 48 organisational components, found %',v_components; END IF;
  IF (SELECT count(*) FROM sw_police.organisation_component WHERE component_type='department')<>1
     OR (SELECT count(*) FROM sw_police.organisation_component WHERE component_type='command')<>4
     OR (SELECT count(*) FROM sw_police.organisation_component WHERE component_type='division')<>12
     OR (SELECT count(*) FROM sw_police.organisation_component WHERE component_type='unit')<>31 THEN
    RAISE EXCEPTION 'Saltwater Police Service hierarchy counts are incorrect';
  END IF;
  IF (SELECT count(*) FROM sw_police.current_organisation_component)<>48 THEN
    RAISE EXCEPTION 'current component view does not resolve every component';
  END IF;
  IF (SELECT count(*) FROM sw_police.rank_definition)<>9
     OR EXISTS(SELECT 1 FROM sw_police.rank_definition WHERE rank_code='RECRUIT') THEN
    RAISE EXCEPTION 'rank catalogue must contain nine substantive ranks and must not treat recruit as a rank';
  END IF;
  SELECT count(*) INTO v_positions FROM sw_police.position_definition;
  IF v_positions<>24 THEN RAISE EXCEPTION 'expected 24 position definitions, found %',v_positions; END IF;
  SELECT count(*) INTO v_posts FROM sw_police.authorised_post;
  IF v_posts<>500 THEN RAISE EXCEPTION 'expected 500 authorised establishment posts, found %',v_posts; END IF;
  IF (SELECT count(*) FROM sw_police.authorised_post WHERE post_status='vacant')<>500
     OR (SELECT count(*) FROM sw_police.authorised_post WHERE post_status<>'vacant')<>0 THEN
    RAISE EXCEPTION 'initial 500-post establishment must be vacant, not fictitiously staffed';
  END IF;
  IF (SELECT count(*) FROM sw_police.authorised_post_event)<>500 THEN
    RAISE EXCEPTION 'each authorised post must have its initial history event';
  END IF;
  SELECT count(*) INTO v_reporting FROM sw_police.reporting_relationship;
  IF v_reporting<>47 THEN RAISE EXCEPTION 'expected 47 parent reporting links, found %',v_reporting; END IF;
  IF EXISTS(
    SELECT 1 FROM sw_police.organisation_component_version v
    JOIN sw_police.organisation_component c ON c.component_id=v.component_id
    LEFT JOIN sw_police.organisation_component p ON p.component_id=v.parent_component_id
    WHERE (c.component_type='department' AND v.parent_component_id IS NOT NULL)
       OR (c.component_type<>'department' AND p.component_id IS NULL)
       OR (c.component_type='command' AND p.component_type<>'department')
       OR (c.component_type='division' AND p.component_type<>'command')
       OR (c.component_type='unit' AND p.component_type<>'division')
  ) THEN RAISE EXCEPTION 'organisational hierarchy parent/type mismatch'; END IF;
  IF EXISTS(
    SELECT 1 FROM sw_police.authorised_post p
    LEFT JOIN sw_police.position_definition d USING(position_id)
    LEFT JOIN sw_police.organisation_component c ON c.component_id=p.component_id
    WHERE d.position_id IS NULL OR c.component_id IS NULL
  ) THEN RAISE EXCEPTION 'authorised post has unresolved position or component'; END IF;
  IF (SELECT count(*) FROM sw_police.personnel)<>0 THEN
    RAISE EXCEPTION 'architecture seed must not invent or appoint personnel';
  END IF;
END
$bp05$;
SELECT 'BP05 Saltwater Police Service architecture acceptance passed' AS result;
