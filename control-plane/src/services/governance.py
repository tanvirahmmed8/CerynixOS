import json
import hashlib
from database.connection import get_db_connection, load_config

def redact_details(details: dict) -> dict:
    """Redacts sensitive values in dict keys matching config.json fields list."""
    if not details:
        return details
    try:
        cfg = load_config()
        redact_keys = cfg.get("audit_redact_fields", ["password", "secret", "token", "key"])
    except:
        redact_keys = ["password", "secret", "token", "key"]
        
    redacted = {}
    for k, v in details.items():
        if any(rk in k.lower() for rk in redact_keys):
            redacted[k] = "[REDACTED]"
        elif isinstance(v, dict):
            redacted[k] = redact_details(v)
        else:
            redacted[k] = v
    return redacted

def calculate_log_hash(previous_hash: str, event_id: str, device_id: str, timestamp: str, service: str, action: str, status: str, details_str: str) -> str:
    """Calculates SHA256 of chained event parameters."""
    prev = previous_hash or "genesis"
    det = details_str or ""
    hash_input = f"{prev}:{event_id}:{device_id}:{timestamp}:{service}:{action}:{status}:{det}"
    return hashlib.sha256(hash_input.encode()).hexdigest()

def ingest_audit_event(device_id: str, event_id: str, timestamp: str, service: str, action: str, status: str, details: dict = None) -> dict:
    """Ingests a new audit event, calculating the cryptographically chained tamper hash."""
    # Redact sensitive parameters
    redacted_details = redact_details(details)
    details_str = json.dumps(redacted_details) if redacted_details else ""
    
    with get_db_connection() as conn:
        # Retrieve previous row's tamper_hash
        cursor = conn.execute("SELECT tamper_hash FROM audit_events ORDER BY rowid DESC LIMIT 1;")
        row = cursor.fetchone()
        previous_hash = row["tamper_hash"] if row else "genesis"
        
        # Calculate chained hash
        tamper_hash = calculate_log_hash(
            previous_hash, event_id, device_id, timestamp, service, action, status, details_str
        )
        
        conn.execute(
            """
            INSERT OR REPLACE INTO audit_events (
                event_id, device_id, timestamp, service, action, status, details, previous_hash, tamper_hash
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (event_id, device_id, timestamp, service, action, status, details_str, previous_hash, tamper_hash)
        )
        
        # Pruning check using retention settings
        try:
            cfg = load_config()
            retention_days = int(cfg.get("audit_retention_days", 90))
            conn.execute("DELETE FROM audit_events WHERE datetime(timestamp) < datetime('now', ?);", (f"-{retention_days} days",))
        except:
            pass
            
        res = conn.execute("SELECT * FROM audit_events WHERE event_id = ?;", (event_id,))
        saved = dict(res.fetchone())
        saved["details"] = json.loads(saved["details"]) if saved["details"] else None
        return saved

def get_audit_events(device_id: str = None, service: str = None, status: str = None) -> list:
    """Lists ingested audit logs, supporting basic filters."""
    query = "SELECT * FROM audit_events WHERE 1=1"
    params = []
    
    if device_id:
        query += " AND device_id = ?"
        params.append(device_id)
    if service:
        query += " AND service = ?"
        params.append(service)
    if status:
        query += " AND status = ?"
        params.append(status)
        
    query += " ORDER BY rowid DESC;"
    
    with get_db_connection() as conn:
        cursor = conn.execute(query, tuple(params))
        events = []
        for row in cursor.fetchall():
            ev = dict(row)
            ev["details"] = json.loads(ev["details"]) if ev["details"] else None
            events.append(ev)
        return events

def verify_audit_chain() -> dict:
    """Validates the chronological hash chain integrity, reporting any tamper details."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM audit_events ORDER BY rowid ASC;")
        rows = cursor.fetchall()
        
    expected_prev = rows[0]["previous_hash"] if rows else "genesis"
    if rows and not rows[0]["previous_hash"]:
        expected_prev = "genesis"
    total_checked = 0
    
    for idx, row in enumerate(rows):
        event_id = row["event_id"]
        details_str = row["details"] or ""
        
        # Verify previous_hash match
        if (row["previous_hash"] or "genesis") != expected_prev:
            return {
                "status": "tampered",
                "broken_at_index": idx,
                "broken_at_event_id": event_id,
                "reason": f"Chained previous_hash mismatch. Expected '{expected_prev}', got '{row['previous_hash']}'."
            }
            
        # Recompute expected hash
        recalculated = calculate_log_hash(
            expected_prev,
            event_id,
            row["device_id"],
            row["timestamp"],
            row["service"],
            row["action"],
            row["status"],
            details_str
        )
        
        if row["tamper_hash"] != recalculated:
            return {
                "status": "tampered",
                "broken_at_index": idx,
                "broken_at_event_id": event_id,
                "reason": f"Tamper hash mismatch. Recomputed '{recalculated}', got '{row['tamper_hash']}'."
            }
            
        expected_prev = row["tamper_hash"]
        total_checked += 1
        
    return {
        "status": "valid",
        "total_checked": total_checked
    }

