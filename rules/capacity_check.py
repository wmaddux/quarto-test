import sqlite3
import pandas as pd

__version__ = "1.5.4"

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    check_id = "2.f"
    check_name = "Cluster Capacity Forecast"
    
    try:
        query = """
            SELECT metric, CAST(value AS REAL) as val
            FROM namespace_stats 
            WHERE metric LIKE '%data_used_pct%' OR metric LIKE '%memory_used_pct%'
        """
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            return {"id": check_id, "name": check_name, "status": "PASS", "message": "Cluster resources are within nominal limits."}

        peak_usage = df['val'].max()
        
        if peak_usage > 85:
            status = "CRITICAL"
            msg = f"Critical Resource Pressure: Cluster peak utilization is at {int(peak_usage)}%."
        elif peak_usage > 70:
            status = "WARNING"
            msg = f"Expansion Planning Required: Cluster peak utilization is at {int(peak_usage)}%."
        else:
            status = "PASS"
            msg = f"Resource utilization is healthy. Peak consumption is currently {int(peak_usage)}%."

        return {
            "id": check_id, "name": check_name, "status": status, "message": msg,
            "remediation": (
                "**Assessment:** Monitoring peak utilization across Disk and RAM is vital for maintaining "
                "availability. High utilization leaves little room for node failures or unexpected traffic spikes.\n\n"
                "**Action Plan:**\n"
                "1. If utilization exceeds 70%, begin planning for a cluster expansion.\n"
                "2. Review the 'Namespace Usage' tables in this report to identify the primary drivers of growth."
            )
        }
    except Exception as e:
        return {"id": check_id, "name": check_name, "status": "CRITICAL", "message": f"Error: {str(e)}"}
    finally:
        conn.close()