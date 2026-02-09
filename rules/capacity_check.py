import sqlite3
__version__ = "1.4.0"

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Query for disk and memory usage across all namespaces
    query = """
    SELECT node_id, namespace, metric, value 
    FROM namespace_stats 
    WHERE metric IN ('data_used_pct', 'indexes_memory_used_pct')
    AND value > 70
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return {
            "name": "Capacity Check",
            "status": "PASS",
            "message": "All namespaces are well below utilization thresholds."
        }

    # If we found issues, format the findings
    findings = [f"{row['namespace']} on {row['node_id']} is at {row['value']}% {row['metric']}" for row in rows]
    
    return {
        "name": "Capacity Check",
        "status": "WARNING",
        "message": "High utilization detected: " + " | ".join(findings),
        "remediation": "Consider increasing capacity or adjusting the high-water-mark if eviction is desired."
    }
