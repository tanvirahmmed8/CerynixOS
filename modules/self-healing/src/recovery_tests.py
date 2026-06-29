import subprocess
import time
import sys

def test_service_recovery():
    print("Testing auto-recovery of stopped services...")
    # Simulate broker crash
    subprocess.run(["systemctl", "stop", "cerynix-action-broker"], check=False)
    
    # Run healer
    subprocess.run(["cerynix-healer"], check=True)
    
    # Verify it was restarted
    res = subprocess.run(["systemctl", "is-active", "cerynix-action-broker"], capture_output=True, text=True)
    if res.stdout.strip() == "active":
        print("PASS: Service auto-recovery successful.")
    else:
        print("FAIL: Service was not recovered.")
        sys.exit(1)

if __name__ == "__main__":
    print("Running Self-Healing Integration Tests...")
    test_service_recovery()
    print("All tests completed.")
