import unittest
import threading
import time
import requests
import sqlite3
import os
import sys

# Ensure src directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import uvicorn
from main import app
from database.connection import get_db_path, get_db_connection
from services.auth import verify_token, HTTPAuthorizationCredentials

class TestControlPlaneAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use a separate test database file
        cls.test_db = os.path.abspath(os.path.join(os.path.dirname(__file__), "../db/control_plane_test.db"))
        
        # Override connection.get_db_path
        import database.connection
        database.connection.get_db_path = lambda: cls.test_db
        
        # Remove old test DB if exists
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)
            
        # Startup uvicorn server on a test port
        cls.server_thread = threading.Thread(
            target=uvicorn.run,
            args=(app,),
            kwargs={"host": "127.0.0.1", "port": 8080, "log_level": "error"},
            daemon=True
        )
        cls.server_thread.start()
        
        # Give the server a moment to start
        time.sleep(1.5)

    @classmethod
    def tearDownClass(cls):
        # Remove test DB at the end
        if os.path.exists(cls.test_db):
            try:
                os.remove(cls.test_db)
                # Remove WAL/SHM files too
                if os.path.exists(cls.test_db + "-wal"):
                    os.remove(cls.test_db + "-wal")
                if os.path.exists(cls.test_db + "-shm"):
                    os.remove(cls.test_db + "-shm")
            except:
                pass

    def setUp(self):
        # Clear out tables between tests to ensure test isolation
        with get_db_connection() as conn:
            conn.execute("DELETE FROM audit_events;")
            conn.execute("DELETE FROM campaign_targets;")
            conn.execute("DELETE FROM campaigns;")
            conn.execute("DELETE FROM releases;")
            conn.execute("DELETE FROM policy_assignments;")
            conn.execute("DELETE FROM policy_revisions;")
            conn.execute("DELETE FROM policies;")
            conn.execute("DELETE FROM devices;")
            conn.execute("DELETE FROM enrollment_tokens;")
            conn.execute("DELETE FROM device_groups;")

    def test_database_initialization(self):
        """Verify that the SQLite database and all 11 tables are initialized on server start."""
        self.assertTrue(os.path.exists(self.test_db))
        
        expected_tables = {
            "device_groups", "enrollment_tokens", "devices", "policies",
            "policy_assignments", "releases", "campaigns", "campaign_targets",
            "audit_events", "health_snapshots", "support_bundles"
        }
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = {row["name"] for row in cursor.fetchall()}
            
        for table in expected_tables:
            self.assertIn(table, tables)

    def test_health_endpoint(self):
        """Verify the health status endpoint responds correctly."""
        res = requests.get("http://127.0.0.1:8080/api/v1/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")

    def test_readiness_endpoint(self):
        """Verify the readiness endpoint checks database responsiveness."""
        res = requests.get("http://127.0.0.1:8080/api/v1/readiness")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ready")
        self.assertEqual(data["database"], "connected")

    def test_correlation_id_middleware(self):
        """Verify request correlation middleware generates and passes back X-Correlation-ID."""
        # Case A: Request without correlation ID header
        res = requests.get("http://127.0.0.1:8080/api/v1/health")
        self.assertIn("X-Correlation-ID", res.headers)
        correlation_id_1 = res.headers["X-Correlation-ID"]
        self.assertTrue(len(correlation_id_1) > 0)
        
        # Case B: Request with existing correlation ID header
        custom_id = "test-corr-id-12345"
        res2 = requests.get(
            "http://127.0.0.1:8080/api/v1/health",
            headers={"X-Correlation-ID": custom_id}
        )
        self.assertEqual(res2.headers.get("X-Correlation-ID"), custom_id)

    def test_auth_scaffold_verification(self):
        """Verify token validation matches config and triggers correct error codes."""
        # Using correct credentials
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token_cerynix_secret_key_2026")
        token = verify_token(creds)
        self.assertEqual(token, "token_cerynix_secret_key_2026")
        
        # Using incorrect credentials raises HTTP 401
        from fastapi import HTTPException
        creds_bad = HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad_token")
        with self.assertRaises(HTTPException) as ctx:
            verify_token(creds_bad)
        self.assertEqual(ctx.exception.status_code, 401)

    def test_enrollment_and_inventory_lifecycle(self):
        """Verify the full device registration, group assignment, search, and transition lifecycle."""
        headers = {"Authorization": "Bearer token_cerynix_secret_key_2026"}
        
        # 1. Create a device group
        group_payload = {
            "group_id": "grp_test_units",
            "name": "Test Units Group",
            "description": "Group for testing device list operations."
        }
        res_g = requests.post("http://127.0.0.1:8080/api/v1/device-groups", json=group_payload, headers=headers)
        self.assertEqual(res_g.status_code, 201)
        
        # 2. List groups
        res_lg = requests.get("http://127.0.0.1:8080/api/v1/device-groups", headers=headers)
        self.assertEqual(res_lg.status_code, 200)
        groups = [g["group_id"] for g in res_lg.json()]
        self.assertIn("grp_test_units", groups)

        # 3. Create an enrollment token (max_uses = 1)
        token_payload = {
            "organization_id": "org_test_enterprise",
            "max_uses": 1
        }
        res_t = requests.post("http://127.0.0.1:8080/api/v1/enrollment-tokens", json=token_payload, headers=headers)
        self.assertEqual(res_t.status_code, 201)
        token_data = res_t.json()
        token = token_data["token"]
        self.assertTrue(token.startswith("tok_"))
        
        # 4. Enroll device 1 with token
        device_id_1 = "dev-test-lifecycle-device-1"
        enroll_payload = {
            "enrollment_token": token,
            "device_id": device_id_1,
            "device_model": "ThinkPad P1 Gen 6",
            "os_version": "cerynixos-gen-42",
            "hardware_profile": {
                "cpu_cores": 8,
                "memory_bytes": 17179869184,
                "storage_bytes": 536870912000
            },
            "installed_capabilities": ["cerynix-base", "cerynix-healer"]
        }
        res_e1 = requests.post("http://127.0.0.1:8080/api/v1/enroll", json=enroll_payload)
        self.assertEqual(res_e1.status_code, 200)
        self.assertEqual(res_e1.json()["status"], "enrolled")
        
        # 5. Try enrolling device 2 with the same (now exhausted) token -> must fail HTTP 400
        device_id_2 = "dev-test-lifecycle-device-2"
        enroll_payload_2 = dict(enroll_payload)
        enroll_payload_2["device_id"] = device_id_2
        res_e2 = requests.post("http://127.0.0.1:8080/api/v1/enroll", json=enroll_payload_2)
        self.assertEqual(res_e2.status_code, 400)
        self.assertIn("Invalid, expired, or fully-consumed", res_e2.json()["detail"])

        # 6. Retrieve single device specification (requires auth)
        res_get = requests.get(f"http://127.0.0.1:8080/api/v1/devices/{device_id_1}", headers=headers)
        self.assertEqual(res_get.status_code, 200)
        device_data = res_get.json()
        self.assertEqual(device_data["enrollment_state"], "enrolled")
        self.assertEqual(device_data["device_model"], "ThinkPad P1 Gen 6")
        self.assertEqual(device_data["installed_capabilities"], ["cerynix-base", "cerynix-healer"])

        # 7. Update device group, tags and transition state (requires auth)
        update_payload = {
            "enrollment_state": "active",
            "group_id": "grp_test_units",
            "tags": ["pilot", "test-run"]
        }
        res_patch = requests.patch(f"http://127.0.0.1:8080/api/v1/devices/{device_id_1}", json=update_payload, headers=headers)
        self.assertEqual(res_patch.status_code, 200)
        updated_device = res_patch.json()
        self.assertEqual(updated_device["enrollment_state"], "active")
        self.assertEqual(updated_device["group_id"], "grp_test_units")
        self.assertEqual(updated_device["tags"], ["pilot", "test-run"])

        # 8. List devices with filters
        # Filter by state
        res_filter_state = requests.get("http://127.0.0.1:8080/api/v1/devices?state=active", headers=headers)
        self.assertEqual(res_filter_state.status_code, 200)
        self.assertEqual(len(res_filter_state.json()), 1)
        self.assertEqual(res_filter_state.json()[0]["device_id"], device_id_1)
        
        # Filter by group_id
        res_filter_group = requests.get("http://127.0.0.1:8080/api/v1/devices?group_id=grp_test_units", headers=headers)
        self.assertEqual(res_filter_group.status_code, 200)
        self.assertEqual(len(res_filter_group.json()), 1)
        
        # Filter by tag
        res_filter_tag = requests.get("http://127.0.0.1:8080/api/v1/devices?tag=pilot", headers=headers)
        self.assertEqual(res_filter_tag.status_code, 200)
        self.assertEqual(len(res_filter_tag.json()), 1)
        
        # Filter by tag (non-matching)
        res_filter_tag_no = requests.get("http://127.0.0.1:8080/api/v1/devices?tag=nonexistent", headers=headers)
        self.assertEqual(res_filter_tag_no.status_code, 200)
        self.assertEqual(len(res_filter_tag_no.json()), 0)

        # Keyword query search
        res_search = requests.get("http://127.0.0.1:8080/api/v1/devices?query=ThinkPad", headers=headers)
        self.assertEqual(res_search.status_code, 200)
        self.assertEqual(len(res_search.json()), 1)

        # 9. Invalid transition check (retiring device is terminal)
        requests.patch(f"http://127.0.0.1:8080/api/v1/devices/{device_id_1}", json={"enrollment_state": "retired"}, headers=headers)
        res_patch_invalid = requests.patch(f"http://127.0.0.1:8080/api/v1/devices/{device_id_1}", json={"enrollment_state": "active"}, headers=headers)
        self.assertEqual(res_patch_invalid.status_code, 400)
        self.assertIn("Cannot transition a device out of 'retired'", res_patch_invalid.json()["detail"])

    def test_policy_engine_operations(self):
        """Verify policy dry-runs, CRUD, versioning, assignments, precedence resolution, and rollbacks."""
        headers = {"Authorization": "Bearer token_cerynix_secret_key_2026"}

        # 1. Dry Run Validation
        # Valid syntax
        good_rules = {
            "allowed_tools": ["systemctl status", "reboot"],
            "approval_mode": "ask_before_act"
        }
        res_dry_ok = requests.post("http://127.0.0.1:8080/api/v1/policies/dry-run", json=good_rules, headers=headers)
        self.assertEqual(res_dry_ok.status_code, 200)
        self.assertEqual(res_dry_ok.json()["status"], "valid")

        # Invalid syntax (bad approval mode)
        bad_rules = {
            "allowed_tools": ["systemctl status"],
            "approval_mode": "incorrect_mode"
        }
        res_dry_bad = requests.post("http://127.0.0.1:8080/api/v1/policies/dry-run", json=bad_rules, headers=headers)
        self.assertEqual(res_dry_bad.status_code, 400)

        # 2. CRUD: Create & update policy rules (version tracking)
        policy_id = "pol_test_ops"
        res_p1 = requests.post("http://127.0.0.1:8080/api/v1/policies", json={"policy_id": policy_id, "rules": good_rules}, headers=headers)
        self.assertEqual(res_p1.status_code, 201)
        self.assertEqual(res_p1.json()["version"], 1)

        # Update the rules to create version 2
        updated_rules = {
            "allowed_tools": ["systemctl status", "reboot", "nixos-rebuild switch"],
            "approval_mode": "auto_act"
        }
        res_p2 = requests.post("http://127.0.0.1:8080/api/v1/policies", json={"policy_id": policy_id, "rules": updated_rules}, headers=headers)
        self.assertEqual(res_p2.status_code, 201)
        self.assertEqual(res_p2.json()["version"], 2)

        # Verify revisions list
        res_rev = requests.get(f"http://127.0.0.1:8080/api/v1/policies/{policy_id}/revisions", headers=headers)
        self.assertEqual(res_rev.status_code, 200)
        self.assertEqual(len(res_rev.json()), 2)
        self.assertEqual(res_rev.json()[0]["version"], 2)
        self.assertEqual(res_rev.json()[1]["version"], 1)

        # 3. Policy Assignments
        # Create a test group and device for target verification
        group_id = "grp_policy_test"
        requests.post("http://127.0.0.1:8080/api/v1/device-groups", json={"group_id": group_id, "name": "Policy Test Group"}, headers=headers)
        
        # We need a token to enroll
        res_t = requests.post("http://127.0.0.1:8080/api/v1/enrollment-tokens", json={"organization_id": "org_test", "max_uses": 5}, headers=headers)
        token = res_t.json()["token"]
        
        device_id = "dev-policy-test-device"
        enroll_payload = {
            "enrollment_token": token,
            "device_id": device_id,
            "device_model": "Studio Tower",
            "os_version": "cerynixos-gen-42",
            "hardware_profile": {"cpu_cores": 8, "memory_bytes": 1024, "storage_bytes": 1024},
            "installed_capabilities": ["cerynix-base"]
        }
        requests.post("http://127.0.0.1:8080/api/v1/enroll", json=enroll_payload)
        requests.patch(f"http://127.0.0.1:8080/api/v1/devices/{device_id}", json={"group_id": group_id}, headers=headers)

        # Establish global, group, and device policies
        global_policy = "pol_global"
        group_policy = "pol_group"
        device_policy = "pol_device"

        requests.post("http://127.0.0.1:8080/api/v1/policies", json={"policy_id": global_policy, "rules": {"allowed_tools": ["global-tool"], "approval_mode": "suggest_only"}}, headers=headers)
        requests.post("http://127.0.0.1:8080/api/v1/policies", json={"policy_id": group_policy, "rules": {"allowed_tools": ["group-tool"], "approval_mode": "ask_before_act"}}, headers=headers)
        requests.post("http://127.0.0.1:8080/api/v1/policies", json={"policy_id": device_policy, "rules": {"allowed_tools": ["device-tool"], "approval_mode": "auto_act"}}, headers=headers)

        # Assign global scope
        requests.post(f"http://127.0.0.1:8080/api/v1/policies/{global_policy}/assign", json={"target_type": "global"}, headers=headers)
        
        # Test Case A: Only global policy is assigned
        res_res1 = requests.get(f"http://127.0.0.1:8080/api/v1/devices/{device_id}/policy")
        self.assertEqual(res_res1.status_code, 200)
        self.assertEqual(res_res1.json()["policy_id"], global_policy)

        # Assign group scope
        requests.post(f"http://127.0.0.1:8080/api/v1/policies/{group_policy}/assign", json={"target_type": "group", "target_id": group_id}, headers=headers)

        # Test Case B: Group policy matches over global (Group > Global)
        res_res2 = requests.get(f"http://127.0.0.1:8080/api/v1/devices/{device_id}/policy")
        self.assertEqual(res_res2.status_code, 200)
        self.assertEqual(res_res2.json()["policy_id"], group_policy)

        # Assign device scope
        requests.post(f"http://127.0.0.1:8080/api/v1/policies/{device_policy}/assign", json={"target_type": "device", "target_id": device_id}, headers=headers)

        # Test Case C: Device policy matches over group (Device > Group)
        res_res3 = requests.get(f"http://127.0.0.1:8080/api/v1/devices/{device_id}/policy")
        self.assertEqual(res_res3.status_code, 200)
        self.assertEqual(res_res3.json()["policy_id"], device_policy)

        # 4. Rollback policy (Rollback Version 2 of pol_test_ops to version 1)
        res_roll = requests.post(f"http://127.0.0.1:8080/api/v1/policies/{policy_id}/rollback", json={"version": 1}, headers=headers)
        self.assertEqual(res_roll.status_code, 200)
        self.assertEqual(res_roll.json()["version"], 3)  # Re-applied as version 3
        self.assertEqual(res_roll.json()["rules"]["allowed_tools"], ["systemctl status", "reboot"])

    def test_update_orchestration_campaigns(self):
        """Verify release registration, update campaigns, staged rollouts, status progress reporting, pausing, rollbacks, and compliance dashboard metrics."""
        headers = {"Authorization": "Bearer token_cerynix_secret_key_2026"}

        # 1. Register Release
        release_id = "rel_test_gen_50"
        payload_rel = {
            "release_id": release_id,
            "version": "cerynixos-gen-50",
            "channel": "pilot",
            "image_url": "https://images.cerynix.internal/releases/gen-50.raw",
            "sha256_hash": "abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcd",
            "force_rollback": False
        }
        res_rel = requests.post("http://127.0.0.1:8080/api/v1/updates/releases", json=payload_rel, headers=headers)
        self.assertEqual(res_rel.status_code, 201)
        self.assertEqual(res_rel.json()["release_id"], release_id)

        # 2. Setup Device/Group Targets
        group_id = "grp_update_test"
        requests.post("http://127.0.0.1:8080/api/v1/device-groups", json={"group_id": group_id, "name": "Update Test Group", "release_channel": "pilot"}, headers=headers)

        res_t = requests.post("http://127.0.0.1:8080/api/v1/enrollment-tokens", json={"organization_id": "org_test", "max_uses": 5}, headers=headers)
        token = res_t.json()["token"]
        
        device_id = "dev-update-test-device"
        enroll_payload = {
            "enrollment_token": token,
            "device_id": device_id,
            "device_model": "ThinkStation P620",
            "os_version": "cerynixos-gen-42",
            "hardware_profile": {"cpu_cores": 16, "memory_bytes": 1024, "storage_bytes": 1024},
            "installed_capabilities": ["cerynix-base"]
        }
        requests.post("http://127.0.0.1:8080/api/v1/enroll", json=enroll_payload)
        requests.patch(f"http://127.0.0.1:8080/api/v1/devices/{device_id}", json={"group_id": group_id}, headers=headers)
        # Verify enrollment is active
        requests.patch(f"http://127.0.0.1:8080/api/v1/devices/{device_id}", json={"enrollment_state": "active"}, headers=headers)

        # 3. Create Campaign
        campaign_id = "camp_test_rollout"
        payload_camp = {
            "campaign_id": campaign_id,
            "release_id": release_id,
            "name": "Pilot Rollout for Gen 50 100%",
            "target_group_ids": [group_id],
            "rollout_percentage": 100
        }
        res_camp = requests.post("http://127.0.0.1:8080/api/v1/updates/campaigns", json=payload_camp, headers=headers)
        self.assertEqual(res_camp.status_code, 201)
        self.assertEqual(res_camp.json()["campaign_id"], campaign_id)

        # 4. Device Update Check
        res_check = requests.get(f"http://127.0.0.1:8080/api/v1/devices/{device_id}/updates/check")
        self.assertEqual(res_check.status_code, 200)
        self.assertTrue(res_check.json()["update_available"])
        self.assertEqual(res_check.json()["version"], "cerynixos-gen-50")
        self.assertEqual(res_check.json()["force_rollback"], False)

        # 5. Staged Rollout percentage check (rollout_percentage = 0 should block check)
        campaign_id_0 = "camp_staged_rollout_0"
        payload_camp_0 = {
            "campaign_id": campaign_id_0,
            "release_id": release_id,
            "name": "Staged rollout 0%",
            "target_group_ids": [group_id],
            "rollout_percentage": 0
        }
        requests.post("http://127.0.0.1:8080/api/v1/updates/campaigns", json=payload_camp_0, headers=headers)
        
        # Pause the first campaign so the 0% one gets evaluated
        requests.post(f"http://127.0.0.1:8080/api/v1/updates/campaigns/{campaign_id}/pause", headers=headers)
        
        res_check_gated = requests.get(f"http://127.0.0.1:8080/api/v1/devices/{device_id}/updates/check")
        self.assertEqual(res_check_gated.status_code, 200)
        self.assertFalse(res_check_gated.json()["update_available"])
        message = res_check_gated.json().get("message", "")
        self.assertTrue("gated" in message or "not selected" in message or "rollout" in message)
        
        # Resume the first campaign and pause the 0% one
        requests.post(f"http://127.0.0.1:8080/api/v1/updates/campaigns/{campaign_id}/resume", headers=headers)
        requests.post(f"http://127.0.0.1:8080/api/v1/updates/campaigns/{campaign_id_0}/pause", headers=headers)

        # 6. Status Progress Reporting
        res_report1 = requests.post(f"http://127.0.0.1:8080/api/v1/devices/{device_id}/updates/status", json={"campaign_id": campaign_id, "status": "applying"})
        self.assertEqual(res_report1.status_code, 200)
        self.assertEqual(res_report1.json()["target"]["status"], "applying")

        # Report Verified (Success) -> should trigger device os_version promotion
        res_report2 = requests.post(f"http://127.0.0.1:8080/api/v1/devices/{device_id}/updates/status", json={"campaign_id": campaign_id, "status": "verified"})
        self.assertEqual(res_report2.status_code, 200)
        self.assertEqual(res_report2.json()["target"]["status"], "verified")

        # Query device and check version is now cerynixos-gen-50
        res_dev = requests.get(f"http://127.0.0.1:8080/api/v1/devices/{device_id}", headers=headers)
        self.assertEqual(res_dev.json()["os_version"], "cerynixos-gen-50")

        # 7. Pause & Rollback Controls
        # Set a rollback directive on the campaign
        res_rb = requests.post(f"http://127.0.0.1:8080/api/v1/updates/campaigns/{campaign_id}/rollback", headers=headers)
        self.assertEqual(res_rb.status_code, 200)
        self.assertEqual(res_rb.json()["status"], "rolled_back")

        # Check for update after rollback -> should yield force_rollback: True
        res_check_rb = requests.get(f"http://127.0.0.1:8080/api/v1/devices/{device_id}/updates/check")
        self.assertEqual(res_check_rb.status_code, 200)
        self.assertTrue(res_check_rb.json()["update_available"])
        self.assertTrue(res_check_rb.json()["force_rollback"])

        # 8. Compliance Dashboard Metrics
        res_comp = requests.get("http://127.0.0.1:8080/api/v1/updates/compliance", headers=headers)
        self.assertEqual(res_comp.status_code, 200)
        self.assertIn("compliance_score", res_comp.json())
        self.assertIn("version_breakdown", res_comp.json())

    def test_audit_governance_compliance(self):
        """Verify audit log ingestion, cryptographic validation check, posture aggregation, and reports evidence exports."""
        headers = {"Authorization": "Bearer token_cerynix_secret_key_2026"}

        # Enroll a device to register its identity
        res_t = requests.post("http://127.0.0.1:8080/api/v1/enrollment-tokens", json={"organization_id": "org_test", "max_uses": 5}, headers=headers)
        token = res_t.json()["token"]
        
        device_id = "dev-gov-test-device"
        enroll_payload = {
            "enrollment_token": token,
            "device_id": device_id,
            "device_model": "System76 Oryx Pro",
            "os_version": "cerynixos-gen-42",
            "hardware_profile": {"cpu_cores": 8, "memory_bytes": 1024, "storage_bytes": 1024},
            "installed_capabilities": ["cerynix-base"]
        }
        requests.post("http://127.0.0.1:8080/api/v1/enroll", json=enroll_payload)
        requests.patch(f"http://127.0.0.1:8080/api/v1/devices/{device_id}", json={"enrollment_state": "active"}, headers=headers)

        # 1. Audit Ingestion
        payload_audit = {
            "event_id": "evt_test_ingest_1",
            "timestamp": "2026-06-30T12:00:00Z",
            "service": "execution_broker",
            "action": "ran_tool",
            "status": "success",
            "details": {"command": "systemctl restart cerynix"}
        }
        res_ingest = requests.post(f"http://127.0.0.1:8080/api/v1/devices/{device_id}/audit/ingest", json=payload_audit)
        self.assertEqual(res_ingest.status_code, 201)
        self.assertEqual(res_ingest.json()["event_id"], "evt_test_ingest_1")
        self.assertIn("tamper_hash", res_ingest.json())

        # Ingest a second event to form a chain link
        payload_audit_2 = {
            "event_id": "evt_test_ingest_2",
            "timestamp": "2026-06-30T12:01:00Z",
            "service": "execution_broker",
            "action": "ran_tool",
            "status": "denied_by_policy",
            "details": {"command": "rm -rf /"}
        }
        res_ingest_2 = requests.post(f"http://127.0.0.1:8080/api/v1/devices/{device_id}/audit/ingest", json=payload_audit_2)
        self.assertEqual(res_ingest_2.status_code, 201)
        self.assertEqual(res_ingest_2.json()["previous_hash"], res_ingest.json()["tamper_hash"])

        # 2. Cryptographic Validation Chain
        res_verify = requests.post("http://127.0.0.1:8080/api/v1/audit/verify", headers=headers)
        self.assertEqual(res_verify.status_code, 200)
        self.assertEqual(res_verify.json()["status"], "valid")

        # 3. Simulate Tampering check by manually altering the DB record
        with get_db_connection() as conn:
            conn.execute("UPDATE audit_events SET action = 'hacked_action' WHERE event_id = 'evt_test_ingest_1';")

        # Chain verification should now report tampered/broken chain
        res_verify_tampered = requests.post("http://127.0.0.1:8080/api/v1/audit/verify", headers=headers)
        self.assertEqual(res_verify_tampered.status_code, 200)
        self.assertEqual(res_verify_tampered.json()["status"], "tampered")

        # 4. Compliance Posture Summaries
        res_posture = requests.get("http://127.0.0.1:8080/api/v1/compliance/posture", headers=headers)
        self.assertEqual(res_posture.status_code, 200)
        self.assertIn("compliance_score", res_posture.json())
        self.assertIn("non_compliant_count", res_posture.json())

        # 5. Export Evidence
        for report in ["inventory", "updates", "policies", "audit"]:
            res_exp = requests.get(f"http://127.0.0.1:8080/api/v1/compliance/export/{report}", headers=headers)
            self.assertEqual(res_exp.status_code, 200)
            self.assertTrue(isinstance(res_exp.json(), list))

    def test_observability_health_diagnostics(self):
        """Verify health snapshots ingestion, fleet status overview, active alert rules evaluation, support bundles, incidents CRUD, and Remote diagnostics commands execution."""
        headers = {"Authorization": "Bearer token_cerynix_secret_key_2026"}

        # Enroll a device
        res_t = requests.post("http://127.0.0.1:8080/api/v1/enrollment-tokens", json={"organization_id": "org_test", "max_uses": 5}, headers=headers)
        token = res_t.json()["token"]
        
        device_id = "dev-obs-test-device"
        enroll_payload = {
            "enrollment_token": token,
            "device_id": device_id,
            "device_model": "Framework Laptop 16",
            "os_version": "cerynixos-gen-42",
            "hardware_profile": {"cpu_cores": 8, "memory_bytes": 1024, "storage_bytes": 1024},
            "installed_capabilities": ["cerynix-base"]
        }
        requests.post("http://127.0.0.1:8080/api/v1/enroll", json=enroll_payload)
        requests.patch(f"http://127.0.0.1:8080/api/v1/devices/{device_id}", json={"enrollment_state": "active"}, headers=headers)

        # 1. Ingest health snapshot
        payload_health = {
            "snapshot_id": "snap_test_1",
            "timestamp": "2026-06-30T05:00:00Z",
            "health_score": 85,
            "components": {
                "cpu": "healthy",
                "memory": "healthy",
                "storage": "healthy",
                "services": "degraded"
            }
        }
        res_health = requests.post(f"http://127.0.0.1:8080/api/v1/devices/{device_id}/health/ingest", json=payload_health)
        self.assertEqual(res_health.status_code, 201)
        self.assertEqual(res_health.json()["health_score"], 85)

        # 2. Fleet health overview
        res_fleet = requests.get("http://127.0.0.1:8080/api/v1/observability/fleet", headers=headers)
        self.assertEqual(res_fleet.status_code, 200)
        self.assertEqual(res_fleet.json()["total_active_devices"], 1)
        self.assertEqual(res_fleet.json()["healthy_count"], 1)

        # 3. Dynamic alerts
        res_alerts = requests.get("http://127.0.0.1:8080/api/v1/observability/alerts", headers=headers)
        self.assertEqual(res_alerts.status_code, 200)
        alerts = res_alerts.json()
        # Should contain degraded alert for services
        alert_types = [a["alert_type"] for a in alerts]
        self.assertIn("resource_services_degraded", alert_types)

        # 4. Ingest support bundle metadata
        payload_bundle = {
            "bundle_id": "bundle-uuid-1234",
            "timestamp": "2026-06-30T13:10:00Z",
            "bundle_size_bytes": 50000,
            "bundle_url": "https://storage.cerynix.internal/bundles/framework-1234.tar.gz",
            "trigger_reason": "operator_request",
            "redaction_applied": True,
            "metadata": {"kernel": "6.1.0-nix"}
        }
        res_bundle = requests.post(f"http://127.0.0.1:8080/api/v1/devices/{device_id}/support-bundles", json=payload_bundle)
        self.assertEqual(res_bundle.status_code, 201)
        self.assertEqual(res_bundle.json()["bundle_id"], "bundle-uuid-1234")

        # 5. Incident CRUD
        incident_id = "inc_test_1"
        payload_inc = {
            "incident_id": incident_id,
            "device_id": device_id,
            "title": "Services degraded alert ticket",
            "description": "System services reported degraded on diagnostics snapshot.",
            "severity": "high"
        }
        res_inc = requests.post("http://127.0.0.1:8080/api/v1/support/incidents", json=payload_inc, headers=headers)
        self.assertEqual(res_inc.status_code, 201)
        self.assertEqual(res_inc.json()["status"], "open")

        # Update note
        res_inc_up = requests.patch(
            f"http://127.0.0.1:8080/api/v1/support/incidents/{incident_id}", 
            json={"status": "investigating", "operator_note": "Assigned to engineer."}, 
            headers=headers
        )
        self.assertEqual(res_inc_up.status_code, 200)
        self.assertEqual(res_inc_up.json()["status"], "investigating")
        self.assertEqual(len(res_inc_up.json()["operator_notes"]), 1)

        # 6. Diagnostics Remote Execution Pipeline
        command_id = "cmd_diag_1"
        payload_exec = {
            "command_id": command_id,
            "command": "systemctl status cerynix-base",
            "arguments": ["--no-pager"]
        }
        res_exec = requests.post(f"http://127.0.0.1:8080/api/v1/devices/{device_id}/diagnostics/execute", json=payload_exec, headers=headers)
        self.assertEqual(res_exec.status_code, 201)
        self.assertEqual(res_exec.json()["status"], "pending")

        # Poll pending command from device side
        res_poll = requests.get(f"http://127.0.0.1:8080/api/v1/devices/{device_id}/diagnostics/pending")
        self.assertEqual(res_poll.status_code, 200)
        self.assertEqual(res_poll.json()["command_id"], command_id)
        self.assertEqual(res_poll.json()["status"], "running")

        # Submit execution results
        res_results = requests.post(
            f"http://127.0.0.1:8080/api/v1/devices/{device_id}/diagnostics/results", 
            json={"command_id": command_id, "status": "completed", "output": "cerynix-base.service is running"}
        )
        self.assertEqual(res_results.status_code, 200)
        self.assertEqual(res_results.json()["status"], "completed")
        self.assertEqual(res_results.json()["output"], "cerynix-base.service is running")

        # Get diagnostic commands history
        res_history = requests.get(f"http://127.0.0.1:8080/api/v1/devices/{device_id}/diagnostics/commands", headers=headers)
        self.assertEqual(res_history.status_code, 200)
        self.assertEqual(len(res_history.json()), 1)

        # 7. Device Timeline View
        res_time = requests.get(f"http://127.0.0.1:8080/api/v1/devices/{device_id}/timeline", headers=headers)
        self.assertEqual(res_time.status_code, 200)
        self.assertTrue(len(res_time.json()) > 0)
        
        # 8. Synthetic Failure Simulation
        res_sim = requests.post(f"http://127.0.0.1:8080/api/v1/devices/{device_id}/simulate-failure", json={"failure_type": "cpu_spike"}, headers=headers)
        self.assertEqual(res_sim.status_code, 200)
        self.assertEqual(res_sim.json()["cpu"], "critical")
        self.assertEqual(res_sim.json()["health_score"], 45)

        # 9. Unhealthy Device Workflow queue filter
        res_unhealthy = requests.get("http://127.0.0.1:8080/api/v1/support/unhealthy", headers=headers)
        self.assertEqual(res_unhealthy.status_code, 200)
        self.assertTrue(len(res_unhealthy.json()) > 0)

    def test_artifact_registry(self):
        """Verify artifact metadata upload registration, catalog listing, version approvals, and secure download URL signing calculations."""
        headers = {"Authorization": "Bearer token_cerynix_secret_key_2026"}

        # 1. Register artifact metadata (starts as pending)
        payload_art_bad = {
            "artifact_id": "plugin-test-plugin-bad",
            "name": "cerynix-plugin-test",
            "type": "plugin",
            "version": "1.2.3",
            "filename": "plugin-test.tar.gz",
            "file_size_bytes": 15000,
            "checksum_sha256": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f61234",
            "download_url": "https://storage.cerynix.internal/registry/plugins/plugin-test.tar.gz",
            "signature": "invalid_sig_format"
        }
        res_reg_bad = requests.post("http://127.0.0.1:8080/api/v1/registry/artifacts", json=payload_art_bad, headers=headers)
        self.assertEqual(res_reg_bad.status_code, 400)

        payload_art = {
            "artifact_id": "plugin-test-plugin",
            "name": "cerynix-plugin-test",
            "type": "plugin",
            "version": "1.2.3",
            "description": "Integration test plugin payload.",
            "filename": "plugin-test.tar.gz",
            "file_size_bytes": 15000,
            "checksum_sha256": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f61234",
            "download_url": "https://storage.cerynix.internal/registry/plugins/plugin-test.tar.gz",
            "signature": "dev_signature_test_2026"
        }
        res_reg = requests.post("http://127.0.0.1:8080/api/v1/registry/artifacts", json=payload_art, headers=headers)
        self.assertEqual(res_reg.status_code, 201)
        self.assertEqual(res_reg.json()["approval_status"], "pending")

        # 2. Get catalog (should be empty because it is pending approval)
        res_cat = requests.get("http://127.0.0.1:8080/api/v1/registry/catalog")
        self.assertEqual(res_cat.status_code, 200)
        self.assertEqual(len(res_cat.json()), 0)

        # 3. Attempt download URL signing for unapproved artifact (should fail with 403)
        res_dl_fail = requests.get("http://127.0.0.1:8080/api/v1/registry/artifacts/plugin-test-plugin/download")
        self.assertEqual(res_dl_fail.status_code, 403)

        # 4. Approve version catalog promotion
        res_app = requests.patch("http://127.0.0.1:8080/api/v1/registry/artifacts/plugin-test-plugin/approve", json={"status": "approved"}, headers=headers)
        self.assertEqual(res_app.status_code, 200)
        self.assertEqual(res_app.json()["approval_status"], "approved")

        # 5. Fetch catalog (should now return 1 item)
        res_cat_ok = requests.get("http://127.0.0.1:8080/api/v1/registry/catalog")
        self.assertEqual(res_cat_ok.status_code, 200)
        self.assertEqual(len(res_cat_ok.json()), 1)
        self.assertEqual(res_cat_ok.json()[0]["artifact_id"], "plugin-test-plugin")

        # 6. Retrieve signed download URL successfully (should contain signature and expires params)
        res_dl_ok = requests.get("http://127.0.0.1:8080/api/v1/registry/artifacts/plugin-test-plugin/download?expires=300")
        self.assertEqual(res_dl_ok.status_code, 200)
        signed_url = res_dl_ok.json()["signed_url"]
        self.assertIn("expires=", signed_url)
        self.assertIn("signature=", signed_url)

        # Validate signed URL manually using verify_signed_url helper
        from services.registry import verify_signed_url
        import urllib.parse
        parsed = urllib.parse.urlparse(signed_url)
        params = urllib.parse.parse_qs(parsed.query)
        expires_val = int(params["expires"][0])
        sig_val = params["signature"][0]
        self.assertTrue(verify_signed_url("plugin-test-plugin", expires_val, sig_val))

if __name__ == "__main__":
    unittest.main()
