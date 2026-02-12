import sqlite3
import pandas as pd

__version__ = "1.6.0"

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    check_id = "3.b"
    check_name = "Config Drift"
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='static_configs'")
        if not cursor.fetchone():
            return {
                "id": check_id, "name": check_name, "status": "⚠️ DATA MISSING",
                "message": "The static aerospike.conf file was not found in the collectinfo bundle.",
                "remediation": (
                    "**Why this matters:** We cannot compare live settings against your config file if the file wasn't bundled.\n\n"
                    "**Action Plan:**\n"
                    "1. Re-run collectinfo and explicitly point to your config file:\n"
                    "   `asadm -e \"collectinfo --cf /etc/aerospike/aerospike.conf\"`\n"
                    "2. If your config is in a custom location, update the path in the command above."
                )
            }

        query = """
            SELECT l.node_id, l.config_name, l.value as live_val, s.value as static_val
            FROM node_configs l
            JOIN static_configs s ON l.node_id = s.node_id AND l.config_name = s.config_name
            WHERE l.value != s.value
        """
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            return {
                "id": check_id, "name": check_name, "status": "PASS",
                "message": "Live running configuration matches the static aerospike.conf file.",
                "remediation": "None"
            }

        example_drifts = df['config_name'].unique()[:3]
        return {
            "id": check_id, "name": check_name, "status": "WARNING",
            "message": f"Detected {len(df)} parameters where the running config differs from the .conf file.",
            "remediation": (
                "**Why this matters:** Runtime changes are lost on reboot. Your config file is currently stale.\n\n"
                f"**Impacted Keys include:** {', '.join(example_drifts)}.\n\n"
                "**Action Plan:**\n"
                "1. Update `/etc/aerospike/aerospike.conf` to match the intended runtime values.\n"
                "2. Use a configuration management tool to ensure consistency across nodes."
            )
        }
    except Exception as e:
        return {"id": check_id, "name": check_name, "status": "CRITICAL", "message": f"Error: {str(e)}"}
    finally:
        conn.close()