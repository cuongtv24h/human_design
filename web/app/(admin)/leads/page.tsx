"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Badge, Button, Card, ErrorBox, PageHeader, Spinner } from "@/components/ui";
import { api, qs } from "@/lib/api";
import { STYLES, THEMES } from "@/lib/game/content";
import { formatTimestamp } from "@/lib/format";
import type { GameFunnelStat, GameLeadOut } from "@/lib/types";

const STATUSES = [
  { value: "", label: "Tất cả" },
  { value: "new", label: "Mới" },
  { value: "contacted", label: "Đã liên hệ" },
  { value: "converted", label: "Đã chốt" },
  { value: "spam", label: "Rác" },
];

const STATUS_TONE: Record<string, "brand" | "gold" | "stone"> = {
  new: "gold",
  contacted: "brand",
  converted: "brand",
  spam: "stone",
};

const FUNNEL_STEPS = [
  { key: "game_start", label: "Bắt đầu" },
  { key: "game_complete", label: "Xong quiz" },
  { key: "bridge_submit", label: "Nhập ngày sinh" },
  { key: "lead_submit", label: "Để lại liên hệ" },
];

function FunnelStrip() {
  const funnel = useQuery({
    queryKey: ["game-funnel"],
    queryFn: () => api.get<GameFunnelStat[]>("/game/leads/funnel"),
  });
  if (funnel.isLoading) return <Spinner />;
  if (funnel.isError || !funnel.data) return null;
  const byTheme: Record<string, Record<string, number>> = {};
  for (const r of funnel.data) {
    if (!byTheme[r.theme]) byTheme[r.theme] = {};
    byTheme[r.theme][r.name] = r.count;
  }
  const slugs = Object.keys(byTheme).sort();
  if (slugs.length === 0) return null;
  return (
    <Card className="mb-4 space-y-3 p-4">
      <div className="text-sm font-bold text-ink">Phễu theo theme (đo A/B)</div>
      {slugs.map((slug) => {
        const counts = byTheme[slug];
        const start = counts["game_start"] ?? 0;
        const lead = counts["lead_submit"] ?? 0;
        return (
          <div key={slug} className="text-sm">
            <div className="font-medium text-ink">
                  {slug ? (THEMES[slug]?.name ?? slug) : "(chung)"}{" "}
              {start > 0 && (
                <span className="text-muted">· chốt {Math.round((lead / start) * 100)}%</span>
              )}
            </div>
            <div className="mt-1 flex flex-wrap gap-x-4 gap-y-1 text-muted">
              {FUNNEL_STEPS.map((s) => (
                <span key={s.key}>
                  {s.label}: <strong className="text-ink">{counts[s.key] ?? 0}</strong>
                </span>
              ))}
            </div>
          </div>
        );
      })}
    </Card>
  );
}

export default function LeadsPage() {
  const queryClient = useQueryClient();
  const [status, setStatus] = useState("");
  const list = useQuery({
    queryKey: ["game-leads", status],
    queryFn: () => api.get<GameLeadOut[]>(`/game/leads${qs({ status })}`),
  });
  const mark = useMutation({
    mutationFn: ({ id, value }: { id: number; value: string }) =>
      api.patch<GameLeadOut>(`/game/leads/${id}`, { status: value }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["game-leads"] }),
  });

  return (
    <>
      <PageHeader
        title="Khách tiềm năng"
        description="Người chơi game “Đúng Thiết Kế” để lại liên hệ để nhận báo cáo đầy đủ."
      />
      <ErrorBox error={list.error ?? mark.error} className="mb-4" />
      <FunnelStrip />
      <Card className="mb-4 flex flex-wrap items-center gap-2 p-4">
        {STATUSES.map((s) => (
          <Button
            key={s.value}
            variant={status === s.value ? "primary" : "secondary"}
            className="px-3 py-1.5 text-sm"
            onClick={() => setStatus(s.value)}
          >
            {s.label}
          </Button>
        ))}
      </Card>
      {list.isLoading ? (
        <Spinner />
      ) : (list.data ?? []).length === 0 ? (
        <Card className="p-10 text-center text-sm text-muted">
          Chưa có khách tiềm năng nào. Chia sẻ game để thu lead đầu tiên.
        </Card>
      ) : (
        <Card className="overflow-x-auto">
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead>
              <tr className="border-b border-line text-xs uppercase tracking-wider text-muted">
                <th className="px-4 py-3">Ngày</th>
                <th className="px-4 py-3">Tên</th>
                <th className="px-4 py-3">Liên hệ</th>
                <th className="px-4 py-3">Ngày sinh</th>
                <th className="px-4 py-3">Phong cách</th>
                <th className="px-4 py-3">Trạng thái</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {(list.data ?? []).map((lead) => (
                <tr key={lead.id} className="align-top">
                  <td className="whitespace-nowrap px-4 py-3 text-muted">
                    {formatTimestamp(lead.created_at)}
                  </td>
                  <td className="px-4 py-3 font-medium text-ink">{lead.name}</td>
                  <td className="px-4 py-3 text-ink">{lead.contact}</td>
                  <td className="whitespace-nowrap px-4 py-3 text-ink">
                    {lead.birth_date} {lead.birth_time}
                    {lead.birth_place ? <span className="text-muted"> · {lead.birth_place}</span> : null}
                  </td>
                  <td className="px-4 py-3">
                    {lead.quiz?.style && STYLES[lead.quiz.style as keyof typeof STYLES] ? (
                      <span>
                        {STYLES[lead.quiz.style as keyof typeof STYLES].icon}{" "}
                        {STYLES[lead.quiz.style as keyof typeof STYLES].name}
                        {typeof lead.quiz.deviation === "number" ? (
                          <span className="text-muted"> · lệch {lead.quiz.deviation}%</span>
                        ) : null}
                      </span>
                    ) : (
                      <span className="text-muted">—</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <Badge tone={STATUS_TONE[lead.status] ?? "stone"}>
                        {STATUSES.find((s) => s.value === lead.status)?.label ?? lead.status}
                      </Badge>
                      <select
                        value={lead.status}
                        disabled={mark.isPending}
                        onChange={(e) => mark.mutate({ id: lead.id, value: e.target.value })}
                        className="rounded-lg border border-line bg-white px-2 py-1 text-xs"
                        aria-label="Đổi trạng thái"
                      >
                        {STATUSES.filter((s) => s.value).map((s) => (
                          <option key={s.value} value={s.value}>
                            {s.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </>
  );
}
