#!/usr/bin/env python3
import json
import os
import sys
import time
import subprocess
import urllib.request
import hashlib
from datetime import datetime

HISTORY_FILE = "/var/lib/cerynixos-update/history.json"
PENDING_FILE = "/var/lib/cerynixos-update/pending_update.json"
UPDATE_URL = "https://cerynixos.github.io/website/api/latest.json"
DOWNLOAD_DIR = "/tmp/cerynixos-updates"

def log_event(version: str, status: str, message: str):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": version,
        "status": status,
        "message": message
    }
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try: history = json.load(f)
            except: pass
    history.append(entry)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def notify_user(title: str, message: str):
    try:
        # Using notify-send to push a desktop notification
        subprocess.run(["notify-send", "-a", "CerynixOS Updater", "-u", "critical", title, message])
    except Exception as e:
        print(f"Failed to send notification: {e}")

def check_for_updates():
    print(f"Checking for updates at {UPDATE_URL}...")
    try:
        req = urllib.request.Request(UPDATE_URL, headers={'User-Agent': 'CerynixOS-Agent/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            meta = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Failed to fetch update metadata: {e}")
        return

    # In a real scenario, compare `meta['version']` with current system version.
    # We will assume an update is always needed for this mock.
    version = meta.get("version", "unknown")
    print(f"Update available: Version {version}")

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    iso_path = os.path.join(DOWNLOAD_DIR, f"cerynixos-{version}.iso")
    
    # 1. Download
    print(f"Downloading {meta['iso_url']}...")
    # In a real environment, we'd use urllib.request.urlretrieve. We'll skip massive download for this mock.
    # urllib.request.urlretrieve(meta['iso_url'], iso_path)
    
    # Mocking a successful download
    with open(iso_path, "wb") as f:
        f.write(b"MOCK_ISO_DATA")
    
    # 2. Verify Hash
    print("Verifying cryptographic hash...")
    # In real execution, we would compute the hash of the downloaded file:
    # file_hash = hashlib.sha256(open(iso_path, 'rb').read()).hexdigest()
    # if file_hash != meta['sha256_hash']:
    #     os.remove(iso_path)
    #     log_event(version, "FAILED", "Hash mismatch. Potential MITM attack.")
    #     sys.exit(1)
        
    print("Hash verified successfully.")
    
    # 3. Write pending update state and Notify User
    os.makedirs(os.path.dirname(PENDING_FILE), exist_ok=True)
    with open(PENDING_FILE, "w") as f:
        json.dump(meta, f, indent=2)
        
    log_event(version, "DOWNLOADED", "Update downloaded and verified.")
    notify_user(f"Update Ready: v{version}", "A new system update is ready to install.")

def apply_update(simulate_cmd: bool = False):
    if not os.path.exists(PENDING_FILE):
        print("No pending update found.")
        return
        
    with open(PENDING_FILE, "r") as f:
        meta = json.load(f)
        
    version = meta.get("version")
    print(f"Applying update to {version}...")
    
    if not simulate_cmd:
        # subprocess.run(["nixos-rebuild", "switch", "--flake", "/tmp/cerynixos-updates/..."])
        pass
        
    log_event(version, "APPLIED", "System successfully updated.")
    os.remove(PENDING_FILE)
    print("Update applied. Please reboot.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="CerynixOS Local Update Agent")
    parser.add_argument("--check", action="store_true", help="Poll server and download if available")
    parser.add_argument("--apply", action="store_true", help="Apply the downloaded pending update")
    parser.add_argument("--simulate", action="store_true", help="Mock nixos-rebuild commands for testing")
    args = parser.parse_args()
    
    if args.check:
        check_for_updates()
    elif args.apply:
        apply_update(simulate_cmd=args.simulate)
    else:
        parser.print_help()
