"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import {
  Badge,
  Button,
  Card,
  ErrorBox,
  Field,
  Input,
  Modal,
  PageHeader,
  Spinner,
} from "@/components/ui";
import { api, qs } from "@/lib/api";
import { BANKS } from "@/lib/game/bank";
import { STYLES, THEMES } from "@/lib/game/content";

interface Concept {
  slug: string;
  name: string;
  entry_label: string;
  entry_desc: string;
  icon: string;
  intro: string;
  bridge: string;
  enabled: boolean;
  is_builtin: boolean;
  sort_order: number;
  custom_total: number;
  custom_enabled: number;
  disabled_builtin: number;
}

interface CustomOption {
  t: string;
  s: string;
}

interface CustomQ {
  id: number;
  concept_slug: string;
  qid: string;
  title: string;
  sit: string;
  options: CustomOption[];
  enabled: boolean;
  created_at: string;
}

interface QuestionsOut {
  custom: CustomQ[];
  disabled_builtin: string[];
}

const STYLE_OPTIONS = Object.values(STYLES).map((s) => ({
  value: s.id,
  label: `${s.icon} ${s.name}`,
}));

function conceptMeta(c: Concept): { name: string; icon: string } {
  const base = THEMES[c.slug];
  return { name: c.name || base?.name || c.slug, icon: c.icon || base?.icon || "🎮" };
}

function Toggle({
  on,
  onChange,
  disabled,
  label,
}: {
  on: boolean;
  onChange: (v: boolean) => void;
  disabled?: boolean;
  label: string;
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={on}
      aria-label={label}
      disabled={disabled}
      onClick={() => onChange(!on)}
      className={`relative h-6 w-11 shrink-0 rounded-full transition-colors ${
        on ? "bg-green-500" : "bg-stone-300"
      } ${disabled ? "opacity-50" : ""}`}
    >
      <span
        className={`absolute top-0.5 size-5 rounded-full bg-white shadow transition-all ${
          on ? "left-[22px]" : "left-0.5"
        }`}
      />
    </button>
  );
}

function SortCell({
  value,
  onSave,
  disabled,
}: {
  value: number;
  onSave: (v: number) => void;
  disabled?: boolean;
}) {
  const [v, setV] = useState(String(value));
  return (
    <div className="flex items-center gap-1">
      <input
        value={v}
        onChange={(e) => setV(e.target.value)}
        inputMode="numeric"
        aria-label="Thứ tự"
        className="w-16 rounded-lg border border-line bg-white px-2 py-1 text-xs"
      />
      {v !== String(value) && (
        <button
          type="button"
          disabled={disabled}
          onClick={() => onSave(Number(v) || 0)}
          className="rounded-lg bg-brand-600 px-2 py-1 text-xs font-bold text-white hover:bg-brand-700"
        >
          Lưu
        </button>
      )}
    </div>
  );
}

const EMPTY_CONCEPT = {
  slug: "",
  name: "",
  entry_label: "",
  entry_desc: "",
  icon: "🎮",
  intro: "",
  bridge: "",
};

