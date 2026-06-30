# static/ — CerynixOS Admin Dashboard Frontend

## What This Folder Does

This folder contains the CerynixOS Fleet Control Console, a single-page application (SPA) served directly from the control plane server at the root path `/`. It provides enterprise operators with a full visual interface to manage devices, policies, update campaigns, compliance, incidents, and diagnostics.

## Main Components

| File | Role |
|---|---|
| `index.html` | Dashboard HTML shell — auth modal, sidebar navigation, 6 operator workspace tabs, modal forms |
| `styles.css` | Dark mode design system — CSS custom properties, glassmorphism cards, terminal shell theme, responsive layouts |
| `app.js` | Frontend controller — token gating, tab routing, API client, form submissions, live alerts polling loop, diagnostics terminal |

## Data Flow

1. **Auth**: User enters token → verified against `GET /api/v1/observability/fleet` → stored in `localStorage`
2. **Dashboard loads**: Triggers `loadOverviewMetrics()` which fetches fleet health, alerts, and compliance posture
3. **Polling**: `setInterval` every 10 seconds refreshes alerts and updates header badge count
4. **Tab navigation**: Each tab switch calls a dedicated load function hitting the relevant API endpoints
5. **Diagnostics terminal**: Enqueues command via `POST /api/v1/devices/{id}/diagnostics/execute`, then simulates device agent polling pending commands and reporting results

## API Endpoints Used

| Endpoint | Tab |
|---|---|
| `GET /api/v1/observability/fleet` | Overview, Auth |
| `GET /api/v1/observability/alerts` | Overview |
| `GET /api/v1/compliance/posture` | Overview |
| `GET /api/v1/devices` | Inventory, Diagnostics, Simulators |
| `GET /api/v1/policies` | Policies |
| `POST /api/v1/policies` | Policies |
| `POST /api/v1/policies/{id}/assign` | Policies |
| `GET /api/v1/updates/releases` | Updates |
| `GET /api/v1/updates/campaigns` | Updates |
| `POST /api/v1/updates/campaigns` | Updates |
| `POST /api/v1/updates/campaigns/{id}/{action}` | Updates |
| `POST /api/v1/audit/verify` | Governance |
| `GET /api/v1/compliance/export/{type}` | Governance |
| `GET /api/v1/support/incidents` | Diagnostics |
| `POST /api/v1/support/incidents` | Diagnostics |
| `PATCH /api/v1/support/incidents/{id}` | Diagnostics |
| `GET /api/v1/support/bundles` | Diagnostics |
| `GET /api/v1/devices/{id}/timeline` | Diagnostics |
| `POST /api/v1/devices/{id}/diagnostics/execute` | Diagnostics |
| `GET /api/v1/devices/{id}/diagnostics/pending` | Diagnostics |
| `POST /api/v1/devices/{id}/diagnostics/results` | Diagnostics |
| `POST /api/v1/devices/{id}/simulate-failure` | Simulators |

## External Dependencies

- [Google Fonts — Outfit](https://fonts.google.com/specimen/Outfit) (loaded via CDN)
- No other external JS or CSS frameworks

## Risks & Limits

- Auth token stored in `localStorage` — intended for pilot use only; not suitable for production
- Role-aware gating is a UI placeholder (role badge only); actual RBAC enforcement is done at the API layer
- Diagnostics terminal results polling uses a client-side simulation loop, not a real WebSocket
