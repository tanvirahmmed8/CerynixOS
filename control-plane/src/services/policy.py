import json
import uuid
from database.connection import get_db_connection

VALID_APPROVAL_MODES = {"suggest_only", "ask_before_act", "auto_act"}

# Safe Fallback Default Policy
DEFAULT_POLICY = {
    "policy_id": "default_fallback_policy",
    "version": 1,
    "rules": {
        "allowed_tools": [
            "systemctl status",
            "journalctl"
        ],
        "approval_mode": "ask_before_act"
    }
}

def validate_policy_rules(rules: dict) -> bool:
    """Dry-run validation checks on the structure of policy rules."""
    if not isinstance(rules, dict):
        raise ValueError("Rules must be a JSON object/dict.")
        
    allowed_tools = rules.get("allowed_tools")
    if not isinstance(allowed_tools, list):
        raise ValueError("Rules property 'allowed_tools' must be a list of strings.")
        
    for idx, tool in enumerate(allowed_tools):
        if not isinstance(tool, str):
            raise ValueError(f"Tool at index {idx} must be a string value.")
            
    approval_mode = rules.get("approval_mode")
    if approval_mode not in VALID_APPROVAL_MODES:
        raise ValueError(f"Rules property 'approval_mode' must be one of {VALID_APPROVAL_MODES}, got '{approval_mode}'.")
        
    return True

def create_or_update_policy(policy_id: str, rules: dict) -> dict:
    """Creates a new policy or increments the version and creates a new revision for an existing policy."""
    validate_policy_rules(rules)
    rules_json = json.dumps(rules)
    
    with get_db_connection() as conn:
        # Determine next version
        cursor = conn.execute("SELECT version FROM policies WHERE policy_id = ?;", (policy_id,))
        row = cursor.fetchone()
        next_version = (row["version"] + 1) if row else 1
        
        # 1. Update active policy state
        conn.execute(
            """
            INSERT INTO policies (policy_id, version, rules)
            VALUES (?, ?, ?)
            ON CONFLICT(policy_id) DO UPDATE SET
                version = excluded.version,
                rules = excluded.rules;
            """,
            (policy_id, next_version, rules_json)
        )
        
        # 2. Add history log record
        conn.execute(
            """
            INSERT INTO policy_revisions (policy_id, version, rules)
            VALUES (?, ?, ?);
            """,
            (policy_id, next_version, rules_json)
        )
        
        cursor = conn.execute("SELECT * FROM policies WHERE policy_id = ?;", (policy_id,))
        p_row = dict(cursor.fetchone())
        p_row["rules"] = json.loads(p_row["rules"])
        return p_row

def get_policy(policy_id: str) -> dict:
    """Retrieves the active policy configuration by ID."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM policies WHERE policy_id = ?;", (policy_id,))
        row = cursor.fetchone()
        if not row:
            return None
        p_row = dict(row)
        p_row["rules"] = json.loads(p_row["rules"])
        return p_row

def list_policy_revisions(policy_id: str) -> list:
    """Lists all historical versions of a policy."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            "SELECT * FROM policy_revisions WHERE policy_id = ? ORDER BY version DESC;",
            (policy_id,)
        )
        revisions = []
        for row in cursor.fetchall():
            rev = dict(row)
            rev["rules"] = json.loads(rev["rules"])
            revisions.append(rev)
        return revisions

def assign_policy(policy_id: str, target_type: str, target_id: str = None) -> dict:
    """Assigns an existing policy to a scope (global, group, device)."""
    if target_type not in ("global", "group", "device"):
        raise ValueError("Invalid target assignment scope. Must be 'global', 'group', or 'device'.")
        
    with get_db_connection() as conn:
        # Check if policy exists
        p_cursor = conn.execute("SELECT 1 FROM policies WHERE policy_id = ?;", (policy_id,))
        if not p_cursor.fetchone():
            raise KeyError(f"Policy '{policy_id}' does not exist.")
            
        # Target constraints checks
        if target_type == "global":
            assignment_id = "global"
            db_target_id = None
        elif target_type == "group":
            if not target_id:
                raise ValueError("Group assignment requires a valid group_id.")
            # Check if group exists
            g_cursor = conn.execute("SELECT 1 FROM device_groups WHERE group_id = ?;", (target_id,))
            if not g_cursor.fetchone():
                raise KeyError(f"Device group '{target_id}' does not exist.")
            assignment_id = f"group:{target_id}"
            db_target_id = target_id
        elif target_type == "device":
            if not target_id:
                raise ValueError("Device assignment requires a valid device_id.")
            # Check if device exists
            d_cursor = conn.execute("SELECT 1 FROM devices WHERE device_id = ?;", (target_id,))
            if not d_cursor.fetchone():
                raise KeyError(f"Device '{target_id}' does not exist.")
            assignment_id = f"device:{target_id}"
            db_target_id = target_id
            
        conn.execute(
            """
            INSERT OR REPLACE INTO policy_assignments (assignment_id, policy_id, target_type, target_id)
            VALUES (?, ?, ?, ?);
            """,
            (assignment_id, policy_id, target_type, db_target_id)
        )
        
        cursor = conn.execute("SELECT * FROM policy_assignments WHERE assignment_id = ?;", (assignment_id,))
        return dict(cursor.fetchone())

def rollback_policy_to_version(policy_id: str, target_version: int) -> dict:
    """Reverts a policy rules configuration to a specific past version number."""
    with get_db_connection() as conn:
        # Look up target rules in revisions
        cursor = conn.execute(
            "SELECT rules FROM policy_revisions WHERE policy_id = ? AND version = ?;",
            (policy_id, target_version)
        )
        row = cursor.fetchone()
        if not row:
            raise KeyError(f"Historical version '{target_version}' for policy '{policy_id}' not found.")
            
        rules = json.loads(row["rules"])
        
    # Re-apply these rules as a new version increment
    return create_or_update_policy(policy_id, rules)

def resolve_policy_for_device(device_id: str) -> dict:
    """Resolves policy applying specificity rules: Device > Group > Global."""
    with get_db_connection() as conn:
        # Get device group details
        d_cursor = conn.execute("SELECT group_id FROM devices WHERE device_id = ?;", (device_id,))
        d_row = d_cursor.fetchone()
        if not d_row:
            # Device not registered. Return fallback default.
            return DEFAULT_POLICY
            
        group_id = d_row["group_id"]
        
        # Select active assignments in order of specificity
        # 1. Device assignment
        a_cursor = conn.execute(
            "SELECT policy_id FROM policy_assignments WHERE target_type = 'device' AND target_id = ?;",
            (device_id,)
        )
        a_row = a_cursor.fetchone()
        if a_row:
            policy = get_policy(a_row["policy_id"])
            if policy: return policy
            
        # 2. Group assignment
        if group_id:
            a_cursor = conn.execute(
                "SELECT policy_id FROM policy_assignments WHERE target_type = 'group' AND target_id = ?;",
                (group_id,)
            )
            a_row = a_cursor.fetchone()
            if a_row:
                policy = get_policy(a_row["policy_id"])
                if policy: return policy
                
        # 3. Global assignment
        a_cursor = conn.execute(
            "SELECT policy_id FROM policy_assignments WHERE target_type = 'global';"
        )
        a_row = a_cursor.fetchone()
        if a_row:
            policy = get_policy(a_row["policy_id"])
            if policy: return policy
            
    return DEFAULT_POLICY
