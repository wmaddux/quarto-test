# Health Maturity Report — Project Manifest

**Current baseline:** 2.0 (branch) | **Release:** 2.0.1 | **Focus:** Data ingestion quality, schema standardization, and requirements alignment.

---

## 1. Core Mission & Design Principles

- **Mission:** Generate a Health Maturity Report that effectively diagnoses cluster health, explains underlying behaviors and causes, and provides actionable remediation guidance.
- **Non-developer extensibility:** Both the SQL data model and the test rules must be easy for TAMs and architects to review, maintain, and extend.
- **Data integrity:** The quality of the health report depends directly on the completeness and standardization of the underlying SQL database.
- **Multi-source ingestion:** Ingest data from collectinfo (JSON), aerospike.log, and aerospike.conf.

---

## 2. Component Inventory

### Templates & standards

- **INGEST-TEMPLATE.md** — Blueprint for all ingest modules; each logical data set (stats, logs, config) is handled by a single, dedicated Python file.
- **RULE-TEMPLATE.md** — Blueprint for health test rules; each test is a standalone Python file.
- **Version–path matrix:** [docs/telemetry-version-path-matrix.md](docs/telemetry-version-path-matrix.md) — Maps collectinfo JSON paths to SQLite tables for 6.x, 7.x, and 8.x.
- **Canonical schema:** [schema/baseline.sql](schema/baseline.sql) (DDL), [docs/schema.md](docs/schema.md) (documentation).

### Orchestration & tools

- **run_ingest.py** — CLI entry for ingestion.
- **ingest_manager.py** — Tarball extraction and coordinate-based ingestion; invokes ingest modules per node.
- **check_integrity.py** — Validates that rules can run against the DB (and, when implemented, schema vs baseline).
- **set_version.py** / **commit_baseline.py** — Global version sync and Git deployment.

### Ingest modules (ingest/)

| Module | Table(s) |
|--------|----------|
| metadata_ingestor_ci.py | cluster_metadata |
| system_info_ingest_ci.py | system_info |
| features_ingest_ci.py | active_features |
| config_ingest_ci.py | node_configs |
| node_stats_ingest_ci.py | node_stats |
| namespace_stats_ingest_ci.py | namespace_stats |
| set_stats_ingest_ci.py | set_stats |
| security_stats_ingest_ci.py | security_stats |

*Optional (not in default pipeline):* platform_ingestor_ci.py writes `cloud_platform` to cluster_metadata.

**Static config:** When the collectinfo bundle includes **aerospike.conf**, `ingest_manager.py` locates it in the tarball, parses it, and inserts into **static_configs** (see [schema/baseline.sql](schema/baseline.sql), [docs/schema.md](docs/schema.md)). The Config Drift rule (3.b) compares `node_configs` (live) to `static_configs` (file). If the file is missing from the bundle, the rule reports DATA MISSING.

**Planned:** log_ingestor.py (aerospike.log).

### Rules (rules/)

17+ rules spanning error skew, storage (HWM, deadlocks), config drift/symmetry, traffic patterns, version consistency, security connection audit, capacity forecasting, and related checks. See [rules/](rules/) and [RULE-TEMPLATE.md](RULE-TEMPLATE.md).

### Report (report_components/)

- _assessment_header.qmd, _executive_summary.qmd, _status_overview.qmd, _performance_utilization.qmd, _observations_remediation.qmd, _cluster_context.qmd, _appendix_all_tests.qmd.

---

## 3. Data Strategy

- **Primary telemetry:** Collectinfo JSON; hierarchical data is flattened and, where needed, 7.x/8.x “wide” structures are normalized into standard columns for simpler SQL and version-agnostic rules.
- **Expansion:** Add ingestion from aerospike.log and aerospike.conf; config from file is required in the bundle (see Requirements).

---

## 4. Technical State

- **Stack:** Python 3.10–3.13, SQLite, Quarto (Markdown/HTML), Plotly.
- **Architecture:** Modular; report.qmd and _setup.qmd drive data loading and rule execution; report_components are included as partials.

---

## 5. Requirements (explicit)

1. **Fixed SQLite schema**  
   The canonical schema is defined in **schema/baseline.sql** and documented in **docs/schema.md**. All ingestors and `check_integrity` align to it; the DB is created from the baseline at ingest init (ingestors only INSERT). Downstream rules depend only on this schema. `check_integrity` validates the live DB schema against the baseline before running rules.

2. **aerospike.conf in bundle**  
   aerospike.conf should be included in the collectinfo bundle by default. If the file is in a non-default location, the asadm command must explicitly request that path; permissions may be required to access it. **If aerospike.conf is missing, ingestion proceeds**; the Config Drift rule (3.b) reports DATA MISSING. Operators should be instructed to include it (and, if needed, path and permissions) for full drift checking. Document how to request path and permissions for asadm.

3. **Ingest tagging**  
   Ingested data must be tagged with an identifier (e.g. `run_id` and/or bundle content hash) so that: (a) runs can be compared to future ingest, and (b) duplicate ingest can be detected or avoided. Store the tag in the DB (e.g. in `cluster_metadata` or a dedicated `ingest_runs` table).

---

## 6. Backlog / Next Steps

- **Ingest process:** Standardize SQLite schema for 6.x, 7.x, 8.x; add schema baseline and validation; add ingest tagging (run_id / bundle hash). (aerospike.conf: ingest proceeds when missing; Config Drift reports DATA MISSING.)
- **Log & config ingestion:** First iterations of aerospike.log and aerospike.conf parsers.
- **UI:** Refine Plotly legends and multi-node presentation (e.g. _performance_utilization.qmd).
- **Capacity forecasting:** Finalize “days-to-HWM” logic.
- **Rules:** Harden capacity_check and security_connection_audit; keep rules aligned with fixed schema.

---

*This manifest is the single reference for project scope, requirements, and backlog. Update it when adding components or changing requirements.*
