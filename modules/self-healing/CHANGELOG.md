# Changelog - Self-Healing Module

## 2026-06-29
- **Feature:** Initial Self-Healing Engine setup
- **Changes:**
  - Created `cerynix-healer` CLI for automatic service restart and storage pressure checks.
  - Implemented `recovery_ui.py` to prompt users before taking destructive actions (like `nix-collect-garbage`).
  - Created `cerynix-snapshot` for backing up and restoring specific user configuration directories.
  - Wrote integration tests for service auto-recovery.
  - Integrated into system packages with `sudo` permissions for the Action Broker.
