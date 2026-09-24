"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Bot, History, Loader2, Plus, Send, Trash2, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Markdown } from "@/components/Markdown";
import { cx } from "@/components/ui";
import { api } from "@/lib/api";
import { formatTokens, formatUsd } from "@/lib/format";
import type { AssistantModel, ChatDetail, ChatMessage, ChatSend, ChatSession } from "@/lib/types";

const TOOL_LABEL: Record<string, string> = {
  search_knowledge: "kho kiến thức",
  list_skills: "danh sách skill",
  read_skill: "skill",
  calculate_chart: "tính chart",
  search_clients: "tìm khách hàng",
  client_chart: "chart khách hàng",
  report_info: "báo cáo",
};

const store = {
  get(key: string): string | null {
    try {
      return sessionStorage.getItem(key);
    } catch {
      return null;
    }
  },
  set(key: string, value: string) {
    try {
      sessionStorage.setItem(key, value);
    } catch { /* bỏ qua */ }
  },
};

function AssistantBubble({ message }: { message: ChatMessage }) {
  return (
    <div className="max-w-[92%] rounded-xl rounded-tl-sm border border-line bg-white px-3 py-2 shadow-sm">
      <Markdown>{message.content}</Markdown>
      {message.sources.length > 0 && (
        <div className="mt-2 border-t border-line pt-1.5 text-[11px] text-muted">
          <span className="font-medium">Nguồn:</span> {message.sources.join(" · ")}
        </div>
      )}
      <div className="mt-1 text-[11px] text-muted/80">
        {message.tools_used.length > 0 && <>Đã tra: {message.tools_used.map((t) => TOOL_LABEL[t] ?? t).join(", ")} · </>}
        {formatTokens(message.prompt_tokens + message.completion_tokens)} token
        {message.cost_usd !== null && message.cost_usd !== undefined ? ` · ${formatUsd(message.cost_usd)}` : ""}
        {message.latency_ms > 0 ? ` · ${(message.latency_ms / 1000).toFixed(1)}s` : ""}
      </div>
    </div>
  );
}

