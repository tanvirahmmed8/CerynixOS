# Secret Rotation Procedure — CerynixOS Control Plane

## Scope

This document defines the steps to rotate secrets in the CerynixOS Control Plane without service downtime during the v1 pilot period.

---

## Secret Inventory

| Secret | Location | Used By |
|---|---|---|
| `api_token` | `control-plane/config.json` | All admin + device-agent API auth |
| `SIGNING_SECRET_KEY` | `control-plane/src/services/registry.py` (line 13) | Registry download URL HMAC signing |

---

## 1. Rotating `api_token`

### Pre-Rotation Checklist
- [ ] Notify all admin operators and device agents of the upcoming rotation window (recommend off-hours).
- [ ] Confirm the new token value is at least 32 random characters (use `openssl rand -hex 32`).
- [ ] Confirm all clients are configured to reload their token from a secrets manager or config file — not hardcoded.

### Rotation Steps

**Step 1** — Generate new token:
```bash
openssl rand -hex 32
```

**Step 2** — Update `config.json` with the new token value:
```json
{
  "api_token": "<new-token-value>"
}
```

**Step 3** — Restart the control plane server:
```bash
# Stop current process
# Then start fresh:
python control-plane/src/main.py
```

**Step 4** — Update all admin operator browser sessions:
- Clear `localStorage` (`cerynix_auth_token`) and re-enter the new token in the dashboard login modal.

**Step 5** — Re-enroll or reconfigure all device agents with the new token in their fleet configuration.

### Post-Rotation Verification
- [ ] Confirm a `GET /api/v1/observability/fleet` request with the **new** token returns `200 OK`.
- [ ] Confirm a request with the **old** token returns `401 Unauthorized`.
- [ ] Confirm security event logs show `auth_success` for the new token, and `auth_failure` for old.

---

## 2. Rotating `SIGNING_SECRET_KEY`

The registry URL signing key is hardcoded in `services/registry.py`. To rotate:

**Step 1** — Generate a new key:
```bash
openssl rand -hex 32
```

**Step 2** — Update the constant in `registry.py`:
```python
SIGNING_SECRET_KEY = b"<new-hex-key-value>"
```

**Step 3** — Restart the control plane server.

> [!WARNING]
> Any previously generated signed download URLs will become invalid immediately after rotation. Notify operators to re-generate download URLs after rotation.

### Future: Externalise Secrets
Both secrets should be moved out of source code before production:
- Load `SIGNING_SECRET_KEY` from `config.json` or an environment variable (`CERYNIX_SIGNING_SECRET`).
- Use a secrets manager (e.g., HashiCorp Vault, Google Secret Manager) for production deployments.
