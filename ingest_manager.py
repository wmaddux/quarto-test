#!/usr/bin/env python3
import sqlite3
import tarfile
import json
import gzip
import zipfile
import io
import os
import sys

# Incremented for v1.3.0 backlog
__version__ = "1.3.0"

# Existing ingest modules
import ingest.node_stats_ingest_ci as node_stats
import ingest.namespace_stats_ingest_ci as ns_stats
import ingest.config_ingest_ci as config_ingest

# New module for System/Network telemetry
# You will create this file in the next step
import ingest.system_info_ingest_ci as sys_ingest

def get_json_content(tar, member):
    """Handles the nested archive layers of Aerospike collectinfo."""
    f_bytes = tar.extractfile(member).read()
    if member.name.endswith('.zip'):
        with zipfile.ZipFile(io.BytesIO(f_bytes)) as z:
            f_bytes = z.read(z.namelist()[0])
    if f_bytes.startswith(b'\x1f\x8b'):
        f_bytes = gzip.decompress(f_bytes)
    return json.loads(f_bytes.decode('utf-8'))

def process_collectinfo(input_path, db_path="aerospike_health.db"):
    print(f"🚀 Processing v{__version__}: {input_path}")
    conn = sqlite3.connect(db_path)
    
    try:
        with tarfile.open(input_path, "r:*") as tar:
            target = next((m for m in tar.getmembers() if "ascinfo.json" in m.name), None)
            if not target:
                print("❌ No ascinfo.json found.")
                return
            data = get_json_content(tar, target)
    except Exception as e:
        print(f"💥 Extraction Error: {e}")
        return

    # Aerospike JSON hierarchy: Timestamp -> Cluster -> Node -> (as_stat, sys_stat)
    for timestamp, clusters in data.items():
        for cluster_name, nodes in clusters.items():
            for node_id, node_data in nodes.items():
                
                # Aerospike specific statistics
                as_stat = node_data.get('as_stat', {})
                # OS/Hardware level statistics (where ENA info resides)
                sys_stat = node_data.get('sys_stat', {})
                
                print(f"DEBUG: Processing Node {node_id}")

                # 1. Ingest standard Aerospike metrics
                if as_stat:
                    node_stats.run_ingest(node_id, as_stat, conn, timestamp)
                    ns_stats.run_ingest(node_id, as_stat, conn, timestamp)
                    config_ingest.run_ingest(node_id, as_stat, conn, timestamp)
                else:
                    print(f"⚠️ No as_stat for {node_id}")

                # 2. Ingest System/Network data for Rule 1.b (ENA Check)
                if sys_stat:
                    sys_ingest.run_ingest(node_id, sys_stat, conn, timestamp)
                else:
                    print(f"⚠️ No sys_stat for {node_id}")

    conn.commit()
    conn.close()
    print(f"✅ Ingestion complete. Database v{__version__} ready.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_collectinfo(sys.argv[1])
    else:
        print(f"Aerospike Health Ingestor v{__version__}")
        print("Usage: ./ingest_manager.py <bundle.tgz>")