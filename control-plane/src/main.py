import sys
import os
import json
import uuid
import time
import logging
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

# Ensure src directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import load_config
from database.schema import init_db
from routes import health, enrollment, devices, policies

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("control-plane")

# FastAPI Application
app = FastAPI(
    title="CerynixOS Fleet Control Plane",
    description="Centralized fleet enrollment, policies, compliance, and update orchestration backend.",
    version="1.0.0"
)

class CorrelationAndLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        
        start_time = time.time()
        
        # Log request receipt
        log_payload = {
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "level": "INFO",
            "correlation_id": correlation_id,
            "event": "request_received",
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown"
        }
        logger.info(json.dumps(log_payload))
        
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            # Log server exception
            log_payload.update({
                "level": "ERROR",
                "event": "request_failed",
                "error": str(e),
                "duration_seconds": round(time.time() - start_time, 4)
            })
            logger.error(json.dumps(log_payload))
            raise e
            
        duration = time.time() - start_time
        response.headers["X-Correlation-ID"] = correlation_id
        
        # Log request completion
        log_payload.update({
            "event": "request_completed",
            "status_code": status_code,
            "duration_seconds": round(duration, 4)
        })
        logger.info(json.dumps(log_payload))
        
        return response

app.add_middleware(CorrelationAndLoggingMiddleware)

# Include Routers
app.include_router(health.router)
app.include_router(enrollment.router)
app.include_router(devices.router)
app.include_router(policies.router)
app.include_router(policies.admin_router)

@app.on_event("startup")
def startup_event():
    """App startup hook to initialize schemas."""
    init_db()
    logger.info(json.dumps({
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        "level": "INFO",
        "event": "server_startup",
        "message": "CerynixOS Control Plane Backend started successfully."
    }))

if __name__ == "__main__":
    import uvicorn
    config = load_config()
    host = config.get("host", "127.0.0.1")
    port = config.get("port", 8000)
    
    logger.info(f"Starting server on http://{host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=False)
