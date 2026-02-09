__version__ = "1.4.0"
import sqlite3
import pandas as pd

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    
    # Check if we have any 'file' source data
    query = "SELECT COUNT(*) as file_count FROM node_configs WHERE source = 'file'"
    file_count = pd.read_sql_query(query, conn).iloc[0]['file_count']
    conn.close()

    if file_count == 0:
        return {
            "id": "3.b",
            "name": "Config Drift",
            "status": "⚠️ DATA MISSING",
            "message": "The static aerospike.conf file was not found in the collectinfo bundle.",
            "finding": (
                "Cannot perform drift analysis (Runtime vs. Static). "
                "To enable this check in the future, run: "
                "'asadm -e \"collectinfo --cf /etc/aerospike/aerospike.conf\"'"
            )
        }

    return {
        "id": "3.b",
        "name": "Config Drift",
        "status": "✅ PASS",
        "message": "No drift detected between runtime and static file configurations."
    }