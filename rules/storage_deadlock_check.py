import sqlite3
__version__ = "1.3.0"

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # We need to compare two different metrics for the same namespace/node
    query = """
    SELECT 
        a.node_id, 
        a.namespace, 
        a.value as hwm_disk, 
        b.value as defrag_lwm
    FROM namespace_stats a
    JOIN namespace_stats b 
      ON a.node_id = b.node_id 
      AND a.namespace = b.namespace
    WHERE a.metric = 'high-water-disk-pct' 
      AND b.metric = 'defrag-lwm-pct'
      AND b.value <= a.value
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return {
            "id": "2.c", "name": "Storage Deadlock Risk",
            "status": "PASS",
            "message": "Defragmentation thresholds are correctly set above eviction marks."
        }

    findings = [f"{r['namespace']} on {r['node_id']} (HWM:{r['hwm_disk']}% >= Defrag:{r['defrag_lwm']}%)" for r in rows]
    
    return {
        "name": "Storage Deadlock Risk",
        "status": "CRITICAL",
        "message": "Potential Deadlock: Eviction threshold is higher than or equal to Defrag LWM: " + " | ".join(findings),
        "remediation": "Increase 'defrag-lwm-pct' or decrease 'high-water-disk-pct'. Defrag must be more aggressive than eviction to ensure free blocks are always available."
    }
