import sys
import os
from ingest_manager import process_collectinfo

__version__ = "1.6.0"

def main():
    if len(sys.argv) < 2:
        print("❌ Usage: python3 run_ingest.py <path_to_bundle.tgz>")
        return

    input_path = sys.argv[1]
    if not os.path.exists(input_path):
        print(f"❌ Error: File not found: {input_path}")
        return

    try:
        process_collectinfo(input_path)
        print("✨ Ingestion complete.")
    except Exception as e:
        print(f"💥 Critical Failure: {e}")

if __name__ == "__main__":
    main()