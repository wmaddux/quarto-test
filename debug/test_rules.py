__version__ = "2.0.1"
#!/usr/bin/env python3
from rules.network_acceleration_check import run_check as ena_check
from rules.version_consistency_check import run_check as version_check

def run_suite():
    db = "aerospike_health.db"
    print("\n🚀 v1.3.0 End-to-End Sandbox Test")
    print("="*40)
    
    for check in [ena_check, version_check]:
        res = check(db)
        print(f"[{res['status']}] {res['name']}")
        print(f"Details: {res['message']}")
        if 'remediation' in res:
            print(f"Action: {res['remediation']}")
        print("-" * 40)

if __name__ == "__main__":
    run_suite()