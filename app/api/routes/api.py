from fastapi import APIRouter

from app.api.routes import store

router = APIRouter()
router.include_router(store.router, tags=["store"], prefix="/store")
