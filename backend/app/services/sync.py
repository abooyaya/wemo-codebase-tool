"""Git Sync 服務 — 透過 GitPython 對所有 codebase 執行 git pull。"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import git
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

from app.config import get_config
from app.models.sync import RepoSyncResult, SyncResponse, SyncStatusResponse

logger = logging.getLogger(__name__)

# ── 記憶體內狀態（重啟後清空）────────────────────────────────────────────────
_last_sync_at: Optional[datetime] = None
_last_results: list[RepoSyncResult] = []


def _pull_repo(name: str, path: str) -> RepoSyncResult:
    """對單一 repo 執行 git pull，回傳結果。"""
    now = datetime.now(timezone.utc)
    abs_path = Path(path).expanduser().resolve()

    try:
        repo = git.Repo(abs_path)
    except (InvalidGitRepositoryError, NoSuchPathError) as exc:
        logger.warning("⚠️  %s: 無法開啟 repo — %s", name, exc)
        return RepoSyncResult(
            name=name, path=path, success=False,
            message=f"無法開啟 repo：{exc}", updated_at=now,
        )

    try:
        origin = repo.remotes.origin
        fetch_info = origin.pull()

        branch = repo.active_branch.name
        commit = repo.head.commit.hexsha[:7]

        # fetch_info 是一個 list，取第一個來判斷是否有更新
        note = fetch_info[0].note if fetch_info else ""
        msg = f"已更新 ({note})" if note else "已是最新"

        logger.info("✅  %s [%s] %s", name, branch, commit)
        return RepoSyncResult(
            name=name, path=path, success=True,
            branch=branch, commit=commit,
            message=msg, updated_at=now,
        )
    except GitCommandError as exc:
        logger.error("❌  %s: git pull 失敗 — %s", name, exc)
        return RepoSyncResult(
            name=name, path=path, success=False,
            message=str(exc), updated_at=now,
        )


def sync_all() -> SyncResponse:
    """同步所有 codebase，更新記憶體狀態並回傳結果。"""
    global _last_sync_at, _last_results

    cfg = get_config()
    triggered_at = datetime.now(timezone.utc)
    logger.info("🔄 開始 Git Sync（%d 個 repo）", len(cfg.codebases))

    results = [_pull_repo(cb.name, cb.path) for cb in cfg.codebases]

    _last_sync_at = triggered_at
    _last_results = results

    ok = sum(1 for r in results if r.success)
    logger.info("✅ Git Sync 完成：%d/%d 成功", ok, len(results))
    return SyncResponse(triggered_at=triggered_at, results=results)


def get_status(next_sync_at: Optional[datetime] = None) -> SyncStatusResponse:
    cfg = get_config()
    return SyncStatusResponse(
        last_sync_at=_last_sync_at,
        next_sync_at=next_sync_at,
        schedule=cfg.sync_schedule,
        results=_last_results,
    )
