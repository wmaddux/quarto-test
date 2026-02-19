# Context & Session Notes

Use this file to resume work or bring a new chat up to speed. See also [MANIFEST.md](../MANIFEST.md) for scope, requirements, and backlog.

---

## Current State (as of last update)

- **Branch:** 2.0
- **Schema:** Canonical schema in `schema/baseline.sql`; DB created from baseline at ingest init; ingestors only INSERT. `check_integrity.py` validates live DB against baseline before running rules.
- **Docs:** [docs/schema.md](schema.md), [docs/telemetry-version-path-matrix.md](telemetry-version-path-matrix.md), version-path matrix includes canonical metric mapping for 6.x/7.x namespace stats.
- **Namespace ingestor:** Flattens nested metrics and writes canonical `service.data_used_pct` / `service.memory_used_pct` from 6.x synonyms (e.g. `storage-engine.max-used-pct`, `high-water-memory-pct`, `memory_free_pct`). Disk Usage % chart and HWM rules work across versions.
- **Setup:** `setup_venv.sh` creates `.venv` and installs pandas, plotly, jupyter, pyyaml. README updated (v2.0, directory structure, docs links, usage).
- **Naming:** Tool name chosen: **AeroScope**. Rename not yet applied across repo (still "Aerospike Health Analyzer" in titles). Report output still "Health Maturity Report."

---

## Open / Next Steps

1. **Index Location shows "Unknown" in Cluster Context**
   - Cause: `cluster_metadata` never has `index_flavor` (metadata ingestor doesn't set it). Fallback in `_setup.qmd` looks for a column `index-type` in `namespace_stats`, but that table is key/value (no such column).
   - Fix (choose one): **(A)** Add `index_flavor` to metadata ingestor from namespace config (`config.namespace.*.service['index-type']` → "Flash (All-Flash)" or "RAM (shmem)"). **(B)** In `_setup.qmd`, derive `idx_type` from `node_configs` (e.g. `config_name` LIKE `%index-type%`, `value` in ('flash','shmem')).

2. **Other report issues** — Review and fix any remaining clarity/accuracy issues in the report (user had a list).

3. **Optional later:** Apply AeroScope naming across repo (README, report title, MANIFEST, etc.).

---

## Decisions

- Tool name: **AeroScope** (for now; rename deferred).
- Report name: Keep "Health Maturity Report" for now.
- Index Location: To be fixed via ingestor or _setup (see above).

---

*Update this file when completing items or when context would help the next session.*
