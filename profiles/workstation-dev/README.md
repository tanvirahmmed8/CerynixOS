# Developer Workstation Profile

## Purpose
Provides a tailored NixOS package set and configuration for software developers and systems engineers using CerynixOS.

## Main Components
- `default.nix`: Installs developer tools (Docker, compilers, terminal utilities).

## Data Flow
Imported by `flake.nix` for target device configurations (e.g., VM or physical developer hardware).

## Risks or Limits
- This profile enables the Docker daemon, which has security implications (users in the `docker` group have root-equivalent access). Ensure users are added to the group explicitly only if needed.
