# Device Certificate Lifecycle — CerynixOS Placeholder Model

## Scope

This document defines the placeholder certificate lifecycle model for CerynixOS device identity. It describes the intended architecture for v2 post-pilot and identifies code extension points.

> [!NOTE]
> In v1 (pilot), device identity is established only by a shared bearer token. This document describes the target state for production-grade device authentication.

---

## Certificate Roles

| Certificate | Issued By | Held By | Purpose |
|---|---|---|---|
| Root CA Certificate | CerynixOS PKI Team | Control Plane (trust anchor) | Signs all intermediate and device certs |
| Intermediate CA | Root CA | Provisioning Service | Signs individual device certificates |
| Device Certificate | Intermediate CA | Device TPM / Secure Enclave | Proves device identity to control plane |

---

## Lifecycle Phases

### 1. Provisioning
- **When**: During device manufacturing or initial OS flashing.
- **How**: The provisioning service generates a unique device key pair inside the device's TPM. The public key is submitted to the intermediate CA for signing.
- **Output**: A device certificate embedded in TPM with fields:
  - `CN` = `dev-<uuid>`
  - `O` = `CerynixOS Pilot Fleet`
  - `SANs` = device serial number
  - `Validity` = 2 years (renewable)

### 2. Enrollment
- **When**: First boot after provisioning.
- **How**: Device presents its certificate to `POST /api/v1/enrollment/enroll`. The control plane verifies the certificate chain against the Root CA. On success, the device record is created and a short-lived auth token is issued.

### 3. Renewal
- **When**: 30 days before certificate expiry (`validity - 30d`).
- **How**: Device initiates a new CSR (Certificate Signing Request) flow via `POST /api/v1/devices/{id}/cert/renew` (to be implemented in v2). The old certificate remains valid until the renewal completes.

### 4. Revocation
- **When**: Device decommissioning, theft/loss, or security incident.
- **How**:
  - Operator calls `PATCH /api/v1/devices/{id}` with `enrollment_state: "decommissioned"`.
  - Control plane adds the device certificate serial number to a Certificate Revocation List (CRL).
  - All subsequent auth attempts from the device are rejected.
- **v1 Equivalent**: Setting `enrollment_state` to `decommissioned` blocks further API access.

---

## TPM Integration Extension Points

The following are the exact code locations where TPM-backed certificate verification would be added in v2:

| File | Location | Change |
|---|---|---|
| `services/auth.py` | `get_role_for_token()` | Replace static token check with `ssl.verify_certificate(cert, root_ca)` |
| `routes/enrollment.py` | `POST /enrollment/enroll` handler | Extract device cert from `X-Device-Cert` header and verify before creating record |
| `services/auth.py` | New `verify_device_cert(cert_pem)` function | Certificate chain validation against embedded Root CA |

---

## Certificate Storage

| Item | v1 Location | v2 Location |
|---|---|---|
| Root CA cert (trust anchor) | N/A | `control-plane/certs/root_ca.pem` |
| Device cert (per device) | N/A | Device TPM (non-exportable private key) |
| CRL | N/A | `control-plane/db/revoked_certs.db` table |
