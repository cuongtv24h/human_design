"use client";

import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { ChevronDown, FileText, Search } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { Card, EmptyState, ErrorBox, PageHeader, Spinner, cx } from "@/components/ui";
import { api, qs } from "@/lib/api";
import { useDebounced } from "@/lib/hooks";

type Hit = {
  file: string;
  title: string;
  section: string;
  source: "knowledge" | "docs";
  score: number;
  snippet: string;
  text: string;
};
type SearchResp = { query: string; hits: Hit[]; count: number; took_ms: number };
type FileEntry = { file: string; title: string; source: "knowledge" | "docs"; sections: number };
type SourceFilter = "all" | "knowledge" | "docs";

// Query seed khi idle — kết quả mặc định hiển thị trên trang trống.
const SEED_QUERY = "human design";
// Popular queries: click là chạy ngay (debounce 300ms).
const SUGGESTED = [
  "manifesting generator",
  "thẩm quyền sacral",
  "profile dòng 6",
  "nuôi dạy con",
  "kênh điện từ",
  "not self",
  "điều kiện hóa",
  "transit hôm nay",
  "192 chữ thập",
  "sợ hãi",
  "quan hệ",
  "tiền bạc",
];

const SOURCE_LABEL: Record<SourceFilter, string> = {
  all: "Tất cả",
  knowledge: "Knowledge",
  docs: "Docs",
};

