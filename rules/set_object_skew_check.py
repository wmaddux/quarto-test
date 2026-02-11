import sqlite3
import pandas as pd

# -----------------------------------------------------------------------------
# VERSION STAMP
# Ensures this rule is compatible with the v1.4.1 Markdown reporting engine.
# -----------------------------------------------------------------------------
__version__ = "1.4.1"

# --- Metadata ---
# ID: 4.f -> Matches the Aerospike Health Catalog
# Title: Set Object Skew

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    
    # -------------------------------------------------------------------------
    # CONFIGURATION
    # -------------------------------------------------------------------------
    check_id = "4.f"
    check_name = "Set Object Skew"
    
    try:
        # ---------------------------------------------------------------------
        # 1. SCHEMA SAFETY CHECK
        # ---------------------------------------------------------------------
        cursor = conn.cursor()
        target_table = "set_stats"
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{target_table}'")
        
        if not cursor.fetchone():
            return {
                "id": check_id, "name": check_name, "status": "⚠️ DATA MISSING",
                "message": f"Table '{target_table}' not found in database.",
                "remediation": "Check if set-level telemetry was collected in the bundle."
            }

        # ---------------------------------------------------------------------
        # 2. DYNAMIC COLUMN DISCOVERY
        # ---------------------------------------------------------------------
        cursor.execute(f"PRAGMA table_info({target_table})")
        columns = [c[1] for c in cursor.fetchall()]
        
        # Determine the correct namespace column
        ns_col = "ns" if "ns" in columns else "ns_name"
        
        # ---------------------------------------------------------------------
        # 3. QUERY LOGIC (Hardened for Vertical Metric Storage)
        # ---------------------------------------------------------------------
        if "metric" in columns and "value" in columns:
            # Vertical Schema (metric='objects', value='1234')
            query = f"""
                SELECT node_id, {ns_col} as ns_name, set_name, CAST(value AS REAL) as objects 
                FROM {target_table} 
                WHERE metric = 'objects' AND set_name != ''
            """
        elif "objects" in columns:
            # Horizontal Schema (objects=1234)
            query = f"""
                SELECT node_id, {ns_col} as ns_name, set_name, CAST(objects AS REAL) as objects 
                FROM {target_table} 
                WHERE set_name != ''
            """
        else:
            # Column not found in either format
            return {
                "id": check_id, "name": check_name, "status": "⚠️ SCHEMA MISMATCH",
                "message": f"Metric 'objects' not found in {target_table} columns: {columns}",
                "remediation": "Verify the Ingestor is correctly flattening set-level statistics."
            }
            
        df = pd.read_sql_query(query, conn)

        # ---------------------------------------------------------------------
        # 4. ANALYSIS & RESULTS
        # ---------------------------------------------------------------------
        if df.empty:
            return {
                "id": check_id, "name": check_name, "status": "PASS",
                "message": "No set-level object data found to analyze.",
                "remediation": "None"
            }
        
        # Calculate Coefficient of Variation (CV = std / mean) per set
        stats = df.groupby(['ns_name', 'set_name'])['objects'].agg(['mean', 'std']).reset_index()
        stats['cv'] = stats['std'] / stats['mean']
        
        # Threshold: 10% deviation
        skewed = stats[stats['cv'] > 0.10]

        if not skewed.empty:
            problem_sets = ", ".join(skewed['set_name'].unique())
            return {
                "id": check_id,
                "name": check_name,
                "status": "WARNING",
                "message": f"Significant object skew detected in sets: {problem_sets}. Deviation exceeds 10% across nodes.",
                "remediation": (
                    "**Why this matters:** Unbalanced sets cause specific nodes to hit HWM prematurely.\n\n"
                    "**Action Plan:**\n"
                    "1. Verify application partitioner logic.\n"
                    "2. Check master partition distribution via `asadm -e 'show pmap'`."
                )
            }

        return {
            "id": check_id, "name": check_name, "status": "PASS",
            "message": "Objects are balanced across all sets and nodes.", "remediation": "None"
        }
        
    except Exception as e:
        return {
            "id": check_id, "name": check_name, "status": "CRITICAL",
            "message": f"Execution Error: {str(e)}",
            "remediation": "Review the database schema and rule query logic."
        }
    finally:
        conn.close()