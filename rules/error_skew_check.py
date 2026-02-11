import sqlite3
import pandas as pd

# -----------------------------------------------------------------------------
# VERSION STAMP
# -----------------------------------------------------------------------------
__version__ = "1.4.0"

# --- Metadata ---
# ID: 1.a
# Title: Service Error Skew

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    check_id = "1.a"
    check_name = "Service Error Skew"
    target_table = "node_stats"
    
    try:
        # 1. SCHEMA SAFETY CHECK
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{target_table}'")
        if not cursor.fetchone():
            return {"id": check_id, "name": check_name, "status": "⚠️ DATA MISSING", "message": "Table node_stats not found."}

        # 2. QUERY LOGIC
        # We look for total client-side service errors
        query = f"""
            SELECT node_id, CAST(value AS REAL) as errors 
            FROM {target_table} 
            WHERE metric = 'service.client_proxy_error' 
               OR metric = 'client_proxy_error'
        """
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            return {
                "id": check_id, "name": check_name, "status": "PASS", 
                "message": "No service-level proxy errors detected.",
                "remediation": "None"
            }

        # 3. ANALYSIS (Skew Detection)
        total_errors = df['errors'].sum()
        mean_errors = df['errors'].mean()
        max_errors = df['errors'].max()

        if total_errors == 0:
             return {
                "id": check_id, "name": check_name, "status": "PASS", 
                "message": f"Cluster is healthy with a total of {int(total_errors)} errors.",
                "remediation": "None"
            }

        # Logic: If a node has 2x the average errors AND more than 100 errors total, flag it.
        if max_errors > (mean_errors * 2) and max_errors > 100:
            skewed_node = df[df['errors'] == max_errors]['node_id'].iloc[0]
            return {
                "id": check_id,
                "name": check_name,
                "status": "WARNING",
                "message": f"Error skew detected on node {skewed_node} ({int(max_errors)} errors vs avg {int(mean_errors)}).",
                "remediation": (
                    "**Why this matters:** When one node shows significantly higher error rates than its peers, "
                    "it typically indicates a localized issue such as failing hardware (SSD), network NIC "
                    "instability, or Linux kernel-level contention.\n\n"
                    "**Action Plan:**\n"
                    "1. Check the system logs (`dmesg` or `/var/log/messages`) on the affected node for hardware alerts.\n"
                    "2. Verify network retransmits using `netstat -s`.\n"
                    "3. If the errors are localized to one node, consider draining traffic and restarting the service."
                )
            }

        return {
            "id": check_id, 
            "name": check_name, 
            "status": "PASS",
            "message": f"Error distribution is uniform across all {len(df)} nodes.",
            "remediation": "None"
        }
        
    except Exception as e:
        return {"id": check_id, "name": check_name, "status": "CRITICAL", "message": f"Error: {str(e)}"}
    finally:
        conn.close()