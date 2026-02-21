import os
import re
from datetime import datetime

# =============================================================================
# CONFIGURATION - Global Version for v2.0.1
# =============================================================================
NEW_VERSION = "2.0.1"
DATE_STR    = datetime.now().strftime("%Y-%m-%d")

# This script will scan these file types across the entire project
TARGET_EXTENSIONS = (".py", ".qmd")
# These documentation files receive specialized regex updates
DOC_FILES = ["CATALOG.md", "README.md"]
# =============================================================================

def update_file_content(content):
    """Updates version strings for both Python logic and Quarto setups."""
    # Matches: __version__ = "2.0.1"
    if "__version__" in content:
        content = re.sub(r'__version__\s*=\s*["\'].*?["\']', f'__version__ = "2.0.1"', content)
    # Matches: PROJECT_VERSION = "2.0.1" (used in _setup.qmd)
    if "PROJECT_VERSION" in content:
        content = re.sub(r'PROJECT_VERSION\s*=\s*["\'].*?["\']', f'PROJECT_VERSION = "2.0.1"', content)
    return content

def process_project():
    """Recursively updates all modules, rules, and report components."""
    print(f"🚀 Syncing project to v{NEW_VERSION}...")

    for root, dirs, files in os.walk("."):
        # Safety: Ignore environment and build artifacts
        for ignore in ['.venv', 'node_modules', '__pycache__', '_site', '.git']:
            if ignore in dirs:
                dirs.remove(ignore)

        for filename in files:
            if filename.endswith(TARGET_EXTENSIONS):
                path = os.path.join(root, filename)
                
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = update_file_content(content)
                
                if new_content != content:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"  ✅ Updated: {path}")

    # Update Documentation Headers and Footers
    for doc in DOC_FILES:
        if os.path.exists(doc):
            with open(doc, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Updates 'v1.X.X' patterns and 'YYYY-MM-DD' datestamps
            content = re.sub(r'v\d+\.\d+\.\d+', f'v{NEW_VERSION}', content)
            content = re.sub(r'\d{4}-\d{2}-\d{2}', DATE_STR, content)
            
            with open(doc, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  📑 Updated Doc: {doc}")

if __name__ == "__main__":
    process_project()
    print(f"\n✨ Global version synchronization to v{NEW_VERSION} complete.")