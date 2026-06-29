# Base Module

## Purpose
Establishes the absolute minimal foundation for CerynixOS. This module configures the bootloader (systemd-boot) to ensure atomic rollbacks, sets up basic networking, installs essential command-line tools, and hardens basic services like SSH.

## Main Components
- `default.nix`: The primary NixOS configuration.

## Data Flow
- This module is imported directly into the `nixosConfigurations` defined in the top-level `flake.nix`.

## Risks or Limits
- **Minimalism:** Do not add heavy desktop environments or AI tools here. Those belong in higher-level profiles or feature modules.
- **Rollback Limit:** We cap `configurationLimit` at 10 to avoid filling up the boot partition.
