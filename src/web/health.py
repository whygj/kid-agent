"""Health check and monitoring endpoints"""

import asyncio
import logging
import os
import time
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Request, Response
from pydantic import BaseModel

from src.config.settings import get_config
from src.memory.store import get_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["health"])


class HealthResponse(BaseModel):
    """Basic health check response"""
    status: str
    timestamp: str
    version: str


class DetailedHealthResponse(BaseModel):
    """Detailed health check response"""
    status: str
    timestamp: str
    version: str
    uptime_seconds: float
    components: dict


class MetricsResponse(BaseModel):
    """Prometheus-style metrics response"""
    metrics: str


# Start time for uptime calculation
_start_time = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request) -> dict:
    """Basic health check endpoint

    Returns a simple status indicating if the service is healthy.
    This endpoint is used by load balancers and orchestration systems.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
    }


@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check(request: Request) -> dict:
    """Detailed health check endpoint

    Provides comprehensive health information including:
    - Database connection status
    - API key configuration
    - Disk space
    - Uptime
    """
    uptime = time.time() - _start_time

    components = {
        "status": "healthy",
        "uptime_seconds": uptime,
        "checks": {},
    }

    # Check database
    try:
        store = await get_store()
        components["checks"]["database"] = {
            "status": "healthy",
            "path": store.db_path,
            "exists": Path(store.db_path).exists(),
        }
    except Exception as e:
        components["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        components["status"] = "degraded"

    # Check API configuration
    try:
        config = get_config()
        api_configured = bool(config.llm.api_key and len(config.llm.api_key) > 10)
        components["checks"]["llm_api"] = {
            "status": "healthy" if api_configured else "warning",
            "provider": config.llm.provider.value,
            "model": config.llm.model,
            "configured": api_configured,
        }
    except Exception as e:
        components["checks"]["llm_api"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        components["status"] = "degraded"

    # Check disk space
    try:
        db_path = Path(config.db.path)
        if db_path.exists():
            stat = os.statvfs(db_path)
            total = stat.f_frsize * stat.f_blocks
            available = stat.f_frsize * stat.f_bavail
            percent_used = 100 - (available / total * 100)

            disk_status = "healthy"
            if percent_used > 80:
                disk_status = "warning"
            if percent_used > 90:
                disk_status = "unhealthy"
                components["status"] = "degraded"

            components["checks"]["disk"] = {
                "status": disk_status,
                "total_bytes": total,
                "available_bytes": available,
                "percent_used": round(percent_used, 2),
            }
        else:
            components["checks"]["disk"] = {
                "status": "healthy",
                "message": "Database file not created yet",
            }
    except Exception as e:
        components["checks"]["disk"] = {
            "status": "unhealthy",
            "error": str(e),
        }

    # Check environment
    try:
        config = get_config()
        components["checks"]["environment"] = {
            "status": "healthy",
            "environment": config.environment.value,
            "log_level": config.log_level,
        }
    except Exception as e:
        components["checks"]["environment"] = {
            "status": "unhealthy",
            "error": str(e),
        }

    return {
        "status": components["status"],
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "uptime_seconds": uptime,
        "components": components,
    }


@router.get("/metrics", response_class=Response)
async def prometheus_metrics(request: Request) -> Response:
    """Prometheus metrics endpoint

    Returns metrics in Prometheus text format.
    Can be scraped by Prometheus or similar monitoring systems.
    """
    uptime = time.time() - _start_time

    metrics = [
        "# HELP kid_agent_uptime_seconds Uptime of the application in seconds",
        "# TYPE kid_agent_uptime_seconds gauge",
        f"kid_agent_uptime_seconds {uptime:.2f}",
        "",
        "# HELP kid_agent_health_status Health status of the application (1=healthy, 0=unhealthy)",
        "# TYPE kid_agent_health_status gauge",
        "kid_agent_health_status 1",
        "",
        "# HELP kid_agent_version Version of the application",
        "# TYPE kid_agent_version gauge",
        'kid_agent_version{version="2.0.0"} 1',
        "",
        "# HELP kid_agent_request_total Total number of HTTP requests",
        "# TYPE kid_agent_request_total counter",
        "kid_agent_request_total 0",
        "",
    ]

    # Add database metrics
    try:
        store = await get_store()
        db_path = Path(store.db_path)
        if db_path.exists():
            db_size = db_path.stat().st_size
            metrics.extend([
                "# HELP kid_agent_database_size_bytes Size of the SQLite database in bytes",
                "# TYPE kid_agent_database_size_bytes gauge",
                f"kid_agent_database_size_bytes {db_size}",
                "",
            ])
    except Exception:
        pass

    # Add disk metrics
    try:
        config = get_config()
        db_path = Path(config.db.path)
        if db_path.exists():
            stat = os.statvfs(db_path)
            total = stat.f_frsize * stat.f_blocks
            available = stat.f_frsize * stat.f_bavail
            percent_used = 100 - (available / total * 100)

            metrics.extend([
                "# HELP kid_agent_disk_percent_used Disk space percentage used",
                "# TYPE kid_agent_disk_percent_used gauge",
                f"kid_agent_disk_percent_used {percent_used:.2f}",
                "",
                "# HELP kid_agent_disk_available_bytes Available disk space in bytes",
                "# TYPE kid_agent_disk_available_bytes gauge",
                f"kid_agent_disk_available_bytes {available}",
                "",
            ])
    except Exception:
        pass

    return Response(content="\n".join(metrics), media_type="text/plain")


@router.get("/ping")
async def ping() -> dict:
    """Simple ping endpoint for quick connectivity checks"""
    return {"ping": "pong"}
