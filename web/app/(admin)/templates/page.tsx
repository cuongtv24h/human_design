"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Copy, Eye, Globe, Layers, Library, Pencil, Plus, Search, Trash2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { PreviewModal, PublishModal, RejectModal, TemplateStatusPill, useTemplateMutations } from "@/components/templates";
import { Badge, Button, Card, EmptyState, ErrorBox, Field, Input, Modal, PageHeader, Spinner, Textarea, cx } from "@/components/ui";
import { api, qs } from "@/lib/api";
import { useMe } from "@/lib/auth";
import { BLOCK_KIND_LABEL, TEMPLATE_STATUS_LABEL, formatTimestamp } from "@/lib/format";
import { useDebounced } from "@/lib/hooks";
import type { BlockVariable, BuiltinSection, OrgVars, TemplateBlock, TemplateDetail, TemplateSummary } from "@/lib/types";

type Tab = "studio" | "library" | "blocks" | "orgvars";

const STATUS_FILTER = ["", "draft", "pending", "active", "rejected", "archived"];
const BLOCK_KINDS = ["intro", "core", "practice", "outro", "disclaimer"];

function RowButton({ children, onClick, danger, title }: {
  children: string; onClick: () => void; danger?: boolean; title?: string;
}) {
  return (
    <button type="button" title={title} onClick={onClick}
      className={cx("rounded-md px-2 py-1 text-xs font-medium",
        danger ? "text-red-700 hover:bg-red-50" : "text-brand-700 hover:bg-brand-50")}>
      {children}
    </button>
  );
}

function VariablesHelp() {
  const vars = useQuery({
    queryKey: ["template-variables"],
    queryFn: () => api.get<BlockVariable[]>("/templates/variables"),
    staleTime: 10 * 60_000,
  });
  if (!vars.data) return null;
  return (
    <details className="rounded-lg bg-paper px-3 py-2 text-xs">
      <summary className="cursor-pointer font-medium text-ink">Biến dùng được trong khối ({vars.data.length})</summary>
      <ul className="mt-2 space-y-1 text-muted">
        {vars.data.map((v) => (
          <li key={v.path}>
            <code className="text-ink">{"{{"}{v.path}{"}}"}</code> — {v.label}
            {v.example ? <span className="text-muted/70"> (vd: {v.example})</span> : null}
          </li>
        ))}
      </ul>
      <p className="mt-2 text-muted">Biến tổ chức: {"{{org.<key>}}"} — do quản trị viên khai báo ở tab Biến tổ chức.</p>
    </details>
  );
}

function CreateModal({ onClose }: { onClose: () => void }) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [source, setSource] = useState<"blank" | "sections" | "operating_manual">("blank");
  const [firstRef, setFirstRef] = useState("summary");
  const builtins = useQuery({
    queryKey: ["builtin-sections"],
    queryFn: () => api.get<BuiltinSection[]>("/templates/builtin-sections"),
    staleTime: 10 * 60_000,
  });
  const create = useMutation({
    mutationFn: () =>
      source === "blank"
        ? api.post<TemplateDetail>("/templates", {
            name: name.trim(), description: description.trim(), sections: [{ type: "builtin", ref: firstRef }],
          })
        : api.post<TemplateDetail>("/templates/from-builtin", { builtin: source, name: name.trim() }),
    onSuccess: (detail) => {
      queryClient.invalidateQueries({ queryKey: ["templates"] });
      router.push(`/templates/${detail.id}`);
    },
  });
  return (
    <Modal title="Tạo mẫu báo cáo" onClose={onClose}>
      <div className="space-y-4">
        <Field label="Tên mẫu" required>
          <Input value={name} onChange={(e) => setName(e.target.value)} maxLength={120}
            placeholder="VD: Mẫu tư vấn tình yêu" />
        </Field>
        <Field label="Mô tả">
          <Input value={description} onChange={(e) => setDescription(e.target.value)} maxLength={500}
            placeholder="Mẫu này dùng cho trường hợp nào?" />
        </Field>
        <Field label="Bắt đầu từ">
          <select value={source} onChange={(e) => setSource(e.target.value as typeof source)}
            className="block w-full rounded-lg border border-line bg-white px-3 py-2 text-sm">
            <option value="blank">Mẫu trắng (1 mục đầu tiên)</option>
            <option value="sections">Sao từ mẫu hệ thống “Theo mục”</option>
            <option value="operating_manual">Sao từ mẫu hệ thống “Cẩm nang vận hành”</option>
          </select>
        </Field>
        {source === "blank" && (
          <Field label="Mục đầu tiên">
            <select value={firstRef} onChange={(e) => setFirstRef(e.target.value)}
              className="block w-full rounded-lg border border-line bg-white px-3 py-2 text-sm">
              {(builtins.data ?? []).map((s) => (
                <option key={s.id} value={s.id}>{s.title}</option>
              ))}
            </select>
          </Field>
        )}
        <ErrorBox error={create.error} />
        <div className="flex gap-2">
          <Button loading={create.isPending} disabled={!name.trim()} onClick={() => create.mutate()}>
            Tạo và soạn thảo
          </Button>
          <Button variant="secondary" onClick={onClose}>Hủy</Button>
        </div>
      </div>
    </Modal>
  );
}

