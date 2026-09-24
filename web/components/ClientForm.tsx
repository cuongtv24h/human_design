"use client";

import { useState, type FormEvent } from "react";
import { Button, Checkbox, ErrorBox, Field, Input, Textarea } from "@/components/ui";
import { dmyToIso, isoToDmy, maskDate, maskTime, normalizeTime } from "@/lib/format";
import type { ClientInput } from "@/lib/types";

export const EMPTY_CLIENT: ClientInput = {
  full_name: "", email: "", phone: "", birth_date: "", birth_time: "", birth_time_known: true,
  birth_place: "", timezone: "+07:00", notes: "",
};

type Errors = Partial<Record<"full_name" | "birth_date" | "birth_time" | "consent", string>>;

export function ClientForm({
  initial = EMPTY_CLIENT,
  requireConsent,
  submitLabel,
  onSubmit,
  onCancel,
}: {
  initial?: ClientInput;
  requireConsent: boolean;
  submitLabel: string;
  onSubmit: (value: ClientInput) => Promise<void>;
  onCancel?: () => void;
}) {
  const [form, setForm] = useState({ ...initial, birth_date: isoToDmy(initial.birth_date) });
  const [consent, setConsent] = useState(false);
  const [errors, setErrors] = useState<Errors>({});
  const [serverError, setServerError] = useState<unknown>(null);
  const [saving, setSaving] = useState(false);
  const set = <K extends keyof ClientInput>(key: K, value: ClientInput[K]) => setForm((f) => ({ ...f, [key]: value }));

  async function submit(event: FormEvent) {
    event.preventDefault();
    const next: Errors = {};
    const isoDate = dmyToIso(form.birth_date);
    const time = normalizeTime(form.birth_time);
    if (!form.full_name.trim()) next.full_name = "Vui lòng nhập họ tên.";
    if (!isoDate) next.birth_date = "Ngày sinh chưa đúng. Nhập theo dạng dd/mm/yyyy, ví dụ 15/05/1990.";
    if (!time) next.birth_time = "Giờ sinh chưa đúng. Nhập theo dạng 24 giờ HH:MM, ví dụ 08:30 hoặc 20:15.";
    if (requireConsent && !consent) next.consent = "Cần có sự đồng ý của khách hàng trước khi lưu dữ liệu sinh.";
    setErrors(next);
    if (Object.keys(next).length) return;
    setSaving(true);
    setServerError(null);
    try {
      await onSubmit({ ...form, full_name: form.full_name.trim(), birth_date: isoDate!, birth_time: time!, consent });
    } catch (err) {
      setServerError(err);
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={submit} className="space-y-6" noValidate>
      <div className="grid gap-5 sm:grid-cols-2">
        <div className="sm:col-span-2">
          <Field label="Họ và tên" required htmlFor="full_name" error={errors.full_name}>
            <Input id="full_name" value={form.full_name} onChange={(e) => set("full_name", e.target.value)}
              placeholder="Nguyễn Văn A" invalid={!!errors.full_name} autoFocus />
          </Field>
        </div>
        <Field label="Ngày sinh" required htmlFor="birth_date" error={errors.birth_date} hint="Dạng dd/mm/yyyy — ngày dương lịch.">
          <Input id="birth_date" inputMode="numeric" value={form.birth_date} placeholder="dd/mm/yyyy"
            onChange={(e) => set("birth_date", maskDate(e.target.value))} invalid={!!errors.birth_date} />
        </Field>
        <Field label="Giờ sinh (giờ Việt Nam)" required htmlFor="birth_time" error={errors.birth_time}
          hint="Dạng 24 giờ, đúng như giấy khai sinh / gia đình ghi nhớ. Hệ thống tính theo UTC+07:00.">
          <Input id="birth_time" inputMode="numeric" value={form.birth_time} placeholder="HH:MM"
            onChange={(e) => set("birth_time", maskTime(e.target.value))} invalid={!!errors.birth_time} />
        </Field>
        <div className="sm:col-span-2">
          <Checkbox checked={!form.birth_time_known} onChange={(v) => set("birth_time_known", !v)}
            label="Giờ sinh chỉ là ước lượng"
            description="Đánh dấu nếu gia đình không nhớ chính xác. Profile, Chữ thập hóa thân và một số cổng có thể thay đổi khi giờ lệch." />
        </div>
        <Field label="Nơi sinh" htmlFor="birth_place" hint="Chỉ để hiển thị trên báo cáo.">
          <Input id="birth_place" value={form.birth_place} onChange={(e) => set("birth_place", e.target.value)} placeholder="Hòa Bình, Việt Nam" />
        </Field>
        <Field label="Số điện thoại" htmlFor="phone">
          <Input id="phone" type="tel" value={form.phone} onChange={(e) => set("phone", e.target.value)} placeholder="09xx xxx xxx" />
        </Field>
        <Field label="Email" htmlFor="email">
          <Input id="email" type="email" value={form.email} onChange={(e) => set("email", e.target.value)} placeholder="khachhang@vidu.com" />
        </Field>
        <div className="sm:col-span-2">
          <Field label="Ghi chú nội bộ" htmlFor="notes" hint="Chỉ bạn và quản trị viên thấy — không xuất hiện trên báo cáo.">
            <Textarea id="notes" value={form.notes} onChange={(e) => set("notes", e.target.value)} placeholder="Mục tiêu tư vấn, bối cảnh hiện tại…" />
          </Field>
        </div>
      </div>

      {requireConsent && (
        <div className="rounded-lg border border-line bg-paper p-4">
          <Checkbox checked={consent} onChange={setConsent}
            label="Khách hàng đã đồng ý cho lưu và xử lý dữ liệu cá nhân (ngày, giờ, nơi sinh) để lập báo cáo."
            description="Theo Luật Bảo vệ dữ liệu cá nhân (hiệu lực 01/01/2026). Thời điểm xác nhận được ghi lại." />
          {errors.consent && <p className="mt-2 text-xs text-red-700">{errors.consent}</p>}
        </div>
      )}

      <ErrorBox error={serverError} />
      <div className="flex flex-wrap gap-3">
        <Button type="submit" loading={saving}>{submitLabel}</Button>
        {onCancel && <Button type="button" variant="secondary" onClick={onCancel}>Hủy</Button>}
      </div>
    </form>
  );
}
