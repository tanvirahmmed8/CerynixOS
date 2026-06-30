#!/usr/bin/env python3
import sys
import os
import json
import uuid
import hashlib

# Ensure src directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from database.connection import get_db_connection
from database.schema import init_db

GROUPS = [
    {"group_id": "grp_dev_workstations", "name": "Developer Workstations", "description": "Laptops and desktops used by CerynixOS developers.", "release_channel": "pilot"},
    {"group_id": "grp_creator_studios", "name": "Creative Studio Desktops", "description": "High-end creative design workstations.", "release_channel": "canary"},
    {"group_id": "grp_security_audit", "name": "Security & Audit Staff", "description": "Restricted devices used by compliance officers.", "release_channel": "broad"}
]

TOKENS = [
    {"token": "tok_unlimited_use_9999", "organization_id": "org_default_cerynix", "max_uses": 999, "uses": 24},
    {"token": "tok_one_use_left_1111", "organization_id": "org_default_cerynix", "max_uses": 1, "uses": 0},
    {"token": "tok_exhausted_token_88", "organization_id": "org_default_cerynix", "max_uses": 5, "uses": 5}
]

DEVICES = [
    {
        "device_id": "dev-fed01d8c-76e9-4e7c-a496-e3d179df3f51",
        "device_model": "ThinkPad P1 Gen 6",
        "os_version": "cerynixos-gen-42",
        "cpu_cores": 14,
        "memory_bytes": 34359738368,
        "storage_bytes": 1099511627776,
        "installed_capabilities": ["cerynix-base", "cerynix-ai-runtime", "cerynix-action-broker", "cerynix-health-agent", "cerynix-optimizer"],
        "enrollment_state": "active",
        "tags": ["developer", "engineering"],
        "group_id": "grp_dev_workstations"
    },
    {
        "device_id": "dev-034ef84c-3c82-411a-bf41-7cf67d64b19f",
        "device_model": "MacBookPro18,3 (M1 Pro)",
        "os_version": "cerynixos-gen-42",
        "cpu_cores": 8,
        "memory_bytes": 17179869184,
        "storage_bytes": 536870912000,
        "installed_capabilities": ["cerynix-base", "cerynix-ai-runtime", "cerynix-action-broker", "cerynix-health-agent"],
        "enrollment_state": "active",
        "tags": ["remote-office"],
        "group_id": "grp_dev_workstations"
    },
    {
        "device_id": "dev-74c03de9-f673-455b-b9d9-6db8a2bf854b",
        "device_model": "Custom Threadripper Studio",
        "os_version": "cerynixos-gen-41",
        "cpu_cores": 32,
        "memory_bytes": 68719476736,
        "storage_bytes": 2199023255552,
        "installed_capabilities": ["cerynix-base", "cerynix-ai-runtime", "cerynix-action-broker", "cerynix-optimizer"],
        "enrollment_state": "active",
        "tags": ["creator", "rendering-node"],
        "group_id": "grp_creator_studios"
    },
    {
        "device_id": "dev-6cb3d4b3-d6c4-42f8-98e3-d784a0c8b212",
        "device_model": "Latitude 5430 Rugged",
        "os_version": "cerynixos-gen-39",
        "cpu_cores": 4,
        "memory_bytes": 8589934592,
        "storage_bytes": 268435456000,
        "installed_capabilities": ["cerynix-base", "cerynix-health-agent"],
        "enrollment_state": "quarantined",
        "tags": ["field-unit", "os-drift"],
        "group_id": "grp_dev_workstations"
    },
    {
        "device_id": "dev-8da74fe3-b6d8-4903-bbfd-ad8cf92b8dff",
        "device_model": "Precision 5820 Tower",
        "os_version": "cerynixos-gen-35",
        "cpu_cores": 10,
        "memory_bytes": 34359738368,
        "storage_bytes": 1099511627776,
        "installed_capabilities": ["cerynix-base"],
        "enrollment_state": "retired",
        "tags": ["legacy-hardware"],
        "group_id": None
    }
]

