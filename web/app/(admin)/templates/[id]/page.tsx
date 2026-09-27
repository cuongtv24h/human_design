"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, BookOpen, ChevronDown, ChevronUp, Copy, Eye, History, Pencil, Plus, Save, Sparkles, ThumbsDown, ThumbsUp, Trash2 } from "lucide-react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import { PreviewModal, PublishModal, RejectModal, TemplateStatusPill, useTemplateMutations } from "@/components/templates";
import { Badge, Button, Card, ErrorBox, Field, Input, Modal, PageHeader, Spinner, Textarea } from "@/components/ui";
import { api } from "@/lib/api";
import { useMe } from "@/lib/auth";
import { BLOCK_KIND_LABEL, SECTION_KIND_LABEL, STYLE_SOURCE_LABEL, STYLE_STATUS_LABEL, formatTimestamp } from "@/lib/format";
import type { BuiltinSection, ResolvedSection, StyleCompareOut, StyleHistoryOut, StylePreviewOut, StyleStatsOut, TemplateBlock, TemplateDetail, TemplateSample, TemplateSummary } from "@/lib/types";

const BLOCK_KINDS = ["intro", "core", "practice", "outro", "disclaimer"];

interface RawEntry {
  type: "builtin" | "block";
  ref: string;
  block_id: number | null;
  title_override: string;
  name: string;
  kind: string;
  title: string;
  body: string;
}

const BLANK: RawEntry = {
  type: "builtin", ref: "", block_id: null, title_override: "", name: "", kind: "core", title: "", body: "",
};

function fromResolved(s: ResolvedSection): RawEntry {
  if (s.type === "builtin") {
    return { ...BLANK, type: "builtin", ref: s.ref, title_override: s.title !== s.title_default ? s.title : "" };
  }
  if (s.block_id) {
    return { ...BLANK, type: "block", block_id: s.block_id, title_override: s.title !== s.title_default ? s.title : "" };
  }
  return {
    ...BLANK, type: "block", block_id: null, name: s.name, kind: s.kind || "core",
    title: s.title === "Khối nội dung" ? "" : s.title, body: s.body,
  };
}

function AddSectionModal({ onClose, onAdd }: { onClose: () => void; onAdd: (e: RawEntry) => void }) {
  const [mode, setMode] = useState<"builtin" | "block" | "inline">("builtin");
  const [ref, setRef] = useState("summary");
  const [blockId, setBlockId] = useState<number | null>(null);
  const [override, setOverride] = useState("");
  const [inline, setInline] = useState({ name: "", kind: "core", title: "", body: "" });
  const builtins = useQuery({
    queryKey: ["builtin-sections"],
    queryFn: () => api.get<BuiltinSection[]>("/templates/builtin-sections"),
    staleTime: 10 * 60_000,
  });
  const blocks = useQuery({
    queryKey: ["template-blocks"],
    queryFn: () => api.get<TemplateBlock[]>("/templates/blocks"),
  });
  const groups = ["summary", "core", "narrative", "domain"];
  const add = () => {
    if (mode === "builtin") onAdd({ ...BLANK, type: "builtin", ref, title_override: override.trim() });
    else if (mode === "block" && blockId) onAdd({ ...BLANK, type: "block", block_id: blockId, title_override: override.trim() });
    else if (mode === "inline" && inline.body.trim()) {
      onAdd({ ...BLANK, type: "block", block_id: null, name: inline.name.trim() || "Khối nội dung", kind: inline.kind, title: inline.title.trim(), body: inline.body });
    }
  };
  const valid = mode === "builtin" ? !!ref : mode === "block" ? blockId !== null : !!inline.body.trim();
  return (
    <Modal title="Thêm mục vào mẫu" onClose={onClose} wide>
      <div className="space-y-4">
        <div className="flex gap-2">
          {(["builtin", "block", "inline"] as const).map((k) => (
            <button key={k} type="button" onClick={() => setMode(k)}
              className={`rounded-lg border px-3 py-1.5 text-sm font-medium ${mode === k ? "border-brand-500 bg-brand-50 text-brand-700" : "border-line text-muted hover:text-ink"}`}>
              {k === "builtin" ? "Mục dựng sẵn" : k === "block" ? "Khối dùng chung" : "Viết trực tiếp"}
            </button>
          ))}
        </div>
        {mode === "builtin" && (
          <>
            <div className="max-h-72 space-y-3 overflow-y-auto rounded-lg border border-line p-3">
              {builtins.isLoading ? <Spinner /> : groups.map((g) => {
                const items = (builtins.data ?? []).filter((s) => s.kind === g);
                if (!items.length) return null;
                return (
                  <div key={g}>
                    <div className="mb-1 text-xs font-semibold uppercase tracking-wider text-muted">
                      {SECTION_KIND_LABEL[g] ?? g}
                    </div>
                    {items.map((s) => (
                      <label key={s.id} className="flex cursor-pointer items-center gap-2 rounded-md px-2 py-1 text-sm hover:bg-paper">
                        <input type="radio" name="builtin-ref" checked={ref === s.id} onChange={() => setRef(s.id)}
                          className="size-4 accent-brand-500" />
                        <span className="text-ink">{s.title}</span>
                      </label>
                    ))}
                  </div>
                );
              })}
            </div>
            <Field label="Đổi tên hiển thị (không bắt buộc)">
              <Input value={override} onChange={(e) => setOverride(e.target.value)} maxLength={160}
                placeholder="Bỏ trống để dùng tên gốc" />
            </Field>
          </>
        )}
        {mode === "block" && (
          <>
            <div className="max-h-72 space-y-1 overflow-y-auto rounded-lg border border-line p-3">
              {blocks.isLoading ? <Spinner /> : !(blocks.data ?? []).length ? (
                <p className="text-sm text-muted">Chưa có khối nào — sang tab Khối nội dung để tạo trước.</p>
              ) : blocks.data!.map((b) => (
                <label key={b.id} className="flex cursor-pointer items-center gap-2 rounded-md px-2 py-1.5 text-sm hover:bg-paper">
                  <input type="radio" name="block-ref" checked={blockId === b.id} onChange={() => setBlockId(b.id)}
                    className="size-4 accent-brand-500" />
                  <span className="font-medium text-ink">{b.name}</span>
                  <Badge>{BLOCK_KIND_LABEL[b.kind] ?? b.kind}</Badge>
                </label>
              ))}
            </div>
            <Field label="Đổi tên hiển thị (không bắt buộc)">
              <Input value={override} onChange={(e) => setOverride(e.target.value)} maxLength={160}
                placeholder="Bỏ trống để dùng tên khối" />
            </Field>
          </>
        )}
        {mode === "inline" && (
          <div className="space-y-3">
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label="Tên khối" required>
                <Input value={inline.name} onChange={(e) => setInline({ ...inline, name: e.target.value })} maxLength={120} />
              </Field>
              <Field label="Loại khối">
                <select value={inline.kind} onChange={(e) => setInline({ ...inline, kind: e.target.value })}
                  className="block w-full rounded-lg border border-line bg-white px-3 py-2 text-sm">
                  {BLOCK_KINDS.map((k) => (
                    <option key={k} value={k}>{BLOCK_KIND_LABEL[k] ?? k}</option>
                  ))}
                </select>
              </Field>
            </div>
            <Field label="Tiêu đề hiển thị">
              <Input value={inline.title} onChange={(e) => setInline({ ...inline, title: e.target.value })} maxLength={160} />
            </Field>
            <Field label="Nội dung" required hint="Hỗ trợ biến {{…}} giống khối dùng chung.">
              <Textarea value={inline.body} onChange={(e) => setInline({ ...inline, body: e.target.value })} rows={6}
                className="font-mono text-[13px]" />
            </Field>
          </div>
        )}
        <div className="flex gap-2">
          <Button disabled={!valid} onClick={add}>Thêm mục</Button>
          <Button variant="secondary" onClick={onClose}>Đóng</Button>
        </div>
      </div>
    </Modal>
  );
}

