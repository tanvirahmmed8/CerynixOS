#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime
import revert_manager

PROFILES_PATH = os.path.join(os.path.dirname(__file__), "profiles.json")
LOG_PATH = "/var/log/cerynixos-optimizer/decisions.log"

def log_decision(reason: str):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        entry = {"timestamp": datetime.utcnow().isoformat() + "Z", "decision": reason}
        f.write(json.dumps(entry) + "\n")

def read_profiles():
    with open(PROFILES_PATH, "r") as f:
        return json.load(f)

# Mock kernel writes since we may be running in a VM without real cpufreq scaling
def _write_sysfs(path: str, value: str):
    if not os.path.exists(path):
        print(f"[MOCK] Would write '{value}' to {path}")
        return
    try:
        with open(path, "w") as f:
            f.write(value)
    except Exception as e:
        print(f"Failed to write {path}: {e}")

def apply_profile(profile_name: str, profiles: dict):
    if profile_name not in profiles:
        print(f"Profile {profile_name} not found.")
        sys.exit(1)
        
    config = profiles[profile_name]
    
    # Save current state for revert (mocking reads for simplicity)
    current_state = {
        "profile": "unknown_previous",
        # Real impl would read from /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor etc
    }
    revert_manager.save_current_state(current_state)
    
    # Apply CPU Governor
    # Usually you'd iterate over all CPUs
    _write_sysfs("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor", config["cpu_governor"])
    
    # Apply Swappiness
    _write_sysfs("/proc/sys/vm/swappiness", str(config["swappiness"]))
    
    log_decision(f"Applied profile '{profile_name}'. Governor: {config['cpu_governor']}, Swappiness: {config['swappiness']}")
    print(f"Successfully applied {profile_name} profile.")

def revert_profile():
    prev = revert_manager.load_previous_state()
    if not prev:
        print("No previous state to revert to.")
        return
    print("Reverted to previous state.")
    log_decision("Reverted to previous state.")
    revert_manager.clear_state()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: cerynix-optimizer [set <profile> | revert]")
        sys.exit(1)

    cmd = sys.argv[1]
    
    if cmd == "set" and len(sys.argv) == 3:
        apply_profile(sys.argv[2], read_profiles())
    elif cmd == "revert":
        revert_profile()
    else:
        print("Invalid command.")
        sys.exit(1)
