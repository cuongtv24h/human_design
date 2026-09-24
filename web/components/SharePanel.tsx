"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, Copy, ExternalLink, Link2, ShieldOff } from "lucide-react";
import { useState } from "react";
import { Badge, Button, Card, Checkbox, ErrorBox, Field, Input, Spinner } from "@/components/ui";
import { api } from "@/lib/api";
import { absoluteUrl, copyText } from "@/lib/clipboard";
import { formatTimestamp } from "@/lib/format";
import type { Share, ShareCreated, ShareFormat } from "@/lib/types";

const FORMAT_OPTIONS: { id: ShareFormat; label: string; description: string }[] = [
  { id: "pdf", label: "PDF", description: "Bản in hoàn chỉnh — phù hợp nhất cho khách hàng" },
  { id: "docx", label: "Word (.docx)", description: "Khi khách muốn tự ghi chú, chỉnh sửa" },
  { id: "markdown", label: "Markdown (.md)", description: "Cho người dùng Notion / Obsidian" },
];
const EXPIRY = [
  { days: 7, label: "7 ngày" },
  { days: 30, label: "30 ngày" },
  { days: 90, label: "3 tháng" },
  { days: 365, label: "1 năm" },
];
const STATUS: Record<Share["status"], { label: string; tone: "brand" | "gold" | "stone" }> = {
  active: { label: "Đang hoạt động", tone: "brand" },
  expired: { label: "Hết hạn", tone: "stone" },
  revoked: { label: "Đã thu hồi", tone: "stone" },
};

export function CopyField({ value, hint }: { value: string; hint?: string }) {
  const [copied, setCopied] = useState<boolean | null>(null);
  return (
    <div>
      <div className="flex gap-2">
        <Input readOnly value={value} onFocus={(e) => e.currentTarget.select()} aria-label="Đường link" className="font-mono text-xs" />
        <Button type="button" variant="secondary" className="shrink-0 px-3" onClick={async () => setCopied(await copyText(value))}>
          {copied ? <Check className="size-4 text-emerald-600" /> : <Copy className="size-4" />} {copied ? "Đã chép" : "Chép"}
        </Button>
      </div>
      {copied === false && <p className="mt-1 text-xs text-amber-700">Trình duyệt chặn sao chép tự động — hãy chọn ô trên rồi nhấn Ctrl/⌘ + C.</p>}
      {hint && <p className="mt-1 text-xs text-muted">{hint}</p>}
    </div>
  );
}

