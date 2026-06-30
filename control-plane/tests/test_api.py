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

if __name__ == "__main__":
    unittest.main()