function ConceptModal({
  concept,
  onClose,
  onSubmit,
  pending,
  error,
}: {
  concept: Concept | null;
  onClose: () => void;
  onSubmit: (data: typeof EMPTY_CONCEPT) => void;
  pending: boolean;
  error: unknown;
}) {
  const [form, setForm] = useState(
    concept
      ? {
          slug: concept.slug,
          name: concept.name,
          entry_label: concept.entry_label,
          entry_desc: concept.entry_desc,
          icon: concept.icon,
          intro: concept.intro,
          bridge: concept.bridge,
        }
      : EMPTY_CONCEPT,
  );
  const set = (k: keyof typeof form) => (e: { target: { value: string } }) =>
    setForm({ ...form, [k]: e.target.value });
  return (
    <Modal title={concept ? `Sửa concept “${concept.slug}”` : "Thêm concept mới"} onClose={onClose}>
      <form
        className="space-y-3"
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit(form);
        }}
      >
        {!concept && (
          <Field label="Slug (duy nhất, chữ thường + số + gạch ngang)" required htmlFor="c-slug">
            <Input
              id="c-slug"
              required
              value={form.slug}
              onChange={set("slug")}
              placeholder="vd: tuoi-tho"
            />
          </Field>
        )}
        <Field label="Tên concept" required htmlFor="c-name">
          <Input id="c-name" required value={form.name} onChange={set("name")} />
        </Field>
        <div className="grid gap-3 sm:grid-cols-2">
          <Field label="Nhãn nút chơi" required htmlFor="c-label">
            <Input id="c-label" required value={form.entry_label} onChange={set("entry_label")} />
          </Field>
          <Field label="Icon (emoji)" htmlFor="c-icon">
            <Input id="c-icon" value={form.icon} onChange={set("icon")} />
          </Field>
        </div>
        <Field label="Mô tả ngắn" required htmlFor="c-desc">
          <Input id="c-desc" required value={form.entry_desc} onChange={set("entry_desc")} />
        </Field>
        <Field label="Intro (màn hình bắt đầu)" required htmlFor="c-intro">
          <textarea
            id="c-intro"
            required
            rows={2}
            value={form.intro}
            onChange={set("intro")}
            className="w-full rounded-lg border border-line bg-white px-3 py-2 text-sm"
          />
        </Field>
        <Field label="Bridge (lời dẫn sang đối chiếu)" required htmlFor="c-bridge">
          <textarea
            id="c-bridge"
            required
            rows={2}
            value={form.bridge}
            onChange={set("bridge")}
            className="w-full rounded-lg border border-line bg-white px-3 py-2 text-sm"
          />
        </Field>
        <ErrorBox error={error} />
        <div className="flex gap-2">
          <Button type="submit" loading={pending}>
            {concept ? "Lưu" : "Thêm concept"}
          </Button>
          <Button type="button" variant="secondary" onClick={onClose}>
            Hủy
          </Button>
        </div>
      </form>
    </Modal>
  );
}

const EMPTY_Q = { title: "", sit: "", options: [] as CustomOption[] };

function QuestionModal({
  initial,
  onClose,
  onSubmit,
  pending,
  error,
}: {
  initial: CustomQ | null;
  onClose: () => void;
  onSubmit: (data: { title: string; sit: string; options: CustomOption[] }) => void;
  pending: boolean;
  error: unknown;
}) {
  const [title, setTitle] = useState(initial?.title ?? "");
  const [sit, setSit] = useState(initial?.sit ?? "");
  const [options, setOptions] = useState<CustomOption[]>(
    initial?.options ?? STYLE_OPTIONS.map((s) => ({ t: "", s: s.value })),
  );
  return (
    <Modal title={initial ? `Sửa câu ${initial.qid}` : "Thêm câu hỏi"} onClose={onClose}>
      <form
        className="space-y-3"
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit({ title, sit, options });
        }}
      >
        <Field label="Tiêu đề" required htmlFor="q-title">
          <Input id="q-title" required value={title} onChange={(e) => setTitle(e.target.value)} />
        </Field>
        <Field label="Tình huống" required htmlFor="q-sit">
          <textarea
            id="q-sit"
            required
            rows={3}
            value={sit}
            onChange={(e) => setSit(e.target.value)}
            className="w-full rounded-lg border border-line bg-white px-3 py-2 text-sm"
          />
        </Field>
        {options.map((o, i) => (
          <div key={i} className="flex gap-2">
            <Input
              required
              value={o.t}
              aria-label={`Đáp án ${i + 1}`}
              placeholder={`Đáp án ${i + 1}`}
              onChange={(e) => {
                const next = [...options];
                next[i] = { ...o, t: e.target.value };
                setOptions(next);
              }}
            />
            <select
              value={o.s}
              aria-label={`Phong cách đáp án ${i + 1}`}
              onChange={(e) => {
                const next = [...options];
                next[i] = { ...o, s: e.target.value };
                setOptions(next);
              }}
              className="shrink-0 rounded-lg border border-line bg-white px-2 py-1 text-xs"
            >
              {STYLE_OPTIONS.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>
        ))}
        <ErrorBox error={error} />
        <div className="flex gap-2">
          <Button type="submit" loading={pending}>
            {initial ? "Lưu" : "Thêm câu hỏi"}
          </Button>
          <Button type="button" variant="secondary" onClick={onClose}>
            Hủy
          </Button>
        </div>
      </form>
    </Modal>
  );
}

