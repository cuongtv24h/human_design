"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import {
  Badge,
  Button,
  Card,
  ErrorBox,
  Field,
  Input,
  Modal,
  Spinner,
} from "@/components/ui";
import { api, qs } from "@/lib/api";
import { BANKS } from "@/lib/game/bank";

interface NodeOut {
  id: number;
  chapter_id: number;
  idx: number;
  mode: string;
  question_count: number;
  time_limit: number;
  question_ids: string[];
  auto: boolean;
}

interface ChapterOut {
  id: number;
  concept_slug: string;
  idx: number;
  name: string;
  icon: string;
  desc: string;
  nodes: NodeOut[];
}

interface BankItem {
  qid: string;
  title: string;
  custom: boolean;
  off: boolean;
}

const MODES = [
  { value: "normal", label: "🗺️ Màn thường" },
  { value: "speed", label: "⚡ Tốc độ" },
  { value: "boss", label: "👹 Trùm" },
];

const MODE_LABEL: Record<string, string> = {
  normal: "🗺️ Thường",
  speed: "⚡ Tốc độ",
  boss: "👹 Trùm",
};

function ChapterModal({
  initial,
  onClose,
  onSubmit,
  pending,
  error,
}: {
  initial: ChapterOut | null;
  onClose: () => void;
  onSubmit: (data: { name: string; icon: string; desc: string }) => void;
  pending: boolean;
  error: unknown;
}) {
  const [name, setName] = useState(initial?.name ?? "");
  const [icon, setIcon] = useState(initial?.icon ?? "🗺️");
  const [desc, setDesc] = useState(initial?.desc ?? "");
  return (
    <Modal title={initial ? "Sửa chương" : "Thêm chương"} onClose={onClose}>
      <form
        className="space-y-3"
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit({ name, icon, desc });
        }}
      >
        <Field label="Tên chương" required htmlFor="ch-name">
          <Input id="ch-name" required value={name} onChange={(e) => setName(e.target.value)} />
        </Field>
        <Field label="Icon (emoji)" htmlFor="ch-icon">
          <Input id="ch-icon" value={icon} onChange={(e) => setIcon(e.target.value)} />
        </Field>
        <Field label="Mô tả" htmlFor="ch-desc">
          <Input id="ch-desc" value={desc} onChange={(e) => setDesc(e.target.value)} />
        </Field>
        <ErrorBox error={error} />
        <div className="flex gap-2">
          <Button type="submit" loading={pending}>
            {initial ? "Lưu" : "Thêm chương"}
          </Button>
          <Button type="button" variant="secondary" onClick={onClose}>
            Hủy
          </Button>
        </div>
      </form>
    </Modal>
  );
}

function NodeModal({
  node,
  onClose,
  onSubmit,
  pending,
  error,
}: {
  node: NodeOut | null;
  onClose: () => void;
  onSubmit: (data: { mode: string; question_count: number; time_limit: number }) => void;
  pending: boolean;
  error: unknown;
}) {
  const [mode, setMode] = useState(node?.mode ?? "normal");
  const [count, setCount] = useState(String(node?.question_count ?? 8));
  const [time, setTime] = useState(String(node?.time_limit ?? 0));
  return (
    <Modal title={node ? `Sửa màn` : "Thêm màn"} onClose={onClose}>
      <form
        className="space-y-3"
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit({ mode, question_count: Number(count) || 8, time_limit: Number(time) || 0 });
        }}
      >
        <Field label="Loại màn" htmlFor="nd-mode">
          <select
            id="nd-mode"
            value={mode}
            onChange={(e) => setMode(e.target.value)}
            className="w-full rounded-lg border border-line bg-white px-3 py-2 text-sm"
          >
            {MODES.map((m) => (
              <option key={m.value} value={m.value}>
                {m.label}
              </option>
            ))}
          </select>
        </Field>
        <div className="grid gap-3 sm:grid-cols-2">
          <Field label="Số câu (auto)" required htmlFor="nd-count" hint="1–25. Bỏ qua nếu đã chọn tay.">
            <Input
              id="nd-count"
              required
              inputMode="numeric"
              value={count}
              onChange={(e) => setCount(e.target.value)}
            />
          </Field>
          <Field label="Giờ/câu (0 = auto)" htmlFor="nd-time" hint="Trùm 8s, tốc độ 10s.">
            <Input
              id="nd-time"
              inputMode="numeric"
              value={time}
              onChange={(e) => setTime(e.target.value)}
            />
          </Field>
        </div>
        {node && !node.auto && (
          <p className="text-xs text-muted">
            Màn này đang chọn tay {node.question_ids.length} câu — sửa set câu trong nút “Câu hỏi”.
          </p>
        )}
        <ErrorBox error={error} />
        <div className="flex gap-2">
          <Button type="submit" loading={pending}>
            {node ? "Lưu" : "Thêm màn"}
          </Button>
          <Button type="button" variant="secondary" onClick={onClose}>
            Hủy
          </Button>
        </div>
      </form>
    </Modal>
  );
}

