# Milestone 2 Testing Strategy

## 1. API Contract Testing
**Objective:** Ensure all Control Plane endpoints adhere to the OpenAPI schema and JSON contracts defined in Phase 0.
**Strategy:**
- Use `Pact` or `Schemathesis` to automatically fuzz the API endpoints based on their OpenAPI definitions.
- Write Pytest fixtures that mock the database layer and validate that the serialization/deserialization logic strictly enforces the expected shapes for Enrollment, Inventory, and Health payloads.

## 2. Synthetic Fleet Integration
**Objective:** Validate system performance under load.
**Strategy:**
- Deploy a Kubernetes `Job` or `DaemonSet` that spins up 1,000 lightweight Python containers, each mimicking a CerynixOS device.
- These synthetic devices will concurrently execute the TPM enrollment flow and begin streaming random Health metrics and Audit events at 1 Hz.
- Assert that the backend API maintains P99 latency < 200ms during this synthetic event storm.

## 3. Policy Resolution Correctness
**Objective:** Ensure conflicting policies merge correctly based on weight/hierarchy.
**Strategy:**
- **Test Case:** Assign a Global policy (Weight 10, Allow USB: False) and an Engineering Team policy (Weight 50, Allow USB: True) to a mock device.
- **Assertion:** The resulting computed policy sent to the device must resolve to `Allow USB: True` because the team policy has a higher weight.

## 4. Staged Rollout Simulation
**Objective:** Validate the canary release engine for OTA updates.
**Strategy:**
- Mock a fleet of 100 devices.
- Define a 10% canary update campaign.
- Assert that exactly 10 devices receive the new update metadata, while 90 devices continue to receive the old baseline.
- Simulate an update failure on 2 of the 10 canary devices. Assert that the rollout campaign automatically pauses and alerts the Admin.

## 5. Admin RBAC Boundary Testing
**Objective:** Prevent privilege escalation in the Control Plane.
**Strategy:**
- Create mock users with roles: `SuperAdmin`, `Auditor`, `PolicyAdmin`.
- Assert that `Auditor` receives an HTTP 403 Forbidden when attempting a POST request to `/api/v1/policies`.
- Assert that `PolicyAdmin` receives HTTP 403 when attempting to delete audit logs.