function SampleModal({ templateId, sample, onClose }: {
  templateId: number; sample: TemplateSample | null; onClose: () => void;
}) {
  const queryClient = useQueryClient();
  const [title, setTitle] = useState(sample?.title ?? "");
  const [body, setBody] = useState(sample?.body ?? "");
  const save = useMutation({
    mutationFn: () =>
      sample
        ? api.patch<TemplateSample>(`/templates/samples/${sample.id}`, { title: title.trim(), body })
        : api.post<TemplateSample>(`/templates/${templateId}/samples`, { title: title.trim(), body }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["template"] });
      onClose();
    },
  });
  return (
    <Modal title={sample ? "Sửa bài mẫu" : "Thêm bài mẫu"} onClose={onClose} wide>
      <div className="space-y-4">
        <Field label="Tiêu đề" required>
          <Input value={title} onChange={(e) => setTitle(e.target.value)} maxLength={200} />
        </Field>
        <Field label="Nội dung" required hint="Tối thiểu 50 ký tự. Bài mẫu chỉ để xem, tham khảo văn phong.">
          <Textarea value={body} onChange={(e) => setBody(e.target.value)} rows={10} />
        </Field>
        <ErrorBox error={save.error} />
        <div className="flex gap-2">
          <Button loading={save.isPending} disabled={!title.trim() || body.trim().length < 50} onClick={() => save.mutate()}>
            {sample ? "Lưu" : "Thêm"}
          </Button>
          <Button variant="secondary" onClick={onClose}>Hủy</Button>
        </div>
      </div>
    </Modal>
  );
}

