from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional
from services.auth import verify_token
from services.inventory import get_device
from services.policy import (
    validate_policy_rules, create_or_update_policy, get_policy, 
    list_policy_revisions, assign_policy, rollback_policy_to_version, 
    resolve_policy_for_device
)

router = APIRouter(prefix="/api/v1")

# Pydantic Schemas
class PolicyRulesSchema(BaseModel):
    allowed_tools: List[str]
    approval_mode: str

class SavePolicyRequest(BaseModel):
    policy_id: str
    rules: PolicyRulesSchema

class AssignPolicyRequest(BaseModel):
    target_type: str
    target_id: Optional[str] = None

class RollbackPolicyRequest(BaseModel):
    version: int = Field(ge=1)

# Device-facing resolved policy endpoint (Public / Checked ID)
@router.get("/devices/{device_id}/policy")
def get_device_policy(device_id: str):
    """Device-facing endpoint to resolve and retrieve active policy settings using Device > Group > Global precedence."""
    # Validate device exists first to prevent unauthorized access
    device = get_device(device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device '{device_id}' is not enrolled in the control plane."
        )
    return resolve_policy_for_device(device_id)

# Admin Operations Router (requires verify_token)
admin_router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_token)])

@admin_router.post("/policies", status_code=status.HTTP_201_CREATED)
def save_policy(payload: SavePolicyRequest):
    """Admin-only endpoint to create or update policy rules, creating a new revision version."""
    try:
        policy = create_or_update_policy(payload.policy_id, payload.rules.dict())
        return policy
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

@admin_router.post("/policies/dry-run")
def dry_run_policy(payload: PolicyRulesSchema):
    """Admin-only endpoint to validate policy rules structure without saving them."""
    try:
        validate_policy_rules(payload.dict())
        return {"status": "valid", "message": "Policy rules structure is valid."}
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

@admin_router.get("/policies/{policy_id}")
def get_policy_by_id(policy_id: str):
    """Admin-only endpoint to fetch active policy metadata."""
    policy = get_policy(policy_id)
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Policy '{policy_id}' not found."
        )
    return policy

@admin_router.get("/policies/{policy_id}/revisions")
def get_revisions(policy_id: str):
    """Admin-only endpoint to view policy history and versions."""
    # Ensure policy exists
    get_policy_by_id(policy_id)
    return list_policy_revisions(policy_id)

@admin_router.post("/policies/{policy_id}/assign")
def set_policy_assignment(policy_id: str, payload: AssignPolicyRequest):
    """Admin-only endpoint to assign policy to global, group, or device scopes."""
    try:
        assignment = assign_policy(policy_id, payload.target_type, payload.target_id)
        return assignment
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except KeyError as ke:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ke))

@admin_router.post("/policies/{policy_id}/rollback")
def rollback_policy(policy_id: str, payload: RollbackPolicyRequest):
    """Admin-only endpoint to rollback policy configuration to a past version number."""
    try:
        policy = rollback_policy_to_version(policy_id, payload.version)
        return policy
    except KeyError as ke:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ke))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
