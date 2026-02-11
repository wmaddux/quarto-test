import os
import re
from datetime import datetime

# --- CONFIGURATION ---
# Synchronizing the entire project to the new stable v1.4.1 baseline
NEW_VERSION = "1.4.1"
TARGET_DIRS = ["rules", "ingest"] 
ROOT_PYTHON_FILES = ["run_ingest.py", "ingest_manager.py", "discovery.py"]
DATE_STR = datetime.now().strftime("%Y-%m-%d")

def update_file_content(path, content):
    """Core logic to update version strings based on variable names."""
    # Update __version__ (used in Python modules)
    if "__version__" in content:
        content = re.sub(r'__version__\s*=\s*["\'].*?["\']', f'__version__ = "{NEW_VERSION}"', content)
    
    # Update PROJECT_VERSION (used in report.qmd)
    if "PROJECT_VERSION" in content:
        content = re.sub(r'PROJECT_VERSION\s*=\s*["\'].*?["\']', f'PROJECT_VERSION = "{NEW_VERSION}"', content)
    
    return content

def process_directory(directory):
    """Recursively update all python files in a directory tree."""
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith(".py"):
                path = os.path.join(root, filename)
                with open(path, 'r') as f:
                    content = f.read()
                
                new_content = update_file_content(path, content)
                
                if new_content != content:
                    with open(path, 'w') as f:
                        f.write(new_content)
                    print(f"✅ Updated Version: {path}")

def update_markdown_and_qmd():
    """Specific logic for Quarto and Documentation files."""
    # 1. Update report.qmd
    if os.path.exists("report.qmd"):
        with open("report.qmd", 'r') as f:
            content = f.read()
        new_content = update_file_content("report.qmd", content)
        if new_content != content:
            with open("report.qmd", 'w') as f:
                f.write(new_content)
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
        
        # Update Title Header
        content = re.sub(r'# Aerospike Health Analyzer \(v.*?\)', 
                         f'# Aerospike Health Analyzer (v{NEW_VERSION})', content)
        
        # Update Usage Header
        content = re.sub(r'## Usage \(v.*?\)', 
                         f'## Usage (v{NEW_VERSION})', content)
        
        # Update Footer Version and Date
        content = re.sub(r'Version \d+\.\d+\.\d+', f'Version {NEW_VERSION}', content)
        content = re.sub(r'\| \d{4}-\d{2}-\d{2}', f'| {DATE_STR}', content)
        
        with open("README.md", 'w') as f:
            f.write(content)
        print("✅ Updated Version & Date: README.md")

if __name__ == "__main__":
    print(f"🚀 Starting Global Version Sync to v{NEW_VERSION}...")
    
    # 1. Update Root Python Files
    for f in ROOT_PYTHON_FILES:
        if os.path.exists(f):
            with open(f, 'r') as file:
                content = file.read()
            new_content = update_file_content(f, content)
            if new_content != content:
                with open(f, 'w') as file:
                    file.write(new_content)
                print(f"✅ Updated Version: ./{f}")

    # 2. Update Logic Directories (Recursive Scan)
    for d in TARGET_DIRS:
        if os.path.exists(d) and os.path.isdir(d):
            process_directory(d)
            
    # 3. Update Documentation and Reports
    update_markdown_and_qmd()
    
    print(f"\n✨ All project files synchronized to v{NEW_VERSION} on {DATE_STR}")