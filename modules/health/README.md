# Local Observability and Diagnostics

## Purpose
The `health` module provides the telemetry and diagnostic foundation for CerynixOS. It monitors system resources and critical services to produce a unified Health Score, which is used by the Action Broker and Optimization Engine to make autonomous decisions.

## Main Components
- `default.nix`: Defines the `cerynix-health-agent` service and installs the `cerynix-diag` CLI tool globally.
- `src/health_agent.py`: A lightweight python daemon that polls metrics every 60 seconds and writes the state to `/var/lib/cerynixos-health/state.json`.
- `src/cerynix_diag.py`: CLI tool for users and the AI to instantly fetch health status or export redacted crash snapshots.
- `docs/metrics-catalog.md`: Documentation of collected metrics.
- `docs/log-format.md`: Documentation of the mandatory JSON structured logging format.

## Data Flow
- Hardware / `systemd` -> `health_agent` -> `state.json`.
- `state.json` -> `cerynix-diag` -> Terminal or AI prompt context.

## Risks or Limits
- The agent currently runs as `root` because it needs to read `systemd` states and `journalctl` logs. In a future production iteration, this should be scoped down to a dedicated user with `systemd-journal` group access and specific Polkit rules.
