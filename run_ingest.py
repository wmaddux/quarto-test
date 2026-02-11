__version__ = "1.4.1"
#!/usr/bin/env python3

import sys
import os
from ingest_manager import process_collectinfo

def main():
    if len(sys.argv) < 2:
        print("❌ Usage: python3 run_ingest.py <path_to_collectinfo>")
        print("Example: python3 run_ingest.py aws-common.collect_info_2026.tgz")
        return

    input_path = sys.argv[1]

    if not os.path.exists(input_path):
        print(f"❌ Error: File not found at {input_path}")
        return

    try:
        print(f"🚀 Processing: {input_path}")
        process_collectinfo(input_path)
        print("✅ Ingestion complete. Run 'quarto render report.qmd' next.")
    except Exception as e:
        print(f"💥 Failed to process {input_path}")
        print(f"Error details: {e}")

if __name__ == "__main__":
    main()
