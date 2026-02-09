import sqlite3
__version__ = "1.4.0"

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Monitor 'client_write_error_key_busy' for non-zero values
    query = """
    SELECT node_id, namespace, value 
    FROM namespace_stats 
    WHERE metric = 'client_write_error_key_busy' AND value > 0
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return {
            "id": "4.a", "name": "Hot Key Detection", 
            "status": "PASS", 
            "message": "No 'key busy' errors detected in this snapshot."
        }

    findings = [f"{r['namespace']} on {r['node_id']} (Count: {int(r['value'])})" for r in rows]
    return {
        "id": "4.a", "name": "Hot Key Detection",
        "status": "WARNING",
        "message": f"Hot keys detected: {', '.join(findings)}",
        "remediation": "Investigate application access patterns for high-frequency keys. Consider increasing transaction-pending-limit if this is expected traffic."
    }
