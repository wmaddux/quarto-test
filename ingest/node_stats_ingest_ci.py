__version__ = "1.4.0"
from ingest.base_ingestor import BaseIngestor

class NodeStatsIngestor(BaseIngestor):
    @property
    def name(self): return "Node Stats"

    def run_ingest(self, node_id, node_data, conn, run_id):
        as_stat = node_data.get('as_stat', {})
        service_stats = as_stat.get('statistics', {}).get('service', as_stat)
        
        cursor = conn.cursor()
        # Added 'source' column
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS node_stats 
            (run_id TEXT, node_id TEXT, metric TEXT, value REAL, source TEXT)
        """)
        
        for metric, value in service_stats.items():
            if isinstance(value, (int, float, str)) and str(value).replace('.','',1).isdigit():
                m_name = f"service.{metric}" if not metric.startswith('service.') else metric
                cursor.execute("INSERT INTO node_stats VALUES (?, ?, ?, ?, ?)", 
                               (run_id, node_id, m_name, float(value), 'statistics'))
        print(f"✅ {self.name} processed for {node_id}")