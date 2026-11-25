-- BP04-03: allow point-contact/nearest road-reserve connection candidates.
-- Disposable schema extension; does not create or approve operational access.
BEGIN;

ALTER TABLE sw_geo.parcel_access_location_candidate
  ALTER COLUMN frontage_candidate_id DROP NOT NULL,
  ADD COLUMN road_connection_candidate_id text,
  ADD COLUMN road_id text,
  ADD COLUMN road_segment_ids text[] NOT NULL DEFAULT ARRAY[]::text[],
  ADD COLUMN contact_type text,
  ADD COLUMN distance_to_road_reserve_m numeric(14,6),
  ADD COLUMN parcel_boundary_x_m numeric(14,6),
  ADD COLUMN parcel_boundary_y_m numeric(14,6);

ALTER TABLE sw_geo.parcel_access_location_candidate
  DROP CONSTRAINT parcel_access_location_candidate_candidate_type_check,
  DROP CONSTRAINT parcel_access_location_candidate_review_status_check,
  ADD CONSTRAINT parcel_access_candidate_type_check
    CHECK (candidate_type IN ('unclassified_access_location','road_reserve_proximity_connection')),
  ADD CONSTRAINT parcel_access_candidate_review_status_check
    CHECK (review_status IN ('UNREVIEWED_GEOMETRIC_CANDIDATE','UNREVIEWED_ROAD_RESERVE_PROXIMITY_CANDIDATE')),
  ADD CONSTRAINT parcel_access_candidate_connection_shape_check
    CHECK (
      (candidate_type='unclassified_access_location'
       AND frontage_candidate_id IS NOT NULL
       AND road_connection_candidate_id IS NULL
       AND contact_type IS NULL
       AND distance_to_road_reserve_m IS NULL
       AND parcel_boundary_x_m IS NULL
       AND parcel_boundary_y_m IS NULL)
      OR
      (candidate_type='road_reserve_proximity_connection'
       AND frontage_candidate_id IS NULL
       AND road_connection_candidate_id IS NOT NULL
       AND length(btrim(road_connection_candidate_id)) BETWEEN 1 AND 180
       AND road_id IS NOT NULL
       AND length(btrim(road_id)) BETWEEN 1 AND 120
       AND cardinality(road_segment_ids)=1
       AND contact_type IN ('POINT_CONTACT_ONLY','NEAREST_EDGE_PROXIMITY_NOT_FRONTAGE')
       AND distance_to_road_reserve_m >= 0
       AND parcel_boundary_x_m IS NOT NULL
       AND parcel_boundary_y_m IS NOT NULL)
    ),
  ADD CONSTRAINT parcel_access_candidate_road_connection_id_key
    UNIQUE (road_connection_candidate_id);

COMMENT ON COLUMN sw_geo.parcel_access_location_candidate.road_connection_candidate_id
  IS 'Stable non-operational candidate identity for a nearest road-reserve connection; not a driveway or access right.';
COMMENT ON COLUMN sw_geo.parcel_access_location_candidate.contact_type
  IS 'Geometric relationship only: point contact or nearest-edge proximity, never proof of legal frontage.';

COMMIT;
