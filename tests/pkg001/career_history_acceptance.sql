\set ON_ERROR_STOP on
DO $bp07$
DECLARE v_careers bigint;
BEGIN
  SELECT count(*) INTO v_careers FROM sw_police.career_episode;
  IF (SELECT count(*) FROM sw_police.career_event WHERE event_kind='career_opened')<>v_careers THEN
    RAISE EXCEPTION 'every career episode must have one opening event';
  END IF;
  IF EXISTS(
    SELECT 1 FROM sw_police.career_episode c
    LEFT JOIN sw_police.career_event e ON e.career_id=c.career_id AND e.event_kind='career_opened'
    WHERE e.career_id IS NULL OR e.event_id<>c.start_event_id
       OR e.effective_tick<>c.started_tick
  ) THEN RAISE EXCEPTION 'career opening event does not match authoritative episode facts'; END IF;
  IF (SELECT count(*) FROM sw_police.career_rank_assignment)<>0
     OR (SELECT count(*) FROM sw_police.career_post_appointment)<>0 THEN
    RAISE EXCEPTION 'recruit entry must not invent substantive rank or post appointment';
  END IF;
  IF (SELECT count(*) FROM sw_police.career_current_rank)<>0
     OR (SELECT count(*) FROM sw_police.career_current_post)<>0 THEN
    RAISE EXCEPTION 'unassigned recruit must have no current rank or post projection';
  END IF;
  IF EXISTS(
    SELECT 1 FROM sw_police.career_episode c
    JOIN sw_police.personnel p ON p.personnel_id=c.personnel_id
    WHERE c.career_stage='recruit' AND p.service_standing<>'recruit'
  ) THEN RAISE EXCEPTION 'recruit career and personnel service standing disagree'; END IF;
  IF (SELECT count(*) FROM sw_police.authorised_post WHERE post_status='vacant')<>500 THEN
    RAISE EXCEPTION 'recruit career opening must not consume a vacant substantive post';
  END IF;
END
$bp07$;
SELECT 'BP07 career history acceptance passed' AS result;
