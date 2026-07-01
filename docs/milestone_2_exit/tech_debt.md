# Milestone 2 Technical Debt & Convergence Handoff

As we conclude Milestone 2 (Control Plane) and prepare for the unified integration with Milestone 1 (Device Plane), the following architectural gaps and open issues must be resolved.

## 1. Device-to-Cloud Wiring (Action Broker)
**Current State:** The Milestone 1 Action Broker reads local JSON files in `mocks/` to determine security policy.
**Convergence Requirement:** The Action Broker must be rewritten to securely poll (or maintain an active WebSocket/MQTT connection to) the live Control Plane `/api/v1/policies` endpoint. It must enforce the real-time policies downloaded from the server, replacing the local mocks.

## 2. Identity Bridging (TPM to mTLS)
**Current State:** Both Milestones use a placeholder UUID string for identity.
**Convergence Requirement:** 
1. The Device must read the hardware TPM Endorsement Key.
2. The Device must generate a CSR and send it to the Control Plane `/api/v1/enroll` endpoint.
3. The Control Plane must validate the TPM attestation against the manufacturer chain.
4. The Control Plane must issue a signed x509 Client Certificate.
5. All future communication from the Device must use this Client Certificate (mTLS) for authentication.

## 3. Telemetry and Health Streaming
**Current State:** The M1 Health Agent logs system metrics to `journalctl`.
**Convergence Requirement:** The Health Agent must batch and push these metrics to the Control Plane `/api/v1/health` endpoint at the interval specified by the active Policy. The Control Plane must parse these and trigger alerts (e.g., "Device 123 CPU > 95%").

## 4. Plugin Distribution Security
**Current State:** Plugins are manually copied into `/var/lib/cerynixos-plugins`.
**Convergence Requirement:** The `cerynix-plugin-manager` on the device must be wired to download `.tar.gz` plugin bundles from the Control Plane Registry, verify the ECDSA signature from the Admin Console, and only execute them if the signature matches the Root of Trust.