def seed_database():
    init_db()
    print("Seeding database tables...")
    
    with get_db_connection() as conn:
        # 1. Seed Groups
        for group in GROUPS:
            conn.execute(
                """
                INSERT INTO device_groups (group_id, name, description, release_channel)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(group_id) DO UPDATE SET
                    name = excluded.name,
                    description = excluded.description,
                    release_channel = excluded.release_channel;
                """,
                (group["group_id"], group["name"], group["description"], group["release_channel"])
            )
            
        # 2. Seed Enrollment Tokens
        for token in TOKENS:
            conn.execute(
                """
                INSERT INTO enrollment_tokens (token, organization_id, max_uses, uses)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(token) DO UPDATE SET
                    organization_id = excluded.organization_id,
                    max_uses = excluded.max_uses,
                    uses = excluded.uses;
                """,
                (token["token"], token["organization_id"], token["max_uses"], token["uses"])
            )
            
        # 3. Seed Devices
        for device in DEVICES:
            conn.execute(
                """
                INSERT INTO devices (
                    device_id, device_model, os_version, cpu_cores, memory_bytes,
                    storage_bytes, installed_capabilities, enrollment_state, tags, group_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(device_id) DO UPDATE SET
                    device_model = excluded.device_model,
                    os_version = excluded.os_version,
                    cpu_cores = excluded.cpu_cores,
                    memory_bytes = excluded.memory_bytes,
                    storage_bytes = excluded.storage_bytes,
                    installed_capabilities = excluded.installed_capabilities,
                    enrollment_state = excluded.enrollment_state,
                    tags = excluded.tags,
                    group_id = excluded.group_id;
                """,
                (
                    device["device_id"],
                    device["device_model"],
                    device["os_version"],
                    device["cpu_cores"],
                    device["memory_bytes"],
                    device["storage_bytes"],
                    json.dumps(device["installed_capabilities"]),
                    device["enrollment_state"],
                    json.dumps(device["tags"]),
                    device["group_id"]
                )
            )
            
        # 4. Seed Policies
        for policy in POLICIES:
            rules_json = json.dumps(policy["rules"])
            # Insert into policies
            conn.execute(
                """
                INSERT INTO policies (policy_id, version, rules)
                VALUES (?, ?, ?)
                ON CONFLICT(policy_id) DO UPDATE SET
                    version = excluded.version,
                    rules = excluded.rules;
                """,
                (policy["policy_id"], policy["version"], rules_json)
            )
            # Insert revision
            conn.execute(
                """
                INSERT INTO policy_revisions (policy_id, version, rules)
                VALUES (?, ?, ?)
                ON CONFLICT(policy_id, version) DO UPDATE SET
                    rules = excluded.rules;
                """,
                (policy["policy_id"], policy["version"], rules_json)
            )
            
        # 5. Seed Assignments
        for assignment in ASSIGNMENTS:
            conn.execute(
                """
                INSERT INTO policy_assignments (assignment_id, policy_id, target_type, target_id)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(assignment_id) DO UPDATE SET
                    policy_id = excluded.policy_id,
                    target_type = excluded.target_type,
                    target_id = excluded.target_id;
                """,
                (
                    assignment["assignment_id"],
                    assignment["policy_id"],
                    assignment["target_type"],
                    assignment["target_id"]
                )
            )
            
        # 6. Seed Releases
        for release in RELEASES:
            conn.execute(
                """
                INSERT INTO releases (release_id, version, channel, image_url, sha256_hash, force_rollback)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(release_id) DO UPDATE SET
                    version = excluded.version,
                    channel = excluded.channel,
                    image_url = excluded.image_url,
                    sha256_hash = excluded.sha256_hash,
                    force_rollback = excluded.force_rollback;
                """,
                (
                    release["release_id"],
                    release["version"],
                    release["channel"],
                    release["image_url"],
                    release["sha256_hash"],
                    release["force_rollback"]
                )
            )
            
        # 7. Seed Campaigns
        for campaign in CAMPAIGNS:
            conn.execute(
                """
                INSERT INTO campaigns (campaign_id, release_id, name, status)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(campaign_id) DO UPDATE SET
                    release_id = excluded.release_id,
                    name = excluded.name,
                    status = excluded.status;
                """,
                (
                    campaign["campaign_id"],
                    campaign["release_id"],
                    campaign["name"],
                    campaign["status"]
                )
            )
            
        # 9. Seed Audit Events (with valid hash chain)
        expected_prev = "genesis"
        for event in AUDIT_EVENTS:
            details_str = json.dumps(event["details"]) if event["details"] else ""
            # Compute hash
            hash_input = f"{expected_prev}:{event['event_id']}:{event['device_id']}:{event['timestamp']}:{event['service']}:{event['action']}:{event['status']}:{details_str}"
            tamper_hash = hashlib.sha256(hash_input.encode()).hexdigest()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO audit_events (
                    event_id, device_id, timestamp, service, action, status, details, previous_hash, tamper_hash
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    event["event_id"],
                    event["device_id"],
                    event["timestamp"],
                    event["service"],
                    event["action"],
                    event["status"],
                    details_str,
                    expected_prev,
                    tamper_hash
                )
            )
            expected_prev = tamper_hash
            
        # 10. Seed Health Snapshots
        for snap in HEALTH_SNAPSHOTS:
            conn.execute(
                """
                INSERT OR REPLACE INTO health_snapshots (snapshot_id, device_id, timestamp, health_score, cpu, memory, storage, services)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    snap["snapshot_id"],
                    snap["device_id"],
                    snap["timestamp"],
                    snap["health_score"],
                    snap["cpu"],
                    snap["memory"],
                    snap["storage"],
                    snap["services"]
                )
            )
            
        # 11. Seed Incidents
        for incident in INCIDENTS:
            conn.execute(
                """
                INSERT OR REPLACE INTO incidents (incident_id, device_id, title, description, status, severity, operator_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    incident["incident_id"],
                    incident["device_id"],
                    incident["title"],
                    incident["description"],
                    incident["status"],
                    incident["severity"],
                    incident["operator_notes"]
                )
            )
            
        # 12. Seed Diagnostic Commands
        for cmd in DIAGNOSTIC_COMMANDS:
            conn.execute(
                """
                INSERT OR REPLACE INTO diagnostic_commands (command_id, device_id, command, arguments, status, output)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (
                    cmd["command_id"],
                    cmd["device_id"],
                    cmd["command"],
                    cmd["arguments"],
                    cmd["status"],
                    cmd["output"]
                )
            )
            
        # 13. Seed Registry Artifacts
        for art in REGISTRY_ARTIFACTS:
            conn.execute(
                """
                INSERT OR REPLACE INTO registry_artifacts (
                    artifact_id, name, type, version, description, filename, file_size_bytes, checksum_sha256, download_url, signature, approval_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    art["artifact_id"],
                    art["name"],
                    art["type"],
                    art["version"],
                    art["description"],
                    art["filename"],
                    art["file_size_bytes"],
                    art["checksum_sha256"],
                    art["download_url"],
                    art["signature"],
                    art["approval_status"]
                )
            )
            
    print("Database seeding completed successfully.")

