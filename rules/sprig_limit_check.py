import sqlite3
import pandas as pd

# -----------------------------------------------------------------------------
# VERSION STAMP
# -----------------------------------------------------------------------------
__version__ = "1.5.4"

# --- Metadata ---
# ID: 2.b
# Title: Sprig Limit Warning

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    check_id = "2.b"
    check_name = "Sprig Limit Warning"
    
    try:
        # 1. SCHEMA SAFETY CHECK
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='node_configs'")
        if not cursor.fetchone():
            return {"id": check_id, "name": check_name, "status": "⚠️ DATA MISSING", "message": "Table not found."}

        # 2. QUERY LOGIC
        # We need namespaces where index-type is flash and the current sprig count
        query = """
            SELECT node_id, config_name, value 
            FROM node_configs 
            WHERE config_name LIKE 'namespace.%.index-type'
               OR config_name LIKE 'namespace.%.partition-tree-sprigs'
        """
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            return {"id": check_id, "name": check_name, "status": "PASS", "message": "No sprig configurations found.", "remediation": "None"}

        # 3. ANALYSIS
        # Extract namespaces using flash
        flash_ns = df[df['value'] == 'flash']['config_name'].str.split('.').str[1].unique()
        
        findings = []
        for ns in flash_ns:
            sprig_key = f"namespace.{ns}.partition-tree-sprigs"
            sprig_val = df[df['config_name'] == sprig_key]['value'].iloc[0] if not df[df['config_name'] == sprig_key].empty else "64"
            
            # 64 is the default. For Flash, we generally want at least 4096 or higher
            # depending on record count. We warn if it's still at the default.
            if int(sprig_val) <= 256:
                findings.append(f"{ns} ({sprig_val} sprigs)")

        if findings:
            return {
                "id": check_id,
                "name": check_name,
                "status": "WARNING",
                "message": f"Namespace(s) {', '.join(findings)} use Index-on-Flash but have low sprig counts.",
                "remediation": (
                    "**Why this matters:** Sprigs define the number of sub-trees in the primary index. For Index-on-Flash, "
                    "a low sprig count causes 'deep' trees, requiring more disk IOPS per lookup. This can lead to high "
                    "read latency and SSD saturation.\n\n"
                    "**Action Plan:**\n"
                    "1. Increase `partition-tree-sprigs` in the namespace stanza (e.g., to 4096, 8192, or 16384).\n"
                    "2. **Note:** This setting requires a cold start of the Aerospike process to rebuild the index."
                )
            }

        return {
            "id": check_id, "name": check_name, "status": "PASS",
            "message": "Sprig counts are appropriately configured for Flash storage.",
            "remediation": "None"
        }
        
    except Exception as e:
        return {"id": check_id, "name": check_name, "status": "CRITICAL", "message": f"Error: {str(e)}"}
    finally:
        conn.close()