-- BP04-01 disposable-only parcel/address references.
-- These synthetic identities are test fixtures, not operational geography.
BEGIN;
DO $$
BEGIN
  IF current_database()<>'saltwater_test' THEN
    RAISE EXCEPTION 'BP04-01 geography fixture is restricted to saltwater_test';
  END IF;
END
$$;
INSERT INTO sw_geo.entity(entity_code,kind)
VALUES ('bp04-test-parcel-0001',6),('bp04-test-address-0001',11)
ON CONFLICT (entity_code) DO NOTHING;
INSERT INTO sw_geo.version(spatial_id,version_no,effective_from_tick,name,source_ref,reason_code)
SELECT spatial_id,1,0,name,source_ref,1
FROM (VALUES
 ('bp04-test-parcel-0001','BP04 Test Parcel One','bp04-test-parcel-0001'),
 ('bp04-test-address-0001','BP04 Test Address One','bp04-test-address-0001')
) v(code,name,source_ref)
JOIN sw_geo.entity e ON e.entity_code=v.code
WHERE NOT EXISTS (SELECT 1 FROM sw_geo.version x WHERE x.spatial_id=e.spatial_id);
COMMIT;
