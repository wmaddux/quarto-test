# Aerospike Health Analyzer (TAM Edition)

A modular diagnostic tool designed to ingest Aerospike `collectinfo` telemetry into a structured SQLite database and generate professional health reports using Quarto.

---

## 🚀 Installation & Setup

### 1. Prerequisites
Ensure you have the following installed:
* **Python 3.10+**
* **Quarto** (`brew install quarto` or download from quarto.org)
* **Python Packages**: `pip install pandas plotly ipykernel`

### 2. Project Structure
Your directory should look like this:

- **ingest_manager.py**: The orchestrator.
- **run_ingest.py**: Entry point for data loading.
- **report.qmd**: Quarto report template.
- **ingest/**: Data Acquisition Modules (config, namespace, node).
- **rules/**: Health Check Modules (capacity, symmetry, etc).

---

## 🏎️ Execution Workflow

### Step 1: Ingest Data
Before rendering a report, you must populate the SQLite database. Place your `collectinfo` (tarball or JSON) in the root and run:

`python3 run_ingest.py`

*This creates/updates `aerospike_health.db` and populates the node_configs, node_stats, and namespace_stats tables.*

### Step 2: Render Report
Generate the HTML wellness report:

`quarto render report.qmd`

*Output is generated at `_site/report.html`.*

---

## 🛠️ Modular Architecture

### Ingestion (ingest/)
Ingestors use the suffix `_ci` to identify **CollectInfo** as the source. 
* **Managers** handle file decompression and JSON navigation.
* **Modules** handle specific data stanzas (e.g., `as_config` vs `as_stat`).
* **Note**: All ingest modules must accept `(node_id, data_subtree, conn, run_id)`.

### Health Rules (rules/)
Rules are standalone Python files. To add a new check:
1. Create `rules/my_new_check.py`.
2. Implement `run_check(db_path)`.
3. Import the module in `report.qmd` and add it to the `raw_results` list.

---

## 📊 Database Schema

| Table | Description |
|-------|-------------|
| **node_stats** | Global node metrics (client_write_error, cluster_size) |
| **namespace_stats** | Per-namespace metrics (data_used_pct, stop_writes) |
| **node_configs** | Running configurations (high-water-disk-pct, index-type) |

---

## 📋 Implemented Health Checks
* **1.b/c**: Capacity, Version Consistency, and Error Skews.
* **2.a/b/c**: Storage Deadlocks, SIndex on Flash, and Sprig Limits.
* **3.a**: Hot Key (Key Busy) Detection.
* **4.b**: Cross-Node Configuration Symmetry (Drift Detection).
