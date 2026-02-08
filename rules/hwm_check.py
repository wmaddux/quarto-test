import sqlite3
import pandas as pd
__version__ = "1.3.0"

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    # 7.2 Namespace-level storage query
    query = """
    SELECT node_id, namespace, value 
    FROM namespace_stats 
    WHERE metric = 'service.data_used_pct'
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        return {"id": "2.d", "name": "Disk HWM Check", "status": "INFO", "message": "No disk-based storage metrics found."}

    # Identify any namespace on any node exceeding 60%
    threshold = 60
    breach_df = df[df['value'] >= threshold]

    if not breach_df.empty:
        # Format a helpful message for the TAM
        offenders = ", ".join([f"{r['namespace']}@{r['node_id']} ({r['value']}%)" for _, r in breach_df.iterrows()])
        return {
            "id": "2.d", "name": "Disk HWM Check",
            "status": "CRITICAL",
            "message": f"High Water Mark breached (>{threshold}%): {offenders}",
            "remediation": "Increase storage capacity or adjust TTL/eviction policies immediately."
        }

    return {
        "id": "2.d", "name": "Disk HWM Check",
        "status": "PASS",
        "message": f"All namespaces are below the {threshold}% High Water Mark."
    }