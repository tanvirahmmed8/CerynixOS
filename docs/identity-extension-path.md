# Identity Extension Path — CerynixOS Control Plane

## Scope

This document maps the evolution of CerynixOS authentication from the v1 pilot static token to production-grade SSO and TPM-backed device identity. It identifies the exact code extension points so future engineers can upgrade auth without disrupting existing routes.

---

## Identity Evolution Roadmap

```
v1 (Pilot)                    v2 (Production)                  v3 (Enterprise)
──────────────────────────    ─────────────────────────────    ────────────────────────────
Static shared bearer token    JWT + OIDC SSO (Google/Okta)     TPM-backed device certs
All callers → "admin" role    Role extracted from JWT claims    Device identity from TPM
config.json token store       OIDC provider as IdP             CerynixOS PKI as CA
```

---

## Stage 1 → Stage 2: Static Token → OIDC JWT SSO

### What Changes

| Component | v1 | v2 |
|---|---|---|
| Token format | Opaque static string | Signed JWT (`RS256`) |
| Token source | `config.json` | OIDC provider (Google, Okta, Azure AD) |
| Role extraction | Hardcoded `admin` | `role` claim in JWT payload |
| Token validation | String equality | `jwt.decode(token, public_key, algorithms=["RS256"])` |

### Code Extension Points (Minimal Changes)

**`services/auth.py` — `get_role_for_token(token)`**

```python
# v1 (current)
def get_role_for_token(token: str) -> str | None:
    if token == get_api_token():
        return "admin"
    return None

# v2 replacement
import jwt
OIDC_PUBLIC_KEY = load_oidc_public_key()

def get_role_for_token(token: str) -> str | None:
    try:
        claims = jwt.decode(token, OIDC_PUBLIC_KEY, algorithms=["RS256"],
                            audience="cerynix-control-plane")
        return claims.get("role")  # "admin", "operator", "readonly"
    except jwt.ExpiredSignatureError:
        log_security_event("auth_failure", "JWT token expired.")
        return None
    except jwt.InvalidTokenError:
        log_security_event("auth_failure", "JWT signature invalid.")
        return None
```

No changes to any route handler, middleware, or dependency injection. All role-gating logic in `require_role()` automatically works with the new role values.

### Dashboard Changes
Update `app.js` auth flow:
1. Replace token text input with an OIDC redirect (`window.location = provider_auth_url`).
2. Exchange OIDC `code` for a JWT via a `/auth/token` endpoint.
3. Store JWT in `sessionStorage` (not `localStorage`; shorter TTL).

---

## Stage 2 → Stage 3: OIDC JWT → TPM-Backed Device Certificates

### What Changes

Device authentication moves from shared tokens to per-device X.509 certificates stored in the device's TPM. Operator (human) authentication remains OIDC JWT.

### Code Extension Points

**`services/auth.py` — Add `verify_device_cert(cert_pem)`**

```python
import ssl, datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend

ROOT_CA_CERT = load_root_ca()

def verify_device_cert(cert_pem: bytes) -> str | None:
    """
    Verifies a device X.509 cert against the Root CA.
    Returns device_id (CN) on success, None on failure.
    """
    try:
        cert = x509.load_pem_x509_certificate(cert_pem, default_backend())
        # Check expiry
        if cert.not_valid_after_utc < datetime.datetime.now(datetime.timezone.utc):
            log_security_event("auth_failure", "Device certificate expired.")
            return None
        # Check issuer chain (simplified — production needs full chain validation)
        if cert.issuer != ROOT_CA_CERT.subject:
            log_security_event("auth_failure", "Certificate issuer does not match Root CA.")
            return None
        return cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
    except Exception as e:
        log_security_event("auth_failure", f"Certificate parse error: {e}")
        return None
```

**`routes/enrollment.py` — Accept `X-Device-Cert` header**

```python
@router.post("/enrollment/enroll")
def enroll_device(request: Request, payload: EnrollmentRequest):
    cert_pem = request.headers.get("X-Device-Cert", "").encode()
    device_id = verify_device_cert(cert_pem)
    if not device_id:
        raise HTTPException(status_code=401, detail="Invalid device certificate.")
    # Proceed with existing enrollment logic using verified device_id
```

---

## Summary: Extension Points Table

| Upgrade | File | Function/Class | Change Type |
|---|---|---|---|
| Static → JWT OIDC | `services/auth.py` | `get_role_for_token()` | Replace body |
| Static → JWT OIDC | `static/app.js` | Auth modal section | Add OIDC redirect flow |
| JWT → Device Cert | `services/auth.py` | New `verify_device_cert()` | Add function |
| JWT → Device Cert | `routes/enrollment.py` | `enroll_device()` | Add cert header check |
| Any stage | `services/auth.py` | `ROLES` dict | Add/update roles |

All route handlers, middleware, and the RBAC permission model require **zero changes** across all upgrade stages.
