# Milestone 2: Control Plane, Fleet Management, and Enterprise Operations

## Purpose
This milestone covers the enterprise backend and operational layer: fleet enrollment, policy distribution, device inventory, updates orchestration, audit, compliance posture, registry foundations, and support operations.

## Owner Model
* Primary owner: Avishek
* Work style: Independent delivery with mocked device-plane clients and synthetic device data
* External dependency rule: Do not block on Milestone 1; use emulator agents, fake health reports, and fixture audit events

## Tracking Legend
* `[ ]` Not started
* `[~]` In progress
* `[x]` Completed

## Done Definition
* A small fleet can be enrolled, managed, observed, and updated
* Policy and audit flows are functional with verifiable records
* Support and compliance basics exist for enterprise pilot review
* Backend interfaces are stable enough for real device integration later

---

## Phase 0: Milestone Setup and Contracts
* [x] Define Milestone 2 scope boundaries and non-goals
* [x] Review Milestone 1 tech_debt.md to map required backend APIs
* [x] Create control-plane architecture diagram
* [x] Define service boundary map for backend components
* [x] Freeze v1 API contracts for:
* [x] Enrollment
* [x] Device inventory
* [x] Policy distribution
* [x] Health ingestion
* [x] Audit ingestion
* [x] Update metadata publishing
* [x] Support bundle registration
* [x] Create mock device simulator and synthetic data generator
* [x] Define local development topology for all backend services
* [x] Establish repo conventions for backend modules, schemas, and API versioning

## Phase 1: Core Backend Foundation
* [x] Select service architecture pattern for v1 backend
* [x] Set up backend project structure
* [x] Set up configuration and secret management approach
* [x] Set up local database stack
* [x] Set up queue or async job processing pattern if needed
* [x] Add API gateway or edge routing foundation
* [x] Add auth middleware scaffolding
* [x] Add structured logging and trace correlation
* [x] Add health checks and readiness endpoints
* [x] Add migration workflow and seed data tooling

## Phase 2: Fleet Enrollment and Device Inventory
* [x] Design enrollment flow for first enterprise pilot
* [x] Implement enrollment token issuance
* [x] Implement device registration endpoint
* [x] Implement device identity record model
* [x] Implement inventory attributes:
* [x] Device model
* [x] OS version
* [x] Hardware profile
* [x] Installed capabilities
* [x] Enrollment state
* [x] Implement device grouping and tagging
* [x] Implement device search and filtering
* [x] Build simulated fleet seeding tools
* [x] Validate fleet lifecycle transitions:
* [x] Enrolled
* [x] Active
* [x] Quarantined
* [x] Retired

## Phase 3: Policy Engine and Configuration Delivery
* [x] Define policy object schema
* [x] Define policy precedence rules
* [x] Define policy scopes:
* [x] Global
* [x] Group
* [x] Device
* [x] Implement policy CRUD APIs
* [x] Implement policy versioning
* [x] Implement policy publication workflow
* [x] Implement device policy resolution endpoint
* [x] Add policy dry-run and validation mode
* [x] Add policy rollback support
* [x] Add policy audit trail
* [x] Create fixture policies for mocked device testing

## Phase 4: Update Orchestration and Release Channels
* [ ] Define release channel model:
* [ ] Canary
* [ ] Pilot
* [ ] Broad
* [ ] Critical
* [ ] Define update metadata schema
* [ ] Implement release record management
* [ ] Implement update assignment rules by group/channel
* [ ] Implement staged rollout controls
* [ ] Implement pause and rollback controls
* [ ] Implement update campaign status tracking
* [ ] Add update compliance dashboard data model
* [ ] Test campaigns using simulated device clients

## Phase 5: Audit, Compliance, and Governance
* [ ] Define audit event taxonomy
* [ ] Implement audit ingestion endpoint
* [ ] Implement tamper-evident audit storage approach
* [ ] Implement privileged action reporting views
* [ ] Define compliance baseline controls for pilot
* [ ] Implement compliance posture aggregation
* [ ] Implement evidence export for:
* [ ] Device inventory
* [ ] Update status
* [ ] Policy state
* [ ] Audit history
* [ ] Add redaction and retention configuration
* [ ] Write governance notes for enterprise review

