from fastapi import APIRouter, HTTPException, status
from database.connection import get_db_connection

router = APIRouter(prefix="/api/v1")

@router.get("/health")
def get_health():
    """Simple service health check."""
    return {"status": "healthy", "service": "CerynixOS Fleet Control Plane"}

@router.get("/readiness")
def get_readiness():
    """Service readiness check verifying database connectivity."""
    try:
        with get_db_connection() as conn:
            conn.execute("SELECT 1;")
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )
