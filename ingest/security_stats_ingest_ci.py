import sqlite3

# -----------------------------------------------------------------------------
# VERSION STAMP
# -----------------------------------------------------------------------------
__version__ = "1.5.4"

class SecurityStatsIngestor:
    """
    Processes as_stat.acl (users and connections) from collectinfo.
    Aligned with INGEST-TEMPLATE.md requirements.
    """
    def run_ingest(self, node_id, node_data, conn, run_id):
        cursor = conn.cursor()

        # 1. Ensure Table Exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_stats (
                node_id TEXT, 
                user TEXT, 
                connections INTEGER, 
                run_id TEXT,
                PRIMARY KEY (node_id, user, run_id)
            )
        """)

        # 2. Extract Data (Navigate the 7.x JSON path: as_stat -> acl -> users)
        acl_data = node_data.get("as_stat", {}).get("acl", {})
        users = acl_data.get("users", {})
        
        # 3. Persist
        for username, user_metrics in users.items():
            conns = user_metrics.get("connections", 0)
            cursor.execute("""
                INSERT OR REPLACE INTO security_stats (node_id, user, connections, run_id)
                VALUES (?, ?, ?, ?)
            """, (node_id, username, conns, run_id))