import sqlite3
import pandas as pd

# -----------------------------------------------------------------------------
# VERSION STAMP
# -----------------------------------------------------------------------------
__version__ = "1.5.4"

# --- Metadata ---
# ID: 2.c
# Title: Storage Deadlock Risk

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    check_id = "2.c"
    check_name = "Storage Deadlock Risk"
    target_table = "node_configs"
    
    try:
        # 1. SCHEMA SAFETY CHECK
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{target_table}'")
        if not cursor.fetchone():
            return {"id": check_id, "name": check_name, "status": "⚠️ DATA MISSING", "message": "Table not found."}

        # 2. QUERY LOGIC
        # We need to compare Defrag LWM and Disk HWM for every namespace
        query = """
            SELECT node_id, config_name, value 
            FROM node_configs 
            WHERE config_name LIKE 'namespace.%.defrag-lwm-free-pct'
               OR config_name LIKE 'namespace.%.high-water-disk-pct'
        """
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            return {
                "id": check_id, "name": check_name, "status": "PASS", 
                "message": "No disk-based namespaces detected; storage deadlock not applicable.",
                "remediation": "None"
            }

        # 3. ANALYSIS
        # Group by namespace to compare thresholds
        namespaces = df['config_name'].str.split('.').str[1].unique()
        findings = []

        for ns in namespaces:
            defrag_key = f"namespace.{ns}.defrag-lwm-free-pct"
            hwm_key = f"namespace.{ns}.high-water-disk-pct"
            
            # Get values (default to Aerospike defaults if missing)
            defrag_val = df[df['config_name'] == defrag_key]['value'].iloc[0] if not df[df['config_name'] == defrag_key].empty else "50"
            hwm_val = df[df['config_name'] == hwm_key]['value'].iloc[0] if not df[df['config_name'] == hwm_key].empty else "50"
            
            # DEADLOCK CALCULATION:
            # If (100 - HWM) < (100 - Defrag LWM), the disk might fill up 
            # before defrag can reclaim enough blocks to stay ahead.
            # Simplified TAM Rule: defrag-lwm-free-pct should generally be >= 50% 
            # and should be at least as aggressive as the HWM.
            if int(defrag_val) < 40 or (int(defrag_val) < int(hwm_val)):
                findings.append(f"{ns} (Defrag: {defrag_val}%, HWM: {hwm_val}%)")

        if findings:
            return {
                "id": check_id,
                "name": check_name,
                "status": "WARNING",
                "message": f"Storage deadlock risk in namespace(s): {', '.join(findings)}.",
                "remediation": (
                    "**Why this matters:** If the Disk High Water Mark (eviction) is reached before defragmentation "
                    "reclaims enough space, the node may stop accepting writes (`stop-writes-pct`). "
                    "A low defrag LWM means blocks are only cleaned when they are nearly empty, which is often too "
                    "slow for high-throughput clusters.\n\n"
                    "**Action Plan:**\n"
                    "1. Increase `defrag-lwm-free-pct` to at least 50 for the affected namespaces.\n"
                    "2. Ensure `high-water-disk-pct` is set at a level that leaves at least 20% headroom before "
                    "`stop-writes-pct` is reached.\n"
                    "3. Monitor `write_enumeration` and `defrag_q` size to ensure space reclamation is keeping pace with ingress."
                )
            }

        return {
            "id": check_id, "name": check_name, "status": "PASS",
            "message": "Defragmentation thresholds are correctly prioritized over eviction marks.",
            "remediation": "None"
        }
        
    except Exception as e:
        return {"id": check_id, "name": check_name, "status": "CRITICAL", "message": f"Error: {str(e)}"}
    finally:
        conn.close()