function StudioTab({ isAdmin }: { isAdmin: boolean }) {
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("");
  const [createOpen, setCreateOpen] = useState(false);
  const [preview, setPreview] = useState<TemplateSummary | null>(null);
  const [rejecting, setRejecting] = useState<TemplateSummary | null>(null);
  const [publishing, setPublishing] = useState<TemplateSummary | null>(null);
  const query = useDebounced(q);
  const list = useQuery({
    queryKey: ["templates", query, status],
    queryFn: () => api.get<TemplateSummary[]>(`/templates${qs({ q: query, status })}`),
  });
  const library = useQuery({
    queryKey: ["templates-library"],
    queryFn: () => api.get<TemplateSummary[]>("/templates/library"),
    staleTime: 60_000,
  });
  const publishedKeys = new Set((library.data ?? []).map((t) => t.key));
  const m = useTemplateMutations();
  const actionError = m.setStatus.error ?? m.removeTpl.error ?? m.duplicate.error ?? m.publish.error ?? m.unpublish.error;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative min-w-60 flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted" aria-hidden />
          <Input className="pl-9" placeholder="Tìm mẫu…" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Tìm mẫu" />
        </div>
        <select value={status} onChange={(e) => setStatus(e.target.value)} aria-label="Lọc trạng thái"
          className="rounded-lg border border-line bg-white px-3 py-2 text-sm">
          {STATUS_FILTER.map((s) => (
            <option key={s} value={s}>{s ? TEMPLATE_STATUS_LABEL[s] : "Mọi trạng thái"}</option>
          ))}
        </select>
        <Button onClick={() => setCreateOpen(true)}><Plus className="size-4" /> Tạo mẫu</Button>
      </div>
      <ErrorBox error={actionError} />
      {list.isLoading ? <Spinner /> : !list.data?.length ? (
        <Card><EmptyState title="Chưa có mẫu nào"
          description="Tạo mẫu đầu tiên cho tổ chức, hoặc vào thư viện chung lấy mẫu về."
          action={<Button onClick={() => setCreateOpen(true)}><Plus className="size-4" /> Tạo mẫu</Button>} /></Card>
      ) : (
        <Card className="divide-y divide-line">
          {list.data.map((t) => (
            <div key={t.id} className="flex flex-wrap items-center gap-x-4 gap-y-2 px-4 py-3">
              <div className="min-w-52 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <Link href={`/templates/${t.id}`} className="font-medium text-ink hover:text-brand-700">{t.name}</Link>
                  <TemplateStatusPill status={t.status} />
                  {t.visibility === "shared" ? <Badge tone="gold">Đã chia sẻ</Badge>
                    : publishedKeys.has(t.key) ? <Badge tone="gold">Đã chia sẻ</Badge> : null}
                  {t.badge ? <Badge>{t.badge}</Badge> : null}
                </div>
                <div className="mt-0.5 text-xs text-muted">
                  {t.sections_count} mục · {t.samples_count} bài mẫu · {t.reports_count} báo cáo · {t.created_by_name} · {formatTimestamp(t.updated_at)}
                </div>
              </div>
              <div className="flex flex-wrap items-center gap-1">
                <Link href={`/templates/${t.id}`} title="Soạn thảo"
                  className="rounded-md p-1.5 text-muted hover:bg-brand-50 hover:text-brand-700"><Pencil className="size-4" /></Link>
                <button type="button" title="Xem trước" onClick={() => setPreview(t)}
                  className="rounded-md p-1.5 text-muted hover:bg-brand-50 hover:text-brand-700"><Eye className="size-4" /></button>
                {(t.status === "draft" || t.status === "rejected") && !isAdmin && (
                  <RowButton onClick={() => m.setStatus.mutate({ id: t.id, body: { status: "pending" } })}>Gửi duyệt</RowButton>
                )}
                {(t.status === "draft" || t.status === "rejected") && isAdmin && t.visibility === "private" && (
                  <RowButton onClick={() => m.setStatus.mutate({ id: t.id, body: { status: "active" } })}>Kích hoạt</RowButton>
                )}
                {t.status === "pending" && isAdmin && (
                  <>
                    <RowButton onClick={() => m.setStatus.mutate({ id: t.id, body: { status: "active" } })}>Duyệt</RowButton>
                    <RowButton danger onClick={() => setRejecting(t)}>Từ chối</RowButton>
                  </>
                )}
                {t.status === "pending" && !isAdmin && (
                  <RowButton onClick={() => m.setStatus.mutate({ id: t.id, body: { status: "draft" } })}>Rút về nháp</RowButton>
                )}
                {t.status === "active" && isAdmin && t.visibility === "private" && (
                  <RowButton onClick={() => m.setStatus.mutate({ id: t.id, body: { status: "archived" } })}>Ngưng dùng</RowButton>
                )}
                {t.status === "archived" && isAdmin && (
                  <RowButton onClick={() => m.setStatus.mutate({ id: t.id, body: { status: "active" } })}>Bật lại</RowButton>
                )}
                {t.status === "active" && isAdmin && t.visibility === "private" && (
                  publishedKeys.has(t.key)
                    ? <RowButton onClick={() => confirm(`Gỡ “${t.name}” khỏi thư viện chung?`) && m.unpublish.mutate(t.id)}>Gỡ chia sẻ</RowButton>
                    : <RowButton onClick={() => setPublishing(t)}>Chia sẻ</RowButton>
                )}
                <button type="button" title="Nhân bản" onClick={() => m.duplicate.mutate(t.id)}
                  className="rounded-md p-1.5 text-muted hover:bg-brand-50 hover:text-brand-700"><Copy className="size-4" /></button>
                {(isAdmin || t.status !== "active") && (
                  <button type="button" title="Xóa" onClick={() => confirm(`Xóa mẫu “${t.name}”? Báo cáo đã tạo không bị ảnh hưởng.`) && m.removeTpl.mutate(t.id)}
                    className="rounded-md p-1.5 text-muted hover:bg-red-50 hover:text-red-700"><Trash2 className="size-4" /></button>
                )}
              </div>
            </div>
          ))}
        </Card>
      )}
      {createOpen && <CreateModal onClose={() => setCreateOpen(false)} />}
      {preview && <PreviewModal templateId={preview.id} name={preview.name} onClose={() => setPreview(null)} />}
      {rejecting && (
        <RejectModal name={rejecting.name} pending={m.setStatus.isPending} error={m.setStatus.error}
          onClose={() => setRejecting(null)}
          onSubmit={(note) => m.setStatus.mutate(
            { id: rejecting.id, body: { status: "rejected", review_note: note } },
            { onSuccess: () => setRejecting(null) })} />
      )}
      {publishing && (
        <PublishModal name={publishing.name} pending={m.publish.isPending} error={m.publish.error}
          onClose={() => setPublishing(null)}
          onSubmit={(body) => m.publish.mutate(
            { id: publishing.id, body },
            { onSuccess: () => setPublishing(null) })} />
      )}
    </div>
  );
}

