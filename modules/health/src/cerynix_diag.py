#!/usr/bin/env python3
import json
import os
import sys
import tarfile
import re
import subprocess
from datetime import datetime

STATE_FILE = "/var/lib/cerynixos-health/state.json"
EXPORT_DIR = "/var/tmp/cerynixos-diagnostics"

def get_status():
    if not os.path.exists(STATE_FILE):
        print("Health state not available. Is cerynix-health-agent running?")
        return
    with open(STATE_FILE, "r") as f:
        state = json.load(f)
    print("=== CerynixOS Health Status ===")
    print(f"Health Score: {state.get('health_score')}/100")
    for k, v in state.get('metrics', {}).items():
        print(f"  {k}: {v}")

def scrub_sensitive_data(text: str) -> str:
    # Basic redaction rules for tokens (e.g. Bearer tokens) and passwords
    text = re.sub(r'Bearer\s+[A-Za-z0-9\-\._~+/\]+=*', 'Bearer [REDACTED]', text)
    text = re.sub(r'(?i)password\s*[:=]\s*\S+', 'password: [REDACTED]', text)
    return text

def generate_snapshot():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = os.path.join(EXPORT_DIR, f"diag-snapshot-{stamp}.tar.gz")
    
    # Collect journalctl logs
    try:
        res = subprocess.run(["journalctl", "-n", "1000", "--no-pager"], capture_output=True, text=True)
        safe_logs = scrub_sensitive_data(res.stdout)
        
        log_path = os.path.join(EXPORT_DIR, "system.log")
        with open(log_path, "w") as f:
            f.write(safe_logs)
            
        with tarfile.open(archive_name, "w:gz") as tar:
            tar.add(log_path, arcname="system.log")
            if os.path.exists(STATE_FILE):
                tar.add(STATE_FILE, arcname="state.json")
                
        # Cleanup temp file
        os.remove(log_path)
        print(f"Diagnostics snapshot exported to: {archive_name}")
    except Exception as e:
        print(f"Failed to generate snapshot: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: cerynix-diag [status|snapshot]")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "status":
        get_status()
    elif cmd == "snapshot":
        generate_snapshot()
    else:
        print("Unknown command.")
