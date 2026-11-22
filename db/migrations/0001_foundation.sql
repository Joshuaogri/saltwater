-- Saltwater migration 0001: compact, auditable platform foundation.
-- No resident/case seed data is inserted by this migration.

BEGIN;

CREATE SCHEMA IF NOT EXISTS sw_core;
CREATE SCHEMA IF NOT EXISTS sw_ops;

CREATE TABLE IF NOT EXISTS sw_core.world_config (
    world_id smallint PRIMARY KEY CHECK (world_id = 1),
    country_name text NOT NULL CHECK (country_name = 'Saltwater'),
    city_name text NOT NULL CHECK (city_name = 'Saltwater'),
    sovereign_city_state boolean NOT NULL DEFAULT true CHECK (sovereign_city_state),
    living_population_limit integer NOT NULL DEFAULT 10000
        CHECK (living_population_limit = 10000),
    playable_city_count smallint NOT NULL DEFAULT 1 CHECK (playable_city_count = 1),
    created_at timestamptz NOT NULL DEFAULT now()
);

INSERT INTO sw_core.world_config
    (world_id, country_name, city_name, sovereign_city_state, living_population_limit, playable_city_count)
VALUES
    (1, 'Saltwater', 'Saltwater', true, 10000, 1)
ON CONFLICT (world_id) DO NOTHING;

CREATE TABLE IF NOT EXISTS sw_ops.schema_migration (
    version integer PRIMARY KEY,
    migration_name text NOT NULL UNIQUE,
    applied_at timestamptz NOT NULL DEFAULT now(),
    checksum_sha256 char(64)
);

CREATE TABLE IF NOT EXISTS sw_ops.storage_operation (
    operation_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    operation_kind text NOT NULL CHECK (
        operation_kind IN ('migration', 'seed_import', 'bulk_insert', 'file_upload', 'archive', 'restore', 'other')
    ),
    description text NOT NULL,
    status text NOT NULL CHECK (status IN ('planned', 'succeeded', 'failed', 'partial')),
    measured_at timestamptz,
    original_bytes bigint CHECK (original_bytes >= 0),
    compressed_bytes bigint CHECK (compressed_bytes >= 0),
    submitted_bytes bigint CHECK (submitted_bytes >= 0),
    database_bytes_before bigint CHECK (database_bytes_before >= 0),
    database_bytes_after bigint CHECK (database_bytes_after >= 0),
    net_database_bytes bigint,
    measurement_notes text,
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK (
        database_bytes_before IS NULL OR database_bytes_after IS NULL
        OR net_database_bytes = database_bytes_after - database_bytes_before
    )
);

CREATE INDEX IF NOT EXISTS storage_operation_created_idx
    ON sw_ops.storage_operation (created_at DESC);

CREATE TABLE IF NOT EXISTS sw_core.event_type (
    event_type_id smallint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_code text NOT NULL UNIQUE,
    description text NOT NULL
);

CREATE TABLE IF NOT EXISTS sw_core.simulation_event (
    event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_type_id smallint NOT NULL REFERENCES sw_core.event_type(event_type_id),
    occurred_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT now(),
    subject_kind text,
    subject_id integer,
    location_id integer,
    source_ref text,
    attributes jsonb NOT NULL DEFAULT '{}'::jsonb,
    CHECK (jsonb_typeof(attributes) = 'object')
);

CREATE INDEX IF NOT EXISTS simulation_event_time_idx
    ON sw_core.simulation_event (occurred_at DESC, event_id DESC);
CREATE INDEX IF NOT EXISTS simulation_event_subject_idx
    ON sw_core.simulation_event (subject_kind, subject_id, occurred_at DESC)
    WHERE subject_id IS NOT NULL;

INSERT INTO sw_ops.schema_migration (version, migration_name)
VALUES (1, 'foundation')
ON CONFLICT (version) DO NOTHING;

INSERT INTO sw_ops.storage_operation
    (operation_kind, description, status, measurement_notes)
VALUES
    ('migration', '0001 foundation schema; no simulation data inserted', 'succeeded',
     'Record actual before/after database size when this migration is applied. No Neon upload has been performed by repository creation.');

COMMIT;