function PickerModal({
  bank,
  initial,
  onClose,
  onSave,
  pending,
}: {
  bank: BankItem[];
  initial: string[];
  onClose: () => void;
  onSave: (ids: string[]) => void;
  pending: boolean;
}) {
  const [search, setSearch] = useState("");
  const [picked, setPicked] = useState<string[]>(initial);
  const list = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return bank;
    return bank.filter(
      (b) => b.qid.toLowerCase().includes(q) || b.title.toLowerCase().includes(q),
    );
  }, [bank, search]);
  const toggle = (qid: string) => {
    setPicked((p) => (p.includes(qid) ? p.filter((x) => x !== qid) : [...p, qid].slice(0, 25)));
  };
  return (
    <Modal title={`Set câu của màn (đã chọn ${picked.length}/25)`} onClose={onClose}>
      <Input
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Tìm theo mã, tiêu đề…"
        aria-label="Tìm câu hỏi"
        className="mb-2"
      />
      <ul className="max-h-80 divide-y divide-line overflow-y-auto rounded-lg border border-line">
        {list.map((b) => {
          const on = picked.includes(b.qid);
          return (
            <li key={b.qid}>
              <button
                type="button"
                onClick={() => toggle(b.qid)}
                className={`flex w-full items-start gap-2 px-3 py-2 text-left text-sm ${
                  on ? "bg-brand-50" : ""
                }`}
              >
                <span
                  className={`mt-0.5 flex size-5 shrink-0 items-center justify-center rounded border text-xs font-black ${
                    on ? "border-brand-600 bg-brand-600 text-white" : "border-line text-transparent"
                  }`}
                >
                  ✓
                </span>
                <span className="min-w-0 flex-1">
                  <span className="mr-2 font-mono text-xs text-muted">{b.qid}</span>
                  {b.title}{" "}
                  {b.custom && <Badge tone="brand">custom</Badge>}{" "}
                  {b.off && <Badge tone="stone">đang tắt</Badge>}
                </span>
              </button>
            </li>
          );
        })}
      </ul>
      <p className="mt-2 text-xs text-muted">
        Thứ tự đã chọn = thứ tự chơi. Câu “đang tắt” sẽ bị bỏ qua khi chơi.
      </p>
      <div className="mt-3 flex gap-2">
        <Button loading={pending} onClick={() => onSave(picked)}>
          Lưu set câu
        </Button>
        <Button variant="secondary" onClick={() => onSave([])}>
          Về auto
        </Button>
        <Button variant="secondary" onClick={onClose}>
          Đóng
        </Button>
      </div>
    </Modal>
  );
}

