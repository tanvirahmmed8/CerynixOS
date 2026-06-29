# Repository Structure and Coding Standards

## Canonical Folder Layout
```text
cerynixos/
├── flake.nix                    # Top-level NixOS flake
├── flake.lock
├── docs/                        # Project documentation
│   └── phase-0/                 # Phase 0 deliverables
├── contracts/                   # Interface contract schemas
├── mocks/                       # Mock services and fixtures
│   └── fixtures/
├── modules/                     # NixOS modules (system config)
│   ├── base/                    # Core system packages and boot
│   ├── ai-runtime/              # AI inference services
│   ├── action-broker/           # Safe action execution
│   ├── optimizer/               # Optimization engine
│   ├── healer/                  # Self-healing services
│   ├── health/                  # Observability and diagnostics
│   ├── update-agent/            # Update lifecycle
│   ├── plugin-runtime/          # Plugin system
│   ├── security/                # Hardening and encryption
│   └── desktop/                 # UX and assistant shell
├── packages/                    # Custom Nix packages
├── overlays/                    # Nix overlays
├── profiles/                    # Hardware/workload profiles
├── tests/                       # Integration and system tests
└── scripts/                     # Dev helper scripts
```

## Rules for New Feature Folders
As outlined in `development_instruction_prompt.md`, every feature or module folder **must** include:
1. `README.md`: Explaining the folder's purpose, flow, inputs/outputs, and risks.
2. `CHANGELOG.md`: For tracking behavior changes, API impacts, and completion notes.

## Coding Standards
1. **Declarative First:** System changes must be applied via Nix configurations, not imperative scripts.
2. **Safe Defaults:** Services should start in their most restrictive, secure state.
3. **Structured Logging:** Use JSON-formatted standard output for logs, ingested by `journald`.
4. **Mocked Periphery:** If a service calls a control plane API, it must have a toggle to use a local JSON fixture from `mocks/fixtures/` during Milestone 1.
