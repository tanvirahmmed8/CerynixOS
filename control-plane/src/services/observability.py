import json
import uuid
from datetime import datetime, timezone, timedelta
from database.connection import get_db_connection

VALID_HEALTH_STATES = {"healthy", "degraded", "critical"}
VALID_INCIDENT_STATUSES = {"open", "resolved", "investigating"}
VALID_INCIDENT_SEVERITIES = {"low", "medium", "high", "critical"}
VALID_COMMAND_STATUSES = {"pending", "running", "completed", "failed"}

def ingest_health_snapshot(device_id: str, snapshot_id: str, timestamp: str, health_score: int, cpu: str, memory: str, storage: str, services: str) -> dict:
    """Ingests a resource health snapshot reported from the device plane."""
    if {cpu, memory, storage, services} - VALID_HEALTH_STATES:
        raise ValueError(f"Components must be one of {VALID_HEALTH_STATES}")
        
    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO health_snapshots (snapshot_id, device_id, timestamp, health_score, cpu, memory, storage, services)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (snapshot_id, device_id, timestamp, health_score, cpu, memory, storage, services)
        )
        
        cursor = conn.execute("SELECT * FROM health_snapshots WHERE snapshot_id = ?;", (snapshot_id,))
        return dict(cursor.fetchone())

def get_fleet_health_overview() -> dict:
    """Aggregates active device health snapshots into fleet-wide summary indexes."""
    with get_db_connection() as conn:
        # Get latest snapshot for each active device
        cursor = conn.execute(
            """
            SELECT h.* FROM health_snapshots h
            JOIN (
                SELECT device_id, MAX(timestamp) as max_t 
                FROM health_snapshots 
                GROUP BY device_id
            ) latest ON h.device_id = latest.device_id AND h.timestamp = latest.max_t
            JOIN devices d ON h.device_id = d.device_id
            WHERE d.enrollment_state = 'active';
            """
        )
        snapshots = cursor.fetchall()
        
    total = len(snapshots)
    if total == 0:
        return {
            "total_active_devices": 0,
            "average_health_score": 100.0,
            "healthy_count": 0,
            "degraded_count": 0,
            "critical_count": 0,
            "resource_alerts": {"cpu": 0, "memory": 0, "storage": 0, "services": 0}
        }
        
    sum_score = 0
    healthy = 0
    degraded = 0
    critical = 0
    
    resources = {"cpu": 0, "memory": 0, "storage": 0, "services": 0}
    
    for snap in snapshots:
        score = snap["health_score"]
        sum_score += score
        
        if score >= 80:
            healthy += 1
        elif score >= 50:
            degraded += 1
        else:
            critical += 1
            
        for key in ["cpu", "memory", "storage", "services"]:
            if snap[key] in ("degraded", "critical"):
                resources[key] = resources.get(key, 0) + 1
                
    return {
        "total_active_devices": total,
        "average_health_score": round(sum_score / total, 2),
        "healthy_count": healthy,
        "degraded_count": degraded,
        "critical_count": critical,
        "resource_alerts": resources
    }

