import sqlite3
import pandas as pd

__version__ = "1.4.0"

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    check_id = "3.a"
    check_name = "Config Symmetry"
    target_table = "node_configs"
    
    try:
        # 1. Schema Safety Check
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{target_table}'")
        if not cursor.fetchone():
            return {"id": check_id, "name": check_name, "status": "⚠️ DATA MISSING", "message": "Table not found."}

        # 2. Query variations
        query = f"SELECT config_name, COUNT(DISTINCT value) as variations FROM {target_table} GROUP BY config_name HAVING variations > 1"
        df = pd.read_sql_query(query, conn)

        # 3. ANALYSIS & FILTERING
        # A. Exact matches to ignore (Identity/Networking)
        ignore_exact = [
            'service.node-id', 'service.cluster-name', 'network.service.address', 
            'network.service.access-address', 'network.service.alternate-access-address',
            'network.heartbeat.address', 'network.heartbeat.mesh-seed-address-port',
            'network.fabric.address', 'network.service.port'
        ]
        df = df[~df['config_name'].isin(ignore_exact)]

        # B. Partial matches to ignore (Dynamic Statistics)
        # These keys contain node-specific data counts, not configurations
        stat_patterns = ['.objects', '.data_used_bytes', '.memory_data_bytes', '.stop-writes-count', '.evict-count']
        df = df[~df['config_name'].str.contains('|'.join(stat_patterns), regex=True)]

        if df.empty:
            return {
                "id": check_id, "name": check_name, "status": "PASS",
                "message": "All cluster-wide configurations are symmetric.", "remediation": "None"
            }
        
        drift_count = len(df)
        return {
            "id": check_id, "name": check_name, "status": "WARNING",
            "message": f"Detected {drift_count} configuration drifts across the cluster.",
            "remediation": (
                "**Why this matters:** Asymmetric configurations create silent bottlenecks and unpredictable behavior.\n\n"
                "**Action Plan:**\n"
                "1. Run `asadm -e 'conf diff'` to pinpoint the remaining differences.\n"
                "2. Standardize timeouts, thread counts, and memory limits across all nodes."
            )
        }
        
    except Exception as e:
        return {"id": check_id, "name": check_name, "status": "CRITICAL", "message": f"Error: {str(e)}"}
    finally:
        conn.close()