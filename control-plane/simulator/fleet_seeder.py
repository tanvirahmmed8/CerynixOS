#!/usr/bin/env python3
import sys
import os
import json
import uuid

# Ensure src directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from database.connection import get_db_connection
from database.schema import init_db

GROUPS = [
    {"group_id": "grp_dev_workstations", "name": "Developer Workstations", "description": "Laptops and desktops used by CerynixOS developers."},
    {"group_id": "grp_creator_studios", "name": "Creative Studio Desktops", "description": "High-end creative design workstations."},
    {"group_id": "grp_security_audit", "name": "Security & Audit Staff", "description": "Restricted devices used by compliance officers."}
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
                INSERT INTO device_groups (group_id, name, description)
                VALUES (?, ?, ?)
                ON CONFLICT(group_id) DO UPDATE SET
                    name = excluded.name,
                    description = excluded.description;
                """,
                (group["group_id"], group["name"], group["description"])
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

if __name__ == "__main__":
    seed_database()