def get_active_alerts() -> list:
    """Dynamically aggregates alerts for offline devices, hardware alerts, and policy denies."""
    alerts = []
    now = datetime.now(timezone.utc)
    
    with get_db_connection() as conn:
        # Query active devices and their latest health report timestamp
        d_cursor = conn.execute(
            """
            SELECT d.device_id, d.device_model, MAX(h.timestamp) as last_seen 
            FROM devices d 
            LEFT JOIN health_snapshots h ON d.device_id = h.device_id 
            WHERE d.enrollment_state = 'active' 
            GROUP BY d.device_id;
            """
        )
        devices = d_cursor.fetchall()
        
        for dev in devices:
            device_id = dev["device_id"]
            model = dev["device_model"]
            last_seen_str = dev["last_seen"]
            
            # 1. Offline Alert check (no reports in 15 minutes or ever)
            is_offline = False
            if not last_seen_str:
                is_offline = True
            else:
                try:
                    # Parse timestamp (handle both ISO formats with/without Z/offsets)
                    t_str = last_seen_str.replace("Z", "+00:00")
                    last_seen_dt = datetime.fromisoformat(t_str)
                    if (now - last_seen_dt) > timedelta(minutes=15):
                        is_offline = True
                except ValueError:
                    is_offline = True
                    
            if is_offline:
                alerts.append({
                    "device_id": device_id,
                    "alert_type": "device_offline",
                    "severity": "critical",
                    "message": f"Device '{model}' ({device_id}) is offline or has stopped reporting health.",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
            # 2. Hardware alerts (query latest snapshot details)
            h_cursor = conn.execute(
                """
                SELECT * FROM health_snapshots 
                WHERE device_id = ? 
                ORDER BY timestamp DESC LIMIT 1;
                """,
                (device_id,)
            )
            h_row = h_cursor.fetchone()
            if h_row:
                for key in ["cpu", "memory", "storage", "services"]:
                    status = h_row[key]
                    if status in ("degraded", "critical"):
                        severity = "critical" if status == "critical" else "warning"
                        alerts.append({
                            "device_id": device_id,
                            "alert_type": f"resource_{key}_degraded",
                            "severity": severity,
                            "message": f"Device '{model}' reports resource '{key}' status as '{status}'. Score: {h_row['health_score']}.",
                            "timestamp": h_row["timestamp"]
                        })
                        
            # 3. Security alerts (policy denies in the last 2 hours)
            time_limit = (now - timedelta(hours=2)).isoformat()
            a_cursor = conn.execute(
                """
                SELECT event_id, service, action, timestamp 
                FROM audit_events 
                WHERE device_id = ? AND status = 'denied_by_policy' AND timestamp >= ?;
                """,
                (device_id, time_limit)
            )
            for audit in a_cursor.fetchall():
                alerts.append({
                    "device_id": device_id,
                    "alert_type": "security_policy_denial",
                    "severity": "high",
                    "message": f"Security violation detected: action '{audit['action']}' on service '{audit['service']}' was denied.",
                    "timestamp": audit["timestamp"]
                })
                
    return alerts

def register_support_bundle(device_id: str, bundle_id: str, timestamp: str, bundle_size_bytes: int, bundle_url: str, trigger_reason: str, redaction_applied: bool = True, metadata: dict = None) -> dict:
    """Registers metadata for a diagnostic support bundle package."""
    meta_str = json.dumps(metadata) if metadata else ""
    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO support_bundles (bundle_id, device_id, timestamp, bundle_size_bytes, bundle_url, trigger_reason, redaction_applied, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (bundle_id, device_id, timestamp, bundle_size_bytes, bundle_url, trigger_reason, 1 if redaction_applied else 0, meta_str)
        )
        
        cursor = conn.execute("SELECT * FROM support_bundles WHERE bundle_id = ?;", (bundle_id,))
        res = dict(cursor.fetchone())
        res["metadata"] = json.loads(res["metadata"]) if res["metadata"] else None
        res["redaction_applied"] = bool(res["redaction_applied"])
        return res

def get_support_bundles() -> list:
    """Lists all support bundles registered."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM support_bundles ORDER BY timestamp DESC;")
        results = []
        for row in cursor.fetchall():
            res = dict(row)
            res["metadata"] = json.loads(res["metadata"]) if res["metadata"] else None
            res["redaction_applied"] = bool(res["redaction_applied"])
            results.append(res)
        return results

def create_incident(incident_id: str, device_id: str, title: str, description: str = None, severity: str = "medium") -> dict:
    """Creates a new fleet support ticket/incident."""
    if severity not in VALID_INCIDENT_SEVERITIES:
        raise ValueError(f"Severity must be one of {VALID_INCIDENT_SEVERITIES}")
        
    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO incidents (incident_id, device_id, title, description, status, severity, operator_notes)
            VALUES (?, ?, ?, ?, 'open', ?, '[]');
            """,
            (incident_id, device_id, title, description, severity)
        )
        cursor = conn.execute("SELECT * FROM incidents WHERE incident_id = ?;", (incident_id,))
        res = dict(cursor.fetchone())
        res["operator_notes"] = json.loads(res["operator_notes"])
        return res

def update_incident(incident_id: str, status: str = None, severity: str = None, operator_note: str = None) -> dict:
    """Updates status, severity, and appends a new operator note log entry."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM incidents WHERE incident_id = ?;", (incident_id,))
        row = cursor.fetchone()
        if not row:
            return None
        curr = dict(row)
        
        up_status = status or curr["status"]
        up_severity = severity or curr["severity"]
        notes = json.loads(curr["operator_notes"]) if curr["operator_notes"] else []
        
        if operator_note:
            note_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "note": operator_note
            }
            notes.append(note_entry)
            
        if up_status not in VALID_INCIDENT_STATUSES:
            raise ValueError(f"Status must be one of {VALID_INCIDENT_STATUSES}")
        if up_severity not in VALID_INCIDENT_SEVERITIES:
            raise ValueError(f"Severity must be one of {VALID_INCIDENT_SEVERITIES}")
            
        conn.execute(
            """
            UPDATE incidents 
            SET status = ?, severity = ?, operator_notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE incident_id = ?;
            """,
            (up_status, up_severity, json.dumps(notes), incident_id)
        )
        
        cursor = conn.execute("SELECT * FROM incidents WHERE incident_id = ?;", (incident_id,))
        res = dict(cursor.fetchone())
        res["operator_notes"] = json.loads(res["operator_notes"])
        return res

def get_incidents() -> list:
    """Retrieves all operator incident tickets."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM incidents ORDER BY created_at DESC;")
        results = []
        for row in cursor.fetchall():
            res = dict(row)
            res["operator_notes"] = json.loads(res["operator_notes"]) if res["operator_notes"] else []
            results.append(res)
        return results

