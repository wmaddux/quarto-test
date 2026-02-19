# Telemetry Version–Path Matrix

## Purpose

This document maps **collectinfo JSON paths** to **SQLite tables** for Aerospike 6.x, 7.x, and 8.x. Data quality for the Health Maturity Report depends on these paths; use this matrix to verify ingestion and to add or adjust ingestors.

---

## Collectinfo structure

- **Archive:** Collectinfo is a `.tgz` or `.tar` containing one or more JSON files (often inside `.zip` or `.gz`) and optionally `aerospike.conf`.
- **Telemetry JSON:** Top level = timestamp(s) → cluster name → node ID → **node payload**.
- **Node payload:** Two main blocks: `as_stat` (Aerospike stats/config) and `sys_stat` (system info). All paths below are relative to a single node’s payload (`node_data`).

---

## Bundle inspection summary (actual bundles)

Bundles under `ingest_samples/` were inspected with `inspect_collectinfo_bundles.py`. Summary:

| Version | Bundle (sample) | aerospike.conf | Node top-level keys | as_stat first-level keys |
|---------|------------------|----------------|---------------------|---------------------------|
| 6.x     | collect_info_v6x / yahoo-*.tgz | **Yes** | `as_stat`, `sys_stat` | `statistics`, `config`, `meta_data`, `histogram`, `latency`, `acl` |
| 7.x     | collect_info_v7x / adobe-*.tgz | No          | `as_stat`, `sys_stat` | `statistics`, `config`, `meta_data`, `histogram`, `latency`, `acl` |
| 8.x     | collect_info_v8x / swarit_*.tgz | **Yes** | `as_stat`, `sys_stat` | `statistics`, `config`, `meta_data`, `histogram`, `latency`, `acl` |

**Paths present in all three inspected bundles:**

- `as_stat`, `sys_stat`
- `as_stat.statistics`, `as_stat.config`, `as_stat.meta_data`, `as_stat.acl`
- `as_stat.statistics.namespace`, `as_stat.statistics.service`
- `as_stat.acl.users`

**Paths absent in these samples (may appear in other clusters):**

- `as_stat.namespaces` (6.x legacy path; this 6.x sample used `statistics.namespace` like 7.x)
- `as_stat.statistics.set` (set metrics; absent when cluster has no sets or structure differs)

Full inspection output: [ingest_samples/bundle_inspection_summary.json](../ingest_samples/bundle_inspection_summary.json).

---

## 1. cluster_metadata

| Version | Source path | SQLite table | Sample | Notes |
|---------|-------------|--------------|--------|-------|
| 6.x | `as_stat.meta_data.asd_build` or `as_stat.statistics.service.asd_build`; `as_stat.config.namespace`; `as_stat.statistics.xdr`; full `node_data` (platform heuristic) | cluster_metadata (key, value) | [node_payload_6x.json](samples/node_payload_6x.json) | Fallback: version from statistics.service if meta_data missing |
| 7.x | Same as above | Same | [node_payload_7x.json](samples/node_payload_7x.json) | Implemented |
| 8.x | Same as 7.x (verified in bundle) | Same | [node_payload_8x.json](samples/node_payload_8x.json) | Same structure as 7.x in inspected bundle |

---

## 2. namespace_stats

| Version | Source path | SQLite table | Sample | Notes |
|---------|-------------|--------------|--------|-------|
| 6.x | `as_stat.namespaces` or `as_stat.statistics.namespace` → per-ns: `ns_data.get('service', ns_data)` (recursively flattened) | namespace_stats (run_id, node_id, namespace, metric, value, source) | [node_payload_6x.json](samples/node_payload_6x.json) | Both paths supported; nested metrics (e.g. storage-engine.max-used-pct) flattened. **Canonical mapping:** 6.x keys `storage-engine.max-used-pct`, `high-water-disk-pct` → also written as `service.data_used_pct`; `high-water-memory-pct`, `memory_free_pct` (as 100−value) → `service.memory_used_pct`. |
| 7.x | `as_stat.statistics.namespace` → per-ns: `ns_data.get('service', ns_data)` (flattened) | Same | [node_payload_7x.json](samples/node_payload_7x.json) | Implemented; 7.x often has `data_used_pct` / `memory_used_pct` directly; same canonical names written for rules/chart. |
| 8.x | Same as 7.x (verified in bundle) | Same | [node_payload_8x.json](samples/node_payload_8x.json) | Same structure in inspected bundle |

**Canonical metrics (version-agnostic):** Rules and the report query `service.data_used_pct` (disk usage %) and `service.memory_used_pct` (memory usage %). The ingestor writes these whenever it sees a synonym: 6.x uses `storage-engine.max-used-pct`, `high-water-disk-pct`, `high-water-memory-pct`, `memory_free_pct`; 7.x/8.x may use `data_used_pct` / `memory_used_pct` directly. All are normalized into the canonical names above.