function LibraryTab() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [preview, setPreview] = useState<TemplateSummary | null>(null);
  const lib = useQuery({
    queryKey: ["templates-library"],
    queryFn: () => api.get<TemplateSummary[]>("/templates/library"),
  });
  const take = useMutation({
    mutationFn: (key: string) => api.post<TemplateDetail>(`/templates/library/${key}/import`),
    onSuccess: (detail) => {
      queryClient.invalidateQueries({ queryKey: ["templates"] });
      queryClient.invalidateQueries({ queryKey: ["templates-library"] });
      router.push(`/templates/${detail.id}`);
    },
  });
  return (
    <div className="space-y-4">
      <p className="text-sm text-muted">
        Mẫu do các tổ chức chia sẻ. “Lấy về studio” tạo một bản nháp riêng để bạn tự do chỉnh sửa.
      </p>
      <ErrorBox error={take.error} />
      {lib.isLoading ? <Spinner /> : !lib.data?.length ? (
        <Card><EmptyState icon={<Library className="size-8" />} title="Thư viện chung chưa có mẫu nào"
          description="Khi tổ chức của bạn chia sẻ mẫu, nó sẽ hiện ở đây cho mọi người dùng." /></Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {lib.data.map((t) => (
            <Card key={t.id} className="flex flex-col gap-3 p-5">
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-semibold text-ink">{t.name}</span>
                  {t.badge ? <Badge tone="gold">{t.badge}</Badge> : null}
                </div>
                <div className="mt-1 text-xs text-muted">
                  {t.origin_label || "Không rõ đơn vị"} · {t.sections_count} mục · {t.samples_count} bài mẫu · {t.import_count} lượt lấy về
                </div>
                {t.description ? <p className="mt-2 text-sm text-muted">{t.description}</p> : null}
              </div>
              <div className="mt-auto flex gap-2">
                <Button variant="secondary" onClick={() => setPreview(t)}><Eye className="size-4" /> Xem trước</Button>
                <Button loading={take.isPending} onClick={() => take.mutate(t.key)}>Lấy về studio</Button>
              </div>
            </Card>
          ))}
        </div>
      )}
      {preview && <PreviewModal templateId={preview.id} name={preview.name} onClose={() => setPreview(null)} />}
    </div>
  );
}

