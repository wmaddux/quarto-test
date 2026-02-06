#!/usr/bin/env python3
import tarfile, json, gzip, zipfile, io, sys, os

def get_content(tar, member):
    """Extracts and handles nested zip/gzip decompression."""
    f = tar.extractfile(member).read()
    
    # Handle .zip wrapper
    if member.name.endswith('.zip'):
        with zipfile.ZipFile(io.BytesIO(f)) as z:
            # Get the first file inside the zip
            inner_name = z.namelist()[0]
            f = z.read(inner_name)
            
    # Handle .gz wrapper or raw gzip bytes
    if f.startswith(b'\x1f\x8b'):
        f = gzip.decompress(f)
        
    return f

def interrogate(file_path):
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    with tarfile.open(file_path, "r:*") as tar:
        members = tar.getmembers()
        # Fuzzy match for the telemetry file
        telemetry_member = next((m for m in members if "ascinfo.json" in m.name), None)
        
        if telemetry_member:
            print(f"✅ Found Telemetry: {telemetry_member.name}")
            content = get_content(tar, telemetry_member)
            data = json.loads(content.decode('utf-8'))
            
            # Drill down to node keys
            ts = list(data.keys())[0]
            cluster = list(data[ts].keys())[0]
            node = list(data[ts][cluster].keys())[0]
            
            print(f"🖥️  Node ID: {node}")
            print(f"🔑 Keys available: {list(data[ts][cluster][node].keys())}")
        else:
            print("❌ No file matching '*ascinfo.json*' found in archive.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        interrogate(sys.argv[1])
