# CerynixAI Native GTK Architecture

## Current Flaw (Milestone 1 Tech Debt)
Currently, the UI is served via a Python `http.server` on `localhost:3000`. This requires an open network port, which introduces a severe attack surface (port scanning, Cross-Site Request Forgery from malicious websites, unencrypted traffic).

## Target Architecture
The CerynixAI UI will be rebuilt as a native desktop application tightly integrated into GNOME.

### 1. The Container (PyGObject & GTK4)
We will write a `main.py` using `gi.repository.Gtk` (GTK4). This script will spawn a borderless, transparent, frameless native window on the desktop. This window will act as the shell for the UI.

### 2. The Renderer (WebKit2GTK)
Inside the GTK4 window, we will embed a `WebKit2GTK` WebView. This allows us to keep 100% of the beautiful Glassmorphism HTML/CSS/JS frontend we already designed, without rewriting it in C or Vala.

### 3. The Security Bridge (UDS)
Instead of the JavaScript making HTTP `fetch()` calls to `localhost:3000`, the WebKit container will inject a native Python callback bridge (`window.webkit.messageHandlers.cerynix.postMessage()`). 
When the user types a prompt in the UI, JavaScript passes the text to the Python bridge. The Python bridge securely writes the prompt directly to the Action Broker's Unix Domain Socket (`/run/cerynix/broker.sock`). 

**Result:** Zero open network ports. 100% secure IPC (Inter-Process Communication).

### 4. GNOME Integration
We will write a tiny JavaScript GNOME Shell Extension. This extension will place the Cerynix logo in the top right system tray (next to the battery/wifi icons). Clicking the icon will toggle the visibility of the GTK4 window (sliding it out from the right side of the screen like a native sidebar).
