# Plugin Runtime and Developer Extensibility

## Purpose
The `plugin-runtime` module defines the lifecycle and execution isolation for third-party tools running on CerynixOS. This enables developers to expand CerynixAI's capabilities without modifying the core OS.

## Main Components
- `docs/plugin-contract.md`: The developer guide outlining the JSON manifest format and the expected CLI I/O format (JSON).
- `src/plugin_manager.py` (`cerynix-plugin-manager`): CLI for installing, removing, and listing plugins within `/var/lib/cerynixos-plugins/`.
- `src/plugin_runner.py` (`cerynix-plugin-runner`): A secure execution wrapper. It enforces timeouts, writes to the `audit.log`, and (via the NixOS configuration) runs the actual plugin script under a restricted UNIX user (`cerynix-plugin-user`) to prevent it from touching system files.
- `src/sample-plugin`: A basic "weather" plugin demonstrating the contract.

## Security Model (v1)
In Milestone 1, isolation is achieved via UNIX user separation (`sudo -u cerynix-plugin-user`). This guarantees that a rogue plugin cannot read the Action Broker's secrets or rewrite system configurations, preventing a major attack vector in Agentic systems.