def get_compliance_posture() -> dict:
    """Aggregates baseline control compliance profiles for all devices."""
    with get_db_connection() as conn:
        # Fetch latest release version per channel for patch compliance
        c_cursor = conn.execute(
            """
            SELECT channel, version FROM (
                SELECT channel, version, ROW_NUMBER() OVER (PARTITION BY channel ORDER BY created_at DESC) as rn
                FROM releases
            ) WHERE rn = 1;
            """
        )
        latest_releases = {row["channel"]: row["version"] for row in c_cursor.fetchall()}
        
        # Query devices
        d_cursor = conn.execute(
            """
            SELECT d.device_id, d.device_model, d.os_version, d.enrollment_state, d.group_id, g.release_channel
            FROM devices d
            LEFT JOIN device_groups g ON d.group_id = g.group_id;
            """
        )
        devices = d_cursor.fetchall()
        
    total_devices = len(devices)
    compliant_devices = []
    non_compliant_devices = []
    
    with get_db_connection() as conn:
        for dev in devices:
            device_id = dev["device_id"]
            state = dev["enrollment_state"]
            os_version = dev["os_version"]
            channel = dev["release_channel"] or "broad"
            
            reasons = []
            
            # Control 1: Device state must be active
            if state != "active":
                reasons.append("inactive_state")
                
            # Control 2: Health state must be healthy (no critical health alerts)
            h_cursor = conn.execute(
                """
                SELECT cpu, memory, storage, services, health_score 
                FROM health_snapshots 
                WHERE device_id = ? 
                ORDER BY timestamp DESC LIMIT 1;
                """,
                (device_id,)
            )
            h_row = h_cursor.fetchone()
            if h_row:
                if h_row["health_score"] < 80:
                    reasons.append("health_degraded")
                if "critical" in (h_row["cpu"], h_row["memory"], h_row["storage"], h_row["services"]):
                    reasons.append("health_critical_alerts")
            else:
                # No health reports yet for newly enrolled devices
                pass
                
            # Control 3: Must be on latest OS version matching release channel
            target_version = latest_releases.get(channel)
            if target_version and os_version != target_version:
                reasons.append("os_outdated")
                
            # Control 4: No policy denied events in audit history
            a_cursor = conn.execute(
                "SELECT 1 FROM audit_events WHERE device_id = ? AND status = 'denied_by_policy' LIMIT 1;",
                (device_id,)
            )
            if a_cursor.fetchone():
                reasons.append("policy_violations")
                
            dev_info = {
                "device_id": device_id,
                "device_model": dev["device_model"],
                "os_version": os_version,
                "release_channel": channel
            }
            
            if reasons:
                dev_info["non_compliance_reasons"] = reasons
                non_compliant_devices.append(dev_info)
            else:
                compliant_devices.append(dev_info)
                
    compliant_count = len(compliant_devices)
    compliance_score = (compliant_count / total_devices * 100) if total_devices > 0 else 100.0
    
    return {
        "total_devices": total_devices,
        "compliant_count": compliant_count,
        "non_compliant_count": len(non_compliant_devices),
        "compliance_score": round(compliance_score, 2),
        "compliant_devices": compliant_devices,
        "non_compliant_devices": non_compliant_devices
    }

def export_evidence(report_type: str) -> list:
    """Generates a list of structured records representing compliance verification evidence."""
    with get_db_connection() as conn:
        if report_type == "inventory":
            # Device Inventory report
            cursor = conn.execute(
                """
                SELECT d.device_id, d.device_model, d.os_version, d.enrollment_state, d.tags, d.group_id, g.name as group_name
                FROM devices d
                LEFT JOIN device_groups g ON d.group_id = g.group_id;
                """
            )
            return [dict(row) for row in cursor.fetchall()]
            
        elif report_type == "updates":
            # Updates rollout tracking status report
            cursor = conn.execute(
                """
                SELECT t.campaign_id, c.name as campaign_name, t.device_id, t.status as target_status, t.updated_at
                FROM campaign_targets t
                JOIN campaigns c ON t.campaign_id = c.campaign_id;
                """
            )
            return [dict(row) for row in cursor.fetchall()]
            
        elif report_type == "policies":
            # Policy assignments configuration report
            cursor = conn.execute(
                """
                SELECT a.assignment_id, a.policy_id, a.target_type, a.target_id, p.version as policy_version
                FROM policy_assignments a
                JOIN policies p ON a.policy_id = p.policy_id;
                """
            )
            return [dict(row) for row in cursor.fetchall()]
            
        elif report_type == "audit":
            # Cryptographically validated audit history report
            cursor = conn.execute("SELECT * FROM audit_events ORDER BY rowid ASC;")
            return [dict(row) for row in cursor.fetchall()]
            
        else:
            raise ValueError(f"Unknown report type: '{report_type}'")
