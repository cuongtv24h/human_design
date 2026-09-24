// Client-facing share page (plan P3-2): server-rendered, mobile-first, noindex.
// Data comes straight from hd-api on the server — the browser only sees this page and
// same-origin /api/v1/public/* file links.

import type { Metadata } from "next";
import { headers } from "next/headers";
import { Download, FileText, Maximize2 } from "lucide-react";
import { ChartTiles } from "@/components/ChartTiles";
import { Logo } from "@/components/Logo";
import { Markdown } from "@/components/Markdown";
import type { PublicReport } from "@/lib/types";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Báo cáo Human Design của bạn",
  robots: { index: false, follow: false, nocache: true },
  referrer: "no-referrer",
};

const API_INTERNAL_URL = process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8001";

const FORMAT_LABEL: Record<string, string> = { pdf: "Tải PDF", docx: "Tải bản Word", markdown: "Tải Markdown" };

type Loaded = { kind: "ok"; data: PublicReport } | { kind: "gone" | "missing" | "error"; message: string };

async function load(token: string): Promise<Loaded> {
  const incoming = await headers();
  const forwarded = incoming.get("x-forwarded-for") ?? "";
  try {
    const res = await fetch(`${API_INTERNAL_URL}/api/v1/public/r/${encodeURIComponent(token)}`, {
      cache: "no-store",
      headers: { Accept: "application/json", ...(forwarded ? { "X-Forwarded-For": forwarded } : {}) },
    });
    if (res.ok) return { kind: "ok", data: (await res.json()) as PublicReport };
    const body = await res.json().catch(() => ({}));
    const message = typeof body?.detail === "string" ? body.detail : "";
    if (res.status === 410) return { kind: "gone", message };
    if (res.status === 404) return { kind: "missing", message };
    return { kind: "error", message };
  } catch {
    return { kind: "error", message: "" };
  }
}

function Shell({ children, org }: { children: React.ReactNode; org?: string }) {
  return (
    <div className="min-h-screen bg-paper">
      <header className="border-b border-line bg-white/80">
        <div className="mx-auto flex max-w-3xl items-center gap-3 px-4 py-3">
          <Logo />
          <div className="text-sm font-semibold text-ink">{org || "Human Design Studio"}</div>
        </div>
      </header>
      <main className="mx-auto max-w-3xl px-4 pb-16 pt-6 sm:pt-10">{children}</main>
    </div>
  );
}

function Notice({ title, text }: { title: string; text: string }) {
  return (
    <Shell>
      <div className="rounded-2xl border border-line bg-white p-8 text-center shadow-sm">
        <h1 className="text-lg font-semibold text-ink">{title}</h1>
        <p className="mx-auto mt-2 max-w-md text-sm text-muted">{text}</p>
      </div>
    </Shell>
  );
}

export default async function SharedReportPage({ params }: { params: Promise<{ token: string }> }) {
  const { token } = await params;
  const result = await load(token);
  if (result.kind === "gone") {
    return <Notice title="Link không còn hiệu lực" text={result.message || "Link đã hết hạn hoặc đã bị thu hồi. Vui lòng liên hệ người tư vấn để nhận link mới."} />;
  }
  if (result.kind === "missing") {
    return <Notice title="Không tìm thấy báo cáo" text="Đường link chưa đúng. Hãy kiểm tra lại link bạn nhận được (chép đầy đủ, không thiếu ký tự)." />;
  }
  if (result.kind !== "ok") {
    return <Notice title="Chưa mở được báo cáo" text="Máy chủ đang bận. Bạn thử tải lại trang sau ít phút nhé." />;
  }

  const r = result.data;
  const base = `/api/v1/public/r/${encodeURIComponent(token)}`;
  return (
    <Shell org={r.org_name}>
      <section className="mb-6">
        <p className="text-xs font-semibold uppercase tracking-wider text-gold-500">Báo cáo Human Design</p>
        <h1 className="mt-1 text-2xl font-bold leading-tight text-ink sm:text-3xl">{r.client_name}</h1>
        <p className="mt-1 text-sm text-muted">Sinh {r.subject_display}</p>
        {r.formats.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {r.formats.map((f, i) => (
              <a key={f} href={`${base}/${f}`}
                className={i === 0
                  ? "inline-flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-brand-600"
                  : "inline-flex items-center gap-2 rounded-lg border border-line bg-white px-4 py-2.5 text-sm font-medium text-ink hover:bg-brand-50"}>
                {i === 0 ? <Download className="size-4" /> : <FileText className="size-4" />} {FORMAT_LABEL[f] ?? f}
              </a>
            ))}
          </div>
        )}
      </section>

      <section className="mb-8 rounded-2xl border border-line bg-white p-4 shadow-sm sm:p-5">
        <ChartTiles summary={r.summary} />
      </section>

      <section className="mb-10">
        <div className="mb-2 flex items-center justify-between">
          <h2 className="text-base font-semibold text-ink">Tóm tắt một trang</h2>
          <a href={`${base}/infographic.html`} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-sm text-brand-700 hover:underline">
            <Maximize2 className="size-3.5" /> Toàn màn hình
          </a>
        </div>
        <div className="overflow-hidden rounded-2xl border border-line bg-white shadow-sm">
          <iframe title="Infographic" src={`${base}/infographic.html`} sandbox="" loading="lazy" className="h-[75vh] w-full" />
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-base font-semibold text-ink">Đọc toàn bộ báo cáo</h2>
        <nav aria-label="Mục lục" className="mb-6 rounded-2xl border border-line bg-white p-4 text-sm">
          <ol className="list-decimal space-y-1 pl-5">
            {r.sections.map((s) => <li key={s.id}><a href={`#${s.id}`} className="text-brand-700 hover:underline">{s.title}</a></li>)}
          </ol>
        </nav>
        <div className="space-y-6">
          {r.sections.map((s) => (
            <article key={s.id} id={s.id} className="scroll-mt-4 rounded-2xl border border-line bg-white p-5 shadow-sm sm:p-7">
              <h3 className="mb-3 text-lg font-semibold text-brand-700">{s.title}</h3>
              <Markdown>{s.content_markdown}</Markdown>
            </article>
          ))}
        </div>
      </section>

      <footer className="mt-12 border-t border-line pt-6 text-center text-xs leading-relaxed text-muted">
        Human Design là công cụ tự quan sát và thử nghiệm trong đời sống — không thay thế tư vấn y tế, tâm lý, pháp lý hay tài chính.
        <br />Link này dành riêng cho bạn; vui lòng không chia sẻ công khai.
      </footer>
    </Shell>
  );
}
