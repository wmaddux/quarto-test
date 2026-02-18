import sqlite3
import pandas as pd

# -----------------------------------------------------------------------------
# VERSION STAMP
# Ensures this rule is compatible with the v1.4.0 Markdown reporting engine.
# -----------------------------------------------------------------------------
__version__ = "1.4.0"

# --- Metadata ---
# ID: {X.y} (e.g., 1.a) -> Matches the Aerospike Health Catalog
# Title: Descriptive Name for the report table

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    
    # -------------------------------------------------------------------------
    # CONFIGURATION
    # Set your Rule ID and Name here. These appear in the final report.
    # -------------------------------------------------------------------------
    check_id = "X.y"
    check_name = "Descriptive Rule Name"
    
    try:
        # ---------------------------------------------------------------------
        # 1. SCHEMA SAFETY CHECK
        # Before querying, we verify the table exists to prevent a crash if 
        # the ingestor failed or the bundle was incomplete.
        # ---------------------------------------------------------------------
        cursor = conn.cursor()
        target_table = "node_stats" # Replace with your required table
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{target_table}'")
        
        if not cursor.fetchone():
            return {
                "id": check_id, "name": check_name, "status": "⚠️ DATA MISSING",
                "message": f"Table '{target_table}' not found in database.",
                "remediation": "Verify that the correct Ingestor is enabled in ingest/__init__.py."
            }

        # ---------------------------------------------------------------------
        # 2. QUERY LOGIC
        # Use standard SQL. Aim for specific columns rather than SELECT *
        # to keep the dataframe lightweight.
        # ---------------------------------------------------------------------
        query = f"SELECT node_id, metric, value FROM {target_table} WHERE metric = 'example_metric'"
        df = pd.read_sql_query(query, conn)
        
        # ---------------------------------------------------------------------
        # 3. ANALYSIS & RESULTS
        # Standard PASS/WARNING/CRITICAL logic.
        # ---------------------------------------------------------------------
        if df.empty:
            return {
                "id": check_id, "name": check_name, "status": "PASS",
                "message": "Healthy state description: e.g., No error skew detected.",
                "remediation": "None"
            }
        
        # Example threshold check (Adjust as needed)
        threshold = 100
        findings = df[df['value'] > threshold]

        if not findings.empty:
            return {
                "id": check_id,
                "name": check_name,
                "status": "WARNING", # Or "CRITICAL"
                "message": f"Detected {len(findings)} nodes exceeding threshold {threshold}.",
                "remediation": (
                    "**Why this matters:** [Explain the technical impact].\n\n"
                    "**Action Plan:**\n"
                    "1. Step-by-step resolution using `asadm`.\n"
                    "2. Configuration changes required."
                )
            }

        # Final default fallback
        return {
            "id": check_id, "name": check_name, "status": "PASS",
            "message": "All metrics within normal bounds.", "remediation": "None"
        }
        
    except Exception as e:
        # Graceful failure: prevents one bad rule from breaking the whole report
        return {
            "id": check_id, "name": check_name, "status": "CRITICAL",
            "message": f"Execution Error: {str(e)}",
            "remediation": "Review the database schema and rule query logic."
        }
    finally:
        conn.close()