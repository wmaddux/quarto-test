# Aerospike Health Analyzer (v1.6.1)

A universal diagnostic framework for Aerospike clusters, providing native support for **6.x, 7.x, and 8.x** Enterprise editions. It ingests `collectinfo` telemetry into a relational SQLite database, executes a version-aware rule engine, and generates modular Quarto HTML reports.

---

## 🏗 Architecture & Design

The tool is built on a **Version-Agnostic Data Pipeline**:

1.  **Schema-Resilient Ingestion (`ingest/`)**:
    * **`run_ingest.py`**: Automated discovery of telemetry regardless of bundle naming conventions.
    * **`ingest_manager.py`**: Handles dynamic schema creation, ensuring compatibility with evolving Aerospike telemetry structures across major versions.
    * **Wide-Table Mapping**: Specifically handles the transition from vertical metric/value pairs in older versions to the horizontal/wide telemetry format in 7.x and 8.x.
2.  **Cross-Generation Logic (`rules/`)**:
    * **Dynamic Discovery**: Rules use "Schema Discovery" (querying `sqlite_master` and `PRAGMA table_info`) to automatically adjust queries based on the detected database version (e.g., handling `ns` vs `ns_name`).
    * **Integrity Gate (`check_integrity.py`)**: A pre-flight validator that ensures the ruleset is compatible with the specific schema of the ingested bundle before rendering.
3.  **Modular Presentation (`report_components/`)**:
    * **`report.qmd`**: A decoupled Quarto template that remains constant while sub-components (`report_components/`) adapt the visualization based on the available data.



---

## 📂 Directory Structure

```text
health-analyzer/
├── run_ingest.py         # Ingestion entry point
├── check_integrity.py    # Multi-version rule validator
├── commit_baseline.py    # Automation & CI/CD pipeline
├── report.qmd            # Master report template
├── _setup.qmd            # Version-aware data loading & rule execution
├── ingest/               # Cross-generation telemetry parsers
├── rules/                # Diagnostic logic library (6.x/7.x/8.x compatible)
├── report_components/    # Modular UI partials (.qmd)
├── bundles/              # Source .tgz collectinfo files
└── aerospike_health.db   # SQLite database (generated)
```

---

## ⚙️ Installation

### Prerequisites
* **Python 3.10+**
* **Quarto CLI**: [Installation Guide](https://quarto.org/docs/get-started/)

### Setup
```bash
git clone [https://github.com/aerospike/health-analyzer.git](https://github.com/aerospike/health-analyzer.git)
cd health-analyzer

# Setup Virtual Environment
python3 -m venv .venv
source .venv/bin/activate

# Install Dependencies
pip install pandas plotly sqlite3
```

---

## 🛠 Usage

### 1. Data Ingestion
Processes a `collectinfo` bundle. The ingestor automatically detects the Aerospike version, cluster flavor (AWS/GCP/Azure/Bare Metal), and topology (AP/SC).

```bash
# Recommended: Clean previous runs
rm -f aerospike_health.db

# Ingest bundle
python3 run_ingest.py bundles/your_bundle.tgz
```

### 2. Integrity Check
Verify that the database schema (version-specific) supports the current ruleset.
```bash
python3 check_integrity.py
```

### 3. Generate Report
Renders the final diagnostic HTML.
```bash
quarto render report.qmd
```

---

## 📝 Rule Development
New rules should implement the `run_check(db_path)` interface. To maintain multi-version support, always use schema-discovery queries to identify column availability before executing analysis.

**Version:** 1.6.0 | **Maintainer:** Aerospike TAM Team | **Target:** Aerospike 6.x, 7.x, 8.x Enterprise