from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn
from policy_engine import evaluate_policy
from executor import execute_tool
from audit_logger import log_audit_event
import os

app = FastAPI(title="CerynixOS Action Broker")

@app.post("/execute")
async def handle_execution(request: Request):
    """
    Receives tool calls from the AI Runtime.
    Expected JSON: {"tool": "tool_name", "arguments": {"arg1": "val1"}}
    """
    data = await request.json()
    tool_name = data.get("tool")
    args = data.get("arguments", {})

    if not tool_name:
        raise HTTPException(status_code=400, detail="Missing tool name")

    # 1. Evaluate against active policy
    policy_result = evaluate_policy(tool_name, args)
    
    if policy_result["status"] == "denied":
        log_audit_event(tool_name, "denied_by_policy", args)
        return JSONResponse(status_code=403, content={"error": "Tool execution denied by policy", "reason": policy_result["reason"]})

    if policy_result["status"] == "requires_approval":
        # In a real implementation, this would trigger a DBus call to the UI.
        log_audit_event(tool_name, "pending_approval", args)
        return {"status": "pending_approval", "message": "User approval requested via UI."}

    # 2. Execute safely
    try:
        exec_result = execute_tool(tool_name, args)
        log_audit_event(tool_name, "success", args)
        return {"status": "success", "result": exec_result}
    except Exception as e:
        log_audit_event(tool_name, "failed", args, error=str(e))
        return JSONResponse(status_code=500, content={"error": "Execution failed", "details": str(e)})

if __name__ == "__main__":
    socket_path = "/run/cerynixos/broker.sock"
    # Ensure directory exists for UDS
    os.makedirs(os.path.dirname(socket_path), exist_ok=True)
    # Start on UDS for local security
    uvicorn.run(app, uds=socket_path)
