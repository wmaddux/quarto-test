__version__ = "1.6.0"
from ingest.base_ingestor import BaseIngestor

class ConfigIngestor(BaseIngestor):
    """
    Parses Aerospike configuration telemetry. 
    Handles the nested structure of Aerospike 7.x and flattens it 
    into a key-value schema compatible with health rules.
    """

    @property
    def name(self):
        return "Configs"

    def run_ingest(self, node_id, node_data, conn, run_id):
        as_stat = node_data.get('as_stat', {})
        
        # In Aerospike 7.x, configs are grouped in a dedicated 'config' block.
        # Fallback to as_stat for legacy versions.
        config_data = as_stat.get('config', as_stat)
        
        cursor = conn.cursor()
        
        # The 'source' column is required by rules like config_drift_check.py
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS node_configs (
                run_id TEXT, 
                node_id TEXT, 
                config_name TEXT, 
                value TEXT, 
                source TEXT
            )
        """)

        def flatten_configs(data, prefix=""):
            """
            Recursively traverses the config dictionary to create 
            dot-notated keys (e.g., 'service.proto-fd-max').
            """
            for k, v in data.items():
                # Avoid re-parsing metadata or statistics if we fell back to as_stat
                if prefix == "" and k in ['statistics', 'meta_data', 'histogram', 'latency']:
                    continue

                full_key = f"{prefix}.{k}" if prefix else k
                
                if isinstance(v, dict):
                    flatten_configs(v, full_key)
                else:
                    # We default source to 'config' to distinguish from 'file' 
                    # sources in future drift analysis.
                    cursor.execute(
                        "INSERT INTO node_configs VALUES (?, ?, ?, ?, ?)",
                        (run_id, node_id, full_key, str(v), 'config')
                    )

        flatten_configs(config_data)
        print(f"✅ {self.name} processed for {node_id}")