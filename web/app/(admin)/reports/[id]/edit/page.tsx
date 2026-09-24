"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, ArrowLeft, BookOpen, Check, Database, History, RotateCcw, Save, Sparkles, X } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Markdown } from "@/components/Markdown";
import { Badge, Button, Card, ErrorBox, Spinner, cx } from "@/components/ui";
import { api, ApiError } from "@/lib/api";
import { diffLines } from "@/lib/diff";
import { formatTimestamp } from "@/lib/format";
import { useDebounced } from "@/lib/hooks";
import type { EditorData, EditorSection, LlmProposal, Revision, SectionSave } from "@/lib/types";

const AUTOSAVE_MS = 10_000;
const draftKey = (id: string) => `hd-draft:${id}`;

type StoredDraft = { version: number; savedAt: string; sections: Record<string, string> };

const CHANGE_LABEL: Record<string, string> = {
  generate: "Tạo báo cáo",
  manual_edit: "Chỉnh sửa tay",
  regenerate: "Tạo lại",
  llm_edit: "AI biên tập",
};
const changeLabel = (c: string) => (c.startsWith("restore:") ? `Khôi phục từ ${c.slice(8)}` : CHANGE_LABEL[c] ?? c);

function readDraft(id: string): StoredDraft | null {
  try {
    const raw = localStorage.getItem(draftKey(id));
    return raw ? (JSON.parse(raw) as StoredDraft) : null;
  } catch {
    return null;
  }
}

function FactsWarning({ facts }: { facts: string[] }) {
  if (!facts.length) return null;
  return (
    <div className="flex gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900" role="status">
      <AlertTriangle className="mt-0.5 size-4 shrink-0" aria-hidden />
      <div>
        Nội dung đang thiếu sự kiện kỹ thuật mà bản gốc của phần này có:{" "}
        {facts.map((f) => <strong key={f} className="mr-1 font-semibold">“{f}”</strong>)}
        <span className="block text-xs text-amber-800">Bạn vẫn lưu được — nhưng nên giữ lại để người đọc không hiểu sai thiết kế của mình.</span>
      </div>
    </div>
  );
}

function DiffModal({ before, proposal, onAccept, onClose }: {
  before: string; proposal: LlmProposal; onAccept: () => void; onClose: () => void;
}) {
  const lines = useMemo(() => diffLines(before, proposal.draft), [before, proposal.draft]);
  const added = lines.filter((l) => l.kind === "add").length;
  const removed = lines.filter((l) => l.kind === "del").length;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/40 p-4" role="dialog" aria-modal="true" aria-label="Đề xuất của AI">
      <Card className="flex max-h-[90vh] w-full max-w-4xl flex-col">
        <div className="flex items-center justify-between border-b border-line px-5 py-4">
          <div>
            <h2 className="flex items-center gap-2 font-semibold"><Sparkles className="size-4 text-gold-500" /> Đề xuất của AI</h2>
            <p className="text-xs text-muted">+{added} dòng mới · −{removed} dòng bỏ. Chưa có gì được lưu.</p>
          </div>
          <button onClick={onClose} className="rounded-md p-1 text-muted hover:bg-paper" aria-label="Đóng"><X className="size-5" /></button>
        </div>
        <div className="overflow-y-auto px-5 py-4">
          <FactsWarning facts={proposal.missing_facts} />
          <pre className="mt-3 whitespace-pre-wrap break-words rounded-lg border border-line bg-white p-3 font-sans text-sm leading-6">
            {lines.map((l, i) => (
              <div key={i} className={cx("px-2", l.kind === "add" && "bg-emerald-50 text-emerald-900", l.kind === "del" && "bg-red-50 text-red-800 line-through decoration-red-300")}>
                <span className="mr-2 select-none text-muted">{l.kind === "add" ? "+" : l.kind === "del" ? "−" : " "}</span>
                {l.text || " "}
              </div>
            ))}
          </pre>
        </div>
        <div className="flex justify-end gap-2 border-t border-line px-5 py-4">
          <Button variant="secondary" onClick={onClose}>Bỏ đề xuất</Button>
          <Button onClick={onAccept}><Check className="size-4" /> Dùng bản này</Button>
        </div>
      </Card>
    </div>
  );
}

