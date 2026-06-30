from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional, List
from services.auth import verify_token
from services.registry import (
    register_artifact_metadata, approve_artifact_version, 
    get_approved_catalog, generate_signed_download_url
)

router = APIRouter(prefix="/api/v1")

# Device-Facing Router
@router.get("/registry/catalog")
def get_catalog(type: Optional[str] = None):
    """Device-facing endpoint to fetch the approved versions catalog list."""
    try:
        return get_approved_catalog(type_filter=type)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

@router.get("/registry/artifacts/{artifact_id}/download")
def download_artifact(artifact_id: str, expires: Optional[int] = 900):
    """Device-facing endpoint to retrieve a secure signed download URL for an approved artifact."""
    try:
        signed_url = generate_signed_download_url(artifact_id, expiration_seconds=expires)
        if not signed_url:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact not found.")
        return {"artifact_id": artifact_id, "signed_url": signed_url}
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))

# Admin Observability/Registry Router
admin_router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_token)])

class RegisterArtifactRequest(BaseModel):
    artifact_id: str
    name: str
    type: str
    version: str
    description: Optional[str] = None
    filename: str
    file_size_bytes: int = Field(..., ge=0)
    checksum_sha256: str
    download_url: str
    signature: str

class ApproveArtifactRequest(BaseModel):
    status: str

@admin_router.post("/registry/artifacts", status_code=status.HTTP_201_CREATED)
def register_artifact(payload: RegisterArtifactRequest):
    """Admin-only: registers metadata specifications for a release target."""
    try:
        art = register_artifact_metadata(
            payload.artifact_id, payload.name, payload.type, payload.version, payload.description,
            payload.filename, payload.file_size_bytes, payload.checksum_sha256, payload.download_url, payload.signature
        )
        return art
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

@admin_router.patch("/registry/artifacts/{artifact_id}/approve")
def approve_artifact(artifact_id: str, payload: ApproveArtifactRequest):
    """Admin-only: updates approval status to include/exclude from device catalogs."""
    try:
        art = approve_artifact_version(artifact_id, payload.status)
        if not art:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact not found.")
        return art
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
