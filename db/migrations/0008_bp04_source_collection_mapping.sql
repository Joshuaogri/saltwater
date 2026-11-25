-- BP04 phase 6: complete source inventory, archive-first package accounting and collection mapping status.
-- Production migration candidate; validate on disposable PostgreSQL before production application.
BEGIN;
ALTER TABLE sw_property.import_dataset
  DROP CONSTRAINT IF EXISTS import_dataset_check;
ALTER TABLE sw_property.import_dataset
  ADD COLUMN IF NOT EXISTS mapping_status text NOT NULL DEFAULT 'fully_mapped'
    CHECK (mapping_status IN ('fully_mapped','partially_mapped','archive_only'));
ALTER TABLE sw_property.import_dataset
  ADD CONSTRAINT import_dataset_loaded_lte_source
  CHECK (loaded_record_count <= source_record_count);
CREATE TABLE sw_property.source_dataset_collection (
  release_id text NOT NULL,
  dataset_id text NOT NULL,
  collection_name text NOT NULL,
  source_record_count bigint NOT NULL CHECK (source_record_count >= 0),
  loaded_record_count bigint NOT NULL CHECK (loaded_record_count >= 0),
  mapping_status text NOT NULL CHECK (mapping_status IN ('mapped','archive_only')),
  PRIMARY KEY (release_id,dataset_id,collection_name),
  FOREIGN KEY (release_id,dataset_id)
    REFERENCES sw_property.import_dataset(release_id,dataset_id) ON DELETE CASCADE,
  CHECK (loaded_record_count <= source_record_count),
  CHECK ((mapping_status='mapped' AND loaded_record_count=source_record_count)
      OR (mapping_status='archive_only' AND loaded_record_count=0))
);
CREATE INDEX source_dataset_collection_status_idx
  ON sw_property.source_dataset_collection(mapping_status,dataset_id);
COMMIT;
