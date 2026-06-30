# Backend Hardening Checklist — CerynixOS Control Plane

This checklist defines the security hardening baseline for the CerynixOS Control Plane before pilot customer onboarding. Each item must be verified before a production promotion.

---

## 1. Authentication Surface

| Check | Status | Notes |
|---|---|---|
| All admin routes require bearer token | ✅ Done | `Depends(verify_token)` on all admin/device routers |
| Auth failures emit security events | ✅ Done | `log_security_event("auth_failure", ...)` in `auth.py` |
| Token is not hardcoded in source | ⚠️ Pilot | `config.json` — must move to secrets manager pre-production |
| Tokens are rotatable without downtime | ✅ Done | Rotation procedure documented in `secret-rotation.md` |
| JWT/certificate auth extension point defined | ✅ Done | `auth.get_role_for_token()` is the sole extension point |

---

## 2. Role-Based Access Control

| Check | Status | Notes |
|---|---|---|
| RBAC role model defined | ✅ Done | `ROLES` + `PERMISSIONS` in `auth.py` |
| Role violation logging | ✅ Done | `log_security_event("role_violation", ...)` |
| `require_role()` dependency factory available | ✅ Done | Use for future fine-grained route gating |
| All pilot routes enforced under `admin` role | ✅ Done | v1: token → admin role |

---

## 3. Input Validation

| Check | Status | Notes |
|---|---|---|
| Pydantic models on all POST/PATCH bodies | ✅ Done | All route handlers use Pydantic `BaseModel` |
| SHA-256 checksum format validated on registry upload | ✅ Done | `CHECKSUM_PATTERN` regex in `registry.py` |
| Semantic version format validated | ✅ Done | `VERSION_PATTERN` regex in `registry.py` |
| Artifact type enum validated | ✅ Done | `VALID_ARTIFACT_TYPES` set check |
| SQL injection protected | ✅ Done | All DB queries use parameterised `?` placeholders |
| Device state transitions validated | ✅ Done | `VALID_STATE_TRANSITIONS` state machine in `inventory.py` |

---

## 4. Response Security Headers

| Header | Status | Value |
|---|---|---|
| `X-Content-Type-Options` | ✅ Done | `nosniff` |
| `X-Frame-Options` | ✅ Done | `DENY` |
| `Referrer-Policy` | ✅ Done | `strict-origin-when-cross-origin` |
| `X-XSS-Protection` | ✅ Done | `1; mode=block` |
| `Content-Security-Policy` | ✅ Done | Restrictive CSP in `SecurityHeadersMiddleware` |
| `Permissions-Policy` | ✅ Done | Geo, mic, camera disabled |

---

## 5. Rate Limiting

| Check | Status | Notes |
|---|---|---|
| Per-IP sliding window rate limiter active | ✅ Done | 120 req/60s in `RateLimitMiddleware` |
| Rate limit events logged as security events | ✅ Done | `suspicious_activity` event type |
| Static files exempt from rate limiting | ✅ Done | `RATE_LIMIT_EXEMPT_PATHS` set |
| Multi-process rate limiting | ❌ Not Done | In-memory only — Redis required before horizontal scaling |

---

## 6. Error Exposure

| Check | Status | Notes |
|---|---|---|
| Internal stack traces not returned in API responses | ✅ Done | FastAPI returns `detail` only; no raw exceptions |
| 404 responses don't reveal internal paths | ✅ Done | Generic "not found" messages |
| Auth failures return generic messages | ✅ Done | "Invalid or missing API Bearer Token" |

---

## 7. Logging Completeness

| Check | Status | Notes |
|---|---|---|
| All requests logged (method, path, status, duration) | ✅ Done | `CorrelationAndLoggingMiddleware` |
| Correlation IDs on every request | ✅ Done | `X-Correlation-ID` header propagated |
| Security events in structured log stream | ✅ Done | `log_security_event()` in `auth.py` |
| Audit events stored in tamper-evident chain | ✅ Done | SHA-256 chained ledger in `governance.py` |
| PII/secret redaction in audit logs | ✅ Done | `audit_redact_fields` in `config.json` |

---

## 8. Secret Management

| Check | Status | Notes |
|---|---|---|
| `api_token` not in source code | ✅ Done | Loaded from `config.json` at runtime |
| `SIGNING_SECRET_KEY` externalisable | ⚠️ Pilot | Hardcoded in `registry.py` — move to config pre-production |
| Secret rotation procedure documented | ✅ Done | `docs/secret-rotation.md` |
| Secrets never logged | ✅ Done | Redact fields configured; no explicit secret logging |

---

## 9. Dependency and Dependency Scanning

| Check | Status | Notes |
|---|---|---|
| Dependencies listed | ✅ Done | `fastapi`, `uvicorn`, `pydantic`, stdlib only |
| Dependency vulnerability scan | ❌ Not Done | Run `pip-audit` or `safety check` before production |
| No unnecessary dependencies | ✅ Done | Minimal dependency footprint |

---

## 10. CORS Policy

| Check | Status | Notes |
|---|---|---|
| CORS policy configured | ⚠️ Default | FastAPI default (permissive) — add `CORSMiddleware` with `allow_origins=["https://your-domain.com"]` before production |
