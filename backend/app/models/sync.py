from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RepoSyncResult(BaseModel):
    name: str
    path: str
    success: bool
    branch: str = ""
    commit: str = ""
    message: str = ""
    updated_at: datetime


class SyncResponse(BaseModel):
    triggered_at: datetime
    results: list[RepoSyncResult]


class SyncStatusResponse(BaseModel):
    last_sync_at: Optional[datetime]
    next_sync_at: Optional[datetime]
    schedule: str
    results: list[RepoSyncResult]
