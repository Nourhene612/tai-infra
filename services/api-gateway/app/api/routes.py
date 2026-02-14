from fastapi import APIRouter
from app.api.routes.auth import router as auth_router
from app.api.routes.auth_simple import router as auth_simple_router
from app.api.routes.debug import router as debug_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(auth_simple_router)
api_router.include_router(debug_router)
