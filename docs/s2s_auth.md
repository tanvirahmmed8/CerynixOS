# Service-to-Service Auth Pattern — CerynixOS Control Plane

## Scope

This document defines the authentication pattern for requests made from device agents to the CerynixOS Control Plane. It covers the v1 pilot pattern and the planned v2 upgrade path.

---

## v1: Static Enrollment Token (Pilot)

### Pattern
All device-agent API calls use a static shared bearer token validated against `config.json`:

```
Authorization: Bearer <api_token>
```

The device also sends its identity in a header:

```
X-Device-ID: dev-<uuid>
```

The control plane validates the bearer token via `services/auth.verify_token()`. The `X-Device-ID` header is used by device-facing route handlers to scope database reads and writes to that specific device record.

### Endpoints Accepting Device-Agent Auth

| Endpoint | Purpose |
|---|---|
| `POST /api/v1/enrollment/enroll` | Device self-registration |
| `POST /api/v1/devices/{id}/health` | Health telemetry ingest |
| `POST /api/v1/devices/{id}/audit/ingest` | Audit event submission |
| `GET /api/v1/devices/{id}/updates/check` | Update check |
| `POST /api/v1/devices/{id}/updates/status` | Update status report |
| `POST /api/v1/support/bundles` | Support bundle upload |
| `GET /api/v1/devices/{id}/diagnostics/pending` | Pending command poll |
| `POST /api/v1/devices/{id}/diagnostics/results` | Command result report |

### Assumptions & Limits
- The static token is a **shared secret** — any device in the fleet can impersonate any other `device_id` if they hold the token.
- This is acceptable for the closed pilot. The `X-Device-ID` header is **not cryptographically authenticated** in v1.
- Do not use this pattern in production multi-tenant environments.

---

## v2: Short-Lived JWT + Device Certificate (Post-Pilot)

### Pattern

1. **Device provisioning**: During manufacturing/flashing, a device-unique X.509 certificate signed by the CerynixOS Root CA is embedded in the device's TPM or secure enclave.
2. **Token exchange**: On boot, the device presents its certificate to a `/auth/token` endpoint. The control plane verifies the certificate chain against the Root CA and issues a short-lived JWT (TTL: 1 hour) with claims:
   ```json
   { "sub": "dev-<uuid>", "role": "device-agent", "exp": 1782900000 }
   ```
3. **Authenticated requests**: The device uses the JWT as a Bearer token for all subsequent API calls within the TTL window.
4. **Renewal**: Before expiry, the device repeats the certificate-based token exchange.

### Extension Point in Code

`services/auth.get_role_for_token()` is the sole extension point. To enable JWTs:
1. Import a JWT verification library (e.g., `python-jose`).
2. Replace the static string comparison with signature verification + claims extraction.
3. Map the `role` claim to the `ROLES` table in `auth.py`.
No changes to any route handler are required.

---

## X-Device-ID Header Convention

All device-facing route handlers must:
1. Accept `X-Device-ID` as a header parameter.
2. Verify the `device_id` path parameter matches the `X-Device-ID` header value.
3. In v2, cross-check the `device_id` against the `sub` claim in the JWT.

This prevents one device from inadvertently (or maliciously) writing data to another device's record.
