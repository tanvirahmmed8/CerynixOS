import time
import psutil
import subprocess
import json
import os

STATE_FILE = "/var/lib/cerynixos-health/state.json"

CRITICAL_SERVICES = [
    "cerynix-action-broker",
    "cerynix-inference-manager"
]

def check_service_state(service: str) -> bool:
    try:
        res = subprocess.run(["systemctl", "is-active", service], capture_output=True, text=True)
        return res.stdout.strip() == "active"
    except:
        return False

def calculate_health_score(mem_pct: float, cpu_pct: float, services_active: int, total_services: int) -> int:
    score = 100
    if mem_pct > 90: score -= 30
    elif mem_pct > 75: score -= 10
    
    if cpu_pct > 95: score -= 20
    
    service_penalty = (total_services - services_active) * 25
    score -= service_penalty
    
    return max(0, score)

def collect_metrics():
    mem = psutil.virtual_memory().percent
    cpu = psutil.cpu_percent(interval=1)
    
    active_count = sum(1 for s in CRITICAL_SERVICES if check_service_state(s))
    
    score = calculate_health_score(mem, cpu, active_count, len(CRITICAL_SERVICES))
    
    state = {
        "timestamp": time.time(),
        "health_score": score,
        "metrics": {
            "memory_percent": mem,
            "cpu_percent": cpu,
            "critical_services_active": f"{active_count}/{len(CRITICAL_SERVICES)}"
        }
    }
    
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    print("Starting CerynixOS Health Agent...")
    while True:
        collect_metrics()
        # Phase 4 requirement: 60s polling
        time.sleep(60)
