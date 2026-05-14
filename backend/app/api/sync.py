from fastapi import APIRouter, BackgroundTasks

from app.models.sync import SyncResponse, SyncStatusResponse
from app.services import sync as sync_service

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("", response_model=SyncResponse)
async def trigger_sync(background_tasks: BackgroundTasks):
    """手動觸發所有 codebase 的 git pull（非同步執行）。"""
    # 在背景執行，立即回傳最新一次的狀態；若從未 sync 過則先同步再回傳
    import asyncio
    from datetime import datetime, timezone
    from app.services.sync import sync_all, _last_sync_at

    if _last_sync_at is None:
        # 第一次：同步等待
        result = sync_all()
        return result

    # 已有上次結果：排入背景並立即回傳觸發確認
    background_tasks.add_task(sync_all)
    from app.services.sync import get_status
    status = get_status()
    from app.models.sync import SyncResponse
    return SyncResponse(
        triggered_at=datetime.now(timezone.utc),
        results=status.results,
    )


@router.get("/status", response_model=SyncStatusResponse)
async def sync_status():
    """回傳最後一次 sync 時間、各 repo 結果、下次排程時間。"""
    from app.main import get_next_sync_time
    next_sync = get_next_sync_time()
    return sync_service.get_status(next_sync_at=next_sync)

