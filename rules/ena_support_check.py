__version__ = "1.3.0"
import sqlite3
import pandas as pd

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    query = "SELECT node_id, value FROM node_stats WHERE metric = 'system.network.ena_enabled'"
    
    df = pd.read_sql_query(query, conn)
    conn.close()

    # The -1 value comes from our new 'Mock/Unknown' ingest logic
    if df.empty or (df['value'] == -1).any():
        return {
            "name": "1.b: ENA Support Check",
            "status": "INFO",
            "message": "ENA Telemetry Missing: OS-level statistics were not found in this bundle.",
            "remediation": "To retrieve this data, run 'collectinfo' as root or use 'asadm --lsmod --ethtool'. Manually verify with: 'ethtool -i eth0'."
        }

    critical_nodes = df[df['value'] == 0]
    if not critical_nodes.empty:
        return {
            "name": "1.b: ENA Support Check",
            "status": "CRITICAL",
            "message": f"ENA driver missing on {len(critical_nodes)} nodes.",
            "remediation": "AWS Nitro instances require the ENA driver for optimal networking. See AWS ENA documentation."
        }

    return {
        "name": "1.b: ENA Support Check",
        "status": "PASS",
        "message": "ENA Support is verified and active on all cluster nodes."
    }