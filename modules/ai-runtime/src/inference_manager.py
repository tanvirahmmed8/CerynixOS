import json
import os
import sys
import psutil
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn
import subprocess

app = FastAPI(title="CerynixOS Inference Manager")
CONFIG_PATH = "/etc/cerynixos/ai/model-config.json"

def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to load config: {e}")
        return None

config = load_config()

def check_memory_budget():
    if not config: return False
    budget_mb = config.get("max_memory_mb", 1024)
    mem_info = psutil.virtual_memory()
    available_mb = mem_info.available / (1024 * 1024)
    if available_mb < budget_mb:
        return False
    return True

# In a real implementation, this would use llama-cpp-python bindings.
# For Milestone 1 device plane, we wrap the llama-cli or llama-server process.
# We stub the actual generation here for the sake of the framework.
@app.post("/generate")
async def generate(request: Request):
    if not check_memory_budget():
        return JSONResponse(status_code=503, content={"error": "Memory budget exceeded. Optimization engine active."})
    
    data = await request.json()
    prompt = data.get("prompt", "")
    
    # Stub response representing local model invocation
    return {"status": "success", "response": f"Acknowledged task: {prompt[:20]}...", "model": config.get("model_id")}

if __name__ == "__main__":
    if not config:
        print("Missing config, exiting.")
        sys.exit(1)
    
    socket_path = "/run/cerynixos/ai-runtime.sock"
    os.makedirs(os.path.dirname(socket_path), exist_ok=True)
    uvicorn.run(app, uds=socket_path)