function escapeRe(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/** Bôi đậm best-effort: khớp exact (không phân biệt hoa/thường) từng token >=2 ký tự. */
function Highlight({ text, query }: { text: string; query: string }) {
  const tokens = useMemo(
    () => [...new Set(query.toLowerCase().split(/\s+/).filter((t) => t.length >= 2))],
    [query],
  );
  if (!tokens.length) return <>{text}</>;
  const parts = text.split(new RegExp(`(${tokens.map(escapeRe).join("|")})`, "gi"));
  const set = new Set(tokens);
  return (
    <>
      {parts.map((part, i) =>
        set.has(part.toLowerCase()) ? (
          <mark key={i} className="rounded bg-amber-100 px-0.5 text-ink">
            {part}
          </mark>
        ) : (
          <span key={i}>{part}</span>
        ),
      )}
    </>
  );
}

function SourceBadge({ source }: { source: Hit["source"] }) {
  return (
    <span
      className={cx(
        "rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide",
        source === "knowledge" ? "bg-indigo-50 text-indigo-700" : "bg-sky-50 text-sky-700",
      )}
    >
      {source === "knowledge" ? "Knowledge" : "Docs"}
    </span>
  );
}

export default function KnowledgeSearchPage() {
  const [q, setQ] = useState("");
  const [source, setSource] = useState<SourceFilter>("all");
  const [file, setFile] = useState("");
  const [expanded, setExpanded] = useState<Record<number, boolean>>({});
  const dq = useDebounced(q, 300);
  const inputRef = useRef<HTMLInputElement>(null);

  // Deep-link ?q=… (vd từ palette ⌘K) — đọc sau mount để không ảnh hưởng SSR.
  useEffect(() => {
    const initial = new URLSearchParams(window.location.search).get("q");
    if (initial) setQ(initial);
  }, []);

  const filesQuery = useQuery({
    queryKey: ["knowledge-files"],
    queryFn: () => api.get<{ files: FileEntry[] }>("/knowledge/files"),
    staleTime: 60_000,
  });
  const visibleFiles = (filesQuery.data?.files ?? []).filter(
    (f) => source === "all" || f.source === source,
  );

  const idle = dq.trim().length < 2;
  const effectiveQ = idle ? SEED_QUERY : dq;
  const searchQuery = useQuery({
    queryKey: ["knowledge-search", effectiveQ, source, file, idle ? 6 : 12],
    queryFn: () =>
      api.get<SearchResp>(`/knowledge/search${qs({ q: effectiveQ, limit: idle ? 6 : 12, source, file })}`),
    placeholderData: keepPreviousData,
  });

  const hits = searchQuery.data?.hits ?? [];

  return (
    <>
      <PageHeader
        title="Tra cứu tri thức"
        description="Tìm trong kho Knowledge (knowledge/) và Docs/Wiki (docs/) — cùng engine với Trợ lý AI nhưng hiển thị trực tiếp, không tốn token."
      />

      <div className="relative mb-3 max-w-2xl">
        <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted" aria-hidden />
        <input
          ref={inputRef}
          autoFocus
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Ví dụ: manifesting generator, nuôi dạy con, hồ sơ dòng 6…"
          aria-label="Tìm trong kho tri thức"
          className="w-full rounded-xl border border-line bg-white py-3 pl-9 pr-3 text-sm text-ink outline-none placeholder:text-muted focus:border-brand-400 focus:ring-2 focus:ring-brand-100"
        />
      </div>

      <div className="mb-4 flex flex-wrap items-center gap-2">
        {(Object.keys(SOURCE_LABEL) as SourceFilter[]).map((s) => (
          <button
            key={s}
            onClick={() => {
              setSource(s);
              setFile("");
            }}
            className={cx(
              "rounded-full border px-3 py-1 text-xs font-medium transition-colors",
              source === s
                ? "border-brand-500 bg-brand-50 text-brand-700"
                : "border-line bg-white text-muted hover:text-ink",
            )}
          >
            {SOURCE_LABEL[s]}
          </button>
        ))}
        <select
          value={file}
          onChange={(e) => setFile(e.target.value)}
          aria-label="Lọc theo file"
          className="ml-auto max-w-[280px] truncate rounded-lg border border-line bg-white px-2 py-1.5 text-xs text-muted outline-none focus:border-brand-400"
        >
          <option value="">Tất cả file ({visibleFiles.length})</option>
          {visibleFiles.map((f) => (
            <option key={f.file} value={f.file}>
              {f.title} — {f.sections} mục
            </option>
          ))}
        </select>
      </div>

      <ErrorBox error={searchQuery.error} className="mb-4" />

      {idle && (
        <Card className="mb-4 p-4">
          <div className="mb-1 text-sm font-semibold text-ink">Gợi ý tra cứu phổ biến</div>
          <p className="mb-3 text-xs text-muted">
            Bấm một gợi ý để tìm ngay — không dấu vẫn trúng (vd: "nuoi day con").
          </p>
          <div className="flex flex-wrap gap-2">
            {SUGGESTED.map((s) => (
              <button
                key={s}
                onClick={() => {
                  setQ(s);
                  setFile("");
                  inputRef.current?.focus();
                }}
                className="rounded-full border border-line bg-white px-3 py-1.5 text-xs font-medium text-muted transition-colors hover:border-brand-400 hover:bg-brand-50 hover:text-brand-700"
              >
                {s}
              </button>
            ))}
          </div>
        </Card>
      )}

      {searchQuery.isLoading && !searchQuery.data ? (
        <Spinner />
      ) : !hits.length ? (
        idle ? null : (
          <EmptyState
            icon={<Search className="size-8" />}
            title="Không tìm thấy kết quả"
            description={`Không có mục nào cho “${dq}”. Thử từ khóa rộng hơn hoặc bỏ bộ lọc file.`}
          />
        )
      ) : (
        <>
          <p className="mb-3 text-xs text-muted">
            {idle
              ? `Gợi ý mặc định · “${SEED_QUERY}” · ${hits.length} mục`
              : `${hits.length} kết quả · ${searchQuery.data?.took_ms} ms`}
          </p>
          <div className="space-y-3">
            {hits.map((hit, i) => {
              const open = !!expanded[i];
              const showSection = hit.section && hit.section !== hit.title;
              return (
                <Card key={`${hit.file}-${i}`} className="p-4">
                  <div className="mb-1.5 flex flex-wrap items-center gap-2 text-xs text-muted">
                    <SourceBadge source={hit.source} />
                    <FileText className="size-3.5" aria-hidden />
                    <span className="truncate font-mono text-[11px]">{hit.file}</span>
                    <span className="ml-auto rounded bg-paper px-1.5 py-0.5 text-[10px]">
                      điểm {hit.score}
                    </span>
                  </div>
                  <div className="text-sm font-semibold text-ink">
                    {hit.title}
                    {showSection && <span className="font-normal text-muted"> — {hit.section}</span>}
                  </div>
                  <p className="mt-1.5 whitespace-pre-wrap text-sm leading-relaxed text-ink/85">
                    <Highlight text={hit.snippet} query={dq} />
                  </p>
                  {open && (
                    <div className="mt-3 rounded-lg bg-paper p-3 text-sm leading-relaxed text-ink/85">
                      <div className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-muted">
                        Nguyên văn mục
                      </div>
                      <Highlight text={hit.text} query={dq} />
                    </div>
                  )}
                  <button
                    onClick={() => setExpanded((m) => ({ ...m, [i]: !m[i] }))}
                    className="mt-2 inline-flex items-center gap-1 text-xs font-medium text-brand-700 hover:underline"
                  >
                    {open ? "Thu gọn" : "Xem toàn bộ mục"}
                    <ChevronDown className={cx("size-3.5 transition-transform", open && "rotate-180")} />
                  </button>
                </Card>
              );
            })}
          </div>
        </>
      )}
    </>
  );
}
