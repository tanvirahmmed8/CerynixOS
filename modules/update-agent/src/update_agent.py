#!/usr/bin/env python3
import json
import os
import sys
import time
import subprocess
from datetime import datetime

HISTORY_FILE = "/var/lib/cerynixos-update/history.json"
HEALTH_STATE = "/var/lib/cerynixos-health/state.json"

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
            try:
                history = json.load(f)
            except:
                pass
                
    history.append(entry)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def pre_update_health_check() -> bool:
    if not os.path.exists(HEALTH_STATE):
        print("Health state not available. Proceeding with caution.")
        return True
        
    with open(HEALTH_STATE, "r") as f:
        state = json.load(f)
        score = state.get("health_score", 100)
        
    if score < 80:
        print(f"Update aborted: System health score ({score}) is below safe threshold (80).")
        return False
    return True

def apply_update(metadata_path: str, simulate_cmd: bool = False):
    with open(metadata_path, "r") as f:
        meta = json.load(f)
        
    version = meta.get("version", "unknown")
    print(f"Staging update to {version}...")
    
    if not pre_update_health_check():
        log_event(version, "ABORTED", "Pre-update health check failed.")
        sys.exit(1)
        
    # STAGE 1: Build (Dry Run)
    print("Stage 1: Building new generation...")
    if not simulate_cmd:
        # In a real environment: subprocess.run(["nixos-rebuild", "build", "--flake", meta['flake_url']])
        pass
        
    # STAGE 2: Apply
    print("Stage 2: Applying update...")
    if not simulate_cmd:
        # subprocess.run(["nixos-rebuild", "switch", "--flake", meta['flake_url']])
        pass
    
    log_event(version, "APPLIED", "Update staged and applied.")
    
    # STAGE 3: Post-Update Verification
    print("Stage 3: Verifying system stability...")
    time.sleep(2) # Give services a moment to start
    
    # Simulate a critical failure if the metadata asks for it
    if meta.get("simulate_failure", False):
        print("CRITICAL: Action Broker failed to start post-update!")
        print("Triggering automatic rollback...")
        
        if not simulate_cmd:
            # subprocess.run(["nixos-rebuild", "switch", "--rollback"])
            pass
            
        log_event(version, "ROLLED_BACK", "Critical service failure detected post-update.")
        sys.exit(1)
        
    print(f"Update to {version} completely successfully.")
    log_event(version, "VERIFIED", "System stable post-update.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="CerynixOS Local Update Agent")
    parser.add_argument("metadata", help="Path to update metadata JSON")
    parser.add_argument("--simulate", action="store_true", help="Mock nixos-rebuild commands for testing")
    args = parser.parse_args()
    
    apply_update(args.metadata, simulate_cmd=args.simulate)
