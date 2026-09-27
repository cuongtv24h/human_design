"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, KeyRound, PlugZap, Plus, Save, Trash2, XCircle } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Badge, Button, Card, Checkbox, ErrorBox, Field, Input, PageHeader, Spinner, cx } from "@/components/ui";
import { api, qs } from "@/lib/api";
import { useMe } from "@/lib/auth";
import { formatTimestamp, formatTokens, formatUsd } from "@/lib/format";
import type { LlmProvider, LlmSettings, LlmTest, LlmTestItem, LlmUsage } from "@/lib/types";

const PRESETS = [
  { label: "OpenAI", base_url: "https://api.openai.com/v1", model: "gpt-4o-mini" },
  { label: "OpenRouter", base_url: "https://openrouter.ai/api/v1", model: "openai/gpt-4o-mini" },
  { label: "Gemini", base_url: "https://generativelanguage.googleapis.com/v1beta/openai", model: "gemini-2.5-flash" },
  { label: "Ollama (máy chủ riêng)", base_url: "http://127.0.0.1:11434/v1", model: "qwen2.5:14b" },
];

const ROLE_LABEL = ["Chính", "Dự phòng 1", "Dự phòng 2"];
const PURPOSE_LABEL: Record<string, string> = { report: "Báo cáo", section: "Sửa mục", test: "Kiểm tra", chat: "Trợ lý" };

interface ProviderForm {
  uid: number;
  /** Vị trí trong chuỗi đã lưu (null = thẻ mới chưa lưu). */
  serverIndex: number | null;
  name: string;
  base_url: string;
  model: string;
  temperature: string;
  timeout: string;
  enabled: boolean;
  input_price: string;
  output_price: string;
  apiKey: string;
  keyDirty: boolean;
}

let nextUid = 1;
const blankForm = (role: string): ProviderForm => ({
  uid: nextUid++,
  serverIndex: null,
  name: role,
  base_url: "https://api.openai.com/v1",
  model: "gpt-4o-mini",
  temperature: "0.6",
  timeout: "120",
  enabled: true,
  input_price: "",
  output_price: "",
  apiKey: "",
  keyDirty: false,
});

const fromServer = (p: LlmProvider, index: number): ProviderForm => ({
  uid: nextUid++,
  serverIndex: index,
  name: p.name,
  base_url: p.base_url,
  model: p.model,
  temperature: String(p.temperature),
  timeout: String(p.timeout),
  enabled: p.enabled,
  input_price: p.input_price > 0 ? String(p.input_price) : "",
  output_price: p.output_price > 0 ? String(p.output_price) : "",
  apiKey: "",
  keyDirty: false,
});

/** Thẻ này có khác bản đã lưu không (thẻ mới luôn coi là chưa lưu). */
const isDirty = (f: ProviderForm, saved?: LlmProvider): boolean => {
  if (!saved || f.serverIndex === null) return true;
  return f.keyDirty
    || f.name.trim() !== saved.name
    || f.base_url.trim() !== saved.base_url
    || f.model.trim() !== saved.model
    || Number(f.temperature) !== saved.temperature
    || Number(f.timeout) !== saved.timeout
    || f.enabled !== saved.enabled
    || Number(f.input_price || 0) !== saved.input_price
    || Number(f.output_price || 0) !== saved.output_price;
};

function TestResult({ test }: { test: LlmTestItem }) {
  return (
    <div className={cx("rounded-md p-3 text-xs", test.ok ? "bg-emerald-50 text-emerald-900" : "bg-red-50 text-red-800")} role="status">
      <div className="flex items-center gap-2 font-medium">
        {test.ok ? <CheckCircle2 className="size-4" /> : <XCircle className="size-4" />}
        {test.ok ? "Hoạt động" : "Lỗi"} · {test.model} · {test.latency_ms} ms
      </div>
      <p className="mt-1 break-words">{test.detail}</p>
    </div>
  );
}

