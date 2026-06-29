# Changelog - Action Broker

## 2026-06-29
- **Feature:** Initial Action Broker implementation
- **Changes:**
  - Implemented UDS-based FastAPI server.
  - Implemented policy engine evaluating against mock JSON fixture.
  - Implemented safe executor with specific sudo tool mappings.
  - Added JSON audit logging.
  - Configured NixOS module with a dedicated `cerynix-broker` user and restrictive sudoers rules.
