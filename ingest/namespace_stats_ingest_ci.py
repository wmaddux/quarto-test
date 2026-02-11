__version__ = "1.4.0"
from ingest.base_ingestor import BaseIngestor

class NamespaceStatsIngestor(BaseIngestor):
    @property
    def name(self): return "Namespace & Set Stats"

    def run_ingest(self, node_id, node_data, conn, run_id):
        as_stat = node_data.get('as_stat', {})
        cursor = conn.cursor()

        # --- PART 1: Namespace Stats (Existing Logic) ---
        ns_container = as_stat.get('statistics', {}).get('namespace', as_stat.get('namespaces', {}))

        if ns_container:
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

        # --- PART 2: Set Stats (New logic for Rule 4.f) ---
        # Path for 7.x: as_stat -> statistics -> set -> <ns> -> <set>
        set_container = as_stat.get('statistics', {}).get('set', {})
        
        if set_container:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS set_stats 
                (node_id TEXT, ns TEXT, set_name TEXT, key TEXT, value TEXT, run_id TEXT,
                 PRIMARY KEY (node_id, ns, set_name, key, run_id))
            """)
            
            for ns_name, sets in set_container.items():
                for set_name, set_metrics in sets.items():
                    for key, val in set_metrics.items():
                        cursor.execute("""
                            INSERT OR REPLACE INTO set_stats (node_id, ns, set_name, key, value, run_id) 
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (node_id, ns_name, set_name, key, str(val), run_id))

        conn.commit()
        print(f"✅ {self.name} processed for {node_id}")