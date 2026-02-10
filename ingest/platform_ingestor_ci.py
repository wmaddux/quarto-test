import sqlite3
from ingest.base_ingestor import BaseIngestor

class PlatformIngestor(BaseIngestor):
    @property
    def name(self):
        return "Platform Discovery"

    def run_ingest(self, node_id, node_data, conn, run_id):
        # 1. Access the config block (since sys_stat is empty in this bundle)
        as_stat = node_data.get('as_stat', {})
        config_block = as_stat.get('config', {})
        
        # 2. Stringify everything we have for a broad search
        search_bucket = (str(config_block) + str(node_id)).lower()
        
        platform = "Bare Metal / On-Prem"

        # 3. Detection Pivot:
        # Since we can't see drivers, we look for region codes and IP patterns
        # 'va7' is a strong indicator of Azure Virginia regions in your naming convention.
        if any(x in search_bucket for x in ["azure", "microsoft", "_va", "10.181."]):
            platform = "Azure"
        elif any(x in search_bucket for x in ["aws", "amazon", "ec2", "172.31."]):
            platform = "AWS"
        elif any(x in search_bucket for x in ["google", "gce", "10.128."]):
            platform = "GCP"

        # 4. Save to DB
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO cluster_metadata (key, value) VALUES (?, ?)",
            ("cloud_platform", platform)
        )
        conn.commit()
        print(f"✅ {self.name}: Identified as {platform} (via Config/Network fingerprinting)")