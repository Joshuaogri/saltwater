-- SW-NAM-001 / SW-GEO-V1 stable identity-map disposable acceptance.
-- TEST FIXTURE ONLY: never run against Neon or any authoritative database.
-- Creates 100 geography identities/names without importing geometry or approving
-- the map for operational use. Generated spatial_id values are captured below.

BEGIN;

CREATE TEMP TABLE expected_geography_identity (
  source_id text PRIMARY KEY,
  entity_code text NOT NULL UNIQUE,
  entity_kind smallint NOT NULL,
  display_name text NOT NULL,
  parent_entity_code text NOT NULL,
  source_ref text NOT NULL
) ON COMMIT DROP;

INSERT INTO expected_geography_identity
  (source_id,entity_code,entity_kind,display_name,parent_entity_code,source_ref)
VALUES
('SW-D01','SW-D01',3,'Westgate','saltwater-city','SW-GEO-V1:district:SW-D01'),
('SW-D01-N1','SW-D01-N1',4,'Westgate Gardens','SW-D01','SW-GEO-V1:neighbourhood:SW-D01-N1'),
('SW-D01-N2','SW-D01-N2',4,'Foundry Quarter','SW-D01','SW-GEO-V1:neighbourhood:SW-D01-N2'),
('SW-D01-N3','SW-D01-N3',4,'Garden Ward','SW-D01','SW-GEO-V1:neighbourhood:SW-D01-N3'),
('SW-D02','SW-D02',3,'Northbank','saltwater-city','SW-GEO-V1:district:SW-D02'),
('SW-D02-N1','SW-D02-N1',4,'Northbank West','SW-D02','SW-GEO-V1:neighbourhood:SW-D02-N1'),
('SW-D02-N2','SW-D02-N2',4,'Northbank East','SW-D02','SW-GEO-V1:neighbourhood:SW-D02-N2'),
('SW-D02-N3','SW-D02-N3',4,'University Quarter','SW-D02','SW-GEO-V1:neighbourhood:SW-D02-N3'),
('SW-D03','SW-D03',3,'Civic Core','saltwater-city','SW-GEO-V1:district:SW-D03'),
('SW-D03-N1','SW-D03-N1',4,'Assembly Quarter','SW-D03','SW-GEO-V1:neighbourhood:SW-D03-N1'),
('SW-D03-N2','SW-D03-N2',4,'Civic Terrace','SW-D03','SW-GEO-V1:neighbourhood:SW-D03-N2'),
('SW-D03-N3','SW-D03-N3',4,'Museum Gardens','SW-D03','SW-GEO-V1:neighbourhood:SW-D03-N3'),
('SW-D04','SW-D04',3,'East Harbour','saltwater-city','SW-GEO-V1:district:SW-D04'),
('SW-D04-N1','SW-D04-N1',4,'Port Quarter','SW-D04','SW-GEO-V1:neighbourhood:SW-D04-N1'),
('SW-D04-N2','SW-D04-N2',4,'Customs Ward','SW-D04','SW-GEO-V1:neighbourhood:SW-D04-N2'),
('SW-D04-N3','SW-D04-N3',4,'Marina Point','SW-D04','SW-GEO-V1:neighbourhood:SW-D04-N3'),
('SW-D05','SW-D05',3,'Greenfields','saltwater-city','SW-GEO-V1:district:SW-D05'),
('SW-D05-N1','SW-D05-N1',4,'Parkside','SW-D05','SW-GEO-V1:neighbourhood:SW-D05-N1'),
('SW-D05-N2','SW-D05-N2',4,'Reservoir Ward','SW-D05','SW-GEO-V1:neighbourhood:SW-D05-N2'),
('SW-D05-N3','SW-D05-N3',4,'South Gardens','SW-D05','SW-GEO-V1:neighbourhood:SW-D05-N3'),
('SW-D06','SW-D06',3,'Southworks','saltwater-city','SW-GEO-V1:district:SW-D06'),
('SW-D06-N1','SW-D06-N1',4,'Industrial Park','SW-D06','SW-GEO-V1:neighbourhood:SW-D06-N1'),
('SW-D06-N2','SW-D06-N2',4,'Rail Yards','SW-D06','SW-GEO-V1:neighbourhood:SW-D06-N2'),
('SW-D06-N3','SW-D06-N3',4,'Canal End','SW-D06','SW-GEO-V1:neighbourhood:SW-D06-N3'),
('SW-D07','SW-D07',3,'Central Market','saltwater-city','SW-GEO-V1:district:SW-D07'),
('SW-D07-N1','SW-D07-N1',4,'Grand Market','SW-D07','SW-GEO-V1:neighbourhood:SW-D07-N1'),
('SW-D07-N2','SW-D07-N2',4,'Exchange Ward','SW-D07','SW-GEO-V1:neighbourhood:SW-D07-N2'),
('SW-D07-N3','SW-D07-N3',4,'Theatre Quarter','SW-D07','SW-GEO-V1:neighbourhood:SW-D07-N3'),
('SW-D08','SW-D08',3,'Old Quays','saltwater-city','SW-GEO-V1:district:SW-D08'),
('SW-D08-N1','SW-D08-N1',4,'Old Harbour','SW-D08','SW-GEO-V1:neighbourhood:SW-D08-N1'),
('SW-D08-N2','SW-D08-N2',4,'Ropewalk','SW-D08','SW-GEO-V1:neighbourhood:SW-D08-N2'),
('SW-D08-N3','SW-D08-N3',4,'Dockside','SW-D08','SW-GEO-V1:neighbourhood:SW-D08-N3'),
('SW-POI-001','SW-POI-001',10,'Saltwater Assembly Hall','saltwater-city','SW-GEO-V1:landmark:SW-POI-001'),
('SW-POI-002','SW-POI-002',10,'Government Square','saltwater-city','SW-GEO-V1:landmark:SW-POI-002'),
('SW-POI-003','SW-POI-003',10,'National Records and Courts','saltwater-city','SW-GEO-V1:landmark:SW-POI-003'),
('SW-POI-004','SW-POI-004',10,'Saltwater Central Police Headquarters','saltwater-city','SW-GEO-V1:landmark:SW-POI-004'),
('SW-POI-005','SW-POI-005',10,'Central General Hospital','saltwater-city','SW-GEO-V1:landmark:SW-POI-005'),
('SW-POI-006','SW-POI-006',10,'Northbank University','saltwater-city','SW-GEO-V1:landmark:SW-POI-006'),
('SW-POI-007','SW-POI-007',10,'Grand Market Exchange','saltwater-city','SW-GEO-V1:landmark:SW-POI-007'),
('SW-POI-008','SW-POI-008',10,'Theatre and Arts Hall','saltwater-city','SW-GEO-V1:landmark:SW-POI-008'),
('SW-POI-009','SW-POI-009',10,'Port Customs House','saltwater-city','SW-GEO-V1:landmark:SW-POI-009'),
('SW-POI-010','SW-POI-010',10,'Eastern Container Terminal','saltwater-city','SW-GEO-V1:landmark:SW-POI-010'),
('SW-POI-011','SW-POI-011',10,'Passenger Ferry Terminal','saltwater-city','SW-GEO-V1:landmark:SW-POI-011'),
('SW-POI-012','SW-POI-012',10,'Old Quays Maritime Museum','saltwater-city','SW-GEO-V1:landmark:SW-POI-012'),
('SW-POI-013','SW-POI-013',10,'Southworks Rail Freight Yard','saltwater-city','SW-GEO-V1:landmark:SW-POI-013'),
('SW-POI-014','SW-POI-014',10,'Canal Freight Basin','saltwater-city','SW-GEO-V1:landmark:SW-POI-014'),
('SW-POI-015','SW-POI-015',10,'Greenfields Reservoir','saltwater-city','SW-GEO-V1:landmark:SW-POI-015'),
('SW-POI-016','SW-POI-016',10,'Parkside Civic Park','saltwater-city','SW-GEO-V1:landmark:SW-POI-016'),
('SW-POI-017','SW-POI-017',10,'Westgate Interchange','saltwater-city','SW-GEO-V1:landmark:SW-POI-017'),
('SW-POI-018','SW-POI-018',10,'Northbank Transit Interchange','saltwater-city','SW-GEO-V1:landmark:SW-POI-018'),
('SW-RT-001','SW-RT-001',9,'Central Orbital Distributor','saltwater-city','SW-GEO-V1:route:SW-RT-001'),
('SW-RT-002','SW-RT-002',9,'Civic North-South Spine','saltwater-city','SW-GEO-V1:route:SW-RT-002'),
('SW-RT-003','SW-RT-003',9,'Central East-West Boulevard','saltwater-city','SW-GEO-V1:route:SW-RT-003'),
('SW-RT-004','SW-RT-004',9,'Eastern Port Emergency Access','saltwater-city','SW-GEO-V1:route:SW-RT-004'),
('SW-RT-005','SW-RT-005',9,'Westgate Emergency Connector','saltwater-city','SW-GEO-V1:route:SW-RT-005'),
('SW-TERR-001','SW-TERR-001',5,'Central-Western Ridge','saltwater-city','SW-GEO-V1:geo_zone:SW-TERR-001'),
('SW-WTR-001','SW-WTR-001',5,'Saltwater Principal Harbour','saltwater-city','SW-GEO-V1:geo_zone:SW-WTR-001'),
('SW-WTR-002','SW-WTR-002',5,'Southworks Freight Canal Basin','saltwater-city','SW-GEO-V1:geo_zone:SW-WTR-002'),
('SWR-B1','SWR-B1',7,'Harbour Bridge','saltwater-city','SW-GEO-V1:road:SWR-B1'),
('SWR-B2','SWR-B2',7,'Customs Bridge','saltwater-city','SW-GEO-V1:road:SWR-B2'),
('SWR-H01','SWR-H01',7,'South Coast Road','saltwater-city','SW-GEO-V1:road:SWR-H01'),
('SWR-H02','SWR-H02',7,'Garden Avenue','saltwater-city','SW-GEO-V1:road:SWR-H02'),
('SWR-H03','SWR-H03',7,'Reservoir Road','saltwater-city','SW-GEO-V1:road:SWR-H03'),
('SWR-H04','SWR-H04',7,'Parkway','saltwater-city','SW-GEO-V1:road:SWR-H04'),
('SWR-H05','SWR-H05',7,'Canal Road','saltwater-city','SW-GEO-V1:road:SWR-H05'),
('SWR-H06','SWR-H06',7,'Railway Avenue','saltwater-city','SW-GEO-V1:road:SWR-H06'),
('SWR-H07','SWR-H07',7,'Industrial Way','saltwater-city','SW-GEO-V1:road:SWR-H07'),
('SWR-H08','SWR-H08',7,'Southworks Boulevard','saltwater-city','SW-GEO-V1:road:SWR-H08'),
('SWR-H09','SWR-H09',7,'Market Cross','saltwater-city','SW-GEO-V1:road:SWR-H09'),
('SWR-H10','SWR-H10',7,'Central Boulevard','saltwater-city','SW-GEO-V1:road:SWR-H10'),
('SWR-H11','SWR-H11',7,'Civic Link','saltwater-city','SW-GEO-V1:road:SWR-H11'),
('SWR-H12','SWR-H12',7,'Northbank Road','saltwater-city','SW-GEO-V1:road:SWR-H12'),
('SWR-H13','SWR-H13',7,'University Avenue','saltwater-city','SW-GEO-V1:road:SWR-H13'),
('SWR-H14','SWR-H14',7,'Museum Road','saltwater-city','SW-GEO-V1:road:SWR-H14'),
('SWR-H15','SWR-H15',7,'Government Avenue','saltwater-city','SW-GEO-V1:road:SWR-H15'),
('SWR-H16','SWR-H16',7,'North Ridge Road','saltwater-city','SW-GEO-V1:road:SWR-H16'),
('SWR-H17','SWR-H17',7,'North Coast Road','saltwater-city','SW-GEO-V1:road:SWR-H17'),
('SWR-V01','SWR-V01',7,'West Coast Road','saltwater-city','SW-GEO-V1:road:SWR-V01'),
('SWR-V02','SWR-V02',7,'Beacon Avenue','saltwater-city','SW-GEO-V1:road:SWR-V02'),
('SWR-V03','SWR-V03',7,'Crown Street','saltwater-city','SW-GEO-V1:road:SWR-V03'),
('SWR-V04','SWR-V04',7,'Foundry Road','saltwater-city','SW-GEO-V1:road:SWR-V04'),
('SWR-V05','SWR-V05',7,'Westgate Avenue','saltwater-city','SW-GEO-V1:road:SWR-V05'),
('SWR-V06','SWR-V06',7,'Ridgeway Drive','saltwater-city','SW-GEO-V1:road:SWR-V06'),
('SWR-V07','SWR-V07',7,'University Road','saltwater-city','SW-GEO-V1:road:SWR-V07'),
('SWR-V08','SWR-V08',7,'Assembly Avenue','saltwater-city','SW-GEO-V1:road:SWR-V08'),
('SWR-V09','SWR-V09',7,'Civic Spine','saltwater-city','SW-GEO-V1:road:SWR-V09'),
('SWR-V10','SWR-V10',7,'Market Street','saltwater-city','SW-GEO-V1:road:SWR-V10'),
('SWR-V11','SWR-V11',7,'Exchange Avenue','saltwater-city','SW-GEO-V1:road:SWR-V11'),
('SWR-V12','SWR-V12',7,'Quays Road','saltwater-city','SW-GEO-V1:road:SWR-V12'),
('SWR-V13','SWR-V13',7,'Customs Avenue','saltwater-city','SW-GEO-V1:road:SWR-V13'),
('SWR-V14','SWR-V14',7,'Port Access Road','saltwater-city','SW-GEO-V1:road:SWR-V14'),
('SWR-V15','SWR-V15',7,'Marina Drive','saltwater-city','SW-GEO-V1:road:SWR-V15'),
('SWR-V16','SWR-V16',7,'Dock Street','saltwater-city','SW-GEO-V1:road:SWR-V16'),
('SWR-V17','SWR-V17',7,'Ropewalk Road','saltwater-city','SW-GEO-V1:road:SWR-V17'),
('SWR-V18','SWR-V18',7,'Harbour View Road','saltwater-city','SW-GEO-V1:road:SWR-V18'),
('SWR-V19','SWR-V19',7,'Eastbank Avenue','saltwater-city','SW-GEO-V1:road:SWR-V19'),
('SWR-V20','SWR-V20',7,'Seafarers Way','saltwater-city','SW-GEO-V1:road:SWR-V20'),
('SWR-V21','SWR-V21',7,'Breakwater Road','saltwater-city','SW-GEO-V1:road:SWR-V21'),
('SWR-V22','SWR-V22',7,'Coastline Drive','saltwater-city','SW-GEO-V1:road:SWR-V22'),
('SWR-V23','SWR-V23',7,'Eastern Promenade','saltwater-city','SW-GEO-V1:road:SWR-V23');

