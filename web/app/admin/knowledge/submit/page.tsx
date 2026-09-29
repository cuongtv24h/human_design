"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FileText, Send } from "lucide-react";
import { useState, type FormEvent } from "react";
import { Badge, Button, ErrorBox, Field, Input, Spinner, Textarea } from "@/components/ui";
import { api } from "@/lib/api";
import { useMe } from "@/lib/auth";

// Đóng góp tri thức (A–C): Coach/ Admin nộp bài → sàng lọc TỰ ĐỘNG
// (heading / ≤60KB / lộ bí mật / trùng ≥90%) → hàng chờ Admin duyệt.
// Không có "bản nháp" — bài luôn có trạng thái pending | approved | rejected.

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

const STATUS_LABEL: Record<Submission["status"], string> = {
  pending: "Chờ duyệt",
  approved: "Đã duyệt",
  rejected: "Từ chối",
};

function StatusBadge({ status }: { status: Submission["status"] }) {
  const tone = status === "pending" ? "gold" : status === "approved" ? "brand" : "stone";
  return <Badge tone={tone}>{STATUS_LABEL[status]}</Badge>;
}

export default function KnowledgeSubmitPage() {
  const me = useMe();
  const qc = useQueryClient();
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [target, setTarget] = useState("");
  const [source, setSource] = useState("");
  const [sent, setSent] = useState<number | null>(null);

  const mine = useQuery({
    queryKey: ["kb-submissions-mine"],
    queryFn: () => api.get<{ items: Submission[]; total: number }>("/knowledge/submissions"),
  });

  const submit = useMutation({
    mutationFn: () =>
      api.post<Submission>("/knowledge/submissions", {
        title,
        content_md: content,
        target_file: target || undefined,
        source_url: source || undefined,
      }),
    onSuccess: (sub) => {
      setSent(sub.id);
      setTitle("");
      setContent("");
      setTarget("");
      setSource("");
      qc.invalidateQueries({ queryKey: ["kb-submissions-mine"] });
    },
  });

  if (me.data && me.data.role !== "admin" && me.data.role !== "coach") {
    return <p className="text-sm text-muted">Chỉ Coach và Admin mới được đóng góp tài liệu.</p>;
  }

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    submit.mutate();
  };

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
      <section className="space-y-4">
        <div>
          <h1 className="text-xl font-semibold">Đóng góp tài liệu</h1>
          <p className="mt-1 text-sm text-muted">
            Bài nộp được sàng lọc tự động (heading, dung lượng, chống lộ bí mật, chống trùng lặp)
            rồi chuyển tới Admin duyệt trước khi vào kho tri thức.
          </p>
        </div>

        {sent !== null && (
          <div className="rounded-lg border border-brand-500/30 bg-brand-50 px-4 py-3 text-sm">
            Đã nộp bài #{sent} — trạng thái <strong>Chờ duyệt</strong>. Admin sẽ xem và phản hồi
            trong “Duyệt đóng góp”.
          </div>
        )}

        <form onSubmit={onSubmit} className="space-y-4 rounded-lg border border-line bg-white p-5">
          <Field label="Tiêu đề bài đóng góp" required htmlFor="kb-title">
            <Input id="kb-title" required maxLength={200} value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Ví dụ: Thêm ghi chú về Gate 17 trong ngữ cảnh dự báo" />
          </Field>
          <Field label="Nội dung Markdown" required htmlFor="kb-content"
            hint="Cần ít nhất một heading # hoặc ##. Không dán khóa API/mật khẩu.">
            <Textarea id="kb-content" required rows={12} value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder={"# Tiêu đề phần\n\n## Section\nNội dung phân tích của bạn..."} />
          </Field>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="File đích (tùy chọn)" htmlFor="kb-target"
              hint="Tên file .md có sẵn, ví dụ 17_decision_authority.md. Bỏ trống nếu không chắc.">
              <Input id="kb-target" maxLength={200} value={target}
                onChange={(e) => setTarget(e.target.value)} placeholder="để trống = Admin chọn" />
            </Field>
            <Field label="Nguồn tham khảo (tùy chọn)" htmlFor="kb-source">
              <Input id="kb-source" type="url" maxLength={500} value={source}
                onChange={(e) => setSource(e.target.value)} placeholder="https://..." />
            </Field>
          </div>
          {submit.error ? <ErrorBox error={submit.error} /> : null}
          <div className="flex items-center gap-3">
            <Button type="submit" disabled={submit.isPending}>
              {submit.isPending ? <Spinner /> : <Send size={16} />} Nộp chờ duyệt
            </Button>
            <span className="text-xs text-muted">Tự kiểm tra: ≥1 heading · ≤60KB · không trùng ≥90%</span>
          </div>
        </form>
      </section>

      <aside className="space-y-3">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-muted">Bài của tôi</h2>
        {mine.isLoading ? <Spinner /> : null}
        {mine.error ? <ErrorBox error={mine.error} /> : null}
        <ul className="space-y-3">
          {(mine.data?.items ?? []).map((sub) => (
            <li key={sub.id} className="rounded-lg border border-line bg-white p-4 text-sm">
              <div className="flex items-start justify-between gap-2">
                <span className="flex items-center gap-2 font-medium">
                  <FileText size={14} className="text-muted" /> {sub.title}
                </span>
                <StatusBadge status={sub.status} />
              </div>
              <p className="mt-1 text-xs text-muted">
                #{sub.id} · {sub.created_at ? new Date(sub.created_at).toLocaleString("vi-VN") : ""}
                {sub.dedupe_report.max_similarity
                  ? ` · trùng tối đa ${Math.round((sub.dedupe_report.max_similarity || 0) * 100)}%`
                  : ""}
              </p>
              {sub.status === "rejected" && sub.reject_reason ? (
                <p className="mt-2 rounded bg-red-50 px-2 py-1 text-xs text-red-700">
                  Lý do: {sub.reject_reason}
                </p>
              ) : null}
              {sub.status === "approved" && sub.target_file ? (
                <p className="mt-2 text-xs text-brand-600">Đã xuất: {sub.target_file}</p>
              ) : null}
            </li>
          ))}
          {mine.data && mine.data.items.length === 0 ? (
            <li className="text-sm text-muted">Chưa có bài nào.</li>
          ) : null}
        </ul>
      </aside>
    </div>
  );
}
