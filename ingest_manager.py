import sqlite3
import tarfile
import json
import os
import datetime
import io
import gzip
import zipfile
from ingest import INGESTORS 

__version__ = "1.6.0"

def get_json_content(tar, member):
    """Handles .json, .json.gz, and .json.zip members inside a tarball."""
    f_bytes = tar.extractfile(member).read()
    # Handle Zip wrapper (common in newer collectinfo)
    if member.name.endswith('.zip'):
        with zipfile.ZipFile(io.BytesIO(f_bytes)) as z:
            f_bytes = z.read(z.namelist()[0])
    # Handle Gzip wrapper
    if f_bytes.startswith(b'\x1f\x8b'):
        f_bytes = gzip.decompress(f_bytes)
    return json.loads(f_bytes.decode('utf-8'))

def find_telemetry_member(tar):
    """
    Dynamic Discovery: Finds the primary telemetry file.
    Filters for files containing '.json' but ignoring 'manifest'.
    Returns the largest such file, as telemetry is always the bulk of the bundle.
    """
    candidates = [
        m for m in tar.getmembers() 
        if (".json" in m.name.lower()) and ("manifest" not in m.name.lower())
    ]
    if not candidates:
        return None
    # Heuristic: The telemetry file is the largest JSON file
    return max(candidates, key=lambda m: m.size)

def process_collectinfo(input_path, db_path="aerospike_health.db"):
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS cluster_metadata (key TEXT PRIMARY KEY, value TEXT)")
    
    # Generate a run_id based on current wall clock
    run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with tarfile.open(input_path, "r:*") as tar:
        target = find_telemetry_member(tar)
        
        if not target:
            raise FileNotFoundError("Dynamic discovery failed: No telemetry JSON found in bundle.")
            
        print(f"🔍 Discovered Telemetry: {target.name} ({target.size / 1024:.2f} KB)")
        data = get_json_content(tar, target)

    # 3-LEVEL NESTED LOOP: Timestamp -> Cluster -> Node
    for timestamp, clusters in data.items():
        for cluster_name, nodes in clusters.items():
            cursor.execute("INSERT OR REPLACE INTO cluster_metadata VALUES (?, ?)", ("cluster_name", cluster_name))
            
            for node_id, node_data in nodes.items():
                print(f"📦 Processing Node: {node_id}")
                for ingestor in INGESTORS:
                    try:
                        ingestor.run_ingest(node_id, node_data, conn, run_id)
                    except Exception as e:
                        print(f"⚠️ {ingestor.__class__.__name__} failed: {e}")
    
    conn.commit()
    conn.close()