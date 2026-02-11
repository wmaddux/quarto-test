import sqlite3
import pandas as pd

# -----------------------------------------------------------------------------
# VERSION STAMP
# -----------------------------------------------------------------------------
__version__ = "1.5.4"

# --- Metadata ---
# ID: 2.d
# Title: Disk HWM Check

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    check_id = "2.d"
    check_name = "Disk HWM Check"
    target_table = "namespace_stats"
    
    try:
        # 1. SCHEMA SAFETY CHECK
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{target_table}'")
        if not cursor.fetchone():
            return {"id": check_id, "name": check_name, "status": "⚠️ DATA MISSING", "message": "Table not found."}

        # 2. QUERY LOGIC
        # We look for the maximum disk usage percentage recorded for each namespace/node
        query = f"""
            SELECT node_id, namespace, CAST(value AS REAL) as used_pct 
            FROM {target_table} 
            WHERE metric = 'service.data_used_pct'
        """
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            return {
                "id": check_id, "name": check_name, "status": "PASS", 
                "message": "No disk-based namespace metrics found.",
                "remediation": "None"
            }

        # 3. ANALYSIS
        # Standard Aerospike HWM is often 60%. We set a warning threshold here.
        # In a perfect world, we'd pull the actual 'high-water-disk-pct' from node_configs,
        # but 60 is the industry-standard baseline for TAM warnings.
        warning_threshold = 60
        critical_threshold = 75
        
        peak_usage = df['used_pct'].max()
        over_threshold = df[df['used_pct'] >= warning_threshold]

        if not over_threshold.empty:
            worst_case = over_threshold.sort_values(by='used_pct', ascending=False).iloc[0]
            status = "CRITICAL" if worst_case['used_pct'] >= critical_threshold else "WARNING"
            
            return {
                "id": check_id,
                "name": check_name,
                "status": status,
                "message": f"Namespace '{worst_case['namespace']}' is at {int(worst_case['used_pct'])}% disk capacity on node {worst_case['node_id']}.",
                "remediation": (
                    f"**Why this matters:** When disk usage exceeds the High Water Mark ({warning_threshold}%), "
                    "Aerospike begins expiring (evicting) data with a TTL. If usage continues to rise and hits "
                    "`stop-writes-pct` (default 90%), the cluster will reject all incoming writes.\n\n"
                    "**Action Plan:**\n"
                    "1. Check for data skew: Run `asadm -e 'show statistics namespace'` to see if one node has more data than others.\n"
                    "2. Verify TTLs: Ensure data has a 'Time To Live' (TTL) so eviction can reclaim space.\n"
                    "3. Add Capacity: Consider adding nodes to the cluster or increasing SSD size if using cloud-native storage."
                )
            }

        # EVIDENCE-BASED PASS
        return {
            "id": check_id, 
            "name": check_name, 
            "status": "PASS",
            "message": f"All namespaces are healthy. Peak disk utilization is {int(peak_usage)}% (Threshold: {warning_threshold}%).",
            "remediation": "None"
        }
        
    except Exception as e:
        return {"id": check_id, "name": check_name, "status": "CRITICAL", "message": f"Error: {str(e)}"}
    finally:
        conn.close()