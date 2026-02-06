__version__ = "1.3.0"
import sqlite3
import re

def run_ingest(node_id, sys_stat, conn, timestamp):
    """
    Parses sys_stat to identify ENA driver status.
    In Aerospike collectinfo, sys_stat often contains a 'network' 
    or 'lsmod' key with raw text output.
    """
    cursor = conn.cursor()
    
    # Ensure the node_stats table can handle our system metric
    # (Assuming node_stats is a standard metric/value/timestamp table)
    
    # 1. Check for ENA in 'ethtool' or 'lsmod' output
    # We look for the 'ena' driver string in any system-level text blob
    ena_active = 0
    
    # We search common keys in sys_stat where network driver info lives
    search_keys = ['network', 'lsmod', 'ethtool', 'interrupts']
    
    for key in search_keys:
        blob = str(sys_stat.get(key, ""))
        # Regex to find 'ena' as a standalone word (driver name)
        if re.search(r'\bena\b', blob, re.IGNORECASE):
            ena_active = 1
            break
            
    # 2. Insert the result into node_stats as a virtual metric
    cursor.execute("""
        INSERT OR REPLACE INTO node_stats (node_id, metric, value, timestamp)
        VALUES (?, ?, ?, ?)
    """, (node_id, 'system.network.ena_enabled', ena_active, timestamp))
    
    # Debug print for your test module
    status = "ENA Found" if ena_active else "ENA Missing"
    # print(f"  [System Ingest] Node {node_id}: {status}")