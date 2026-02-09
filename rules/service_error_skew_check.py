import sqlite3
__version__ = "1.4.0"

def run_check(db_path="aerospike_health.db"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Query to find nodes where specific errors are significantly higher than the average
    # We focus on general service errors as highlighted in the wellness report
    query = """
    WITH ErrorStats AS (
        SELECT 
            metric, 
            AVG(value) as avg_val,
            MAX(value) as max_val
        FROM node_stats
        WHERE metric LIKE 'batch_index_error' OR metric LIKE 'client_proxy_error'
        GROUP BY metric
    )
    SELECT 
        n.node_id, 
        n.metric, 
        n.value, 
        e.avg_val
    FROM node_stats n
    JOIN ErrorStats e ON n.metric = e.metric
    WHERE n.value > (e.avg_val * 2) AND n.value > 10
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return {
            "id": "1.a", "name": "Service Error Skew",
            "status": "PASS",
            "message": "Service error counts are consistent across the cluster."
        }

    findings = [f"{r['metric']} on {r['node_id']} (Value: {r['value']} vs Avg: {r['avg_val']:.1f})" for r in rows]
    
    return {
        "id": "1.a",  # Added missing ID to match your template
        "name": "Service Error Skew",
        "status": "WARNING",
        "message": f"Skewed error patterns detected: {'; '.join(findings)}",
        "remediation": "Investigate network stability or hardware health on the outlier nodes. Skewed errors often precede node failure or indicate localized congestion."
    }
