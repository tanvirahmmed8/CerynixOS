#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from recovery_ui import prompt_recovery

HEALTH_STATE = "/var/lib/cerynixos-health/state.json"
CRITICAL_SERVICES = ["cerynix-action-broker", "cerynix-inference-manager"]

def check_services():
    for service in CRITICAL_SERVICES:
        res = subprocess.run(["systemctl", "is-active", service], capture_output=True, text=True)
        if res.stdout.strip() != "active":
            print(f"[Healer] Auto-recovering {service}...")
            # Automatic recovery: no prompt needed
            subprocess.run(["systemctl", "restart", service])

def check_storage():
    # Check /nix/store or root partition
    res = subprocess.run(["df", "-h", "/"], capture_output=True, text=True)
    lines = res.stdout.strip().split("\n")
    if len(lines) > 1:
        # Parse Use%
        parts = lines[1].split()
        use_pct = int(parts[4].replace("%", ""))
        if use_pct > 90:
            if prompt_recovery("Storage Pressure (>90% full)", "nix-collect-garbage -d"):
                print("[Healer] Running garbage collection...")
                subprocess.run(["nix-collect-garbage", "-d"])
            else:
                print("[Healer] Garbage collection aborted by user.")

def run_diagnostics():
    print("Running CerynixOS Self-Healing Diagnostics...")
    check_services()
    check_storage()
    print("Diagnostics complete.")

if __name__ == "__main__":
    run_diagnostics()
