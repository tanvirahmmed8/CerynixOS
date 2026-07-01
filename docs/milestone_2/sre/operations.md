# Standard Operating Procedures (SOPs)

## 1. Backup and Restore Procedures
**Database Assumption:** Managed PostgreSQL cluster.
- **RPO (Recovery Point Objective):** 5 minutes (via Continuous WAL archiving).
- **RTO (Recovery Time Objective):** 1 hour (Time to spin up a new instance from snapshot).
- **Procedure:** 
  - Automated daily snapshots retained for 35 days.
  - In a catastrophic loss, use cloud-native tooling (e.g., RDS Point-In-Time-Recovery) to restore to a newly provisioned instance, update DNS/secrets, and monitor application reconnection.

## 2. Staging-to-Production Promotion Checklist
Before deploying new Control Plane code to Production:
- [ ] CI pipeline passes (Unit, Integration, and E2E tests).
- [ ] Synthetic Fleet integration tests pass in Staging.
- [ ] Security scan (SAST/DAST) reports zero critical/high vulnerabilities.
- [ ] Database migrations reviewed and deemed backward-compatible.
- [ ] Release notes and rollback plan documented.

## 3. Pilot Customer Onboarding Checklist
When onboarding a new Enterprise Tenant to the Control Plane:
- [ ] Provision Tenant ID and dedicated database schema (or logical separation).
- [ ] Issue Root CA credentials for the tenant's enrollment process.
- [ ] Create initial "Baseline" Security Policy.
- [ ] Create initial "Admin" and "Auditor" RBAC roles for the customer.
- [ ] Verify Tenant can access their Admin Console dashboard.
- [ ] Distribute CerynixOS ISO bundle with injected Tenant identifiers.
