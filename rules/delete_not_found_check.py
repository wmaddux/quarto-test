import sqlite3
import pandas as pd

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    # Target 7.2 specific path
    query = "SELECT node_id, namespace, value FROM namespace_stats WHERE metric = 'service.client_delete_not_found' AND value > 0"
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        return {"name": "Rule 3.c: Delete Not Found", "status": "PASS", "message": "No 'Delete Not Found' events detected."}

    total_dnf = df['value'].sum()
    formatted_dnf = "{:,}".format(int(total_dnf)) # Adds the commas
    
    status = "WARNING" if total_dnf > 1000000 else "INFO"
    
    return {
        "name": "Rule 3.c: Delete Not Found",
        "status": status,
        "message": f"Detected {formatted_dnf} 'Delete Not Found' events across {df['node_id'].nunique()} nodes.",
        "remediation": "This suggests the application is attempting to delete records that do not exist (Blind Deletes). Review application logic."
    }
