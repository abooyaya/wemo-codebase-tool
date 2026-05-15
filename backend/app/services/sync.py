"""Git Sync 服務 — 透過 GitPython 對所有 codebase 執行 git pull。"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import git
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

from app.config import get_config
from app.models.sync import RepoSyncResult, SyncResponse, SyncStatusResponse

logger = logging.getLogger(__name__)

# 專案根目錄：backend/app/services/sync.py → ../../../ = 專案根
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()

# SSH 選項：不等 passphrase 輸入、連線最多等 10 秒
_GIT_SSH_CMD = (
    "ssh -o BatchMode=yes "
    "-o StrictHostKeyChecking=accept-new "
    "-o ConnectTimeout=10 "
    "-o ServerAliveInterval=5 "
    "-o ServerAliveCountMax=1"
)

# ── 記憶體內狀態（重啟後清空）────────────────────────────────────────────────
_last_sync_at: Optional[datetime] = None
_last_results: list[RepoSyncResult] = []


def _resolve_path(path: str) -> Path:
    """將 .env 中的路徑解析為絕對路徑，相對路徑以專案根目錄為基準。"""
    p = Path(path).expanduser()
    if p.is_absolute():
        return p
    return (_PROJECT_ROOT / p).resolve()


def _pull_repo(name: str, path: str) -> RepoSyncResult:
    """對單一 repo 執行 git pull，回傳結果。"""
    now = datetime.now(timezone.utc)
    abs_path = _resolve_path(path)

    try:
        repo = git.Repo(abs_path)
    except (InvalidGitRepositoryError, NoSuchPathError) as exc:
        logger.warning("⚠️  %s: 無法開啟 repo — %s", name, exc)
        return RepoSyncResult(
            name=name, path=path, success=False,
            message=f"無法開啟 repo：{exc}", updated_at=now,
        )

    try:
        # 注入 SSH 選項，確保不會 hang 在等待使用者輸入
        with repo.git.custom_environment(GIT_SSH_COMMAND=_GIT_SSH_CMD):
            fetch_info = repo.remotes.origin.pull()

        branch = repo.active_branch.name
        commit = repo.head.commit.hexsha[:7]
        note = fetch_info[0].note if fetch_info else ""
        msg = f"已更新 ({note})" if note else "已是最新"

        logger.info("✅  %s [%s] %s", name, branch, commit)
        return RepoSyncResult(
            name=name, path=path, success=True,
            branch=branch, commit=commit,
            message=msg, updated_at=now,
        )
    except GitCommandError as exc:
        # 擷取簡短訊息（去掉多餘 stderr 噪音）
        err_lines = [l.strip() for l in str(exc).splitlines() if l.strip()]
        short_msg = next(
            (l for l in err_lines if l and not l.startswith("cmd")), str(exc)
        )[:200]
        logger.error("❌  %s: git pull 失敗 — %s", name, short_msg)
        return RepoSyncResult(
            name=name, path=path, success=False,
            message=short_msg, updated_at=now,
        )
    except Exception as exc:
        logger.error("❌  %s: 未預期錯誤 — %s", name, exc)
        return RepoSyncResult(
            name=name, path=path, success=False,
            message=str(exc)[:200], updated_at=now,
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
