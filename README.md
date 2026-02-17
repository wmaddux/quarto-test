# Aerospike Health Analyzer (v1.6.1)

A universal diagnostic framework for Aerospike clusters, providing native support for **6.x, 7.x, and 8.x** Enterprise editions. It ingests `collectinfo` telemetry into a relational SQLite database, executes a version-aware rule engine, and generates modular Quarto HTML reports.

---

## 🏗 Architecture & Design

The tool operates as a decoupled data pipeline:

1.  **Ingestion Layer (`ingest/`)**: Orchestrates schema creation and JSON traversal, flattening hierarchical telemetry into relational tables.
2.  **Logic Layer (`rules/`)**: Independent Python modules that perform version-aware anomaly detection using schema discovery.
3.  **Presentation Layer (`report_components/`)**: A modular Quarto-based UI that adapts visualizations based on available data.

---

## ⚙️ Prerequisites & Installation

### Local Environment Requirements
* **Python 3.10 - 3.13**: The core engine utilizes modern Python features and type hinting.
* **Quarto CLI**: Required for rendering the interactive HTML report. [Download Quarto](https://quarto.org/docs/get-started/)
* **Aerospike Admin (asadm)**: Necessary for collecting the telemetry bundles (`.tgz`) from target clusters.

### Setup
```bash
git clone [https://github.com/aerospike/health-analyzer.git](https://github.com/aerospike/health-analyzer.git)
cd health-analyzer

# Initialize Virtual Environment
python3 -m venv .venv
source .venv/bin/activate

# Install Dependencies
pip install pandas plotly sqlite3
```

---

## 📂 Directory Structure

```text
health-analyzer/
├── run_ingest.py         # Ingestion entry point
├── check_integrity.py    # Rule/Schema validator
├── commit_baseline.py    # Git automation script
├── set_version.py        # Global version synchronizer
├── report.qmd            # Master Quarto template
├── _setup.qmd            # Data loading & rule execution
├── ingest/               # Telemetry parsers
├── rules/                # Diagnostic logic library
├── report_components/    # Modular UI partials
└── bundles/              # Source .tgz collectinfo files
```

---

## 🛠 Usage

### 1. Ingest Telemetry
Ingests an Aerospike `collectinfo` bundle. The analyzer automatically detects the version and cloud platform.

```bash
# Clean previous database to prevent schema pollution
rm -f aerospike_health.db

# Ingest new bundle
python3 run_ingest.py bundles/your_bundle.tgz
```

### 2. Verify and Render
Always run the integrity check before rendering to ensure your local environment and ruleset are aligned with the ingested data.

```bash
# Verify rules
python3 check_integrity.py

# Generate HTML report
quarto render report.qmd
```

### 3. Maintain the Baseline
Use the internal tools to keep versioning and Git history synchronized.

```bash
# Sync version strings globally (rules, ingestors, docs)
python3 set_version.py

# Execute atomic Git commit and tagging
python3 commit_baseline.py
```

---

**Version:** 1.6.1 | **Target Support:** Aerospike 6.x, 7.x, 8.x Enterprise | **Maintainer:** TAM Team