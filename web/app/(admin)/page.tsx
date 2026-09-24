"use client";

import { useQuery } from "@tanstack/react-query";
import { FilePlus2, FileText, UserPlus, Users } from "lucide-react";
import { ReportTable } from "@/components/ReportTable";
import { Card, EmptyState, ErrorBox, LinkButton, PageHeader, Spinner } from "@/components/ui";
import { api } from "@/lib/api";
import { useMe } from "@/lib/auth";
import type { Dashboard } from "@/lib/types";

function Stat({ label, value, tone = "text-ink" }: { label: string; value: number | string; tone?: string }) {
  return (
    <Card className="p-5">
      <div className="text-xs font-medium uppercase tracking-wide text-muted">{label}</div>
      <div className={`mt-2 text-3xl font-bold ${tone}`}>{value}</div>
    </Card>
  );
}

export default function DashboardPage() {
  const me = useMe();
  const { data, error, isLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => api.get<Dashboard>("/dashboard"),
    refetchInterval: (q) => ((q.state.data?.reports_by_status.generating ?? 0) > 0 ? 4000 : false),
  });
  const name = me.data?.full_name?.split(" ").slice(-1)[0] || "";

  return (
    <>
      <PageHeader
        title={`Xin chào${name ? `, ${name}` : ""}`}
        description="Tổng quan khách hàng và báo cáo của bạn."
        actions={
          <>
            <LinkButton href="/clients/new" variant="secondary"><UserPlus className="size-4" /> Thêm khách hàng</LinkButton>
            <LinkButton href="/reports/new"><FilePlus2 className="size-4" /> Tạo báo cáo</LinkButton>
          </>
        }
      />
      <ErrorBox error={error} className="mb-6" />
      {isLoading || !data ? (
        <Spinner />
      ) : (
        <>
          <div className="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
            <Stat label="Khách hàng" value={data.clients} />
            <Stat label="Báo cáo hoàn tất" value={data.reports_by_status.ready ?? 0} tone="text-emerald-700" />
            <Stat label="Đang tạo" value={data.reports_by_status.generating ?? 0} tone="text-amber-700" />
            <Stat label="Lỗi" value={data.reports_by_status.failed ?? 0} tone={(data.reports_by_status.failed ?? 0) > 0 ? "text-red-700" : "text-ink"} />
          </div>
          <Card>
            <div className="flex items-center justify-between border-b border-line px-5 py-4">
              <h2 className="font-semibold text-ink">Báo cáo gần đây</h2>
              <LinkButton href="/reports" variant="ghost" className="px-2 py-1">Xem tất cả</LinkButton>
            </div>
            {data.recent_reports.length ? (
              <ReportTable reports={data.recent_reports} />
            ) : data.clients === 0 ? (
              <EmptyState icon={<Users className="size-8" />} title="Bắt đầu bằng việc thêm khách hàng đầu tiên"
                description="Nhập họ tên, ngày và giờ sinh (giờ Việt Nam). Sau đó bạn có thể tạo báo cáo chỉ trong vài giây."
                action={<LinkButton href="/clients/new"><UserPlus className="size-4" /> Thêm khách hàng</LinkButton>} />
            ) : (
              <EmptyState icon={<FileText className="size-8" />} title="Chưa có báo cáo nào"
                action={<LinkButton href="/reports/new"><FilePlus2 className="size-4" /> Tạo báo cáo đầu tiên</LinkButton>} />
            )}
          </Card>
        </>
      )}
    </>
  );
}