function StatusBar({ detail, isAdmin, published }: { detail: TemplateDetail; isAdmin: boolean; published: boolean }) {
  const [rejectOpen, setRejectOpen] = useState(false);
  const [publishOpen, setPublishOpen] = useState(false);
  const m = useTemplateMutations();
  const err = m.setStatus.error ?? m.publish.error ?? m.unpublish.error;
  const btn = "rounded-md px-2.5 py-1.5 text-xs font-medium text-brand-700 hover:bg-brand-50";
  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center gap-2">
        <TemplateStatusPill status={detail.status} />
        {detail.visibility === "shared" ? <Badge tone="gold">Bản chia sẻ</Badge> : published ? <Badge tone="gold">Đã chia sẻ</Badge> : null}
        <span className="text-xs text-muted">v{detail.version} · {formatTimestamp(detail.updated_at)}</span>
        <span className="ml-auto flex flex-wrap gap-1">
          {detail.status === "pending" && isAdmin && detail.visibility === "private" && (
            <>
              <button type="button" className={btn}
                onClick={() => m.setStatus.mutate({ id: detail.id, body: { status: "active" } })}>Duyệt & kích hoạt</button>
              <button type="button" className="rounded-md px-2.5 py-1.5 text-xs font-medium text-red-700 hover:bg-red-50"
                onClick={() => setRejectOpen(true)}>Từ chối</button>
            </>
          )}
          {(detail.status === "draft" || detail.status === "rejected") && detail.visibility === "private" && (
            isAdmin
              ? <button type="button" className={btn}
                  onClick={() => m.setStatus.mutate({ id: detail.id, body: { status: "active" } })}>Kích hoạt</button>
              : <button type="button" className={btn}
                  onClick={() => m.setStatus.mutate({ id: detail.id, body: { status: "pending" } })}>Gửi duyệt</button>
          )}
          {detail.status === "pending" && !isAdmin && detail.visibility === "private" && (
            <button type="button" className={btn}
              onClick={() => m.setStatus.mutate({ id: detail.id, body: { status: "draft" } })}>Rút về nháp</button>
          )}
          {detail.status === "active" && isAdmin && detail.visibility === "private" && (
            <button type="button" className={btn}
              onClick={() => m.setStatus.mutate({ id: detail.id, body: { status: "archived" } })}>Ngưng dùng</button>
          )}
          {detail.status === "archived" && isAdmin && (
            <button type="button" className={btn}
              onClick={() => m.setStatus.mutate({ id: detail.id, body: { status: "active" } })}>Bật lại</button>
          )}
          {detail.status === "active" && isAdmin && detail.visibility === "private" && (
            published
              ? <button type="button" className={btn}
                  onClick={() => confirm(`Gỡ “${detail.name}” khỏi thư viện chung?`) && m.unpublish.mutate(detail.id)}>Gỡ chia sẻ</button>
              : <button type="button" className={btn} onClick={() => setPublishOpen(true)}>Chia sẻ</button>
          )}
        </span>
      </div>
      {detail.status === "rejected" && detail.review_note && (
        <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800">Lý do từ chối: {detail.review_note}</p>
      )}
      {detail.reports_count > 0 && (
        <p className="text-xs text-muted">
          Đang dùng trong {detail.reports_count} báo cáo — sửa mẫu không ảnh hưởng báo cáo đã tạo (mỗi báo cáo giữ bản chụp riêng).
        </p>
      )}
      <ErrorBox error={err} />
      {rejectOpen && (
        <RejectModal name={detail.name} pending={m.setStatus.isPending} error={m.setStatus.error}
          onClose={() => setRejectOpen(false)}
          onSubmit={(note) => m.setStatus.mutate(
            { id: detail.id, body: { status: "rejected", review_note: note } },
            { onSuccess: () => setRejectOpen(false) })} />
      )}
      {publishOpen && (
        <PublishModal name={detail.name} pending={m.publish.isPending} error={m.publish.error}
          onClose={() => setPublishOpen(false)}
          onSubmit={(body) => m.publish.mutate(
            { id: detail.id, body },
            { onSuccess: () => setPublishOpen(false) })} />
      )}
    </div>
  );
}

