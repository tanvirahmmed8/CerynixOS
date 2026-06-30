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

## 2026-06-30
### Feature: Update Orchestration and Release Channels (Milestone 2, Phase 4)
- **Added:** Implemented update metadata management, campaigns setup, stateless staged rollouts, and compliance dashboard metrics calculation in [update.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/control-plane/src/services/update.py).
- **Added:** Created HTTP routes for releases, campaigns management, campaign status controls (pause, resume, rollback), and client-facing update-check and reporting in [updates.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/control-plane/src/routes/updates.py).
- **Added:** Extended [fleet_seeder.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/control-plane/simulator/fleet_seeder.py) to seed group release channels and update campaigns fixtures.
- **Migration Impact:** Updated schema definitions in [schema.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/control-plane/src/database/schema.py) to add a `release_channel` column on `device_groups` with check constraints and automatic table migration run block on server start.
- **API Impact:** Exposes `/api/v1/updates/releases`, `/api/v1/updates/campaigns`, `/api/v1/updates/compliance`, `/api/v1/devices/{device_id}/updates/check`, and `/api/v1/devices/{device_id}/updates/status`.

## 2026-06-30
### Feature: Audit, Compliance, and Governance (Milestone 2, Phase 5)
- **Added:** Implemented cryptographically chained tamper-evident audit log ledger checks and validation crawler in [governance.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/control-plane/src/services/governance.py).
- **Added:** Implemented sensitivity parameters redaction and database logs retention days pruning in `ingest_audit_event()`.
- **Added:** Created routes for audit logging, verification checks, and baseline posture aggregate stats in [governance.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/control-plane/src/routes/governance.py).
- **Added:** Implemented structured evidence exports for fleet inventory, rollout campaigns, policy targets, and audit ledger.
- **Migration Impact:** Added `previous_hash` and `tamper_hash` columns to the `audit_events` table with automatic sqlite schemas migrations.
- **API Impact:** Exposes `/api/v1/devices/{device_id}/audit/ingest`, `/api/v1/audit`, `/api/v1/audit/verify`, `/api/v1/compliance/posture`, and `/api/v1/compliance/export/{report_type}`.

## 2026-06-30
### Feature: Observability, Health, and Support Operations (Milestone 2, Phase 6)
- **Added:** Implemented health snapshots ingestion, fleet health aggregator overview metrics, and dynamic heartbeats/degradation alert evaluation rules in [observability.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/control-plane/src/services/observability.py).
- **Added:** Implemented operator support incident ticket logs, annotations/notes logger, and support bundles manifests registration.
- **Added:** Implemented diagnostics terminal remote execute queue (enqueueing, pulling, execution results reporting).
- **Added:** Added device chronological timeline aggregation, support workflow filters for unhealthy devices, and synthetic failure scenarios.
- **Added:** Exposed device and admin routes in [observability.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/control-plane/src/routes/observability.py).
- **Migration Impact:** Initialized `incidents` and `diagnostic_commands` schemas and registered tables order in [schema.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/control-plane/src/database/schema.py).
- **API Impact:** Exposes endpoints for `/health/ingest`, `/support-bundles`, `/diagnostics/pending`, `/diagnostics/results`, `/diagnostics/execute`, `/diagnostics/commands`, `/timeline`, `/simulate-failure`, `/observability/fleet`, `/observability/alerts`, and `/support/incidents`.