## Phase 6: Observability, Health, and Support Operations
* [ ] Define health report schema
* [ ] Implement health ingestion endpoint
* [ ] Implement per-device health scoring
* [ ] Implement fleet health overview
* [ ] Implement alert rules for pilot scale
* [ ] Implement support bundle registration and retrieval metadata
* [ ] Implement device timeline view
* [ ] Implement incident notes or operator annotation support
* [ ] Add support workflow filters for unhealthy devices
* [ ] Add synthetic failure scenarios for operational testing

## Phase 7: Artifact, Model, and Plugin Registry Foundations
* [ ] Define registry scope for system artifacts, models, and plugins
* [ ] Define artifact metadata schema
* [ ] Implement signed artifact metadata storage
* [ ] Implement approved version catalog
* [ ] Implement artifact publishing workflow
* [ ] Implement artifact deprecation workflow
* [ ] Implement registry lookup API
* [ ] Add placeholder signature verification workflow
* [ ] Seed registry with fake and test artifacts for integration

## Phase 8: Admin Experience and Enterprise UX
* [ ] Define primary operator personas
* [ ] Design admin information architecture
* [ ] Build admin dashboard shell
* [ ] Build device inventory screens
* [ ] Build policy management screens
* [ ] Build update campaign screens
* [ ] Build audit and compliance views
* [ ] Build support diagnostics views
* [ ] Add role-aware UI gating placeholders
* [ ] Validate UI against core pilot workflows

## Phase 9: Security and Identity Foundations
* [ ] Define admin auth strategy for v1
* [ ] Add role-based access control foundation
* [ ] Define service-to-service auth pattern
* [ ] Add secret rotation procedure
* [ ] Define device certificate lifecycle placeholder model
* [ ] Add backend hardening checklist
* [ ] Add security event logging
* [ ] Review exposed endpoints for abuse and over-permission
* [ ] Document future SSO and TPM-backed identity extension path

## Phase 10: SRE, Release Operations, and Pilot Readiness
* [ ] Define SLOs for critical backend services
* [ ] Define error budgets and alert thresholds
* [ ] Write runbooks for:
* [ ] Enrollment failure
* [ ] Policy publication failure
* [ ] Update campaign failure
* [ ] Audit pipeline degradation
* [ ] Database capacity issue
* [ ] Define backup and restore procedure
* [ ] Define staging-to-production promotion checklist
* [ ] Define pilot customer onboarding checklist
* [ ] Run disaster recovery tabletop exercise
* [ ] Create milestone readiness review deck

## Phase 11: Quality, Testing, and Milestone Exit
* [ ] Create API contract test suite
* [ ] Create synthetic fleet integration test suite
* [ ] Run policy resolution correctness tests
* [ ] Run staged rollout simulation tests
* [ ] Run audit retention and export tests
* [ ] Run admin permission boundary tests
* [ ] Freeze milestone scope
* [ ] Publish Milestone 2 operator guide
* [ ] Document open issues, technical debt, and integration notes for Milestone 1 convergence

---

## Parallelization Notes
* Milestone 2 should not wait for real devices
* Every device interaction must be testable with emulators or fixture payloads
* API contracts should be versioned and mockable from day one
* Backend rollout logic should be validated with synthetic fleets before endpoint integration

## Milestone Exit Deliverables
* [ ] Fleet enrollment service
* [ ] Device inventory and grouping
* [ ] Policy engine v1
* [ ] Update orchestration v1
* [ ] Audit and compliance baseline
* [ ] Fleet health and support operations views
* [ ] Artifact/model/plugin registry foundation
* [ ] Admin console v1
* [ ] SRE runbooks and pilot readiness package
* [ ] Milestone validation report
