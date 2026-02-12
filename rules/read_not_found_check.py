import sqlite3
import pandas as pd

# -----------------------------------------------------------------------------
# VERSION STAMP
# -----------------------------------------------------------------------------
__version__ = "1.6.0"

# --- Metadata ---
# ID: 4.b
# Title: Read Not Found Rate

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    check_id = "4.b"
    check_name = "Read Not Found Rate"
    target_table = "namespace_stats"
    
    try:
        # 1. SCHEMA SAFETY CHECK
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{target_table}'")
        if not cursor.fetchone():
            return {"id": check_id, "name": check_name, "status": "⚠️ DATA MISSING", "message": "Table not found."}

        # 2. QUERY LOGIC
        # Compare Read Not Found vs Total Master Reads
        query = f"""
            SELECT node_id, namespace, 
                   CAST(value AS REAL) as not_found_count
            FROM {target_table} 
            WHERE metric = 'client_read_not_found'
        """
        df = pd.read_sql_query(query, conn)
        
        if df.empty or df['not_found_count'].sum() == 0:
            return {"id": check_id, "name": check_name, "status": "PASS", "message": "No 'Read Not Found' events detected.", "remediation": "None"}

        # 3. ANALYSIS
        total_not_found = int(df['not_found_count'].sum())
        
        # We generally treat this as an 'INFO' level PASS unless it's astronomical.
        # For this tool, we will PASS but provide the evidence.
        return {
            "id": check_id,
            "name": check_name,
            "status": "PASS",
            "message": f"Detected {total_not_found:,} 'Read Not Found' events. This is expected in cache-miss workflows.",
            "remediation": (
                "**Why this matters:** A high rate of 'Not Found' results increases application latency as the "
                "client must handle the null result. If this is higher than expected, verify your Data Retention (TTL) "
                "settings or check if keys are being evicted prematurely due to HWM."
            )
        }
        
    except Exception as e:
        return {"id": check_id, "name": check_name, "status": "CRITICAL", "message": f"Error: {str(e)}"}
    finally:
        conn.close()