# Control-Plane Architecture and Service Boundary Map

This document outlines the architecture design and service boundaries of the CerynixOS Fleet Control Plane.

## Architecture Diagram

The control plane sits above the individual device plane instances, offering secure, centralized orchestration, governance, and updates.

```mermaid
flowchart TD
    %% Admin UX Layer
    subgraph UI [Operator Experience]
        Console[Admin Web Console]
    end

    %% Control Plane Core Services (Backend)
    subgraph CP [CerynixOS Fleet Control Plane (Python)]
        Gateway[API Gateway / Router]
        EnrollSvc[Enrollment Service]
        InventorySvc[Inventory & Identity Service]
        PolicySvc[Policy Engine Service]
        UpdateSvc[Update Orchestrator Service]
        AuditSvc[Audit & Compliance Service]
        ObsSvc[Observability & Support Service]
        RegistrySvc[Artifact & Model Registry]
        
        DB[(SQLite DB / Fleet State)]
    end

    %% Device Plane (Endpoints)
    subgraph Device [CerynixOS Device Plane]
        Agent[Cerynix Agent / Updater]
        HealthAgent[Health Telemetry Agent]
        Broker[Action Broker / Audit]
    end

    %% Admin Console Communications
    Console --> |REST API / HTTPS| Gateway

    %% Gateway Routing
    Gateway --> EnrollSvc
    Gateway --> InventorySvc
    Gateway --> PolicySvc
    Gateway --> UpdateSvc
    Gateway --> AuditSvc
    Gateway --> ObsSvc
    Gateway --> RegistrySvc

    %% DB Storage
    EnrollSvc --> DB
    InventorySvc --> DB
    PolicySvc --> DB
    UpdateSvc --> DB
    AuditSvc --> DB
    ObsSvc --> DB
    RegistrySvc --> DB

    %% Device Communications
    Agent --> |Enrollment & Policy Fetch| Gateway
    HealthAgent --> |Health Ingestion| Gateway
    Broker --> |Audit Log Ingestion| Gateway
    Agent --> |Support Bundle & Update Check| Gateway
```

## Service Boundary Map

The control plane consists of the following modular service boundaries:

| Service Name | Purpose / Boundary | Communication Protocols | Key Storage Model (SQLite) |
|---|---|---|---|
| **Enrollment Service** | Validates enrollment tokens, registers initial device hardware profile, and issues certificates/identities. | HTTPS POST (`/api/v1/enroll`) | `enrollment_tokens`, `devices` |
| **Inventory Service** | Manages hardware properties, OS versions, active tag/group assignments, and device lifecycle states. | HTTPS GET/PUT (`/api/v1/devices`) | `devices`, `device_groups` |
| **Policy Service** | Resolves overlapping policies (Global, Group, Device) according to precedence. Handles policy CRUD, dry-runs, and publication. | HTTPS GET (`/api/v1/policy/resolve`) | `policies`, `policy_assignments` |
| **Update Orchestrator** | Manages release channels (Canary, Pilot, Broad, Critical), coordinates updates, tracks staged campaigns, and logs compliance. | HTTPS GET/POST (`/api/v1/updates/*`) | `releases`, `campaigns`, `campaign_targets` |
| **Audit & Compliance** | Ingests structured JSON logs from the device plane. Aggregates audit trails and compliance posture evidence. | HTTPS POST (`/api/v1/audit/ingest`) | `audit_events`, `compliance_postures` |
| **Observability & Support** | Receives health telemetry. Generates notifications/alerts, manages operator comments, and registers support bundles. | HTTPS POST (`/api/v1/health/ingest`) | `health_snapshots`, `support_bundles`, `incidents` |
| **Artifact & Model Registry** | Catalogs and serves metadata/hashes for validated base OS images, AI model weights, and plugin packages. | HTTPS GET/POST (`/api/v1/registry/*`) | `artifacts`, `signatures` |

## Service Dependencies and Owners
- **Owner Role:** Avishek (Control Plane Owner).
- **Service Topology:** To minimize dependency overhead during the enterprise pilot phase, all services will run under a unified backend server wrapper with SQLite backing, allowing independent modules to share a single DB file but maintain strict code boundary separation.
