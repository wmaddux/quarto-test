import sqlite3
import pandas as pd

# -----------------------------------------------------------------------------
# VERSION STAMP
# -----------------------------------------------------------------------------
__version__ = "1.5.4"

def run_check(db_path="aerospike_health.db"):
    """
    Standardized Rule 6.a: ACL Connection Monopoly Audit.
    Ensures single users are not saturating cluster connection limits.
    """
    conn = sqlite3.connect(db_path)
    check_id = "6.a"
    check_name = "Security Connection Audit"
    
    try:
        # ---------------------------------------------------------------------
        # 1. SCHEMA SAFETY & DATA DISCOVERY
        # ---------------------------------------------------------------------
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='security_stats'")
        
        if not cursor.fetchone():
            return {
                "id": check_id, 
                "name": check_name, 
                "status": "⚠️ DATA MISSING",
                "message": "Security telemetry (ACL) not found in the database.",
                "remediation": (
                    "**Assessment:** This check requires Enterprise Edition ACL telemetry.\n\n"
                    "**Action Plan:**\n"
                    "1. Verify the cluster is running Aerospike Enterprise Edition.\n"
                    "2. Ensure `security_stats_ingest_ci.py` is included in the ingestion pipeline."
                )
            }

        # ---------------------------------------------------------------------
        # 2. ANALYSIS LOGIC
        # ---------------------------------------------------------------------
        query = "SELECT user, SUM(connections) as total_conns FROM security_stats GROUP BY user"
        df = pd.read_sql_query(query, conn)
        
        if df.empty or df['total_conns'].sum() == 0:
            return {
                "id": check_id, 
                "name": check_name, 
                "status": "PASS", 
                "message": "No active client connections detected via ACL telemetry."
            }

        total_cluster_conns = df['total_conns'].sum()
        df['pct'] = (df['total_conns'] / total_cluster_conns) * 100
        df = df.sort_values(by='pct', ascending=False)
        
        top_user_row = df.iloc[0]
        top_user = top_user_row['user']
        top_pct = int(top_user_row['pct'])
        top_count = int(top_user_row['total_conns'])

        # ---------------------------------------------------------------------
        # 3. STATUS & REMEDIATION (The Template "Finding")
        # ---------------------------------------------------------------------
        if top_pct > 80 and top_count > 100:
            status = "WARNING"
            message = f"Connection Monopoly: User [{top_user}] holds {top_pct}% of cluster connections ({top_count})."
        else:
            status = "PASS"
            message = f"Connection distribution is healthy. Top user: {top_user} ({top_pct}%)."

        return {
            "id": check_id,
            "name": check_name,
            "status": status,
            "message": message,
            "remediation": (
                "**Assessment:** A single user account monopolizing client connections can lead to 'Service Unavailable' "
                "errors for other applications and administrative tools (asadm/asinfo).\n\n"
                "**Action Plan:**\n"
                f"1. Audit the connection pooling configuration for the application using the **{top_user}** account.\n"
                "2. Ensure client SDKs are using a max connection limit that aligns with the cluster's `proto-fd-max` setting.\n"
                "3. Check for 'connection leaks' in long-running application processes."
            )
        }

    except Exception as e:
        return {
            "id": check_id, 
            "name": check_name, 
            "status": "CRITICAL", 
            "message": f"Execution Error: {str(e)}",
            "remediation": "Contact the Tooling Team to verify the `security_stats` schema compatibility."
        }
    finally:
        conn.close()