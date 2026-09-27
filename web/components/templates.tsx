"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";
import { Markdown } from "@/components/Markdown";
import { Badge, Button, ErrorBox, Field, Input, Modal, Spinner, Textarea } from "@/components/ui";
import { api } from "@/lib/api";
import { TEMPLATE_STATUS_LABEL } from "@/lib/format";
import type { TemplateDetail, TemplatePreview } from "@/lib/types";

const TONE: Record<string, "brand" | "gold" | "stone"> = {
  draft: "stone",
  pending: "gold",
  active: "brand",
  rejected: "gold",
  archived: "stone",
};

export function TemplateStatusPill({ status }: { status: string }) {
  return <Badge tone={TONE[status] ?? "stone"}>{TEMPLATE_STATUS_LABEL[status] ?? status}</Badge>;
}

export function useTemplateMutations() {
  const queryClient = useQueryClient();
  const refresh = () => {
    queryClient.invalidateQueries({ queryKey: ["templates"] });
    queryClient.invalidateQueries({ queryKey: ["templates-library"] });
    queryClient.invalidateQueries({ queryKey: ["template"] });
    queryClient.invalidateQueries({ queryKey: ["catalog"] });
  };
  const setStatus = useMutation({
    mutationFn: ({ id, body }: { id: number; body: Record<string, string> }) =>
      api.patch<TemplateDetail>(`/templates/${id}`, body),
    onSuccess: refresh,
  });
  const removeTpl = useMutation({
    mutationFn: (id: number) => api.del(`/templates/${id}`),
    onSuccess: refresh,
  });
  const duplicate = useMutation({
    mutationFn: (id: number) => api.post<TemplateDetail>(`/templates/${id}/duplicate`),
    onSuccess: refresh,
  });
  const publish = useMutation({
    mutationFn: ({ id, body }: { id: number; body: { badge: string; origin_label: string } }) =>
      api.post<TemplateDetail>(`/templates/${id}/publish`, body),
    onSuccess: refresh,
  });
  const unpublish = useMutation({
    mutationFn: (id: number) => api.post<void>(`/templates/${id}/unpublish`),
    onSuccess: refresh,
  });
  return { setStatus, removeTpl, duplicate, publish, unpublish };
}

export function PreviewModal({ templateId, name, onClose }: { templateId: number; name: string; onClose: () => void }) {
  const preview = useQuery({
    queryKey: ["template-preview", templateId],
    queryFn: () => api.post<TemplatePreview>("/templates/preview", { template_id: templateId }),
    staleTime: 30_000,
  });
  return (
    <Modal title={`Xem trước: ${name}`} onClose={onClose} wide>
      {preview.isLoading ? (
        <Spinner label="Đang dựng bản xem trước…" />
      ) : preview.error || !preview.data ? (
        <ErrorBox error={preview.error} />
      ) : (
        <div className="space-y-4">
          <p className="text-xs text-muted">
            Nội dung mẫu với dữ liệu khách hàng giả định — biến {"{{org.*}}"} lấy theo tổ chức của bạn.
          </p>
          {preview.data.warnings.length > 0 && (
            <ul className="list-disc space-y-0.5 rounded-lg bg-amber-50 px-4 py-3 pl-8 text-xs text-amber-900">
              {preview.data.warnings.map((w, i) => (
                <li key={i}>{w}</li>
              ))}
            </ul>
          )}
          {preview.data.sections.map((s) => (
            <details key={s.id} open className="rounded-lg border border-line">
              <summary className="cursor-pointer px-4 py-2 text-sm font-semibold text-ink">{s.title}</summary>
              <div className="border-t border-line px-4 py-3">
                <Markdown>{s.markdown || "*— Trống —*"}</Markdown>
              </div>
            </details>
          ))}
        </div>
      )}
    </Modal>
  );
}

export function RejectModal({ name, pending, error, onClose, onSubmit }: {
  name: string; pending: boolean; error: unknown; onClose: () => void; onSubmit: (note: string) => void;
}) {
  const [note, setNote] = useState("");
  const submit = (e: FormEvent) => {
    e.preventDefault();
    if (note.trim()) onSubmit(note.trim());
  };
  return (
    <Modal title={`Từ chối mẫu: ${name}`} onClose={onClose}>
      <form onSubmit={submit} className="space-y-4">
        <Field label="Lý do từ chối" required hint="Chuyên viên sẽ thấy lý do này để chỉnh sửa.">
          <Textarea value={note} onChange={(e) => setNote(e.target.value)} rows={4}
            placeholder="VD: Thiếu mục kêu gọi đặt lịch tư vấn ở cuối." />
        </Field>
        <ErrorBox error={error} />
        <div className="flex gap-2">
          <Button type="submit" variant="danger" loading={pending} disabled={!note.trim()}>Từ chối</Button>
          <Button type="button" variant="secondary" onClick={onClose}>Hủy</Button>
        </div>
      </form>
    </Modal>
  );
}

export function PublishModal({ name, pending, error, onClose, onSubmit }: {
  name: string; pending: boolean; error: unknown; onClose: () => void;
  onSubmit: (body: { badge: string; origin_label: string }) => void;
}) {
  const [badge, setBadge] = useState("");
  const [origin, setOrigin] = useState("");
  const submit = (e: FormEvent) => {
    e.preventDefault();
    onSubmit({ badge: badge.trim(), origin_label: origin.trim() });
  };
  return (
    <Modal title={`Chia sẻ ra thư viện chung: ${name}`} onClose={onClose}>
      <form onSubmit={submit} className="space-y-4">
        <p className="text-sm text-muted">
          Mọi tổ chức đều thấy và lấy mẫu này về dùng. Nội dung chia sẻ là bản sao — sửa bản gốc rồi chia sẻ lại để cập nhật.
        </p>
        <Field label="Nhãn nổi bật" hint="VD: Chính chủ, Mẫu bán hàng. Bỏ trống nếu không cần.">
          <Input value={badge} onChange={(e) => setBadge(e.target.value)} maxLength={40} placeholder="Chính chủ" />
        </Field>
        <Field label="Tên đơn vị hiển thị" hint="Bỏ trống để dùng tên tổ chức của bạn.">
          <Input value={origin} onChange={(e) => setOrigin(e.target.value)} maxLength={120} placeholder="Tên studio của bạn" />
        </Field>
        <ErrorBox error={error} />
        <div className="flex gap-2">
          <Button type="submit" loading={pending}>Chia sẻ</Button>
          <Button type="button" variant="secondary" onClick={onClose}>Hủy</Button>
        </div>
      </form>
    </Modal>
  );
}
