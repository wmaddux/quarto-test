import sqlite3
from ingest.base_ingestor import BaseIngestor

# -----------------------------------------------------------------------------
# VERSION STAMP
# -----------------------------------------------------------------------------
__version__ = "1.6.0"

# --- Metadata ---
# Module: MetadataIngestor
# Purpose: Cluster-wide flavor discovery (Cloud, Storage, Consistency)
# Target: cluster_metadata table

class MetadataIngestor(BaseIngestor):
    @property
    def name(self):
        return "Metadata & Flavor Discovery"

    def run_ingest(self, node_id, node_data, conn, run_id):
        # -------------------------------------------------------------------------
        # DATA EXTRACTION
        # -------------------------------------------------------------------------
        as_stat = node_data.get('as_stat', {})
        config = as_stat.get('config', {})
        stats = as_stat.get('statistics', {}).get('service', {})
        meta = as_stat.get('meta_data', {}) # New for 7.x
        
        # -------------------------------------------------------------------------
        # FLAVOR DISCOVERY LOGIC
        # -------------------------------------------------------------------------
        
        # 1. Version Flavor (Hardened for 7.x meta_data block)
        version_str = meta.get('asd_build') or stats.get('asd_build', "Unknown")
        major_v = version_str.split('.')[0] if version_str != "Unknown" else "Unknown"

        # 2. Extract Namespaces
        ns_configs = config.get('namespace', {}) # Note: 'namespace' singular in your JSON

        # 3. Consistency Flavor
        is_sc = False
        for ns_conf in ns_configs.values():
            svc_conf = ns_conf.get('service', {})
            if str(svc_conf.get('strong-consistency', 'false')).lower() == 'true':
                is_sc = True
                break
        consistency = "Strong Consistency (SC)" if is_sc else "Available/Partition-Tolerant (AP)"

        # 4. Storage Flavor (Hardened for your specific DEVICE string)
        storage_types = set()
        for ns_conf in ns_configs.values():
            svc_conf = ns_conf.get('service', {})
            se = svc_conf.get('storage-engine')
            
            if isinstance(se, str):
                se_lower = se.lower()
                if 'device' in se_lower: storage_types.add("DEVICE")
                elif 'file' in se_lower: storage_types.add("FILE")
                else: storage_types.add("MEMORY")
            elif isinstance(se, dict):
                if any(k in se for k in ['devices', 'device']): storage_types.add("DEVICE")
                elif any(k in se for k in ['files', 'file']): storage_types.add("FILE")
                else: storage_types.add("MEMORY")
            else:
                storage_types.add("MEMORY")

        storage_flavor = "/".join(sorted(storage_types)) if storage_types else "MEMORY"

        # 5. Platform Flavor (catching naming conventions like va6prod)
        full_context = str(node_data).lower()
        platform = "Bare Metal / On-Prem"
        if any(x in full_context for x in ["amazonaws", "ec2.internal", "10.94."]): 
            platform = "AWS"
        elif any(x in full_context for x in ["azure", "cloudapp", "10.181."]): 
            platform = "Azure"

        # 6. Topology Discovery
        is_xdr = len(as_stat.get('statistics', {}).get('xdr', {})) > 0
        topology = "XDR Enabled" if is_xdr else "Standalone"

        # -------------------------------------------------------------------------
        # DATABASE UPDATE
        # -------------------------------------------------------------------------
        cursor = conn.cursor()
        meta_items = [
            ("server_version", version_str), 
            ("major_version", major_v),
            ("cloud_platform", platform), 
            ("consistency_model", consistency),
            ("storage_flavor", storage_flavor), 
            ("topology", topology)
        ]
        for key, val in meta_items:
            cursor.execute("INSERT OR REPLACE INTO cluster_metadata (key, value) VALUES (?, ?)", (key, val))
        
        conn.commit()

        print(f"✅ {self.name}: Identified as {platform} | {consistency} | {storage_flavor}")