function EditorForm({ detail, isAdmin, editable }: { detail: TemplateDetail; isAdmin: boolean; editable: boolean }) {
  const queryClient = useQueryClient();
  const [entries, setEntries] = useState<RawEntry[]>(() => detail.sections.map(fromResolved));
  const [meta, setMeta] = useState({ name: detail.name, description: detail.description, badge: detail.badge });
  const [addOpen, setAddOpen] = useState(false);
  const builtins = useQuery({
    queryKey: ["builtin-sections"],
    queryFn: () => api.get<BuiltinSection[]>("/templates/builtin-sections"),
    staleTime: 10 * 60_000,
  });
  const blocks = useQuery({
    queryKey: ["template-blocks"],
    queryFn: () => api.get<TemplateBlock[]>("/templates/blocks"),
  });
  const builtinTitle = (ref: string) => builtins.data?.find((s) => s.id === ref)?.title ?? ref;
  const builtinKind = (ref: string) => builtins.data?.find((s) => s.id === ref)?.kind ?? "";
  const blockName = (id: number | null) => blocks.data?.find((b) => b.id === id)?.name ?? `Khối #${id}`;

  const move = (i: number, dir: -1 | 1) =>
    setEntries((es) => {
      const nx = [...es];
      const j = i + dir;
      if (j < 0 || j >= nx.length) return es;
      [nx[i], nx[j]] = [nx[j], nx[i]];
      return nx;
    });
  const upd = (i: number, patch: Partial<RawEntry>) =>
    setEntries((es) => es.map((e, k) => (k === i ? { ...e, ...patch } : e)));

  const saveMeta = useMutation({
    mutationFn: () => api.patch<TemplateDetail>(`/templates/${detail.id}`, {
      name: meta.name.trim(), description: meta.description.trim(), badge: meta.badge.trim(),
    }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["template"] }),
  });
  const saveSections = useMutation({
    mutationFn: () => api.patch<TemplateDetail>(`/templates/${detail.id}`, { sections: entries }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["template"] }),
  });
  const metaDirty = meta.name.trim() !== detail.name || meta.description.trim() !== detail.description || meta.badge.trim() !== detail.badge;
  const sectionsDirty = JSON.stringify(entries) !== JSON.stringify(detail.sections.map(fromResolved));

  return (
    <div className="space-y-6">
      <Card className="space-y-4 p-5">
        <h2 className="font-semibold text-ink">Thông tin chung</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Tên mẫu" required>
            <Input value={meta.name} onChange={(e) => setMeta({ ...meta, name: e.target.value })} maxLength={120} disabled={!editable} />
          </Field>
          <Field label="Nhãn nổi bật">
            <Input value={meta.badge} onChange={(e) => setMeta({ ...meta, badge: e.target.value })} maxLength={40} disabled={!editable} />
          </Field>
        </div>
        <Field label="Mô tả">
          <Input value={meta.description} onChange={(e) => setMeta({ ...meta, description: e.target.value })} maxLength={500} disabled={!editable} />
        </Field>
        {editable && (
          <div className="flex items-center gap-3">
            <Button loading={saveMeta.isPending} disabled={!metaDirty || !meta.name.trim()} onClick={() => saveMeta.mutate()}>
              <Save className="size-4" /> Lưu thông tin
            </Button>
            <ErrorBox error={saveMeta.error} />
          </div>
        )}
      </Card>

      <Card className="space-y-3 p-5">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="font-semibold text-ink">Các mục trong mẫu ({entries.length})</h2>
          {editable && <Button variant="secondary" onClick={() => setAddOpen(true)}><Plus className="size-4" /> Thêm mục</Button>}
        </div>
        {entries.map((e, i) => (
          <div key={i} className="rounded-lg border border-line p-3">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-muted">#{i + 1}</span>
              {e.type === "builtin" ? (
                <Badge>{SECTION_KIND_LABEL[builtinKind(e.ref)] ?? "Dựng sẵn"}</Badge>
              ) : (
                <Badge>{e.block_id ? "Khối dùng chung" : "Viết trực tiếp"}</Badge>
              )}
              <span className="truncate text-sm font-medium text-ink">
                {e.type === "builtin" ? builtinTitle(e.ref) : e.block_id ? blockName(e.block_id) : e.name || "Khối nội dung"}
              </span>
              {editable && (
                <span className="ml-auto flex shrink-0 gap-0.5">
                  <button type="button" title="Lên" disabled={i === 0} onClick={() => move(i, -1)}
                    className="rounded-md p-1 text-muted hover:bg-paper disabled:opacity-30"><ChevronUp className="size-4" /></button>
                  <button type="button" title="Xuống" disabled={i === entries.length - 1} onClick={() => move(i, 1)}
                    className="rounded-md p-1 text-muted hover:bg-paper disabled:opacity-30"><ChevronDown className="size-4" /></button>
                  <button type="button" title="Gỡ mục" disabled={entries.length <= 1}
                    onClick={() => setEntries((es) => es.filter((_, k) => k !== i))}
                    className="rounded-md p-1 text-muted hover:bg-red-50 hover:text-red-700 disabled:opacity-30"><Trash2 className="size-4" /></button>
                </span>
              )}
            </div>
            {editable && (e.type === "builtin" || e.block_id) && (
              <div className="mt-2">
                <Input value={e.title_override} onChange={(ev) => upd(i, { title_override: ev.target.value })} maxLength={160}
                  placeholder="Đổi tên hiển thị (bỏ trống để dùng tên gốc)" aria-label={`Tên hiển thị mục ${i + 1}`} />
              </div>
            )}
            {editable && e.type === "block" && !e.block_id && (
              <div className="mt-2 space-y-2">
                <div className="grid gap-2 sm:grid-cols-3">
                  <Input value={e.name} onChange={(ev) => upd(i, { name: ev.target.value })} maxLength={120}
                    placeholder="Tên khối" aria-label={`Tên khối mục ${i + 1}`} />
                  <select value={e.kind} onChange={(ev) => upd(i, { kind: ev.target.value })}
                    className="block w-full rounded-lg border border-line bg-white px-3 py-2 text-sm" aria-label={`Loại khối mục ${i + 1}`}>
                    {BLOCK_KINDS.map((k) => (
                      <option key={k} value={k}>{BLOCK_KIND_LABEL[k] ?? k}</option>
                    ))}
                  </select>
                  <Input value={e.title} onChange={(ev) => upd(i, { title: ev.target.value })} maxLength={160}
                    placeholder="Tiêu đề hiển thị" aria-label={`Tiêu đề mục ${i + 1}`} />
                </div>
                <Textarea value={e.body} onChange={(ev) => upd(i, { body: ev.target.value })} rows={5}
                  className="font-mono text-[13px]" aria-label={`Nội dung mục ${i + 1}`} />
              </div>
            )}
          </div>
        ))}
        {editable && (
          <div className="flex items-center gap-3">
            <Button loading={saveSections.isPending} disabled={!sectionsDirty} onClick={() => saveSections.mutate()}>
              <Save className="size-4" /> Lưu bố cục mục
            </Button>
            <ErrorBox error={saveSections.error} />
          </div>
        )}
      </Card>
      {addOpen && (
        <AddSectionModal onClose={() => setAddOpen(false)}
          onAdd={(e) => { setEntries((es) => [...es, e]); setAddOpen(false); }} />
      )}
    </div>
  );
}

