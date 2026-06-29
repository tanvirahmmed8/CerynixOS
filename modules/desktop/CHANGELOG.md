# Changelog - Desktop Module

## 2026-06-29
- **Feature:** Initial Desktop and CerynixAI UX setup
- **Changes:**
  - Configured GNOME as the base Wayland desktop environment in `default.nix`.
  - Built a premium glassmorphism Web UI for the CerynixAI overlay (`index.html`, `index.css`, `app.js`).
  - Added an Optimization Dashboard and Action Approval modal to the UI.
  - Implemented `ui_server.py` to serve the local interface.
  - Implemented `voice_stub.py` to simulate local STT pipelines.
