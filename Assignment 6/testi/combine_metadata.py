import os
import json
from pathlib import Path

def combine_metadata():
    metadata_dir = Path("output_metadata")
    combined = []

    if not metadata_dir.exists():
        print("❌ Metadata directory does not exist.")
        return

    for json_file in metadata_dir.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                combined.append(data)
        except Exception as e:
            print(f"⚠️ Failed to read {json_file}: {e}")

    if not combined:
        print("⚠️ No metadata found to combine.")
        return

    output_path = metadata_dir / "combined_metadata.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=4)
    print(f"✅ Combined metadata saved to {output_path}")

if __name__ == "__main__":
    combine_metadata()
