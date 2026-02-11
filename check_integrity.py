import os
import sys
import sqlite3
import importlib

# -----------------------------------------------------------------------------
# VERSION STAMP
# -----------------------------------------------------------------------------
__version__ = "1.4.1"

def verify():
    db_path = "aerospike_health.db"
    if not os.path.exists(db_path):
        print(f"❌ FAILED: {db_path} not found. Run ingestion first.")
        return False

    # Define the ruleset to check
    # We import them here to ensure we are testing the actual installed modules
    try:
        from rules import (
            error_skew_check, version_consistency_check, network_acceleration_check,
            deadlock_check, sindex_check, sprigs_check, hwm_check,
            memory_hwm_check, config_symmetry_check, config_drift_check,
            hot_key_check, read_not_found_check, delete_not_found_check,
            set_object_skew_check, capacity_check
        )
    except ImportError as e:
        print(f"❌ FAILED: Could not import rules. {e}")
        return False

    REQUIRED_RULES = [
        error_skew_check, version_consistency_check, network_acceleration_check,
        deadlock_check, sindex_check, sprigs_check, hwm_check,
        memory_hwm_check, config_symmetry_check, config_drift_check,
        hot_key_check, read_not_found_check, delete_not_found_check,
        set_object_skew_check, capacity_check
    ]

    print(f"--- Integrity Check: Validating {len(REQUIRED_RULES)} Rules ---")
    errors = 0
    
    for rule in REQUIRED_RULES:
        rule_name = getattr(rule, "__name__", str(rule))
        try:
            # Run the check against the live database
            # We are looking for SQL execution errors (Schema Mismatches)
            res = rule.run_check(db_path)
            
            # If the rule returns a message containing "Error" or "no such column", it's a fail
            msg = res.get('message', '')
            if "Error" in msg or "no such" in msg.lower():
                print(f"❌ {rule_name:<30} | SCHEMA ERROR: {msg}")
                errors += 1
            else:
                print(f"✅ {rule_name:<30} | Logic OK ({res['status']})")
                
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