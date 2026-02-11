# Aerospike Health Analyzer (v1.4.1)

A professional diagnostic suite designed for Aerospike 7.2+ environments. This tool ingests `collectinfo` bundles into a localized SQLite database and executes a comprehensive ruleset to identify performance bottlenecks, configuration drift, and hardware risks.

## Usage (v1.4.1)

### 1. Ingest Telemetry
Process a standard Aerospike `collectinfo` bundle into the analyzer's database:
BACKTICKSbash
python3 run_ingest.py --bundle bundles/your-collectinfo.tgz
BACKTICKS

### 2. Validate Environment
(Optional but recommended) Run the integrity check to verify rule signatures and schema:
BACKTICKSbash
python3 check_integrity.py
BACKTICKS

### 3. Generate Report
Render the high-fidelity HTML report using Quarto:
BACKTICKSbash
quarto render report.qmd
BACKTICKS

## Key Features
* **Recursive Ingestion:** Modernized ingestors handle nested 7.x telemetry structures.
* **Cloud-Aware:** Automatic detection of AWS (ENA) and Azure platforms.
* **Proactive Forecasting:** Capacity rules predict HWM breaches based on ingestion trends.
* **Interactive Visualizations:** Plotly-based utilization and connection charts.

---
**Version:** 1.4.1 | **Last Updated:** 2026-02-10