import tarfile, json, gzip, zipfile, io

def peek():
    path = 'aws-common.collect_info_20260120_230014.tgz'
    with tarfile.open(path, "r:*") as tar:
        member = next(m for m in tar.getmembers() if 'ascinfo.json' in m.name)
        f = tar.extractfile(member).read()
        
        # Unzip inner layer
        with zipfile.ZipFile(io.BytesIO(f)) as z:
            content = z.read(z.namelist()[0])
            
        data = json.loads(content.decode('utf-8'))
        ts = list(data.keys())[0]
        cl = list(data[ts].keys())[0]
        node = list(data[ts][cl].keys())[0]
        node_data = data[ts][cl][node]
        
        print(f"--- Top Level Keys ---\n{list(node_data.keys())}")
        
        if 'as_stat' in node_data:
            print(f"\n--- Keys inside as_stat ---\n{list(node_data['as_stat'].keys())}")
            
            # Check for common namespace locations
            for key in ['namespace', 'statistics', 'sub_stats']:
                if key in node_data['as_stat']:
                    val = node_data['as_stat'][key]
                    print(f"\n--- Found '{key}'! It is a {type(val)} ---")
                    if isinstance(val, dict):
                        print(f"Sample sub-keys: {list(val.keys())[:5]}")

if __name__ == "__main__":
    peek()
