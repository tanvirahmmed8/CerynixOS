import json
import os

POLICY_FIXTURE_PATH = "/etc/cerynixos/mocks/fixtures/sample-policy.json"

def _load_policy():
    if not os.path.exists(POLICY_FIXTURE_PATH):
        # Fail safe: deny all if policy is missing
        return {"rules": {"allowed_tools": [], "approval_mode": "suggest_only"}}
    with open(POLICY_FIXTURE_PATH, "r") as f:
        return json.load(f)

def evaluate_policy(tool_name: str, args: dict) -> dict:
    policy = _load_policy()
    rules = policy.get("rules", {})
    allowed_tools = rules.get("allowed_tools", [])
    mode = rules.get("approval_mode", "suggest_only")

    if tool_name not in allowed_tools:
        return {"status": "denied", "reason": f"Tool '{tool_name}' not in allowed list."}

    if mode == "suggest_only":
        return {"status": "denied", "reason": "Enterprise policy enforces suggest_only mode."}
    
    if mode == "ask_before_act":
        return {"status": "requires_approval"}
    
    if mode == "auto_act":
        return {"status": "approved"}

    return {"status": "denied", "reason": "Unknown approval mode."}
