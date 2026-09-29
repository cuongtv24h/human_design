"use client";

import { useQuery } from "@tanstack/react-query";
import { FileText, Library, Lock } from "lucide-react";
import { useEffect, useState } from "react";
import { Markdown } from "@/components/Markdown";
import { Card, EmptyState, ErrorBox, PageHeader, Spinner, cx } from "@/components/ui";
import { api, qs } from "@/lib/api";
import { useMe } from "@/lib/auth";

type FileEntry = { file: string; title: string; source: "knowledge" | "docs"; sections: number };
type Doc = { file: string; title: string; source: "knowledge" | "docs"; text: string };

/**
 * Đọc tài liệu (Admin): load trực tiếp md từ knowledge/ và docs/ để đọc
 * nguyên văn — companion với Tra cứu tri thức (tìm) và palette ⌘K (nhảy).
 */
export default function DocsReadPage() {
  const me = useMe();
  const isAdmin = me.data?.role === "admin";
  const [selected, setSelected] = useState("");

  const filesQuery = useQuery({
    queryKey: ["knowledge-files"],
    queryFn: () => api.get<{ files: FileEntry[] }>("/knowledge/files"),
    enabled: isAdmin,
    staleTime: 60_000,
  });

  // Chọn mặc định file đầu tiên khi danh sách tải xong.
  useEffect(() => {
    if (!selected && filesQuery.data?.files?.length) setSelected(filesQuery.data.files[0].file);
  }, [filesQuery.data, selected]);

  const docQuery = useQuery({
    queryKey: ["knowledge-doc", selected],
    queryFn: () => api.get<Doc>(`/knowledge/doc${qs({ file: selected })}`),
    enabled: isAdmin && !!selected,
  });

  if (me.isLoading) return <Spinner label="Đang kiểm tra quyền…" />;
  if (!isAdmin) {
    return (
      <EmptyState
        icon={<Lock className="size-8" />}
        title="Chỉ dành cho Quản trị viên"
        description="Trang Đọc tài liệu dành cho Admin. Hãy dùng Tra cứu tri thức để tìm nội dung."
      />
    );
  }

  const files = filesQuery.data?.files ?? [];
  const groups: { key: FileEntry["source"]; label: string; items: FileEntry[] }[] = [
    { key: "knowledge", label: "Knowledge (knowledge/)", items: files.filter((f) => f.source === "knowledge") },
    { key: "docs", label: "Docs / Wiki (docs/)", items: files.filter((f) => f.source === "docs") },
  ];

  return (
    <>
      <PageHeader
        title="Đọc tài liệu"
        description="Đọc trực tiếp toàn bộ tài liệu tri thức (Knowledge + Docs/Wiki). Chỉ Admin."
      />

      {/* Chọn file trên mobile (aside ẩn) */}
      <select
        value={selected}
        onChange={(e) => setSelected(e.target.value)}
        aria-label="Chọn tài liệu"
        className="mb-3 w-full rounded-lg border border-line bg-white px-3 py-2 text-sm outline-none focus:border-brand-400 sm:hidden"
      >
        {files.map((f) => (
          <option key={f.file} value={f.file}>
            {f.title}
          </option>
        ))}
      </select>

      <div className="flex flex-col gap-4 sm:flex-row">
        {/* Danh sách file */}
        <aside className="w-full shrink-0 sm:w-72">
          <Card className="max-h-[70vh] overflow-y-auto p-2">
            {filesQuery.isLoading ? (
              <Spinner />
            ) : !files.length ? (
              <p className="px-3 py-4 text-sm text-muted">Chưa có tài liệu nào.</p>
            ) : (
              groups.map((g) =>
                g.items.length ? (
                  <div key={g.key} className="mb-2">
                    <div className="px-3 pb-1 pt-2 text-[11px] font-semibold uppercase tracking-wider text-muted">
                      {g.label}
                    </div>
                    <ul className="space-y-0.5">
                      {g.items.map((f) => (
                        <li key={f.file}>
                          <button
                            onClick={() => setSelected(f.file)}
                            className={cx(
                              "flex w-full items-start gap-2 rounded-lg px-3 py-2 text-left text-sm transition-colors",
                              selected === f.file
                                ? "bg-brand-50 font-medium text-brand-700"
                                : "text-muted hover:bg-paper hover:text-ink",
                            )}
                          >
                            <FileText className="mt-0.5 size-3.5 shrink-0" aria-hidden />
                            <span className="min-w-0 flex-1">
                              <span className="block truncate">{f.title}</span>
                              <span className="block text-[11px] font-normal text-muted">
                                {f.sections} mục
                              </span>
                            </span>
                          </button>
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : null,
              )
            )}
          </Card>
        </aside>

        {/* Nội dung */}
        <div className="min-w-0 flex-1">
          <ErrorBox error={docQuery.error} className="mb-3" />
          {!selected ? (
            <EmptyState icon={<Library className="size-8" />} title="Chọn một tài liệu bên trái" />
          ) : docQuery.isLoading && !docQuery.data ? (
            <Spinner />
          ) : docQuery.data ? (
            <Card className="p-5 sm:p-7">
              <div className="mb-1 flex flex-wrap items-center gap-2 text-xs text-muted">
                <span
                  className={cx(
                    "rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide",
                    docQuery.data.source === "knowledge" ? "bg-indigo-50 text-indigo-700" : "bg-sky-50 text-sky-700",
                  )}
                >
                  {docQuery.data.source === "knowledge" ? "Knowledge" : "Docs"}
                </span>
                <span className="font-mono text-[11px]">{docQuery.data.file}</span>
              </div>
              <Markdown>{docQuery.data.text}</Markdown>
            </Card>
          ) : null}
        </div>
      </div>
    </>
  );
}
