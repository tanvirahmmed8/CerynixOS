import subprocess
import shlex

# Mapping of safe tools to actual binaries and restricted flags
SAFE_TOOLS = {
    "systemctl_status": ["systemctl", "status"],
    "systemctl_restart": ["sudo", "systemctl", "restart"],
    "file_read": ["cat"],
    "journalctl_read": ["journalctl", "-n", "50", "--no-pager", "-u"]
}

def execute_tool(tool_name: str, args: dict, timeout_sec: int = 15) -> str:
    if tool_name not in SAFE_TOOLS:
        raise ValueError(f"Tool {tool_name} is not implemented in the executor.")

    cmd_base = SAFE_TOOLS[tool_name]
    
    # Extract arguments safely. We avoid shell=True entirely.
    if tool_name == "systemctl_status" or tool_name == "systemctl_restart" or tool_name == "journalctl_read":
        target = args.get("service")
        if not target or not target.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Invalid service name.")
        cmd = cmd_base + [target]
    
    elif tool_name == "file_read":
        path = args.get("path")
        # Extremely basic directory traversal prevention
        if ".." in path or not path.startswith("/etc/"): 
            raise ValueError("File read restricted to /etc/ for this tool.")
        cmd = cmd_base + [path]
    else:
        raise ValueError("Argument parsing not defined for tool.")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec)
    
    if result.returncode != 0:
        raise RuntimeError(f"Command failed with code {result.returncode}:\n{result.stderr}")
        
    return result.stdout
