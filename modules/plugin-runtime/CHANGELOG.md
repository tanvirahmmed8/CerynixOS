# Changelog - Plugin Runtime

## 2026-06-29
- **Feature:** Initial Plugin framework and isolation model
- **Changes:**
  - Defined `plugin-contract.md` with `manifest.json` schema.
  - Implemented `cerynix-plugin-manager` for install/remove/list operations.
  - Implemented `cerynix-plugin-runner` which executes plugins and captures JSON stdout.
  - Added strict audit logging for all plugin executions.
  - Configured `default.nix` to create a dedicated `cerynix-plugin-user` for UNIX-level isolation.
  - Provided `weather-plugin` as an SDK sample.
  - Created `plugin_test.py` simulation harness.
