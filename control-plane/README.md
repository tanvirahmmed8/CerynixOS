# Fleet Control Plane

This folder contains the enterprise backend server for CerynixOS fleet management, policy distribution, and OTA updates.

## What this folder does
This folder implements the centralized backend APIs used by CerynixOS endpoints. It manages:
- Token-based fleet enrollment.
- System, model, and plugin registry metadata.
- Precedence-based policy resolution and distribution.
- Telemetry ingestion, health scoring, and alert management.
- Update rings (Canary, Pilot, Broad, Critical) and campaign management.
- Multi-dimensional compliance evidence reporting.
- Diagnostic support bundle storage registries.

## Main components
- **`src/main.py`:** Application initialization, correlation routing, and log settings.
- **`src/database/`:** Schema layout, SQLite WAL initialization, and query execution context managers.
- **`src/routes/`:** Decoupled HTTP REST endpoint routers (health check, database readiness).
- **`src/services/`:** Business logic and helper dependencies (token authentication).
- **`simulator/`:** Synthetic device generator and JSON schema validator testing endpoints.

## Data flow
1. **Device Requests:** Device-plane clients invoke endpoints on port `8000`.
2. **Correlation ID:** Middleware intercepts incoming requests, attaches `X-Correlation-ID` header, and records request telemetry to stdout in JSON format.
3. **Authentication:** The request payload or bearer header is verified via auth checks.
4. **Endpoint Router:** Router endpoints execute operations via standard query methods.
5. **Database Transaction:** SQLite commits fleet changes in WAL mode.
6. **Telemetry Ingestion:** Health and audit telemetry payloads are verified against schemas before database record writes.

## External dependencies
- **FastAPI / Uvicorn:** Core routing framework and server runtime.
- **SQLite 3:** Lightweight local fleet datastore.

## Risks or limits
- **Pilot Scope Isolation:** Local SQLite state lacks distributed clustering or multi-region replication. High-concurrency environments should migrate backend modules to a PostgreSQL engine.
- **Scaffolded TLS/SSO:** Active Directory and SSO bindings are deferred to subsequent development phases.
