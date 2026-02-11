# Aerospike Health Analyzer (v1.5.4)

[cite_start]The **Aerospike Health Analyzer** is a diagnostic framework developed to enable rapid identification of configuration and operational issues across Aerospike 7.x clusters[cite: 3, 7]. [cite_start]By automating the detection of recurring issue patterns tied to deployment topology and resource limits, this tool provides a structured, data-driven way to communicate cluster health[cite: 6, 7].



---

## 🚀 Application Pipeline

[cite_start]The analyzer transforms raw telemetry into actionable insights through a three-stage lifecycle[cite: 7, 12]:

1.  [cite_start]**Ingestion:** Dynamically discovers the primary telemetry member within `.tgz` bundles and normalizes data into a structured SQLite database[cite: 9, 66].
2.  [cite_start]**Analysis:** Executes a declarative anomaly detection framework using independent rule modules to identify deviations from best practices[cite: 10, 16].
3.  [cite_start]**Reporting:** Renders a high-fidelity "Wellness Report" via Quarto, grouping findings by subsystem and providing remediation advice[cite: 3, 50, 52].

---

## 📂 Project Structure

### Core Orchestration
* **`run_ingest.py`**: CLI entry point that delegates bundle processing to the manager.
* **`ingest_manager.py`**: Handles dynamic bundle interrogation and orchestrates the 3-level JSON loop (Timestamp → Cluster → Node).
* **`ingest/`**: Class-based ingestors implementing the standard `run_ingest` signature for specific telemetry slices (e.g., `set_stats`, `security_stats`).

### Analysis & UI
* **`rules/`**: The logic library. [cite_start]Each module expresses and detects a specific anomaly, such as storage deadlocks or security connection spikes[cite: 10, 36].
* **`check_integrity.py`**: A validation suite that verifies the database schema against the full ruleset to ensure project integrity.
* **`report.qmd`**: The Quarto template that generates the final interactive HTML scorecard[cite: 49, 50].

---

## ⚙️ Installation & Setup

### Prerequisites
* **Python 3.10+**
* **Quarto CLI:** [Download and Install Quarto](https://quarto.org/docs/get-started/)

### Setup
```bash
# Clone the repository
git clone https://github.com/aerospike/health-analyzer.git
cd health-analyzer

# Initialize virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install required dependencies
pip install pandas plotly sqlite3
```

---

## 🛠 Usage

### 1. Ingest Telemetry
Pass a standard Aerospike `collectinfo` bundle. The analyzer dynamically discovers the nested JSON regardless of filename prefixes. 
**Note:** To ensure a clean state, it is recommended to delete any existing database before re-ingesting.
```bash
# Remove old data
rm -f aerospike_health.db

# Ingest new bundle
python3 run_ingest.py bundles/aws-cluster.collect_info_20260120.tgz
```

### 2. Verify Integrity
Ensure the ingested data is consistent with the latest ruleset before rendering.
```bash
python3 check_integrity.py
```

### 3. Generate the Wellness Report
Render the final diagnostic report into a self-contained HTML file.
```bash
quarto render report.qmd
```

---

## 🤝 Contributing
We encourage contributions that expand our declarative ruleset[cite: 23, 57]. To add a new rule:
1.  Review the **`CATALOG.md`** for planned roadmap items.
2.  Implement your logic in `rules/` using the standard `run_check(db_path)` interface.
3.  Register your rule in `check_integrity.py` and `report.qmd`.

---
**Baseline:** v1.5.4 | **Last Updated:** 2026-02-11 | **Maintainer:** Technical Account Management (TAM) [cite: 14, 76]