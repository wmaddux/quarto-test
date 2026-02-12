import sqlite3
import pandas as pd

# -----------------------------------------------------------------------------
# VERSION STAMP
# -----------------------------------------------------------------------------
__version__ = "1.6.0"

def run_check(db_path):
    """
    ID: 4.f - Set Object Skew
    Description: Node-level object count deviation for specific sets.
    """
    # Standard Rule Metadata for Report logic
    rule_meta = {"id": "4.f", "name": "Set Object Skew"}
    
    try:
        conn = sqlite3.connect(db_path)
        query = """
        SELECT node_id, ns, set_name, CAST(value AS FLOAT) as objects
        FROM set_stats 
        WHERE key = 'objects'
        """
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            return {
                **rule_meta,
                "status": "PASS", 
                "message": "No set-level object data found to analyze."
            }

        findings = []
        for (ns, set_n), group in df.groupby(['ns', 'set_name']):
            if len(group) < 2: continue
            avg_objects = group['objects'].mean()
            if avg_objects < 1000: continue
            
            group['deviation_pct'] = (abs(group['objects'] - avg_objects) / avg_objects) * 100
            max_skew = group['deviation_pct'].max()

            if max_skew > 10:
                findings.append(f"{ns}:{set_n} ({max_skew:.1f}% skew)")

        if findings:
            return {
                **rule_meta,
                "status": "WARNING",
                "message": f"High object skew detected in sets: {', '.join(findings)}"
            }

        return {
            **rule_meta,
            "status": "PASS",
            "message": "Set object distribution is balanced across nodes."
        }

    except Exception as e:
        return {
            **rule_meta,
            "status": "SCHEMA MISMATCH", 
            "message": f"Analysis failed: {str(e)}"
        }