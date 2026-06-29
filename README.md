# CerynixOS

**The Enterprise AI Operating System**

CerynixOS is a next-generation, local-first operating system built on the immutable foundations of NixOS. It embeds a lightweight, on-device AI runtime that acts as a deeply integrated system assistant, capable of understanding user intent and executing system administration tasks securely.

## Core Architecture

CerynixOS is built around a Zero-Trust security model for its intelligent capabilities:

1. **Immutable Base OS:** Built using NixOS flakes, ensuring every deployment is 100% reproducible and declarative.
2. **Local AI Runtime:** Uses a quantized Qwen 2.5 0.5B model running entirely offline on-device via `llama.cpp`. It respects strict memory budgets and operates via a secure Unix Domain Socket.
3. **Action Broker:** The AI cannot execute commands directly. It outputs JSON tool calls which are routed to the Action Broker. The Broker sanitizes arguments, checks enterprise policy, handles user approval, and executes the action safely with full audit logging.

## Project Structure

```text
cerynixos/
├── flake.nix                    # Top-level NixOS flake
├── docs/                        # Project documentation & Milestone tracking
├── contracts/                   # JSON schemas for control-plane interfaces
├── mocks/                       # Local stubs for remote enterprise policies
├── modules/
│   ├── base/                    # Core OS packages, networking, systemd-boot
│   ├── ai-runtime/              # Local AI Engine & UDS API
│   └── action-broker/           # Safe execution sandbox and policy engine
└── profiles/
    ├── workstation-dev/         # Developer environment baseline
    └── workstation-creator/     # Creative environment baseline
```

## Getting Started (Milestone 1)

Ensure you have Nix installed with flakes enabled.

### Run in a local VM
To compile and boot the OS in a QEMU virtual machine:
```bash
nix build .#nixosConfigurations.cerynixos-vm.config.system.build.vm
./result/bin/run-cerynixos-vm
```

### Build a bootable ISO
To create a live USB installer for physical hardware:
```bash
nix build .#nixosConfigurations.cerynixos-iso.config.system.build.isoImage
```
The ISO will be placed in `./result/iso/`.

## Roadmap

This project is currently executing **Milestone 1: Device Plane**. 
See `milestone_1_device_plane.md` for the full task breakdown and current progress on observability, self-healing, and UX integration.
