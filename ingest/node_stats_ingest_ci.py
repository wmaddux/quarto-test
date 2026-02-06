import sqlite3
__version__ = "1.1.0"

def run_ingest(node_id, as_stat, conn, run_id):
    cursor = conn.cursor()
    # Ensure table exists
    cursor.execute("CREATE TABLE IF NOT EXISTS node_stats (run_id TEXT, node_id TEXT, metric TEXT, value REAL)")
    
    # Path: as_stat -> statistics -> service
    service_root = as_stat.get('statistics', {}).get('service', {})
    
    if not isinstance(service_root, dict):
        return

    count = 0
    def flatten_and_insert(prefix, data):
        nonlocal count
        for key, val in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(val, dict):
                flatten_and_insert(full_key, val)
            else:
                try:
                    cursor.execute(
                        "INSERT INTO node_stats (run_id, node_id, metric, value) VALUES (?, ?, ?, ?)",
                        (run_id, node_id, full_key, float(val))
                    )
                    count += 1
                except (ValueError, TypeError):
                    continue

    flatten_and_insert("service", service_root)
    conn.commit()
    print(f"✅ Node Stats: Ingested {count} metrics for {node_id}")
