"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CalendarClock, FilePlus2, MapPin, Pencil, Phone, Mail, Trash2, FileText, CheckCircle2 } from "lucide-react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState, type ReactNode } from "react";
import { ClientForm } from "@/components/ClientForm";
import { ReportTable } from "@/components/ReportTable";
import { Button, Card, EmptyState, ErrorBox, LinkButton, PageHeader, Spinner } from "@/components/ui";
import { api } from "@/lib/api";
import { formatTimestamp } from "@/lib/format";
import type { Client, Paged, ReportSummary } from "@/lib/types";

function Info({ icon, label, children }: { icon: ReactNode; label: string; children: ReactNode }) {
  return (
    <div className="flex gap-3">
      <div className="mt-0.5 text-muted">{icon}</div>
      <div>
        <div className="text-xs text-muted">{label}</div>
        <div className="text-sm text-ink">{children}</div>
      </div>
    </div>
  );
}

function ClientDetail() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const created = useSearchParams().get("created");
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState(false);
  const client = useQuery({ queryKey: ["client", id], queryFn: () => api.get<Client>(`/clients/${id}`) });
  const reports = useQuery({
    queryKey: ["client-reports", id],
    queryFn: () => api.get<Paged<ReportSummary>>(`/clients/${id}/reports`),
  });
  const remove = useMutation({
    mutationFn: () => api.del(`/clients/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      router.replace("/clients");
    },
  });

  if (client.isLoading) return <Spinner />;
  if (client.error || !client.data) return <ErrorBox error={client.error ?? "Không tìm thấy khách hàng."} />;
  const c = client.data;

  return (
    <>
      <PageHeader title={c.full_name} description={`Phụ trách: ${c.owner_name} · Tạo ${formatTimestamp(c.created_at)}`}
        actions={
          !editing && (
            <>
              <Button variant="secondary" onClick={() => setEditing(true)}><Pencil className="size-4" /> Sửa</Button>
              <LinkButton href={`/reports/new?client=${c.id}`}><FilePlus2 className="size-4" /> Tạo báo cáo</LinkButton>
            </>
          )
        } />

      {created && !editing && (
        <div className="mb-6 flex items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
          <CheckCircle2 className="size-4" /> Đã lưu khách hàng. Bước tiếp theo: tạo báo cáo đầu tiên cho {c.full_name}.
        </div>
      )}

      {editing ? (
        <Card className="mb-6 max-w-3xl p-6">
          <ClientForm initial={c} requireConsent={false} submitLabel="Lưu thay đổi" onCancel={() => setEditing(false)}
            onSubmit={async (value) => {
              const { consent: _consent, ...patch } = value;
              const updated = await api.patch<Client>(`/clients/${id}`, patch);
              queryClient.setQueryData(["client", id], updated);
              queryClient.invalidateQueries({ queryKey: ["clients"] });
              setEditing(false);
            }} />
        </Card>
      ) : (
        <Card className="mb-6 grid gap-5 p-6 sm:grid-cols-2 lg:grid-cols-4">
          <Info icon={<CalendarClock className="size-4" />} label="Ngày · giờ sinh">
            {c.birth_display}
            {!c.birth_time_known && <div className="text-xs text-amber-700">Giờ sinh ước lượng</div>}
          </Info>
          <Info icon={<MapPin className="size-4" />} label="Nơi sinh">{c.birth_place || "—"}</Info>
          <Info icon={<Phone className="size-4" />} label="Điện thoại">{c.phone || "—"}</Info>
          <Info icon={<Mail className="size-4" />} label="Email">{c.email || "—"}</Info>
          {c.notes && (
            <div className="rounded-lg bg-paper p-4 text-sm text-ink sm:col-span-2 lg:col-span-4">
              <div className="mb-1 text-xs text-muted">Ghi chú nội bộ</div>
              <p className="whitespace-pre-line">{c.notes}</p>
            </div>
          )}
        </Card>
      )}

      <Card>
        <div className="border-b border-line px-5 py-4">
          <h2 className="font-semibold text-ink">Báo cáo của {c.full_name}</h2>
        </div>
        {reports.isLoading ? (
          <Spinner />
        ) : reports.data?.items.length ? (
          <ReportTable reports={reports.data.items} showClient={false} />
        ) : (
          <EmptyState icon={<FileText className="size-8" />} title="Chưa có báo cáo"
            action={<LinkButton href={`/reports/new?client=${c.id}`}><FilePlus2 className="size-4" /> Tạo báo cáo</LinkButton>} />
        )}
      </Card>

      <div className="mt-10 border-t border-line pt-6">
        <ErrorBox error={remove.error} className="mb-3" />
        <Button variant="danger" loading={remove.isPending}
          onClick={() => {
            if (confirm(`Xóa khách hàng “${c.full_name}”? Các báo cáo của người này sẽ bị ẩn.`)) remove.mutate();
          }}>
          <Trash2 className="size-4" /> Xóa khách hàng
        </Button>
      </div>
    </>
  );
}

export default function ClientDetailPage() {
  return (
    <Suspense fallback={<Spinner />}>
      <ClientDetail />
    </Suspense>
  );
}
