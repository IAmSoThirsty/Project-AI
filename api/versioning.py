"""
API Versioning Support for Project-AI
Implements URL-based and header-based API versioning
"""

import logging
from typing import Optional
from fastapi import APIRouter, Request, Header, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime

logger = logging.getLogger(__name__)

# API Version Configuration
CURRENT_VERSION = "v1"
SUPPORTED_VERSIONS = ["v1"]
DEPRECATED_VERSIONS = []


class APIVersion:
    """API version manager"""
    
    @staticmethod
    def extract_version(request: Request, api_version: Optional[str] = Header(None)) -> str:
        """
        Extract API version from request
        
        Priority:
        1. Header: API-Version
        2. URL path: /v1/endpoint
        3. Query parameter: ?version=v1
        4. Default: current version
        """
        # Check header
        if api_version:
            return api_version
        
        # Check URL path
        path_parts = request.url.path.split('/')
        for part in path_parts:
            if part.startswith('v') and part[1:].isdigit():
                return part
        
        # Check query parameter
        version = request.query_params.get('version')
        if version:
            return version
        
        # Default to current version
        return CURRENT_VERSION
    
    @staticmethod
    def validate_version(version: str) -> bool:
        """Validate if version is supported"""
        return version in SUPPORTED_VERSIONS
    
    @staticmethod
    def is_deprecated(version: str) -> bool:
        """Check if version is deprecated"""
        return version in DEPRECATED_VERSIONS


def version_middleware(request: Request, call_next):
    """Middleware to handle API versioning"""
    
    # Extract version
    version = APIVersion.extract_version(request)
    
    # Validate version
    if not APIVersion.validate_version(version):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "unsupported_api_version",
                "message": f"API version '{version}' is not supported",
                "supported_versions": SUPPORTED_VERSIONS,
                "current_version": CURRENT_VERSION
            }
        )
    
    # Check if deprecated
    if APIVersion.is_deprecated(version):
        # Add deprecation warning header
        logger.warning(f"Deprecated API version used: {version}")
    
    # Store version in request state
    request.state.api_version = version
    
    # Process request
    response = call_next(request)
    
    # Add version headers to response
    if hasattr(response, 'headers'):
        response.headers['X-API-Version'] = version
        response.headers['X-API-Current-Version'] = CURRENT_VERSION
        
        if APIVersion.is_deprecated(version):
            response.headers['X-API-Deprecation'] = 'true'
            response.headers['X-API-Sunset'] = '2025-12-31'  # Example sunset date
    
    return response


# Version-specific routers
router_v1 = APIRouter(prefix="/v1", tags=["v1"])


@router_v1.get("/info")
async def api_info_v1():
    """Get API information (v1)"""
    return {
        "version": "v1",
        "status": "stable",
        "released": "2024-01-01",
        "documentation": "https://docs.projectai.dev/api/v1"
    }


@router_v1.get("/features")
async def api_features_v1():
    """List available features (v1)"""
    return {
        "version": "v1",
        "features": [
            "health_checks",
            "governance_api",
            "user_management",
            "rate_limiting",
            "circuit_breakers"
        ]
    }


# Versioned endpoints example
@router_v1.post("/actions/submit")
async def submit_action_v1(request: Request):
    """Submit action for governance review (v1)"""
    return {
        "version": "v1",
        "message": "Action submitted for review",
        "api_version": request.state.api_version
    }


# Future version router (v2)
router_v2 = APIRouter(prefix="/v2", tags=["v2"])


@router_v2.get("/info")
async def api_info_v2():
    """Get API information (v2)"""
    return {
        "version": "v2",
        "status": "beta",
        "released": "2025-01-01",
        "documentation": "https://docs.projectai.dev/api/v2",
        "breaking_changes": [
            "New authentication mechanism",
            "Response format changes",
            "Rate limit adjustments"
        ]
    }


# Version compatibility layer
class VersionCompatibility:
    """Handle backward compatibility between versions"""
    
    @staticmethod
    def convert_v1_to_v2(data: dict) -> dict:
        """Convert v1 response format to v2"""
        # Example transformation
        return {
            "version": "v2",
            "data": data,
            "metadata": {
                "converted_from": "v1",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    @staticmethod
    def convert_v2_to_v1(data: dict) -> dict:
        """Convert v2 response format to v1"""
        # Example transformation
        if "data" in data:
            return data["data"]
        return data


# Usage example in main FastAPI app
"""
from fastapi import FastAPI
from api.versioning import router_v1, router_v2, version_middleware

app = FastAPI()

# Add versioning middleware
app.middleware("http")(version_middleware)

# Include version-specific routers
app.include_router(router_v1)
app.include_router(router_v2)

# Also support root-level endpoints with header-based versioning
@app.get("/health")
async def health(request: Request):
    version = request.state.api_version
    
    if version == "v1":
        return {"status": "ok", "version": "v1"}
    elif version == "v2":
        return {
            "status": "healthy",
            "version": "v2",
            "checks": {
                "database": "ok",
                "cache": "ok"
            }
        }
"""
