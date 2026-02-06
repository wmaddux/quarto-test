#!/usr/bin/env python3
import sqlite3
import tarfile
import json
import gzip
import zipfile
import io
import os
import sys

# These are the files in your ingest/ folder
import ingest.node_stats_ingest_ci as node_stats
import ingest.namespace_stats_ingest_ci as ns_stats
import ingest.config_ingest_ci as config_ingest

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
    print(f"🚀 Processing: {input_path}")
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

    # Aerospike JSON hierarchy: Timestamp -> Cluster -> Node -> as_stat
    for timestamp, clusters in data.items():
        for cluster_name, nodes in clusters.items():
            for node_id, node_data in nodes.items():
                
                as_stat = node_data.get('as_stat', {})
                
                if as_stat:
                    # Debug trace to confirm we have the payload
                    print(f"DEBUG: Processing Node {node_id}")
                    
                    # 1. Ingest general service metrics (cluster size, connections)
                    node_stats.run_ingest(node_id, as_stat, conn, timestamp)
                    
                    # 2. Ingest namespace metrics (Rule 3.c - DNF check)
                    ns_stats.run_ingest(node_id, as_stat, conn, timestamp)
                    
                    # 3. Ingest configurations (Rule 4.b - Symmetry check)
                    config_ingest.run_ingest(node_id, as_stat, conn, timestamp)
                else:
                    print(f"⚠️ No as_stat for {node_id}")

    conn.commit()
    conn.close()
    print(f"✅ Ingestion complete.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_collectinfo(sys.argv[1])
    else:
        print("Usage: ./ingest_manager.py <bundle.tgz>")
