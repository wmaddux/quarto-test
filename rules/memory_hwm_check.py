import sqlite3
import pandas as pd

__version__ = "1.2.0"

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    # Updated to the verified 7.2 metric name
    query = "SELECT node_id, value FROM node_stats WHERE metric = 'service.system_free_mem_pct'"
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        return {"name": "2.e: Memory HWM Check", "status": "INFO", "message": "Memory metrics not found in telemetry."}

    # Alert if free system memory drops below 20%
    threshold = 20
    critical_nodes = df[df['value'] < threshold]

    if not critical_nodes.empty:
        nodes_list = ", ".join(critical_nodes['node_id'].astype(str).tolist())
        return {
            "name": "2.e: Memory HWM Check",
            "status": "CRITICAL",
            "message": f"System free memory below {threshold}% on nodes: {nodes_list}",
            "remediation": "Check for non-Aerospike processes consuming RAM or increase system memory."
        }

    return {
        "name": "2.e: Memory HWM Check",
        "status": "PASS",
        "message": f"System memory headroom is healthy (all nodes > {threshold}% free)."
    }