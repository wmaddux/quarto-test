import sqlite3

class NodeStatsIngestor:
    def __init__(self):
        self.table_name = "node_stats"

    def flatten_dict(self, d, parent_key='', sep='.'):
        """Recursively flattens nested Aerospike 7.x JSON."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def run_ingest(self, node_id, data, conn, run_id):
        cursor = conn.cursor()
        
        # Ensure the table can store both Numbers and Strings
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                run_id TEXT,
                node_id TEXT,
                metric TEXT,
                value TEXT
            )
        """)

        # Aerospike 7.x data is often nested under 'statistics' or 'service'
        # We flatten everything to catch 'service.build', 'service.version', etc.
        flat_data = self.flatten_dict(data)

        insert_items = []
        for key, value in flat_data.items():
            if value is None:
                continue
            
            # We store everything as TEXT in the DB to ensure 
            # versions like 'E-7.2.0.6' aren't dropped. 
            # The Rules will handle casting to REAL/FLOAT when needed.
            insert_items.append((run_id, node_id, key, str(value)))

        cursor.executemany(
            f"INSERT INTO {self.table_name} (run_id, node_id, metric, value) VALUES (?, ?, ?, ?)",
            insert_items
        )
        conn.commit()