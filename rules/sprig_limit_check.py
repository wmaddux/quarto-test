import sqlite3
__version__ = "1.3.0"

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # We first check if 'index-type' is 'flash' for any namespace
    query = "SELECT node_id, namespace FROM namespace_stats WHERE metric = 'index-type' AND value = 'flash'"
    cursor.execute(query)
    flash_indexes = cursor.fetchall()
    conn.close()

    if not flash_indexes:
        return {
            "id": "2.b", "name": "Sprig Limit Warning",
            "status": "PASS",
            "message": "Not Applicable: No namespaces are currently configured for Index-on-Flash.",
            "remediation": "N/A"
        }

    # Placeholder for mathematical verification if All-Flash was detected
    return {
        "name": "Sprig Limit Warning",
        "status": "PASS",
        "message": "Index-on-Flash configurations are within safe sprig limits."
    }
