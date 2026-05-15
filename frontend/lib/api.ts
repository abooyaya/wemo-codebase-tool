const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}

export interface ChatRequest {
  question: string;
  codebases: string[];   // 空陣列 = 全選
}

export type MessageRole = "user" | "assistant";

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  type?: "text" | "diagram" | "ui_render";  // assistant 回應類型
  sources?: Source[];
}

export interface Source {
  codebase: string;
  file_path: string;
  start_line: number;
  end_line: number;
}

// SSE streaming chat
export async function streamChat(
  req: ChatRequest,
  onChunk: (text: string) => void,
  onDone: (meta?: { type: string; sources?: Source[] }) => void,
  onError: (err: Error) => void,
) {
  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req),
    });

    if (!res.ok || !res.body) {
      throw new Error(`API error: ${res.status}`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const lines = decoder.decode(value).split("\n");
      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = line.slice(6).trim();
          if (data === "[DONE]") {
            onDone();
            return;
          }
          try {
            const parsed = JSON.parse(data);
            if (parsed.chunk) onChunk(parsed.chunk);
            if (parsed.done) { onDone(parsed); return; }
          } catch {
            // plain text chunk fallback
            if (data) onChunk(data);
          }
        }
      }
    }
    onDone();
  } catch (err) {
    onError(err instanceof Error ? err : new Error(String(err)));
  }
}

// ── Sync ─────────────────────────────────────────────────────────────────────

export interface RepoSyncResult {
  name: string;
  path: string;
  success: boolean;
  branch: string;
  commit: string;
  message: string;
  updated_at: string;
}

export interface SyncResponse {
  triggered_at: string;
  results: RepoSyncResult[];
}

export interface SyncStatusResponse {
  last_sync_at: string | null;
  next_sync_at: string | null;
  schedule: string;
  results: RepoSyncResult[];
}

export async function triggerSync(): Promise<SyncResponse> {
  const res = await fetch(`${API_BASE}/sync`, { method: "POST" });
  if (!res.ok) throw new Error(`Sync failed: ${res.status}`);
  return res.json();
}

export async function getSyncStatus(): Promise<SyncStatusResponse> {
  const res = await fetch(`${API_BASE}/sync/status`);
  if (!res.ok) throw new Error(`Status failed: ${res.status}`);
  return res.json();
}

export const ALL_CODEBASES = [
  "mnemosyne",
  "mnemosyne-api",
  "talos",
  "ServiceConsole-Apollo",
  "UserAPP-Android",
  "UserAPP-IOS",
];

