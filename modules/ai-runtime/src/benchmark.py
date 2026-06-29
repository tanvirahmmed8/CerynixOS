import time
import psutil
import subprocess

SOCKET_PATH = "/run/cerynixos/ai-runtime.sock"
API_URL = "http://localhost/generate"

def run_benchmark():
    print("Starting CerynixOS Inference Benchmark...")
    start_mem = psutil.virtual_memory().used
    
    start_time = time.time()
    try:
        # Use curl to communicate over Unix Domain Socket
        cmd = [
            "curl", "--unix-socket", SOCKET_PATH,
            "-X", "POST", API_URL,
            "-H", "Content-Type: application/json",
            "-d", '{"prompt": "Write a bash script to update the system."}',
            "-s"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except Exception as e:
        print(f"Benchmark failed: API unreachable or error. {e}")
        sys.exit(1)
        
    end_time = time.time()
    end_mem = psutil.virtual_memory().used
    
    latency = end_time - start_time
    mem_diff_mb = (end_mem - start_mem) / (1024 * 1024)
    
    print(f"Latency: {latency:.2f} seconds")
    print(f"Memory Spike: {mem_diff_mb:.2f} MB")
    
    if mem_diff_mb > 1024:
        print("FAIL: Memory exceeded the 1GB budget for the 0.5B model!")
        sys.exit(1)
    else:
        print("PASS: Resource usage within budget.")

if __name__ == "__main__":
    run_benchmark()
