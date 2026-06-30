# CerynixOS

**The Enterprise AI Operating System**

CerynixOS is a next-generation, local-first operating system built on the immutable foundations of NixOS. It embeds a lightweight, on-device AI runtime acting as a deeply integrated system assistant — **CerynixAI** — capable of understanding user intent and executing system administration tasks securely, without ever sending data to the cloud.

---

## ✅ Milestone 1 (Device Plane) — COMPLETED

CerynixOS Milestone 1 has been fully implemented, compiled, and verified as a **2.5GB bootable ISO image**.

All 11 phases are complete:

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Architecture & Base OS | ✅ Done |
| 1 | NixOS Image Build | ✅ Done |
| 2 | Local AI Runtime (CerynixAI) | ✅ Done |
| 3 | Action Broker & Safe Execution | ✅ Done |
| 4 | Health, Observability & Diagnostics | ✅ Done |
| 5 | Optimization Engine | ✅ Done |
| 6 | Desktop UX | ✅ Done |
| 7 | Voice & Ambient Input | ✅ Done |
| 8 | Self-Healing & Update Agent | ✅ Done |
| 9 | Plugin Runtime & Developer Extensibility | ✅ Done |
| 10 | Security Hardening | ✅ Done |
| 11 | Quality, Certification & Milestone Exit | ✅ Done |

---

## Core Architecture

CerynixOS is built around a **Zero-Trust, Local-first** security model:

1. **Immutable Base OS:** Built using NixOS flakes — every deployment is 100% reproducible and declarative. Rollback to any prior generation in seconds.
2. **Local AI Runtime:** Uses a quantized `qwen2.5-0.5b-instruct-q4_k_m.gguf` model running entirely offline on-device via `llama.cpp`. It operates via a secure Unix Domain Socket (UDS) — no open TCP ports.
3. **Zero-Trust Action Broker:** The AI cannot execute commands directly. It outputs JSON tool calls which are intercepted by the Action Broker. The Broker sanitizes arguments, checks enterprise policy, prompts the user for confirmation via the Action Modal UI, and executes only with full audit logging.
4. **Self-Healing Agent:** A watchdog daemon continuously monitors all CerynixOS system services and automatically restarts any that crash, preventing a single service failure from degrading the user experience.
5. **Plugin Runtime:** Third-party developer skills and tools run inside a fully isolated UNIX user sandbox (`cerynix-plugin-user`). Every execution is cryptographically audited.
6. **Security Baseline:** AppArmor enabled globally, model weights verified by SHA256 integrity checks, and a device identity stub ready for TPM-backed enrollment in Milestone 2.

---

## Project Structure

```text
cerynixos/
├── flake.nix                    # Top-level NixOS flake (VM, ISO, Baremetal targets)
├── flake.lock                   # Pinned dependency snapshot
├── docs/
│   └── milestone_1_exit/        # QA Test Matrix, Operator Guide, Tech Debt Handoff
├── contracts/                   # JSON schemas for control-plane interfaces
├── mocks/                       # Local stubs for remote enterprise policies
├── modules/
│   ├── base/                    # Core OS packages, networking, systemd-boot
│   ├── ai-runtime/              # Local AI Engine, UDS API & model loader
│   ├── action-broker/           # Safe execution sandbox and policy engine
│   ├── health/                  # Telemetry, diagnostics & health scoring
│   ├── optimizer/               # One-click system optimization profiles & revert manager
│   ├── self-healing/            # Watchdog daemon & auto-recovery
│   ├── desktop/                 # CerynixAI glassmorphism UI (Web/HTML)
│   ├── update-agent/            # OTA update agent with automatic rollback
│   ├── plugin-runtime/          # Isolated plugin lifecycle manager & runner
│   └── security/                # AppArmor, integrity checker, device identity
└── profiles/
    ├── workstation-dev/         # Developer environment baseline
    └── workstation-creator/     # Creative environment baseline
```

---

## Building CerynixOS

### Prerequisites
- WSL2 with Ubuntu installed
- Nix package manager (via [Determinate Systems installer](https://install.determinate.systems/nix))

### Setup (first time only)
```bash
# Inside Ubuntu (WSL)
git config --global --add safe.directory '/mnt/e/Test code/os'
. /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
```

### Build a Bootable ISO
```bash
nix build .#nixosConfigurations.cerynixos-iso.config.system.build.isoImage
# Output: ./result/iso/nixos-*.iso  (~2.5 GB)
```
Flash to a USB drive or load in VirtualBox/VMware to boot.

### Build a VM Image
```bash
nix build .#nixosConfigurations.cerynixos-vm.config.system.build.vm
./result/bin/run-cerynixos-vm
```

---

## Running the UI (Windows / Development)
The CerynixAI Desktop UI can be previewed on any machine without booting the full OS:
```bash
python modules/desktop/src/ui_server.py
```
Open `http://localhost:3000` in your browser to see the glassmorphism interface.

---

## Roadmap

| Milestone | Description | Status |
|-----------|-------------|--------|
| **1 — Device Plane** | Local AI OS, Action Broker, Self-Healing, Plugins, Security | ✅ **COMPLETE** |
| **2 — Control Plane** | Fleet Enrollment, Policy Engine, Update Orchestration, Admin Console | 🔵 Up Next |
| **3+** | Advanced AI features, Multi-device sync, Enterprise SSO | 🗓️ Planned |

See [`milestone_1_device_plane.md`](milestone_1_device_plane.md) and [`milestone_2_control_plane.md`](milestone_2_control_plane.md) for full task breakdowns.

---

## AI Assistant: CerynixAI
CerynixAI is the name of the integrated AI assistant in CerynixOS. It runs entirely on-device using a small quantized language model, communicates exclusively over Unix Domain Sockets, and is strictly gated by the Action Broker. Users interact through the glassmorphism chat UI or voice commands. It never sends data to the internet without explicit user approval.
