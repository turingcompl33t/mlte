"""
mlte/backend/api/api.py

Top-level API functionality.
"""

from fastapi import APIRouter

from mlte.backend.api.endpoints import (
    artifact,
    catalog_entry,
    context,
    custom_list_entry,
    group,
    health,
    token,
    user,
)
from mlte.user.model import ResourceType

# The common URL prefix for all artifact routes
_ARTIFACT_PREFIX = (
    f"/{ResourceType.MODEL.value}" "/{model_id}/version/{version_id}"
)

# The base API router across all endpoints
api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(token.router, tags=["token"])
api_router.include_router(
    context.router, prefix=f"/{ResourceType.MODEL.value}", tags=["context"]
)
api_router.include_router(
    user.router, prefix=f"/{ResourceType.USER.value}", tags=["user"]
)
api_router.include_router(
    group.router, prefix=f"/{ResourceType.GROUP.value}", tags=["group"]
)
api_router.include_router(
    catalog_entry.router,
    prefix=f"/{ResourceType.CATALOG.value}",
    tags=["catalog_entry"],
)
api_router.include_router(
    artifact.router,
    prefix=f"{_ARTIFACT_PREFIX}/artifact",
    tags=["artifact"],
)
api_router.include_router(
    custom_list_entry.router,
    prefix=f"/{ResourceType.CUSTOM_LIST.value}",
    tags=["custom_list_entry"],
)
