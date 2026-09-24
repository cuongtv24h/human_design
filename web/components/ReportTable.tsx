"use client";

import Link from "next/link";
import { AlertTriangle } from "lucide-react";
import { Badge, StatusBadge } from "@/components/ui";
import { formatTimestamp, MODE_LABEL, TEMPLATE_LABEL, TIER_LABEL } from "@/lib/format";
import type { ReportSummary } from "@/lib/types";

export function ReportTable({ reports, showClient = true }: { reports: ReportSummary[]; showClient?: boolean }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-line text-left text-xs uppercase tracking-wide text-muted">
            {showClient && <th className="px-4 py-3 font-medium">Khách hàng</th>}
            <th className="px-4 py-3 font-medium">Loại báo cáo</th>
            <th className="px-4 py-3 font-medium">Nội dung</th>
            <th className="px-4 py-3 font-medium">Trạng thái</th>
            <th className="px-4 py-3 font-medium">Tạo lúc</th>
          </tr>
        </thead>
        <tbody>
          {reports.map((r) => (
            <tr key={r.id} className="border-b border-line/70 last:border-0 hover:bg-paper/60">
              {showClient && (
                <td className="px-4 py-3">
                  <Link href={`/reports/${r.id}`} className="font-medium text-ink hover:text-brand-600">{r.client_name}</Link>
                </td>
              )}
              <td className="px-4 py-3">
                <Link href={`/reports/${r.id}`} className="hover:text-brand-600">
                  {TIER_LABEL[r.tier] ?? r.tier} · {TEMPLATE_LABEL[r.template] ?? r.template}
                </Link>
                {r.domains.length > 0 && <div className="text-xs text-muted">+ {r.domains.length} chủ đề chuyên sâu</div>}
              </td>
              <td className="px-4 py-3">
                <Badge tone={r.content_mode === "llm" ? "gold" : "brand"}>{MODE_LABEL[r.content_mode] ?? r.content_mode}</Badge>
              </td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  <StatusBadge status={r.status} />
                  {r.warnings_count > 0 && (
                    <span title={`${r.warnings_count} cảnh báo`} className="inline-flex items-center gap-1 text-xs text-amber-700">
                      <AlertTriangle className="size-3.5" aria-hidden /> {r.warnings_count}
                    </span>
                  )}
                </div>
              </td>
              <td className="whitespace-nowrap px-4 py-3 text-muted">{formatTimestamp(r.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