function StyleHistory({ templateId, editable }: { templateId: number; editable: boolean }) {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const hist = useQuery({
    queryKey: ["template-style-history", templateId],
    queryFn: () => api.get<StyleHistoryOut[]>(`/templates/${templateId}/style-history`),
    enabled: open,
  });
  const restore = useMutation({
    mutationFn: (version: number) => api.post<TemplateDetail>(`/templates/${templateId}/style-restore/${version}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["template"] });
      queryClient.invalidateQueries({ queryKey: ["template-style-history", templateId] });
    },
  });
  return (
    <div className="space-y-2 border-t border-line pt-4">
      <button type="button" onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-2 text-sm font-semibold text-ink hover:text-brand-700">
        <History className="size-4" /> Lịch sử văn phong
        {open ? <ChevronUp className="size-4" /> : <ChevronDown className="size-4" />}
      </button>
      {open && (
        <div className="space-y-2">
          <ErrorBox error={hist.error ?? restore.error} />
          {hist.isLoading ? <Spinner /> : (hist.data ?? []).map((h) => (
            <div key={h.version_no} className="flex flex-wrap items-start justify-between gap-2 rounded-xl bg-paper p-3 text-sm">
              <div className="min-w-0">
                <div className="font-medium text-ink">
                  Bản {h.version_no} · {STYLE_SOURCE_LABEL[h.source] ?? h.source}
                </div>
                <div className="text-xs text-muted">
                  {h.created_by_name} · {formatTimestamp(h.created_at)} · {h.sample_count} bài mẫu
                </div>
                {h.tone ? <p className="mt-1 text-ink">{h.tone}</p> : null}
              </div>
              {editable && (
                <Button variant="secondary" className="px-3 py-1.5 text-xs" loading={restore.isPending}
                  onClick={() => confirm(`Khôi phục văn phong bản ${h.version_no}? Bản hiện tại sẽ được lưu lại.`) && restore.mutate(h.version_no)}>
                  Khôi phục
                </Button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function StyleCopy({ templateId }: { templateId: number }) {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [fromId, setFromId] = useState("");
  const list = useQuery({
    queryKey: ["templates"],
    queryFn: () => api.get<TemplateSummary[]>("/templates"),
    enabled: open,
  });
  const copy = useMutation({
    mutationFn: () => api.post<TemplateDetail>(`/templates/${templateId}/style-copy`, { from_template_id: Number(fromId) }),
    onSuccess: () => {
      setOpen(false);
      queryClient.invalidateQueries({ queryKey: ["template"] });
      queryClient.invalidateQueries({ queryKey: ["template-style-history", templateId] });
    },
  });
  const candidates = (list.data ?? []).filter((t) => t.id !== templateId && t.style_status === "ready");
  if (!open) {
    return (
      <Button variant="secondary" onClick={() => setOpen(true)}>
        <Copy className="size-4" /> Sao chép từ mẫu khác
      </Button>
    );
  }
  return (
    <div className="space-y-2 rounded-xl border border-line p-3">
      <Field label="Mẫu nguồn (đã có văn phong)">
        <select value={fromId} onChange={(e) => setFromId(e.target.value)}
          className="w-full rounded-lg border border-line bg-white px-3 py-2 text-sm text-ink">
          <option value="">— Chọn mẫu —</option>
          {candidates.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
        </select>
      </Field>
      {list.isSuccess && candidates.length === 0 && (
        <p className="text-xs text-muted">Chưa có mẫu nào khác có văn phong sẵn sàng.</p>
      )}
      <ErrorBox error={list.error ?? copy.error} />
      <div className="flex gap-2">
        <Button loading={copy.isPending} disabled={!fromId} onClick={() => copy.mutate()}>
          Sao chép
        </Button>
        <Button variant="secondary" onClick={() => setOpen(false)}>Hủy</Button>
      </div>
    </div>
  );
}

function StyleVerify({ templateId, editable }: { templateId: number; editable: boolean }) {
  const [topic, setTopic] = useState("");
  const [preview, setPreview] = useState<StylePreviewOut | null>(null);
  const [compare, setCompare] = useState<StyleCompareOut | null>(null);
  const body = { topic: topic.trim() ? topic.trim() : null };
  const runPreview = useMutation({
    mutationFn: () => api.post<StylePreviewOut>(`/templates/${templateId}/style-preview`, body),
    onSuccess: (out) => { setPreview(out); setCompare(null); },
  });
  const runCompare = useMutation({
    mutationFn: () => api.post<StyleCompareOut>(`/templates/${templateId}/style-compare`, body),
    onSuccess: (out) => { setCompare(out); setPreview(null); },
  });
  if (!editable) return null;
  return (
    <div className="space-y-3 border-t border-line pt-4">
      <div className="text-sm font-semibold text-ink">Kiểm chứng văn phong</div>
      <p className="text-xs text-muted">
        AI viết thử một đoạn ngắn để bạn duyệt giọng trước khi dùng cho báo cáo thật.
      </p>
      <Input value={topic} onChange={(e) => setTopic(e.target.value)}
        placeholder="Chủ đề viết thử (bỏ trống = chủ đề mặc định)" maxLength={300} />
      <div className="flex flex-wrap gap-2">
        <Button variant="secondary" loading={runPreview.isPending} onClick={() => runPreview.mutate()}>
          <Sparkles className="size-4" /> Viết thử
        </Button>
        <Button variant="secondary" loading={runCompare.isPending} onClick={() => runCompare.mutate()}>
          <Eye className="size-4" /> So sánh A/B
        </Button>
      </div>
      <ErrorBox error={runPreview.error ?? runCompare.error} />
      {preview && (
        <div className="space-y-1 rounded-xl bg-paper p-4">
          <div className="text-xs text-muted">Viết thử · {preview.topic} · {preview.provider}</div>
          <p className="whitespace-pre-line text-sm text-ink">{preview.preview}</p>
        </div>
      )}
      {compare && (
        <div className="space-y-2">
          <div className="text-xs text-muted">So sánh · {compare.topic} · {compare.provider}</div>
          <div className="grid gap-3 md:grid-cols-2">
            <div className="space-y-1 rounded-xl bg-paper p-4">
              <div className="text-xs font-semibold uppercase tracking-wider text-muted">A · Giọng mặc định</div>
              <p className="whitespace-pre-line text-sm text-ink">{compare.default_text}</p>
            </div>
            <div className="space-y-1 rounded-xl border border-brand-200 bg-brand-50 p-4">
              <div className="text-xs font-semibold uppercase tracking-wider text-brand-700">B · Giọng mẫu này</div>
              <p className="whitespace-pre-line text-sm text-ink">{compare.styled_text}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StyleStats({ templateId }: { templateId: number }) {
  const stats = useQuery({
    queryKey: ["template-style-stats", templateId],
    queryFn: () => api.get<StyleStatsOut>(`/templates/${templateId}/style-stats`),
  });
  if (stats.isLoading || stats.isError) return null;
  if (!stats.data || (stats.data.up === 0 && stats.data.down === 0)) return null;
  return (
    <div className="space-y-2 border-t border-line pt-4">
      <div className="flex items-center gap-3 text-sm">
        <span className="font-semibold text-ink">Đánh giá từ báo cáo thực tế:</span>
        <span className="flex items-center gap-1 text-ink"><ThumbsUp className="size-4 text-brand-600" /> {stats.data.up}</span>
        <span className="flex items-center gap-1 text-ink"><ThumbsDown className="size-4 text-red-600" /> {stats.data.down}</span>
      </div>
      {stats.data.by_version.length > 0 && (
        <ul className="flex flex-wrap gap-2 text-xs text-muted">
          {stats.data.by_version.map((v) => (
            <li key={v.version} className="rounded-full bg-paper px-2.5 py-1">
              Bản {v.version}: {v.up} thích / {v.down} không thích
            </li>
          ))}
        </ul>
      )}
      <ul className="space-y-1 text-sm">
        {stats.data.reports.map((rep) => (
          <li key={rep.report_id} className="flex items-center gap-2">
            {rep.rating === 1
              ? <ThumbsUp className="size-3.5 shrink-0 text-brand-600" />
              : <ThumbsDown className="size-3.5 shrink-0 text-red-600" />}
            <Link href={`/reports/${rep.report_id}`} className="text-brand-700 hover:underline">
              {rep.client_name}
            </Link>
            <span className="text-xs text-muted">{formatTimestamp(rep.created_at)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function StyleCard({ detail, editable }: { detail: TemplateDetail; editable: boolean }) {
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({ tone: "", rhythm: "", vocabulary: "", structure: "", do: "", dont: "", excerpt: "" });
  const st = detail.style_status || "none";
  const p = detail.style_profile;
  const startEdit = () => {
    setForm({
      tone: p.tone, rhythm: p.rhythm, vocabulary: p.vocabulary, structure: p.structure,
      do: p.do.join("\n"), dont: p.dont.join("\n"), excerpt: p.excerpt,
    });
    setEditing(true);
  };
  const refresh = () => queryClient.invalidateQueries({ queryKey: ["template"] });
  const analyze = useMutation({
    mutationFn: () => api.post<TemplateDetail>(`/templates/${detail.id}/analyze-style`),
    onSuccess: refresh,
  });
  const save = useMutation({
    mutationFn: () => api.patch<TemplateDetail>(`/templates/${detail.id}`, {
      style_profile: {
        tone: form.tone.trim(), rhythm: form.rhythm.trim(), vocabulary: form.vocabulary.trim(),
        structure: form.structure.trim(), excerpt: form.excerpt.trim(),
        do: form.do.split("\n").map((s) => s.trim()).filter(Boolean),
        dont: form.dont.split("\n").map((s) => s.trim()).filter(Boolean),
      },
    }),
    onSuccess: () => { setEditing(false); refresh(); },
  });
  const tone = st === "ready" ? "brand" : st === "stale" ? "gold" : "stone";
  return (
    <Card className="space-y-4 p-5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="flex items-center gap-2 font-semibold text-ink">
          <Sparkles className="size-4" /> Văn phong AI
        </h2>
        <Badge tone={tone}>{STYLE_STATUS_LABEL[st] ?? st}</Badge>
      </div>
      <p className="text-xs text-muted">
        AI học cách viết từ bài mẫu của mẫu này. Áp dụng khi tạo báo cáo ở chế độ AI biên tập (có công tắc tắt ở bước tạo).
      </p>
      <ErrorBox error={analyze.error ?? save.error} />
      {editing ? (
        <div className="space-y-3">
          <div className="grid gap-3 sm:grid-cols-2">
            <Field label="Giọng điệu"><Input value={form.tone} onChange={(e) => setForm({ ...form, tone: e.target.value })} /></Field>
            <Field label="Nhịp câu"><Input value={form.rhythm} onChange={(e) => setForm({ ...form, rhythm: e.target.value })} /></Field>
            <Field label="Từ vựng"><Input value={form.vocabulary} onChange={(e) => setForm({ ...form, vocabulary: e.target.value })} /></Field>
            <Field label="Cấu trúc"><Input value={form.structure} onChange={(e) => setForm({ ...form, structure: e.target.value })} /></Field>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <Field label="Nên (mỗi dòng một điều)"><Textarea value={form.do} onChange={(e) => setForm({ ...form, do: e.target.value })} rows={4} /></Field>
            <Field label="Tránh (mỗi dòng một điều)"><Textarea value={form.dont} onChange={(e) => setForm({ ...form, dont: e.target.value })} rows={4} /></Field>
          </div>
          <Field label="Đoạn trích minh họa"><Textarea value={form.excerpt} onChange={(e) => setForm({ ...form, excerpt: e.target.value })} rows={3} /></Field>
          <div className="flex gap-2">
            <Button loading={save.isPending} onClick={() => save.mutate()}><Save className="size-4" /> Lưu văn phong</Button>
            <Button variant="secondary" onClick={() => setEditing(false)}>Hủy</Button>
          </div>
        </div>
      ) : st === "none" ? (
        <div className="space-y-3">
          <p className="rounded-lg bg-paper px-4 py-5 text-center text-sm text-muted">
            {detail.samples.length < 2
              ? `Cần ít nhất 2 bài mẫu để phân tích (hiện có ${detail.samples.length}). Thêm bài mẫu ở mục bên dưới trước.`
              : "Chưa phân tích. AI sẽ đọc các bài mẫu và trích thành hồ sơ văn phong (tốn 1 lượt gọi AI)."}
          </p>
          {editable && detail.samples.length >= 2 && (
            <Button loading={analyze.isPending} onClick={() => analyze.mutate()}>
              <Sparkles className="size-4" /> Phân tích văn phong
            </Button>
          )}
          {editable && <StyleCopy templateId={detail.id} />}
        </div>
      ) : (
        <div className="space-y-3">
          {st === "stale" && (
            <p className="rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-900">
              Bài mẫu đã thay đổi sau lần phân tích trước — nên phân tích lại để hồ sơ khớp.
            </p>
          )}
          {p.excerpt ? (
            <blockquote className="border-l-2 border-brand-500 pl-3 text-sm italic text-ink">“{p.excerpt}”</blockquote>
          ) : null}
          <dl className="grid gap-2 text-sm sm:grid-cols-2">
            {[["Giọng điệu", p.tone], ["Nhịp câu", p.rhythm], ["Từ vựng", p.vocabulary], ["Cấu trúc", p.structure]].map(([k, v]) => (
              v ? <div key={k}><dt className="text-xs font-semibold uppercase tracking-wider text-muted">{k}</dt><dd className="text-ink">{v}</dd></div> : null
            ))}
          </dl>
          <div className="grid gap-3 text-sm sm:grid-cols-2">
            {p.do.length > 0 && (
              <div><div className="text-xs font-semibold uppercase tracking-wider text-muted">Nên</div>
                <ul className="list-disc pl-5 text-ink">{p.do.map((d, i) => <li key={i}>{d}</li>)}</ul></div>
            )}
            {p.dont.length > 0 && (
              <div><div className="text-xs font-semibold uppercase tracking-wider text-muted">Tránh</div>
                <ul className="list-disc pl-5 text-ink">{p.dont.map((d, i) => <li key={i}>{d}</li>)}</ul></div>
            )}
          </div>
          <p className="text-xs text-muted">Trích từ {p.sample_count} bài mẫu.</p>
          {editable && (
            <div className="flex flex-wrap gap-2">
              <Button variant="secondary" loading={analyze.isPending} onClick={() => analyze.mutate()}>
                <Sparkles className="size-4" /> Phân tích lại
              </Button>
              <Button variant="secondary" onClick={startEdit}><Pencil className="size-4" /> Sửa tay</Button>
            </div>
          )}
          <StyleVerify templateId={detail.id} editable={editable} />
          <StyleStats templateId={detail.id} />
          <StyleHistory templateId={detail.id} editable={editable} />
          {editable && <StyleCopy templateId={detail.id} />}
        </div>
      )}
    </Card>
  );
}

function SamplesCard({ detail, editable }: { detail: TemplateDetail; editable: boolean }) {
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState<TemplateSample | null | undefined>(undefined);
  const removeSample = useMutation({
    mutationFn: (id: number) => api.del(`/templates/samples/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["template"] }),
  });
  return (
    <Card className="space-y-3 p-5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="flex items-center gap-2 font-semibold text-ink">
          <BookOpen className="size-4" /> Bài mẫu ({detail.samples.length}/10)
        </h2>
        {editable && detail.samples.length < 10 && (
          <Button variant="secondary" onClick={() => setEditing(null)}><Plus className="size-4" /> Thêm bài mẫu</Button>
        )}
      </div>
      <p className="text-xs text-muted">Bài mẫu chỉ để xem, tham khảo văn phong — không đưa vào báo cáo.</p>
      <ErrorBox error={removeSample.error} />
      {!detail.samples.length ? (
        <p className="rounded-lg bg-paper px-4 py-5 text-center text-sm text-muted">Chưa có bài mẫu nào.</p>
      ) : (
        <div className="space-y-2">
          {detail.samples.map((s) => (
            <details key={s.id} className="rounded-lg border border-line">
              <summary className="flex cursor-pointer items-center gap-2 px-4 py-2 text-sm font-medium text-ink">
                <span className="truncate">{s.title}</span>
                {editable && (
                  <span className="ml-auto flex shrink-0 gap-2" onClick={(e) => e.preventDefault()}>
                    <button type="button" className="text-xs font-medium text-brand-700 hover:underline"
                      onClick={() => setEditing(s)}>Sửa</button>
                    <button type="button" className="text-xs font-medium text-red-700 hover:underline"
                      onClick={() => confirm(`Xóa bài mẫu “${s.title}”?`) && removeSample.mutate(s.id)}>Xóa</button>
                  </span>
                )}
              </summary>
              <div className="whitespace-pre-wrap border-t border-line px-4 py-3 text-sm text-muted">{s.body}</div>
            </details>
          ))}
        </div>
      )}
      {editing !== undefined && (
        <SampleModal templateId={detail.id} sample={editing} onClose={() => setEditing(undefined)} />
      )}
    </Card>
  );
}

