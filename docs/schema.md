# SQLite schema (aerospike_health.db)

The canonical schema is defined in **[schema/baseline.sql](../schema/baseline.sql)**. All ingestors write only to these tables; rules read only from them. For the JSON path → table mapping per Aerospike version, see the [Telemetry Version–Path Matrix](telemetry-version-path-matrix.md).

---

## Tables

### cluster_metadata

Run-level key/value (flavor, version, platform, consistency, storage, topology). Written by the metadata ingestor and ingest_manager (e.g. cluster_name).

| Column | Type | Meaning |
|--------|------|---------|
| key | TEXT | Key name (e.g. server_version, cloud_platform, cluster_name). |
| value | TEXT | Value. |

**Primary key:** `key`.

**Source paths:** See [Version–Path Matrix § cluster_metadata](telemetry-version-path-matrix.md#1-cluster_metadata). Ingest tagging (e.g. run_id, bundle_hash) will be stored here or in a future `ingest_runs` table.

---

### system_info

System/infrastructure info per node (e.g. instance-type, OS). One row per (run_id, node_id, metric).

| Column | Type | Meaning |
|--------|------|---------|
| run_id | TEXT | Ingest run identifier. |
| node_id | TEXT | Node address (e.g. host:port). |
| metric | TEXT | Metric name. |
| value | TEXT | Value (often string). |

**Source paths:** [Version–Path Matrix § system_info](telemetry-version-path-matrix.md#8-system_info) — `node_data.sys_stat`.

---

### active_features

Discovered feature flags per node (KVS, Batch, UDF, Security, TLS, etc.). One row per (run_id, node_id, feature).

| Column | Type | Meaning |
|--------|------|---------|
| run_id | TEXT | Ingest run identifier. |
| node_id | TEXT | Node address. |
| feature | TEXT | Feature name. |

**Source paths:** [Version–Path Matrix § active_features](telemetry-version-path-matrix.md#7-active_features).

---

### node_configs

Configuration key/value per node (flattened from collectinfo config block). Used by config_drift and config_symmetry rules.

| Column | Type | Meaning |
|--------|------|---------|
| run_id | TEXT | Ingest run identifier. |
| node_id | TEXT | Node address. |
| config_name | TEXT | Dot-notated config key (e.g. service.proto-fd-max). |
| value | TEXT | Value. |
| source | TEXT | Origin (e.g. config). |

**Source paths:** [Version–Path Matrix § node_configs](telemetry-version-path-matrix.md#6-node_configs).

---

### static_configs

Static aerospike.conf key/value per node (parsed from the collectinfo bundle file). Used by the Config Drift rule (3.b) to compare live running config (`node_configs`) with the on-disk config file.

| Column | Type | Meaning |
|--------|------|---------|
| run_id | TEXT | Ingest run identifier. |
| node_id | TEXT | Node address (same as in node_configs for JOIN). |
| config_name | TEXT | Dot-notated config key (must match node_configs keys for drift comparison). |
| value | TEXT | Value from the .conf file. |

**Source:** The aerospike.conf file inside the collectinfo tarball is located by name, parsed by `ingest_manager.parse_aerospike_conf()`, and inserted once per node so each node has the same static keys for JOIN. If no aerospike.conf member is found in the bundle, this table is empty and the Config Drift rule reports DATA MISSING.

---

### node_stats

Node-level statistics (flattened to dot-notated metric keys). Used by version_consistency, error_skew, and related rules.

| Column | Type | Meaning |
|--------|------|---------|
| run_id | TEXT | Ingest run identifier. |
| node_id | TEXT | Node address. |
| metric | TEXT | Dot-notated metric (e.g. as_stat.statistics.service.build). |
| value | TEXT | Value (rules cast to REAL where needed). |

**Source paths:** [Version–Path Matrix § node_stats](telemetry-version-path-matrix.md#3-node_stats) — full node_data flattened.

---

### namespace_stats

Namespace-level metrics (e.g. memory, objects, HWM). Used by HWM, capacity, read/delete not found, hot key rules.

| Column | Type | Meaning |
|--------|------|---------|
| run_id | TEXT | Ingest run identifier. |
| node_id | TEXT | Node address. |
| namespace | TEXT | Namespace name. |
| metric | TEXT | Metric name (e.g. service.memory_used_bytes). |
| value | REAL | Numeric value. |
| source | TEXT | Origin (e.g. statistics). |

**Source paths:** [Version–Path Matrix § namespace_stats](telemetry-version-path-matrix.md#2-namespace_stats).

---

### set_stats

Set-level metrics per namespace/set. Used by set_object_skew and similar rules.

| Column | Type | Meaning |
|--------|------|---------|
| node_id | TEXT | Node address. |
| ns | TEXT | Namespace name. |
| set_name | TEXT | Set name. |
| key | TEXT | Metric key. |
| value | TEXT | Value. |
| run_id | TEXT | Ingest run identifier. |

**Primary key:** (node_id, ns, set_name, key, run_id).

**Source paths:** [Version–Path Matrix § set_stats](telemetry-version-path-matrix.md#4-set_stats).

---

### security_stats

ACL user connection counts per node. Used by security_connection_audit rule.

| Column | Type | Meaning |
|--------|------|---------|
| node_id | TEXT | Node address. |
| user | TEXT | User name. |
| connections | INTEGER | Connection count. |
| run_id | TEXT | Ingest run identifier. |

**Primary key:** (node_id, user, run_id).

**Source paths:** [Version–Path Matrix § security_stats](telemetry-version-path-matrix.md#5-security_stats).

---

## Maintenance

- When adding a table or column, update **schema/baseline.sql** first, then **docs/schema.md** and the Version–Path Matrix so the three stay in sync.
- Ingestors must not define their own DDL; the DB is created from baseline at ingest init.
