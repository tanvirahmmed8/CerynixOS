# CerynixOS Governance & Compliance Review Notes

This document provides a technical summary of the security governance, audit logs, and compliance baseline postures implemented inside the CerynixOS Control Plane for enterprise review.

## 1. Cryptographic Audit Chain (Tamper-Evidence)

To prevent log editing or deletion (even by database administrators), audit logs are stored in a cryptographically chained ledger within SQLite.

### Mechanism
- Each audit event contains a `previous_hash` and a `tamper_hash`.
- The `tamper_hash` is computed as:
  $$\text{tamper\_hash} = \text{SHA256}(\text{previous\_hash} + \text{event\_id} + \text{device\_id} + \text{timestamp} + \text{service} + \text{action} + \text{status} + \text{details\_json\_string})$$
- The chain starts with a genesis block using the hash `"genesis"`.
- If any event row is edited or deleted, the subsequent records will fail verification.

### Validation API
Operators can trigger an verification scan at:
`POST /api/v1/audit/verify`

It chronologically crawls the database, re-evaluating each block hash, and flags any breaks immediately, identifying the tampered row.

---

## 2. Redaction & Retention Policies

Audit records ingestion includes active, server-side data sanitation and size management.

### Redaction Configuration
The control plane reads `audit_redact_fields` from `config.json` (defaults to: `"password"`, `"secret"`, `"token"`, `"key"`).
- Any keys in the details JSON matching these parameters (case-insensitive substring) are replaced with `"[REDACTED]"` prior to hashing and database storage.

### Retention Pruning
To prevent disk exhaustion during the pilot, database transactions prune old entries based on the `audit_retention_days` setting in `config.json` (defaults to `90` days).
- **Chain Resilience:** To support chain verification after old records are pruned, the verify API accepts the `previous_hash` of the oldest remaining record as the validation root instead of breaking.

---

## 3. Patch & Compliance Scoring Baselines

The system aggregates telemetry and logs into a single fleet-wide posture scoring model. A device is classified as **Compliant** only if it passes all four controls:

1. **State Baseline:** The device must be in the `'active'` enrollment state.
2. **Patch Baseline:** The device's current OS version must match the latest version registered for its assigned release channel (Canary, Pilot, Broad, or Critical).
3. **Health Baseline:** The latest health snapshot score must be $\ge 80$, and no CPU, memory, storage, or system services alerts must be in `'critical'` state.
4. **Policy Baseline:** The device must not have any policy execution denial events (`status = 'denied_by_policy'`) in its audit log history.

---

## 4. Evidence Report Exports

Structured datasets are exportable via:
`GET /api/v1/compliance/export/{report_type}`

Supported reports:
- **`inventory`:** Export device hardware details, models, active groups, and tags.
- **`updates`:** Export progressive update rollout status (pending, applying, verified, failed) per campaign.
- **`policies`:** Export global, group, and device-specific configuration policy targets.
- **`audit`:** Export chronological ledger showing cryptographic validation hashes and previous block targets.
