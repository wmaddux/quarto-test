import sqlite3
import pandas as pd

__version__ = "1.4.2"

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    check_id = "4.f"
    check_name = "Set Object Skew"
    
    try:
        # Dynamic Schema Discovery: Find the correct namespace column name
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(set_stats)")
        cols = [column[1] for column in cursor.fetchall()]
        ns_col = "ns" if "ns" in cols else "ns_name" if "ns_name" in cols else "namespace"
        
        query = f"""
            SELECT node_id, {ns_col} as ns_name, set_name, CAST(value AS REAL) as objects
            FROM set_stats 
            WHERE metric = 'objects' AND set_name != ''
        """
        df = pd.read_sql_query(query, conn)
        
        if df.empty or df['objects'].sum() < 50000:
            return {"id": check_id, "name": check_name, "status": "PASS", 
                    "message": "Data distribution is balanced across all sets.", "remediation": "None"}

        set_groups = df.groupby(['ns_name', 'set_name'])
        skewed_sets = []

        for name, group in set_groups:
            mean_obj = group['objects'].mean()
            max_obj = group['objects'].max()
            if max_obj > (mean_obj * 1.20) and mean_obj > 1000:
                skewed_sets.append(f"{name[1]} (Max: {int(max_obj)}, Avg: {int(mean_obj)})")

        if skewed_sets:
            return {
                "id": check_id, "name": check_name, "status": "WARNING",
                "message": f"Significant data skew detected in set(s): {', '.join(skewed_sets)}.",
                "remediation": (
                    "**Assessment:** Unbalanced sets lead to 'hot nodes' where individual servers handle "
                    "disproportionate storage and IO load.\n\n"
                    "**Action Plan:**\n"
                    "1. Verify if the cluster is currently undergoing migrations.\n"
                    "2. Use `asadm -e 'show statistics set'` to identify if the skew is persistent."
                )
            }

        return {"id": check_id, "name": check_name, "status": "PASS",
                "message": "All database sets are distributed evenly across the cluster nodes.",
                "remediation": "None"}
    except Exception as e:
        return {"id": check_id, "name": check_name, "status": "CRITICAL", "message": f"Error: {str(e)}"}
    finally:
        conn.close()