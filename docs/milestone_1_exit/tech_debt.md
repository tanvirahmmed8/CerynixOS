# Milestone 1 Technical Debt & Handoff

As we conclude Milestone 1 (Device Plane) and prepare for Milestone 2 (Control Plane), the following local mocks and stubs MUST be replaced with real backend integrations.

## 1. Identity & Enrollment (Phase 10)
**Current State:** `cerynix-identity` generates a mock x509 cert and random UUID.
**M2 Requirement:** The Control Plane must implement a Fleet Registration API that validates a real hardware TPM attestation quote and issues a signed client certificate.

## 2. Update Metadata Contracts (Phase 8)
**Current State:** `cerynix-update` reads from local static files (`mocks/update-metadata-good.json`).
**M2 Requirement:** The OS must poll (or listen via gRPC/MQTT) a Fleet Management API to receive Over-The-Air (OTA) update metadata payloads.

## 3. AI Inference Manager (Phase 2)
**Current State:** `inference_manager.py` uses a sleep timer to return a hardcoded "Hello World" completion.
**M2 Requirement:** This must be wired up to actual local weights (e.g., via `llama.cpp` or `vLLM`) or proxied to the secure cloud backend if local constraints are met.

## 4. Voice Pipeline (Phase 7)
**Current State:** `voice_stub.py` simulates a wake-word and random commands every 15-60 seconds.
**M2 Requirement:** Integrate actual local STT (e.g., Whisper.cpp) and a VAD (Voice Activity Detection) engine like Silero.

## 5. Plugin Distribution (Phase 9)
**Current State:** Plugins are installed via local directory copy.
**M2 Requirement:** Implement a secure Plugin Marketplace/Registry where the `plugin_manager` can download and verify cryptographically signed packages over HTTPS.

## 6. Desktop UI Architecture (Phase 6)
**Current State:** The UI is served via a Python HTTP server (`ui_server.py`) on `localhost:3000`. This poses security risks (unencrypted local traffic, port scanning by other local apps, port collisions).
**Future Requirement:** The HTTP server must be replaced by a native GTK+WebKit application. The CerynixAI UI should be launched via a native GNOME Shell Extension (as a status bar icon) and integrated directly into GNOME Settings, communicating directly over the UDS socket.
