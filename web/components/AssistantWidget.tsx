"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Bot, FilePlus2, History, Loader2, Plus, Send, ThumbsDown, ThumbsUp, Trash2, X } from "lucide-react";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { Markdown } from "@/components/Markdown";
import { cx } from "@/components/ui";
import { api, postChatStream } from "@/lib/api";
import { formatTokens, formatUsd } from "@/lib/format";
import type { AssistantModel, ChatDetail, ChatMessage, ChatSession } from "@/lib/types";

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

function emptyMessage(role: "user" | "assistant", content: string): ChatMessage {
  return { id: -Date.now(), role, content, tools_used: [], sources: [], prompt_tokens: 0,
    completion_tokens: 0, cost_usd: null, latency_ms: 0, rating: null, created_at: new Date().toISOString() };
}

function AssistantBubble({ message, canInsert, onRate, onInsert, inserted }: {
  message: ChatMessage;
  canInsert: boolean;
  onRate: (id: number, rating: number) => void;
  onInsert: (message: ChatMessage) => void;
  inserted: boolean;
}) {
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
      {message.id > 0 && (
        <div className="mt-1.5 flex items-center gap-1 border-t border-line pt-1.5">
          <button title="Hữu ích" onClick={() => onRate(message.id, message.rating === 1 ? 0 : 1)}
            className={cx("rounded-md p-1", message.rating === 1 ? "bg-green-50 text-green-700" : "text-muted hover:bg-paper hover:text-ink")}>
            <ThumbsUp className="size-3.5" />
          </button>
          <button title="Chưa tốt" onClick={() => onRate(message.id, message.rating === -1 ? 0 : -1)}
            className={cx("rounded-md p-1", message.rating === -1 ? "bg-red-50 text-red-700" : "text-muted hover:bg-paper hover:text-ink")}>
            <ThumbsDown className="size-3.5" />
          </button>
          {canInsert && (
            <button title="Chèn câu trả lời vào mục báo cáo đang sửa" onClick={() => onInsert(message)}
              className="ml-auto flex items-center gap-1 rounded-md px-1.5 py-1 text-[11px] text-brand-700 hover:bg-brand-50">
              <FilePlus2 className="size-3.5" />{inserted ? "Đã chèn ✓" : "Đưa vào báo cáo"}
            </button>
          )}
        </div>
      )}
    </div>
  );
}

