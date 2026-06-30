# CerynixOS Operator Personas

This document outlines the three primary administrative operator personas who interact with the CerynixOS Control Plane, guiding the information architecture, permission models, and user interfaces.

---

## 1. Platform SRE Architect (Alistair)
* **Goal:** Fleet provisioning, release management, rollouts monitoring, and device configuration orchestration.
* **Role:** Platform Engineer / Administrator
* **Key Workflows:**
  - Standardizing global and group configuration policies.
  - Designing release version configurations and scheduling progressive update campaigns.
  - Reviewing fleet compliance scores and monitoring rollout status.
* **UI Requirements:**
  - Actionable dashboard summaries (averages health score, update rollout campaigns stats).
  - Revision history control lists and policy assignments forms.
  - Deployment campaign progress sliders and rollbacks controls.

---

## 2. Helpdesk Support Engineer (Sarah)
* **Goal:** Troubleshoot failing device plane issues, review logs, check system resources, and manage incident tickets.
* **Role:** Operations Operator / Support Technician
* **Key Workflows:**
  - Responding to degraded CPU, memory, or crashed service alerts.
  - Querying support logs and retrieval manifests for diagnostic packages.
  - Logging incident notes and tracking resolution statuses.
  - Dispatched diagnostic reboots and checking live system service statuses.
* **UI Requirements:**
  - Chronological device timelines merging audit trails and snapshots.
  - Interactive diagnostics terminal shell simulating live command executes.
  - Operations ticket workspace for notes and ticket severity/state overrides.

---

## 3. Compliance & Security Auditor (Marcus)
* **Goal:** Verify cryptographic log chains, review access logs, and guarantee policy enforcement.
* **Role:** Auditor / Security Engineer
* **Key Workflows:**
  - Running chronological database chain validation scans to check for tampering.
  - Querying policy denied execution audit lists.
  - Exporting evidence reports (inventory, policies, update campaigns, audit chains).
* **UI Requirements:**
  - Single-click cryptographic ledger validation.
  - Explicit role gating indicators.
  - Direct download links for raw structured JSON evidence archives.
