"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, Archive, Download, FileCode2, FileImage, FileText, Link2, Loader2, PencilLine, RefreshCw } from "lucide-react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import { ChartTiles } from "@/components/ChartTiles";
import { Markdown } from "@/components/Markdown";
import { CopyField, SharePanel } from "@/components/SharePanel";
import { absoluteUrl } from "@/lib/clipboard";
import { Badge, Button, Card, ErrorBox, PageHeader, Spinner, StatusBadge, cx } from "@/components/ui";
import { api, fileUrl } from "@/lib/api";
import { formatTimestamp, formatUsd, MODE_LABEL, TEMPLATE_LABEL, TIER_LABEL } from "@/lib/format";
import type { DownloadLink, ReportDetail } from "@/lib/types";

const TABS = [
  { id: "content", label: "Nội dung" },
  { id: "infographic", label: "Infographic" },
  { id: "bodygraph", label: "BodyGraph" },
  { id: "export", label: "Xuất file" },
  { id: "share", label: "Chia sẻ" },
] as const;
type Tab = (typeof TABS)[number]["id"];

function ExportRow({ icon, title, description, href, reportId, linkFormat }: {
  icon: React.ReactNode; title: string; description: string; href: string; reportId: string;
  linkFormat: "pdf" | "docx" | "markdown" | "infographic" | "bodygraph_svg";
}) {
  const [link, setLink] = useState<DownloadLink | null>(null);
  const make = useMutation({
    mutationFn: () => api.post<DownloadLink>(`/reports/${reportId}/links`, { format: linkFormat }),
    onSuccess: setLink,
  });
  return (
    <div className="px-5 py-4">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="mt-0.5 text-brand-600">{icon}</div>
          <div>
            <div className="font-medium text-ink">{title}</div>
            <div className="text-sm text-muted">{description}</div>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="ghost" className="px-3 py-1.5" loading={make.isPending} onClick={() => make.mutate()}
            title="Link tải trực tiếp, không cần đăng nhập, hết hạn sau 5 phút">
            <Link2 className="size-4" /> Link 5 phút
          </Button>
          <a href={href} className="inline-flex items-center gap-2 rounded-lg border border-line bg-white px-3 py-1.5 text-sm font-medium hover:bg-brand-50">
            <Download className="size-4" /> Tải về
          </a>
        </div>
      </div>
      <ErrorBox error={make.error} className="mt-3" />
      {link && (
        <div className="mt-3">
          <CopyField value={absoluteUrl(link.url)} hint={`Mở được không cần đăng nhập đến ${formatTimestamp(link.expires_at)} (5 phút). Để gửi khách lâu dài, dùng tab “Chia sẻ”.`} />
        </div>
      )}
    </div>
  );
}