export function SharePanel({ reportId, clientName }: { reportId: string; clientName: string }) {
  const queryClient = useQueryClient();
  const [formats, setFormats] = useState<ShareFormat[]>(["pdf"]);
  const [days, setDays] = useState(30);
  const [label, setLabel] = useState("");
  const [created, setCreated] = useState<string | null>(null);

  const shares = useQuery({ queryKey: ["shares", reportId], queryFn: () => api.get<Share[]>(`/reports/${reportId}/shares`) });
  const create = useMutation({
    mutationFn: () => api.post<ShareCreated>(`/reports/${reportId}/shares`, { formats, expires_days: days, label }),
    onSuccess: (res) => {
      setCreated(absoluteUrl(res.url));
      setLabel("");
      queryClient.invalidateQueries({ queryKey: ["shares", reportId] });
    },
  });
  const revoke = useMutation({
    mutationFn: (id: number) => api.post<Share>(`/shares/${id}/revoke`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["shares", reportId] }),
  });

  const toggle = (id: ShareFormat) => setFormats((cur) => (cur.includes(id) ? cur.filter((f) => f !== id) : [...cur, id]));

  return (
    <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,26rem)_minmax(0,1fr)]">
      <Card className="space-y-4 p-5">
        <div>
          <h2 className="flex items-center gap-2 font-semibold text-ink"><Link2 className="size-4 text-brand-600" /> Tạo link cho khách hàng</h2>
          <p className="mt-1 text-sm text-muted">
            {clientName} mở link trên điện thoại để xem Infographic, đọc báo cáo và tải các định dạng bạn cho phép — không cần tài khoản.
            Link luôn hiển thị phiên bản mới nhất của báo cáo.
          </p>
        </div>
        <fieldset className="space-y-2">
          <legend className="mb-1 text-sm font-medium text-ink">Cho phép tải</legend>
          {FORMAT_OPTIONS.map((f) => (
            <Checkbox key={f.id} checked={formats.includes(f.id)} onChange={() => toggle(f.id)} label={f.label} description={f.description} />
          ))}
          {formats.length === 0 && <p className="text-xs text-muted">Không chọn định dạng nào: khách chỉ xem trực tuyến.</p>}
        </fieldset>
        <Field label="Hiệu lực" htmlFor="share-days">
          <select id="share-days" value={days} onChange={(e) => setDays(Number(e.target.value))}
            className="block w-full rounded-lg border border-line bg-white px-3 py-2 text-sm">
            {EXPIRY.map((x) => <option key={x.days} value={x.days}>{x.label}</option>)}
          </select>
        </Field>
        <Field label="Ghi chú (chỉ bạn thấy)" htmlFor="share-label" hint="Ví dụ: Gửi qua Zalo 24/9">
          <Input id="share-label" value={label} maxLength={120} onChange={(e) => setLabel(e.target.value)} />
        </Field>
        <ErrorBox error={create.error} />
        <Button onClick={() => create.mutate()} loading={create.isPending}><Link2 className="size-4" /> Tạo link chia sẻ</Button>
        {created && (
          <div className="space-y-2 rounded-lg border border-emerald-200 bg-emerald-50 p-3">
            <div className="text-sm font-medium text-emerald-900">Link đã sẵn sàng</div>
            <CopyField value={created} hint="Link chỉ hiển thị một lần này — hãy chép và gửi ngay. Mất link thì tạo link mới." />
            <a href={created} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-sm text-brand-700 hover:underline">
              <ExternalLink className="size-3.5" /> Mở thử như khách hàng
            </a>
          </div>
        )}
      </Card>

      <Card>
        <div className="border-b border-line px-5 py-3 text-sm font-semibold text-ink">Link đã tạo</div>
        {shares.isLoading ? (
          <Spinner />
        ) : !shares.data?.length ? (
          <p className="px-5 py-6 text-sm text-muted">Chưa có link chia sẻ nào cho báo cáo này.</p>
        ) : (
          <ul className="divide-y divide-line">
            {shares.data.map((s) => (
              <li key={s.id} className="flex flex-wrap items-center justify-between gap-3 px-5 py-3">
                <div className="min-w-0 text-sm">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge tone={STATUS[s.status].tone}>{STATUS[s.status].label}</Badge>
                    <span className="font-medium text-ink">{s.label || `Link #${s.id}`}</span>
                  </div>
                  <div className="mt-1 text-xs text-muted">
                    Tạo {formatTimestamp(s.created_at)} · {s.status === "revoked" ? `thu hồi ${formatTimestamp(s.revoked_at)}` : `hết hạn ${formatTimestamp(s.expires_at)}`}
                    {" · "}{s.view_count} lượt xem{s.last_viewed_at ? ` (gần nhất ${formatTimestamp(s.last_viewed_at)})` : ""}
                    {" · "}Tải: {s.formats.length ? s.formats.map((f) => f.toUpperCase()).join(", ") : "không"}
                  </div>
                </div>
                {s.status === "active" && (
                  <Button variant="danger" className="px-3 py-1.5 text-xs" loading={revoke.isPending && revoke.variables === s.id}
                    onClick={() => confirm("Thu hồi link này? Khách hàng sẽ không mở được nữa.") && revoke.mutate(s.id)}>
                    <ShieldOff className="size-3.5" /> Thu hồi
                  </Button>
                )}
              </li>
            ))}
          </ul>
        )}
        <ErrorBox error={revoke.error} className="m-4" />
      </Card>
    </div>
  );
}
