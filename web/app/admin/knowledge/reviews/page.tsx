"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, Inbox, RefreshCw, ScanSearch, Sparkles, X } from "lucide-react";
import { useEffect, useState } from "react";
import { Badge, Button, ErrorBox, Field, Modal, Spinner, Textarea } from "@/components/ui";
import { api } from "@/lib/api";
import { useMe } from "@/lib/auth";

// Duyệt đóng góp (Admin): master–detail + stats strip.
// Coach KHÔNG vào được (useMe guard + API 403). Duyệt = xuất kho ngay.

type Submission = {
  id: number;
  title: string;
  target_file: string;
  source_url: string;
  status: "pending" | "approved" | "rejected";
  dedupe_report: { max_similarity?: number; level?: string; matches?: { file: string; section: string; similarity: number }[] };
  ai_notes: Record<string, string> | null;
  reject_reason: string | null;
  contributor: string;
  created_at: string | null;
  decided_at: string | null;
};

type Detail = Submission & {
  content_md: string;
  preview: { file: string; title: string; section: string; score: number }[];
  can_review: boolean;
};

type Stats = {
  submissions: { pending: number; approved: number; rejected: number; total: number };
  queries_30d: { total: number; avg_took_ms: number | null; top: { query: string; n: number }[] };
};

type ScanResult = { chunks: number; pairs_found: number; pairs: { a: { file: string; section: string }; b: { file: string; section: string }; similarity: number }[]; duration_ms: number };

const TONE = { pending: "gold", approved: "brand", rejected: "stone" } as const;

