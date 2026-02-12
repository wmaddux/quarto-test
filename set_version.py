import os
import re
from datetime import datetime

# --- CONFIGURATION ---
NEW_VERSION = "1.6.0"
TARGET_DIRS = ["rules", "ingest"] 
ROOT_PYTHON_FILES = ["run_ingest.py", "ingest_manager.py", "discovery.py", "check_integrity.py"]
DATE_STR = datetime.now().strftime("%Y-%m-%d")

def update_file_content(content):
    """Core logic to update version strings based on variable names."""
    if "__version__" in content:
        content = re.sub(r'__version__\s*=\s*["\'].*?["\']', f'__version__ = "1.6.0"', content)
    if "PROJECT_VERSION" in content:
        content = re.sub(r'PROJECT_VERSION\s*=\s*["\'].*?["\']', f'PROJECT_VERSION = "1.6.0"', content)
    return content

def process_files():
    """Update all relevant Python and Quarto files."""
    for root, _, files in os.walk("."):
        for filename in files:
            # Target both engine logic and the new modular report files
            if filename.endswith(".py") or filename.endswith(".qmd"):
                path = os.path.join(root, filename)
                with open(path, 'r') as f:
                    content = f.read()
                
                new_content = update_file_content(content)
                
                if new_content != content:
                    with open(path, 'w') as f:
                        f.write(new_content)
                    print(f"✅ Updated Version: {path}")

    # Update Documentation
    for doc in ["CATALOG.md", "README.md"]:
        if os.path.exists(doc):
            with open(doc, 'r') as f:
                content = f.read()
            content = re.sub(r'v\d+\.\d+\.\d+', f'v{NEW_VERSION}', content)
            content = re.sub(r'\d{4}-\d{2}-\d{2}', DATE_STR, content)
            with open(doc, 'w') as f:
                f.write(content)
            print(f"✅ Updated Documentation: {doc}")

if __name__ == "__main__":
    print(f"🚀 Global Version Sync to v{NEW_VERSION}...")
    process_files()
    print(f"✨ Sync Complete.")