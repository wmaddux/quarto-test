# Testing

## End-to-end loop (ingest → validate → rules)

To quickly verify that ingest and rules work without rendering the full Quarto report:

1. **Single command** (bundle path as argument):

   ```bash
   python3 tests/run_e2e.py path/to/your_bundle.tgz
   ```

2. **Using a fixture bundle** (fast iteration):

   Set `AEROSPIKE_E2E_BUNDLE` to a collectinfo tarball path so you don’t pass it every time:

   ```bash
   export AEROSPIKE_E2E_BUNDLE=/path/to/collectinfo.tgz
   python3 tests/run_e2e.py
   ```

   Exit code: `0` = pass (schema matches baseline, all rules run without schema/SQL errors), `1` = fail, `2` = usage or missing bundle.

## What the e2e run does

1. **Ingest:** `run_ingest.py <bundle>` — builds `aerospike_health.db` from `schema/baseline.sql` and runs all ingestors.
2. **Integrity:** `check_integrity.py` — checks live DB schema against `schema/baseline.sql`, then runs every rule and reports schema errors or rule crashes.

Use this loop after changing ingest logic or rules to confirm the pipeline and rule data needs are satisfied.

**Rules report mode (customer-facing guidance):** To see the full output that would appear in the report for each rule (message + remediation), run:

```bash
python3 check_integrity.py --report
```

This prints each rule’s id, name, status, message, and full remediation so you can review clarity and effectiveness without rendering the Quarto report.

## Rule data dependencies

Rules depend on tables and columns defined in the canonical schema. See:

- [docs/schema.md](schema.md) — table descriptions and usage.
- [docs/telemetry-version-path-matrix.md](telemetry-version-path-matrix.md) — version-specific JSON paths mapped to tables.

If a rule reports `DATA MISSING` or schema/SQL errors, ensure the ingestors for the required tables are enabled and the bundle contains the expected telemetry for your Aerospike version.
