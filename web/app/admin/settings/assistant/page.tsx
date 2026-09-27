"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ChevronDown, Trash2 } from "lucide-react";
import { useState } from "react";
import { Markdown } from "@/components/Markdown";
import { Button, Card, ErrorBox, PageHeader, Spinner, cx } from "@/components/ui";
import { api, qs } from "@/lib/api";
import { useMe } from "@/lib/auth";
import { formatTimestamp, formatTokens, formatUsd } from "@/lib/format";
import type { ChatAdminSession, ChatAdminStats, ChatDetail } from "@/lib/types";

function SessionRow({ session }: { session: ChatAdminSession }) {
  const [open, setOpen] = useState(false);
  const queryClient = useQueryClient();
  const detail = useQuery({
    queryKey: ["assistant-admin-detail", session.id],
    queryFn: () => api.get<ChatDetail>(`/assistant/sessions/${session.id}`),
    enabled: open,
  });
  const remove = useMutation({
    mutationFn: () => api.del(`/assistant/sessions/${session.id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["assistant-admin-sessions"] }),
  });
  return (
    <div className="border-b border-line last:border-0">
      <div className="flex flex-wrap items-center gap-3 px-4 py-3">
        <button onClick={() => setOpen((v) => !v)} className="min-w-0 flex-1 text-left">
          <div className="truncate text-sm font-medium text-ink">{session.title}</div>
          <div className="text-xs text-muted">
            {session.user_name || session.user_email} · {session.model || "—"} · {session.message_count} tin ·{" "}
            {formatUsd(session.total_cost_usd)} · {formatTimestamp(session.updated_at)}
          </div>
        </button>
        <ChevronDown className={cx("size-4 text-muted transition-transform", open && "rotate-180")} aria-hidden />
        <button title="Xóa phiên này"
          onClick={() => confirm("Xóa phiên chat này và toàn bộ tin nhắn?") && remove.mutate()}
          className="rounded-md p-1.5 text-muted hover:bg-red-50 hover:text-red-700">
          <Trash2 className="size-4" />
        </button>
      </div>
      {open && (
        <div className="space-y-2 bg-paper px-4 py-3">
          {detail.isLoading && <Spinner />}
          <ErrorBox error={detail.error} />
          {(detail.data?.messages ?? []).map((m) => (
            <div key={m.id} className={cx("max-w-3xl rounded-lg px-3 py-2 text-sm", m.role === "user" ? "ml-auto bg-brand-500 text-white" : "border border-line bg-white")}>
              {m.role === "user" ? (
                <span className="whitespace-pre-wrap">{m.content}</span>
              ) : (
                <>
                  <Markdown>{m.content}</Markdown>
                  <div className="mt-1 text-[11px] text-muted">
                    {m.sources.length > 0 && <>Nguồn: {m.sources.join(" · ")} · </>}
                    {formatTokens(m.prompt_tokens + m.completion_tokens)} token · {formatUsd(m.cost_usd)}
                    {m.rating === 1 && <> · <span className="text-green-700">👍 hữu ích</span></>}
                    {m.rating === -1 && <> · <span className="text-red-700">👎 chưa tốt</span></>}
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function AssistantAdminPage() {
  const me = useMe();
  const isAdmin = me.data?.role === "admin";
  const [days, setDays] = useState(30);
  const stats = useQuery({
    queryKey: ["assistant-admin-stats", days],
    queryFn: () => api.get<ChatAdminStats>(`/assistant/admin/stats${qs({ days })}`),
    enabled: isAdmin,
  });
  const sessions = useQuery({
    queryKey: ["assistant-admin-sessions"],
    queryFn: () => api.get<ChatAdminSession[]>("/assistant/admin/sessions?limit=50"),
    enabled: isAdmin,
  });

  if (me.data && !isAdmin) return <ErrorBox error="Chỉ quản trị viên được truy cập trang này." />;
  if (stats.isLoading || !stats.data) return stats.error ? <ErrorBox error={stats.error} /> : <Spinner />;
  const t = stats.data;
  const cards = [
    { label: "Phiên chat", value: `${t.sessions}` },
    { label: "Tin nhắn AI", value: `${t.messages}` },
    { label: "Token vào / ra", value: `${formatTokens(t.prompt_tokens)} / ${formatTokens(t.completion_tokens)}` },
    { label: "Chi phí ước tính", value: formatUsd(t.cost_usd) },
    { label: "Đánh giá 👍 / 👎", value: `${t.likes} / ${t.dislikes}` },
  ];

  return (
    <>
      <PageHeader
        title="Trợ lý AI"
        description="Ai đang dùng widget trợ lý tra cứu, hỏi gì, tốn bao nhiêu — coaches chỉ thấy phiên của mình, admin thấy tất cả."
      />
      <div className="mb-4 flex gap-1 self-start rounded-lg border border-line bg-white p-1 text-sm">
        {[7, 30, 90].map((d) => (
          <button key={d} type="button" onClick={() => setDays(d)}
            className={cx("rounded-md px-3 py-1", days === d ? "bg-brand-500 text-white" : "text-muted hover:bg-paper")}>
            {d} ngày
          </button>
        ))}
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {cards.map((c) => (
          <Card key={c.label} className="p-4">
            <div className="text-xs text-muted">{c.label}</div>
            <div className="mt-1 text-xl font-bold text-ink">{c.value}</div>
          </Card>
        ))}
      </div>

      <h2 className="mb-3 mt-8 text-lg font-semibold text-ink">Theo người dùng</h2>
      <Card className="overflow-x-auto">
        {t.by_user.length === 0 ? (
          <p className="p-5 text-sm text-muted">Chưa ai dùng trợ lý trong {t.days} ngày qua.</p>
        ) : (
          <table className="w-full min-w-[36rem] text-sm">
            <thead>
              <tr className="border-b border-line text-left text-xs uppercase tracking-wider text-muted">
                <th className="px-4 py-3 font-medium">Người dùng</th>
                <th className="px-4 py-3 text-right font-medium">Phiên</th>
                <th className="px-4 py-3 text-right font-medium">Tin AI</th>
                <th className="px-4 py-3 text-right font-medium">Chi phí</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {t.by_user.map((u) => (
                <tr key={u.user_id}>
                  <td className="px-4 py-2.5">
                    <span className="font-medium text-ink">{u.full_name || u.email}</span>
                    {u.full_name && <span className="block text-xs text-muted">{u.email}</span>}
                  </td>
                  <td className="px-4 py-2.5 text-right">{u.sessions}</td>
                  <td className="px-4 py-2.5 text-right">{u.messages}</td>
                  <td className="px-4 py-2.5 text-right">{formatUsd(u.cost_usd)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>

      <h2 className="mb-3 mt-8 text-lg font-semibold text-ink">Phiên gần đây</h2>
      <Card>
        {sessions.isLoading && <Spinner />}
        <ErrorBox error={sessions.error} className="m-4" />
        {(sessions.data ?? []).map((s) => (
          <SessionRow key={s.id} session={s} />
        ))}
        {sessions.data?.length === 0 && <p className="p-5 text-sm text-muted">Chưa có phiên nào.</p>}
      </Card>
    </>
  );
}
