import subprocess
import os

# =============================================================================
# CONFIGURATION - Set for v1.6.1 Patch Release
# =============================================================================
NEW_VERSION  = "1.6.1"
TAG_SUFFIX   = "stable"
REMOTE_PUSH  = "origin"
BRANCH_NAME  = "main"
# =============================================================================

def run_cmd(cmd):
    """Executes a shell command and returns success status."""
    print(f"🏃 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ ERROR: {result.stderr}")
        return False
    return True

def commit_pipeline():
    print(f"🚀 Starting Git Baseline Pipeline for v{NEW_VERSION}...")

    # --- 1. Phase 1: Core Engine & Ingestors ---
    print("\n📦 Phase 1: Locking Core Engine...")
    run_cmd(["git", "add", "run_ingest.py", "ingest_manager.py", "set_version.py"])
    run_cmd(["git", "add", "ingest/"])
    run_cmd(["git", "commit", "-m", f"BASE: Core Engine & Ingestors (v{NEW_VERSION})"])

    # --- 2. Phase 2: Logic & Ruleset ---
    print("\n🧠 Phase 2: Locking Ruleset...")
    run_cmd(["git", "add", "rules/"])
    # Note: check_integrity.py and discovery.py included if they are in root
    run_cmd(["git", "add", "check_integrity.py", "commit_baseline.py"])
    run_cmd(["git", "commit", "-m", f"LOGIC: Multi-Version Ruleset (v{NEW_VERSION})"])

    # --- 3. Phase 3: Presentation Layer (Modular) ---
    print("\n📄 Phase 3: Locking Modular Report Components...")
    run_cmd(["git", "add", "report.qmd", "_setup.qmd", "CATALOG.md", "README.md", "_quarto.yml"])
    run_cmd(["git", "add", "report_components/"]) 
    run_cmd(["git", "commit", "-m", f"DOCS: Modular Report Architecture (v{NEW_VERSION})"])

    # --- 4. Tagging ---
    tag_name = f"v{NEW_VERSION}-{TAG_SUFFIX}"
    print(f"\n🏷️ Phase 4: Tagging as {tag_name}...")
    subprocess.run(["git", "tag", "-d", tag_name], capture_output=True) # Clean local
    run_cmd(["git", "tag", "-a", tag_name, "-m", f"Aerospike Health Analyzer v{NEW_VERSION} modular stable"])
    
    print(f"\n✨ v{NEW_VERSION} is staged and committed locally.")
    
    confirm = input(f"❓ Push to {REMOTE_PUSH} {BRANCH_NAME} now? (y/n): ")
    if confirm.lower() == 'y':
        run_cmd(["git", "push", REMOTE_PUSH, BRANCH_NAME, "--tags", "-f"])
        print(f"✅ Pushed to {REMOTE_PUSH} successfully.")
    else:
        print("💡 Commit saved locally. Remember to push to remote when ready.")

if __name__ == "__main__":
    commit_pipeline()