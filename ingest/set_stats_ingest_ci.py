import sqlite3

# -----------------------------------------------------------------------------
# VERSION STAMP
# -----------------------------------------------------------------------------
__version__ = "1.6.0"

class SetStatsIngestor:
    """
    Processes Aerospike 7.x set metrics using the standard Vertical Schema.
    Aligned with INGEST-TEMPLATE.md requirements.
    """
    def run_ingest(self, node_id, node_data, conn, run_id):
        cursor = conn.cursor()

        # 1. Ensure Table Exists (Matches existing vertical schema)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS set_stats (
                node_id TEXT, 
                ns TEXT, 
                set_name TEXT, 
                key TEXT, 
                value TEXT, 
                run_id TEXT,
                PRIMARY KEY (node_id, ns, set_name, key, run_id)
            )
        """)

        # 2. Navigate hierarchy: as_stat -> statistics -> set
        set_data = node_data.get("as_stat", {}).get("statistics", {}).get("set", {})
        
        # 3. Extract and Persist using the Vertical (Key/Value) pattern
        for ns_name, sets in set_data.items():
            for set_name, metrics in sets.items():
                for key, val in metrics.items():
                    cursor.execute("""
                        INSERT OR REPLACE INTO set_stats (node_id, ns, set_name, key, value, run_id)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (node_id, ns_name, set_name, key, str(val), run_id))