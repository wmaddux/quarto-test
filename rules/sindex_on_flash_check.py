import sqlite3
__version__ = "1.1.0"

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Query for namespaces with sindexes where index-type is not 'flash'
    query = """
    SELECT node_id, namespace 
    FROM namespace_stats 
    WHERE metric = 'sindex_type' AND value != 'flash'
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return {
            "name": "SIndex on Flash", 
            "status": "PASS", 
            "message": "Secondary indexes are optimized on Flash or not present."
        }

    findings = [f"{r['namespace']} on {r['node_id']}" for r in rows]
    return {
        "name": "SIndex on Flash",
        "status": "INFO",
        "message": f"Secondary indexes detected in RAM: {', '.join(findings)}",
        "remediation": "If running Aerospike 7.2+, consider moving secondary indexes to Flash to reduce RAM consumption."
    }
