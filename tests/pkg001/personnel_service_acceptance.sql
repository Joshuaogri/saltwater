\set ON_ERROR_STOP on
BEGIN;
UPDATE sw_runtime.state SET state=2,player_present=true WHERE singleton=1;
DO $bp06$
DECLARE
  v_personnel bigint;
  v_appointment uuid;
  v_person_id integer;
  v_population_before integer;
BEGIN
  SELECT count(*) INTO v_personnel FROM sw_police.personnel;
  IF (SELECT active_police_service_members FROM sw_people.population_summary)<>v_personnel THEN
    RAISE EXCEPTION 'BP06 appointments must automatically qualify their canonical people as active police-service members';
  END IF;
  IF EXISTS(
    SELECT 1 FROM sw_police.personnel p
    JOIN sw_people.population_state pop ON pop.person_id=p.person_id
    WHERE NOT pop.active_police_service OR pop.life_status<>1 OR pop.scope_status<>1
  ) THEN
    RAISE EXCEPTION 'BP06 personnel and BP03 population qualification are not synchronised';
  END IF;
  IF (SELECT count(*) FROM sw_police.personnel_service_engagement)<>v_personnel THEN
    RAISE EXCEPTION 'each personnel dossier must have exactly one initial service engagement';
  END IF;
  IF (SELECT count(*) FROM sw_police.personnel_service_event WHERE event_kind='appointed')<>v_personnel THEN
    RAISE EXCEPTION 'each personnel appointment must have one append-only appointment event';
  END IF;
  IF (SELECT count(*) FROM sw_police.service_number_history WHERE event_kind='issued')<>v_personnel THEN
    RAISE EXCEPTION 'each personnel service number must have one immutable issue event';
  END IF;
  IF (SELECT count(*) FROM sw_police.personnel_supervision_link WHERE relationship_type='recruit_supervisor' AND effective_to_tick IS NULL)
     <>
     (SELECT count(*) FROM sw_police.personnel WHERE service_standing='recruit') THEN
    RAISE EXCEPTION 'each recruit must have one active authorised supervisor relationship';
  END IF;
  IF EXISTS(
    SELECT 1 FROM sw_police.personnel p
    LEFT JOIN sw_police.personnel_service_engagement e ON e.personnel_id=p.personnel_id AND e.is_primary
    LEFT JOIN sw_people.population_state pop ON pop.person_id=p.person_id
    LEFT JOIN sw_police.service_number_history n ON n.personnel_id=p.personnel_id AND n.service_number=p.service_number
    LEFT JOIN sw_police.personnel_supervision_link s ON s.supervisee_personnel_id=p.personnel_id
       AND s.relationship_type='recruit_supervisor' AND s.effective_to_tick IS NULL
    WHERE e.appointment_id IS NULL OR e.service_state<>'active'
       OR e.personnel_category<>'sworn_officer' OR pop.person_id IS NULL
       OR pop.life_status<>1 OR pop.scope_status<>1 OR n.service_number IS NULL
       OR (p.service_standing='recruit' AND s.supervisee_personnel_id IS NULL)
  ) THEN RAISE EXCEPTION 'personnel service dossier, person population or supervisor linkage is inconsistent'; END IF;
  IF EXISTS(
    SELECT 1 FROM sw_police.personnel p
    JOIN sw_police.personnel_service_engagement e ON e.personnel_id=p.personnel_id
    WHERE p.service_standing='recruit' AND e.service_state<>'active'
  ) THEN RAISE EXCEPTION 'recruit service standing and active service state must remain distinct but consistent'; END IF;
  -- Police service is an overlapping population qualification. Non-terminal
  -- leave/suspension/secondment states remain countable; terminal separation
  -- removes only the police qualification and preserves the canonical person.
  SELECT e.appointment_id,p.person_id INTO STRICT v_appointment,v_person_id
    FROM sw_police.personnel_service_engagement e
    JOIN sw_police.personnel p USING(personnel_id)
    ORDER BY p.service_number LIMIT 1;
    SELECT living_included INTO v_population_before FROM sw_people.population_counter WHERE singleton=1;

    PERFORM sw_police.transition_personnel_service_engagement(
      v_appointment,'leave','BP06-LIFECYCLE-TEST:LEAVE','bp06-ci','temporary leave');
    IF NOT (SELECT active_police_service FROM sw_people.population_state WHERE person_id=v_person_id)
       OR (SELECT living_included FROM sw_people.population_counter WHERE singleton=1)<>v_population_before THEN
      RAISE EXCEPTION 'leave must preserve police membership and the single-person population count';
    END IF;

    PERFORM sw_police.transition_personnel_service_engagement(
      v_appointment,'suspended','BP06-LIFECYCLE-TEST:SUSPEND','bp06-ci','suspension pending review');
    IF NOT (SELECT active_police_service FROM sw_people.population_state WHERE person_id=v_person_id) THEN
      RAISE EXCEPTION 'suspension must preserve police service membership';
    END IF;

    PERFORM sw_police.transition_personnel_service_engagement(
      v_appointment,'separated','BP06-LIFECYCLE-TEST:SEPARATE','bp06-ci','service ended');
    IF (SELECT active_police_service FROM sw_people.population_state WHERE person_id=v_person_id)
       OR (SELECT living_included FROM sw_people.population_counter WHERE singleton=1)<>v_population_before-1
       OR (SELECT life_status FROM sw_people.population_state WHERE person_id=v_person_id)<>1 THEN
      RAISE EXCEPTION 'separation must remove only police qualification while preserving living identity';
    END IF;
    IF sw_police.transition_personnel_service_engagement(
      v_appointment,'separated','BP06-LIFECYCLE-TEST:SEPARATE','bp06-ci','idempotent replay')
       <>v_population_before-1 THEN
      RAISE EXCEPTION 'service transition replay changed population count';
    END IF;
  IF (SELECT count(*) FROM sw_police.personnel_service_event
      WHERE source_ref LIKE 'BP06-LIFECYCLE-TEST:%')<>3 THEN
    RAISE EXCEPTION 'service lifecycle must retain exactly three immutable transition events';
  END IF;

  IF (SELECT count(*) FROM sw_police.authorised_post WHERE post_status='filled')<>0 THEN
    RAISE EXCEPTION 'personnel appointment must not silently fill an authorised post';
  END IF;
END
$bp06$;
SELECT 'BP06 personnel service records acceptance passed' AS result;
ROLLBACK;