---

## 3. node_stats

| Version | Source path | SQLite table | Sample | Notes |
|---------|-------------|--------------|--------|-------|
| 6.x | `node_data` (full payload flattened to dot-notation keys) | node_stats (run_id, node_id, metric, value) | [node_payload_6x.json](samples/node_payload_6x.json) | No version-specific path; metric names may differ |
| 7.x | Same | Same | [node_payload_7x.json](samples/node_payload_7x.json) | Implemented |
| 8.x | Same | Same | [node_payload_8x.json](samples/node_payload_8x.json) | Same approach |

---

## 4. set_stats

| Version | Source path | SQLite table | Sample | Notes |
|---------|-------------|--------------|--------|-------|
| 6.x | `as_stat.statistics.set` (or legacy path TBD) → `{ns: {set_name: {key: value}}}` | set_stats (node_id, ns, set_name, key, value, run_id) | [node_payload_6x.json](samples/node_payload_6x.json) | statistics.set absent in inspected 6.x; may appear when sets exist |
| 7.x | `as_stat.statistics.set` → same shape | Same | [node_payload_7x.json](samples/node_payload_7x.json) | Implemented; set absent in inspected bundle |
| 8.x | Same as 7.x (assumed) | Same | [node_payload_8x.json](samples/node_payload_8x.json) | statistics.set absent in inspected bundle |

---

## 5. security_stats

| Version | Source path | SQLite table | Sample | Notes |
|---------|-------------|--------------|--------|-------|
| 6.x | `as_stat.acl.users` → per user `connections` | security_stats (node_id, user, connections, run_id) | [node_payload_6x.json](samples/node_payload_6x.json) | Present in inspected 6.x bundle |
| 7.x | Same | Same | [node_payload_7x.json](samples/node_payload_7x.json) | Implemented |
| 8.x | Same (verified in bundle) | Same | [node_payload_8x.json](samples/node_payload_8x.json) | Verified |

---

## 6. node_configs

| Version | Source path | SQLite table | Sample | Notes |
|---------|-------------|--------------|--------|-------|
| 6.x | `as_stat.config` or full `as_stat` (skip statistics, meta_data, histogram, latency at root) | node_configs (run_id, node_id, config_name, value, source) | [node_payload_6x.json](samples/node_payload_6x.json) | Fallback in code |
| 7.x | `as_stat.config` (fallback: as_stat) | Same | [node_payload_7x.json](samples/node_payload_7x.json) | Implemented |
| 8.x | Same as 7.x (verified) | Same | [node_payload_8x.json](samples/node_payload_8x.json) | Same structure |

---

## 7. active_features

| Version | Source path | SQLite table | Sample | Notes |
|---------|-------------|--------------|--------|-------|
| 6.x | `as_stat.statistics.service`, `as_stat.statistics.namespace`, `as_stat.config.security`, `as_stat.config.network`, `as_stat.config.namespace` (and nested ns service blocks) | active_features (run_id, node_id, feature) | [node_payload_6x.json](samples/node_payload_6x.json) | Same blocks present in 6.x bundle |
| 7.x | Same | Same | [node_payload_7x.json](samples/node_payload_7x.json) | Implemented |
| 8.x | Same as 7.x (verified) | Same | [node_payload_8x.json](samples/node_payload_8x.json) | Same structure |

---

## 8. system_info

| Version | Source path | SQLite table | Sample | Notes |
|---------|-------------|--------------|--------|-------|
| 6.x | `node_data.sys_stat` | system_info (run_id, node_id, metric, value) | [node_payload_6x.json](samples/node_payload_6x.json) | No version branching in code |
| 7.x | Same | Same | [node_payload_7x.json](samples/node_payload_7x.json) | Implemented |
| 8.x | Same | Same | [node_payload_8x.json](samples/node_payload_8x.json) | Same |

---

## aerospike.conf (future ingest)

| Version | In bundle | Typical path in archive |
|---------|-----------|--------------------------|
| 6.x | Yes (in inspected bundle) | `tmp/collect_info_<id>/<id>_aerospike.conf` |
| 7.x | No (in inspected bundle; bundle-dependent) | Same pattern when present |
| 8.x | Yes (in inspected bundle) | Same |

---

## Maintenance

- When adding an ingestor, add a row per version to the matrix.
- When verifying with new 6.x/7.x/8.x bundles, re-run `inspect_collectinfo_bundles.py` and update this doc and [ingest_samples/bundle_inspection_summary.json](../ingest_samples/bundle_inspection_summary.json).
- Sample payloads in `docs/samples/` can be minimal anonymized snippets extracted from the bundles in `ingest_samples/`.