export default function LlmSettingsPage() {
  const me = useMe();
  const queryClient = useQueryClient();
  const isAdmin = me.data?.role === "admin";
  const settings = useQuery({
    queryKey: ["llm-settings"],
    queryFn: () => api.get<LlmSettings>("/settings/llm"),
    enabled: isAdmin,
  });
  const [forms, setForms] = useState<ProviderForm[] | null>(null);
  const [tests, setTests] = useState<Record<number, LlmTestItem>>({});
  const [savedTick, setSavedTick] = useState<Record<number, number>>({});
  const [days, setDays] = useState(30);
  const initialized = useRef(false);

  useEffect(() => {
    if (!settings.data || initialized.current) return;
    initialized.current = true;
    const list = settings.data.providers;
    setForms(list.length ? list.map((p, idx) => fromServer(p, idx)) : [blankForm("Chính")]);
  }, [settings.data]);

  const usage = useQuery({
    queryKey: ["llm-usage", days],
    queryFn: () => api.get<LlmUsage>(`/settings/llm/usage${qs({ days })}`),
    enabled: isAdmin,
  });

  const patch = (uid: number, change: Partial<ProviderForm>) => {
    setForms((list) => (list ?? []).map((f) => (f.uid === uid ? { ...f, ...change } : f)));
    setSavedTick((marks) => {
      if (!(uid in marks)) return marks;
      const next = { ...marks };
      delete next[uid];
      return next;
    });
  };

  /** Chuỗi đã lưu dạng payload (giữ nguyên khóa): điểm xuất phát mỗi lần lưu/xóa 1 thẻ. */
  const savedPayload = () =>
    (queryClient.getQueryData<LlmSettings>(["llm-settings"])?.providers ?? []).map((p) => ({
      name: p.name,
      base_url: p.base_url,
      model: p.model,
      temperature: p.temperature,
      timeout: p.timeout,
      enabled: p.enabled,
      input_price: p.input_price,
      output_price: p.output_price,
      api_key: null as string | null,
    }));

  const formPayload = (f: ProviderForm) => ({
    name: f.name.trim(),
    base_url: f.base_url.trim(),
    model: f.model.trim(),
    temperature: Number(f.temperature),
    timeout: Number(f.timeout),
    enabled: f.enabled,
    input_price: Number(f.input_price || 0),
    output_price: Number(f.output_price || 0),
    api_key: f.keyDirty ? (f.apiKey.trim() ? f.apiKey.trim() : "") : null,
  });

  const afterSave = (data: LlmSettings) => {
    queryClient.setQueryData(["llm-settings"], data);
    queryClient.invalidateQueries({ queryKey: ["catalog"] });
    queryClient.invalidateQueries({ queryKey: ["editor"] });
  };

  /** Lưu 1 thẻ: các thẻ khác giữ nguyên bản đã lưu, bản nháp của chúng không bị động tới. */
  const saveOne = useMutation({
    mutationFn: (vars: { uid: number; serverIndex: number | null }) => {
      const form = (forms ?? []).find((f) => f.uid === vars.uid);
      if (!form) throw new Error("Không tìm thấy thẻ cần lưu.");
      const providers = savedPayload();
      if (vars.serverIndex === null) providers.push(formPayload(form));
      else providers[vars.serverIndex] = formPayload(form);
      return api.put<LlmSettings>("/settings/llm", { providers });
    },
    onSuccess: (data, vars) => {
      afterSave(data);
      const idx = vars.serverIndex ?? data.providers.length - 1;
      setForms((list) =>
        (list ?? [])
          .map((f) => (f.uid === vars.uid ? { ...fromServer(data.providers[idx], idx), uid: vars.uid } : f))
          .map((f, pos) => ({ f, pos }))
          .sort((a, b) => (a.f.serverIndex ?? 999) - (b.f.serverIndex ?? 999) || a.pos - b.pos)
          .map(({ f }) => f),
      );
      setTests((prev) => {
        const next = { ...prev };
        delete next[idx];
        return next;
      });
      setSavedTick((marks) => ({ ...marks, [vars.uid]: Date.now() }));
    },
  });

  /** Xóa 1 thẻ đã lưu khỏi chuỗi (lưu ngay, các bản nháp khác giữ nguyên). */
  const delOne = useMutation({
    mutationFn: (vars: { uid: number; serverIndex: number }) => {
      const providers = savedPayload();
      providers.splice(vars.serverIndex, 1);
      return api.put<LlmSettings>("/settings/llm", { providers });
    },
    onSuccess: (data, vars) => {
      afterSave(data);
      setForms((list) =>
        (list ?? [])
          .filter((f) => f.uid !== vars.uid)
          .map((f) => (f.serverIndex !== null && f.serverIndex > vars.serverIndex
            ? { ...f, serverIndex: f.serverIndex - 1 }
            : f)),
      );
      setTests({});
      setSavedTick((marks) => {
        const next = { ...marks };
        delete next[vars.uid];
        return next;
      });
    },
  });

  const removeCard = (f: ProviderForm) => {
    if (f.serverIndex === null) {
      setForms((list) => (list ?? []).filter((x) => x.uid !== f.uid)); // thẻ mới chưa lưu: chỉ gỡ khỏi màn hình
      return;
    }
    if (confirm(`Xóa “${f.name.trim() || "nhà cung cấp này"}” khỏi chuỗi? Thao tác lưu ngay.`)) {
      delOne.mutate({ uid: f.uid, serverIndex: f.serverIndex });
    }
  };

  const check = useMutation({
    mutationFn: (index: number | null) =>
      api.post<LlmTest>("/settings/llm/test", index === null ? {} : { provider_index: index }),
    onSuccess: (data) => {
      const merged: Record<number, LlmTestItem> = {};
      for (const r of data.results) merged[r.index] = r;
      setTests((prev) => ({ ...prev, ...merged }));
    },
  });

  if (me.data && !isAdmin) return <ErrorBox error="Chỉ quản trị viên được truy cập trang này." />;
  if (settings.isLoading || !settings.data || !forms)
    return settings.error ? <ErrorBox error={settings.error} /> : <Spinner />;
  const s = settings.data;
  const anyKey = s.providers.some((p) => p.has_key);
  const busy = saveOne.isPending || delOne.isPending;

  return (
    <>
      <PageHeader
        title="AI / LLM"
        description="Chuỗi nhà cung cấp cho chế độ “AI biên tập”: thử từ trên xuống, cái nào lỗi thì tự chuyển sang cái tiếp theo. Chuẩn OpenAI-compatible."
      />
      <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_20rem]">
        <div className="space-y-4">
          {forms.map((f, i) => {
            const saved = f.serverIndex !== null ? s.providers[f.serverIndex] : undefined;
            const dirty = isDirty(f, saved);
            const savingThis = saveOne.isPending && saveOne.variables?.uid === f.uid;
            return (
              <Card key={f.uid} className="p-5">
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    saveOne.mutate({ uid: f.uid, serverIndex: f.serverIndex });
                  }}
                  className="space-y-4">
                <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <Badge tone={i === 0 ? "gold" : "brand"}>{ROLE_LABEL[i] ?? `Dự phòng ${i}`}</Badge>
                    {saved?.has_key && <span className="text-xs text-muted">Khóa: {saved.key_hint}</span>}
                    {saved && !saved.has_key && <span className="text-xs text-amber-700">Chưa có khóa — sẽ bị bỏ qua khi chạy.</span>}
                    {!saved && <span className="text-xs text-amber-700">Thẻ mới — bấm Lưu ở dưới để thêm vào chuỗi.</span>}
                  </div>
                  <div className="flex items-center gap-3">
                    <Checkbox label="Bật" checked={f.enabled} onChange={(v) => patch(f.uid, { enabled: v })} />
                    {(f.serverIndex === null || s.providers.length > 1) && (
                      <button
                        type="button"
                        title={f.serverIndex === null ? "Gỡ thẻ mới này" : "Xóa nhà cung cấp này khỏi chuỗi (lưu ngay)"}
                        disabled={busy}
                        onClick={() => removeCard(f)}
                        className="rounded-md p-1.5 text-muted hover:bg-red-50 hover:text-red-700 disabled:opacity-50">
                        <Trash2 className="size-4" />
                      </button>
                    )}
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex flex-wrap gap-2">
                    <span className="self-center text-xs text-muted">Mẫu nhanh:</span>
                    {PRESETS.map((p) => (
                      <button key={p.label} type="button" onClick={() => patch(f.uid, { base_url: p.base_url, model: p.model })}
                        className="rounded-full border border-line px-3 py-1 text-xs hover:bg-brand-50">{p.label}</button>
                    ))}
                  </div>
                  <div className="grid gap-4 sm:grid-cols-2">
                    <Field label="Tên gợi nhớ" required htmlFor={`llm-name-${f.uid}`} hint="Hiện khi tạo báo cáo, ví dụ “OpenAI chính”.">
                      <Input id={`llm-name-${f.uid}`} required value={f.name} onChange={(e) => patch(f.uid, { name: e.target.value })} />
                    </Field>
                    <Field label="Địa chỉ API (base URL)" required htmlFor={`llm-url-${f.uid}`} hint="Phần trước /chat/completions.">
                      <Input id={`llm-url-${f.uid}`} required value={f.base_url} onChange={(e) => patch(f.uid, { base_url: e.target.value })} />
                    </Field>
                  </div>
                  <div className="grid gap-4 sm:grid-cols-3">
                    <Field label="Mô hình" required htmlFor={`llm-model-${f.uid}`}>
                      <Input id={`llm-model-${f.uid}`} required value={f.model} onChange={(e) => patch(f.uid, { model: e.target.value })} />
                    </Field>
                    <Field label="Temperature" htmlFor={`llm-temp-${f.uid}`} hint="0,4–0,7: ấm áp mà vẫn bám dữ liệu.">
                      <Input id={`llm-temp-${f.uid}`} type="number" min={0} max={2} step={0.1} value={f.temperature}
                        onChange={(e) => patch(f.uid, { temperature: e.target.value })} />
                    </Field>
                    <Field label="Chờ tối đa (giây)" htmlFor={`llm-timeout-${f.uid}`}>
                      <Input id={`llm-timeout-${f.uid}`} type="number" min={10} max={600} step={10} value={f.timeout}
                        onChange={(e) => patch(f.uid, { timeout: e.target.value })} />
                    </Field>
                  </div>
                  <div className="grid gap-4 sm:grid-cols-2">
                    <Field label="Giá đầu vào (USD / 1M token)" htmlFor={`llm-in-${f.uid}`} hint="Để trống nếu chưa biết — sẽ không tính chi phí.">
                      <Input id={`llm-in-${f.uid}`} type="number" min={0} step={0.01} placeholder="vd 0.15" value={f.input_price}
                        onChange={(e) => patch(f.uid, { input_price: e.target.value })} />
                    </Field>
                    <Field label="Giá đầu ra (USD / 1M token)" htmlFor={`llm-out-${f.uid}`} hint="Để trống nếu chưa biết.">
                      <Input id={`llm-out-${f.uid}`} type="number" min={0} step={0.01} placeholder="vd 0.60" value={f.output_price}
                        onChange={(e) => patch(f.uid, { output_price: e.target.value })} />
                    </Field>
                  </div>
                  <Field label="Khóa API" htmlFor={`llm-key-${f.uid}`}
                    hint={saved?.has_key ? (f.keyDirty ? "Sẽ đổi khóa khi bấm Lưu." : "Để trống nếu không đổi khóa. Khóa được mã hóa khi lưu.") : "Khóa được mã hóa khi lưu và không bao giờ hiển thị lại."}>
                    <div className="flex gap-2">
                      <Input id={`llm-key-${f.uid}`} type="password" autoComplete="off" value={f.apiKey}
                        onChange={(e) => patch(f.uid, { apiKey: e.target.value, keyDirty: true })}
                        placeholder={saved?.has_key ? saved.key_hint : "sk-…"} />
                      {saved?.has_key && (
                        <Button type="button" variant="danger"
                          onClick={() => confirm(`Xóa khóa của “${saved.name}”?`) && patch(f.uid, { apiKey: "", keyDirty: true })}>
                          Xóa
                        </Button>
                      )}
                    </div>
                  </Field>
                  {saved?.key_unreadable && (
                    <p className="rounded-md bg-amber-50 p-2 text-xs text-amber-900">
                      Khóa đã lưu không giải mã được (HD_SECRET_KEY trên máy chủ đã đổi). Hãy nhập lại khóa.
                    </p>
                  )}
                  <div className="flex flex-wrap items-center gap-2 border-t border-line pt-4">
                    <Button type="submit" loading={savingThis}
                      disabled={delOne.isPending || (saveOne.isPending && !savingThis)}>
                      <Save className="size-4" /> Lưu nhà cung cấp này
                    </Button>
                    {dirty && !savingThis && <span className="text-xs text-amber-700">● Có thay đổi chưa lưu</span>}
                    {!dirty && savedTick[f.uid] && <span className="text-xs text-emerald-700">Đã lưu ✓</span>}
                  </div>
                  {saveOne.error && saveOne.variables?.uid === f.uid && <ErrorBox error={saveOne.error} />}
                  <div className="flex flex-wrap items-center gap-2">
                    <Button type="button" variant="secondary" loading={check.isPending}
                      disabled={f.serverIndex === null || !saved?.has_key}
                      onClick={() => f.serverIndex !== null && check.mutate(f.serverIndex)}>
                      <PlugZap className="size-4" /> Kiểm tra nhà cung cấp này
                    </Button>
                    {f.serverIndex === null && <span className="text-xs text-muted">Bấm Lưu ở trên trước rồi mới kiểm tra được.</span>}
                    {f.serverIndex !== null && !saved?.has_key && <span className="text-xs text-muted">Lưu khóa trước rồi mới kiểm tra được.</span>}
                  </div>
                  {f.serverIndex !== null && tests[f.serverIndex] && <TestResult test={tests[f.serverIndex]} />}
                </div>
                </form>
              </Card>
            );
          })}

          {forms.length < 3 && (
            <Button type="button" variant="secondary" onClick={() => setForms((list) => [...(list ?? []), blankForm(ROLE_LABEL[(list ?? []).length] ?? "Dự phòng")])}>
              <Plus className="size-4" /> Thêm nhà cung cấp dự phòng ({forms.length}/3)
            </Button>
          )}

          <ErrorBox error={delOne.error} />
          <div className="flex flex-wrap gap-2">
            <Button type="button" variant="secondary" loading={check.isPending} disabled={!anyKey}
              onClick={() => check.mutate(null)}>
              Kiểm tra tất cả
            </Button>
          </div>
          <ErrorBox error={check.error} />
          <p className="text-xs text-muted">Mỗi thẻ có nút Lưu riêng — chỉ lưu đúng thẻ đó. “Kiểm tra” chỉ gửi vài token bằng cấu hình <strong>đã lưu</strong> và không tính vào thống kê chi phí.</p>
        </div>

        <div className="space-y-4 lg:sticky lg:top-6">
          <Card className="space-y-3 p-5 text-sm">
            <div className="flex items-center gap-2 font-semibold text-ink"><KeyRound className="size-4 text-brand-600" /> Chuỗi đang chạy</div>
            {s.providers.filter((p) => p.has_key && p.enabled).length > 0 ? (
              <ol className="space-y-1.5">
                {s.providers.filter((p) => p.has_key && p.enabled).map((p, order) => (
                  <li key={p.index} className="text-muted">
                    <span className="font-medium text-ink">{order + 1}. {p.name}</span>
                    <span className="block text-xs">{p.model} · {p.key_hint}</span>
                  </li>
                ))}
              </ol>
            ) : s.key_source === "environment" ? (
              <p className="text-muted">Khóa từ biến môi trường HD_LLM_API_KEY trên máy chủ.</p>
            ) : (
              <p className="text-muted">Chưa có khóa — chế độ “AI biên tập” sẽ tự dùng nội dung chuẩn.</p>
            )}
            {s.providers.some((p) => p.has_key && !p.enabled) && (
              <p className="text-xs text-muted">Có nhà cung cấp đang tắt, không tham gia chuỗi.</p>
            )}
            {anyKey && <p className="text-xs text-muted">Khi đã lưu khóa ở đây, HD_LLM_API_KEY trên máy chủ sẽ không được dùng.</p>}
            {s.updated_at && <p className="text-xs text-muted">Cập nhật {formatTimestamp(s.updated_at)} bởi {s.updated_by}</p>}
          </Card>
        </div>
      </div>

      <div className="mt-8">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-lg font-semibold text-ink">Chi phí &amp; lượt gọi</h2>
          <div className="flex gap-1 rounded-lg border border-line bg-white p-1 text-sm">
            {[7, 30, 90].map((d) => (
              <button key={d} type="button" onClick={() => setDays(d)}
                className={cx("rounded-md px-3 py-1", days === d ? "bg-brand-500 text-white" : "text-muted hover:bg-paper")}>
                {d} ngày
              </button>
            ))}
          </div>
        </div>
        {usage.isLoading ? <Spinner /> : usage.error || !usage.data ? <ErrorBox error={usage.error} /> : (
          <UsageStats usage={usage.data} />
        )}
      </div>
    </>
  );
}

