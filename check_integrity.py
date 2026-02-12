import os
import sys
import sqlite3
import importlib

# -----------------------------------------------------------------------------
# VERSION STAMP
# -----------------------------------------------------------------------------
__version__ = "1.6.0"

def verify():
    db_path = "aerospike_health.db"
    if not os.path.exists(db_path):
        print(f"❌ FAILED: {db_path} not found. Run ingestion first.")
        return False

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