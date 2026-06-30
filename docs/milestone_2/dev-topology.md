# Local Development Topology and Repo Conventions

This document specifies the network ports, paths, and directory layout conventions for local development of the **CerynixOS Fleet Control Plane**.

## Local Development Topology

For local validation, all control plane services and database operations run locally.

### 1. Network Port Assignments

| Component | Default Port | Protocol | Description |
|---|---|---|---|
| **Control Plane REST API** | `8000` | HTTP/HTTPS | Main REST API gateway for all device-plane endpoints and the Admin UX. |
| **Admin Web Console** | `5000` | HTTP | Serves the web-based Operator Interface dashboard. |

### 2. Database Stack
- **Database Engine:** SQLite 3.
- **Local File Path:** `control-plane/db/control_plane.db` (auto-created on startup).
- **Migration Strategy:** Simple schema verification on startup or a lightweight SQL migrations runner.

### 3. API Versioning Scheme
- All endpoints exposed by the control plane REST API must start with the prefix `/api/v1/`.
  - Example enrollment route: `/api/v1/enroll`
  - Example policy route: `/api/v1/policy/resolve`

---

## Repository Conventions

The control plane files will be organized under the `control-plane/` root folder in the repository workspace:

```text
cerynixos/
├── control-plane/
│   ├── README.md               # Folder purpose, architecture, and dependencies
│   ├── CHANGELOG.md            # Completed feature log
│   ├── db/
│   │   └── control_plane.db    # SQLite local file (git-ignored)
│   ├── simulator/
│   │   └── device_simulator.py # Mock device simulator executable
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py             # Entry point / routing server
│   │   ├── database/           # SQLite connection, tables initialization, and seed data
│   │   │   ├── connection.py
│   │   │   └── schema.py
│   │   └── services/           # Decoupled backend business logic
│   │       ├── enrollment.py
│   │       ├── inventory.py
│   │       ├── policy.py
│   │       ├── updates.py
│   │       ├── audit.py
│   │       ├── health.py
│   │       └── registry.py
│   ├── tests/                  # Backend unit/integration tests
│   │   └── test_api.py
│   └── ui/                     # Admin UI frontend files (HTML/CSS/JS)
│       ├── index.html
│       ├── index.css
│       └── app.js
```

### Module Boundaries
Each file under `control-plane/src/services/` should expose clean functions and limit inter-module direct dependencies. Database queries should pass through a central database utility or SQL helper functions to prevent connection locks and verify schemas.
