import json
from database.connection import get_db_connection

VALID_STATES = {"enrolled", "active", "quarantined", "retired"}

def parse_device_row(row) -> dict:
    """Helper to convert database Row objects into Python dicts with deserialized JSON columns."""
    if not row:
        return None
    d = dict(row)
    if d.get("tags"):
        try:
            d["tags"] = json.loads(d["tags"])
        except:
            d["tags"] = []
    else:
        d["tags"] = []
        
    if d.get("installed_capabilities"):
        try:
            d["installed_capabilities"] = json.loads(d["installed_capabilities"])
        except:
            d["installed_capabilities"] = []
    else:
        d["installed_capabilities"] = []
        
    return d

def register_or_update_device(
    device_id: str,
    device_model: str,
    os_version: str,
    cpu_cores: int,
    memory_bytes: int,
    storage_bytes: int,
    installed_capabilities: list,
    tags: list = None,
    group_id: str = None
) -> dict:
    """Registers a new device or updates hardware capabilities of an existing device."""
    caps_json = json.dumps(installed_capabilities or [])
    tags_json = json.dumps(tags or [])
    
    with get_db_connection() as conn:
        # Check if device already exists to preserve enrollment state and group_id
        cursor = conn.execute("SELECT enrollment_state, tags, group_id FROM devices WHERE device_id = ?;", (device_id,))
        existing = cursor.fetchone()
        
        if existing:
            state = existing["enrollment_state"]
            # Keep existing group and tags if not explicitly passed
            db_group_id = group_id if group_id is not None else existing["group_id"]
            db_tags_json = tags_json if tags is not None else existing["tags"]
        else:
            state = "enrolled"
            db_group_id = group_id
            db_tags_json = tags_json
            
        conn.execute(
            """
            INSERT INTO devices (
                device_id, device_model, os_version, cpu_cores, memory_bytes, 
                storage_bytes, installed_capabilities, enrollment_state, tags, group_id, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(device_id) DO UPDATE SET
                device_model = excluded.device_model,
                os_version = excluded.os_version,
                cpu_cores = excluded.cpu_cores,
                memory_bytes = excluded.memory_bytes,
                storage_bytes = excluded.storage_bytes,
                installed_capabilities = excluded.installed_capabilities,
                updated_at = CURRENT_TIMESTAMP;
            """,
            (
                device_id, device_model, os_version, cpu_cores, memory_bytes,
                storage_bytes, caps_json, state, db_tags_json, db_group_id
            )
        )
        
        cursor = conn.execute("SELECT * FROM devices WHERE device_id = ?;", (device_id,))
        return parse_device_row(cursor.fetchone())

def get_device(device_id: str) -> dict:
    """Retrieves a single device by ID."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM devices WHERE device_id = ?;", (device_id,))
        return parse_device_row(cursor.fetchone())

def list_devices(
    filter_state: str = None,
    filter_group: str = None,
    filter_tag: str = None,
    query_text: str = None
) -> list:
    """Lists devices matching filter criteria."""
    query = "SELECT * FROM devices WHERE 1=1"
    params = []
    
    if filter_state:
        query += " AND enrollment_state = ?"
        params.append(filter_state)
        
    if filter_group:
        query += " AND group_id = ?"
        params.append(filter_group)
        
    with get_db_connection() as conn:
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        
    devices = [parse_device_row(row) for row in rows]
    
    # Apply client-side filters for tags and keyword search to keep SQL compatible
    if filter_tag:
        devices = [d for d in devices if filter_tag in d.get("tags", [])]
        
    if query_text:
        q = query_text.lower()
        devices = [
            d for d in devices
            if q in d["device_id"].lower() or q in d["device_model"].lower()
        ]
        
    return devices

def update_device_state(device_id: str, new_state: str) -> dict:
    """Validates and updates a device's lifecycle state."""
    if new_state not in VALID_STATES:
        raise ValueError(f"Invalid state transition target: '{new_state}'")
        
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT enrollment_state FROM devices WHERE device_id = ?;", (device_id,))
        row = cursor.fetchone()
        if not row:
            raise KeyError(f"Device '{device_id}' not found.")
            
        current_state = row["enrollment_state"]
        
        # State Transition validation rules:
        # retired is terminal
        if current_state == "retired" and new_state != "retired":
            raise ValueError("Cannot transition a device out of 'retired' state.")
            
        conn.execute(
            "UPDATE devices SET enrollment_state = ?, updated_at = CURRENT_TIMESTAMP WHERE device_id = ?;",
            (new_state, device_id)
        )
        
        cursor = conn.execute("SELECT * FROM devices WHERE device_id = ?;", (device_id,))
        return parse_device_row(cursor.fetchone())

def update_device_group_and_tags(device_id: str, group_id: str = None, tags: list = None) -> dict:
    """Updates the group ID and/or tags of an enrolled device."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM devices WHERE device_id = ?;", (device_id,))
        existing = cursor.fetchone()
        if not existing:
            raise KeyError(f"Device '{device_id}' not found.")
            
        if group_id is not None:
            # Check if group exists if setting a group
            if group_id != "":
                g_cursor = conn.execute("SELECT 1 FROM device_groups WHERE group_id = ?;", (group_id,))
                if not g_cursor.fetchone():
                    raise KeyError(f"Device group '{group_id}' does not exist.")
            db_group = group_id if group_id != "" else None
        else:
            db_group = existing["group_id"]
            
        db_tags = json.dumps(tags) if tags is not None else existing["tags"]
        
        conn.execute(
            "UPDATE devices SET group_id = ?, tags = ?, updated_at = CURRENT_TIMESTAMP WHERE device_id = ?;",
            (db_group, db_tags, device_id)
        )
        
        cursor = conn.execute("SELECT * FROM devices WHERE device_id = ?;", (device_id,))
        return parse_device_row(cursor.fetchone())

def create_device_group(group_id: str, name: str, description: str = None) -> dict:
    """Creates a new device group."""
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO device_groups (group_id, name, description) VALUES (?, ?, ?);",
            (group_id, name, description)
        )
        cursor = conn.execute("SELECT * FROM device_groups WHERE group_id = ?;", (group_id,))
        return dict(cursor.fetchone())

def list_device_groups() -> list:
    """Lists all registered device groups."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM device_groups ORDER BY name ASC;")
        return [dict(row) for row in cursor.fetchall()]
