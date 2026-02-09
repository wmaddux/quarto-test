__version__ = "1.4.0"
from ingest.base_ingestor import BaseIngestor

class NamespaceStatsIngestor(BaseIngestor):
    @property
    def name(self): return "Namespace Stats"

    def run_ingest(self, node_id, node_data, conn, run_id):
        as_stat = node_data.get('as_stat', {})
        ns_container = as_stat.get('statistics', {}).get('namespace', as_stat.get('namespaces', {}))

        if not ns_container: return
        
        cursor = conn.cursor()
        # Added 'source' column
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS namespace_stats 
            (run_id TEXT, node_id TEXT, namespace TEXT, metric TEXT, value REAL, source TEXT)
        """)
        
        for ns_name, ns_data in ns_container.items():
            metrics = ns_data.get('service', ns_data) if isinstance(ns_data, dict) else {}
            for metric, value in metrics.items():
                if isinstance(value, (int, float, str)) and str(value).replace('.','',1).isdigit():
                    m_name = f"service.{metric}" if not metric.startswith('service.') else metric
                    cursor.execute("INSERT INTO namespace_stats VALUES (?, ?, ?, ?, ?, ?)",
                                   (run_id, node_id, ns_name, m_name, float(value), 'statistics'))
        print(f"✅ {self.name} processed for {node_id}")