export function AssistantWidget() {
  const queryClient = useQueryClient();
  const pathname = usePathname();
  const [open, setOpen] = useState(() => store.get("hd-assistant-open") === "1");
  const [view, setView] = useState<"chat" | "history">("chat");
  const [sessionId, setSessionId] = useState<string | null>(() => store.get("hd-assistant-session"));
  const [modelIndex, setModelIndex] = useState(() => Number(store.get("hd-assistant-model") ?? 0) || 0);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [live, setLive] = useState<string | null>(null);
  const [toolStatus, setToolStatus] = useState<string | null>(null);
  const [failed, setFailed] = useState<string | null>(null);
  const [withContext, setWithContext] = useState(true);
  const [insertedId, setInsertedId] = useState<number | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  // Ngữ cảnh từ trang đang xem: /clients/7… hoặc /reports/abc…(/edit)
  const clientCtx = pathname?.match(/^\/clients\/(\d+)/)?.[1] ?? null;
  const reportCtx = pathname?.match(/^\/reports\/([^/]+)/)?.[1] ?? null;
  const isEditPage = !!reportCtx && pathname?.includes("/edit");
  const activeCtx = withContext ? { client: clientCtx, report: reportCtx } : { client: null, report: null };

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
  }, [messages, live, toolStatus, open]);
  useEffect(() => () => abortRef.current?.abort(), []);

  const openSession = async (id: string) => {
    const detail = await api.get<ChatDetail>(`/assistant/sessions/${id}`);
    setSessionId(detail.session.id);
    setMessages(detail.messages);
    setView("chat");
  };

  const streaming = live !== null;

  const submit = async (raw: string) => {
    const text = raw.trim();
    if (!text || streaming) return;
    abortRef.current?.abort();
    const ctrl = new AbortController();
    abortRef.current = ctrl;
    setDraft("");
    setFailed(null);
    setInsertedId(null);
    setMessages((list) => [...list, emptyMessage("user", text)]);
    setLive("");
    setToolStatus(null);
    try {
      await postChatStream("/assistant/chat/stream", {
        session_id: sessionId,
        model_index: modelIndex,
        message: text,
        context_client_id: activeCtx.client ? Number(activeCtx.client) : null,
        context_report_id: activeCtx.report,
      }, {
        onMeta: (meta) => setSessionId(meta.session_id),
        onToken: (piece) => setLive((cur) => (cur ?? "") + piece),
        onTool: (info) => {
          if (info.phase === "start") setToolStatus(`Đang tra ${TOOL_LABEL[info.tool] ?? info.tool}…`);
          else setToolStatus(null);
        },
        onDone: (message) => {
          setMessages((list) => [...list, message]);
          setLive(null);
          setToolStatus(null);
          queryClient.invalidateQueries({ queryKey: ["assistant-sessions"] });
        },
      }, ctrl.signal);
    } catch (e) {
      if ((e as Error).name === "AbortError") return;
      setLive(null);
      setToolStatus(null);
      setFailed((e as Error).message || "Gửi thất bại, thử lại sau.");
      setDraft(text);
    }
  };

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

  const rate = useMutation({
    mutationFn: ({ id, rating }: { id: number; rating: number }) =>
      api.post<ChatMessage>(`/assistant/messages/${id}/rate`, { rating }),
    onSuccess: (updated) => {
      setMessages((list) => list.map((m) => (m.id === updated.id ? updated : m)));
    },
  });

  const insertIntoReport = (message: ChatMessage) => {
    if (!reportCtx) return;
    window.dispatchEvent(new CustomEvent("hd:assistant-insert", {
      detail: { reportId: reportCtx, text: message.content },
    }));
    setInsertedId(message.id);
  };

  const suggestions: string[] = activeCtx.client
    ? ["Điểm mạnh của khách hàng này là gì?", "Chiến lược và Authority của khách này?", "Tóm tắt nhanh chart của khách này"]
    : activeCtx.report
      ? ["Tóm tắt báo cáo này trong 5 câu", "Báo cáo này viết về ai, Type gì?", "Gợi ý 3 điểm nhấn để tư vấn từ báo cáo này"]
      : ["Generator vận hành thế nào?", "Phân biệt Strategy và Authority?", "Tính chart cho người sinh 15/05/1990 lúc 08:30"];

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
        {(clientCtx || reportCtx) && (
          <button onClick={() => setWithContext((v) => !v)} title="Bật/tắt ngữ cảnh trang đang xem"
            className={cx("mt-1.5 flex w-full items-center gap-1.5 rounded-md px-2 py-1 text-left text-[11px]",
              withContext ? "bg-brand-50 text-brand-800" : "bg-paper text-muted line-through")}>
            <span className="truncate">
              {withContext ? "◉" : "○"} Ngữ cảnh: {clientCtx ? `khách hàng #${clientCtx}` : `báo cáo ${reportCtx?.slice(0, 8)}…`}
            </span>
          </button>
        )}
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
            {messages.length === 0 && !streaming && (
              <div className="rounded-xl border border-line bg-white p-3 text-xs text-muted">
                Hỏi mình về Type, Strategy, Authority, Centers, Channels, Gates… hoặc nhờ tính chart
                (vd: “Tính chart cho người sinh 15/05/1990 lúc 08:30”).
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {suggestions.map((s) => (
                    <button key={s} onClick={() => submit(s)}
                      className="rounded-full border border-brand-200 bg-brand-50 px-2.5 py-1 text-[11px] text-brand-800 hover:bg-brand-100">
                      {s}
                    </button>
                  ))}
                </div>
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
                <AssistantBubble key={m.id} message={m} canInsert={!!isEditPage}
                  onRate={(id, rating) => rate.mutate({ id, rating })}
                  onInsert={insertIntoReport} inserted={insertedId === m.id} />
              ),
            )}
            {live !== null && (
              <div className="max-w-[92%] rounded-xl rounded-tl-sm border border-line bg-white px-3 py-2 shadow-sm">
                {live ? <Markdown>{live}</Markdown> : <span className="text-xs text-muted">Đang trả lời…</span>}
                <span className="ml-1 inline-block h-3.5 w-1.5 animate-pulse rounded-sm bg-brand-400 align-middle" />
              </div>
            )}
            {toolStatus && (
              <div className="flex items-center gap-2 text-xs text-muted">
                <Loader2 className="size-4 animate-spin" /> {toolStatus}
              </div>
            )}
            {streaming && (
              <button onClick={() => abortRef.current?.abort()}
                className="rounded-full border border-line bg-white px-3 py-1 text-[11px] text-muted hover:text-red-700">
                Dừng lại
              </button>
            )}
            {failed && (
              <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-xs text-red-800">
                {failed}
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
                    submit(draft);
                  }
                }}
                placeholder="Hỏi về Human Design… (Enter để gửi)"
                maxLength={2000}
                className="max-h-28 min-h-10 flex-1 resize-none rounded-lg border border-line px-3 py-2 text-sm focus:border-brand-500 focus:outline-none"
              />
              <button onClick={() => submit(draft)} disabled={streaming || !draft.trim()}
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
