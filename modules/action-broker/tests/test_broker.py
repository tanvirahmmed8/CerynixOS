import pytest
from fastapi.testclient import TestClient
import sys
import os

# Ensure src is in path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from broker import app
from policy_engine import evaluate_policy

client = TestClient(app)

def test_missing_tool_name():
    response = client.post("/execute", json={"arguments": {}})
    assert response.status_code == 400

def test_policy_engine_deny_unknown_tool():
    # evaluate_policy uses the mock file. Assuming 'rm_rf_slash' isn't in it.
    res = evaluate_policy("rm_rf_slash", {})
    assert res["status"] == "denied"

def test_executor_sandbox_rejection():
    # Attempting to read outside /etc should fail
    response = client.post("/execute", json={"tool": "file_read", "arguments": {"path": "/root/secret.txt"}})
    # If the policy allows file_read but executor denies it, it will return 500 Execution failed (or similar).
    # Since we can't guarantee the mock policy state during test, we just ensure it doesn't return 200 with the file content.
    assert response.status_code in [403, 500]
