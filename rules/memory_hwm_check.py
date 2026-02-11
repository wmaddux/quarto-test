import sqlite3
import pandas as pd

# -----------------------------------------------------------------------------
# VERSION STAMP
# -----------------------------------------------------------------------------
__version__ = "1.5.4"

# --- Metadata ---
# ID: 2.e
# Title: Memory HWM Check

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    check_id = "2.e"
    check_name = "Memory HWM Check"
    target_table = "namespace_stats"
    
    try:
        # 1. SCHEMA SAFETY CHECK
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{target_table}'")
        if not cursor.fetchone():
            return {"id": check_id, "name": check_name, "status": "⚠️ DATA MISSING", "message": "Table not found."}

        # 2. QUERY LOGIC
        # We look for the maximum memory usage percentage recorded for each namespace/node
        query = f"""
            SELECT node_id, namespace, CAST(value AS REAL) as used_pct 
            FROM {target_table} 
            WHERE metric = 'service.memory_used_pct'
        """
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            return {
                "id": check_id, "name": check_name, "status": "PASS", 
                "message": "No memory-based namespace metrics found.",
                "remediation": "None"
            }

        # 3. ANALYSIS
        # Thresholds: 60% is a standard TAM Warning; 80% is Critical (Approaching Stop-Writes)
        warning_threshold = 60
        critical_threshold = 80
        
        peak_usage = df['used_pct'].max()
        over_threshold = df[df['used_pct'] >= warning_threshold]

        if not over_threshold.empty:
            worst_case = over_threshold.sort_values(by='used_pct', ascending=False).iloc[0]
            status = "CRITICAL" if worst_case['used_pct'] >= critical_threshold else "WARNING"
            
            return {
                "id": check_id,
                "name": check_name,
                "status": status,
                "message": f"Namespace '{worst_case['namespace']}' is at {int(worst_case['used_pct'])}% memory capacity on node {worst_case['node_id']}.",
                "remediation": (
                    f"**Why this matters:** Memory exhaustion is a critical risk. Once `high-water-memory-pct` is reached, "
                    "Aerospike begins evicting data. If memory hits `stop-writes-sys-memory-pct` or `stop-writes-pct`, "
                    "the node will stop accepting all client writes to prevent a crash.\n\n"
                    "**Action Plan:**\n"
                    "1. **Check Index Size:** If you recently added Secondary Indexes, they consume RAM. Review SIndex memory usage.\n"
                    "2. **Check Set Deletions:** If you are deleting data, ensure defragmentation is reclaiming memory effectively.\n"
                    "3. **Scale Up:** Memory issues are best solved by adding nodes to the cluster or increasing the `memory-size` "
                    "parameter if the host has physical RAM available."
                )
            }

        # EVIDENCE-BASED PASS
        return {
            "id": check_id, 
            "name": check_name, 
            "status": "PASS",
            "message": f"Cluster RAM headroom is healthy. Peak memory utilization is {int(peak_usage)}% (Threshold: {warning_threshold}%).",
            "remediation": "None"
        }
        
    except Exception as e:
        return {"id": check_id, "name": check_name, "status": "CRITICAL", "message": f"Error: {str(e)}"}
    finally:
        conn.close()