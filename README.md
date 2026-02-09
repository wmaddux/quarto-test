# Aerospike Health Analyzer (v1.4.0)

A modular diagnostic orchestration tool designed to ingest Aerospike telemetry into a structured SQLite database, execute health-check rules, and generate professional HTML reports via Quarto.

---

## 🚀 Application Pipeline

The analyzer transforms raw telemetry into actionable insights through a three-stage lifecycle:

1. **Ingestion:** Normalizes raw `ascinfo.json` data into `aerospike_health.db`.
2. **Analysis:** Executes independent logic modules from `rules/` against the database.
3. **Reporting:** Renders `report.qmd` into a self-contained HTML document with interactive visualizations.



---

## 📂 Project Structure

### Core Ingestion
* **`run_ingest.py`**: The primary CLI entry point.
* **`ingest_manager.py`**: Manages the SQLite schema and parser orchestration.
* **`ingest/`**: Contains specialized parsers (Stats, Config, Features).

### Analysis & UI
* **`rules/`**: The logic library. Every script here identifies a specific issue (e.g., HWM Skew, Storage Deadlocks).
* **`report.qmd`**: The Quarto template that executes rules and generates the UI.

---

## ⚙️ Installation

### Prerequisites
* **Python 3.10+**
* **Quarto CLI:** [Download Here](https://quarto.org/docs/get-started/)

### Setup
```bash
# Clone the repository
git clone [https://github.com/aerospike/health-analyzer.git](https://github.com/aerospike/health-analyzer.git)
cd health-analyzer

# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install pandas plotly