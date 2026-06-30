# Changelog

## 2026-06-30
### Feature: Core Backend Foundation (Milestone 2, Phase 1)
- **Added:** Initialized the fleet control plane codebase.
- **Added:** Implemented `FastAPI` application entry point in [main.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS-main/control-plane/src/main.py) with request logging and correlation tracing.
- **Added:** Created SQLite database connection contexts in [connection.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS-main/control-plane/src/database/connection.py) with WAL mode enabled.
- **Added:** Defined 11 SQL tables in [schema.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS-main/control-plane/src/database/schema.py) implementing automatic schema initialization on startup.
- **Added:** Implemented auth scaffolding verifying API tokens in [auth.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS-main/control-plane/src/services/auth.py).
- **Added:** Created health and readiness endpoints in [health.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS-main/control-plane/src/routes/health.py).
- **Migration Impact:** Schema is automatically generated inside `control-plane/db/control_plane.db` on server startup.
- **API Impact:** Exposes `/api/v1/health` and `/api/v1/readiness` on port `8000`.

## 2026-06-30
### Feature: Fleet Enrollment and Device Inventory (Milestone 2, Phase 2)
- **Added:** Implemented enrollment token services in [enrollment.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS-main/control-plane/src/services/enrollment.py).
- **Added:** Implemented device and group database query services in [inventory.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS-main/control-plane/src/services/inventory.py) supporting state transitions, tagging, and group assignments.
- **Added:** Implemented `/api/v1/enrollment-tokens` and public onboarding `/api/v1/enroll` endpoints in [enrollment.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS-main/control-plane/src/routes/enrollment.py).
- **Added:** Implemented device query filtering and PATCH lifecycle update routes in [devices.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS-main/control-plane/src/routes/devices.py).
- **Added:** Created [fleet_seeder.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS-main/control-plane/simulator/fleet_seeder.py) to seed initial tokens, groups, and device models.
- **Migration Impact:** Modified `devices` table schema in [schema.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS-main/control-plane/src/database/schema.py) to support `tags` and `installed_capabilities`.
- **API Impact:** Exposes `/api/v1/enroll`, `/api/v1/enrollment-tokens`, `/api/v1/devices`, and `/api/v1/device-groups`.

## 2026-06-30
### Feature: Policy Engine and Configuration Delivery (Milestone 2, Phase 3)
- **Added:** Implemented policy CRUD, revisions, rollback, and resolution logic in [policy.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS-main/control-plane/src/services/policy.py).
- **Added:** Implemented policies routes, assignments, and device resolution endpoints in [policies.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS-main/control-plane/src/routes/policies.py).
- **Added:** Updated [fleet_seeder.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS-main/control-plane/simulator/fleet_seeder.py) to seed policy configuration fixtures and assignments.
- **Migration Impact:** Added `policy_revisions` table schema to [schema.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS-main/control-plane/src/database/schema.py) to support history tracking and rollbacks.
- **API Impact:** Exposes `/api/v1/policies`, `/api/v1/policies/dry-run`, `/api/v1/policies/{policy_id}/assign`, `/api/v1/policies/{policy_id}/rollback`, `/api/v1/policies/{policy_id}/revisions`, and `/api/v1/devices/{device_id}/policy`.