POLICIES = [
    {
        "policy_id": "pol_global_default",
        "version": 1,
        "rules": {
            "allowed_tools": ["systemctl status", "journalctl", "cerynix-diag"],
            "approval_mode": "ask_before_act"
        }
    },
    {
        "policy_id": "pol_dev_workstations",
        "version": 1,
        "rules": {
            "allowed_tools": ["systemctl status", "journalctl", "cerynix-diag", "nixos-rebuild switch", "cerynix-optimizer apply"],
            "approval_mode": "auto_act"
        }
    },
    {
        "policy_id": "pol_strict_sandbox",
        "version": 1,
        "rules": {
            "allowed_tools": ["systemctl status"],
            "approval_mode": "suggest_only"
        }
    }
]

ASSIGNMENTS = [
    {"assignment_id": "global", "policy_id": "pol_global_default", "target_type": "global", "target_id": None},
    {"assignment_id": "group:grp_dev_workstations", "policy_id": "pol_dev_workstations", "target_type": "group", "target_id": "grp_dev_workstations"},
    {"assignment_id": "device:dev-6cb3d4b3-d6c4-42f8-98e3-d784a0c8b212", "policy_id": "pol_strict_sandbox", "target_type": "device", "target_id": "dev-6cb3d4b3-d6c4-42f8-98e3-d784a0c8b212"}
]

RELEASES = [
    {
        "release_id": "rel_gen_43_canary",
        "version": "cerynixos-gen-43",
        "channel": "canary",
        "image_url": "https://images.cerynix.internal/releases/gen-43-canary.raw",
        "sha256_hash": "a4d3a2b1c0f9e8d7c6b5a4d3a2b1c0f9e8d7c6b5a4d3a2b1c0f9e8d7c6b5a4d3",
        "force_rollback": 0
    },
    {
        "release_id": "rel_gen_42_broad",
        "version": "cerynixos-gen-42",
        "channel": "broad",
        "image_url": "https://images.cerynix.internal/releases/gen-42.raw",
        "sha256_hash": "b5e4d3c2b1a0f9e8d7c6b5a4d3a2b1c0f9e8d7c6b5a4d3a2b1c0f9e8d7c6b5a4",
        "force_rollback": 0
    }
]

CAMPAIGNS = [
    {
        "campaign_id": "camp_gen_43_rollout",
        "release_id": "rel_gen_43_canary",
        "name": "Canary Rollout for Gen 43",
        "status": "active"
    }
]

CAMPAIGN_TARGETS = [
    {
        "campaign_id": "camp_gen_43_rollout",
        "device_id": "dev-74c03de9-f673-455b-b9d9-6db8a2bf854b",
        "status": "pending"
    }
]

