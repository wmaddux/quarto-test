__version__ = "1.3.0"
import sqlite3
import pandas as pd

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    # Checking for both 'build' and 'version' to be safe
    query = "SELECT node_id, value FROM configs WHERE name IN ('build', 'version')"
    
    try:
        df = pd.read_sql_query(query, conn)
    except Exception:
        return {"id": "1.c", "name": "Version Consistency", "status": "INFO", "message": "Telemetry not yet ingested."}
    finally:
        conn.close()

    if df.empty:
        return {"id": "1.c", "name": "Version Consistency", "status": "WARNING", "message": "No version/build found."}

    unique_versions = df['value'].unique()
    if len(unique_versions) > 1:
        return {
            "id": "1.c", "name": "Version Consistency", 
            "status": "CRITICAL", 
            "message": f"Mismatches: {', '.join(unique_versions)}"
        }

    return {"id": "1.c", "name": "Version Consistency", "status": "PASS", "message": f"Cluster consistent on {unique_versions[0]}"}