import sqlite3
__version__ = "1.2.0"

def run_ingest(node_id, as_stat, conn, run_id):
    cursor = conn.cursor()
    
    # ADD THIS LINE: Ensure the table exists before any logic runs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS namespace_stats 
        (run_id TEXT, node_id TEXT, namespace TEXT, metric TEXT, value REAL)
    """)
    
    stats_root = as_stat.get('statistics', {})
    namespaces = stats_root.get('namespace', {})
    
    if not isinstance(namespaces, dict):
        return

    total_count = 0

    def flatten_and_insert(ns_name, prefix, data):
        nonlocal total_count
        for key, val in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(val, dict):
                flatten_and_insert(ns_name, full_key, val)
            else:
                try:
                    numeric_val = float(val)
                    cursor.execute(
                        "INSERT INTO namespace_stats (run_id, node_id, namespace, metric, value) VALUES (?, ?, ?, ?, ?)",
                        (run_id, node_id, ns_name, full_key, numeric_val)
                    )
                    total_count += 1
                except (ValueError, TypeError):
                    continue

    for ns_name, metrics in namespaces.items():
        if isinstance(metrics, dict):
            flatten_and_insert(ns_name, "", metrics)
    
    conn.commit()
    if total_count > 0:
        print(f"✅ Namespace Stats: Ingested {total_count} metrics for {node_id}")
