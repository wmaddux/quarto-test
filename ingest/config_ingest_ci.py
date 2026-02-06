import sqlite3
__version__ = "1.1.0"

def run_ingest(node_id, as_stat, conn, run_id):
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS node_configs (run_id TEXT, node_id TEXT, namespace TEXT, config_name TEXT, value TEXT)")
    
    config_root = as_stat.get('config', {})
    
    count = 0
    def flatten_and_insert(context, prefix, data):
        nonlocal count
        for key, val in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(val, dict):
                flatten_and_insert(context, full_key, val)
            else:
                cursor.execute(
                    "INSERT INTO node_configs (run_id, node_id, namespace, config_name, value) VALUES (?, ?, ?, ?, ?)",
                    (run_id, node_id, context, full_key, str(val))
                )
                count += 1

    for context, settings in config_root.items():
        if isinstance(settings, dict):
            flatten_and_insert(context, "", settings)
            
    conn.commit()
    print(f"✅ Configs: Ingested {count} settings for {node_id}")
