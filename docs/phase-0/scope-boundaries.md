# Milestone 1: Scope Boundaries

## In Scope
This milestone covers the **Device Plane** foundation. It establishes the secure, self-healing, AI-capable endpoint OS environment without requiring a real enterprise control plane.

- **Base System:** NixOS flakes, core modules, boot flow, rollback mechanism.
- **AI Runtime:** Local inference using `llama.cpp` or `vLLM` with a small language model (e.g., Llama 3 8B, Phi-3).
- **Action Broker:** The sandboxed execution environment with explicit permission models (suggest, ask, auto) and local audit logging.
- **Optimization Engine (v1):** Rule-based engine reacting to local telemetry (CPU, memory, thermals).
- **Self-Healing (v1):** Detection of drift or basic failures, followed by automatic or guided rollback.
- **Observability:** Local metric collection, structured logs, and health scoring.
- **Update Agent:** Staged application of updates and rollback upon failure.
- **Plugin Runtime (v1):** Execution of local, isolated skills/plugins.
- **Desktop UX:** GNOME or KDE base with an integrated text-first AI assistant overlay and optimization dashboard.
- **Security:** Local permission hardening, model integrity checks, and basic isolation.

## Out of Scope (Non-Goals)
These items are deferred to Milestone 2 (Control Plane) or beyond.
- **Real Control Plane Backend:** Do not integrate with a real remote server. All remote interactions must use the local mock services and fixtures.
- **Multi-Device Sync:** No cloud syncing of profiles, task memory, or configurations.
- **Advanced Voice Interaction:** Voice pipelines are out of scope (stub implementations are acceptable but not required).
- **On-Device Training:** No continuous learning, RL, or fine-tuning (LoRA) pipelines.
- **Enterprise Identity:** No SSO, Active Directory, or full zero-trust identity flows.
- **Mobile/Embedded Builds:** Target x86_64/ARM64 standard PCs and VMs only.
- **Compliance Tooling:** No SBOM generation, SOC2 evidence gathering, or automated audit exports.
- **App Marketplace:** No central plugin registry or app store.
