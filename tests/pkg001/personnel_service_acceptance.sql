\set ON_ERROR_STOP on
DO $bp06$
DECLARE
  v_personnel bigint;
BEGIN
  SELECT count(*) INTO v_personnel FROM sw_police.personnel;
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
  IF (SELECT count(*) FROM sw_police.authorised_post WHERE post_status='filled')<>0 THEN
    RAISE EXCEPTION 'personnel appointment must not silently fill an authorised post';
  END IF;
END
$bp06$;
SELECT 'BP06 personnel service records acceptance passed' AS result;
