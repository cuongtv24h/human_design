"use client";

import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { Search, UserPlus, Users } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { useDebounced } from "@/lib/hooks";
import { Card, EmptyState, ErrorBox, Input, LinkButton, PageHeader, Spinner } from "@/components/ui";
import { api, qs } from "@/lib/api";
import { formatTimestamp } from "@/lib/format";
import type { Client, Paged } from "@/lib/types";

export default function ClientsPage() {
  const [q, setQ] = useState("");
  const query = useDebounced(q);
  const { data, error, isLoading } = useQuery({
    queryKey: ["clients", query],
    queryFn: () => api.get<Paged<Client>>(`/clients${qs({ q: query, limit: 100 })}`),
    placeholderData: keepPreviousData,
  });

  return (
    <>
      <PageHeader title="Khách hàng" description={data ? `${data.total} người` : undefined}
        actions={<LinkButton href="/clients/new"><UserPlus className="size-4" /> Thêm khách hàng</LinkButton>} />
      <div className="relative mb-4 max-w-md">
        <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted" aria-hidden />
        <Input className="pl-9" placeholder="Tìm theo tên, email hoặc số điện thoại…" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Tìm khách hàng" />
      </div>
      <ErrorBox error={error} className="mb-4" />
      <Card>
        {isLoading ? (
          <Spinner />
        ) : !data?.items.length ? (
          query ? (
            <EmptyState icon={<Search className="size-8" />} title="Không tìm thấy khách hàng phù hợp" description={`Không có kết quả cho “${query}”.`} />
          ) : (
            <EmptyState icon={<Users className="size-8" />} title="Chưa có khách hàng nào"
              description="Thêm khách hàng với ngày và giờ sinh để bắt đầu tạo báo cáo."
              action={<LinkButton href="/clients/new"><UserPlus className="size-4" /> Thêm khách hàng</LinkButton>} />
          )
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-line text-left text-xs uppercase tracking-wide text-muted">
                  <th className="px-4 py-3 font-medium">Họ tên</th>
                  <th className="px-4 py-3 font-medium">Ngày · giờ sinh</th>
                  <th className="px-4 py-3 font-medium">Liên hệ</th>
                  <th className="px-4 py-3 text-right font-medium">Báo cáo</th>
                  <th className="px-4 py-3 font-medium">Cập nhật</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((c) => (
                  <tr key={c.id} className="border-b border-line/70 last:border-0 hover:bg-paper/60">
                    <td className="px-4 py-3">
                      <Link href={`/clients/${c.id}`} className="font-medium text-ink hover:text-brand-600">{c.full_name}</Link>
                      {c.birth_place && <div className="text-xs text-muted">{c.birth_place}</div>}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3">
                      {c.birth_display}
                      {!c.birth_time_known && <span className="ml-1 text-xs text-amber-700">(ước lượng)</span>}
                    </td>
                    <td className="px-4 py-3 text-muted">{c.phone || c.email || "—"}</td>
                    <td className="px-4 py-3 text-right tabular-nums">{c.report_count}</td>
                    <td className="whitespace-nowrap px-4 py-3 text-muted">{formatTimestamp(c.updated_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </>
  );
}
