# Update Agent and Local Release Safety

## Purpose
The `update-agent` module handles the safe application of NixOS flake updates. It ensures that CerynixOS only updates when healthy, and provides a built-in safety net that immediately triggers a system rollback if a new generation causes a critical service failure.

## Main Components
- `src/update_agent.py` (`cerynix-update`): The main engine. It checks the Health Agent score, stages the update, applies it, and runs post-verifications.
- `src/update_status.py` (`cerynix-update-status`): A simple CLI to read `/var/lib/cerynixos-update/history.json` and print a table of update attempts and rollbacks.
- `src/update_test.py`: The simulation harness to prove the rollback logic works.
- `default.nix`: Installs the CLI tools and grants the Action Broker the necessary `sudo` rights so CerynixAI can orchestrate updates transparently.

## Data Flow
- Control Plane (or Local Metadata file) -> `cerynix-update` -> `nixos-rebuild switch` -> Verification -> Success OR `nixos-rebuild switch --rollback`.
