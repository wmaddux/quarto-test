#!/usr/bin/env python3
"""
End-to-end test: run ingestion then integrity check.
Exit code = integrity result (0 = pass, 1 = fail).

Usage:
  python3 tests/run_e2e.py <path_to_bundle.tgz>
  python3 tests/run_e2e.py              # uses AEROSPIKE_E2E_BUNDLE env var if set

For a fast change→test loop, set AEROSPIKE_E2E_BUNDLE to a fixture bundle path
so you don't have to pass the path each time.
"""
import os
import sys
import subprocess

def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(repo_root)

    bundle = (sys.argv[1:] and sys.argv[1]) or os.environ.get("AEROSPIKE_E2E_BUNDLE")
    if not bundle:
        print("❌ Usage: python3 tests/run_e2e.py <path_to_bundle.tgz>")
        print("   Or set AEROSPIKE_E2E_BUNDLE to a fixture bundle path.")
        sys.exit(2)
    if not os.path.exists(bundle):
        print(f"❌ Bundle not found: {bundle}")
        sys.exit(2)

    # 1. Ingest
    r = subprocess.run([sys.executable, "run_ingest.py", bundle], cwd=repo_root)
    if r.returncode != 0:
        print("\n🛑 FAIL: Ingestion failed.")
        sys.exit(1)

    # 2. Integrity (schema + rules)
    r = subprocess.run([sys.executable, "check_integrity.py"], cwd=repo_root)
    sys.exit(r.returncode)

if __name__ == "__main__":
    main()
