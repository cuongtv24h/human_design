"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, KeyRound, PlugZap, XCircle } from "lucide-react";
import { useEffect, useState, type FormEvent } from "react";
import { Badge, Button, Card, ErrorBox, Field, Input, PageHeader, Spinner } from "@/components/ui";
import { api } from "@/lib/api";
import { useMe } from "@/lib/auth";
import { formatTimestamp } from "@/lib/format";
import type { LlmSettings, LlmTest } from "@/lib/types";

const PRESETS = [
  { label: "OpenAI", base_url: "https://api.openai.com/v1", model: "gpt-4o-mini" },
  { label: "OpenRouter", base_url: "https://openrouter.ai/api/v1", model: "openai/gpt-4o-mini" },
  { label: "Ollama (máy chủ riêng)", base_url: "http://127.0.0.1:11434/v1", model: "qwen2.5:14b" },
];

const SOURCE: Record<LlmSettings["key_source"], string> = {
  database: "Khóa lưu trong hệ thống (đã mã hóa)",
  environment: "Khóa từ biến môi trường HD_LLM_API_KEY trên máy chủ",
  none: "Chưa có khóa — chế độ “AI biên tập” sẽ tự dùng nội dung chuẩn",
};

export default function LlmSettingsPage() {
  const me = useMe();
  const queryClient = useQueryClient();
  const settings = useQuery({ queryKey: ["llm-settings"], queryFn: () => api.get<LlmSettings>("/settings/llm"), enabled: me.data?.role === "admin" });
  const [form, setForm] = useState({ base_url: "", model: "", temperature: "0.6", timeout: "120" });
  const [apiKey, setApiKey] = useState("");
  const [test, setTest] = useState<LlmTest | null>(null);

  useEffect(() => {
    if (!settings.data) return;
    const s = settings.data;
    setForm({ base_url: s.base_url, model: s.model, temperature: String(s.temperature), timeout: String(s.timeout) });
  }, [settings.data]);

  const save = useMutation({
    mutationFn: (key: string | null) =>
      api.put<LlmSettings>("/settings/llm", {
        base_url: form.base_url, model: form.model, temperature: Number(form.temperature), timeout: Number(form.timeout), api_key: key,
      }),
    onSuccess: (data) => {
      queryClient.setQueryData(["llm-settings"], data);
      queryClient.invalidateQueries({ queryKey: ["editor"] });
      setApiKey("");
      setTest(null);
    },
  });
  const check = useMutation({ mutationFn: () => api.post<LlmTest>("/settings/llm/test"), onSuccess: setTest });

  if (me.data && me.data.role !== "admin") return <ErrorBox error="Chỉ quản trị viên được truy cập trang này." />;
  if (settings.isLoading || !settings.data) return settings.error ? <ErrorBox error={settings.error} /> : <Spinner />;
  const s = settings.data;

  const submit = (e: FormEvent) => {
    e.preventDefault();
    save.mutate(apiKey.trim() ? apiKey.trim() : null);
  };

  return (
    <>
      <PageHeader title="AI / LLM" description="Nhà cung cấp AI dùng cho chế độ “AI biên tập” và nút “AI biên tập phần này”. Chuẩn OpenAI-compatible." />
      <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_20rem]">
        <Card className="p-6">
          <form onSubmit={submit} className="space-y-5">
            <div className="flex flex-wrap gap-2">
              <span className="self-center text-xs text-muted">Mẫu nhanh:</span>
              {PRESETS.map((p) => (
                <button key={p.label} type="button" onClick={() => setForm({ ...form, base_url: p.base_url, model: p.model })}
                  className="rounded-full border border-line px-3 py-1 text-xs hover:bg-brand-50">{p.label}</button>
              ))}
            </div>
            <Field label="Địa chỉ API (base URL)" required htmlFor="llm-url" hint="Phần trước /chat/completions.">
              <Input id="llm-url" required value={form.base_url} onChange={(e) => setForm({ ...form, base_url: e.target.value })} placeholder="https://api.openai.com/v1" />
            </Field>
            <div className="grid gap-4 sm:grid-cols-3">
              <Field label="Mô hình" required htmlFor="llm-model">
                <Input id="llm-model" required value={form.model} onChange={(e) => setForm({ ...form, model: e.target.value })} />
              </Field>
              <Field label="Temperature" htmlFor="llm-temp" hint="0,4–0,7: ấm áp mà vẫn bám dữ liệu.">
                <Input id="llm-temp" type="number" min={0} max={2} step={0.1} value={form.temperature} onChange={(e) => setForm({ ...form, temperature: e.target.value })} />
              </Field>
              <Field label="Thời gian chờ (giây)" htmlFor="llm-timeout">
                <Input id="llm-timeout" type="number" min={10} max={600} step={10} value={form.timeout} onChange={(e) => setForm({ ...form, timeout: e.target.value })} />
              </Field>
            </div>
            <Field label="Khóa API" htmlFor="llm-key"
              hint={s.key_source === "database" ? `Đang dùng ${s.key_hint}. Để trống nếu không đổi khóa.` : "Khóa được mã hóa khi lưu và không bao giờ hiển thị lại."}>
              <Input id="llm-key" type="password" autoComplete="off" value={apiKey} onChange={(e) => setApiKey(e.target.value)} placeholder={s.key_source === "database" ? s.key_hint : "sk-…"} />
            </Field>
            <ErrorBox error={save.error} />
            <div className="flex flex-wrap gap-2">
              <Button type="submit" loading={save.isPending && save.variables !== ""}>Lưu cấu hình</Button>
              {s.key_source === "database" && (
                <Button type="button" variant="danger" loading={save.isPending && save.variables === ""}
                  onClick={() => confirm("Xóa khóa API đã lưu? Hệ thống sẽ dùng HD_LLM_API_KEY trên máy chủ (nếu có).") && save.mutate("")}>
                  Xóa khóa đã lưu
                </Button>
              )}
            </div>
          </form>
        </Card>

        <div className="space-y-4">
          <Card className="space-y-3 p-5 text-sm">
            <div className="flex items-center gap-2 font-semibold text-ink"><KeyRound className="size-4 text-brand-600" /> Trạng thái khóa</div>
            <Badge tone={s.key_source === "none" ? "stone" : "brand"}>{s.key_source === "none" ? "Chưa bật AI" : `AI đang bật · ${s.key_hint}`}</Badge>
            <p className="text-muted">{SOURCE[s.key_source]}</p>
            {s.key_unreadable && (
              <p className="rounded-md bg-amber-50 p-2 text-xs text-amber-900">Khóa đã lưu không giải mã được (HD_SECRET_KEY trên máy chủ đã đổi). Hãy nhập lại khóa.</p>
            )}
            {s.updated_at && <p className="text-xs text-muted">Cập nhật {formatTimestamp(s.updated_at)} bởi {s.updated_by}</p>}
          </Card>
          <Card className="space-y-3 p-5 text-sm">
            <div className="flex items-center gap-2 font-semibold text-ink"><PlugZap className="size-4 text-brand-600" /> Kiểm tra kết nối</div>
            <p className="text-muted">Gửi một yêu cầu rất ngắn bằng cấu hình <strong>đã lưu</strong>.</p>
            <Button variant="secondary" loading={check.isPending} disabled={s.key_source === "none"} onClick={() => check.mutate()}>Kiểm tra ngay</Button>
            <ErrorBox error={check.error} />
            {test && (
              <div className={test.ok ? "rounded-md bg-emerald-50 p-3 text-emerald-900" : "rounded-md bg-red-50 p-3 text-red-800"} role="status">
                <div className="flex items-center gap-2 font-medium">
                  {test.ok ? <CheckCircle2 className="size-4" /> : <XCircle className="size-4" />}
                  {test.ok ? "Hoạt động" : "Lỗi"} · {test.model} · {test.latency_ms} ms
                </div>
                <p className="mt-1 break-words text-xs">{test.detail}</p>
              </div>
            )}
          </Card>
        </div>
      </div>
    </>
  );
}
