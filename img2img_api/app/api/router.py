from fastapi import APIRouter
from ..api.endpoints import redesign_populated,redesign_empty,inpainting,tasks
# Create API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    redesign_populated.router,
    prefix="/redesign/populated",
    tags=["redesign"]
)

api_router.include_router(
    redesign_empty.router,
    prefix="/redesign/empty",
    tags=["redesign"]
)

api_router.include_router(
    inpainting.router,
    prefix="/inpainting",
    tags=["inpainting"]
)

api_router.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["tasks"]
)