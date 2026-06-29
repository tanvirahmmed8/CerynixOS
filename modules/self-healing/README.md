# Self-Healing and Recovery v1

## Purpose
The `self-healing` module provides the automated logic to detect drift, recover from service crashes, and guide the user (or CerynixAI) through medium-risk fixes like rolling back a system update or clearing disk space.

## Main Components
- `docs/scenarios.md`: The 5 core supported failure scenarios for Milestone 1.
- `src/healer.py`: The `cerynix-healer` CLI tool. It actively repairs critical broken services, and uses `recovery_ui.py` to ask for permission before running destructive cleanups.
- `src/snapshot_manager.py`: The `cerynix-snapshot` CLI tool. It backs up `~/.config/cerynixos` to allow localized rollback of user config drift without reverting the entire OS.
- `default.nix`: Grants `cerynix-broker` passwordless `sudo` rights so CerynixAI can orchestrate these healing functions dynamically.
