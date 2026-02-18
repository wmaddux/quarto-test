# Aerospike Ingestor Template (v1.0.0)

## Overview
All ingestors must be Class-based and reside in the `ingest/` directory. They are responsible for taking a specific slice of the Aerospike JSON telemetry and persisting it to SQLite.

## Technical Requirements
* **Signature:** Must implement `run_ingest(self, node_id, node_data, conn, run_id)`.
* **Schema Safety:** Must use `CREATE TABLE IF NOT EXISTS`.
* **Data Integrity:** Must use `INSERT OR REPLACE` to avoid duplication.
* **Version Stamp:** Must include a `__version__` string at the top of the file.

## Implementation Pattern
```python
import sqlite3

__version__ = "1.x.x"

class YourMetricIngestor:
    def run_ingest(self, node_id, node_data, conn, run_id):
        cursor = conn.cursor()
        
        # 1. Ensure Table Exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS your_table (
                node_id TEXT,
                metric_name TEXT,
                value REAL,
                PRIMARY KEY (node_id, metric_name)
            )
        """)
        
        # 2. Extract Data from node_data
        # Navigate to your specific JSON path (e.g., node_data['as_stat']['...'])
        target_metrics = node_data.get("as_stat", {}).get("target_key", {})
        
        # 3. Persist
        for key, val in target_metrics.items():
            cursor.execute("""
                INSERT OR REPLACE INTO your_table (node_id, metric_name, value)
                VALUES (?, ?, ?)
            """, (node_id, key, val))
```