AUDIT_EVENTS = [
    {
        "event_id": "evt_enroll_1234",
        "device_id": "dev-fed01d8c-76e9-4e7c-a496-e3d179df3f51",
        "timestamp": "2026-06-30T10:00:00Z",
        "service": "enrollment_agent",
        "action": "device_enrolled",
        "status": "success",
        "details": {"method": "token"}
    },
    {
        "event_id": "evt_policy_fetch_1234",
        "device_id": "dev-fed01d8c-76e9-4e7c-a496-e3d179df3f51",
        "timestamp": "2026-06-30T10:05:00Z",
        "service": "policy_broker",
        "action": "fetched_policy",
        "status": "success",
        "details": {"policy_id": "pol_dev_workstations"}
    }
]

HEALTH_SNAPSHOTS = [
    {
        "snapshot_id": "snap_dev_workstation_1",
        "device_id": "dev-fed01d8c-76e9-4e7c-a496-e3d179df3f51",
        "timestamp": "2026-06-30T10:00:00Z",
        "health_score": 95,
        "cpu": "healthy",
        "memory": "healthy",
        "storage": "healthy",
        "services": "healthy"
    },
    {
        "snapshot_id": "snap_creator_studio_1",
        "device_id": "dev-74c03de9-f673-455b-b9d9-6db8a2bf854b",
        "timestamp": "2026-06-30T10:05:00Z",
        "health_score": 75,
        "cpu": "degraded",
        "memory": "healthy",
        "storage": "healthy",
        "services": "healthy"
    }
]

INCIDENTS = [
    {
        "incident_id": "inc_creator_studio_cpu",
        "device_id": "dev-74c03de9-f673-455b-b9d9-6db8a2bf854b",
        "title": "High CPU utilization degraded alert",
        "description": "Studio desktop CPU has been in degraded state for over 30 minutes.",
        "status": "open",
        "severity": "high",
        "operator_notes": '[{"timestamp": "2026-06-30T10:10:00Z", "note": "Checked logs, seems like optimizer service is running high CPU execution tasks."}]'
    }
]

DIAGNOSTIC_COMMANDS = [
    {
        "command_id": "cmd_reboot_studio",
        "device_id": "dev-74c03de9-f673-455b-b9d9-6db8a2bf854b",
        "command": "reboot",
        "arguments": "[]",
        "status": "completed",
        "output": "System is going down for reboot now!"
    }
]

REGISTRY_ARTIFACTS = [
    {
        "artifact_id": "model_qwen25_05b_gguf",
        "name": "qwen2.5-0.5b-instruct-q4_k_m.gguf",
        "type": "model",
        "version": "1.0.0",
        "description": "Default v1 CerynixAI model for low-latency on-device processing.",
        "filename": "qwen2.5-0.5b-instruct-q4_k_m.gguf",
        "file_size_bytes": 390000000,
        "checksum_sha256": "81f1853d9e847c21f2bb8b15d2a84c21f2bb8b15d2a84c21f2bb8b15d2a84c21",
        "download_url": "https://storage.cerynix.internal/registry/models/qwen2.5-0.5b-instruct-q4_k_m.gguf",
        "signature": "dev_signature_gguf_2026",
        "approval_status": "approved"
    },
    {
        "artifact_id": "system_cerynixos_kernel_v61",
        "name": "cerynixos-kernel-6.1",
        "type": "system",
        "version": "6.1.12",
        "description": "Core LTS Linux kernel payload for Framework and ThinkPad profiles.",
        "filename": "bzImage-6.1.12",
        "file_size_bytes": 12500000,
        "checksum_sha256": "4a8c9a3b8d1e2f7c6b5d4a3c2b1a0d7c4a8c9a3b8d1e2f7c6b5d4a3c2b1a0d7c",
        "download_url": "https://storage.cerynix.internal/registry/system/bzImage-6.1.12",
        "signature": "dev_signature_kernel_2026",
        "approval_status": "approved"
    },
    {
        "artifact_id": "plugin_usb_guard",
        "name": "cerynix-plugin-usbguard",
        "type": "plugin",
        "version": "2.1.0",
        "description": "USBGuard capability extension daemon for device hardware authorization policies.",
        "filename": "plugin-usbguard-2.1.0.tar.gz",
        "file_size_bytes": 45000,
        "checksum_sha256": "9b8a7c6d5e4d3c2b1a0f9e8d7c6b5a4f9b8a7c6d5e4d3c2b1a0f9e8d7c6b5a4f",
        "download_url": "https://storage.cerynix.internal/registry/plugins/plugin-usbguard-2.1.0.tar.gz",
        "signature": "dev_signature_usbguard_2026",
        "approval_status": "pending"
    }
]

if __name__ == "__main__":
    seed_database()
