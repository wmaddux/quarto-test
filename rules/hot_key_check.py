import sqlite3
import pandas as pd

# -----------------------------------------------------------------------------
# VERSION STAMP
# -----------------------------------------------------------------------------
__version__ = "1.4.1"

# --- Metadata ---
# ID: 4.a
# Title: Hot Key Detection

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    check_id = "4.a"
    check_name = "Hot Key Detection"
    
    try:
        # Query for contention errors (fail_key_busy)
        query = """
            SELECT node_id, namespace, CAST(value AS REAL) as busy_errors
            FROM namespace_stats 
            WHERE metric LIKE '%fail_key_busy%'
        """
        df = pd.read_sql_query(query, conn)
        
        total_errors = df['busy_errors'].sum() if not df.empty else 0

        if total_errors > 0:
            return {
                "id": check_id, 
                "name": check_name, 
                "status": "WARNING",
                "message": f"Detected {int(total_errors):,} 'Key Busy' errors in the cluster telemetry.",
                "remediation": (
                    "**Assessment:** 'Key Busy' errors occur when multiple concurrent transactions attempt to "
                    "access the same record, exceeding the internal lock wait timeout. This almost always indicates "
                    "a 'Hot Key' (high-contention record) in the application data model.\n\n"
                    "**Action Plan:**\n"
                    "1. Use `asadm -e 'show statistics namespace'` and search for the `fail_key_busy` metric to "
                    "identify the specific Namespace and Node experiencing the highest contention.\n"
                    "2. Evaluate application-level caching or data sharding to distribute access more evenly across different keys.\n"
                    "3. Check for long-running transactions (UDFs, large batch writes, or complex Read-Modify-Write cycles) "
                    "that may be holding record locks for extended periods."
                )
            }

        return {
            "id": check_id, 
            "name": check_name, 
            "status": "PASS",
            "message": "No 'key busy' or transaction contention errors detected in this snapshot.",
            "remediation": "None"
        }
    except Exception as e:
        return {"id": check_id, "name": check_name, "status": "CRITICAL", "message": f"Diagnostic Error: {str(e)}"}
    finally:
        conn.close()