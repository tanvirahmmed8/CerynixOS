# Endpoint Security Review — CerynixOS Control Plane

This document reviews all exposed HTTP endpoints for authentication requirements, permission scope, and abuse risk.

---

## Legend

- ✅ **Auth Required** — Bearer token verified on every request
- ⚠️ **Open** — No authentication required (device-facing or health check)
- 🔒 **Admin Only** — Requires admin token; not callable by unauthenticated clients

---

## Health Routes (`routes/health.py`)

| Method | Path | Auth | Risk Notes |
|---|---|---|---|
| `GET` | `/api/v1/health` | ⚠️ Open | Safe — returns basic server status. No sensitive data exposed. Acceptable. |
| `GET` | `/api/v1/health/ready` | ⚠️ Open | Same as above. Consider returning generic `{"status": "ok"}` only. |

---

## Enrollment Routes (`routes/enrollment.py`)

| Method | Path | Auth | Risk Notes |
|---|---|---|---|
| `POST` | `/api/v1/enrollment/enroll` | ✅ Auth Required | **Abuse Risk**: An attacker with a valid token could flood device records. Recommend device-ID uniqueness enforcement + rate limiting. |

---

## Device Routes (`routes/devices.py`)

| Method | Path | Auth | Risk Notes |
|---|---|---|---|
| `GET` | `/api/v1/devices` | ✅ Auth Required | Returns full device list. Scoped to authenticated callers only. ✓ |
| `GET` | `/api/v1/devices/{device_id}` | ✅ Auth Required | Single device lookup. ✓ |
| `PATCH` | `/api/v1/devices/{device_id}` | ✅ Auth Required | State transitions enforced by `VALID_STATE_TRANSITIONS`. ✓ |
| `POST` | `/api/v1/devices/{device_id}/health` | ✅ Auth Required | Health ingest. **Note**: v2 should restrict to device-agent role only. |
| `GET` | `/api/v1/devices/{device_id}/updates/check` | ✅ Auth Required | Update eligibility check. ✓ |
| `POST` | `/api/v1/devices/{device_id}/updates/status` | ✅ Auth Required | Update status report. ✓ |
| `GET` | `/api/v1/devices/{device_id}/timeline` | ✅ Auth Required | Audit timeline. ✓ |
| `POST` | `/api/v1/devices/{device_id}/diagnostics/execute` | ✅ Auth Required | **High Risk**: Enqueues remote command. Must remain admin-only. Never expose to device-agent role. |
| `GET` | `/api/v1/devices/{device_id}/diagnostics/pending` | ✅ Auth Required | Device polls pending commands. v2: restrict to `device-agent` role only. |
| `POST` | `/api/v1/devices/{device_id}/diagnostics/results` | ✅ Auth Required | Device submits command output. v2: restrict to `device-agent` role only. |
| `POST` | `/api/v1/devices/{device_id}/simulate-failure` | ✅ Auth Required | **Admin Only**: Synthetic failure injection. Must never be exposed to device agents. |

---

## Policy Routes (`routes/policies.py`)

| Method | Path | Auth | Risk Notes |
|---|---|---|---|
| `GET` | `/api/v1/policies` | ✅ Auth Required | ✓ |
| `POST` | `/api/v1/policies` | ✅ Auth Required | ✓ |
| `GET` | `/api/v1/policies/{policy_id}` | ✅ Auth Required | ✓ |
| `POST` | `/api/v1/policies/{policy_id}/assign` | ✅ Auth Required | ✓ |
| `GET` | `/api/v1/devices/{device_id}/policy` | ✅ Auth Required | ✓ |

---

## Update Routes (`routes/updates.py`)

| Method | Path | Auth | Risk Notes |
|---|---|---|---|
| `GET` | `/api/v1/updates/releases` | ✅ Auth Required | ✓ |
| `POST` | `/api/v1/updates/releases` | ✅ Auth Required | Admin-only creation. ✓ |
| `GET` | `/api/v1/updates/campaigns` | ✅ Auth Required | ✓ |
| `POST` | `/api/v1/updates/campaigns` | ✅ Auth Required | ✓ |
| `POST` | `/api/v1/updates/campaigns/{id}/pause` | ✅ Auth Required | ✓ |
| `POST` | `/api/v1/updates/campaigns/{id}/resume` | ✅ Auth Required | ✓ |
| `POST` | `/api/v1/updates/campaigns/{id}/rollback` | ✅ Auth Required | **High Risk**: Triggers fleet-wide rollback. Must remain strictly admin-only. |
| `GET` | `/api/v1/updates/compliance` | ✅ Auth Required | ✓ |

---

## Governance Routes (`routes/governance.py`)

| Method | Path | Auth | Risk Notes |
|---|---|---|---|
| `POST` | `/api/v1/devices/{device_id}/audit/ingest` | ✅ Auth Required | Device-facing. v2: restrict to `device-agent` role only. |
| `GET` | `/api/v1/audit/events` | ✅ Auth Required | ✓ |
| `POST` | `/api/v1/audit/verify` | ✅ Auth Required | Cryptographic scan. CPU-intensive — rate limit recommended. |
| `GET` | `/api/v1/compliance/posture` | ✅ Auth Required | ✓ |
| `GET` | `/api/v1/compliance/export/{type}` | ✅ Auth Required | Returns bulk data. Add pagination before production. |

---

## Observability Routes (`routes/observability.py`)

| Method | Path | Auth | Risk Notes |
|---|---|---|---|
| `POST` | `/api/v1/devices/{device_id}/health/ingest` | ✅ Auth Required | v2: device-agent role only. |
| `GET` | `/api/v1/observability/fleet` | ✅ Auth Required | ✓ |
| `GET` | `/api/v1/observability/alerts` | ✅ Auth Required | ✓ |
| `GET` | `/api/v1/support/incidents` | ✅ Auth Required | ✓ |
| `POST` | `/api/v1/support/incidents` | ✅ Auth Required | ✓ |
| `PATCH` | `/api/v1/support/incidents/{id}` | ✅ Auth Required | ✓ |
| `POST` | `/api/v1/support/bundles` | ✅ Auth Required | ✓ |
| `GET` | `/api/v1/support/bundles` | ✅ Auth Required | ✓ |

---

## Registry Routes (`routes/registry.py`)

| Method | Path | Auth | Risk Notes |
|---|---|---|---|
| `POST` | `/api/v1/registry/artifacts` | ✅ Auth Required | Signature validation enforced. ✓ |
| `PATCH` | `/api/v1/registry/artifacts/{id}/approve` | ✅ Auth Required | **High Risk**: Promotes artifacts to approved catalog. Strictly admin-only. |
| `GET` | `/api/v1/registry/catalog` | ✅ Auth Required | ✓ |
| `GET` | `/api/v1/registry/artifacts/{id}/download` | ✅ Auth Required | Returns signed URL. Approval status checked before signing. ✓ |

---

## Summary: Priority Actions Before Production

1. **Separate device-agent and admin roles**: Routes marked "v2: restrict to device-agent role" should use `Depends(require_role("device:health_ingest"))` etc.
2. **Add CORS policy**: Restrict `allow_origins` to your production domain.
3. **Rate limit `/audit/verify`**: Cryptographic scan is CPU-bound. Limit to 1 req/minute per IP.
4. **Paginate bulk exports**: `/compliance/export/{type}` returns unbounded data.
5. **Run `pip-audit`**: Verify no known CVEs in dependencies.
