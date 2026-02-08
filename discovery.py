__version__ = "1.3.0"
# discovery_v2.py
import json, tarfile, io, gzip, zipfile

def get_json_content(tar, member):
    f_bytes = tar.extractfile(member).read()
    if member.name.endswith('.zip'):
        with zipfile.ZipFile(io.BytesIO(f_bytes)) as z:
            f_bytes = z.read(z.namelist()[0])
    if f_bytes.startswith(b'\x1f\x8b'):
        f_bytes = gzip.decompress(f_bytes)
    return json.loads(f_bytes.decode('utf-8'))

with tarfile.open("../aws-common.collect_info_20260120_230014.tgz", "r:*") as tar:
    target = next((m for m in tar.getmembers() if "ascinfo.json" in m.name), None)
    data = get_json_content(tar, target)
    
    first_ts = list(data.keys())[0]
    first_cluster = list(data[first_ts].keys())[0]
    first_node = list(data[first_ts][first_cluster].keys())[0]
    
    sys_content = data[first_ts][first_cluster][first_node].get('sys_stat', {})
    
    print(f"--- Content of sys_stat for {first_node} ---")
    if isinstance(sys_content, dict):
        print(f"Sub-keys found: {list(sys_content.keys())}")
    else:
        print(f"Type is {type(sys_content)}. First 100 chars: {str(sys_content)[:100]}")
        