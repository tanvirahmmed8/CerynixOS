import sys
import os
import json
import uuid
import time
import logging
from collections import defaultdict
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

# Ensure src directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import load_config
from database.schema import init_db
from routes import health, enrollment, devices, policies, updates, governance, observability, registry

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

# ─── Security Headers Middleware ──────────────────────────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds HTTP hardening headers to every response."""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "connect-src 'self';"
        )
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# ─── In-Memory Rate Limiter Middleware ────────────────────────────────────────
# Simple per-IP sliding window counter. Not suitable for multi-process deployment.
# Replace with Redis-backed rate limiter before production scaling.
RATE_LIMIT_MAX_REQUESTS = 120   # max requests per window
RATE_LIMIT_WINDOW_SECONDS = 60  # window duration
RATE_LIMIT_EXEMPT_PATHS = {"/", "/styles.css", "/app.js", "/favicon.ico"}

_rate_limit_counters: dict = defaultdict(list)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rejects requests exceeding rate limit threshold from a single IP."""
    async def dispatch(self, request: Request, call_next):
        if request.url.path in RATE_LIMIT_EXEMPT_PATHS:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - RATE_LIMIT_WINDOW_SECONDS

        # Prune timestamps outside the window
        _rate_limit_counters[client_ip] = [
            ts for ts in _rate_limit_counters[client_ip] if ts > window_start
        ]

        if len(_rate_limit_counters[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
            logger.warning(json.dumps({
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                "level": "WARNING",
                "event_type": "security_event",
                "security_event_type": "suspicious_activity",
                "detail": f"Rate limit exceeded: {client_ip} sent {len(_rate_limit_counters[client_ip])} requests in {RATE_LIMIT_WINDOW_SECONDS}s.",
                "client_ip": client_ip,
                "path": request.url.path,
                "severity": "WARNING"
            }))
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please slow down your requests."}
            )

        _rate_limit_counters[client_ip].append(now)
        return await call_next(request)

app.add_middleware(RateLimitMiddleware)

# Include Routers
app.include_router(health.router)
app.include_router(enrollment.router)
app.include_router(devices.router)
app.include_router(policies.router)
app.include_router(policies.admin_router)
app.include_router(updates.router)
app.include_router(updates.admin_router)
app.include_router(governance.router)
app.include_router(governance.admin_router)
app.include_router(observability.router)
app.include_router(observability.admin_router)
app.include_router(registry.router)
app.include_router(registry.admin_router)

# Mount Static Dashboard Files
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../static"))
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

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
