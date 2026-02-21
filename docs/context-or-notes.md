# Context & Session Notes

Use this file to resume work or bring a new chat up to speed. See also [MANIFEST.md](../MANIFEST.md) for scope, requirements, and backlog.

---

## Current State (as of last update)

- **Branch:** 2.0 | **Release:** 2.0.1
- **Schema:** Canonical schema in `schema/baseline.sql`; DB created from baseline at ingest init; ingestors only INSERT. `check_integrity.py` validates live DB against baseline before running rules. `static_configs` table added for aerospike.conf from bundle.
- **Docs:** [docs/schema.md](schema.md), [docs/telemetry-version-path-matrix.md](telemetry-version-path-matrix.md), [docs/testing.md](testing.md), [docs/report-issues.md](report-issues.md). Version-path matrix includes canonical metric mapping for 6.x/7.x namespace stats.
- **Namespace ingestor:** Flattens nested metrics and writes canonical `service.data_used_pct` / `service.memory_used_pct` from 6.x synonyms. Disk Usage % chart and HWM rules work across versions.
- **Setup:** `setup_venv.sh` creates `.venv` and installs pandas, plotly, jupyter, pyyaml. README updated (v2.0.1, directory structure, docs links, usage).
- **Naming:** Tool name chosen: **AeroScope**. Rename not yet applied across repo (still "Aerospike Health Analyzer" in titles). Report output still "Health Maturity Report."

### Recently completed (v2.0.1)

- **Index Location:** Fixed in metadata ingestor (`index_flavor` from config.namespace.*.service index-type/sindex-type; 6.x stats fallback). Cluster Context no longer shows "Unknown."
- **aerospike.conf:** Ingest from bundle in `ingest_manager.py` (find, parse, insert into `static_configs`). Config Drift rule (3.b) uses it when present.
- **Active Features:** Fixed cursor scope in `_setup.qmd`; features ingestor made 6.x-aware (key synonyms, namespaces fallback). Cluster Context shows detected features.
- **E2E/testing:** `tests/run_e2e.py` wrapper, `docs/testing.md`, `check_integrity.py --report` for rules output. Inspect script reports on all bundles under `ingest_samples/collect_info*`.

---

## Open / Next Steps

1. **Automated testing loop** — Evaluate the effectiveness of end to end testing. `tests/run_e2e.py`, `check_integrity.py`, and `check_integrity.py --report` support the loop without rendering the full report.

2. **Other report issues** — Review and fix any remaining clarity/accuracy issues in the report. See [Remaining report issues](#remaining-report-issues) below for the backlog (add items as needed).

3. **Optional later:** Project renaming to title: "Aerospike TAM Healthcheck Report". Repo: tam-health-report

### Remaining report issues

*(Add specific clarity/accuracy items in [report-issues.md](report-issues.md) and tackle one by one.)*

---

## Decisions

- Tool name: **tam-health-report** (for now; rename deferred).
- Report name: Keep "Health Maturity Report" for now.
- Index Location: Fixed in metadata ingestor (`index_flavor`).

---

*Update this file when completing items or when context would help the next session.*
