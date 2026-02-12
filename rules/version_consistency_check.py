import sqlite3
import pandas as pd

# -----------------------------------------------------------------------------
# VERSION STAMP
# -----------------------------------------------------------------------------
__version__ = "1.6.0"

# --- Metadata ---
# ID: 1.c
# Title: Version Consistency

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    check_id = "1.c"
    check_name = "Version Consistency"
    
    try:
        # 1. DYNAMIC KEY DISCOVERY
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT metric 
            FROM node_stats 
            WHERE metric LIKE '%version' OR metric LIKE '%build'
        """)
        found_keys = [row[0] for row in cursor.fetchall()]
        
        # 2. HANDLING MISSING TELEMETRY (PROFESSIONAL TONE)
        if not found_keys:
            return {
                "id": check_id, 
                "name": check_name, 
                "status": "⚠️ DATA MISSING",
                "message": "Software version telemetry is not available for this cluster snapshot.",
                "remediation": (
                    "**Assessment:** A comprehensive version consistency audit could not be performed because "
                    "software build identifiers were not captured in the diagnostic bundle.\n\n"
                    "**Action Plan:**\n"
                    "1. Ensure the diagnostic utility (`asadm`) has sufficient permissions to query the Aerospike 'info' protocol.\n"
                    "2. Re-generate the collection bundle using `asadm -e \"collectinfo\"` ensuring all nodes are reachable.\n"
                    "3. Validate that the Aerospike daemon is active and responding on its management port across all cluster nodes."
                )
            }

        # 3. ANALYSIS
        placeholders = ','.join(['?'] * len(found_keys))
        query = f"SELECT node_id, value FROM node_stats WHERE metric IN ({placeholders})"
        df = pd.read_sql_query(query, conn, params=found_keys)
        df = df.drop_duplicates(subset=['node_id'])
        
        versions_found = df['value'].unique()
        node_count = len(df['node_id'].unique())

        if len(versions_found) > 1:
            # SKEW DETECTED
            v_counts = df['value'].value_counts().to_dict()
            summary = ", ".join([f"{v} ({c} nodes)" for v, c in v_counts.items()])
            return {
                "id": check_id, 
                "name": check_name, 
                "status": "WARNING",
                "message": f"Mismatched software versions detected across the cluster: {summary}.",
                "remediation": (
                    "**Assessment:** Operating a cluster with inconsistent software versions is only supported during "
                    "active rolling upgrades. Prolonged version skew can lead to heartbeat instability and "
                    "inconsistent feature availability.\n\n"
                    "**Action Plan:**\n"
                    "1. Identify outlier nodes and prioritize alignment to a single GA or Hotfix release.\n"
                    "2. Consult the Aerospike Release Notes to ensure protocol compatibility between the identified versions."
                )
            }

        # 4. PASS (PROFESSIONAL EVIDENTIARY LOG)
        current_version = versions_found[0]
        return {
            "id": check_id, 
            "name": check_name, 
            "status": "PASS",
            "message": f"All {node_count} nodes are confirmed consistent on Aerospike {current_version}.",
            "remediation": "None"
        }
        
    except Exception as e:
        return {"id": check_id, "name": check_name, "status": "CRITICAL", "message": "Diagnostic execution error during version audit."}
    finally:
        conn.close()