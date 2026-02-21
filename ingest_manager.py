import sqlite3
import tarfile
import json
import os
import datetime
import io
import gzip
import zipfile
from ingest import INGESTORS 

__version__ = "2.0.1"

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

def find_aerospike_conf_member(tar):
    """Find a member whose path contains or ends with aerospike.conf. Returns the member or None."""
    for m in tar.getmembers():
        if not m.isfile():
            continue
        name = m.name.replace("\\", "/")
        if "aerospike.conf" in name or name.endswith("aerospike.conf"):
            return m
    return None

def parse_aerospike_conf(text):
    """
    Parse aerospike.conf into flat config_name -> value dict.
    Supports [section], 'section {', 'namespace NAME {', and key-value lines (first space separates).
    Keys are dot-prefixed (e.g. namespace.foo.replication-factor) to match node_configs.
    """
    import re
    out = {}
    prefix_stack = []
    prefix = None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # Closing brace: restore previous prefix
        if stripped == "}":
            if prefix_stack:
                prefix = prefix_stack.pop()
            continue
        # Section header: [logging], [namespace name] (INI-style)
        m = re.match(r"^\[(.+)\]$", stripped)
        if m:
            section = m.group(1).strip()
            parts = section.split(None, 1)
            if len(parts) >= 2 and parts[0].lower() == "namespace":
                prefix = "namespace." + parts[1].strip()
            else:
                prefix = section.replace(" ", ".")
            prefix_stack = [prefix]
            continue
        # Block start: "namespace NAME {" (two words then brace)
        m = re.match(r"^namespace\s+(\S+)\s*\{\s*$", stripped, re.IGNORECASE)
        if m:
            prefix_stack.append(prefix)
            prefix = "namespace." + m.group(1).strip()
            continue
        # Block start: "section {" or "key value {" (single word then brace)
        m = re.match(r"^(\S+)\s*\{\s*$", stripped)
        if m:
            prefix_stack.append(prefix)
            part = m.group(1)
            prefix = (prefix + "." + part) if prefix else part
            continue
        # key value (first space or tab)
        idx = stripped.find("\t")
        if idx < 0:
            idx = stripped.find(" ")
        if idx > 0:
            key = stripped[:idx].strip()
            value = stripped[idx + 1:].strip().strip('"')
            if prefix:
                full_key = f"{prefix}.{key}"
            else:
                full_key = key
            out[full_key] = value
    return out

def _apply_baseline_schema(conn):
    """Create all tables from the canonical schema. Call once at DB init."""
    baseline_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema", "baseline.sql")
    if not os.path.exists(baseline_path):
        raise FileNotFoundError(f"Schema baseline not found: {baseline_path}")
    with open(baseline_path, "r") as f:
        conn.executescript(f.read())

def process_collectinfo(input_path, db_path="aerospike_health.db"):
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    _apply_baseline_schema(conn)
    cursor = conn.cursor()

    # Generate a run_id based on current wall clock
    run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with tarfile.open(input_path, "r:*") as tar:
        target = find_telemetry_member(tar)
        
        if not target:
            raise FileNotFoundError("Dynamic discovery failed: No telemetry JSON found in bundle.")
            
        print(f"🔍 Discovered Telemetry: {target.name} ({target.size / 1024:.2f} KB)")
        data = get_json_content(tar, target)

        # Collect all node_ids for static_configs (one conf file per cluster, same rows per node)
        node_ids = []
        for timestamp, clusters in data.items():
            for cluster_name, nodes in clusters.items():
                node_ids.extend(nodes.keys())

        # Ingest static aerospike.conf from bundle if present
        conf_member = find_aerospike_conf_member(tar)
        if conf_member:
            try:
                conf_bytes = tar.extractfile(conf_member).read()
                conf_text = conf_bytes.decode("utf-8", errors="replace")
                static_kv = parse_aerospike_conf(conf_text)
                if static_kv and node_ids:
                    for node_id in node_ids:
                        for config_name, value in static_kv.items():
                            cursor.execute(
                                "INSERT INTO static_configs (run_id, node_id, config_name, value) VALUES (?, ?, ?, ?)",
                                (run_id, node_id, config_name, value),
                            )
                    print(f"✅ Static config: loaded {len(static_kv)} keys from aerospike.conf for {len(node_ids)} node(s)")
            except Exception as e:
                print(f"⚠️ Failed to parse aerospike.conf: {e}")
        else:
            print("ℹ️ No aerospike.conf file in bundle; Config Drift check will report DATA MISSING.")

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