export default function ReportPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<Tab>("content");
  const report = useQuery({
    queryKey: ["report", id],
    queryFn: () => api.get<ReportDetail>(`/reports/${id}`),
    refetchInterval: (q) => (q.state.data?.status === "generating" ? 3000 : false),
  });
  const archive = useMutation({
    mutationFn: () => api.post<ReportDetail>(`/reports/${id}/archive`),
    onSuccess: (r) => {
      queryClient.setQueryData(["report", id], r);
      queryClient.invalidateQueries({ queryKey: ["reports"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });

  const regenerate = useMutation({
    mutationFn: () => api.post<ReportDetail>(`/reports/${id}/regenerate`, {}),
    onSuccess: (data) => {
      queryClient.setQueryData(["report", id], data);
      queryClient.invalidateQueries({ queryKey: ["reports"] });
    },
  });

  if (report.isLoading) return <Spinner />;
  if (!report.data) return <ErrorBox error={report.error ?? "Không tìm thấy báo cáo."} />;
  const r = report.data;
  const hasDocument = r.status === "ready" || (r.status === "archived" && r.sections.length > 0);

  return (
    <>
      <PageHeader
        title={r.client_name}
        description={
          <span className="flex flex-wrap items-center gap-2">
            <StatusBadge status={r.status} />
            <span>{TIER_LABEL[r.tier]} · {TEMPLATE_LABEL[r.template]}</span>
            <Badge tone={r.content_mode === "llm" ? "gold" : "brand"}>{MODE_LABEL[r.content_mode]}</Badge>
            {r.llm_provider && <span>· Viết bởi {r.llm_provider}{r.llm_cost_usd !== null && r.llm_cost_usd !== undefined ? ` (${formatUsd(r.llm_cost_usd)})` : ""}</span>}
            <span>· Tạo {formatTimestamp(r.created_at)} · v{r.version}</span>
          </span>
        }
        actions={
          <>
            <Link href={`/clients/${r.client_id}`} className="inline-flex items-center rounded-lg px-3 py-2 text-sm text-brand-700 hover:bg-brand-50">Hồ sơ khách hàng</Link>
            {r.status === "ready" && (
              <Link href={`/reports/${r.id}/edit`} className="inline-flex items-center gap-2 rounded-lg border border-line bg-white px-4 py-2 text-sm font-medium text-ink shadow-sm hover:bg-paper">
                <PencilLine className="size-4" /> Biên tập
              </Link>
            )}
            {hasDocument && (
              <a href={fileUrl(r.id, "pdf", true)} className="inline-flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-brand-600">
                <Download className="size-4" /> Tải PDF
              </a>
            )}
            {r.status !== "archived" && r.status !== "generating" && (
              <Button variant="secondary" loading={archive.isPending}
                onClick={() => confirm("Lưu trữ báo cáo này? Báo cáo sẽ ẩn khỏi danh sách đang dùng.") && archive.mutate()}>
                <Archive className="size-4" /> Lưu trữ
              </Button>
            )}
          </>
        }
      />
      <ErrorBox error={archive.error} className="mb-4" />

      {r.status === "generating" && (
        <Card className="flex flex-col items-center gap-3 p-10 text-center">
          <Loader2 className="size-8 animate-spin text-brand-500" />
          <div className="font-semibold">AI đang biên tập nội dung…</div>
          <p className="max-w-md text-sm text-muted">Thường mất 1–2 phút. Trang sẽ tự cập nhật — bạn có thể làm việc khác và quay lại sau.</p>
        </Card>
      )}

      {r.status === "failed" && (
        <Card className="space-y-3 p-6">
          <div className="flex items-center gap-2 font-semibold text-red-800"><AlertTriangle className="size-5" /> Tạo báo cáo thất bại</div>
          <p className="text-sm text-muted">{r.error || "Không rõ nguyên nhân."}</p>
          <ErrorBox error={regenerate.error} />
          <div className="flex flex-wrap gap-2">
            <Button loading={regenerate.isPending} onClick={() => regenerate.mutate()}>
              <RefreshCw className="size-4" /> Tạo lại với cùng tùy chọn
            </Button>
            <Button variant="secondary" onClick={() => router.push(`/reports/new?client=${r.client_id}`)}>Tạo báo cáo mới</Button>
          </div>
        </Card>
      )}

      {hasDocument && (
        <>
          {r.warnings.length > 0 && (
            <div className="mb-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
              <div className="mb-1 flex items-center gap-2 font-medium"><AlertTriangle className="size-4" /> {r.warnings.length} lưu ý khi tạo báo cáo</div>
              <ul className="list-disc space-y-0.5 pl-5">{r.warnings.map((w, i) => <li key={i}>{w}</li>)}</ul>
            </div>
          )}
          {r.summary && (
            <Card className="mb-6 p-5">
              <div className="mb-3 text-xs text-muted">Sinh {r.subject_display}</div>
              <ChartTiles summary={r.summary} />
            </Card>
          )}

          <div className="mb-4 flex gap-1 border-b border-line" role="tablist">
            {TABS.map((t) => (
              <button key={t.id} role="tab" aria-selected={tab === t.id} onClick={() => setTab(t.id)}
                className={cx("-mb-px border-b-2 px-4 py-2 text-sm font-medium",
                  tab === t.id ? "border-brand-500 text-brand-700" : "border-transparent text-muted hover:text-ink")}>
                {t.label}
              </button>
            ))}
          </div>

          {tab === "content" && (
            <div className="grid items-start gap-6 lg:grid-cols-[13rem_minmax(0,1fr)]">
              <nav className="hidden text-sm lg:sticky lg:top-6 lg:block">
                <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted">Mục lục</div>
                <ol className="space-y-1.5">
                  {r.sections.filter((s) => s.status !== "omitted").map((s) => (
                    <li key={s.id} className="leading-snug text-ink">
                      {s.title}
                      {s.warnings.length > 0 && <AlertTriangle className="ml-1 inline size-3 text-amber-600" />}
                    </li>
                  ))}
                </ol>
              </nav>
              <Card className="p-6 sm:p-8"><Markdown>{r.markdown}</Markdown></Card>
            </div>
          )}

          {tab === "infographic" && (
            <Card className="overflow-hidden">
              <iframe title="Infographic" src={fileUrl(r.id, "infographic.html")} sandbox="" className="h-[80vh] w-full bg-white" />
            </Card>
          )}

          {tab === "bodygraph" && (
            <Card className="p-6">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={fileUrl(r.id, "bodygraph.svg")} alt={`BodyGraph của ${r.client_name}`} className="mx-auto max-h-[75vh] w-full object-contain" />
            </Card>
          )}

          {tab === "export" && (
            <Card className="divide-y divide-line">
              <ExportRow reportId={r.id} linkFormat="pdf" icon={<FileText className="size-5" />} title="PDF" description="Bản in hoàn chỉnh: bìa, BodyGraph, mục lục và toàn bộ nội dung." href={fileUrl(r.id, "pdf", true)} />
              <ExportRow reportId={r.id} linkFormat="docx" icon={<FileText className="size-5" />} title="Word (.docx)" description="Cùng nội dung như PDF — chuyên viên chỉnh sửa, bổ sung trước khi gửi." href={fileUrl(r.id, "docx", true)} />
              <ExportRow reportId={r.id} linkFormat="markdown" icon={<FileText className="size-5" />} title="Markdown (.md)" description="Toàn bộ nội dung — mở bằng Word, Notion, Obsidian…" href={fileUrl(r.id, "markdown", true)} />
              <ExportRow reportId={r.id} linkFormat="infographic" icon={<FileCode2 className="size-5" />} title="Infographic (.html)" description="Trang tóm tắt một màn hình, gửi kèm cho khách hàng." href={fileUrl(r.id, "infographic.html", true)} />
              <ExportRow reportId={r.id} linkFormat="bodygraph_svg" icon={<FileImage className="size-5" />} title="BodyGraph (.svg)" description="Hình BodyGraph chất lượng cao, in ấn không vỡ nét." href={fileUrl(r.id, "bodygraph.svg", true)} />
            </Card>
          )}

          {tab === "share" && (
            r.status === "archived"
              ? <ErrorBox error="Báo cáo đã lưu trữ — không tạo link chia sẻ mới được." />
              : <SharePanel reportId={r.id} clientName={r.client_name} />
          )}
        </>
      )}
    </>
  );
}
