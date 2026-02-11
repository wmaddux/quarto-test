__version__ = "1.4.0"
#!/usr/bin/env python3
import sqlite3
import tarfile
import json
import os
import sys
import datetime
import io
import gzip
import zipfile

# ONLY import the registry from the package. 
# Do NOT import individual classes here or re-define INGESTORS.
from ingest import INGESTORS 

def get_json_content(tar, member):
    # ... (Keep existing implementation)
    f_bytes = tar.extractfile(member).read()
    if member.name.endswith('.zip'):
        with zipfile.ZipFile(io.BytesIO(f_bytes)) as z:
            f_bytes = z.read(z.namelist()[0])
    if f_bytes.startswith(b'\x1f\x8b'):
        f_bytes = gzip.decompress(f_bytes)
    return json.loads(f_bytes.decode('utf-8'))

def process_collectinfo(input_path, db_path="aerospike_health.db"):
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Initialize Core Tables
    cursor.execute("CREATE TABLE IF NOT EXISTS cluster_metadata (key TEXT PRIMARY KEY, value TEXT)")
    
    # Ensure set_stats exists at the start
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS set_stats (
            node_id TEXT, ns TEXT, set_name TEXT, key TEXT, value TEXT, run_id TEXT,
            PRIMARY KEY (node_id, ns, set_name, key, run_id)
        )
    """)
    
    run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with tarfile.open(input_path, "r:*") as tar:
        target = next((m for m in tar.getmembers() if "ascinfo.json" in m.name), None)
        data = get_json_content(tar, target)

    for timestamp, clusters in data.items():
        for cluster_name, nodes in clusters.items():
            cursor.execute("INSERT OR REPLACE INTO cluster_metadata VALUES (?, ?)", ("cluster_name", cluster_name))
            
            for node_id, node_data in nodes.items():
                print(f"\n🔍 Inspecting Node: {node_id}")
                
                # 1. Capture Global Version Metadata
                as_stat = node_data.get('as_stat', {})
                asd_build = as_stat.get('meta_data', {}).get('asd_build')
                if asd_build:
                    cursor.execute("INSERT OR REPLACE INTO cluster_metadata VALUES (?, ?)", 
                                   ("server_version", f"E-{asd_build}"))

                # 2. Run Plugins (This now uses the correct 5-item list)
                for ingestor in INGESTORS:
                    try:
                        ingestor.run_ingest(node_id, node_data, conn, run_id)
                    except Exception as e:
                        print(f"⚠️ {ingestor.name} failed: {e}")

    conn.commit()
    conn.close()
    print("✅ Ingestion modularly completed.")