DO $$
BEGIN
  IF current_database() <> 'saltwater_test' THEN
    RAISE EXCEPTION 'geography identity-map fixture is restricted to saltwater_test';
  END IF;
  IF current_setting('server_version_num')::integer < 160000
     OR current_setting('server_version_num')::integer >= 170000 THEN
    RAISE EXCEPTION 'geography identity-map fixture requires disposable PostgreSQL 16';
  END IF;
  IF (SELECT count(*) FROM expected_geography_identity) <> 100 THEN
    RAISE EXCEPTION 'identity map must contain exactly 100 non-root records';
  END IF;
  IF EXISTS (
    SELECT 1 FROM expected_geography_identity m
    LEFT JOIN sw_geo.entity p ON p.entity_code=m.parent_entity_code
    LEFT JOIN expected_geography_identity local_parent
      ON local_parent.entity_code=m.parent_entity_code
    WHERE p.spatial_id IS NULL AND local_parent.entity_code IS NULL
  ) THEN
    RAISE EXCEPTION 'one or more identity-map parent codes do not resolve';
  END IF;
END
$$;

SELECT pg_database_size(current_database()) AS map_before_bytes \gset

INSERT INTO sw_geo.entity(entity_code,kind)
SELECT entity_code,entity_kind
FROM expected_geography_identity
ORDER BY entity_code
ON CONFLICT (entity_code) DO NOTHING;

DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM expected_geography_identity m
    JOIN sw_geo.entity e USING(entity_code)
    WHERE e.kind <> m.entity_kind
  ) THEN
    RAISE EXCEPTION 'existing spatial entity kind conflicts with identity map';
  END IF;
END
$$;

INSERT INTO sw_geo.version
  (spatial_id,version_no,effective_from_tick,parent_id,name,active,source_ref,reason_code)
SELECT e.spatial_id,1,0,p.spatial_id,m.display_name,true,m.source_ref,1
FROM expected_geography_identity m
JOIN sw_geo.entity e ON e.entity_code=m.entity_code
JOIN sw_geo.entity p ON p.entity_code=m.parent_entity_code
ORDER BY e.spatial_id
ON CONFLICT (spatial_id,version_no) DO NOTHING;

DO $$
BEGIN
  IF (SELECT count(*) FROM expected_geography_identity m
      JOIN sw_geo.entity e ON e.entity_code=m.entity_code
      JOIN sw_geo.version v ON v.spatial_id=e.spatial_id AND v.version_no=1
      WHERE v.name=m.display_name AND v.parent_id=(
        SELECT p.spatial_id FROM sw_geo.entity p
        WHERE p.entity_code=m.parent_entity_code
      )) <> 100 THEN
    RAISE EXCEPTION 'materialised spatial identity/version/parent mapping is incomplete';
  END IF;

  IF (SELECT count(*) FROM expected_geography_identity m
      JOIN sw_geo.entity e ON e.entity_code=m.entity_code
      JOIN sw_names.registry r ON r.entity_type='GEOGRAPHY'
        AND r.entity_id=e.spatial_id AND r.display_name=m.display_name
        AND r.name_form='canonical' AND r.status='active') <> 100 THEN
    RAISE EXCEPTION 'naming registry did not activate all 100 geography names';
  END IF;

  IF (SELECT count(*) FROM sw_names.search_name('Saltwater')) <> 2
     OR NOT (SELECT bool_and(ambiguous) FROM sw_names.search_name('Saltwater')) THEN
    RAISE EXCEPTION 'approved Saltwater root pair must remain explicitly ambiguous';
  END IF;
