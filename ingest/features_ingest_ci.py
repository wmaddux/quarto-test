__version__ = "1.6.0"
from ingest.base_ingestor import BaseIngestor

class FeaturesIngestor(BaseIngestor):
    @property
    def name(self):
        return "Feature Discovery"

    def run_ingest(self, node_id, node_data, conn, run_id):
        as_stat = node_data.get('as_stat', {})
        stats = as_stat.get('statistics', {})
        configs = as_stat.get('config', {})
        
        # Aerospike 7.2.x Specific Path Mapping
        service_stats = stats.get('service', {})
        ns_stats = stats.get('namespace', {})
        security_configs = configs.get('security', {})
        network_configs = configs.get('network', {})
        ns_configs = configs.get('namespace', {})

        active = set()

        def stat_gt(block, keys, threshold=0):
            if not block: return False
            for k in keys:
                try:
                    val = block.get(k, 0)
                    if val is not None and float(val) > threshold:
                        return True
                except (ValueError, TypeError):
                    continue
            return False

        # 1. KVS (Service Stats)
        if stat_gt(service_stats, ['stat_read_reqs', 'stat_write_reqs']):
            active.add("KVS")
        
        # 2. Batch (Service Stats)
        if stat_gt(service_stats, ['batch_initiate', 'batch_index_initiate']):
            active.add("Batch")

        # 3. UDF (Service Stats)
        if stat_gt(service_stats, ['udf_read_reqs', 'udf_write_reqs']):
            active.add("UDF")

        # 4. Scan (Service Stats)
        scan_service_keys = [
            'tscan_initiate', 'basic_scans_success', 'aggr_scans_success', 'udf_bg_scans_success'
        ]
        if stat_gt(service_stats, scan_service_keys):
            active.add("Scan")

        # 5. Query (Service Stats)
        if stat_gt(service_stats, ['query_reqs', 'query_success']):
            active.add("Query")

        # 6. SIndex (Service Stats)
        if stat_gt(service_stats, ['sindex-used-bytes-memory']):
            active.add("SIndex")

        # 7. XDR (Service Stats / Config)
        if stat_gt(service_stats, ['stat_read_reqs_xdr', 'xdr_read_success', 'stat_write_reqs_xdr']):
            active.add("XDR")
        if 'xdr' in configs:
            active.add("XDR")

        # 8. Rack-aware (Service Stats)
        try:
            if float(service_stats.get('self-group-id', 0)) > 0:
                active.add("Rack-aware")
        except: pass

        # 9. Security (Config)
        if str(security_configs.get('enable-security', '')).lower() == 'true':
            active.add("Security")

        # 10. TLS (Network Configs)
        if float(network_configs.get('service', {}).get('tls-port', 0)) > 0: active.add("TLS")
        if float(network_configs.get('fabric', {}).get('tls-port', 0)) > 0: active.add("TLS")

        # 11. Namespace-level Discovery
        for ns_name, ns_data in ns_stats.items():
            ns_svc_stats = ns_data.get('service', {})
            # In 7.2.x, ns config keys are nested in a 'service' block
            ns_full_cfg = ns_configs.get(ns_name, {})
            ns_svc_cfg = ns_full_cfg.get('service', {})

            # KVS (Namespace Stats)
            if stat_gt(ns_svc_stats, ['client_read_success', 'client_write_success']):
                active.add("KVS")
            
            # UDF (Namespace Stats)
            if stat_gt(ns_svc_stats, ['client_udf_complete', 'client_udf_error']):
                active.add("UDF")

            # PIndex / SIndex Query
            if stat_gt(ns_svc_stats, [k for k in ns_svc_stats.keys() if k.startswith('pi_query_')]):
                active.add("PIndex Query")
            if stat_gt(ns_svc_stats, [k for k in ns_svc_stats.keys() if k.startswith('si_query_')]):
                active.add("SIndex Query")

            # Rack-aware (Namespace Config)
            try:
                if float(ns_svc_cfg.get('rack-id', 0)) > 0:
                    active.add("Rack-aware")
            except: pass

            # Strong Consistency (Namespace Config)
            if str(ns_svc_cfg.get('strong-consistency', '')).lower() == 'true':
                active.add("SC")

            # Index-on-flash (Namespace Config or Stats)
            if ns_svc_cfg.get('index-type') == 'flash' or \
               stat_gt(ns_svc_stats, ['index_flash_used_bytes', 'index_flash_alloc_bytes']):
                active.add("Index-on-flash")

        # --- Database Insertion ---
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS active_features (run_id TEXT, node_id TEXT, feature TEXT)")
        for feature in active:
            cursor.execute("INSERT INTO active_features VALUES (?, ?, ?)", (run_id, node_id, feature))
        
        print(f"✅ {self.name} processed for {node_id} ({len(active)} features discovered)")