# Aerospike Health Analyzer (v1.5.4)

The **Aerospike Health Analyzer** is a professional diagnostic framework and toolset developed to enable rapid identification of configuration and operational issues across Aerospike 7.x clusters[cite: 3]. By automating the detection of recurring issue patterns tied to deployment topology, resource limits, and operational practices, this tool provides a structured, data-driven way to analyze and communicate cluster health[cite: 6, 7]. It serves as the foundation for delivering scalable, proactive support to enterprise environments[cite: 5].

---

## 🚀 Application Pipeline

The analyzer transforms raw telemetry into actionable insights through a three-stage lifecycle:

1.  **Ingestion:** Dynamically discovers the primary telemetry member within `.tgz` bundles and normalizes system vitals and configuration attributes into a structured SQLite database.
2.  **Analysis:** Executes a declarative, rule-based anomaly detection framework to identify deviations from best practices, such as inconsistent replication factors or sindex memory exhaustion.
3.  **Reporting:** Renders a high-fidelity "Wellness Report" via Quarto, providing a summary dashboard of cluster vitals and detailed remediation recommendations with severity and impact levels.

---

## 📂 Project Structure

### Core Orchestration
* **`run_ingest.py`**: The primary CLI entry point for processing bundles.
* **`ingest_manager.py`**: Manages the SQLite schema, parser orchestration, and the 3-level JSON loop (Timestamp → Cluster → Node).
* **`ingest/`**: Contains specialized class-based ingestors for specific telemetry slices, such as `set_stats` and `security_stats`.

### Analysis & UI
* **`rules/`**: The logic library. Each independent module expresses and detects a specific anomaly, such as storage deadlocks or hot keys[cite: 10, 18].
* **`check_integrity.py`**: A validation suite used to verify the database schema and rule signatures before report generation.
* **`report.qmd`**: The Quarto template that executes rules and generates the final interactive HTML scorecard.

---

## ⚙️ Installation & Setup

### Prerequisites
* **Python 3.10+**
* **Quarto CLI:** [Download and Install Quarto](https://quarto.org/docs/get-started/)

### Setup
```bash
# Clone the repository
git clone [https://github.com/aerospike/health-analyzer.git](https://github.com/aerospike/health-analyzer.git)
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
Pass a standard Aerospike `collectinfo` bundle[cite: 66]. The analyzer dynamically discovers the nested JSON regardless of filename prefixes. 
**Note:** To ensure a clean data model and prevent schema conflicts, always delete any existing database before re-ingesting new data[cite: 9].

```bash
# Remove old data to ensure a fresh schema
rm -f aerospike_health.db

# Ingest new bundle
python3 run_ingest.py bundles/aws-cluster.collect_info_20260120.tgz
```

### 2. Verify Integrity
Ensure the ingested data is consistent with the latest rule signatures before rendering the report.
```bash
python3 check_integrity.py
```

### 3. Generate the Wellness Report
Render the final diagnostic scorecard into a self-contained HTML file[cite: 63, 69].
```bash
quarto render report.qmd
```

---

## 🤝 Contributing
We encourage contributions that expand our declarative ruleset[cite: 47]. To add a new rule:
1.  Review the **`CATALOG.md`** for planned roadmap items and identified product gaps[cite: 26].
2.  Implement your logic in `rules/` using the standard `run_check(db_path)` interface.
3.  Register your rule in `check_integrity.py` and `report.qmd`.

---
**Baseline:** v1.5.4 | **Last Updated:** 2026-02-11 | **Maintainer:** Technical Account Management (TAM)