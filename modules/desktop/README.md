# Desktop UX and CerynixAI Experience

## Purpose
The `desktop` module defines the graphical environment for CerynixOS (GNOME) and contains the reference Web-based UI for the **CerynixAI Overlay**.

## Main Components
- `default.nix`: Configures GNOME, GDM, and base fonts.
- `src/ui_server.py`: A lightweight python web server to host the local HTML UI.
- `ui/`: Contains the `index.html`, `index.css`, and `app.js` for the CerynixAI panel. This UI features a Chat interface, an Optimization dashboard, and Action Confirmation modals.
- `src/voice_stub.py`: A simulated voice detection pipeline that forwards commands to the AI.

## Running the UI Locally
In a real deployment, the CerynixAI UI would be a Tauri app or a GNOME WebKit extension. For Milestone 1, we can test the aesthetics by running:
```bash
cerynix-ui-server
```
And opening `http://localhost:3000` in a browser.
