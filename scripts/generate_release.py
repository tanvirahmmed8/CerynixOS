#!/usr/bin/env python3
import sys
import hashlib
import json
import datetime
import os

def generate_sha256(filepath):
    print(f"Hashing {filepath}...")
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def update_latest_json(version, iso_path, changelog):
    latest_json_path = os.path.join(os.path.dirname(__file__), "../website/api/latest.json")
    
    hash_val = generate_sha256(iso_path)
    release_date = datetime.datetime.utcnow().isoformat() + "Z"
    iso_url = f"https://github.com/cerynixos/cerynixos/releases/download/v{version}/cerynixos-{version}-x86_64.iso"
    
    data = {
        "version": version,
        "release_date": release_date,
        "iso_url": iso_url,
        "sha256_hash": hash_val,
        "urgency": "low",
        "changelog": changelog
    }
    
    with open(latest_json_path, "w") as f:
        json.dump(data, f, indent=2)
        
    print(f"Successfully updated {latest_json_path}")
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 generate_release.py <version> <path_to_iso> [changelog_item1, changelog_item2...]")
        sys.exit(1)
        
    version = sys.argv[1]
    iso_path = sys.argv[2]
    changelog = sys.argv[3:] if len(sys.argv) > 3 else ["Routine update."]
    
    if not os.path.exists(iso_path):
        print(f"Error: File {iso_path} not found.")
        sys.exit(1)
        
    update_latest_json(version, iso_path, changelog)
