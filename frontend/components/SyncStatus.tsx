"use client";

import { useState, useEffect, useCallback } from "react";
import { RefreshCw, CheckCircle2, XCircle, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { triggerSync, getSyncStatus, SyncStatusResponse, RepoSyncResult } from "@/lib/api";

function formatTime(iso: string | null): string {
  if (!iso) return "從未";
  return new Date(iso).toLocaleString("zh-TW", {
    month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit",
  });
}

function RepoChip({ r }: { r: RepoSyncResult }) {
  return (
    <span
      title={`${r.branch} ${r.commit} — ${r.message}`}
      className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full border
        ${r.success
          ? "bg-green-50 text-green-700 border-green-200"
          : "bg-red-50 text-red-700 border-red-200"
        }`}
    >
      {r.success
        ? <CheckCircle2 className="w-3 h-3" />
        : <XCircle className="w-3 h-3" />
      }
      {r.name}
    </span>
  );
}

export function SyncStatus() {
  const [status, setStatus] = useState<SyncStatusResponse | null>(null);
  const [syncing, setSyncing] = useState(false);

  const loadStatus = useCallback(async () => {
    try {
      const s = await getSyncStatus();
      setStatus(s);
    } catch {
      // 後端未啟動時靜默失敗
    }
  }, []);

  useEffect(() => {
    loadStatus();
  }, [loadStatus]);

  const handleSync = async () => {
    setSyncing(true);
    try {
      const res = await triggerSync();
      setStatus((prev) => prev
        ? { ...prev, last_sync_at: res.triggered_at, results: res.results }
        : null
      );
      // 重整狀態以更新 next_sync_at
      await loadStatus();
    } catch (err) {
      console.error("Sync failed", err);
    } finally {
      setSyncing(false);
    }
  };

  return (
    <div className="flex items-center gap-2 flex-wrap">
      {/* Repo chips */}
      {status?.results.map((r) => <RepoChip key={r.name} r={r} />)}

      {/* 時間資訊 */}
      {status && (
        <span className="text-xs text-muted-foreground flex items-center gap-1">
          <Clock className="w-3 h-3" />
          上次：{formatTime(status.last_sync_at)}
        </span>
      )}

      {/* Sync Now 按鈕 */}
      <Button
        size="sm"
        variant="outline"
        onClick={handleSync}
        disabled={syncing}
        className="h-7 text-xs px-2"
      >
        <RefreshCw className={`w-3 h-3 mr-1 ${syncing ? "animate-spin" : ""}`} />
        {syncing ? "Syncing…" : "Sync Now"}
      </Button>
    </div>
  );
}
