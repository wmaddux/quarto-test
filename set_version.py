import os
import re
from datetime import datetime

# --- CONFIGURATION ---
NEW_VERSION = "1.4.0"
TARGET_DIRS = [".", "rules", "ingest"] 
DATE_STR = datetime.now().strftime("%Y-%m-%d")

def update_python_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != "set_version.py":
            path = os.path.join(directory, filename)
            with open(path, 'r') as f:
                content = f.read()
            
            # Update or Add __version__
            if "__version__" in content:
                content = re.sub(r'__version__\s*=\s*".*?"', f'__version__ = "{NEW_VERSION}"', content)
            else:
                content = f'__version__ = "{NEW_VERSION}"\n' + content
                
            with open(path, 'w') as f:
                f.write(content)
            print(f"✅ Updated Version: {path}")

def update_markdown_and_qmd():
    # 1. Update report.qmd
    if os.path.exists("report.qmd"):
        with open("report.qmd", 'r') as f:
            content = f.read()
        content = re.sub(r'PROJECT_VERSION\s*=\s*["\'].*?["\']', f'PROJECT_VERSION = "{NEW_VERSION}"', content)
        with open("report.qmd", 'w') as f:
            f.write(content)
        print("✅ Updated Version: report.qmd")

    # 2. Update CATALOG.md
    if os.path.exists("CATALOG.md"):
        with open("CATALOG.md", 'r') as f:
            content = f.read()
        content = re.sub(r'\*\*Baseline:\*\* v.*', f'**Baseline:** v{NEW_VERSION}', content)
        content = re.sub(r'\*\*Last Updated:\*\* \d{4}-\d{2}-\d{2}', f'**Last Updated:** {DATE_STR}', content)
        with open("CATALOG.md", 'w') as f:
            f.write(content)
        print("✅ Updated Version & Date: CATALOG.md")

    # 3. Update README.md
    if os.path.exists("README.md"):
        with open("README.md", 'r') as f:
            content = f.read()
        
        # Pattern 1: Title # Aerospike Health Analyzer (vX.X.X)
        content = re.sub(r'# Aerospike Health Analyzer \(v.*?\)', 
                         f'# Aerospike Health Analyzer (v{NEW_VERSION})', content)
        
        # Pattern 2: Usage Header ## Usage (vX.X.X)
        content = re.sub(r'## Usage \(v.*?\)', 
                         f'## Usage (v{NEW_VERSION})', content)
        
        # Pattern 3: Footer Version X.X.X | YYYY-MM-DD
        content = re.sub(r'Version \d+\.\d+\.\d+', f'Version {NEW_VERSION}', content)
        content = re.sub(r'\| \d{4}-\d{2}-\d{2}', f'| {DATE_STR}', content)
        
        with open("README.md", 'w') as f:
            f.write(content)
        print("✅ Updated Version & Date: README.md")

if __name__ == "__main__":
    print(f"🚀 Starting Global Version Sync to v{NEW_VERSION}...")
    for d in TARGET_DIRS:
        if os.path.exists(d) and os.path.isdir(d):
            update_python_files(d)
    update_markdown_and_qmd()
    print(f"\n✨ All project files synchronized to v{NEW_VERSION} on {DATE_STR}")