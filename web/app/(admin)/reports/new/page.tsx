"use client";

import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, ArrowRight, Check, Eye, Search, Sparkles, UserPlus } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState, type ReactNode } from "react";
import { ChartTiles, SvgImage } from "@/components/ChartTiles";
import { Markdown } from "@/components/Markdown";
import { Badge, Button, Card, Checkbox, ErrorBox, Input, LinkButton, PageHeader, Spinner, cx } from "@/components/ui";
import { api, qs } from "@/lib/api";
import { MODE_LABEL, TEMPLATE_LABEL, TIER_LABEL } from "@/lib/format";
import { useDebounced } from "@/lib/hooks";
import type { Catalog, CatalogOption, Client, Paged, Preview, ReportDetail } from "@/lib/types";

const STEPS = ["Khách hàng", "Loại báo cáo", "Cách viết nội dung", "Xác nhận"];

function Stepper({ step, onJump, maxStep }: { step: number; onJump: (i: number) => void; maxStep: number }) {
  return (
    <ol className="mb-6 flex flex-wrap items-center gap-2 text-sm">
      {STEPS.map((label, i) => {
        const done = i < step;
        const active = i === step;
        return (
          <li key={label} className="flex items-center gap-2">
            <button type="button" disabled={i > maxStep} onClick={() => onJump(i)}
              className={cx("flex items-center gap-2 rounded-full py-1 pl-1 pr-3 transition-colors disabled:cursor-not-allowed",
                active ? "bg-brand-500 text-white" : done ? "bg-brand-50 text-brand-700 hover:bg-brand-100" : "bg-white text-muted ring-1 ring-line")}>
              <span className={cx("flex size-6 items-center justify-center rounded-full text-xs font-semibold",
                active ? "bg-white/20" : done ? "bg-brand-500 text-white" : "bg-paper")}>
                {done ? <Check className="size-3.5" /> : i + 1}
              </span>
              {label}
            </button>
            {i < STEPS.length - 1 && <span className="h-px w-4 bg-line" aria-hidden />}
          </li>
        );
      })}
    </ol>
  );
}

function OptionCard({ option, selected, onSelect, disabled, extra }: {
  option: CatalogOption; selected: boolean; onSelect: () => void; disabled?: boolean; extra?: ReactNode;
}) {
  return (
    <button type="button" onClick={onSelect} disabled={disabled} aria-pressed={selected}
      className={cx("w-full rounded-xl border p-4 text-left transition-all disabled:cursor-not-allowed disabled:opacity-55",
        selected ? "border-brand-500 bg-brand-50/60 ring-2 ring-brand-100" : "border-line bg-white hover:border-brand-500/50")}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="font-semibold text-ink">{option.label}</div>
          {option.description && <p className="mt-1 text-sm text-muted">{option.description}</p>}
          {extra}
        </div>
        <span className={cx("mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full border",
          selected ? "border-brand-500 bg-brand-500 text-white" : "border-line")}>
          {selected && <Check className="size-3" />}
        </span>
      </div>
    </button>
  );
}

