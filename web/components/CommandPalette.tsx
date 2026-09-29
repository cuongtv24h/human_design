"use client";

import { useQuery } from "@tanstack/react-query";
import { FileText, LayoutTemplate, Search, User, X } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
import { api, qs } from "@/lib/api";
import { useDebounced } from "@/lib/hooks";
import type { Client, Paged, ReportSummary, TemplateSummary } from "@/lib/types";

type KnowledgeHit = {
  file: string;
  title: string;
  section: string;
  source: "knowledge" | "docs";
  snippet: string;
};
type PaletteItem = {
  key: string;
  group: string;
  title: string;
  sub?: string;
  href: string;
  icon: typeof Search;
};

const GROUP_ORDER = ["Tri thức", "Khách hàng", "Báo cáo", "Mẫu báo cáo"];

/**
 * Palette tìm kiếm toàn cục (⌘K / Ctrl+K): gộp tri thức + khách hàng + báo cáo +
 * mẫu báo cáo. Tri thức mở trang tra cứu với q đã điền (xem đầy đủ + bộ lọc).
 */
export function CommandPalette({ onClose }: { onClose: () => void }) {
  const router = useRouter();
  const [q, setQ] = useState("");
  const [sel, setSel] = useState(0);
  const dq = useDebounced(q, 200);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);
  useEffect(() => setSel(0), [dq]);

  const enabledClient = dq.trim().length >= 1;
  const knowledge = useQuery({
    queryKey: ["palette-knowledge", dq],
    queryFn: () =>
      api.get<{ hits: KnowledgeHit[] }>(`/knowledge/search${qs({ q: dq, limit: 5 })}`),
    enabled: dq.trim().length >= 2,
    staleTime: 30_000,
  });
  const clients = useQuery({
    queryKey: ["palette-clients", dq],
    queryFn: () => api.get<Paged<Client>>(`/clients${qs({ q: dq, limit: 5 })}`),
    enabled: enabledClient,
    staleTime: 30_000,
  });
  const reports = useQuery({
    queryKey: ["palette-reports", dq],
    queryFn: () => api.get<Paged<ReportSummary>>(`/reports${qs({ q: dq, limit: 5 })}`),
    enabled: enabledClient,
    staleTime: 30_000,
  });
  const templates = useQuery({
    queryKey: ["palette-templates", dq],
    queryFn: () => api.get<TemplateSummary[]>(`/templates${qs({ q: dq, limit: 5 })}`),
    enabled: enabledClient,
    staleTime: 30_000,
  });

  const items = useMemo<PaletteItem[]>(() => {
    const out: PaletteItem[] = [];
    for (const hit of knowledge.data?.hits ?? []) {
      out.push({
        key: `k:${hit.file}:${hit.section}:${out.length}`,
        group: "Tri thức",
        title: hit.section || hit.title,
        sub: `${hit.source === "docs" ? "Docs" : "Knowledge"} · ${hit.file}`,
        href: `/admin/knowledge${qs({ q: dq })}`,
        icon: Search,
      });
    }
    for (const c of clients.data?.items ?? []) {
      out.push({
        key: `c:${c.id}`,
        group: "Khách hàng",
        title: c.full_name,
        sub: c.email || c.birth_display,
        href: `/admin/clients/${c.id}`,
        icon: User,
      });
    }
    for (const r of reports.data?.items ?? []) {
      out.push({
        key: `r:${r.id}`,
        group: "Báo cáo",
        title: `${r.client_name} · ${r.template_name}`,
        sub: r.status,
        href: `/admin/reports/${r.id}`,
        icon: FileText,
      });
    }
    for (const t of templates.data ?? []) {
      out.push({
        key: `t:${t.id}`,
        group: "Mẫu báo cáo",
        title: t.name,
        sub: t.description || undefined,
        href: `/admin/templates/${t.id}`,
        icon: LayoutTemplate,
      });
    }
    // sắp theo thứ tự nhóm cố định (giữ nguyên thứ tự bên trong nhóm)
    return out.sort((a, b) => GROUP_ORDER.indexOf(a.group) - GROUP_ORDER.indexOf(b.group));
  }, [knowledge.data, clients.data, reports.data, templates.data, dq]);

  const loading =
    knowledge.isFetching || clients.isFetching || reports.isFetching || templates.isFetching;
  const waiting = enabledClient && loading && !items.length;

  const go = (item: PaletteItem) => {
    onClose();
    router.push(item.href);
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      e.preventDefault();
      onClose();
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      setSel((s) => Math.min(s + 1, Math.max(items.length - 1, 0)));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSel((s) => Math.max(s - 1, 0));
    } else if (e.key === "Enter" && items[sel]) {
      e.preventDefault();
      go(items[sel]);
    }
  };

  let lastGroup = "";

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center">
      <div className="absolute inset-0 bg-ink/40 backdrop-blur-[2px]" onClick={onClose} />
      <div
        role="dialog"
        aria-label="Tìm kiếm toàn cục"
        className="relative mt-[10vh] w-[min(640px,92vw)] overflow-hidden rounded-2xl border border-line bg-white shadow-2xl"
      >
        <div className="flex items-center gap-2 border-b border-line px-4">
          <Search className="size-4 shrink-0 text-muted" aria-hidden />
          <input
            ref={inputRef}
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Tìm tri thức, khách hàng, báo cáo, mẫu…"
            aria-label="Tìm kiếm toàn cục"
            className="w-full bg-transparent py-3.5 text-sm text-ink outline-none placeholder:text-muted"
          />
          <button
            onClick={onClose}
            aria-label="Đóng tìm kiếm"
            className="rounded-md p-1 text-muted hover:bg-paper hover:text-ink"
          >
            <X className="size-4" />
          </button>
        </div>

        <div className="max-h-[55vh] overflow-y-auto p-2">
          {waiting ? (
            <p className="px-3 py-6 text-center text-sm text-muted">Đang tìm…</p>
          ) : !dq.trim() ? (
            <p className="px-3 py-6 text-center text-sm text-muted">
              Gõ để tìm trong tri thức, khách hàng, báo cáo và mẫu báo cáo.
            </p>
          ) : !items.length ? (
            <p className="px-3 py-6 text-center text-sm text-muted">
              Không có kết quả cho “{dq}”.
            </p>
          ) : (
            items.map((item, i) => {
              const header = item.group !== lastGroup ? ((lastGroup = item.group), item.group) : null;
              return (
                <div key={item.key}>
                  {header && (
                    <div className="px-3 pb-1 pt-2.5 text-[11px] font-semibold uppercase tracking-wider text-muted">
                      {header}
                    </div>
                  )}
                  <button
                    onMouseMove={() => setSel(i)}
                    onClick={() => go(item)}
                    className={cxItem(i === sel)}
                  >
                    <item.icon className="size-4 shrink-0 text-muted" aria-hidden />
                    <span className="min-w-0 flex-1 text-left">
                      <span className="block truncate text-sm font-medium text-ink">{item.title}</span>
                      {item.sub && <span className="block truncate text-xs text-muted">{item.sub}</span>}
                    </span>
                  </button>
                </div>
              );
            })
          )}
        </div>

        <div className="flex items-center gap-3 border-t border-line bg-paper px-4 py-2 text-[11px] text-muted">
          <span>↑↓ chọn</span>
          <span>Enter mở</span>
          <span>Esc đóng</span>
          <span className="ml-auto">{items.length} kết quả</span>
        </div>
      </div>
    </div>
  );
}

function cxItem(active: boolean): string {
  return [
    "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left transition-colors",
    active ? "bg-brand-50 text-brand-700" : "text-ink hover:bg-paper",
  ].join(" ");
}
