#!/usr/bin/env python3
import tarfile, json, gzip, zipfile, io, sys, os
__version__ = "1.1.0"

def profile_telemetry(path):
    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        return

    print(f"🕵️  Profiling Bundle: {path}\n" + "="*60)
    try:
        with tarfile.open(path, "r:*") as tar:
            member = next((m for m in tar.getmembers() if 'ascinfo.json' in m.name), None)
            if not member:
                print("❌ No ascinfo.json found.")
                return
            
            f = tar.extractfile(member).read()
            if member.name.endswith('.zip'):
                with zipfile.ZipFile(io.BytesIO(f)) as z:
                    f = z.read(z.namelist()[0])
            elif f.startswith(b'\x1f\x8b'):
                f = gzip.decompress(f)
            
            data = json.loads(f.decode('utf-8'))
            
            # Drill to first node
            ts = list(data.keys())[0]
            cluster = list(data[ts].keys())[0]
            node = list(data[ts][cluster].keys())[0]
            payload = data[ts][cluster][node]

            print(f"📍 Node: {node}")
            print(f"⏰ Timestamp: {ts}")

            # 1. Version Discovery
            # Versions are usually in as_stat -> meta_data or as_stat -> statistics -> service
            as_stat = payload.get('as_stat', {})
            version = "Unknown"
            
            # Search common locations for version strings
            search_paths = [
                as_stat.get('meta_data', {}).get('edition'),
                as_stat.get('statistics', {}).get('service', {}).get('build'),
                payload.get('sys_stat', {}).get('os') # OS version as fallback
            ]
            version = next((v for v in search_paths if v), "Unknown")
            print(f"🆔 Detected Version/Build: {version}")

            # 2. Key Type Analysis (The 'Why is it 0' check)
            print(f"\n🔍 Data Type Analysis for 'as_stat':")
            for key in ['statistics', 'config', 'namespace']:
                val = as_stat.get(key, "MISSING")
                v_type = type(val)
                v_len = len(val) if hasattr(val, '__len__') else "N/A"
                print(f"   - {key:12}: Type={str(v_type):15} Size={v_len}")
                
                # If it's a dict, show the first level of sub-keys
                if isinstance(val, dict) and v_len > 0:
                    print(f"     └─ Sub-keys: {list(val.keys())[:5]}")
                    
                    # Special check for namespaces (the current pain point)
                    if key == 'statistics' and 'namespace' in val:
                        ns_val = val['namespace']
                        print(f"     └─ Found 'namespace' inside statistics! Type: {type(ns_val)}")
                        if isinstance(ns_val, dict):
                             first_ns = list(ns_val.keys())[0]
                             print(f"        └─ Sample NS [{first_ns}] Type: {type(ns_val[first_ns])}")

    except Exception as e:
        print(f"💥 Profiling Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        profile_telemetry(sys.argv[1])
    else:
        print("Usage: debug_structure.py <bundle.tgz>")
