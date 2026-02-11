import sqlite3
from ingest.base_ingestor import BaseIngestor

class PlatformIngestor(BaseIngestor):
    @property
    def name(self):
        return "Platform Discovery"

    def run_ingest(self, node_id, node_data, conn, run_id):
        # 1. Access both config and stats blocks
        as_stat = node_data.get('as_stat', {})
        config_block = as_stat.get('config', {})
        stats_block = as_stat.get('statistics', {})
        
        # 2. Build the search bucket
        search_bucket = (str(config_block) + str(stats_block) + str(node_id)).lower()
        
        platform = "Bare Metal / On-Prem"

        # 3. HIGH CONFIDENCE DETECTION (Explicit Cloud Identifiers)
        if any(x in search_bucket for x in ["amazonaws.com", "ec2.internal", "ami-id", "aws-"]):
            platform = "AWS"
        elif any(x in search_bucket for x in ["azure.com", "cloudapp.net", "hv_vmbus", "microsoft"]):
            platform = "Azure"
        elif any(x in search_bucket for x in ["googleapis.com", "gce.internal", "google-managed"]):
            platform = "GCP"
            
        # 4. LOW CONFIDENCE FALLBACK (Naming Conventions / IPs)
        # Only check these if the above didn't find a match
        if platform == "Bare Metal / On-Prem":
            if "10.181." in search_bucket or "_va7" in search_bucket:
                platform = "Azure"
            elif "10.94." in search_bucket or "us-east-" in search_bucket:
                platform = "AWS"

        # 5. Save to DB
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO cluster_metadata (key, value) VALUES (?, ?)",
            ("cloud_platform", platform)
        )
        conn.commit()
        print(f"✅ {self.name}: Identified as {platform}")