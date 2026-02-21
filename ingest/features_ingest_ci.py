__version__ = "2.0.1"
from ingest.base_ingestor import BaseIngestor

# 6.x / 7.x key synonyms: 7.x uses underscores, 6.x sometimes hyphens or different names.
# Each list is tried in order; first key with value > threshold wins.
SERVICE_KVS_KEYS = ['stat_read_reqs', 'stat-read-reqs', 'stat_write_reqs', 'stat-write-reqs', 'client_connections']
SERVICE_BATCH_KEYS = ['batch_initiate', 'batch-initiate', 'batch_index_initiate', 'batch_index_complete']
SERVICE_UDF_KEYS = ['udf_read_reqs', 'udf-read-reqs', 'udf_write_reqs', 'udf-write-reqs']
SERVICE_SCAN_KEYS = ['tscan_initiate', 'tscan-initiate', 'basic_scans_success', 'aggr_scans_success', 'udf_bg_scans_success']
SERVICE_QUERY_KEYS = ['query_reqs', 'query-reqs', 'query_success', 'query-success']
SERVICE_SINDEX_KEYS = ['sindex-used-bytes-memory', 'sindex_used_bytes_memory']
SERVICE_XDR_KEYS = ['stat_read_reqs_xdr', 'stat-read-reqs-xdr', 'xdr_read_success', 'xdr-read-success', 'stat_write_reqs_xdr', 'stat-write-reqs-xdr']
NS_KVS_KEYS = ['client_read_success', 'client-read-success', 'client_write_success', 'client-write-success']
NS_UDF_KEYS = ['client_udf_complete', 'client-udf-complete', 'client_udf_error', 'client-udf-error']
NS_INDEX_FLASH_KEYS = ['index_flash_used_bytes', 'index-flash-used-bytes', 'index_flash_alloc_bytes', 'index-flash-alloc-bytes']

class FeaturesIngestor(BaseIngestor):
    @property
    def name(self):
        return "Feature Discovery"

    def run_ingest(self, node_id, node_data, conn, run_id):
        as_stat = node_data.get('as_stat', {})
        stats = as_stat.get('statistics', {})
        configs = as_stat.get('config', {})
        # 6.x: namespace may be under statistics.namespace or as_stat.namespaces
        ns_stats = stats.get('namespace', {}) or as_stat.get('namespaces', {})
        service_stats = stats.get('service', {})
        security_configs = configs.get('security', {})
        network_configs = configs.get('network', {})
        ns_configs = configs.get('namespace', {})

        active = set()

        def stat_gt(block, keys, threshold=0):
            if not block or not isinstance(block, dict):
                return False
            for k in keys:
                try:
                    val = block.get(k, 0)
                    if val is None:
                        continue
                    v = float(val) if not isinstance(val, (int, float)) else val
                    if v > threshold:
                        return True
                except (ValueError, TypeError):
                    continue
            return False

        def stat_gt_any_key(block, prefix_list):
            """True if any key in block starting with any of prefix_list has value > 0 (6.x/7.x prefix variants)."""
            if not block or not isinstance(block, dict):
                return False
            for k, v in block.items():
                try:
                    val = float(v) if v is not None else 0
                except (ValueError, TypeError):
                    continue
                if val <= 0:
                    continue
                for p in prefix_list:
                    if k.startswith(p):
                        return True
            return False

        # 1. KVS (Service Stats) — 6.x may use client_connections or stat-read-reqs
        if stat_gt(service_stats, SERVICE_KVS_KEYS):
            active.add("KVS")

        # 2. Batch (Service Stats) — 6.x has batch_index_initiate, batch_index_complete
        if stat_gt(service_stats, SERVICE_BATCH_KEYS):
            active.add("Batch")

        # 3. UDF (Service Stats)
        if stat_gt(service_stats, SERVICE_UDF_KEYS):
            active.add("UDF")

        # 4. Scan (Service Stats)
        if stat_gt(service_stats, SERVICE_SCAN_KEYS):
            active.add("Scan")

        # 5. Query (Service Stats)
        if stat_gt(service_stats, SERVICE_QUERY_KEYS):
            active.add("Query")

        # 6. SIndex (Service Stats)
        if stat_gt(service_stats, SERVICE_SINDEX_KEYS):
            active.add("SIndex")

        # 7. XDR (Service Stats / Config)
        if stat_gt(service_stats, SERVICE_XDR_KEYS):
            active.add("XDR")
        if 'xdr' in configs:
            active.add("XDR")

        # 8. Rack-aware (Service Stats) — 6.x/7.x both use self-group-id
        try:
            v = service_stats.get('self-group-id') or service_stats.get('self_group_id')
            if v is not None and float(v) > 0:
                active.add("Rack-aware")
        except (ValueError, TypeError):
            pass

        # 9. Security (Config)
        if str(security_configs.get('enable-security', '') or security_configs.get('enable_security', '')).lower() == 'true':
            active.add("Security")

        # 10. TLS (Network Configs)
        svc_net = network_configs.get('service', {})
        fabric_net = network_configs.get('fabric', {})
        tls_port = svc_net.get('tls-port') or svc_net.get('tls_port') or 0
        if float(tls_port or 0) > 0:
            active.add("TLS")
        if float(fabric_net.get('tls-port') or fabric_net.get('tls_port') or 0) > 0:
            active.add("TLS")

        # 11. Namespace-level Discovery (6.x: statistics.namespace or namespaces)
        for ns_name, ns_data in (ns_stats.items() if isinstance(ns_stats, dict) else []):
            if not isinstance(ns_data, dict):
                continue
            ns_svc_stats = ns_data.get('service', ns_data)
            ns_full_cfg = ns_configs.get(ns_name, {})
            ns_svc_cfg = ns_full_cfg.get('service', {})

            if stat_gt(ns_svc_stats, NS_KVS_KEYS):
                active.add("KVS")
            if stat_gt(ns_svc_stats, NS_UDF_KEYS):
                active.add("UDF")
            if stat_gt_any_key(ns_svc_stats, ['pi_query_', 'pi-query-']):
                active.add("PIndex Query")
            if stat_gt_any_key(ns_svc_stats, ['si_query_', 'si-query-']):
                active.add("SIndex Query")
            try:
                rv = ns_svc_cfg.get('rack-id') or ns_svc_cfg.get('rack_id')
                if rv is not None and float(rv) > 0:
                    active.add("Rack-aware")
            except (ValueError, TypeError):
                pass
            if str(ns_svc_cfg.get('strong-consistency', '') or ns_svc_cfg.get('strong_consistency', '')).lower() == 'true':
                active.add("SC")
            idx_type = ns_svc_cfg.get('index-type') or ns_svc_cfg.get('index_type')
            if idx_type == 'flash' or stat_gt(ns_svc_stats, NS_INDEX_FLASH_KEYS):
                active.add("Index-on-flash")

        # --- Database Insertion --- (table created from schema/baseline.sql at ingest init)
        cursor = conn.cursor()
        for feature in active:
            cursor.execute("INSERT INTO active_features VALUES (?, ?, ?)", (run_id, node_id, feature))
        
        print(f"✅ {self.name} processed for {node_id} ({len(active)} features discovered)")