## 2026-06-30
### Feature: Artifact, Model, and Plugin Registry Foundations (Milestone 2, Phase 7)
- **Added:** Implemented metadata registry database schema in [schema.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/control-plane/src/database/schema.py).
- **Added:** Created JSON schema contract for registry metadata validation in [registry-metadata.json](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/contracts/registry-metadata.json).
- **Added:** Implemented services for registration publishing, version catalog approvals (approved, rejected, deprecated), catalog listings, and simulated SHA256 HMAC-signed downloads tokens generator in [registry.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/control-plane/src/services/registry.py).
- **Added:** Implemented HTTP routes for registry metadata uploads, version promotions, catalog queries, and download signed URLs in [registry.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/control-plane/src/routes/registry.py).
- **Added:** Formulated developer guidelines detailing metadata packaging, signature checks, and lookup flows in [registry-guidelines.md](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/docs/registry-guidelines.md).
- **Added:** Extended [fleet_seeder.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/control-plane/simulator/fleet_seeder.py) to seed default GGUF AI models and system binaries.
- **Migration Impact:** Initialized `registry_artifacts` table with automatic sqlite database tables migration.
- **API Impact:** Exposes `/api/v1/registry/artifacts`, `/api/v1/registry/artifacts/{artifact_id}/approve`, `/api/v1/registry/catalog`, and `/api/v1/registry/artifacts/{artifact_id}/download`.

## 2026-06-30
### Feature: Admin Experience and Enterprise UX (Milestone 2, Phase 8)
- **Added:** Defined three primary enterprise operator personas (SRE Platform Architect, Helpdesk Support Engineer, Compliance Auditor) in [personas.md](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/docs/personas.md).
- **Added:** Mounted `StaticFiles` in [main.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/control-plane/src/main.py) serving a full admin dashboard SPA at the root path `/`.
- **Added:** Built premium, dark-mode SPA dashboard shell in [index.html](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/control-plane/static/index.html) covering six operator workspaces: Overview, Inventory, Policies, Campaigns, Governance, and Diagnostics.
- **Added:** Created comprehensive CSS design system in [styles.css](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/control-plane/static/styles.css) using glassmorphism, dark mode color tokens, terminal shell themes, and micro-animations.
- **Added:** Implemented full frontend controller in [app.js](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/control-plane/static/app.js) integrating bearer token auth gating, live alerts polling, inventory filtering, policy CRUD, campaign controls (pause/resume/rollback), cryptographic ledger verification UI, support incident tickets CRM, and remote diagnostics terminal.
- **UI Impact:** Dashboard accessible at `http://127.0.0.1:8000/`.
## 2026-06-30
### Feature: Security and Identity Foundations (Milestone 2, Phase 9)
- **Added:** Expanded [auth.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/control-plane/src/services/auth.py) with full RBAC model (`ROLES`, `PERMISSIONS`), `get_role_for_token()`, `require_role()` dependency factory, and `log_security_event()` structured security emitter.
- **Added:** `SecurityHeadersMiddleware` in [main.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/control-plane/src/main.py) — sets `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `X-XSS-Protection`, `Content-Security-Policy`, and `Permissions-Policy` on every response.
- **Added:** `RateLimitMiddleware` in [main.py](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/control-plane/src/main.py) — in-memory per-IP sliding window (120 req/60s). Rate limit breaches logged as `suspicious_activity` security events. Static files exempt.
- **Added:** [s2s_auth.md](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/docs/s2s_auth.md) — v1 static token device-agent auth pattern and v2 JWT certificate upgrade path.
- **Added:** [secret-rotation.md](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/docs/secret-rotation.md) — step-by-step `api_token` and `SIGNING_SECRET_KEY` rotation procedures.
- **Added:** [device-cert-lifecycle.md](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/docs/device-cert-lifecycle.md) — placeholder model for device certificate provisioning, renewal, and revocation with TPM extension points.
- **Added:** [hardening-checklist.md](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/docs/hardening-checklist.md) — 10-category production hardening checklist (auth, RBAC, input validation, headers, rate limiting, error exposure, logging, secrets, dependencies, CORS).
- **Added:** [endpoint-security-review.md](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/docs/endpoint-security-review.md) — full route table with auth status, risk classification, and 5 priority pre-production action items.
- **Added:** [identity-extension-path.md](file:///c:/Users/mojoa/Downloads/Compressed/CerynixOS/docs/identity-extension-path.md) — 3-stage migration roadmap (static token → OIDC JWT → TPM device certs) with exact code extension points.
- **Security Impact:** Security events (`auth_success`, `auth_failure`, `role_violation`, `suspicious_activity`) now appear in the structured log stream alongside application request logs.
- **No Breaking Changes:** All 11 existing integration tests continue to pass.
