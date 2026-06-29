# Changelog - Optimizer Module

## 2026-06-29
- **Feature:** Initial Optimization Engine setup
- **Changes:**
  - Created JSON profiles for Gaming, Coding, Rendering, and Battery Saver.
  - Implemented `cerynix-optimizer` CLI for safely writing to sysfs.
  - Implemented `revert` mechanism to allow one-click rollback of profile changes.
  - Integrated explainability logs at `/var/log/cerynixos-optimizer/decisions.log`.
  - Added specific `sudoers` rule allowing the Action Broker to invoke the optimizer.