function ImportModal({
  slug,
  onClose,
  onDone,
}: {
  slug: string;
  onClose: () => void;
  onDone: () => void;
}) {
  const [text, setText] = useState("");
  const [result, setResult] = useState("");
  const [busy, setBusy] = useState(false);
  const run = async () => {
    setBusy(true);
    setResult("");
    try {
      const items = JSON.parse(text) as unknown;
      if (!Array.isArray(items) || items.length === 0) throw new Error("JSON phải là mảng câu hỏi.");
      let ok = 0;
      for (let i = 0; i < items.length; i++) {
        const it = items[i] as { title?: string; sit?: string; options?: CustomOption[] };
        await api.post<CustomQ>("/game/questions", {
          concept_slug: slug,
          title: it.title ?? "",
          sit: it.sit ?? "",
          options: it.options ?? [],
        });
        ok++;
      }
      setResult(`Đã nhập ${ok}/${items.length} câu.`);
      onDone();
    } catch (e) {
      setResult(e instanceof Error ? `Lỗi: ${e.message}` : "Lỗi không rõ.");
    } finally {
      setBusy(false);
    }
  };
  return (
    <Modal title={`Nhập câu hỏi cho “${slug}”`} onClose={onClose}>
      <p className="mb-2 text-xs text-muted">
        Dán mảng JSON: mỗi phần tử gồm title, sit và options (4 đáp án, mỗi đáp án có t = nội dung,
        s = 1 trong khoi_xuong, kien_tao, dan_duong, tam_guong).
      </p>
      <textarea
        rows={10}
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder='[{"title": "...", "sit": "...", "options": [{"t": "...", "s": "khoi_xuong"}, ...]}]'
        className="w-full rounded-lg border border-line bg-white px-3 py-2 font-mono text-xs"
      />
      {result && <p className="mt-2 text-sm font-medium">{result}</p>}
      <div className="mt-3 flex gap-2">
        <Button onClick={run} loading={busy}>
          Nhập
        </Button>
        <Button variant="secondary" onClick={onClose}>
          Đóng
        </Button>
      </div>
    </Modal>
  );
}

