from fastapi import APIRouter
from app.api import health, chat, sync

router = APIRouter(prefix="/api")
router.include_router(health.router)
router.include_router(chat.router)
router.include_router(sync.router)
