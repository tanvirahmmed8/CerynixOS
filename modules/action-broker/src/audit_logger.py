import json
import os
from datetime import datetime

AUDIT_LOG_PATH = "/var/log/cerynixos-audit/broker-events.log"

def log_audit_event(action: str, status: str, details: dict, error: str = None):
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "cerynix-action-broker",
        "action": action,
        "status": status,
        "details": details
    }
    if error:
        event["details"]["error"] = error
        
    os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)
    with open(AUDIT_LOG_PATH, "a") as f:
        f.write(json.dumps(event) + "\n")
