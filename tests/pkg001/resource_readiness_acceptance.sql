\set ON_ERROR_STOP on
DO $bp09$
BEGIN
  IF (SELECT count(*) FROM sw_police.resource_model)<>15
     OR (SELECT count(*) FROM sw_police.resource_asset)<>527
     OR (SELECT count(*) FROM sw_police.resource_allocation)<>500
     OR (SELECT count(*) FROM sw_police.resource_allocation_event)<>500 THEN
    RAISE EXCEPTION 'initial police resource catalogue, assets or allocations do not reconcile';
  END IF;
  IF (SELECT count(*) FROM sw_police.resource_asset WHERE resource_model_id IN
      ('SWPS-RM-PATROL-VEH','SWPS-RM-TRAFFIC-VEH','SWPS-RM-PORT-VEH','SWPS-RM-PUBLICORDER-VAN',
       'SWPS-RM-TACTICAL-VEH','SWPS-RM-SAFEGUARD-VEH','SWPS-RM-SEARCH-VEH','SWPS-RM-CUSTODY-VEH'))<>50 THEN
    RAISE EXCEPTION 'initial police fleet count incorrect';
  END IF;
  IF (SELECT count(*) FROM sw_police.resource_asset WHERE lifecycle_state='available')<>27
     OR (SELECT count(*) FROM sw_police.resource_asset WHERE lifecycle_state='allocated')<>500
     OR EXISTS(SELECT 1 FROM sw_police.resource_asset WHERE serviceability_state<>'serviceable') THEN
    RAISE EXCEPTION 'resource pool state or initial serviceability inconsistent';
  END IF;
  IF EXISTS(
    SELECT 1 FROM sw_police.resource_allocation r
    JOIN sw_police.resource_asset a USING(asset_id)
    WHERE r.status<>'active' OR a.lifecycle_state<>'allocated'
  ) THEN RAISE EXCEPTION 'active resource allocation and asset lifecycle disagree'; END IF;
  IF EXISTS(
    SELECT asset_id FROM sw_police.resource_allocation
    WHERE status='active' AND effective_to_tick IS NULL
    GROUP BY asset_id HAVING count(*)>1
  ) THEN RAISE EXCEPTION 'serialized resource allocated more than once'; END IF;
  IF (SELECT count(*) FROM sw_police.unit_resource_requirement)<>39
     OR (SELECT count(*) FROM sw_police.unit_resource_readiness)<>7
     OR (SELECT count(*) FROM sw_police.unit_resource_readiness WHERE resources_ready)<>7 THEN
    RAISE EXCEPTION 'dispatchable unit resource requirements are not fully satisfied';
  END IF;
  IF (SELECT count(*) FROM sw_police.unit_readiness WHERE resources_ready)<>7
     OR (SELECT count(*) FROM sw_police.unit_readiness WHERE dispatch_eligible)<>0
     OR (SELECT count(*) FROM sw_police.unit_readiness WHERE staffing_eligible)<>0 THEN
    RAISE EXCEPTION 'resource readiness must not override unavailable or unstaffed unit state';
  END IF;
  IF (SELECT count(*) FROM sw_police.unit_membership)<>0 THEN
    RAISE EXCEPTION 'resource baseline must not create unit personnel memberships';
  END IF;
  IF (SELECT count(*) FROM sw_police.authorised_post WHERE post_status='vacant')<>500 THEN
    RAISE EXCEPTION 'resource allocation must not fill personnel establishment posts';
  END IF;
END
$bp09$;
SELECT 'BP09 resource inventory and dispatch-readiness acceptance passed' AS result;
