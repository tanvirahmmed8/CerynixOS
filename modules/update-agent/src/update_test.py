import subprocess
import os
import sys

def run_simulation():
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    good_mock = os.path.join(repo_root, "mocks", "update-metadata-good.json")
    bad_mock = os.path.join(repo_root, "mocks", "update-metadata-bad.json")
    
    print("=== Testing Good Update ===")
    subprocess.run(["cerynix-update", good_mock, "--simulate"], check=True)
    
    print("\n=== Testing Bad Update (Expect Rollback) ===")
    res = subprocess.run(["cerynix-update", bad_mock, "--simulate"])
    if res.returncode == 0:
        print("FAIL: Bad update did not trigger a rollback exit code.")
        sys.exit(1)
    else:
        print("PASS: Bad update was caught and rolled back.")
        
    print("\n=== Update History ===")
    subprocess.run(["cerynix-update-status"])

if __name__ == "__main__":
    try:
        run_simulation()
    except Exception as e:
        print(f"Test framework failed: {e}")
        sys.exit(1)
