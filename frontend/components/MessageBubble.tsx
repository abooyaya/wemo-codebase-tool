"use client";

import { Message } from "@/lib/api";
import { Badge } from "@/components/ui/badge";

const PATH_LABELS: Record<string, string> = {
  rag: "RAG",
  full_scan: "Full Scan",
  diagram: "Diagram",
  ui_render: "UI Render",
};

interface Props {
  message: Message;
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <div className={`flex w-full ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div className={`max-w-[80%] ${isUser ? "items-end" : "items-start"} flex flex-col gap-1`}>
        {/* bubble */}
        <div
          className={`rounded-2xl px-4 py-3 text-sm whitespace-pre-wrap leading-relaxed shadow-sm ${
            isUser
              ? "bg-primary text-primary-foreground rounded-br-sm"
              : "bg-card border rounded-bl-sm"
          }`}
        >
          {message.type === "ui_render" ? (
            <UIRenderPreview html={message.content} />
          ) : (
            message.content || <span className="animate-pulse text-muted-foreground">▍</span>
          )}
        </div>

        {/* sources */}
        {message.sources && message.sources.length > 0 && (
          <div className="flex flex-wrap gap-1 px-1">
            {message.sources.map((s, i) => (
              <Badge key={i} variant="secondary" className="text-xs font-mono">
                {s.codebase}/{s.file_path}:{s.start_line}
              </Badge>
            ))}
          </div>
        )}

        {/* path type label */}
        {message.type && message.type !== "text" && (
          <span className="text-xs text-muted-foreground px-1">
            {PATH_LABELS[message.type] ?? message.type}
          </span>
        )}
      </div>
    </div>
  );
}

function UIRenderPreview({ html }: { html: string }) {
  return (
    <div className="flex flex-col gap-2">
      <p className="text-xs text-amber-600">
        ⚠️ AI 根據程式碼生成的近似預覽，非實際畫面
      </p>
      <iframe
        srcDoc={html}
        sandbox="allow-scripts"
        className="w-full min-h-[400px] rounded border bg-white"
        title="UI Preview"
      />
    </div>
  );
}