function ClientPicker({ value, onChange }: { value: number | null; onChange: (c: Client) => void }) {
  const [q, setQ] = useState("");
  const query = useDebounced(q);
  const { data, isLoading } = useQuery({
    queryKey: ["clients", query],
    queryFn: () => api.get<Paged<Client>>(`/clients${qs({ q: query, limit: 50 })}`),
    placeholderData: keepPreviousData,
  });
  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-3">
        <div className="relative min-w-60 flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted" aria-hidden />
          <Input className="pl-9" placeholder="Tìm khách hàng…" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Tìm khách hàng" />
        </div>
        <LinkButton href="/clients/new" variant="secondary"><UserPlus className="size-4" /> Khách hàng mới</LinkButton>
      </div>
      {isLoading ? <Spinner /> : !data?.items.length ? (
        <p className="rounded-lg bg-paper p-4 text-sm text-muted">Chưa có khách hàng phù hợp. Hãy thêm khách hàng mới trước.</p>
      ) : (
        <ul className="max-h-96 divide-y divide-line overflow-y-auto rounded-xl border border-line bg-white">
          {data.items.map((c) => (
            <li key={c.id}>
              <button type="button" onClick={() => onChange(c)} aria-pressed={value === c.id}
                className={cx("flex w-full items-center justify-between gap-3 px-4 py-3 text-left text-sm",
                  value === c.id ? "bg-brand-50" : "hover:bg-paper")}>
                <span>
                  <span className="font-medium text-ink">{c.full_name}</span>
                  <span className="block text-xs text-muted">{c.birth_display}{c.birth_place ? ` · ${c.birth_place}` : ""}</span>
                </span>
                {value === c.id && <Check className="size-4 text-brand-600" />}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function PreviewPanel({ clientId, tier, template, domains }: { clientId: number | null; tier: string; template: string; domains: string[] }) {
  const [showDraft, setShowDraft] = useState(false);
  const preview = useQuery({
    queryKey: ["preview", clientId, tier, template, [...domains].sort().join(",")],
    queryFn: () => api.post<Preview>("/reports/preview", { client_id: clientId, tier, template, domains }),
    enabled: clientId !== null,
    placeholderData: keepPreviousData,
    staleTime: 5 * 60_000,
  });
  if (clientId === null) {
    return <p className="p-5 text-sm text-muted">Chọn khách hàng để xem trước BodyGraph và các thông số chính.</p>;
  }
  if (preview.isLoading) return <Spinner label="Đang tính BodyGraph…" />;
  if (preview.error || !preview.data) return <div className="p-5"><ErrorBox error={preview.error} /></div>;
  const p = preview.data;
  return (
    <div className={cx("space-y-4 p-5 transition-opacity", preview.isFetching && "opacity-60")}>
      <div className="text-xs text-muted">Sinh {p.subject_display}</div>
      <SvgImage svg={p.bodygraph_svg} alt="BodyGraph" className="mx-auto max-h-96 w-full rounded-lg bg-white object-contain" />
      <ChartTiles summary={p.summary} />
      <div>
        <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted">Các phần sẽ có ({p.sections.length})</div>
        <ol className="space-y-1 text-sm">
          {p.sections.map((s, i) => <li key={s.id} className="text-ink"><span className="text-muted">{i + 1}.</span> {s.title}</li>)}
        </ol>
      </div>
      <Button variant="ghost" className="px-2" onClick={() => setShowDraft((v) => !v)}>
        <Eye className="size-4" /> {showDraft ? "Ẩn nội dung nháp" : "Xem nội dung nháp (Template)"}
      </Button>
      {showDraft && (
        <div className="max-h-[32rem] overflow-y-auto rounded-lg border border-line bg-white p-4">
          <Markdown>{p.markdown}</Markdown>
        </div>
      )}
    </div>
  );
}

function Wizard() {
  const router = useRouter();
  const params = useSearchParams();
  const queryClient = useQueryClient();
  const catalog = useQuery({ queryKey: ["catalog"], queryFn: () => api.get<Catalog>("/catalog"), staleTime: 10 * 60_000 });
  const initialClient = Number(params.get("client")) || null;
  const preset = useQuery({
    queryKey: ["client", String(initialClient)],
    queryFn: () => api.get<Client>(`/clients/${initialClient}`),
    enabled: initialClient !== null,
  });

  const [step, setStep] = useState(0);
  const [maxStep, setMaxStep] = useState(0);
  const [client, setClient] = useState<Client | null>(null);
  const [tier, setTier] = useState("deep_core");
  const [template, setTemplate] = useState("operating_manual");
  const [domains, setDomains] = useState<string[]>([]);
  const [mode, setMode] = useState("template");

  useEffect(() => {
    if (preset.data && !client) {
      setClient(preset.data);
      setStep(1);
      setMaxStep(1);
    }
  }, [preset.data, client]);

  const go = (i: number) => {
    setStep(i);
    setMaxStep((m) => Math.max(m, i));
  };

  const create = useMutation({
    mutationFn: () => api.post<ReportDetail>("/reports", { client_id: client!.id, tier, template, domains, content_mode: mode }),
    onSuccess: (report) => {
      queryClient.invalidateQueries({ queryKey: ["reports"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.setQueryData(["report", report.id], report);
      router.push(`/reports/${report.id}`);
    },
  });

  if (catalog.isLoading) return <Spinner />;
  if (!catalog.data) return <ErrorBox error={catalog.error} />;
  const cat = catalog.data;

  const toggleDomain = (value: string, on: boolean) =>
    setDomains((d) => (on ? [...d, value] : d.filter((x) => x !== value)));

  return (
    <>
      <PageHeader title="Tạo báo cáo" description="4 bước — bạn luôn thấy trước BodyGraph và nội dung nháp trước khi tạo." />
      <Stepper step={step} onJump={go} maxStep={maxStep} />
      <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,26rem)]">
        <Card className="p-6">
          {step === 0 && (
            <section className="space-y-4">
              <h2 className="text-lg font-semibold">Báo cáo này dành cho ai?</h2>
              <ClientPicker value={client?.id ?? null} onChange={(c) => setClient(c)} />
            </section>
          )}

          {step === 1 && (
            <section className="space-y-6">
              <div className="space-y-3">
                <h2 className="text-lg font-semibold">Mức độ phân tích</h2>
                <div className="grid gap-3 sm:grid-cols-2">
                  {cat.tiers.map((o) => <OptionCard key={o.value} option={o} selected={tier === o.value} onSelect={() => setTier(o.value)} />)}
                </div>
              </div>
              <div className="space-y-3">
                <h2 className="text-lg font-semibold">Cách trình bày</h2>
                <div className="grid gap-3 sm:grid-cols-2">
                  {cat.templates.map((o) => (
                    <OptionCard key={o.value} option={o} selected={template === o.value} onSelect={() => setTemplate(o.value)}
                      extra={o.value === "operating_manual" ? <div className="mt-2"><Badge tone="gold">Khuyên dùng cho người mới</Badge></div> : undefined} />
                  ))}
                </div>
              </div>
              <div className="space-y-3">
                <div>
                  <h2 className="text-lg font-semibold">Chủ đề chuyên sâu <span className="text-sm font-normal text-muted">(không bắt buộc)</span></h2>
                  <p className="text-sm text-muted">Thêm các chương phân tích riêng theo nhu cầu của khách hàng.</p>
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                  {cat.domains.map((d) => (
                    <Checkbox key={d.value} label={d.label} checked={domains.includes(d.value)} onChange={(on) => toggleDomain(d.value, on)} />
                  ))}
                </div>
              </div>
            </section>
          )}

          {step === 2 && (
            <section className="space-y-4">
              <h2 className="text-lg font-semibold">Ai viết phần nội dung?</h2>
              <p className="text-sm text-muted">
                Thông tin khách hàng và BodyGraph luôn giống nhau. Chỉ phần lời văn khác nhau: nội dung chuẩn tạo ngay,
                hoặc AI biên tập lại theo giọng chuyên gia tham vấn — giàu thấu cảm, dễ chạm tới người đọc.
              </p>
              <div className="grid gap-3">
                {cat.content_modes.map((o) => {
                  const unavailable = o.value === "llm" && !cat.llm_available;
                  return (
                    <OptionCard key={o.value} option={o} selected={mode === o.value} disabled={unavailable} onSelect={() => setMode(o.value)}
                      extra={unavailable ? (
                        <p className="mt-2 text-xs text-amber-700">Chưa cấu hình khóa AI (Cài đặt → AI / LLM hoặc HD_LLM_API_KEY) — tạm thời chưa dùng được.</p>
                      ) : o.value === "llm" ? (
                        <div className="mt-2 space-y-1 text-xs text-[#7a5516]">
                          <div className="flex items-center gap-1"><Sparkles className="size-3.5" /> AI không tính lại chart — chỉ viết lại lời văn từ dữ liệu đã tính.</div>
                          {cat.llm_providers.length > 0 && (
                            <div>
                              Thử theo thứ tự: <strong>{cat.llm_providers[0].name} · {cat.llm_providers[0].model}</strong>
                              {cat.llm_providers.slice(1).map((p) => (
                                <span key={`${p.name}-${p.model}`}> → {p.name} · {p.model}</span>
                              ))}
                            </div>
                          )}
                        </div>
                      ) : undefined} />
                  );
                })}
              </div>
            </section>
          )}

          {step === 3 && client && (
            <section className="space-y-5">
              <h2 className="text-lg font-semibold">Kiểm tra lại trước khi tạo</h2>
              <dl className="divide-y divide-line rounded-xl border border-line text-sm">
                {[
                  ["Khách hàng", `${client.full_name} — ${client.birth_display}`],
                  ["Mức độ", TIER_LABEL[tier]],
                  ["Trình bày", TEMPLATE_LABEL[template]],
                  ["Chủ đề chuyên sâu", domains.length ? cat.domains.filter((d) => domains.includes(d.value)).map((d) => d.label).join(", ") : "Không"],
                  ["Nội dung", mode === "llm" && cat.llm_providers.length
                    ? `${MODE_LABEL[mode]} (${cat.llm_providers.map((p) => `${p.name} · ${p.model}`).join(" → ")})`
                    : MODE_LABEL[mode]],
                ].map(([k, v]) => (
                  <div key={k} className="grid grid-cols-3 gap-3 px-4 py-3">
                    <dt className="text-muted">{k}</dt>
                    <dd className="col-span-2 text-ink">{v}</dd>
                  </div>
                ))}
              </dl>
              {mode === "llm" && (
                <p className="rounded-lg bg-gold-100 p-3 text-sm text-[#6b4a12]">
                  AI cần khoảng 1–2 phút. Bạn có thể rời trang — báo cáo sẽ ở trạng thái “Đang tạo” và tự cập nhật khi xong.
                </p>
              )}
              <ErrorBox error={create.error} />
            </section>
          )}

          <div className="mt-8 flex items-center justify-between border-t border-line pt-5">
            <Button variant="secondary" onClick={() => go(step - 1)} disabled={step === 0}>
              <ArrowLeft className="size-4" /> Quay lại
            </Button>
            {step < 3 ? (
              <Button onClick={() => go(step + 1)} disabled={step === 0 && !client}>
                Tiếp tục <ArrowRight className="size-4" />
              </Button>
            ) : (
              <Button onClick={() => create.mutate()} loading={create.isPending}>
                <Check className="size-4" /> Tạo báo cáo
              </Button>
            )}
          </div>
        </Card>

        <Card className="lg:sticky lg:top-6">
          <div className="border-b border-line px-5 py-4">
            <h2 className="font-semibold text-ink">Xem trước</h2>
            {client && <p className="text-xs text-muted">{client.full_name}</p>}
          </div>
          <PreviewPanel clientId={client?.id ?? null} tier={tier} template={template} domains={domains} />
        </Card>
      </div>
    </>
  );
}

export default function NewReportPage() {
  return (
    <Suspense fallback={<Spinner />}>
      <Wizard />
    </Suspense>
  );
}
