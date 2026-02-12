import subprocess
import sys
import os

# =============================================================================
# CONFIGURATION - Set for v1.6.0 Modular Release
# =============================================================================
NEW_VERSION  = "1.6.0"
TAG_SUFFIX   = "stable"
REMOTE_PUSH  = "origin"
BRANCH_NAME  = "main"
CLEAN_DB     = True
TEST_BUNDLE  = "bundles/aws-common.collect_info_20260120_230014.tgz"
# =============================================================================

def run_cmd(cmd, silent=False):
    if not silent:
        print(f"🏃 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ ERROR: {result.stderr}")
        return False
    return True

def commit_pipeline():
    print(f"🚀 Starting Standardized Git Pipeline for v{NEW_VERSION}...")

    if CLEAN_DB:
        print("\n🧹 Cleaning old database and re-ingesting...")
        if os.path.exists("aerospike_health.db"):
            os.remove("aerospike_health.db")
        if not run_cmd(["python3", "run_ingest.py", TEST_BUNDLE]):
            print("🛑 ABORTING: Ingestion failed.")
            return

    if not run_cmd(["python3", "check_integrity.py"]):
        print("🛑 ABORTING: Integrity check failed.")
        return

    print("\n📦 Phase 1: Locking Core Engine...")
    run_cmd(["git", "add", "run_ingest.py", "ingest_manager.py", "discovery.py", "set_version.py"])
    run_cmd(["git", "add", "ingest/"])
    run_cmd(["git", "commit", "-m", f"BASE: Core Engine (v{NEW_VERSION})"])

    print("\n🧠 Phase 2: Locking Ruleset...")
    run_cmd(["git", "add", "rules/"])
    run_cmd(["git", "add", "check_integrity.py", "commit_baseline.py"])
    run_cmd(["git", "commit", "-m", f"LOGIC: Ruleset (v{NEW_VERSION})"])

    print("\n📄 Phase 3: Locking Presentation Layer (Modular)...")
    # Captures report.qmd AND all included .qmd modules
    run_cmd(["git", "add", "*.qmd", "_setup.qmd", "CATALOG.md", "README.md", "_quarto.yml"])
    run_cmd(["git", "commit", "-m", f"DOCS: Modular Report Architecture (v{NEW_VERSION})"])

    tag_name = f"v{NEW_VERSION}-{TAG_SUFFIX}"
    print(f"\n🏷️ Phase 4: Tagging as {tag_name}...")
    subprocess.run(["git", "tag", "-d", tag_name], capture_output=True)
    run_cmd(["git", "tag", "-a", tag_name, "-m", f"Aerospike Health Analyzer v{NEW_VERSION}"])
    
    print(f"\n✨ v{NEW_VERSION} is staged locally.")
    confirm = input(f"❓ Push to {REMOTE_PUSH} {BRANCH_NAME} now? (y/n): ")
    if confirm.lower() == 'y':
        run_cmd(["git", "push", REMOTE_PUSH, BRANCH_NAME, "--tags", "-f"])
        print(f"✅ Pushed successfully.")

if __name__ == "__main__":
    commit_pipeline()