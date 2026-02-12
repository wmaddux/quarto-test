import sqlite3
import pandas as pd

# -----------------------------------------------------------------------------
# VERSION STAMP
# -----------------------------------------------------------------------------
__version__ = "1.6.0"

# --- Metadata ---
# ID: 4.c
# Title: Delete Not Found Rate

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    check_id = "4.c"
    check_name = "Delete Not Found Rate"
    target_table = "namespace_stats"
    
    try:
        # 1. SCHEMA SAFETY CHECK
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{target_table}'")
        if not cursor.fetchone():
            return {"id": check_id, "name": check_name, "status": "⚠️ DATA MISSING", "message": "Table not found."}

        # 2. QUERY LOGIC
        query = f"""
            SELECT node_id, namespace, CAST(value AS REAL) as delete_not_found
            FROM {target_table} 
            WHERE metric = 'client_delete_not_found'
        """
        df = pd.read_sql_query(query, conn)
        
        if df.empty or df['delete_not_found'].sum() == 0:
            return {"id": check_id, "name": check_name, "status": "PASS", "message": "No unnecessary delete attempts detected.", "remediation": "None"}

        # 3. ANALYSIS
        total_missed_deletes = int(df['delete_not_found'].sum())

        # If missed deletes > 1 Million, we issue a WARNING to investigate app logic
        if total_missed_deletes > 1_000_000:
            return {
                "id": check_id,
                "name": check_name,
                "status": "WARNING",
                "message": f"Detected {total_missed_deletes:,} 'Delete Not Found' events across the cluster.",
                "remediation": (
                    "**Why this matters:** Deleting a non-existent record still consumes a transaction "
                    "on the Aerospike server. 50M+ missed deletes suggest an application logic error, "
                    "such as 'double-deletes' or trying to delete records that have already expired via TTL.\n\n"
                    "**Action Plan:**\n"
                    "1. Audit application code for redundant delete calls.\n"
                    "2. Check if the application is attempting to delete records that Aerospike has already "
                    "removed via the Eviction process (check your TTL and HWM settings)."
                )
            }

        return {
            "id": check_id,
            "name": check_name,
            "status": "PASS",
            "message": f"Minor 'Delete Not Found' volume detected ({total_missed_deletes:,} events).",
            "remediation": "None"
        }
        
    except Exception as e:
        return {"id": check_id, "name": check_name, "status": "CRITICAL", "message": f"Error: {str(e)}"}
    finally:
        conn.close()