def enqueue_diagnostic_command(command_id: str, device_id: str, command: str, arguments: list = None) -> dict:
    """Enqueues a Remote Diagnostic Command for device agent consumption."""
    args_str = json.dumps(arguments) if arguments else "[]"
    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO diagnostic_commands (command_id, device_id, command, arguments, status, output)
            VALUES (?, ?, ?, ?, 'pending', NULL);
            """,
            (command_id, device_id, command, args_str)
        )
        cursor = conn.execute("SELECT * FROM diagnostic_commands WHERE command_id = ?;", (command_id,))
        res = dict(cursor.fetchone())
        res["arguments"] = json.loads(res["arguments"])
        return res

def poll_pending_command(device_id: str) -> dict:
    """Device client pull action: fetches oldest pending task, promoting it to running."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM diagnostic_commands 
            WHERE device_id = ? AND status = 'pending' 
            ORDER BY created_at ASC LIMIT 1;
            """,
            (device_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        cmd = dict(row)
        
        # Transition status to running
        conn.execute(
            "UPDATE diagnostic_commands SET status = 'running', updated_at = CURRENT_TIMESTAMP WHERE command_id = ?;",
            (cmd["command_id"],)
        )
        
    cmd["status"] = "running"
    cmd["arguments"] = json.loads(cmd["arguments"]) if cmd["arguments"] else []
    return cmd

def report_command_results(command_id: str, status: str, output: str) -> dict:
    """Device client report action: registers execution results, completing the diagnostic task."""
    if status not in ("completed", "failed"):
        raise ValueError("Diagnostic execution status must be either 'completed' or 'failed'.")
        
    with get_db_connection() as conn:
        conn.execute(
            """
            UPDATE diagnostic_commands 
            SET status = ?, output = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE command_id = ?;
            """,
            (status, output, command_id)
        )
        
        cursor = conn.execute("SELECT * FROM diagnostic_commands WHERE command_id = ?;", (command_id,))
        row = cursor.fetchone()
        if not row:
            return None
        res = dict(row)
        res["arguments"] = json.loads(res["arguments"]) if res["arguments"] else []
        return res

def get_diagnostic_history(device_id: str) -> list:
    """Admin-only: lists execution trails of remote diagnostics on a device."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            "SELECT * FROM diagnostic_commands WHERE device_id = ? ORDER BY created_at DESC;",
            (device_id,)
        )
        results = []
        for row in cursor.fetchall():
            res = dict(row)
            res["arguments"] = json.loads(res["arguments"]) if res["arguments"] else []
            results.append(res)
        return results

