#!/usr/bin/env python3
import json
import os
import sys
import subprocess
from datetime import datetime

PLUGIN_DIR = "/var/lib/cerynixos-plugins"
AUDIT_LOG = "/var/log/cerynixos-plugins/audit.log"

def log_audit(plugin: str, status: str, details: str):
    os.makedirs(os.path.dirname(AUDIT_LOG), exist_ok=True)
    with open(AUDIT_LOG, "a") as f:
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "plugin": plugin,
            "status": status,
            "details": details
        }
        f.write(json.dumps(entry) + "\n")

def run_plugin(plugin_name: str, args: list):
    plugin_path = os.path.join(PLUGIN_DIR, plugin_name)
    manifest_path = os.path.join(plugin_path, "manifest.json")
    
    if not os.path.exists(manifest_path):
        err = f"Plugin {plugin_name} not found or corrupted."
        print(json.dumps({"error": err}))
        log_audit(plugin_name, "DENIED", err)
        sys.exit(1)
        
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
        
    # Permission check mock - in a real scenario we'd drop capabilities based on this
    perms = manifest.get("permissions", [])
    
    entrypoint = manifest.get("entrypoint")
    if not entrypoint:
        err = "Manifest missing entrypoint."
        print(json.dumps({"error": err}))
        log_audit(plugin_name, "DENIED", err)
        sys.exit(1)
        
    cmd_path = os.path.join(plugin_path, entrypoint)
    # Ensure it's executable
    os.chmod(cmd_path, 0o755)
    
    # Milestone 1 Isolation: We execute this python script under sudo as cerynix-plugin-user
    # Note: If already running as the plugin user via sudo from Broker, we just exec.
    
    log_audit(plugin_name, "EXECUTING", f"Args: {args}")
    try:
        # Run the plugin and capture JSON stdout
        res = subprocess.run([cmd_path] + args, capture_output=True, text=True, timeout=10)
        
        if res.returncode != 0:
            log_audit(plugin_name, "FAILED", f"Exit code {res.returncode}. Stderr: {res.stderr}")
            print(json.dumps({"error": "Plugin execution failed.", "stderr": res.stderr}))
            sys.exit(1)
            
        print(res.stdout) # Pass raw JSON back to Action Broker
        log_audit(plugin_name, "SUCCESS", "Completed normally.")
        
    except subprocess.TimeoutExpired:
        err = "Execution timed out after 10 seconds."
        print(json.dumps({"error": err}))
        log_audit(plugin_name, "TIMEOUT", err)
        sys.exit(1)
    except Exception as e:
        err = f"Execution error: {e}"
        print(json.dumps({"error": err}))
        log_audit(plugin_name, "ERROR", err)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: cerynix-plugin-runner <plugin_name> [args...]"}), file=sys.stderr)
        sys.exit(1)
        
    run_plugin(sys.argv[1], sys.argv[2:])
