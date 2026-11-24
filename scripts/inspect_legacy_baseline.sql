-- BP38-02 supplementary production baseline review.
-- Every statement is SELECT-only. The workflow also enforces
-- default_transaction_read_only=on for this target connection.

SELECT 'database' AS section,
       jsonb_build_object(
         'database', current_database(),
         'server_version', current_setting('server_version'),
         'database_bytes', pg_database_size(current_database()),
         'transaction_read_only', current_setting('transaction_read_only')
       ) AS details;

SELECT 'schemas_and_relations' AS section,
       jsonb_build_object(
         'schema', n.nspname,
         'relation', c.relname,
         'kind', c.relkind,
         'owner', pg_get_userbyid(c.relowner),
         'acl', c.relacl,
         'rls_enabled', c.relrowsecurity,
         'rls_forced', c.relforcerowsecurity
       ) AS details
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname IN ('sw_core', 'sw_ops')
  AND c.relkind IN ('r', 'p', 'S', 'v', 'm', 'f')
ORDER BY n.nspname, c.relname;

SELECT 'sequences' AS section,
       jsonb_build_object(
         'schema', schemaname,
         'sequence', sequencename,
         'data_type', data_type,
         'start_value', start_value,
         'min_value', min_value,
         'max_value', max_value,
         'increment_by', increment_by,
         'cycle', cycle,
         'cache_size', cache_size,
         'last_value', last_value
       ) AS details
FROM pg_sequences
WHERE schemaname IN ('sw_core', 'sw_ops')
ORDER BY schemaname, sequencename;

SELECT 'role_memberships' AS section,
       jsonb_build_object(
         'granted_role', granted.rolname,
         'member_role', member.rolname,
         'grantor', grantor.rolname,
         'admin_option', m.admin_option
       ) AS details
FROM pg_auth_members m
JOIN pg_roles granted ON granted.oid = m.roleid
JOIN pg_roles member ON member.oid = m.member
JOIN pg_roles grantor ON grantor.oid = m.grantor
ORDER BY granted.rolname, member.rolname;

SELECT 'extensions' AS section,
       jsonb_build_object(
         'name', e.extname,
         'version', e.extversion,
         'schema', n.nspname
       ) AS details
FROM pg_extension e
JOIN pg_namespace n ON n.oid = e.extnamespace
ORDER BY e.extname;

SELECT 'selected_database_settings' AS section,
       jsonb_build_object(
         'name', name,
         'setting', setting,
         'unit', unit,
         'source', source,
         'pending_restart', pending_restart
       ) AS details
FROM pg_settings
WHERE name IN (
  'TimeZone', 'search_path', 'default_transaction_read_only',
  'statement_timeout', 'lock_timeout', 'idle_in_transaction_session_timeout',
  'max_connections', 'shared_buffers', 'work_mem',
  'default_statistics_target', 'row_security'
)
ORDER BY name;

SELECT 'schema_migration_ledger' AS section,
       jsonb_build_object(
         'version', version,
         'migration_name', migration_name,
         'checksum_sha256', checksum_sha256,
         'schema_fingerprint_sha256', schema_fingerprint_sha256,
         'applied_at', applied_at
       ) AS details
FROM sw_ops.schema_migration
ORDER BY version;

SELECT 'storage_operation_history' AS section,
       jsonb_build_object(
         'operation_id', operation_id,
         'operation_type', operation_type,
         'status', status,
         'created_at', created_at
       ) AS details
FROM sw_ops.storage_operation
ORDER BY operation_id;
