# Milestone 2: Scope Boundaries

This document defines the in-scope deliverables and out-of-scope boundaries (non-goals) for **Milestone 2: Control Plane, Fleet Management, and Enterprise Operations**.

## In Scope

Milestone 2 focuses on delivering the centralized fleet administration and operations backend.

### 1. Fleet Enrollment & Device Inventory
- **Enrollment Service:** API endpoints for validating enrollment tokens, registering devices, and issuing mock client certificates.
- **Identity & Inventory:** Maintaining database records of enrolled devices (hardware specs, OS version, tagging, groups).
- **Lifecycle States:** Tracking and changing device states: `Enrolled` -> `Active` -> `Quarantined` -> `Retired`.

### 2. Policy Engine & Configuration Delivery
- **Policy Schema & Precedence:** Global, Group-level, and Device-specific policy application.
- **APIs:** Policy creation, publishing, dry-runs, and version rollback.
- **Resolution:** A secure endpoint for devices to fetch their resolved policy.

### 3. Update Orchestration
- **Release Channels:** Support for `Canary`, `Pilot`, `Broad`, and `Critical` channels.
- **Campaign Controls:** Staged rollout management, campaigns pause/resume, and rollbacks.
- **Compliance Tracking:** Reporting update status and fleet-wide patch compliance.

### 4. Audit & Compliance
- **Audit Logging:** Centralized log ingestion endpoint for device-plane audit events.
- **Compliance Baselines:** Fleet-wide compliance posture monitoring and evidence exports.

### 5. Observability & Support
- **Health Ingestion:** Receiving and scoring telemetry/health snapshots from devices.
- **Support Workflow:** Incident notes, operator alerts, and support bundle registration/metadata retrieval.

### 6. Artifact, Model & Plugin Registry
- **Registry Catalog:** Cataloging approved OS images, plugins, and AI models.
- **Cryptographic Signatures:** Model metadata verification and publishing flows.

### 7. Operator UX (Admin Console)
- **Web-based Admin Portal:** A modern, premium UI prototype for monitoring fleet health, managing policies, viewing audits, and starting update campaigns.

---

## Out of Scope (Non-Goals)

These items are deferred to future milestones:
- **Physical TPM Attestation:** We will mock/scaffold TPM quote verification. Real hardware attestation validation is out of scope.
- **Production SSO/Identity Providers:** Integrations with Active Directory, Okta, or other OIDC providers are out of scope (scaffolded/role-based local authentication is used).
- **Production-Scale Database Hosting:** High-availability distributed database clustering (e.g., multi-region Postgres/Spanner) is out of scope. A local SQLite or single PostgreSQL DB setup is sufficient.
- **Real OS Image Hosting Infrastructure:** Hosting large OS binaries/payloads on dedicated CDNs is out of scope. The registry will track metadata and hashes, while using mock file URLs for downloads.
- **True Multi-Tenant Billing/Metering:** Commercial SaaS metering is out of scope.
