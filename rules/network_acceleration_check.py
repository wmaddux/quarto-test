import sqlite3
import pandas as pd

__version__ = "1.4.0"

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    check_id = "1.b"
    check_name = "Network Acceleration Check"
    target_table = "sys_stats"
    
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{target_table}'")
        if not cursor.fetchone():
            return {
                "id": check_id, "name": check_name, "status": "WARNING",
                "message": "System telemetry (sys_stats) is missing from the bundle.",
                "remediation": (
                    "**Why this matters:** Without system-level telemetry, we cannot verify if hardware interrupt "
                    "queues or optimized network drivers (ENA) are active.\n\n"
                    "**Action Plan:**\n"
                    "1. Re-run the collection with system metrics enabled: `asadm -e \"collectinfo\"`.\n"
                    "2. Ensure the user running the command has permissions to execute `ethtool`, `lsmod`, and `top`.\n"
                    "3. If using Docker, ensure the container has visibility into the host network stack."
                )
            }

        query = f"SELECT node_id, value FROM {target_table} WHERE metric = 'network_driver'"
        df = pd.read_sql_query(query, conn)
        
        cursor.execute("SELECT value FROM cluster_metadata WHERE key = 'cloud_platform'")
        platform = (cursor.fetchone() or ["Unknown"])[0]

        if "AWS" in platform.upper():
            if df.empty or not df['value'].str.contains('ena|vfio-pci').any():
                return {
                    "id": check_id, "name": check_name, "status": "WARNING",
                    "message": "Optimized network drivers (ENA/vfio-pci) not detected on AWS instances.",
                    "remediation": (
                        "**Why this matters:** Standard drivers introduce high interrupt latency. AWS ENA is "
                        "required for consistent low-latency performance.\n\n"
                        "**Action Plan:**\n"
                        "1. Verify ENA support on your EC2 instance type.\n"
                        "2. Ensure the driver is active in the OS: `modinfo ena`.\n"
                        "3. Update the AMI if ENA is not supported."
                    )
                }

        return {
            "id": check_id, "name": check_name, "status": "PASS",
            "message": f"Network acceleration is correctly configured for {platform}.",
            "remediation": "None"
        }
    except Exception as e:
        return {"id": check_id, "name": check_name, "status": "CRITICAL", "message": f"Error: {str(e)}"}
    finally:
        conn.close()