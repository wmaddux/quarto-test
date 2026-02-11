__version__ = "1.5.4"
from ingest.base_ingestor import BaseIngestor

class SystemInfoIngestor(BaseIngestor):
    @property
    def name(self):
        return "System Info"

    def run_ingest(self, node_id, node_data, conn, run_id):
        # System info lives in a peer object to as_stat
        sys_info = node_data.get('sys_stat', {})
        if not sys_info:
            return

        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_info (
                run_id TEXT, 
                node_id TEXT, 
                metric TEXT, 
                value TEXT
            )
        """)

        for metric, value in sys_info.items():
            # System info is often strings (e.g., "instance-type": "m5.large")
            cursor.execute(
                "INSERT INTO system_info VALUES (?, ?, ?, ?)",
                (run_id, node_id, metric, str(value))
            )
        
        print(f"✅ {self.name}: Ingested for {node_id}")