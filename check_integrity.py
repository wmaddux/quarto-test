import os
import sys
import sqlite3
import importlib

# -----------------------------------------------------------------------------
# VERSION STAMP
# -----------------------------------------------------------------------------
__version__ = "1.6.1"

def _get_schema_from_db(conn):
    """Return dict: table_name -> list of (column_name, type)."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    out = {}
    for t in tables:
        cursor.execute(f"PRAGMA table_info({t})")
        out[t] = [(row[1], row[2]) for row in cursor.fetchall()]
    return out

def _validate_schema_against_baseline(db_path):
    """Ensure live DB schema matches schema/baseline.sql. Return (True, None) or (False, error_msg)."""
    baseline_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema", "baseline.sql")
    if not os.path.exists(baseline_path):
        return False, f"Schema baseline not found: {baseline_path}"
    with open(baseline_path, "r") as f:
        baseline_sql = f.read()
    # Build expected schema by running baseline on an in-memory DB
    mem = sqlite3.connect(":memory:")
    try:
        mem.executescript(baseline_sql)
        expected = _get_schema_from_db(mem)
    finally:
        mem.close()
    # Get actual schema from live DB
    if not os.path.exists(db_path):
        return False, f"{db_path} not found. Run ingestion first."
    conn = sqlite3.connect(db_path)
    try:
        actual = _get_schema_from_db(conn)
    finally:
        conn.close()
    # Compare
    if set(expected.keys()) != set(actual.keys()):
        missing = set(expected.keys()) - set(actual.keys())
        extra = set(actual.keys()) - set(expected.keys())
        msg = []
        if missing:
            msg.append(f"missing tables: {sorted(missing)}")
        if extra:
            msg.append(f"extra tables: {sorted(extra)}")
        return False, "Schema mismatch: " + "; ".join(msg)
    for table in expected:
        if expected[table] != actual[table]:
            return False, f"Schema mismatch in table '{table}': expected columns {expected[table]}, got {actual[table]}"
    return True, None

def verify():
    db_path = "aerospike_health.db"
    if not os.path.exists(db_path):
        print(f"❌ FAILED: {db_path} not found. Run ingestion first.")
        return False

    ok, err = _validate_schema_against_baseline(db_path)
    if not ok:
        print(f"❌ FAILED: {err}")
        return False
    print("✅ Schema matches schema/baseline.sql")

    # Define the ruleset to check
    try:
        from rules import (
            error_skew_check, version_consistency_check, network_acceleration_check,
            storage_deadlock_check, sindex_on_flash_check, sprig_limit_check, hwm_check,
            memory_hwm_check, config_symmetry_check, config_drift_check,
            hot_key_check, read_not_found_check, delete_not_found_check,
            set_object_skew_check, capacity_check,
            security_connection_audit  # Added incrementally
        )
    except ImportError as e:
        print(f"❌ FAILED: Could not import rules. {e}")
        return False

    REQUIRED_RULES = [
        error_skew_check, version_consistency_check, network_acceleration_check,
        storage_deadlock_check, sindex_on_flash_check, sprig_limit_check, hwm_check,
        memory_hwm_check, config_symmetry_check, config_drift_check,
        hot_key_check, read_not_found_check, delete_not_found_check,
        set_object_skew_check, capacity_check,
        security_connection_audit  # Added to validation list
    ]

    print(f"--- Integrity Check: Validating {len(REQUIRED_RULES)} Rules ---")
    errors = 0
    
    # ... inside your for rule in REQUIRED_RULES loop ...
    for rule in REQUIRED_RULES:
        rule_name = getattr(rule, "__name__", str(rule))
        try:
            res = rule.run_check(db_path)
            rid = res.get('id', '??')  # Get the ID from the rule output
            
            msg = res.get('message', '')
            if "Error" in msg or "no such" in msg.lower():
                print(f"❌ {rid:<5} | {rule_name:<30} | SCHEMA ERROR: {msg}")
                errors += 1
            else:
                print(f"✅ {rid:<5} | {rule_name:<30} | Logic OK ({res['status']})")
                
        except Exception as e:
            print(f"💥 {rule_name:<30} | CRASHED: {str(e)}")
            errors += 1
    
    return errors == 0

if __name__ == "__main__":
    if verify():
        print("\n✨ PASS: Project integrity is sound. Safe to render report.")
        sys.exit(0)
    else:
        print("\n🛑 FAIL: Integrity issues detected. Fix the rules/schema above.")
        sys.exit(1)