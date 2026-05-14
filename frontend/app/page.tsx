"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { CodebaseSelector } from "@/components/CodebaseSelector";
import { MessageBubble } from "@/components/MessageBubble";
import { ChatInput } from "@/components/ChatInput";
import { SyncStatus } from "@/components/SyncStatus";
import { ScrollArea } from "@/components/ui/scroll-area";
import { streamChat, Message, Source } from "@/lib/api";

let idCounter = 0;
const uid = () => String(++idCounter);

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: uid(),
      role: "assistant",
      content: "👋 你好！請問有什麼關於 WeMo codebase 的問題想問？\n\n可以試試：\n• 「Android App 有哪些 Firebase event？」\n• 「iOS 的 onboarding 流程是什麼？」\n• 「Apollo 的機車 filter Group 0 代表什麼？」",
    },
  ]);
  const [selectedCodebases, setSelectedCodebases] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = useCallback(
    async (question: string) => {
      if (isLoading) return;

      const userMsg: Message = { id: uid(), role: "user", content: question };
      const assistantId = uid();
      const assistantMsg: Message = { id: assistantId, role: "assistant", content: "" };

      setMessages((prev) => [...prev, userMsg, assistantMsg]);
      setIsLoading(true);

      await streamChat(
        { question, codebases: selectedCodebases },
        (chunk) => {
          setMessages((prev) =>
            prev.map((m) => m.id === assistantId ? { ...m, content: m.content + chunk } : m)
          );
        },
        (meta) => {
          if (meta) {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId
                  ? { ...m, type: meta.type as Message["type"], sources: meta.sources as Source[] }
                  : m
              )
            );
          }
          setIsLoading(false);
        },
        (err) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, content: `❌ 錯誤：${err.message}` } : m
            )
          );
          setIsLoading(false);
        }
      );
    },
    [isLoading, selectedCodebases]
  );

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <header className="border-b px-6 py-3 flex items-center justify-between bg-card flex-wrap gap-2">
        <div>
          <h1 className="font-semibold text-base">WeMo Codebase QA</h1>
          <p className="text-xs text-muted-foreground">用自然語言問 codebase 問題</p>
        </div>
        <SyncStatus />
      </header>

      {/* Codebase selector */}
      <CodebaseSelector selected={selectedCodebases} onChange={setSelectedCodebases} />

      {/* Messages */}
      <ScrollArea className="flex-1 px-4 py-4">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        <div ref={bottomRef} />
      </ScrollArea>

      {/* Input */}
      <ChatInput onSend={handleSend} disabled={isLoading} />
    </div>
  );
}
