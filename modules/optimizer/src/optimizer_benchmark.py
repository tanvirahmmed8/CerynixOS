import subprocess
import time
import sys
import os

def run_benchmark():
    print("Starting Optimizer Profile Benchmark...")
    print("This will test switching between Battery Saver and Performance profiles.")
    
    # 1. Switch to Battery Saver
    print("\n--- Applying Battery Saver ---")
    subprocess.run(["cerynix-optimizer", "set", "battery_saver"], check=True)
    # Mocking a workload
    time.sleep(2)
    
    # 2. Switch to Performance
    print("\n--- Applying Performance ---")
    subprocess.run(["cerynix-optimizer", "set", "performance"], check=True)
    time.sleep(2)
    
    # 3. Revert
    print("\n--- Reverting to Baseline ---")
    subprocess.run(["cerynix-optimizer", "revert"], check=True)
    
    print("\nBenchmark complete. Check /var/log/cerynixos-optimizer/decisions.log for details.")

if __name__ == "__main__":
    # Ensure this runs only if cerynix-optimizer is in PATH
    try:
        run_benchmark()
    except Exception as e:
        print(f"Benchmark failed: {e}")
        sys.exit(1)
