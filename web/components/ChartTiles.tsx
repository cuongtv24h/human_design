import type { ChartSummary } from "@/lib/types";

function Tile({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="rounded-lg border border-line bg-white p-3">
      <div className="text-[11px] font-semibold uppercase tracking-wider text-muted">{label}</div>
      <div className="mt-1 text-sm font-semibold text-ink">{value || "—"}</div>
      {sub && <div className="text-xs text-muted">{sub}</div>}
    </div>
  );
}

/** Key chart facts, bilingual per the shared terminology (tools/hd_language.py). */
export function ChartTiles({ summary }: { summary: ChartSummary }) {
  return (
    <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
      <Tile label="Loại năng lượng" value={summary.type_vn || summary.type} sub={summary.type} />
      <Tile label="Chiến lược sống" value={summary.strategy} />
      <Tile label="Quyền nội tại" value={summary.authority} />
      <Tile label="Nhân cách (Profile)" value={summary.profile} />
      <Tile label="Định nghĩa" value={summary.definition} />
      <Tile label="Trung tâm định nghĩa" value={`${summary.defined_centers}/9`} />
      <div className="col-span-2 md:col-span-3">
        <Tile label="Chữ thập hóa thân (Incarnation Cross)" value={summary.incarnation_cross} />
      </div>
    </div>
  );
}

/** Render generated SVG through <img> so any embedded markup can never execute. */
export function SvgImage({ svg, alt, className }: { svg: string; alt: string; className?: string }) {
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img src={`data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`} alt={alt} className={className} />
  );
}
