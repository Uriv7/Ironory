from fastapi import APIRouter
from backend.app.api.v1.endpoints import health, system, auth, organizations

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(system.router)
api_router.include_router(auth.router)
api_router.include_router(organizations.router)
