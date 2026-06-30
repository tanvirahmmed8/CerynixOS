from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional
from services.auth import verify_token
from services.enrollment import create_enrollment_token, consume_enrollment_token
from services.inventory import register_or_update_device

router = APIRouter(prefix="/api/v1")

# Pydantic Schemas
class CreateTokenRequest(BaseModel):
    organization_id: str
    max_uses: Optional[int] = Field(default=1, ge=1)

class HardwareProfileSchema(BaseModel):
    cpu_cores: int = Field(ge=1)
    memory_bytes: int = Field(ge=0)
    storage_bytes: int = Field(ge=0)

class DeviceEnrollRequest(BaseModel):
    enrollment_token: str
    device_id: str
    device_model: str
    os_version: str
    hardware_profile: HardwareProfileSchema
    installed_capabilities: List[str]

@router.post("/enrollment-tokens", status_code=status.HTTP_201_CREATED)
def generate_token(payload: CreateTokenRequest, admin_token: str = Depends(verify_token)):
    """Admin-only endpoint to generate a new enrollment token."""
    token_details = create_enrollment_token(payload.organization_id, payload.max_uses)
    if not token_details:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate enrollment token."
        )
    return token_details

@router.post("/enroll", status_code=status.HTTP_200_OK)
def enroll_device(payload: DeviceEnrollRequest):
    """Public onboarding endpoint for new CerynixOS devices using an enrollment token."""
    # 1. Validate and consume token usage
    success = consume_enrollment_token(payload.enrollment_token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid, expired, or fully-consumed enrollment token."
        )
        
    # 2. Register the device spec in the inventory db
    device = register_or_update_device(
        device_id=payload.device_id,
        device_model=payload.device_model,
        os_version=payload.os_version,
        cpu_cores=payload.hardware_profile.cpu_cores,
        memory_bytes=payload.hardware_profile.memory_bytes,
        storage_bytes=payload.hardware_profile.storage_bytes,
        installed_capabilities=payload.installed_capabilities
    )
    
    return {
        "status": "enrolled",
        "device_id": device["device_id"],
        "message": "Device enrolled successfully"
    }
