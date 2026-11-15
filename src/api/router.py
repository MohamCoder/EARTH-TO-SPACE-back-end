from fastapi import APIRouter
from src.api.analyze import router as analyze_router
from src.api.catalog import router as catalog_router

api_router = APIRouter()
api_router.include_router(analyze_router)
api_router.include_router(catalog_router)
