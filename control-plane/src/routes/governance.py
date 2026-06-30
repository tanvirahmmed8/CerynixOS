from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict, Any
from services.auth import verify_token
from services.inventory import get_device
from services.governance import (
    ingest_audit_event, get_audit_events, verify_audit_chain, 
    get_compliance_posture, export_evidence
)

router = APIRouter(prefix="/api/v1")

# Pydantic Schemas
class IngestAuditEventRequest(BaseModel):
    event_id: str
    timestamp: str
    service: str
    action: str
    status: str
    details: Optional[Dict[str, Any]] = None

# Device-Facing Route (Audit Ingestion)
@router.post("/devices/{device_id}/audit/ingest", status_code=status.HTTP_201_CREATED)
def report_audit_event(device_id: str, payload: IngestAuditEventRequest):
    """Device-facing endpoint to submit local audit log records for persistent storage."""
    # Ensure device exists
    device = get_device(device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device '{device_id}' is not enrolled in the control plane."
        )
        
    try:
        saved = ingest_audit_event(
            device_id, payload.event_id, payload.timestamp, 
            payload.service, payload.action, payload.status, payload.details
        )
        return saved
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

# Admin Governance Operations (requires verify_token)
admin_router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_token)])

@admin_router.get("/audit")
def list_logs(device_id: Optional[str] = None, service: Optional[str] = None, log_status: Optional[str] = None):
    """Admin-only endpoint to retrieve the logs."""
    return get_audit_events(device_id, service, log_status)

@admin_router.post("/audit/verify")
def run_audit_verification():
    """Admin-only endpoint to check the cryptographic integrity of the audit logs chain."""
    return verify_audit_chain()

@admin_router.get("/compliance/posture")
def get_posture_summary():
    """Admin-only endpoint to retrieve active patches/health baseline compliance score."""
    return get_compliance_posture()

@admin_router.get("/compliance/export/{report_type}")
def get_report_export(report_type: str):
    """Admin-only endpoint to fetch evidence report datasets (inventory, updates, policies, audit)."""
    try:
        records = export_evidence(report_type)
        return records
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