export default function KnowledgeReviewsPage() {
  const me = useMe();
  const qc = useQueryClient();
  const [selected, setSelected] = useState<number | null>(null);
  const [rejecting, setRejecting] = useState(false);
  const [reason, setReason] = useState("");
  const [editContent, setEditContent] = useState<string | null>(null);
  const [scan, setScan] = useState<ScanResult | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const stats = useQuery({
    queryKey: ["kb-stats"],
    queryFn: () => api.get<Stats>("/knowledge/stats"),
    enabled: me.data?.role === "admin",
  });
  const list = useQuery({
    queryKey: ["kb-submissions", "all"],
    queryFn: () => api.get<{ items: Submission[]; total: number }>("/knowledge/submissions"),
    enabled: me.data?.role === "admin",
  });
  const detail = useQuery({
    queryKey: ["kb-submission", selected],
    queryFn: () => api.get<Detail>(`/knowledge/submissions/${selected}`),
    enabled: selected !== null && me.data?.role === "admin",
  });

  useEffect(() => {
    if (selected === null) {
      const first = list.data?.items.find((s) => s.status === "pending")
        ?? list.data?.items[0];
      if (first) setSelected(first.id);
    }
  }, [list.data, selected]);

  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ["kb-submissions"] });
    qc.invalidateQueries({ queryKey: ["kb-stats"] });
    if (selected !== null) qc.invalidateQueries({ queryKey: ["kb-submission", selected] });
  };

  const approve = useMutation({
    mutationFn: () =>
      api.post<{ published: { file: string; mode: string } }>(
        `/knowledge/submissions/${selected}/approve`,
        editContent !== null ? { content_md: editContent } : {},
      ),
    onSuccess: (res) => {
      setNotice(`Đã duyệt — xuất kho file \`${res.published.file}\` (${res.published.mode}).`);
      setEditContent(null);
      invalidate();
    },
    onError: (error) => {
      setNotice(null);
      console.warn(error);
    },
  });
  const reject = useMutation({
    mutationFn: () => api.post(`/knowledge/submissions/${selected}/reject`, { reason }),
    onSuccess: () => {
      setRejecting(false);
      setReason("");
      invalidate();
    },
  });
  const ai = useMutation({
    mutationFn: () => api.post<{ ran: boolean; ai_notes: Record<string, string> | null; error: string | null }>(
      `/knowledge/submissions/${selected}/ai-review`, {}),
    onSuccess: (res) => {
      setNotice(res.ran ? "AI đã ghi ghi chú kiểm duyệt." : `AI chưa chạy được: ${res.error}`);
      invalidate();
    },
  });
  const dedupeScan = useMutation({
    mutationFn: () => api.post<ScanResult>("/knowledge/dedupe-scan", {}),
    onSuccess: setScan,
  });

  if (me.isLoading) return <Spinner />;
  if (me.data?.role !== "admin") {
    return <p className="text-sm text-muted">Chỉ Admin mới được duyệt đóng góp.</p>;
  }

  const items = list.data?.items ?? [];
  const current = detail.data;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="flex items-center gap-2 text-xl font-semibold"><Inbox size={18} /> Duyệt đóng góp</h1>
          <p className="mt-1 text-sm text-muted">
            Coach chỉ nộp bài; toàn quyền duyệt (duyệt/từ chối/AI) thuộc Admin ở đây.
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={() => dedupeScan.mutate()} disabled={dedupeScan.isPending}>
            {dedupeScan.isPending ? <Spinner label="" /> : <ScanSearch size={16} />} Quét trùng lặp toàn kho
          </Button>
          <Button variant="ghost" onClick={() => list.refetch()} title="Tải lại">
            <RefreshCw size={16} />
          </Button>
        </div>
      </div>

      {stats.data ? (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <StatCard label="Chờ duyệt" value={stats.data.submissions.pending} accent />
            <StatCard label="Đã duyệt" value={stats.data.submissions.approved} />
          <StatCard label="Từ chối" value={stats.data.submissions.rejected} />
          <StatCard label="Truy vấn 30 ngày" value={stats.data.queries_30d.total}
            hint={stats.data.queries_30d.avg_took_ms !== null ? `bình quân ${stats.data.queries_30d.avg_took_ms}ms` : undefined} />
        </div>
      ) : null}

      {notice ? (
        <div className="rounded-lg border border-brand-500/30 bg-brand-50 px-4 py-3 text-sm">{notice}</div>
      ) : null}
      {list.error ? <ErrorBox error={list.error} /> : null}

      <div className="grid gap-4 lg:grid-cols-[320px_minmax(0,1fr)]">
        <aside className="max-h-[70vh] space-y-2 overflow-y-auto pr-1">
          {list.isLoading ? <Spinner /> : null}
          {items.map((sub) => (
            <button key={sub.id} type="button" onClick={() => { setSelected(sub.id); setEditContent(null); setNotice(null); }}
              className={`w-full rounded-lg border px-3 py-2.5 text-left text-sm transition ${
                selected === sub.id ? "border-brand-500 bg-brand-50" : "border-line bg-white hover:border-brand-500/40"
              }`}>
              <div className="flex items-center justify-between gap-2">
                <span className="font-medium line-clamp-1">{sub.title}</span>
                <Badge tone={TONE[sub.status]}>{sub.status === "pending" ? "Chờ" : sub.status === "approved" ? "Duyệt" : "Từ chối"}</Badge>
              </div>
              <span className="mt-0.5 block text-xs text-muted">
                #{sub.id} · {sub.contributor}
                {sub.created_at ? ` · ${new Date(sub.created_at).toLocaleDateString("vi-VN")}` : ""}
              </span>
            </button>
          ))}
          {items.length === 0 && !list.isLoading ? (
            <p className="rounded-lg border border-dashed border-line px-3 py-6 text-center text-sm text-muted">
              Chưa có bài đóng góp nào.
            </p>
          ) : null}
        </aside>

        <section className="min-h-[320px] rounded-lg border border-line bg-white p-5">
          {!current ? <Spinner /> : (
            <div className="space-y-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h2 className="text-lg font-semibold">{current.title}</h2>
                  <p className="mt-0.5 text-xs text-muted">
                    Bởi {current.contributor} · {current.created_at ? new Date(current.created_at).toLocaleString("vi-VN") : ""}
                    {current.source_url ? (
                      <> · <a className="text-brand-600 underline" href={current.source_url} target="_blank" rel="noreferrer">nguồn</a></>
                    ) : null}
                  </p>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <Button variant="secondary" onClick={() => ai.mutate()} disabled={!current.can_review || ai.isPending}>
                    {ai.isPending ? <Spinner label="" /> : <Sparkles size={16} />} AI kiểm duyệt
                  </Button>
                  {current.can_review ? (
                    <>
                      <Button onClick={() => approve.mutate()} disabled={approve.isPending}>
                        <Check size={16} /> {editContent !== null ? "Duyệt bản đã sửa" : "Duyệt & xuất kho"}
                      </Button>
                      <Button variant="danger" onClick={() => setRejecting(true)}>
                        <X size={16} /> Từ chối
                      </Button>
                    </>
                  ) : (
                    <Badge tone={TONE[current.status]}>
                      {current.status === "pending" ? "Chờ duyệt" : current.status === "approved" ? "Đã duyệt" : "Đã từ chối"}
                    </Badge>
                  )}
                </div>
              </div>

              {approve.error ? <ErrorBox error={approve.error} /> : null}
              {reject.error ? <ErrorBox error={reject.error} /> : null}
              {current.reject_reason ? (
                <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
                  Lý do từ chối: {current.reject_reason}
                </div>
              ) : null}
              {current.ai_notes ? (
                <div className="rounded-lg border border-gold-500/40 bg-gold-100/50 px-4 py-3 text-sm">
                  <p className="mb-1 font-semibold text-gold-500">AI kiểm duyệt (gợi ý)</p>
                  <ul className="list-inside list-disc space-y-0.5">
                    {Object.entries(current.ai_notes).map(([k, v]) => v ? (
                      <li key={k}><span className="font-medium">{k}:</span> {v}</li>
                    ) : null)}
                  </ul>
                </div>
              ) : null}

              <div className="grid gap-3 sm:grid-cols-3">
                <div className="rounded-lg bg-paper px-3 py-2 text-xs">
                  <p className="text-muted">Trùng tối đa</p>
                  <p className="text-sm font-semibold">
                    {Math.round((current.dedupe_report.max_similarity ?? 0) * 100)}%
                    {current.dedupe_report.level === "hard" ? " (cứng)" : current.dedupe_report.level === "soft" ? " (cảnh báo)" : ""}
                  </p>
                </div>
                <div className="rounded-lg bg-paper px-3 py-2 text-xs">
                  <p className="text-muted">Gợi ý file đích</p>
                  <p className="truncate text-sm font-semibold">{current.target_file || "(Admin chọn lúc duyệt)"}</p>
                </div>
                <div className="rounded-lg bg-paper px-3 py-2 text-xs">
                  <p className="text-muted">Đối thủ relevancy</p>
                  <p className="text-sm font-semibold">{current.preview.length} trạng liên quan</p>
                </div>
              </div>

              {current.preview.length > 0 ? (
                <div className="rounded-lg border border-line px-4 py-3 text-xs">
                  <p className="mb-1 font-semibold text-muted">3 trạng gần nhất (context duyệt)</p>
                  <ul className="space-y-0.5">
                    {current.preview.map((p) => (
                      <li key={`${p.file}-${p.section}`}>{p.file} — {p.section} <span className="text-muted">({p.score})</span></li>
                    ))}
                  </ul>
                </div>
              ) : null}

              <div>
                <div className="mb-1 flex items-center justify-between">
                  <p className="text-sm font-semibold">Nội dung {editContent !== null ? "(bản Admin đang sửa)" : ""}</p>
                  {current.can_review && editContent === null ? (
                    <button type="button" className="text-xs text-brand-600 underline"
                      onClick={() => setEditContent(current.content_md)}>Sửa trước khi duyệt</button>
                  ) : null}
                  {editContent !== null ? (
                    <button type="button" className="text-xs text-muted underline"
                      onClick={() => setEditContent(null)}>Hoàn tác sửa</button>
                  ) : null}
                </div>
                {editContent !== null ? (
                  <Textarea rows={14} value={editContent} onChange={(e) => setEditContent(e.target.value)} />
                ) : (
                  <pre className="max-h-[45vh] overflow-auto whitespace-pre-wrap rounded-lg bg-paper px-4 py-3 font-mono text-xs leading-relaxed">
                    {current.content_md}
                  </pre>
                )}
              </div>
            </div>
          )}
        </section>
      </div>

      {scan ? (
        <Modal title={`Quét trùng lặp toàn kho — ${scan.pairs_found} cặp ≥70%`} onClose={() => setScan(null)} wide>
          <div className="space-y-3 text-sm">
            <p className="text-muted">
              {scan.chunks} section · quét {scan.duration_ms}ms
              {scan.pairs.length < scan.pairs_found ? ` · hiển thị top ${scan.pairs.length}` : ""}.
            </p>
            {scan.pairs.length === 0 ? (
              <p>Không phát hiện cặp trùng lặp nào ≥70%.</p>
            ) : (
              <ul className="max-h-[50vh] space-y-2 overflow-y-auto">
                {scan.pairs.map((p, i) => (
                  <li key={i} className="rounded border border-line px-3 py-2 text-xs">
                    <span className="font-semibold text-brand-600">{Math.round(p.similarity * 100)}%</span>
                    {" · "}{p.a.file} <span className="text-muted">({p.a.section})</span>
                    {" ↔ "}{p.b.file} <span className="text-muted">({p.b.section})</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </Modal>
      ) : null}

      {rejecting ? (
        <Modal title="Từ chối bài đóng góp" onClose={() => setRejecting(false)}>
          <div className="space-y-4">
            <Field label="Lý do (hiện với người nộp)" required htmlFor="kb-reason">
              <Textarea id="kb-reason" rows={4} value={reason} onChange={(e) => setReason(e.target.value)}
                placeholder="Ví dụ: Nguồn chưa đủ tin cậy, trùng với Gate 17 đang có..." />
            </Field>
            <div className="flex justify-end gap-2">
              <Button variant="ghost" onClick={() => setRejecting(false)}>Hủy</Button>
              <Button variant="danger" onClick={() => reject.mutate()}
                disabled={reject.isPending || reason.trim().length === 0}>
                Gửi từ chối
              </Button>
            </div>
          </div>
        </Modal>
      ) : null}
    </div>
  );
}

function StatCard({ label, value, hint, accent }: { label: string; value: number; hint?: string; accent?: boolean }) {
  return (
    <div className={`rounded-lg border px-4 py-3 ${accent ? "border-gold-500/50 bg-gold-100/40" : "border-line bg-white"}`}>
      <p className="text-xs text-muted">{label}</p>
      <p className="text-xl font-semibold">{value}</p>
      {hint ? <p className="text-[11px] text-muted">{hint}</p> : null}
    </div>
  );
}
