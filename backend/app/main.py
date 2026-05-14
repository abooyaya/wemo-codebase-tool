import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.config import get_config
from app.services.sync import sync_all

logger = logging.getLogger(__name__)

_scheduler: Optional[AsyncIOScheduler] = None


def get_next_sync_time() -> Optional[datetime]:
    """回傳 APScheduler 下一次排程執行時間（UTC）。"""
    if _scheduler is None:
        return None
    jobs = _scheduler.get_jobs()
    if not jobs:
        return None
    next_run = jobs[0].next_run_time
    return next_run


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _scheduler
    cfg = get_config()
    logger.info("✅ LLM: %s/%s", cfg.llm_provider, cfg.llm_model)
    logger.info("✅ Embedding: %s/%s", cfg.embedding_provider, cfg.embedding_model)
    logger.info("✅ Codebases: %s", [c.name for c in cfg.codebases])

    # 啟動 APScheduler
    _scheduler = AsyncIOScheduler(timezone="UTC")
    try:
        trigger = CronTrigger.from_crontab(cfg.sync_schedule, timezone="UTC")
        _scheduler.add_job(sync_all, trigger, id="git_sync", replace_existing=True)
        _scheduler.start()
        logger.info("⏰ Git Sync 排程啟動：%s", cfg.sync_schedule)
    except Exception as exc:
        logger.warning("⚠️  排程設定失敗（%s），跳過排程", exc)

    yield

    # 關閉 APScheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("⏹  APScheduler 已關閉")


app = FastAPI(
    title="Codebase QA Tool",
    description="自然語言問答 WeMo codebases",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

