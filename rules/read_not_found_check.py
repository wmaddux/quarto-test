import sqlite3
import pandas as pd
__version__ = "1.4.0"

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    # Correct Aerospike 7.2 path
    query = "SELECT node_id, value FROM namespace_stats WHERE metric = 'service.client_read_not_found' AND value > 0"
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        return {"name": "Rule 3.a: Read Not Found", "status": "PASS", "message": "No 'Read Not Found' events detected."}

    total_rnf = df['value'].sum()
    formatted_rnf = "{:,}".format(int(total_rnf))
    
    return {
        "id": "4.b", "name": "Read Not Found",
        "status": "INFO",
        "message": f"Detected {formatted_rnf} 'Read Not Found' events. This is often normal for application cache-miss workflows.",
        "remediation": "If the application expects all records to exist, investigate potential expiration or eviction issues."
    }