function BlockModal({ block, onClose }: { block: TemplateBlock | null; onClose: () => void }) {
  const queryClient = useQueryClient();
  const [name, setName] = useState(block?.name ?? "");
  const [kind, setKind] = useState(block?.kind ?? "core");
  const [body, setBody] = useState(block?.body ?? "");
  const save = useMutation({
    mutationFn: () =>
      block
        ? api.patch<TemplateBlock>(`/templates/blocks/${block.id}`, { name: name.trim(), kind, body })
        : api.post<TemplateBlock>("/templates/blocks", { name: name.trim(), kind, body }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["template-blocks"] });
      onClose();
    },
  });
  return (
    <Modal title={block ? `Sửa khối: ${block.name}` : "Tạo khối nội dung"} onClose={onClose} wide>
      <div className="space-y-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Tên khối" required>
            <Input value={name} onChange={(e) => setName(e.target.value)} maxLength={120} placeholder="VD: Lời chào đầu báo cáo" />
          </Field>
          <Field label="Loại khối">
            <select value={kind} onChange={(e) => setKind(e.target.value)}
              className="block w-full rounded-lg border border-line bg-white px-3 py-2 text-sm">
              {BLOCK_KINDS.map((k) => (
                <option key={k} value={k}>{BLOCK_KIND_LABEL[k] ?? k}</option>
              ))}
            </select>
          </Field>
        </div>
        <Field label="Nội dung" required hint="Hỗ trợ biến {{…}} và điều kiện {{#if …}}…{{/if}}.">
          <Textarea value={body} onChange={(e) => setBody(e.target.value)} rows={10} className="font-mono text-[13px]"
            placeholder={"Xin chào {{subject.name}}!\nHotline hỗ trợ: {{org.hotline}}"} />
        </Field>
        <VariablesHelp />
        <ErrorBox error={save.error} />
        <div className="flex gap-2">
          <Button loading={save.isPending} disabled={!name.trim() || !body.trim()} onClick={() => save.mutate()}>
            {block ? "Lưu" : "Tạo khối"}
          </Button>
          <Button variant="secondary" onClick={onClose}>Hủy</Button>
        </div>
      </div>
    </Modal>
  );
}