export function AssistantWidget() {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(() => store.get("hd-assistant-open") === "1");
  const [view, setView] = useState<"chat" | "history">("chat");
  const [sessionId, setSessionId] = useState<string | null>(() => store.get("hd-assistant-session"));
  const [modelIndex, setModelIndex] = useState(() => Number(store.get("hd-assistant-model") ?? 0) || 0);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  const models = useQuery({
    queryKey: ["assistant-models"],
    queryFn: () => api.get<AssistantModel[]>("/assistant/models"),
    enabled: open,
    staleTime: 5 * 60_000,
  });
  const sessions = useQuery({
    queryKey: ["assistant-sessions"],
    queryFn: () => api.get<ChatSession[]>("/assistant/sessions"),
    enabled: open && view === "history",
  });

  useEffect(() => store.set("hd-assistant-open", open ? "1" : "0"), [open]);
  useEffect(() => {
    if (sessionId) store.set("hd-assistant-session", sessionId);
  }, [sessionId]);
  useEffect(() => store.set("hd-assistant-model", String(modelIndex)), [modelIndex]);
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, open]);

  const openSession = async (id: string) => {
    const detail = await api.get<ChatDetail>(`/assistant/sessions/${id}`);
    setSessionId(detail.session.id);
    setMessages(detail.messages);
    setView("chat");
  };

  const send = useMutation({
    mutationFn: (text: string) =>
      api.post<ChatSend>("/assistant/chat", { session_id: sessionId, model_index: modelIndex, message: text }),
    onMutate: (text) => {
      setMessages((list) => [
        ...list,
        { id: -Date.now(), role: "user", content: text, tools_used: [], sources: [], prompt_tokens: 0,
          completion_tokens: 0, cost_usd: null, latency_ms: 0, created_at: new Date().toISOString() },
      ]);
      setDraft("");
    },
    onSuccess: (data) => {
      setSessionId(data.session.id);
      setMessages((list) => [...list, data.message]);
      queryClient.invalidateQueries({ queryKey: ["assistant-sessions"] });
    },
    onError: () => {
      setMessages((list) => list.slice(0, -1));
      setDraft(send.variables ?? "");
    },
  });

  const remove = useMutation({
    mutationFn: (id: string) => api.del(`/assistant/sessions/${id}`),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ["assistant-sessions"] });
      if (id === sessionId) {
        setSessionId(null);
        setMessages([]);
      }
    },
  });

  const submit = () => {
    const text = draft.trim();
    if (!text || send.isPending) return;
    send.mutate(text);
  };

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        title="Trợ lý Human Design"
        className="fixed bottom-5 right-5 z-30 flex size-13 items-center justify-center rounded-full bg-brand-500 p-3.5 text-white shadow-lg transition-transform hover:scale-105 hover:bg-brand-600">
        <Bot className="size-6" aria-hidden />
      </button>
    );
  }

  return (
    <div className="fixed bottom-5 right-5 z-50 flex h-[560px] max-h-[calc(100vh-6rem)] w-[380px] max-w-[calc(100vw-2rem)] flex-col overflow-hidden rounded-2xl border border-line bg-paper shadow-2xl">
      <div className="flex items-center gap-2 border-b border-line bg-white px-3 py-2.5">
        <Bot className="size-5 shrink-0 text-brand-600" aria-hidden />
        <div className="min-w-0 flex-1 leading-tight">
          <div className="truncate text-sm font-semibold text-ink">Trợ lý Human Design</div>
          <div className="truncate text-[11px] text-muted">Chỉ trả lời trong phạm vi Human Design</div>
        </div>
        <button title="Lịch sử chat" onClick={() => setView(view === "chat" ? "history" : "chat")}
          className="rounded-md p-1.5 text-muted hover:bg-paper hover:text-ink">
          <History className="size-4" />
        </button>
        <button title="Cuộc trò chuyện mới" onClick={() => { setSessionId(null); setMessages([]); setView("chat"); }}
          className="rounded-md p-1.5 text-muted hover:bg-paper hover:text-ink">
          <Plus className="size-4" />
        </button>
        <button title="Đóng" onClick={() => setOpen(false)} className="rounded-md p-1.5 text-muted hover:bg-paper hover:text-ink">
          <X className="size-4" />
        </button>
      </div>

      <div className="border-b border-line bg-white px-3 py-2">
        <label className="flex items-center gap-2 text-xs text-muted">
          Mô hình
          <select
            value={modelIndex}
            onChange={(e) => setModelIndex(Number(e.target.value))}
            className="min-w-0 flex-1 rounded-md border border-line bg-white px-2 py-1 text-xs text-ink">
            {(models.data ?? []).map((m) => (
              <option key={m.index} value={m.index}>{m.name} · {m.model}</option>
            ))}
            {(models.data ?? []).length === 0 && <option value={0}>Chưa có mô hình</option>}
          </select>
        </label>
      </div>

      {view === "history" ? (
        <div className="flex-1 overflow-y-auto p-2">
          {sessions.isLoading && <p className="p-4 text-center text-sm text-muted">Đang tải…</p>}
          {sessions.data?.length === 0 && <p className="p-4 text-center text-sm text-muted">Chưa có cuộc trò chuyện nào.</p>}
          <ul className="space-y-1">
            {(sessions.data ?? []).map((s) => (
              <li key={s.id}
                className={cx("group flex items-center gap-1 rounded-lg px-2 py-2 hover:bg-white",
                  s.id === sessionId && "bg-white ring-1 ring-brand-100")}>
                <button onClick={() => openSession(s.id)} className="min-w-0 flex-1 text-left">
                  <div className="truncate text-sm font-medium text-ink">{s.title}</div>
                  <div className="text-[11px] text-muted">
                    {s.model ? `${s.model} · ` : ""}{s.message_count} tin · {formatUsd(s.total_cost_usd)}
                  </div>
                </button>
                <button title="Xóa" onClick={() => confirm("Xóa cuộc trò chuyện này?") && remove.mutate(s.id)}
                  className="rounded-md p-1.5 text-muted opacity-0 hover:bg-red-50 hover:text-red-700 group-hover:opacity-100">
                  <Trash2 className="size-3.5" />
                </button>
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <>
          <div className="flex-1 space-y-3 overflow-y-auto p-3">
            {(models.data ?? []).length === 0 && !models.isLoading && (
              <div className="rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs text-amber-900">
                AI chưa được cấu hình. Quản trị viên vào <strong>Cài đặt → AI / LLM</strong> để nhập khóa API.
              </div>
            )}
            {messages.length === 0 && (
              <div className="rounded-xl border border-line bg-white p-3 text-xs text-muted">
                Hỏi mình về Type, Strategy, Authority, Centers, Channels, Gates… hoặc nhờ tính chart
                (vd: “Tính chart cho người sinh 15/05/1990 lúc 08:30”).
              </div>
            )}
            {messages.map((m) =>
              m.role === "user" ? (
                <div key={m.id} className="flex justify-end">
                  <div className="max-w-[92%] whitespace-pre-wrap rounded-xl rounded-tr-sm bg-brand-500 px-3 py-2 text-sm text-white">
                    {m.content}
                  </div>
                </div>
              ) : (
                <AssistantBubble key={m.id} message={m} />
              ),
            )}
            {send.isPending && (
              <div className="flex items-center gap-2 text-xs text-muted">
                <Loader2 className="size-4 animate-spin" /> Đang tra cứu…
              </div>
            )}
            {send.error && (
              <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-xs text-red-800">
                {(send.error as Error).message}
              </div>
            )}
            <div ref={bottomRef} />
          </div>
          <div className="border-t border-line bg-white p-2">
            <div className="flex items-end gap-2">
              <textarea
                rows={2}
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    submit();
                  }
                }}
                placeholder="Hỏi về Human Design… (Enter để gửi)"
                maxLength={2000}
                className="max-h-28 min-h-10 flex-1 resize-none rounded-lg border border-line px-3 py-2 text-sm focus:border-brand-500 focus:outline-none"
              />
              <button onClick={submit} disabled={send.isPending || !draft.trim()}
                title="Gửi"
                className="rounded-lg bg-brand-500 p-2.5 text-white hover:bg-brand-600 disabled:opacity-50">
                <Send className="size-4" />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
