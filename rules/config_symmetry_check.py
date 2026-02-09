import sqlite3
import pandas as pd
__version__ = "1.4.0"

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    query = """
    SELECT config_name, COUNT(DISTINCT value) as variations
    FROM node_configs
    GROUP BY config_name
    HAVING variations > 1
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Filter out settings that ARE supposed to be unique per node
    ignore = ['service.node-id', 'network.service.address', 'network.heartbeat.address', 'service.cluster-name']
    df = df[~df['config_name'].isin(ignore)]

    if df.empty:
        return {"name": "Rule 4.b: Config Symmetry", "status": "PASS", "message": "All cluster-wide configurations are symmetric."}

    return {
        "id": "3.a", "name": "Config Symmetry",
        "status": "WARNING",
        "message": f"Detected {len(df)} configuration drifts across the cluster.",
        "remediation": "Check the Technical Details section to identify which specific parameters (e.g. memory, timeouts) differ."
    }