export default function StructureManager({ slug }: { slug: string }) {
  const queryClient = useQueryClient();
  const [chapterModal, setChapterModal] = useState<null | { chapter: ChapterOut | null }>(null);
  const [nodeModal, setNodeModal] = useState<null | { chapterId: number; node: NodeOut | null }>(null);
  const [picker, setPicker] = useState<null | { node: NodeOut }>(null);

  const structures = useQuery({
    queryKey: ["game-structures", slug],
    queryFn: () => api.get<ChapterOut[]>(`/game/chapters${qs({ concept_slug: slug })}`),
    enabled: !!slug,
  });
  const questions = useQuery({
    queryKey: ["game-questions", slug],
    queryFn: () =>
      api.get<{ custom: { qid: string; title: string; enabled: boolean }[]; disabled_builtin: string[] }>(
        `/game/questions${qs({ concept_slug: slug })}`,
      ),
    enabled: !!slug,
  });
  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["game-structures", slug] });

  const seed = useMutation({
    mutationFn: () => api.post<ChapterOut[]>("/game/chapters/seed", { concept_slug: slug }),
    onSuccess: invalidate,
  });
  const clearAll = useMutation({
    mutationFn: () => api.del(`/game/chapters${qs({ concept_slug: slug })}`),
    onSuccess: invalidate,
  });
  const saveChapter = useMutation({
    mutationFn: (args: { id?: number; body: Record<string, unknown> }) =>
      args.id
        ? api.patch<ChapterOut>(`/game/chapters/${args.id}`, args.body)
        : api.post<ChapterOut>("/game/chapters", args.body),
    onSuccess: () => {
      invalidate();
      setChapterModal(null);
    },
  });
  const delChapter = useMutation({
    mutationFn: (id: number) => api.del(`/game/chapters/${id}`),
    onSuccess: invalidate,
  });
  const saveNode = useMutation({
    mutationFn: (args: { id?: number; body: Record<string, unknown> }) =>
      args.id
        ? api.patch<NodeOut>(`/game/nodes/${args.id}`, args.body)
        : api.post<NodeOut>("/game/nodes", args.body),
    onSuccess: () => {
      invalidate();
      setNodeModal(null);
      setPicker(null);
    },
  });
  const delNode = useMutation({
    mutationFn: (id: number) => api.del(`/game/nodes/${id}`),
    onSuccess: invalidate,
  });

  const bank: BankItem[] = useMemo(() => {
    const builtin = (BANKS[slug] ?? []).map((b) => ({
      qid: b.id,
      title: b.title,
      custom: false,
      off: false,
    }));
    const custom = (questions.data?.custom ?? []).map((c) => ({
      qid: c.qid,
      title: c.title,
      custom: true,
      off: !c.enabled,
    }));
    const disabled = new Set(questions.data?.disabled_builtin ?? []);
    return [...builtin.map((b) => ({ ...b, off: disabled.has(b.qid) })), ...custom];
  }, [slug, questions.data]);

  const moveChapter = (ch: ChapterOut, dir: -1 | 1) => {
    const list = structures.data ?? [];
    const i = list.findIndex((c) => c.id === ch.id);
    const other = list[i + dir];
    if (!other) return;
    saveChapter.mutate({ id: ch.id, body: { idx: other.idx } });
    saveChapter.mutate({ id: other.id, body: { idx: ch.idx } });
  };
  const moveNode = (ch: ChapterOut, n: NodeOut, dir: -1 | 1) => {
    const i = ch.nodes.findIndex((x) => x.id === n.id);
    const other = ch.nodes[i + dir];
    if (!other) return;
    saveNode.mutate({ id: n.id, body: { idx: other.idx } });
    saveNode.mutate({ id: other.id, body: { idx: n.idx } });
  };

  let globalIdx = 0;
  const err =
    structures.error ?? seed.error ?? clearAll.error ?? saveChapter.error ?? delChapter.error;

  return (
    <>
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-base font-bold text-ink">
          Cấu trúc chương/màn{slug ? ` — /${slug}` : ""}
        </h2>
        {(structures.data ?? []).length > 0 && (
          <Button
            variant="secondary"
            className="px-3 py-1.5 text-xs text-red-700"
            loading={clearAll.isPending}
            onClick={() => {
              if (window.confirm("Xóa cấu trúc riêng, về mặc định trong code?"))
                clearAll.mutate();
            }}
          >
            Xóa cấu trúc riêng
          </Button>
        )}
      </div>
      <ErrorBox error={err ?? saveNode.error ?? delNode.error} className="mb-2" />
      {structures.isLoading ? (
        <Spinner />
      ) : (structures.data ?? []).length === 0 ? (
        <Card className="mb-6 p-6 text-center text-sm text-muted">
          <p>Concept này đang dùng cấu trúc mặc định: 4 chương × 3 màn, mỗi màn 8 câu.</p>
          <div className="mt-3 flex justify-center gap-2">
            <Button loading={seed.isPending} onClick={() => seed.mutate()}>
              Copy mặc định để tùy chỉnh
            </Button>
            <Button variant="secondary" onClick={() => setChapterModal({ chapter: null })}>
              Thêm chương trống
            </Button>
          </div>
        </Card>
      ) : (
        <div className="mb-6 space-y-3">
          {(structures.data ?? []).map((ch) => (
            <Card key={ch.id} className="p-4">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xl">{ch.icon || "🗺️"}</span>
                <span className="font-bold text-ink">{ch.name}</span>
                <span className="text-xs text-muted">{ch.desc}</span>
                <span className="ml-auto flex gap-1">
                  <Button
                    variant="secondary"
                    className="px-2 py-1 text-xs"
                    onClick={() => moveChapter(ch, -1)}
                    aria-label="Chương lên trên"
                  >
                    ↑
                  </Button>
                  <Button
                    variant="secondary"
                    className="px-2 py-1 text-xs"
                    onClick={() => moveChapter(ch, 1)}
                    aria-label="Chương xuống dưới"
                  >
                    ↓
                  </Button>
                  <Button
                    variant="secondary"
                    className="px-3 py-1 text-xs"
                    onClick={() => setChapterModal({ chapter: ch })}
                  >
                    Sửa
                  </Button>
                  <Button
                    variant="secondary"
                    className="px-3 py-1 text-xs text-red-700"
                    loading={delChapter.isPending}
                    onClick={() => {
                      if (window.confirm(`Xóa chương “${ch.name}” và toàn bộ màn?`))
                        delChapter.mutate(ch.id);
                    }}
                  >
                    Xóa
                  </Button>
                </span>
              </div>
              <ul className="mt-2 divide-y divide-line rounded-lg border border-line">
                {ch.nodes.map((n) => {
                  globalIdx += 1;
                  const gi = globalIdx;
                  return (
                    <li key={n.id} className="flex flex-wrap items-center gap-2 px-3 py-2 text-sm">
                      <span className="font-bold text-ink">Màn {gi}</span>
                      <Badge tone={n.mode === "boss" ? "gold" : n.mode === "speed" ? "brand" : "stone"}>
                        {MODE_LABEL[n.mode] ?? n.mode}
                      </Badge>
                      <span className="text-muted">
                        {n.auto ? `auto ${n.question_count} câu` : `tay ${n.question_ids.length} câu`}
                      </span>
                      <span className="text-muted">{n.time_limit > 0 ? `${n.time_limit}s/câu` : "giờ auto"}</span>
                      <span className="ml-auto flex gap-1">
                        <Button
                          variant="secondary"
                          className="px-2 py-1 text-xs"
                          onClick={() => setPicker({ node: n })}
                        >
                          Câu hỏi
                        </Button>
                        <Button
                          variant="secondary"
                          className="px-2 py-1 text-xs"
                          onClick={() => moveNode(ch, n, -1)}
                          aria-label="Màn lên trên"
                        >
                          ↑
                        </Button>
                        <Button
                          variant="secondary"
                          className="px-2 py-1 text-xs"
                          onClick={() => moveNode(ch, n, 1)}
                          aria-label="Màn xuống dưới"
                        >
                          ↓
                        </Button>
                        <Button
                          variant="secondary"
                          className="px-2 py-1 text-xs"
                          onClick={() => setNodeModal({ chapterId: ch.id, node: n })}
                        >
                          Sửa
                        </Button>
                        <Button
                          variant="secondary"
                          className="px-2 py-1 text-xs text-red-700"
                          loading={delNode.isPending}
                          onClick={() => {
                            if (window.confirm(`Xóa Màn ${gi}?`)) delNode.mutate(n.id);
                          }}
                        >
                          Xóa
                        </Button>
                      </span>
                    </li>
                  );
                })}
              </ul>
              <div className="mt-2">
                <Button
                  variant="secondary"
                  className="px-3 py-1.5 text-xs"
                  onClick={() => setNodeModal({ chapterId: ch.id, node: null })}
                >
                  + Thêm màn
                </Button>
              </div>
            </Card>
          ))}
          <div>
            <Button variant="secondary" onClick={() => setChapterModal({ chapter: null })}>
              + Thêm chương
            </Button>
          </div>
        </div>
      )}

      {chapterModal && (
        <ChapterModal
          key={chapterModal.chapter?.id ?? "new"}
          initial={chapterModal.chapter}
          onClose={() => setChapterModal(null)}
          pending={saveChapter.isPending}
          error={saveChapter.error}
          onSubmit={(data) => {
            if (chapterModal.chapter) {
              saveChapter.mutate({ id: chapterModal.chapter.id, body: data });
            } else {
              saveChapter.mutate({ body: { ...data, concept_slug: slug } });
            }
          }}
        />
      )}
      {nodeModal && (
        <NodeModal
          key={nodeModal.node?.id ?? `new-${nodeModal.chapterId}`}
          node={nodeModal.node}
          onClose={() => setNodeModal(null)}
          pending={saveNode.isPending}
          error={saveNode.error}
          onSubmit={(data) => {
            if (nodeModal.node) {
              saveNode.mutate({ id: nodeModal.node.id, body: data });
            } else {
              saveNode.mutate({ body: { ...data, chapter_id: nodeModal.chapterId } });
            }
          }}
        />
      )}
      {picker && (
        <PickerModal
          bank={bank}
          initial={picker.node.question_ids}
          onClose={() => setPicker(null)}
          pending={saveNode.isPending}
          onSave={(ids) => saveNode.mutate({ id: picker.node.id, body: { question_ids: ids } })}
        />
      )}
    </>
  );
}
