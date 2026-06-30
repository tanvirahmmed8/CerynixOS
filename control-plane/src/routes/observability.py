from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from services.auth import verify_token
from services.inventory import get_device
from services.observability import (
    ingest_health_snapshot, get_fleet_health_overview, get_active_alerts,
    register_support_bundle, get_support_bundles, create_incident, 
    update_incident, get_incidents, enqueue_diagnostic_command, 
    poll_pending_command, report_command_results, get_diagnostic_history,
    get_device_timeline, get_unhealthy_devices_workflow, simulate_device_failure
)

router = APIRouter(prefix="/api/v1")

# Pydantic Schemas
class HealthComponents(BaseModel):
    cpu: str
    memory: str
    storage: str
    services: str

class IngestHealthRequest(BaseModel):
    snapshot_id: str
    timestamp: str
    health_score: int = Field(..., ge=0, le=100)
    components: HealthComponents

class SupportBundleRequest(BaseModel):
    bundle_id: str
    timestamp: str
    bundle_size_bytes: int = Field(..., ge=0)
    bundle_url: str
    trigger_reason: str
    redaction_applied: Optional[bool] = True
    metadata: Optional[Dict[str, Any]] = None

class ReportDiagnosticResultsRequest(BaseModel):
    command_id: str
    status: str
    output: str

# Device-Facing Routes
@router.post("/devices/{device_id}/health/ingest", status_code=status.HTTP_201_CREATED)
def report_health(device_id: str, payload: IngestHealthRequest):
    """Device-facing endpoint to submit telemetry and health snapshot metrics."""
    device = get_device(device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not enrolled.")
    try:
        snap = ingest_health_snapshot(
            device_id, payload.snapshot_id, payload.timestamp, payload.health_score,
            payload.components.cpu, payload.components.memory, payload.components.storage, payload.components.services
        )
        return snap
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

@router.post("/devices/{device_id}/support-bundles", status_code=status.HTTP_201_CREATED)
def submit_support_bundle(device_id: str, payload: SupportBundleRequest):
    """Device-facing endpoint to register support bundle upload packages."""
    device = get_device(device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not enrolled.")
    bundle = register_support_bundle(
        device_id, payload.bundle_id, payload.timestamp, payload.bundle_size_bytes,
        payload.bundle_url, payload.trigger_reason, payload.redaction_applied, payload.metadata
    )
    return bundle

@router.get("/devices/{device_id}/diagnostics/pending")
def check_pending_diagnostics(device_id: str):
    """Device-facing endpoint to poll for remote diagnostics commands."""
    device = get_device(device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not enrolled.")
    cmd = poll_pending_command(device_id)
    if not cmd:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No pending commands.")
    return cmd

@router.post("/devices/{device_id}/diagnostics/results")
def submit_diagnostic_results(device_id: str, payload: ReportDiagnosticResultsRequest):
    """Device-facing endpoint to submit results from remote diagnostics tools execution."""
    try:
        res = report_command_results(payload.command_id, payload.status, payload.output)
        if not res:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Command not found.")
        return res
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

# Admin Observability Router
admin_router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_token)])

# Incident CRM Requests
class CreateIncidentRequest(BaseModel):
    incident_id: str
    device_id: str
    title: str
    description: Optional[str] = None
    severity: Optional[str] = "medium"

class UpdateIncidentRequest(BaseModel):
    status: Optional[str] = None
    severity: Optional[str] = None
    operator_note: Optional[str] = None

# Remote Execute Diagnostics Request
class RemoteExecuteRequest(BaseModel):
    command_id: str
    command: str
    arguments: Optional[List[str]] = []

class SimulateFailureRequest(BaseModel):
    failure_type: str

@admin_router.get("/observability/fleet")
def get_fleet_health():
    """Admin-only: aggregates telemetry from device snapshots."""
    return get_fleet_health_overview()

@admin_router.get("/observability/alerts")
def get_fleet_alerts():
    """Admin-only: aggregates alerts dynamically across health and security logs."""
    return get_active_alerts()

@admin_router.get("/support/bundles")
def list_support_bundles():
    """Admin-only: retrieves metadata lists of support package logs uploads."""
    return get_support_bundles()

@admin_router.post("/support/incidents", status_code=status.HTTP_201_CREATED)
def open_incident_ticket(payload: CreateIncidentRequest):
    """Admin-only: logs a support incident/ticket."""
    try:
        incident = create_incident(
            payload.incident_id, payload.device_id, payload.title, payload.description, payload.severity
        )
        return incident
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

@admin_router.patch("/support/incidents/{incident_id}")
def edit_incident_details(incident_id: str, payload: UpdateIncidentRequest):
    """Admin-only: updates support incident status or logs notes."""
    try:
        incident = update_incident(incident_id, payload.status, payload.severity, payload.operator_note)
        if not incident:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident ticket not found.")
        return incident
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

@admin_router.get("/support/incidents")
def list_incident_tickets():
    """Admin-only: retrieves list of open/resolved support incidents."""
    return get_incidents()

@admin_router.post("/devices/{device_id}/diagnostics/execute", status_code=status.HTTP_201_CREATED)
def execute_remote_diagnostic(device_id: str, payload: RemoteExecuteRequest):
    """Admin-only: enqueues a command task for remote execution diagnostic terminal access."""
    device = get_device(device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not enrolled.")
    cmd = enqueue_diagnostic_command(payload.command_id, device_id, payload.command, payload.arguments)
    return cmd

@router.get("/devices/{device_id}/diagnostics/commands")
def query_diagnostic_executions(device_id: str, verified: bool = Depends(verify_token)):
    """Admin-only: list diagnostic execution history for a device (reboots, system logs)."""
    return get_diagnostic_history(device_id)

@admin_router.get("/devices/{device_id}/timeline")
def get_timeline(device_id: str):
    """Admin-only: retrieves unified timeline of event types for the device."""
    return get_device_timeline(device_id)

@admin_router.get("/support/unhealthy")
def list_unhealthy_devices():
    """Admin-only: support workflow queue filtering for non-compliant/degraded devices."""
    return get_unhealthy_devices_workflow()

@admin_router.post("/devices/{device_id}/simulate-failure")
def trigger_simulated_failure(device_id: str, payload: SimulateFailureRequest):
    """Admin-only: triggers synthetic device resource degradation error state for testing alerts."""
    try:
        snap = simulate_device_failure(device_id, payload.failure_type)
        return snap
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