function UsageStats({ usage }: { usage: LlmUsage }) {
  const t = usage.totals;
  const stats = [
    { label: "Lượt gọi", value: `${t.requests}` },
    { label: "Token vào / ra", value: `${formatTokens(t.prompt_tokens)} / ${formatTokens(t.completion_tokens)}` },
    { label: "Chi phí ước tính", value: formatUsd(t.cost_usd) },
    { label: "Lượt lỗi", value: `${t.errors}` },
  ];
  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((s) => (
          <Card key={s.label} className="p-4">
            <div className="text-xs text-muted">{s.label}</div>
            <div className="mt-1 text-xl font-bold text-ink">{s.value}</div>
          </Card>
        ))}
      </div>
      {t.unpriced_requests > 0 && (
        <p className="text-xs text-amber-700">
          Có {t.unpriced_requests} lượt gọi chưa tính được tiền (nhà cung cấp chưa nhập giá). Nhập giá ở từng nhà cung cấp phía trên để thống kê đầy đủ.
        </p>
      )}
      {usage.by_provider.length > 0 && (
        <Card className="overflow-x-auto">
          <table className="w-full min-w-[36rem] text-sm">
            <thead>
              <tr className="border-b border-line text-left text-xs uppercase tracking-wider text-muted">
                <th className="px-4 py-3 font-medium">Nhà cung cấp</th>
                <th className="px-4 py-3 text-right font-medium">Lượt gọi</th>
                <th className="px-4 py-3 text-right font-medium">Token</th>
                <th className="px-4 py-3 text-right font-medium">Chi phí</th>
                <th className="px-4 py-3 text-right font-medium">Lỗi</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {usage.by_provider.map((p) => (
                <tr key={`${p.provider}-${p.model}`}>
                  <td className="px-4 py-2.5">
                    <span className="font-medium text-ink">{p.provider}</span>
                    <span className="block text-xs text-muted">{p.model}</span>
                  </td>
                  <td className="px-4 py-2.5 text-right">{p.requests}</td>
                  <td className="px-4 py-2.5 text-right">{formatTokens(p.prompt_tokens + p.completion_tokens)}</td>
                  <td className="px-4 py-2.5 text-right">{p.cost_usd > 0 || p.unpriced_requests === 0 ? formatUsd(p.cost_usd) : "—"}</td>
                  <td className="px-4 py-2.5 text-right">{p.errors}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
      {usage.recent.length > 0 && (
        <Card className="overflow-x-auto">
          <div className="border-b border-line px-4 py-3 text-sm font-semibold text-ink">Gần đây nhất</div>
          <table className="w-full min-w-[44rem] text-sm">
            <thead>
              <tr className="border-b border-line text-left text-xs uppercase tracking-wider text-muted">
                <th className="px-4 py-2 font-medium">Thời gian</th>
                <th className="px-4 py-2 font-medium">Việc</th>
                <th className="px-4 py-2 font-medium">Nhà cung cấp</th>
                <th className="px-4 py-2 text-right font-medium">Token vào/ra</th>
                <th className="px-4 py-2 text-right font-medium">Chi phí</th>
                <th className="px-4 py-2 text-right font-medium">Kết quả</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {usage.recent.slice(0, 20).map((r) => (
                <tr key={r.id}>
                  <td className="px-4 py-2 text-xs text-muted">{formatTimestamp(r.created_at)}</td>
                  <td className="px-4 py-2">{PURPOSE_LABEL[r.purpose] ?? r.purpose}</td>
                  <td className="px-4 py-2">
                    <span className="text-ink">{r.provider}</span>
                    <span className="block text-xs text-muted">{r.model}</span>
                  </td>
                  <td className="px-4 py-2 text-right">{formatTokens(r.prompt_tokens)}/{formatTokens(r.completion_tokens)}</td>
                  <td className="px-4 py-2 text-right">{formatUsd(r.cost_usd)}</td>
                  <td className="px-4 py-2 text-right">
                    {r.ok
                      ? <span className="text-xs text-emerald-700">{r.latency_ms} ms</span>
                      : <span className="block max-w-56 truncate text-xs text-red-700" title={r.error}>{r.error || "Lỗi"}</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
      {usage.recent.length === 0 && (
        <Card><p className="p-5 text-sm text-muted">Chưa có lượt gọi AI nào trong {usage.days} ngày qua.</p></Card>
      )}
    </div>
  );
}
