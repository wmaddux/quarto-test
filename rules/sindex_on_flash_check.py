import sqlite3
import pandas as pd

# -----------------------------------------------------------------------------
# VERSION STAMP
# -----------------------------------------------------------------------------
__version__ = "1.4.0"

# --- Metadata ---
# ID: 2.a
# Title: SIndex on Flash

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    check_id = "2.a"
    check_name = "SIndex on Flash"
    
    try:
        # 1. SCHEMA SAFETY CHECK
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='node_configs'")
        if not cursor.fetchone():
            return {
                "id": check_id, "name": check_name, "status": "⚠️ DATA MISSING",
                "message": "Required table 'node_configs' not found.",
                "remediation": "Verify the ConfigIngestor is active."
            }

        # 2. QUERY LOGIC
        # We check if any namespace is using Index-on-Flash (index-type flash)
        # and if SIndexes are also configured to use flash.
        query = """
            SELECT node_id, config_name, value 
            FROM node_configs 
            WHERE config_name LIKE 'namespace.%.index-type'
               OR config_name LIKE 'namespace.%.sindex-type'
        """
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            return {
                "id": check_id, "name": check_name, "status": "PASS",
                "message": "No Index-on-Flash namespaces detected; no action required.",
                "remediation": "None"
            }

        # 3. FINDING LOGIC
        # Identify namespaces that have index-type=flash
        flash_ns = df[df['value'] == 'flash']['config_name'].str.split('.').str[1].unique()
        
        findings = []
        for ns in flash_ns:
            # For each Flash NS, check if its sindex-type is also 'flash'
            sindex_key = f"namespace.{ns}.sindex-type"
            sindex_val = df[df['config_name'] == sindex_key]['value'].unique()
            
            if len(sindex_val) > 0 and 'flash' not in sindex_val:
                findings.append(ns)

        if findings:
            return {
                "id": check_id,
                "name": check_name,
                "status": "WARNING",
                "message": f"Secondary Indexes for namespace(s) {', '.join(findings)} are in memory but Primary Index is on Flash.",
                "remediation": (
                    "**Why this matters:** When the Primary Index is on Flash, it is usually because the dataset is too large "
                    "for RAM. Leaving Secondary Indexes in RAM can lead to unexpected 'Out of Memory' (OOM) crashes as the "
                    "dataset grows.\n\n"
                    "**Action Plan:**\n"
                    "1. Update the configuration for the affected namespaces.\n"
                    "2. Add `sindex-type flash` to the namespace stanza in `aerospike.conf`.\n"
                    "3. Perform a rolling restart of the cluster nodes."
                )
            }

        return {
            "id": check_id, "name": check_name, "status": "PASS",
            "message": "Secondary indexes are correctly aligned with Primary Index storage (Flash).",
            "remediation": "None"
        }
        
    except Exception as e:
        return {"id": check_id, "name": check_name, "status": "CRITICAL", "message": f"Error: {str(e)}"}
    finally:
        conn.close()