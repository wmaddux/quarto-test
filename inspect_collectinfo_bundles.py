#!/usr/bin/env python3
"""
One-off script to inspect collectinfo bundles (6.x, 7.x, 8.x).
Reports: telemetry JSON path, aerospike.conf presence, one node's top-level keys
and paths for as_stat, statistics, config, namespaces, set, acl, sys_stat.
"""
import json
import os
import sys
import tarfile
import gzip
import zipfile
import io

def get_json_content(tar, member):
    f_bytes = tar.extractfile(member).read()
    if member.name.endswith('.zip'):
        with zipfile.ZipFile(io.BytesIO(f_bytes)) as z:
            f_bytes = z.read(z.namelist()[0])
    if f_bytes.startswith(b'\x1f\x8b'):
        f_bytes = gzip.decompress(f_bytes)
    return json.loads(f_bytes.decode('utf-8'))

def find_telemetry_member(tar):
    candidates = [
        m for m in tar.getmembers()
        if (".json" in m.name.lower()) and ("manifest" not in m.name.lower())
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda m: m.size)

def deep_keys(d, prefix="", max_depth=4, depth=0):
    """Return list of key paths (e.g. 'as_stat.statistics.namespace') up to max_depth."""
    if depth >= max_depth or not isinstance(d, dict):
        return []
    out = []
    for k, v in d.items():
        path = f"{prefix}.{k}" if prefix else k
        out.append(path)
        if isinstance(v, dict) and depth + 1 < max_depth:
            out.extend(deep_keys(v, path, max_depth, depth + 1))
    return out

def inspect_bundle(label, path):
    print(f"\n{'='*60}")
    print(f"BUNDLE: {label}")
    print(f"PATH: {path}")
    print("="*60)
    if not os.path.exists(path):
        print("  (file not found)")
        return None
    try:
        with tarfile.open(path, "r:*") as tar:
            names = [m.name for m in tar.getmembers()]
            # aerospike.conf presence
            conf_candidates = [n for n in names if "aerospike.conf" in n or n.endswith("aerospike.conf")]
            has_conf = bool(conf_candidates)
            print(f"  aerospike.conf present: {has_conf}")
            if conf_candidates:
                print(f"  paths: {conf_candidates[:5]}{' ...' if len(conf_candidates) > 5 else ''}")
            # Telemetry member
            tele = find_telemetry_member(tar)
            if not tele:
                print("  telemetry JSON: NOT FOUND")
                return None
            print(f"  telemetry JSON: {tele.name} ({tele.size} bytes)")
            data = get_json_content(tar, tele)
            # Top-level keys (timestamp -> cluster -> node)
            top_level = list(data.keys())[:3]
            print(f"  data top-level keys (sample): {top_level}")
            # One node payload
            node_payload = None
            for ts, clusters in data.items():
                for cname, nodes in clusters.items():
                    for nid, ndata in nodes.items():
                        node_payload = ndata
                        node_id = nid
                        break
                    if node_payload is not None:
                        break
                if node_payload is not None:
                    break
            if node_payload is None:
                print("  node payload: NONE FOUND")
                return None
            print(f"  first node_id: {node_id}")
            node_top = list(node_payload.keys())
            print(f"  node payload top-level keys: {node_top}")
            # Paths we care about
            as_stat = node_payload.get("as_stat")
            sys_stat = node_payload.get("sys_stat")
            paths = {
                "as_stat": "present" if as_stat is not None else "ABSENT",
                "sys_stat": "present" if sys_stat is not None else "ABSENT",
            }
            if as_stat and isinstance(as_stat, dict):
                paths["as_stat.statistics"] = "present" if as_stat.get("statistics") is not None else "ABSENT"
                paths["as_stat.config"] = "present" if as_stat.get("config") is not None else "ABSENT"
                paths["as_stat.meta_data"] = "present" if as_stat.get("meta_data") is not None else "ABSENT"
                paths["as_stat.acl"] = "present" if as_stat.get("acl") is not None else "ABSENT"
                paths["as_stat.namespaces"] = "present" if as_stat.get("namespaces") is not None else "ABSENT"
                st = as_stat.get("statistics") or {}
                paths["as_stat.statistics.namespace"] = "present" if st.get("namespace") is not None else "ABSENT"
                paths["as_stat.statistics.set"] = "present" if st.get("set") is not None else "ABSENT"
                paths["as_stat.statistics.service"] = "present" if st.get("service") is not None else "ABSENT"
                if as_stat.get("acl") and isinstance(as_stat["acl"], dict):
                    paths["as_stat.acl.users"] = "present" if as_stat["acl"].get("users") is not None else "ABSENT"
            for k, v in sorted(paths.items()):
                print(f"    {k}: {v}")
            # Optional: show first-level keys under as_stat
            if as_stat and isinstance(as_stat, dict):
                as_stat_keys = list(as_stat.keys())
                print(f"  as_stat first-level keys: {as_stat_keys}")
            return {
                "label": label,
                "path": path,
                "aerospike_conf_present": has_conf,
                "aerospike_conf_paths": conf_candidates,
                "telemetry_member": tele.name,
                "data_top_level": list(data.keys()),
                "node_id": node_id,
                "node_top_level": node_top,
                "paths": paths,
                "as_stat_keys": list(as_stat.keys()) if as_stat and isinstance(as_stat, dict) else [],
            }
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    base = os.path.join(os.path.dirname(__file__), "ingest_samples")
    bundles = [
        ("6.x", os.path.join(base, "collect_info_v6x", "yahoo-collect_info_20251001_122057.tgz")),
        ("7.x", os.path.join(base, "collect_info_v7x", "adobe-azure-els.collect_info_20260120_225608.tgz")),
        ("8.x", os.path.join(base, "collect_info_v8x", "swarit_collect_info_20260108_065237.tgz")),
    ]
    results = []
    for label, path in bundles:
        r = inspect_bundle(label, path)
        if r:
            results.append(r)
    # JSON summary for programmatic use
    summary_path = os.path.join(os.path.dirname(__file__), "ingest_samples", "bundle_inspection_summary.json")
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSummary written to {summary_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