function DetailView({ detail, isAdmin }: { detail: TemplateDetail; isAdmin: boolean }) {
  const router = useRouter();
  const [previewOpen, setPreviewOpen] = useState(false);
  const lib = useQuery({
    queryKey: ["templates-library"],
    queryFn: () => api.get<TemplateDetail[]>("/templates/library"),
    staleTime: 60_000,
  });
  const published = (lib.data ?? []).some((t) => t.key === detail.key);
  const m = useTemplateMutations();
  const take = useMutation({
    mutationFn: () => api.post<TemplateDetail>(`/templates/library/${detail.key}/import`),
    onSuccess: (d) => router.push(`/templates/${d.id}`),
  });
  const editable = detail.visibility === "private"
    && (isAdmin || ["draft", "pending", "rejected"].includes(detail.status));
  return (
    <div className="space-y-6">
      <PageHeader title={detail.name}
        description={
          <span className="flex flex-wrap items-center gap-2">
            <span>Tác giả: {detail.created_by_name}</span>
            {detail.origin_label ? <span>· {detail.origin_label}</span> : null}
            {detail.description ? <span className="basis-full text-muted">{detail.description}</span> : null}
          </span>
        }
        actions={
          <>
            <Link href="/templates"
              className="inline-flex items-center gap-2 rounded-lg border border-line bg-white px-4 py-2 text-sm font-medium text-ink hover:bg-paper">
              <ArrowLeft className="size-4" /> Danh sách
            </Link>
            <Button variant="secondary" onClick={() => setPreviewOpen(true)}><Eye className="size-4" /> Xem trước</Button>
            <DetailCopyButton detailId={detail.id} />
            {editable && (
              <Button variant="danger"
                onClick={() => confirm(`Xóa mẫu “${detail.name}”? Báo cáo đã tạo không bị ảnh hưởng.`) &&
                  m.removeTpl.mutate(detail.id, { onSuccess: () => router.push("/templates") })}>
                <Trash2 className="size-4" /> Xóa
              </Button>
            )}
            {detail.visibility === "shared" && (
              <Button loading={take.isPending} onClick={() => take.mutate()}><Copy className="size-4" /> Lấy về studio</Button>
            )}
          </>
        }
      />
      <ErrorBox error={take.error} />
      <StatusBar detail={detail} isAdmin={isAdmin} published={published} />
      {detail.visibility === "shared" ? (
        <Card className="space-y-2 p-5">
          <h2 className="font-semibold text-ink">Các mục trong mẫu ({detail.sections.length})</h2>
          <p className="text-sm text-muted">Bản chia sẻ chỉ đọc — lấy về studio để chỉnh sửa thành mẫu riêng.</p>
          <ol className="list-decimal space-y-1 pl-5 text-sm">
            {detail.sections.map((s, i) => (
              <li key={i}>{s.title} <span className="text-muted">({s.type === "builtin" ? builtinKindLabel(s.kind) : s.block_id ? "khối dùng chung" : "viết trực tiếp"})</span></li>
            ))}
          </ol>
        </Card>
      ) : editable ? (
        <EditorForm detail={detail} isAdmin={isAdmin} editable />
      ) : (
        <Card className="space-y-2 p-5">
          <h2 className="font-semibold text-ink">Các mục trong mẫu ({detail.sections.length})</h2>
          <p className="text-sm text-muted">Bạn chỉ có quyền xem mẫu này.</p>
          <ol className="list-decimal space-y-1 pl-5 text-sm">
            {detail.sections.map((s, i) => (
              <li key={i}>{s.title}</li>
            ))}
          </ol>
        </Card>
      )}
      {detail.visibility === "private" && <StyleCard detail={detail} editable={editable} />}
      <SamplesCard detail={detail} editable={editable} />
      {previewOpen && <PreviewModal templateId={detail.id} name={detail.name} onClose={() => setPreviewOpen(false)} />}
    </div>
  );
}

function builtinKindLabel(kind: string) {
  return SECTION_KIND_LABEL[kind] ?? kind;
}

function DetailCopyButton({ detailId }: { detailId: number }) {
  const router = useRouter();
  const m = useTemplateMutations();
  return (
    <Button variant="secondary"
      onClick={() => m.duplicate.mutate(detailId, { onSuccess: (d) => router.push(`/templates/${d.id}`) })}>
      <Copy className="size-4" /> Nhân bản
    </Button>
  );
}

export default function TemplateDetailPage() {
  const { id } = useParams<{ id: string }>();
  const me = useMe();
  const detail = useQuery({
    queryKey: ["template", id],
    queryFn: () => api.get<TemplateDetail>(`/templates/${id}`),
    enabled: !!id,
  });
  if (detail.isLoading) return <Spinner />;
  if (detail.error || !detail.data) return <ErrorBox error={detail.error ?? "Không tìm thấy mẫu báo cáo."} />;
  return <DetailView detail={detail.data} isAdmin={me.data?.role === "admin"} />;
}
