import hmac
import hashlib
import re
from datetime import datetime, timezone, timedelta
from database.connection import get_db_connection

VALID_ARTIFACT_TYPES = {"system", "model", "plugin"}
VALID_APPROVAL_STATUSES = {"approved", "rejected", "deprecated"}
VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?$")
CHECKSUM_PATTERN = re.compile(r"^[a-fA-F0-9]{64}$")

SIGNING_SECRET_KEY = b"cerynix_registry_url_secure_signing_secret_key_2026"

def register_artifact_metadata(
    artifact_id: str,
    name: str,
    type: str,
    version: str,
    description: str,
    filename: str,
    file_size_bytes: int,
    checksum_sha256: str,
    download_url: str,
    signature: str
) -> dict:
    """Registers metadata for a new system binary, LLM model, or plugin package."""
    if type not in VALID_ARTIFACT_TYPES:
        raise ValueError(f"Invalid artifact type. Must be one of {VALID_ARTIFACT_TYPES}")
    if not VERSION_PATTERN.match(version):
        raise ValueError("Invalid version format. Must follow Semantic Versioning (e.g. 1.2.3)")
    if not CHECKSUM_PATTERN.match(checksum_sha256):
        raise ValueError("Invalid checksum format. Must be a 64-character SHA-256 hex string")
    
    # Placeholder signature verification check
    if not signature or not signature.startswith("dev_signature"):
        raise ValueError("Invalid cryptographic signature. Must start with 'dev_signature'")
        
    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO registry_artifacts (
                artifact_id, name, type, version, description, filename, file_size_bytes, checksum_sha256, download_url, signature, approval_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending');
            """,
            (artifact_id, name, type, version, description, filename, file_size_bytes, checksum_sha256, download_url, signature)
        )
        
        cursor = conn.execute("SELECT * FROM registry_artifacts WHERE artifact_id = ?;", (artifact_id,))
        return dict(cursor.fetchone())

def approve_artifact_version(artifact_id: str, status: str) -> dict:
    """Promotes or rejects a registered artifact version for deployment compatibility catalog inclusion."""
    if status not in VALID_APPROVAL_STATUSES:
        raise ValueError(f"Invalid approval status. Must be one of {VALID_APPROVAL_STATUSES}")
        
    with get_db_connection() as conn:
        conn.execute(
            "UPDATE registry_artifacts SET approval_status = ?, updated_at = CURRENT_TIMESTAMP WHERE artifact_id = ?;",
            (status, artifact_id)
        )
        
        cursor = conn.execute("SELECT * FROM registry_artifacts WHERE artifact_id = ?;", (artifact_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return dict(row)

def get_approved_catalog(type_filter: str = None) -> list:
    """Queries the catalog for approved system profiles, plugins, or AI model releases."""
    query = "SELECT * FROM registry_artifacts WHERE approval_status = 'approved'"
    params = []
    
    if type_filter:
        if type_filter not in VALID_ARTIFACT_TYPES:
            raise ValueError(f"Invalid type filter. Must be one of {VALID_ARTIFACT_TYPES}")
        query += " AND type = ?"
        params.append(type_filter)
        
    query += " ORDER BY name ASC, version DESC;"
    
    with get_db_connection() as conn:
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def generate_signed_download_url(artifact_id: str, expiration_seconds: int = 900) -> str:
    """Generates a secure, time-bound download URL utilizing SHA256 HMAC code signature simulation."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT download_url, approval_status FROM registry_artifacts WHERE artifact_id = ?;", (artifact_id,))
        row = cursor.fetchone()
        if not row:
            return None
        if row["approval_status"] != "approved":
            raise PermissionError("Cannot sign download URLs for non-approved registry items.")
            
        base_url = row["download_url"]
        
    # Generate timestamp expiry parameter (UTC epoch timestamp)
    expiry = int((datetime.now(timezone.utc) + timedelta(seconds=expiration_seconds)).timestamp())
    
    # Calculate HMAC signature over artifact path and expiry
    msg = f"{artifact_id}:{expiry}".encode("utf-8")
    sig = hmac.new(SIGNING_SECRET_KEY, msg, hashlib.sha256).hexdigest()
    
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}expires={expiry}&signature={sig}"

def verify_signed_url(artifact_id: str, expires: int, signature: str) -> bool:
    """Validates if a signed download URL query parameter parameters are still valid and unexpired."""
    now = int(datetime.now(timezone.utc).timestamp())
    if now > expires:
        return False
        
    msg = f"{artifact_id}:{expires}".encode("utf-8")
    expected_sig = hmac.new(SIGNING_SECRET_KEY, msg, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_sig, signature)
