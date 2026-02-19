-- Canonical schema for aerospike_health.db
-- Single source of truth. Ingestors and check_integrity must align.
-- DB is created from this file at ingest init; ingestors only INSERT.

-- Run-level key/value (metadata ingestor, ingest_manager)
CREATE TABLE IF NOT EXISTS cluster_metadata (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- System info per node (system_info_ingest_ci)
CREATE TABLE IF NOT EXISTS system_info (
    run_id TEXT,
    node_id TEXT,
    metric TEXT,
    value TEXT
);

-- Feature flags per node (features_ingest_ci)
CREATE TABLE IF NOT EXISTS active_features (
    run_id TEXT,
    node_id TEXT,
    feature TEXT
);

-- Config key/value per node (config_ingest_ci)
CREATE TABLE IF NOT EXISTS node_configs (
    run_id TEXT,
    node_id TEXT,
    config_name TEXT,
    value TEXT,
    source TEXT
);

-- Node-level stats, flattened (node_stats_ingest_ci)
CREATE TABLE IF NOT EXISTS node_stats (
    run_id TEXT,
    node_id TEXT,
    metric TEXT,
    value TEXT
);

-- Namespace-level stats (namespace_stats_ingest_ci)
CREATE TABLE IF NOT EXISTS namespace_stats (
    run_id TEXT,
    node_id TEXT,
    namespace TEXT,
    metric TEXT,
    value REAL,
    source TEXT
);

-- Set-level metrics (set_stats_ingest_ci)
CREATE TABLE IF NOT EXISTS set_stats (
    node_id TEXT,
    ns TEXT,
    set_name TEXT,
    key TEXT,
    value TEXT,
    run_id TEXT,
    PRIMARY KEY (node_id, ns, set_name, key, run_id)
);

-- ACL user connection counts (security_stats_ingest_ci)
CREATE TABLE IF NOT EXISTS security_stats (
    node_id TEXT,
    user TEXT,
    connections INTEGER,
    run_id TEXT,
    PRIMARY KEY (node_id, user, run_id)
);