END
$$;

SELECT
  pg_database_size(current_database()) AS map_after_bytes,
  (pg_database_size(current_database()) - :map_before_bytes::bigint) AS map_delta_bytes,
  pg_total_relation_size('sw_geo.entity'::regclass) AS geography_entity_total_bytes,
  pg_total_relation_size('sw_geo.version'::regclass) AS geography_version_total_bytes,
  pg_total_relation_size('sw_names.name_reservation'::regclass) AS name_reservation_total_bytes,
  pg_total_relation_size('sw_names.name_event'::regclass) AS name_event_total_bytes
\gset

\echo SW_GEO_IDENTITY_MAP_DATABASE_BEFORE_BYTES=:map_before_bytes
\echo SW_GEO_IDENTITY_MAP_DATABASE_AFTER_BYTES=:map_after_bytes
\echo SW_GEO_IDENTITY_MAP_DATABASE_DELTA_BYTES=:map_delta_bytes
\echo SW_GEO_IDENTITY_MAP_ENTITY_RELATION_BYTES=:geography_entity_total_bytes
\echo SW_GEO_IDENTITY_MAP_VERSION_RELATION_BYTES=:geography_version_total_bytes
\echo SW_GEO_IDENTITY_MAP_NAME_RESERVATION_RELATION_BYTES=:name_reservation_total_bytes
\echo SW_GEO_IDENTITY_MAP_NAME_EVENT_RELATION_BYTES=:name_event_total_bytes

SELECT m.source_id,m.entity_code,e.spatial_id,m.entity_kind,m.display_name,
       m.parent_entity_code,p.spatial_id AS parent_spatial_id
FROM expected_geography_identity m
JOIN sw_geo.entity e ON e.entity_code=m.entity_code
JOIN sw_geo.entity p ON p.entity_code=m.parent_entity_code
ORDER BY m.source_id;

COMMIT;