function SourcePanel({ section }: { section: EditorSection }) {
  const json = useMemo(() => JSON.stringify(section.data, null, 2), [section.data]);
  return (
    <div className="space-y-3 text-sm">
      <p className="text-xs text-muted">Dữ liệu đã tính cho phần này — nguồn sự thật, không sửa ở đây.</p>
      {section.knowledge_refs.length > 0 && (
        <div className="flex flex-wrap gap-1">{section.knowledge_refs.map((r) => <Badge key={r} tone="stone">{r}</Badge>)}</div>
      )}
      <pre className="max-h-[60vh] overflow-auto rounded-lg bg-paper p-3 text-xs leading-5 text-ink">{json === "{}" ? "(Phần này không có dữ liệu riêng)" : json}</pre>
    </div>
  );
}

function GlossaryPanel({ data }: { data: EditorData }) {
  const [q, setQ] = useState("");
  const needle = q.trim().toLowerCase();
  return (
    <div className="space-y-3 text-sm">
      <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Tra thuật ngữ…" aria-label="Tra thuật ngữ"
        className="w-full rounded-lg border border-line px-3 py-1.5 text-sm focus:border-brand-500 focus:outline-none" />
      <div className="max-h-[60vh] space-y-4 overflow-y-auto">
        {data.glossary.map((g) => {
          const terms = g.terms.filter((t) => !needle || `${t.source} ${t.term}`.toLowerCase().includes(needle));
          if (!terms.length) return null;
          return (
            <div key={g.title}>
              <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-muted">{g.title}</div>
              <ul className="space-y-1">
                {terms.map((t) => (
                  <li key={t.source} className="rounded-md px-2 py-1 hover:bg-paper">
                    <div className="text-ink">{t.term}</div>
                    <div className="text-xs text-muted">{t.source}</div>
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function HistoryPanel({ reportId, currentVersion, dirty, onRestored }: {
  reportId: string; currentVersion: number; dirty: boolean; onRestored: () => void;
}) {
  const history = useQuery({ queryKey: ["revisions", reportId, currentVersion], queryFn: () => api.get<Revision[]>(`/reports/${reportId}/revisions`) });
  const restore = useMutation({
    mutationFn: (version: number) => api.post(`/reports/${reportId}/revisions/${version}/restore`),
    onSuccess: onRestored,
  });
  if (history.isLoading) return <Spinner />;
  return (
    <div className="space-y-2 text-sm">
      <ErrorBox error={history.error ?? restore.error} />
      <ol className="space-y-1">
        {history.data?.map((r) => (
          <li key={r.version} className="flex items-center justify-between gap-2 rounded-md px-2 py-1.5 hover:bg-paper">
            <div className="min-w-0">
              <div className="font-medium text-ink">v{r.version} · {changeLabel(r.change_type)}</div>
              <div className="truncate text-xs text-muted">{formatTimestamp(r.created_at)} · {r.author}</div>
            </div>
            {r.version === currentVersion ? (
              <Badge>Hiện tại</Badge>
            ) : (
              <Button variant="ghost" className="px-2 py-1 text-xs" loading={restore.isPending && restore.variables === r.version}
                onClick={() => {
                  const warn = dirty ? "\nCác chỉnh sửa chưa lưu sẽ bị bỏ." : "";
                  if (confirm(`Khôi phục nội dung về phiên bản v${r.version}? Hệ thống tạo phiên bản mới, không xóa lịch sử.${warn}`)) restore.mutate(r.version);
                }}>
                <RotateCcw className="size-3.5" /> Khôi phục
              </Button>
            )}
          </li>
        ))}
      </ol>
    </div>
  );
}

export default function EditReportPage() {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const editor = useQuery({ queryKey: ["editor", id], queryFn: () => api.get<EditorData>(`/reports/${id}/editor`), staleTime: Infinity });

  const [server, setServer] = useState<Record<string, EditorSection>>({});
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const [version, setVersion] = useState(0);
  const [selected, setSelected] = useState<string>("");
  const [view, setView] = useState<"write" | "preview">("write");
  const [panel, setPanel] = useState<"source" | "glossary" | "history">("source");
  const [recoverable, setRecoverable] = useState<StoredDraft | null>(null);
  const [proposal, setProposal] = useState<LlmProposal | null>(null);
  const [notice, setNotice] = useState<string>("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const load = useCallback((data: EditorData) => {
    setServer(Object.fromEntries(data.sections.map((s) => [s.id, s])));
    setDrafts(Object.fromEntries(data.sections.map((s) => [s.id, s.content_markdown])));
    setVersion(data.report.version);
    setSelected((cur) => (cur && data.sections.some((s) => s.id === cur) ? cur : data.sections[0]?.id ?? ""));
  }, []);

  useEffect(() => {
    if (!editor.data) return;
    load(editor.data);
    const stored = readDraft(id);
    if (stored && Object.entries(stored.sections).some(([sid, text]) => editor.data.sections.find((s) => s.id === sid)?.content_markdown !== text)) {
      setRecoverable(stored);
    }
  }, [editor.data, id, load]);

  const section = server[selected];
  const text = drafts[selected] ?? "";
  const dirtyIds = useMemo(() => Object.keys(server).filter((sid) => drafts[sid] !== server[sid].content_markdown), [drafts, server]);
  const dirty = dirtyIds.includes(selected);

  // Autosave unsaved edits to this browser every 10 s (server revisions are created by "Lưu phiên bản").
  const latest = useRef({ drafts, server, version, dirtyIds });
  latest.current = { drafts, server, version, dirtyIds };
  useEffect(() => {
    const timer = setInterval(() => {
      const { drafts: d, version: v, dirtyIds: ids } = latest.current;
      if (!ids.length) {
        localStorage.removeItem(draftKey(id));
        return;
      }
      const payload: StoredDraft = { version: v, savedAt: new Date().toISOString(), sections: Object.fromEntries(ids.map((sid) => [sid, d[sid]])) };
      localStorage.setItem(draftKey(id), JSON.stringify(payload));
    }, AUTOSAVE_MS);
    return () => clearInterval(timer);
  }, [id]);

  useEffect(() => {
    const handler = (e: BeforeUnloadEvent) => {
      if (latest.current.dirtyIds.length) e.preventDefault();
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, []);

  // Live, non-blocking facts check.
  const debounced = useDebounced(text, 700);
  const facts = useQuery({
    queryKey: ["facts", id, selected, debounced],
    queryFn: () => api.post<{ missing_facts: string[] }>(`/reports/${id}/sections/${selected}/check`, { content_markdown: debounced }),
    enabled: !!selected && !!section,
    staleTime: Infinity,
  });

  const save = useMutation({
    mutationFn: () => api.put<SectionSave>(`/reports/${id}/sections/${selected}`, { content_markdown: text, base_version: version }),
    onSuccess: (res) => {
      setServer((s) => ({ ...s, [res.section.id]: res.section }));
      setDrafts((d) => ({ ...d, [res.section.id]: res.section.content_markdown }));
      setVersion(res.version);
      setNotice(`Đã lưu phiên bản v${res.version}.`);
      queryClient.invalidateQueries({ queryKey: ["report", id] });
      queryClient.invalidateQueries({ queryKey: ["reports"] });
    },
  });

  const ai = useMutation({
    mutationFn: () => api.post<LlmProposal>(`/reports/${id}/sections/${selected}/llm`),
    onSuccess: setProposal,
  });

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
        e.preventDefault();
        if (dirty && !save.isPending) save.mutate();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [dirty, save]);

  useEffect(() => {
    if (!notice) return;
    const t = setTimeout(() => setNotice(""), 4000);
    return () => clearTimeout(t);
  }, [notice]);

  if (editor.isLoading) return <Spinner label="Đang mở trình biên tập…" />;
  if (!editor.data) {
    return <ErrorBox error={editor.error instanceof ApiError && editor.error.status === 409 ? "Báo cáo đang được tạo — hãy quay lại khi hoàn tất." : editor.error} />;
  }
  const data = editor.data;
  const locked = data.report.status !== "ready";
  const conflict = save.error instanceof ApiError && save.error.status === 409;

  return (
    <div className="-mx-2 sm:-mx-4 lg:-mx-6">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div className="min-w-0">
          <Link href={`/reports/${id}`} className="mb-1 inline-flex items-center gap-1 text-sm text-brand-700 hover:underline"><ArrowLeft className="size-4" /> Về báo cáo</Link>
          <h1 className="truncate text-xl font-bold text-ink">Biên tập · {data.report.client_name}</h1>
          <p className="text-xs text-muted">Sinh {data.subject_display} · Phiên bản hiện tại v{version}{dirtyIds.length ? ` · ${dirtyIds.length} phần chưa lưu` : ""}</p>
        </div>
        {notice && <span className="rounded-full bg-emerald-50 px-3 py-1 text-sm text-emerald-800 ring-1 ring-emerald-200">{notice}</span>}
      </div>

      {locked && <ErrorBox error="Báo cáo đã lưu trữ hoặc chưa sẵn sàng — chỉ xem, không chỉnh sửa được." className="mb-4" />}
      {recoverable && (
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3 rounded-lg border border-brand-100 bg-brand-50 px-4 py-3 text-sm">
          <span>Có bản nháp chưa lưu trong trình duyệt này ({formatTimestamp(recoverable.savedAt)}, {Object.keys(recoverable.sections).length} phần).</span>
          <span className="flex gap-2">
            <Button variant="secondary" className="px-3 py-1" onClick={() => { localStorage.removeItem(draftKey(id)); setRecoverable(null); }}>Bỏ bản nháp</Button>
            <Button className="px-3 py-1" onClick={() => { setDrafts((d) => ({ ...d, ...recoverable.sections })); setRecoverable(null); }}>Khôi phục bản nháp</Button>
          </span>
        </div>
      )}

      <div className="grid items-start gap-4 lg:grid-cols-[12rem_minmax(0,1fr)] xl:grid-cols-[12rem_minmax(0,1fr)_18rem]">
        <nav aria-label="Các phần của báo cáo" className="lg:sticky lg:top-6">
          <ol className="space-y-1">
            {data.sections.map((s) => {
              const isDirty = dirtyIds.includes(s.id);
              const hasWarn = (server[s.id]?.warnings.length ?? 0) > 0;
              return (
                <li key={s.id}>
                  <button onClick={() => setSelected(s.id)} aria-current={selected === s.id}
                    className={cx("flex w-full items-start gap-2 rounded-lg px-3 py-2 text-left text-sm leading-snug",
                      selected === s.id ? "bg-brand-50 font-medium text-brand-700" : "text-ink hover:bg-white")}>
                    <span className="flex-1">{s.title}</span>
                    {isDirty && <span className="mt-1.5 size-2 shrink-0 rounded-full bg-brand-500" title="Chưa lưu" />}
                    {!isDirty && hasWarn && <AlertTriangle className="mt-0.5 size-3.5 shrink-0 text-amber-600" aria-label="Có cảnh báo" />}
                  </button>
                </li>
              );
            })}
          </ol>
        </nav>

        {section && (
          <Card className="flex min-h-[70vh] flex-col">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line px-4 py-3">
              <div className="flex gap-1 rounded-lg bg-paper p-1" role="tablist">
                {(["write", "preview"] as const).map((v) => (
                  <button key={v} role="tab" aria-selected={view === v} onClick={() => setView(v)}
                    className={cx("rounded-md px-3 py-1 text-xs font-medium", view === v ? "bg-white text-ink shadow-sm" : "text-muted")}>
                    {v === "write" ? "Soạn thảo" : "Xem trước"}
                  </button>
                ))}
              </div>
              <div className="flex flex-wrap gap-2">
                <Button variant="secondary" className="px-3 py-1.5" disabled={locked || !data.llm_available} loading={ai.isPending}
                  title={data.llm_available ? "AI viết lại riêng phần này; bạn xem so sánh trước khi dùng" : "Chưa bật AI — quản trị viên cấu hình ở Cài đặt → AI / LLM"}
                  onClick={() => ai.mutate()}>
                  <Sparkles className="size-4" /> {ai.isPending ? "AI đang viết…" : "AI biên tập phần này"}
                </Button>
                {dirty && (
                  <Button variant="ghost" className="px-3 py-1.5" onClick={() => setDrafts((d) => ({ ...d, [selected]: section.content_markdown }))}>
                    Hoàn tác
                  </Button>
                )}
                <Button className="px-3 py-1.5" disabled={locked || !dirty} loading={save.isPending} onClick={() => save.mutate()} title="Ctrl/⌘ + S">
                  <Save className="size-4" /> Lưu phiên bản
                </Button>
              </div>
            </div>
            <div className="border-b border-line px-4 py-2 text-sm font-semibold text-ink">{section.title}</div>
            <div className="flex-1 p-4">
              {view === "write" ? (
                <textarea ref={textareaRef} value={text} disabled={locked} spellCheck={false}
                  onChange={(e) => setDrafts((d) => ({ ...d, [selected]: e.target.value }))}
                  aria-label={`Nội dung phần ${section.title}`}
                  className="h-full min-h-[55vh] w-full resize-y rounded-lg border border-line bg-white p-3 font-mono text-[13px] leading-6 text-ink focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100" />
              ) : (
                <div className="min-h-[55vh] rounded-lg border border-line bg-white p-5"><Markdown>{text}</Markdown></div>
              )}
            </div>
            <div className="space-y-2 border-t border-line px-4 py-3">
              <FactsWarning facts={facts.data?.missing_facts ?? []} />
              {conflict ? (
                <ErrorBox error={save.error} />
              ) : (
                <ErrorBox error={save.error ?? ai.error} />
              )}
              <p className="text-xs text-muted">
                Markdown: <code>## Tiêu đề</code>, <code>**đậm**</code>, <code>*nghiêng*</code>, <code>- gạch đầu dòng</code>, <code>&gt; trích dẫn</code>.
                Bản nháp tự lưu trong trình duyệt mỗi 10 giây; “Lưu phiên bản” tạo một phiên bản trên máy chủ (PDF/Word cập nhật theo).
              </p>
            </div>
          </Card>
        )}

        {section && (
          <Card className="hidden p-4 xl:sticky xl:top-6 xl:block">
            <div className="mb-3 flex gap-1 rounded-lg bg-paper p-1 text-xs" role="tablist">
              {([["source", "Dữ liệu", Database], ["glossary", "Thuật ngữ", BookOpen], ["history", "Lịch sử", History]] as const).map(([key, label, Icon]) => (
                <button key={key} role="tab" aria-selected={panel === key} onClick={() => setPanel(key)}
                  className={cx("flex flex-1 items-center justify-center gap-1 rounded-md px-2 py-1 font-medium", panel === key ? "bg-white text-ink shadow-sm" : "text-muted")}>
                  <Icon className="size-3.5" aria-hidden /> {label}
                </button>
              ))}
            </div>
            {panel === "source" && <SourcePanel section={section} />}
            {panel === "glossary" && <GlossaryPanel data={data} />}
            {panel === "history" && (
              <HistoryPanel reportId={id} currentVersion={version} dirty={dirtyIds.length > 0}
                onRestored={async () => {
                  localStorage.removeItem(draftKey(id));
                  const fresh = await queryClient.fetchQuery({ queryKey: ["editor", id], queryFn: () => api.get<EditorData>(`/reports/${id}/editor`), staleTime: 0 });
                  load(fresh);
                  setNotice("Đã khôi phục — tạo phiên bản mới.");
                  queryClient.invalidateQueries({ queryKey: ["report", id] });
                }} />
            )}
          </Card>
        )}
      </div>

      {proposal && section && (
        <DiffModal before={text} proposal={proposal} onClose={() => setProposal(null)}
          onAccept={() => {
            setDrafts((d) => ({ ...d, [selected]: proposal.draft }));
            setProposal(null);
            setView("write");
            setNotice("Đã đưa bản AI vào trình soạn thảo — bấm “Lưu phiên bản” để lưu.");
          }} />
      )}
    </div>
  );
}
