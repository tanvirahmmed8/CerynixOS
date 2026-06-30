from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional
from services.auth import verify_token
from services.inventory import (
    get_device, list_devices, update_device_state, 
    update_device_group_and_tags, create_device_group, list_device_groups
)

router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_token)])

# Pydantic Schemas
class CreateGroupRequest(BaseModel):
    group_id: str
    name: str
    description: Optional[str] = None

class UpdateDeviceRequest(BaseModel):
    enrollment_state: Optional[str] = None
    group_id: Optional[str] = None
    tags: Optional[List[str]] = None

@router.get("/devices")
def get_devices(
    state: Optional[str] = None,
    group_id: Optional[str] = None,
    tag: Optional[str] = None,
    channel: Optional[str] = None,
    query: Optional[str] = None
):
    """Admin-only endpoint to search and filter devices in the fleet."""
    return list_devices(
        filter_state=state,
        filter_group=group_id,
        filter_tag=tag,
        filter_channel=channel,
        query_text=query
    )

@router.get("/devices/{device_id}")
def get_device_by_id(device_id: str):
    """Admin-only endpoint to fetch a single device details."""
    device = get_device(device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device '{device_id}' not found."
        )
    return device

@router.patch("/devices/{device_id}")
def modify_device(device_id: str, payload: UpdateDeviceRequest):
    """Admin-only endpoint to update group membership, tags, or transition device enrollment state."""
    # 1. State transition
    if payload.enrollment_state is not None:
        try:
            update_device_state(device_id, payload.enrollment_state)
        except ValueError as ve:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
        except KeyError as ke:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ke))
            
    # 2. Group & tag update
    if payload.group_id is not None or payload.tags is not None:
        try:
            update_device_group_and_tags(device_id, payload.group_id, payload.tags)
        except KeyError as ke:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ke))
            
    return get_device_by_id(device_id)

@router.post("/device-groups", status_code=status.HTTP_201_CREATED)
def add_device_group(payload: CreateGroupRequest):
    """Admin-only endpoint to register a new device group."""
    try:
        group = create_device_group(payload.group_id, payload.name, payload.description)
        return group
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create group. Check constraints (e.g. unique name). Error: {str(e)}"
        )

@router.get("/device-groups")
def get_device_groups():
    """Admin-only endpoint to list all registered device groups."""
    return list_device_groups()
