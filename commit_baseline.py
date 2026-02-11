import subprocess
import sys
import os

# =============================================================================
# CONFIGURATION - Set these for each release
# =============================================================================
NEW_VERSION  = "1.4.1"
TAG_SUFFIX   = "stable"
REMOTE_PUSH  = "origin"
BRANCH_NAME  = "main"
CLEAN_DB     = True  # If True, deletes .db and re-runs ingestion before commit
TEST_BUNDLE  = "bundles/aws-common.collect_info_20260120_230014.tgz"
# =============================================================================

def run_cmd(cmd, silent=False):
    """Executes a shell command and returns success status."""
    if not silent:
        print(f"🏃 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ ERROR: {result.stderr}")
        return False
    return True

def commit_pipeline():
    print(f"🚀 Starting Standardized Git Pipeline for v{NEW_VERSION}...")

    # --- 1. Fresh Data Validation ---
    if CLEAN_DB:
        print("\n🧹 Cleaning old database and re-ingesting...")
        if os.path.exists("aerospike_health.db"):
            os.remove("aerospike_health.db")
        
        if not run_cmd(["python3", "run_ingest.py", TEST_BUNDLE]):
            print("🛑 ABORTING: Ingestion failed. Commit stopped.")
            return

    # --- 2. Integrity Pre-Flight ---
    if not run_cmd(["python3", "check_integrity.py"]):
        print("🛑 ABORTING: Integrity check failed. Fix the rules before committing.")
        return

    # --- 3. Phase 1: Core Engine & Ingestors ---
    print("\n📦 Phase 1: Locking Core Engine...")
    run_cmd(["git", "add", "run_ingest.py", "ingest_manager.py", "discovery.py", "set_version.py"])
    run_cmd(["git", "add", "ingest/"])
    run_cmd(["git", "commit", "-m", f"BASE: Modernized Ingestors & Core Engine (v{NEW_VERSION})"])

    # --- 4. Phase 2: Ruleset ---
    print("\n🧠 Phase 2: Locking Ruleset...")
    run_cmd(["git", "add", "rules/"])
    run_cmd(["git", "add", "check_integrity.py", "commit_baseline.py"]) # Include this script
    run_cmd(["git", "commit", "-m", f"LOGIC: Verified Ruleset with Schema Safety (v{NEW_VERSION})"])

    # --- 5. Phase 3: Presentation & Docs ---
    print("\n📄 Phase 3: Locking Presentation Layer...")
    run_cmd(["git", "add", "report.qmd", "CATALOG.md", "README.md", "_quarto.yml"])
    run_cmd(["git", "commit", "-m", f"DOCS: Updated Master Catalog and Report Template (v{NEW_VERSION})"])

    # --- 6. Tagging ---
    tag_name = f"v{NEW_VERSION}-{TAG_SUFFIX}"
    print(f"\n🏷️ Phase 4: Tagging as {tag_name}...")
    subprocess.run(["git", "tag", "-d", tag_name], capture_output=True) # Clear local tag if exists
    run_cmd(["git", "tag", "-a", tag_name, "-m", f"Aerospike Health Analyzer v{NEW_VERSION} verified {TAG_SUFFIX}"])
    
    print(f"\n✨ v{NEW_VERSION} is staged and committed locally.")
    
    confirm = input(f"❓ Push to {REMOTE_PUSH} {BRANCH_NAME} now? (y/n): ")
    if confirm.lower() == 'y':
        run_cmd(["git", "push", REMOTE_PUSH, BRANCH_NAME, "--tags", "-f"])
        print(f"✅ Pushed to {REMOTE_PUSH} successfully.")
    else:
        print("💡 Commit saved locally. Remember to push when ready.")

if __name__ == "__main__":
    commit_pipeline()
