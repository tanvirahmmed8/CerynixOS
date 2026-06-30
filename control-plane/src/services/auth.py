"""
Auth Service — CerynixOS Control Plane

Assumptions and Limits:
- v1 uses a single static bearer token (from config.json) that maps to the 'admin' role.
- Role extraction from token is placeholder logic; future versions will verify signed JWTs.
- All tokens not matching the admin token are rejected with 401.
- Security events are emitted to the structured log stream alongside application logs.
- This module is security-sensitive: do not add magic defaults or silent fallbacks.
"""
import json
import logging
import time

from fastapi import HTTPException, Security, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from database.connection import load_config

logger = logging.getLogger("control-plane.security")

security = HTTPBearer()

# ─── Role Definitions ─────────────────────────────────────────────────────────
# Roles define what a caller is permitted to do.
# v1: All valid callers receive 'admin' role (single pilot token).
# Future: Extract role from JWT claims.

ROLES = {
    "admin": {
        "description": "Full access: fleet management, policies, updates, audit, registry.",
        "permissions": [
            "device:read", "device:write",
            "enrollment:write",
            "policy:read", "policy:write",
            "update:read", "update:write",
            "governance:read", "governance:write",
            "observability:read",
            "registry:read", "registry:write",
            "support:read", "support:write",
        ]
    },
    "operator": {
        "description": "Read-only fleet view plus incident management.",
        "permissions": [
            "device:read",
            "policy:read",
            "update:read",
            "governance:read",
            "observability:read",
            "registry:read",
            "support:read", "support:write",
        ]
    },
    "device-agent": {
        "description": "Device plane only — enrollment, health ingest, audit ingest, update check.",
        "permissions": [
            "enrollment:write",
            "device:health_ingest",
            "governance:audit_ingest",
            "update:check",
            "support:bundle_upload",
            "diagnostics:poll",
            "diagnostics:results",
        ]
    },
    "readonly": {
        "description": "Read-only view across all resources. No mutations.",
        "permissions": [
            "device:read",
            "policy:read",
            "update:read",
            "governance:read",
            "observability:read",
            "registry:read",
        ]
    }
}


# ─── Token → Role Mapping ─────────────────────────────────────────────────────
# v1: Static mapping. Pilot admin token maps to 'admin' role.
# Future: Parse and verify signed JWT, extract `role` claim.

def get_api_token() -> str:
    """Load the expected API token from config."""
    config = load_config()
    return config.get("api_token", "token_cerynix_secret_key_2026")


def get_role_for_token(token: str) -> str | None:
    """
    Maps a token to a role string.

    v1: Only the configured admin token is accepted, returning 'admin'.
    Returns None if the token does not map to any known role.

    Future extension: Decode JWT, validate signature, return role claim.
    """
    expected_token = get_api_token()
    if token == expected_token:
        return "admin"
    return None


def has_permission(role: str, permission: str) -> bool:
    """Check whether a role grants a specific permission."""
    role_def = ROLES.get(role)
    if not role_def:
        return False
    return permission in role_def["permissions"]


# ─── Security Event Logging ───────────────────────────────────────────────────

def log_security_event(
    event_type: str,
    detail: str,
    severity: str = "WARNING",
    client_ip: str = "unknown",
    path: str = "unknown",
    role: str = None
) -> None:
    """
    Emit a structured security event to the log stream.

    Security events are separate from application request logs.
    They must always be emitted — never silenced.

    event_type examples:
      - auth_failure         Token missing or invalid
      - auth_success         Token validated successfully
      - role_violation       Valid token but insufficient role permissions
      - token_rotation       Admin triggered token rotation
      - suspicious_activity  Rate limit exceeded or anomalous request pattern
    """
    payload = {
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        "level": severity,
        "event_type": "security_event",
        "security_event_type": event_type,
        "detail": detail,
        "client_ip": client_ip,
        "path": path,
        "severity": severity,
    }
    if role:
        payload["role"] = role

    logger.warning(json.dumps(payload))


# ─── FastAPI Auth Dependencies ────────────────────────────────────────────────

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """
    FastAPI dependency: validates bearer token and returns it.

    Emits a security_event log on failure.
    Used by all admin and device-facing routes requiring auth.
    """
    token = credentials.credentials
    role = get_role_for_token(token)

    if role is None:
        log_security_event(
            event_type="auth_failure",
            detail="Rejected bearer token does not match any known identity.",
            severity="WARNING"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Bearer Token"
        )

    log_security_event(
        event_type="auth_success",
        detail=f"Token validated. Role: {role}.",
        severity="INFO",
        role=role
    )
    return token


def require_role(required_permission: str):
    """
    FastAPI dependency factory: requires a caller to hold a specific permission.

    Usage:
        @router.post("/admin/something", dependencies=[Depends(require_role("policy:write"))])

    v1: All admin tokens pass. Future: check decoded JWT role against ROLES table.
    """
    def _check(credentials: HTTPAuthorizationCredentials = Security(security)):
        token = credentials.credentials
        role = get_role_for_token(token)

        if role is None:
            log_security_event(
                event_type="auth_failure",
                detail=f"Rejected: unknown token attempted to access '{required_permission}'.",
                severity="WARNING"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API Bearer Token"
            )

        if not has_permission(role, required_permission):
            log_security_event(
                event_type="role_violation",
                detail=f"Role '{role}' does not have permission '{required_permission}'.",
                severity="ERROR",
                role=role
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: '{required_permission}'."
            )

        return token

    return _check