export default function GameManagerPage() {
  const queryClient = useQueryClient();
  const [slug, setSlug] = useState("");
  const [search, setSearch] = useState("");
  const [conceptModal, setConceptModal] = useState<null | { concept: Concept | null }>(null);
  const [questionModal, setQuestionModal] = useState<null | { question: CustomQ | null }>(null);
  const [importOpen, setImportOpen] = useState(false);

  const concepts = useQuery({
    queryKey: ["game-concepts"],
    queryFn: () => api.get<Concept[]>("/game/concepts"),
  });
  useEffect(() => {
    if (!slug && concepts.data && concepts.data.length > 0) setSlug(concepts.data[0].slug);
  }, [concepts.data, slug]);

  const questions = useQuery({
    queryKey: ["game-questions", slug],
    queryFn: () => api.get<QuestionsOut>(`/game/questions${qs({ concept_slug: slug })}`),
    enabled: !!slug,
  });
  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["game-concepts"] });
    queryClient.invalidateQueries({ queryKey: ["game-questions", slug] });
  };

  const patchConcept = useMutation({
    mutationFn: ({ slug: s, body }: { slug: string; body: Record<string, unknown> }) =>
      api.patch<Concept>(`/game/concepts/${s}`, body),
    onSuccess: () => {
      invalidate();
      setConceptModal(null);
    },
  });
  const createConcept = useMutation({
    mutationFn: (body: Record<string, unknown>) => api.post<Concept>("/game/concepts", body),
    onSuccess: () => {
      invalidate();
      setConceptModal(null);
    },
  });
  const deleteConcept = useMutation({
    mutationFn: (s: string) => api.del(`/game/concepts/${s}`),
    onSuccess: (_, s) => {
      if (slug === s) setSlug("");
      invalidate();
    },
  });
  const saveQuestion = useMutation({
    mutationFn: (args: { id?: number; body: Record<string, unknown> }) =>
      args.id
        ? api.patch<CustomQ>(`/game/questions/${args.id}`, args.body)
        : api.post<CustomQ>("/game/questions", args.body),
    onSuccess: () => {
      invalidate();
      setQuestionModal(null);
    },
  });
  const deleteQuestion = useMutation({
    mutationFn: (id: number) => api.del(`/game/questions/${id}`),
    onSuccess: invalidate,
  });
  const toggleDisabled = useMutation({
    mutationFn: ({ qid, off }: { qid: string; off: boolean }) =>
      off
        ? api.post("/game/questions/disabled", { concept_slug: slug, qid })
        : api.del(`/game/questions/disabled${qs({ concept_slug: slug, qid })}`),
    onSuccess: invalidate,
  });

  const stats = useMemo(() => {
    const list = concepts.data ?? [];
    const customTotal = list.reduce((a, c) => a + c.custom_total, 0);
    const customOn = list.reduce((a, c) => a + c.custom_enabled, 0);
    const hidden = list.reduce((a, c) => a + c.disabled_builtin, 0);
    const runtime = list.reduce(
      (a, c) => a + (BANKS[c.slug]?.length ?? 0) - c.disabled_builtin + c.custom_enabled,
      0,
    );
    return {
      enabled: list.filter((c) => c.enabled).length,
      total: list.length,
      customTotal,
      customOn,
      hidden,
      runtime,
    };
  }, [concepts.data]);

  const builtin = useMemo(() => {
    const bank = BANKS[slug] ?? [];
    const q = search.trim().toLowerCase();
    if (!q) return bank;
    return bank.filter(
      (b) =>
        b.id.toLowerCase().includes(q) ||
        b.title.toLowerCase().includes(q) ||
        b.sit.toLowerCase().includes(q),
    );
  }, [slug, search]);
  const custom = useMemo(() => {
    const list = questions.data?.custom ?? [];
    const q = search.trim().toLowerCase();
    if (!q) return list;
    return list.filter(
      (c) =>
        c.qid.toLowerCase().includes(q) ||
        c.title.toLowerCase().includes(q) ||
        c.sit.toLowerCase().includes(q),
    );
  }, [questions.data, search]);
  const disabledSet = useMemo(
    () => new Set(questions.data?.disabled_builtin ?? []),
    [questions.data],
  );

  const exportJson = () => {
    const blob = new Blob([JSON.stringify(questions.data?.custom ?? [], null, 2)], {
      type: "application/json",
    });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `game-${slug}-custom.json`;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  return (
    <>
      <PageHeader
        title="Game Manager"
        description="Bật/tắt concept, thêm concept mới và quản trị kho câu hỏi của game “Đúng Thiết Kế”. Thay đổi có hiệu lực ngay với người chơi."
      />
      <ErrorBox
        error={
          concepts.error ??
          questions.error ??
          patchConcept.error ??
          createConcept.error ??
          deleteConcept.error ??
          saveQuestion.error ??
          deleteQuestion.error ??
          toggleDisabled.error
        }
        className="mb-4"
      />

      <div className="mb-4 grid grid-cols-2 gap-3 lg:grid-cols-4">
        {[
          { n: `${stats.enabled}/${stats.total}`, l: "concept đang bật" },
          { n: String(stats.runtime), l: "câu hỏi đang live" },
          { n: `${stats.customOn}/${stats.customTotal}`, l: "câu custom đang bật" },
          { n: String(stats.hidden), l: "câu built-in bị ẩn" },
        ].map((s) => (
          <Card key={s.l} className="p-4 text-center">
            <div className="text-2xl font-black text-ink">{s.n}</div>
            <div className="mt-1 text-xs text-muted">{s.l}</div>
          </Card>
        ))}
      </div>

      <div className="mb-2 flex items-center justify-between">
        <h2 className="text-base font-bold text-ink">Concept</h2>
        <Button onClick={() => setConceptModal({ concept: null })}>+ Thêm concept</Button>
      </div>
      {concepts.isLoading ? (
        <Spinner />
      ) : (
        <Card className="mb-6 overflow-x-auto">
          <table className="w-full min-w-[820px] text-left text-sm">
            <thead>
              <tr className="border-b border-line text-xs uppercase tracking-wider text-muted">
                <th className="px-4 py-3">Concept</th>
                <th className="px-4 py-3">Bật</th>
                <th className="px-4 py-3">Thứ tự</th>
                <th className="px-4 py-3">Kho câu hỏi</th>
                <th className="px-4 py-3">Thao tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {(concepts.data ?? []).map((c) => {
                const meta = conceptMeta(c);
                const builtinCount = BANKS[c.slug]?.length ?? 0;
                return (
                  <tr key={c.slug} className={slug === c.slug ? "bg-brand-50/50" : undefined}>
                    <td className="px-4 py-3">
                      <span className="mr-2 text-xl">{meta.icon}</span>
                      <span className="font-medium text-ink">{meta.name}</span>{" "}
                      <span className="text-xs text-muted">/{c.slug}</span>{" "}
                      <Badge tone={c.is_builtin ? "stone" : "brand"}>
                        {c.is_builtin ? "Có sẵn" : "Tự thêm"}
                      </Badge>
                    </td>
                    <td className="px-4 py-3">
                      <Toggle
                        on={c.enabled}
                        label={`Bật/tắt ${c.slug}`}
                        disabled={patchConcept.isPending}
                        onChange={(v) => patchConcept.mutate({ slug: c.slug, body: { enabled: v } })}
                      />
                    </td>
                    <td className="px-4 py-3">
                      <SortCell
                        key={`${c.slug}-${c.sort_order}`}
                        value={c.sort_order}
                        disabled={patchConcept.isPending}
                        onSave={(v) => patchConcept.mutate({ slug: c.slug, body: { sort_order: v } })}
                      />
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-muted">
                      {builtinCount - c.disabled_builtin}/{builtinCount} có sẵn ·{" "}
                      {c.custom_enabled}/{c.custom_total} custom
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-2">
                        <Button
                          variant="secondary"
                          className="px-3 py-1.5 text-xs"
                          onClick={() => setSlug(c.slug)}
                        >
                          Câu hỏi
                        </Button>
                        <a
                          href={`/${c.slug}?preview=1`}
                          target="_blank"
                          rel="noreferrer"
                          className="rounded-lg border border-line px-3 py-1.5 text-xs font-medium hover:bg-paper"
                        >
                          Xem trước
                        </a>
                        {!c.is_builtin && (
                          <>
                            <Button
                              variant="secondary"
                              className="px-3 py-1.5 text-xs"
                              onClick={() => setConceptModal({ concept: c })}
                            >
                              Sửa
                            </Button>
                            <Button
                              variant="secondary"
                              className="px-3 py-1.5 text-xs text-red-700"
                              loading={deleteConcept.isPending}
                              onClick={() => {
                                if (
                                  window.confirm(
                                    `Xóa concept “${c.slug}” và toàn bộ câu custom của nó?`,
                                  )
                                )
                                  deleteConcept.mutate(c.slug);
                              }}
                            >
                              Xóa
                            </Button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </Card>
      )}

      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-base font-bold text-ink">
          Kho câu hỏi{slug ? ` — /${slug}` : ""}
        </h2>
        <div className="flex flex-wrap gap-2">
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Tìm theo mã, tiêu đề…"
            aria-label="Tìm câu hỏi"
            className="w-56"
          />
          <select
            value={slug}
            onChange={(e) => setSlug(e.target.value)}
            aria-label="Chọn concept"
            className="rounded-lg border border-line bg-white px-2 py-1.5 text-sm"
          >
            {(concepts.data ?? []).map((c) => (
              <option key={c.slug} value={c.slug}>
                /{c.slug}
              </option>
            ))}
          </select>
        </div>
      </div>
      {questions.isLoading ? (
        <Spinner />
      ) : (
        <>
          <Card className="mb-4 p-4">
            <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
              <div className="text-sm font-bold text-ink">
                Câu tự thêm ({custom.length}
                {search ? `/${questions.data?.custom.length ?? 0}` : ""})
              </div>
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  className="px-3 py-1.5 text-xs"
                  onClick={() => setQuestionModal({ question: null })}
                >
                  + Thêm câu hỏi
                </Button>
                <Button
                  variant="secondary"
                  className="px-3 py-1.5 text-xs"
                  onClick={() => setImportOpen(true)}
                >
                  Nhập JSON
                </Button>
                <Button
                  variant="secondary"
                  className="px-3 py-1.5 text-xs"
                  onClick={exportJson}
                >
                  Xuất JSON
                </Button>
              </div>
            </div>
            {custom.length === 0 ? (
              <p className="py-4 text-center text-sm text-muted">
                {search ? "Không khớp từ khóa." : "Chưa có câu tự thêm."}
              </p>
            ) : (
              <ul className="divide-y divide-line">
                {custom.map((q) => (
                  <li key={q.id} className="flex items-start gap-3 py-3">
                    <div className="min-w-0 flex-1">
                      <div className="text-sm font-medium text-ink">
                        <span className="mr-2 font-mono text-xs text-muted">{q.qid}</span>
                        {q.title}{" "}
                        {!q.enabled && <Badge tone="stone">Đang tắt</Badge>}
                      </div>
                      <p className="mt-0.5 line-clamp-2 text-xs text-muted">{q.sit}</p>
                      <details className="mt-1 text-xs">
                        <summary className="cursor-pointer text-muted">Xem 4 đáp án</summary>
                        <ul className="mt-1 list-disc space-y-0.5 pl-5 text-ink">
                          {q.options.map((o, i) => (
                            <li key={i}>
                              {o.t}{" "}
                              <span className="text-muted">
                                ({STYLE_OPTIONS.find((s) => s.value === o.s)?.label ?? o.s})
                              </span>
                            </li>
                          ))}
                        </ul>
                      </details>
                    </div>
                    <div className="flex shrink-0 gap-2">
                      <Toggle
                        on={q.enabled}
                        label={`Bật/tắt ${q.qid}`}
                        disabled={saveQuestion.isPending}
                        onChange={(v) =>
                          saveQuestion.mutate({ id: q.id, body: { enabled: v } })
                        }
                      />
                      <Button
                        variant="secondary"
                        className="px-3 py-1.5 text-xs"
                        onClick={() => setQuestionModal({ question: q })}
                      >
                        Sửa
                      </Button>
                      <Button
                        variant="secondary"
                        className="px-3 py-1.5 text-xs text-red-700"
                        loading={deleteQuestion.isPending}
                        onClick={() => {
                          if (window.confirm(`Xóa câu ${q.qid}?`)) deleteQuestion.mutate(q.id);
                        }}
                      >
                        Xóa
                      </Button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </Card>

          <Card className="p-4">
            <div className="mb-3 text-sm font-bold text-ink">
              Câu có sẵn ({builtin.length}
              {search ? `/${BANKS[slug]?.length ?? 0}` : ""}) — chỉ ẩn/hiện, không sửa
            </div>
            {builtin.length === 0 ? (
              <p className="py-4 text-center text-sm text-muted">
                {search ? "Không khớp từ khóa." : "Concept này không có câu có sẵn."}
              </p>
            ) : (
              <ul className="divide-y divide-line">
                {builtin.map((b) => {
                  const off = disabledSet.has(b.id);
                  return (
                    <li key={b.id} className="flex items-start gap-3 py-2.5">
                      <div className="min-w-0 flex-1">
                        <div className="text-sm text-ink">
                          <span className="mr-2 font-mono text-xs text-muted">{b.id}</span>
                          {b.title} {off && <Badge tone="stone">Đang ẩn</Badge>}
                        </div>
                        <p className="mt-0.5 line-clamp-1 text-xs text-muted">{b.sit}</p>
                      </div>
                      <Button
                        variant="secondary"
                        className="shrink-0 px-3 py-1.5 text-xs"
                        loading={toggleDisabled.isPending}
                        onClick={() => toggleDisabled.mutate({ qid: b.id, off: !off })}
                      >
                        {off ? "Hiện" : "Ẩn"}
                      </Button>
                    </li>
                  );
                })}
              </ul>
            )}
          </Card>
        </>
      )}

      {conceptModal && (
        <ConceptModal
          key={conceptModal.concept?.slug ?? "new"}
          concept={conceptModal.concept}
          onClose={() => setConceptModal(null)}
          pending={createConcept.isPending || patchConcept.isPending}
          error={createConcept.error ?? patchConcept.error}
          onSubmit={(data) => {
            if (conceptModal.concept) {
              const { slug: _s, ...body } = data;
              patchConcept.mutate({ slug: conceptModal.concept.slug, body });
            } else {
              createConcept.mutate(data);
            }
          }}
        />
      )}
      {questionModal && (
        <QuestionModal
          key={questionModal.question?.id ?? "new"}
          initial={questionModal.question}
          onClose={() => setQuestionModal(null)}
          pending={saveQuestion.isPending}
          error={saveQuestion.error}
          onSubmit={(data) => {
            if (questionModal.question) {
              saveQuestion.mutate({ id: questionModal.question.id, body: data });
            } else {
              saveQuestion.mutate({ body: { ...data, concept_slug: slug, enabled: true } });
            }
          }}
        />
      )}
      {importOpen && (
        <ImportModal slug={slug} onClose={() => setImportOpen(false)} onDone={invalidate} />
      )}
    </>
  );
}
