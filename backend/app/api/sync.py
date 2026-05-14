from fastapi import APIRouter

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("")
async def trigger_sync():
    # TODO: M2 — Git sync service
    return {"message": "Sync endpoint - coming in M2"}


@router.get("/status")
async def sync_status():
    # TODO: M2 — sync status
    return {"message": "Sync status - coming in M2"}
