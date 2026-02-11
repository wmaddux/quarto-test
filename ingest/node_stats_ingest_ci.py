import sqlite3

# -----------------------------------------------------------------------------
# VERSION STAMP
# -----------------------------------------------------------------------------
__version__ = "1.5.4"

# --- Metadata ---
# Module: NodeStatsIngestor
# Purpose: Recursively flattens and ingests node-level statistics/service metrics
# Target: node_stats table (Schema: run_id, node_id, metric, value)

class NodeStatsIngestor:
    def __init__(self):
        self.table_name = "node_stats"

    def flatten_dict(self, d, parent_key='', sep='.'):
        """
        Recursively flattens nested Aerospike 7.x JSON.
        Converts nested structures into dot-notated metric keys.
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def run_ingest(self, node_id, data, conn, run_id):
        # -------------------------------------------------------------------------
        # TABLE INITIALIZATION
        # -------------------------------------------------------------------------
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

        # -------------------------------------------------------------------------
        # DATA PROCESSING
        # -------------------------------------------------------------------------
        # Aerospike 7.x data is often nested under 'statistics' or 'service'
        # We flatten everything to catch 'service.build', 'service.version', etc.
        flat_data = self.flatten_dict(data)

        insert_items = []
        for key, value in flat_data.items():
            if value is None:
                continue
            
            # ---------------------------------------------------------------------
            # TYPE HANDLING
            # ---------------------------------------------------------------------
            # We store everything as TEXT in the DB to ensure version strings
            # and build numbers (e.g., 'E-7.2.0.6') aren't truncated or lost.
            # Rules handle casting to REAL/FLOAT for mathematical comparisons.
            insert_items.append((run_id, node_id, key, str(value)))

        # -------------------------------------------------------------------------
        # BATCH INGESTION
        # -------------------------------------------------------------------------
        cursor.executemany(
            f"INSERT INTO {self.table_name} (run_id, node_id, metric, value) VALUES (?, ?, ?, ?)",
            insert_items
        )
        conn.commit()