import tarfile
import json
import gzip
import io
__version__ = "1.4.0"

def interrogate():
    bundle_path = "aws-common.collect_info_20260120_230014.tgz"
    inventory = {"telemetry": [], "configs": [], "logs": [], "other": []}
    
    print(f"🧐 Scanning Bundle: {bundle_path}\n" + "="*50)
    
    with tarfile.open(bundle_path, "r:*") as tar:
        # 1. Categorize every file in the bundle
        for member in tar.getmembers():
            name = member.name.lower()
            if name.endswith("ascinfo.json"):
                inventory["telemetry"].append(member)
            elif name.endswith(".conf"):
                inventory["configs"].append(member)
            elif name.endswith(".log") or "aerospike.log" in name:
                inventory["logs"].append(member)
            else:
                inventory["other"].append(member)

        print(f"📊 Inventory Summary:")
        print(f"   - Telemetry (JSON): {len(inventory['telemetry'])}")
        print(f"   - Config Files:     {len(inventory['configs'])}")
        print(f"   - Log Files:        {len(inventory['logs'])}")
        print(f"   - Other Files:      {len(inventory['other'])}\n")

        # 2. Deep Dive into the first Telemetry file found
        if inventory["telemetry"]:
            target = inventory["telemetry"][0]
            print(f"🔍 Peeking inside Telemetry: {target.name}")
            
            f_bytes = tar.extractfile(target).read()
            # Handle potential internal Gzip
            if f_bytes.startswith(b'\x1f\x8b'):
                f_bytes = gzip.decompress(f_bytes)
            
            try:
                data = json.loads(f_bytes.decode('utf-8'))
                # Navigate to the first node's data
                ts = list(data.keys())[0]
                cluster = list(data[ts].keys())[0]
                node_id = list(data[ts][cluster].keys())[0]
                node_data = data[ts][cluster][node_id]
                
                print(f"✅ Successfully parsed JSON for Node: {node_id}")
                print(f"🔑 Available Node Keys: {list(node_data.keys())}")
                
                # Check for nested stats/configs
                for key in ['as_stat', 'statistics', 'as_config', 'configs']:
                    if key in node_data:
                        sub_keys = list(node_data[key].keys())[:5]
                        print(f"   -> '{key}' found with keys like: {sub_keys}...")

            except Exception as e:
                print(f"❌ Failed to parse JSON: {e}")

        # 3. List found config files (TAMs often need to know if custom .conf exists)
        if inventory["configs"]:
            print(f"\n📄 Found Config Files:")
            for cfg in inventory["configs"][:5]: # Show first 5
                print(f"   - {cfg.name}")

if __name__ == "__main__":
    interrogate()