def get_device_timeline(device_id: str) -> list:
    """Aggregates and merges diagnostic history, health snapshots, support bundles, and incidents into a chronological timeline."""
    timeline = []
    
    with get_db_connection() as conn:
        # 1. Fetch Audit Events
        a_cursor = conn.execute("SELECT timestamp, action, service, status, details FROM audit_events WHERE device_id = ?;", (device_id,))
        for row in a_cursor.fetchall():
            timeline.append({
                "timestamp": row["timestamp"],
                "event_type": "audit_event",
                "title": f"Audit: {row['action']} on {row['service']}",
                "details": {"status": row["status"], "details": json.loads(row["details"]) if row["details"] else None}
            })
            
        # 2. Fetch Health Snapshots
        h_cursor = conn.execute("SELECT timestamp, health_score, cpu, memory, storage, services FROM health_snapshots WHERE device_id = ?;", (device_id,))
        for row in h_cursor.fetchall():
            timeline.append({
                "timestamp": row["timestamp"],
                "event_type": "health_snapshot",
                "title": f"Telemetry Check: Score {row['health_score']}",
                "details": {"cpu": row["cpu"], "memory": row["memory"], "storage": row["storage"], "services": row["services"]}
            })
            
        # 3. Fetch Support Bundles
        b_cursor = conn.execute("SELECT timestamp, bundle_id, trigger_reason, bundle_size_bytes FROM support_bundles WHERE device_id = ?;", (device_id,))
        for row in b_cursor.fetchall():
            timeline.append({
                "timestamp": row["timestamp"],
                "event_type": "support_bundle",
                "title": "Support bundle generated",
                "details": {"bundle_id": row["bundle_id"], "trigger_reason": row["trigger_reason"], "size_bytes": row["bundle_size_bytes"]}
            })
            
        # 4. Fetch Incidents
        i_cursor = conn.execute("SELECT created_at, incident_id, title, status, severity FROM incidents WHERE device_id = ?;", (device_id,))
        for row in i_cursor.fetchall():
            timeline.append({
                "timestamp": row["created_at"],
                "event_type": "incident",
                "title": f"Incident Opened: {row['title']}",
                "details": {"incident_id": row["incident_id"], "status": row["status"], "severity": row["severity"]}
            })
            
        # 5. Fetch Diagnostic Commands
        c_cursor = conn.execute("SELECT created_at, command, status, output FROM diagnostic_commands WHERE device_id = ?;", (device_id,))
        for row in c_cursor.fetchall():
            timeline.append({
                "timestamp": row["created_at"],
                "event_type": "diagnostic_command",
                "title": f"Diagnostics: Executed '{row['command']}'",
                "details": {"status": row["status"], "output": row["output"]}
            })
            
    # Sort descending by timestamp
    timeline.sort(key=lambda x: x["timestamp"], reverse=True)
    return timeline

def get_unhealthy_devices_workflow() -> list:
    """Filters the active fleet to return only devices failing baseline health or compliance criteria."""
    from services.governance import get_compliance_posture
    posture = get_compliance_posture()
    
    # Unhealthy devices are those that are non-compliant, or have low health_score
    unhealthy = []
    
    # Add non-compliant devices
    for dev in posture.get("non_compliant_devices", []):
        unhealthy.append({
            "device_id": dev["device_id"],
            "device_model": dev["device_model"],
            "os_version": dev["os_version"],
            "release_channel": dev["release_channel"],
            "status": "non_compliant",
            "reasons": dev.get("non_compliance_reasons", [])
        })
        
    # Also fetch any active device whose latest health snapshot is < 80
    with get_db_connection() as conn:
        cursor = conn.execute(
            """
            SELECT h.device_id, d.device_model, h.health_score 
            FROM health_snapshots h
            JOIN (
                SELECT device_id, MAX(timestamp) as max_t 
                FROM health_snapshots 
                GROUP BY device_id
            ) latest ON h.device_id = latest.device_id AND h.timestamp = latest.max_t
            JOIN devices d ON h.device_id = d.device_id
            WHERE d.enrollment_state = 'active' AND h.health_score < 80;
            """
        )
        low_health = {row["device_id"]: row["health_score"] for row in cursor.fetchall()}
        
    for dev_id, score in low_health.items():
        # Avoid duplicate additions
        found = False
        for u in unhealthy:
            if u["device_id"] == dev_id:
                u["health_score"] = score
                if "health_degraded" not in u["reasons"]:
                    u["reasons"].append("health_degraded")
                found = True
                break
        if not found:
            # Get device details
            with get_db_connection() as conn:
                d_row = conn.execute("SELECT device_model, os_version FROM devices WHERE device_id = ?;", (dev_id,)).fetchone()
            if d_row:
                unhealthy.append({
                    "device_id": dev_id,
                    "device_model": d_row["device_model"],
                    "os_version": d_row["os_version"],
                    "status": "degraded_health",
                    "health_score": score,
                    "reasons": ["health_degraded"]
                })
                
    return unhealthy

def simulate_device_failure(device_id: str, failure_type: str) -> dict:
    """Injects a synthetic health snapshot to simulate critical failure states for testing."""
    valid_failures = {"cpu_spike", "memory_leak", "service_crash"}
    if failure_type not in valid_failures:
        raise ValueError(f"Invalid failure type. Must be one of {valid_failures}")
        
    snapshot_id = f"synthetic_fail_{uuid.uuid4().hex[:8]}"
    timestamp = datetime.now(timezone.utc).isoformat()
    
    if failure_type == "cpu_spike":
        return ingest_health_snapshot(device_id, snapshot_id, timestamp, 45, "critical", "healthy", "healthy", "healthy")
    elif failure_type == "memory_leak":
        return ingest_health_snapshot(device_id, snapshot_id, timestamp, 50, "healthy", "critical", "healthy", "healthy")
    else: # service_crash
        return ingest_health_snapshot(device_id, snapshot_id, timestamp, 30, "healthy", "healthy", "healthy", "critical")

