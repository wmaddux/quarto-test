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
    
    # -------------------------------------------------------------------------
    # CONFIGURATION
    # -------------------------------------------------------------------------
    check_id = "1.a"
    check_name = "Service Error Skew"
    target_table = "node_stats"
    
    try:
        # 1. SCHEMA SAFETY CHECK
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{target_table}'")
        
        if not cursor.fetchone():
            return {
                "id": check_id, "name": check_name, "status": "⚠️ DATA MISSING",
                "message": f"Table '{target_table}' not found in database.",
                "remediation": "Verify that the NodeStatsIngestor is enabled in ingest/__init__.py."
            }

        # 2. QUERY LOGIC
        # We look for total service errors recorded since the process started.
        query = f"""
            SELECT node_id, CAST(value AS REAL) as error_count 
            FROM {target_table} 
            WHERE metric = 'service.service_error'
        """
        df = pd.read_sql_query(query, conn)
        
        # 3. ANALYSIS & RESULTS
        if df.empty or df['error_count'].sum() == 0:
            return {
                "id": check_id, "name": check_name, "status": "PASS",
                "message": "No service errors detected across the cluster.",
                "remediation": "None"
            }
        
        # Calculate evidence metrics
        total_errors = df['error_count'].sum()
        max_errors = df['error_count'].max()
        mean_errors = df['error_count'].mean()
        
        # Calculate skew: Is any node's error count > 2x the cluster average?
        # We also set a floor of 100 errors to avoid flagging tiny, insignificant skews.
        skewed_nodes = df[(df['error_count'] > (mean_errors * 2)) & (df['error_count'] > 100)]

        if not skewed_nodes.empty:
            worst_node = skewed_nodes.sort_values(by='error_count', ascending=False).iloc[0]
            return {
                "id": check_id,
                "name": check_name,
                "status": "WARNING",
                "message": f"Node {worst_node['node_id']} shows significant error skew ({int(worst_node['error_count'])} errors).",
                "remediation": (
                    "**Why this matters:** When one node exhibits significantly higher error rates than the rest of the cluster, "
                    "it typically points to a localized issue such as a failing SSD, a saturated network interface (NIC), "
                    "or OS-level resource exhaustion.\n\n"
                    "**Action Plan:**\n"
                    "1. Check node-specific logs: `asadm -e 'log show' --node {worst_node['node_id']}`.\n"
                    "2. Inspect the 'service' section of `asinfo -v statistics` for that node to identify which specific "
                    "error codes (e.g., `error_no_node_id`) are driving the skew.\n"
                    "3. Verify hardware health and kernel logs (`dmesg`) on the affected host."
                )
            }

        # EVIDENCE-BASED PASS
        return {
            "id": check_id, 
            "name": check_name, 
            "status": "PASS",
            "message": (
                f"Cluster total: {int(total_errors)} errors. "
                f"Max per-node: {int(max_errors)} (Mean: {int(mean_errors)}). "
                f"Distribution is within healthy thresholds."
            ),
            "remediation": "None"
        }
        
    except Exception as e:
        return {
            "id": check_id, "name": check_name, "status": "CRITICAL",
            "message": f"Execution Error: {str(e)}",
            "remediation": "Review the database schema and rule query logic."
        }
    finally:
        conn.close()