function BlocksTab() {
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState<TemplateBlock | null | undefined>(undefined);
  const list = useQuery({
    queryKey: ["template-blocks"],
    queryFn: () => api.get<TemplateBlock[]>("/templates/blocks"),
  });
  const removeBlock = useMutation({
    mutationFn: (id: number) => api.del(`/templates/blocks/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["template-blocks"] }),
  });
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="max-w-2xl text-sm text-muted">
          Khối là đoạn nội dung tái sử dụng trong nhiều mẫu. Sửa khối sẽ đổi mọi mẫu đang dùng nó (báo cáo đã tạo không đổi).
        </p>
        <Button onClick={() => setEditing(null)}><Plus className="size-4" /> Tạo khối</Button>
      </div>
      <ErrorBox error={removeBlock.error} />
      {list.isLoading ? <Spinner /> : !list.data?.length ? (
        <Card><EmptyState icon={<Layers className="size-8" />} title="Chưa có khối nào"
          description="Tạo khối dùng chung như lời chào, chân trang, thông tin liên hệ…"
          action={<Button onClick={() => setEditing(null)}><Plus className="size-4" /> Tạo khối</Button>} /></Card>
      ) : (
        <Card className="divide-y divide-line">
          {list.data.map((b) => (
            <div key={b.id} className="px-4 py-3">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-medium text-ink">{b.name}</span>
                <Badge>{BLOCK_KIND_LABEL[b.kind] ?? b.kind}</Badge>
                <span className="ml-auto flex gap-1">
                  <button type="button" title="Sửa" onClick={() => setEditing(b)}
                    className="rounded-md p-1.5 text-muted hover:bg-brand-50 hover:text-brand-700"><Pencil className="size-4" /></button>
                  <button type="button" title="Xóa" onClick={() => confirm(`Xóa khối “${b.name}”?`) && removeBlock.mutate(b.id)}
                    className="rounded-md p-1.5 text-muted hover:bg-red-50 hover:text-red-700"><Trash2 className="size-4" /></button>
                </span>
              </div>
              <p className="mt-1 line-clamp-2 whitespace-pre-wrap text-sm text-muted">{b.body}</p>
              <div className="mt-1.5 flex flex-wrap gap-1.5 text-xs text-muted">
                {b.variables.map((v) => (
                  <code key={v} className="rounded bg-paper px-1.5 py-0.5">{"{{"}{v}{"}}"}</code>
                ))}
                {b.used_in.length > 0 && <span className="py-0.5">· Dùng trong: {b.used_in.join(", ")}</span>}
              </div>
            </div>
          ))}
        </Card>
      )}
      {editing !== undefined && <BlockModal block={editing} onClose={() => setEditing(undefined)} />}
    </div>
  );
}

function OrgVarsTab() {
  const queryClient = useQueryClient();
  const data = useQuery({ queryKey: ["org-vars"], queryFn: () => api.get<OrgVars>("/templates/org-vars") });
  const [rows, setRows] = useState<{ key: string; label: string; value: string }[] | null>(null);
  const [savedTick, setSavedTick] = useState(0);
  useEffect(() => {
    if (data.data && rows === null) setRows(data.data.vars);
  }, [data.data, rows]);
  const save = useMutation({
    mutationFn: () => api.put<OrgVars>("/templates/org-vars", { vars: rows ?? [] }),
    onSuccess: (d) => {
      setRows(d.vars);
      setSavedTick((t) => t + 1);
      queryClient.invalidateQueries({ queryKey: ["org-vars"] });
    },
  });
  const setRow = (i: number, patch: Partial<{ key: string; label: string; value: string }>) =>
    setRows((rs) => (rs ?? []).map((r, k) => (k === i ? { ...r, ...patch } : r)));
  return (
    <div className="space-y-4">
      <p className="max-w-3xl text-sm text-muted">
        Biến tổ chức dùng trong mọi mẫu qua {"{{org.<key>}}"} — VD: hotline, địa chỉ, tên thương hiệu. Đổi giá trị ở đây sẽ áp dụng cho báo cáo tạo mới.
      </p>
      <ErrorBox error={save.error} />
      {data.isLoading || rows === null ? <Spinner /> : (
        <>
          <Card className="divide-y divide-line">
            {rows.length === 0 && <p className="px-4 py-6 text-sm text-muted">Chưa có biến nào. Thêm biến đầu tiên bên dưới.</p>}
            {rows.map((r, i) => (
              <div key={i} className="grid items-end gap-3 px-4 py-3 sm:grid-cols-[10rem_12rem_minmax(0,1fr)_auto]">
                <Field label={i === 0 ? "Key" : ""}>
                  <Input value={r.key} onChange={(e) => setRow(i, { key: e.target.value })} placeholder="hotline"
                    aria-label={`Key biến ${i + 1}`} className="font-mono text-[13px]" />
                </Field>
                <Field label={i === 0 ? "Nhãn" : ""}>
                  <Input value={r.label} onChange={(e) => setRow(i, { label: e.target.value })} placeholder="Hotline"
                    aria-label={`Nhãn biến ${i + 1}`} />
                </Field>
                <Field label={i === 0 ? "Giá trị" : ""}>
                  <Input value={r.value} onChange={(e) => setRow(i, { value: e.target.value })} placeholder="1900 …"
                    aria-label={`Giá trị biến ${i + 1}`} />
                </Field>
                <button type="button" title="Xóa biến" onClick={() => setRows((rs) => (rs ?? []).filter((_, k) => k !== i))}
                  className="rounded-md p-2 text-muted hover:bg-red-50 hover:text-red-700"><Trash2 className="size-4" /></button>
              </div>
            ))}
          </Card>
          <div className="flex flex-wrap items-center gap-2">
            <Button variant="secondary" onClick={() => setRows((rs) => [...(rs ?? []), { key: "", label: "", value: "" }])}>
              <Plus className="size-4" /> Thêm biến
            </Button>
            <Button loading={save.isPending} onClick={() => save.mutate()}>Lưu biến tổ chức</Button>
            {savedTick > 0 && !save.isPending && !save.error && (
              <span className="text-sm text-emerald-700">Đã lưu.</span>
            )}
          </div>
          <p className="text-xs text-muted">Key viết thường, chữ/số/gạch dưới, bắt đầu bằng chữ (VD: hotline, dia_chi).</p>
        </>
      )}
    </div>
  );
}

export default function TemplatesPage() {
  const me = useMe();
  const [tab, setTab] = useState<Tab>("studio");
  const isAdmin = me.data?.role === "admin";
  const tabs: { id: Tab; label: string; icon: typeof Pencil; admin?: boolean }[] = [
    { id: "studio", label: "Studio", icon: Pencil },
    { id: "library", label: "Thư viện chung", icon: Library },
    { id: "blocks", label: "Khối nội dung", icon: Layers },
    { id: "orgvars", label: "Biến tổ chức", icon: Globe, admin: true },
  ];
  return (
    <>
      <PageHeader title="Mẫu báo cáo"
        description="Soạn mẫu riêng của tổ chức, trình duyệt, chia sẻ ra thư viện chung và dùng lại khối nội dung." />
      <div className="mb-5 flex gap-1 border-b border-line" role="tablist">
        {tabs.filter((t) => !t.admin || isAdmin).map((t) => {
          const Icon = t.icon;
          return (
            <button key={t.id} role="tab" aria-selected={tab === t.id} onClick={() => setTab(t.id)}
              className={cx("-mb-px flex items-center gap-2 border-b-2 px-4 py-2 text-sm font-medium",
                tab === t.id ? "border-brand-500 text-brand-700" : "border-transparent text-muted hover:text-ink")}>
              <Icon className="size-4" /> {t.label}
            </button>
          );
        })}
      </div>
      {tab === "studio" && <StudioTab isAdmin={isAdmin} />}
      {tab === "library" && <LibraryTab />}
      {tab === "blocks" && <BlocksTab />}
      {tab === "orgvars" && isAdmin && <OrgVarsTab />}
    </>
  );
}
