# Endpoint Service List and Ownership Map

| Service Name | Purpose | Owner | Dependencies | Milestone Phase |
|---|---|---|---|---|
| `cerynix-base` | Core NixOS configuration and hardware support | Platform | Linux Kernel | Phase 1 |
| `cerynix-ai-runtime` | Loads and manages the lifecycle of the local SLM | AI Systems | Base | Phase 2 |
| `cerynix-action-broker` | Validates, executes, and audits all privileged tool calls | Platform | Policy Agent, Base | Phase 3 |
| `cerynix-telemetry` | Collects local eBPF and kernel metrics with low overhead | Observability| Kernel | Phase 4 |
| `cerynix-health-agent` | Aggregates telemetry into health scores and log bundles | Observability| Telemetry | Phase 4 |
| `cerynix-optimizer` | Rule-based performance adjustments (CPU/Mem/I/O) | Platform | Telemetry | Phase 5 |
| `cerynix-healer` | Detects config drift and triggers safe rollbacks | Platform | Base, Config | Phase 6 |
| `cerynix-assistant-ui`| Text-first AI interaction layer embedded in the desktop | UX | AI Runtime | Phase 7 |
| `cerynix-update-agent`| Parses update metadata and performs staged OS upgrades | Platform | Mock Metadata | Phase 8 |
| `cerynix-plugin-runtime`| Discovers and isolates local capability extensions | Platform | Action Broker | Phase 9 |
| `cerynix-policy-agent`| Enforces local and mocked remote enterprise policies | Security | Mock Policy | Phase 3 |

## Service Communication
- Internal service-to-service communication should default to local `systemd` sockets, DBus, or gRPC over Unix Domain Sockets.
- All services must run under their own least-privilege user account.
