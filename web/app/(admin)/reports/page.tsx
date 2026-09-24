"use client";

import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { FilePlus2, FileText, Search } from "lucide-react";
import { useState } from "react";
import { ReportTable } from "@/components/ReportTable";
import { Card, EmptyState, ErrorBox, Input, LinkButton, PageHeader, Spinner, cx } from "@/components/ui";
import { api, qs } from "@/lib/api";
import { useDebounced } from "@/lib/hooks";
import type { Paged, ReportSummary } from "@/lib/types";

const FILTERS = [
  { value: "", label: "Đang dùng" },
  { value: "ready", label: "Hoàn tất" },
  { value: "generating", label: "Đang tạo" },
  { value: "failed", label: "Lỗi" },
  { value: "archived", label: "Đã lưu trữ" },
];

export default function ReportsPage() {
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("");
  const query = useDebounced(q);
  const { data, error, isLoading } = useQuery({
    queryKey: ["reports", query, status],
    queryFn: () => api.get<Paged<ReportSummary>>(`/reports${qs({ q: query, status, limit: 100 })}`),
    placeholderData: keepPreviousData,
    refetchInterval: (q) => (q.state.data?.items.some((r) => r.status === "generating") ? 4000 : false),
  });

  return (
    <>
      <PageHeader title="Báo cáo" description={data ? `${data.total} báo cáo` : undefined}
        actions={<LinkButton href="/reports/new"><FilePlus2 className="size-4" /> Tạo báo cáo</LinkButton>} />
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <div className="relative w-full max-w-sm">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted" aria-hidden />
          <Input className="pl-9" placeholder="Tìm theo tên khách hàng…" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Tìm báo cáo" />
        </div>
        <div className="flex flex-wrap gap-1 rounded-lg border border-line bg-white p-1" role="tablist">
          {FILTERS.map((f) => (
            <button key={f.value} role="tab" aria-selected={status === f.value} onClick={() => setStatus(f.value)}
              className={cx("rounded-md px-3 py-1.5 text-xs font-medium", status === f.value ? "bg-brand-500 text-white" : "text-muted hover:bg-paper")}>
              {f.label}
            </button>
          ))}
        </div>
      </div>
      <ErrorBox error={error} className="mb-4" />
      <Card>
        {isLoading ? <Spinner /> : data?.items.length ? <ReportTable reports={data.items} /> : (
          <EmptyState icon={<FileText className="size-8" />} title="Không có báo cáo nào"
            action={<LinkButton href="/reports/new"><FilePlus2 className="size-4" /> Tạo báo cáo</LinkButton>} />
        )}
      </Card>
    </>
  );
}
