from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional
from services.auth import verify_token
from services.update import (
    create_release, get_releases, get_release, create_campaign, 
    list_campaigns, get_campaign, pause_campaign, resume_campaign, 
    rollback_campaign, check_device_update, update_device_campaign_status, 
    get_compliance_metrics
)

router = APIRouter(prefix="/api/v1")

# Pydantic Request Models
class CreateReleaseRequest(BaseModel):
    release_id: str
    version: str
    channel: str
    image_url: str
    sha256_hash: str
    force_rollback: Optional[bool] = False

class CreateCampaignRequest(BaseModel):
    campaign_id: str
    release_id: str
    name: str
    target_group_ids: Optional[List[str]] = []
    target_device_ids: Optional[List[str]] = []
    rollout_percentage: Optional[int] = Field(100, ge=0, le=100)

class ReportStatusRequest(BaseModel):
    campaign_id: str
    status: str

# Device-Facing routes (Public update-check and reporting endpoints)
@router.get("/devices/{device_id}/updates/check")
def check_for_updates(device_id: str):
    """Device-facing endpoint to query if any active/rolled back update campaign applies."""
    res = check_device_update(device_id)
    # If device not found or unregistered
    if res.get("message") == "Device not enrolled.":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=res["message"]
        )
    return res

@router.post("/devices/{device_id}/updates/status")
def report_update_progress(device_id: str, payload: ReportStatusRequest):
    """Device-facing endpoint to report progress/completion of an update installation."""
    try:
        updated = update_device_campaign_status(device_id, payload.campaign_id, payload.status)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device target record for campaign '{payload.campaign_id}' not found."
            )
        return {"status": "updated", "target": updated}
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

# Admin Update Orchestration Router (requires verify_token)
admin_router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_token)])

@admin_router.post("/updates/releases", status_code=status.HTTP_201_CREATED)
def register_release(payload: CreateReleaseRequest):
    """Admin-only endpoint to register a new base OS release."""
    try:
        release = create_release(
            payload.release_id, payload.version, payload.channel, 
            payload.image_url, payload.sha256_hash, payload.force_rollback
        )
        return release
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

@admin_router.get("/updates/releases")
def list_all_releases():
    """Admin-only endpoint to list all releases."""
    return get_releases()

@admin_router.post("/updates/campaigns", status_code=status.HTTP_201_CREATED)
def launch_update_campaign(payload: CreateCampaignRequest):
    """Admin-only endpoint to launch a staged update rollout campaign."""
    try:
        campaign = create_campaign(
            payload.campaign_id, payload.release_id, payload.name, 
            payload.target_group_ids, payload.target_device_ids, payload.rollout_percentage
        )
        return campaign
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except KeyError as ke:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ke))

@admin_router.get("/updates/campaigns")
def list_all_campaigns():
    """Admin-only endpoint to list campaigns."""
    return list_campaigns()

@admin_router.get("/updates/campaigns/{campaign_id}")
def get_campaign_by_id(campaign_id: str):
    """Admin-only endpoint to retrieve campaign details and target metrics."""
    campaign = get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign '{campaign_id}' not found."
        )
    return campaign

@admin_router.post("/updates/campaigns/{campaign_id}/pause")
def pause_rollout(campaign_id: str):
    """Admin-only endpoint to suspend campaign update deliveries."""
    campaign = pause_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found.")
    return campaign

@admin_router.post("/updates/campaigns/{campaign_id}/resume")
def resume_rollout(campaign_id: str):
    """Admin-only endpoint to resume update deliveries."""
    campaign = resume_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found.")
    return campaign

@admin_router.post("/updates/campaigns/{campaign_id}/rollback")
def force_campaign_rollback(campaign_id: str):
    """Admin-only endpoint to flag the campaign as rolled back, sending rollback directives to targets."""
    campaign = rollback_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found.")
    return campaign

@admin_router.get("/updates/compliance")
def get_compliance_dashboard():
    """Admin-only endpoint to retrieve patch compliance statistics."""
    return get_compliance_metrics()
