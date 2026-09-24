"use client";

import Link from "next/link";
import { Loader2 } from "lucide-react";
import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode, TextareaHTMLAttributes } from "react";
import { STATUS_LABEL } from "@/lib/format";

export function cx(...parts: (string | false | null | undefined)[]) {
  return parts.filter(Boolean).join(" ");
}

type Variant = "primary" | "secondary" | "ghost" | "danger";
const VARIANTS: Record<Variant, string> = {
  primary: "bg-brand-500 text-white hover:bg-brand-600 shadow-sm disabled:bg-brand-500/50",
  secondary: "bg-white text-ink border border-line hover:bg-brand-50 disabled:opacity-50",
  ghost: "text-brand-700 hover:bg-brand-50 disabled:opacity-50",
  danger: "bg-white text-red-700 border border-red-200 hover:bg-red-50 disabled:opacity-50",
};
const BASE_BTN =
  "inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500 disabled:cursor-not-allowed";

export function Button({
  variant = "primary",
  loading,
  className,
  children,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant; loading?: boolean }) {
  return (
    <button className={cx(BASE_BTN, VARIANTS[variant], className)} disabled={loading || props.disabled} {...props}>
      {loading && <Loader2 className="size-4 animate-spin" aria-hidden />}
      {children}
    </button>
  );
}

export function LinkButton({
  href,
  variant = "primary",
  className,
  children,
  ...rest
}: { href: string; variant?: Variant; className?: string; children: ReactNode; download?: boolean; target?: string }) {
  return (
    <Link href={href} className={cx(BASE_BTN, VARIANTS[variant], className)} {...rest}>
      {children}
    </Link>
  );
}

export function Card({ className, children }: { className?: string; children: ReactNode }) {
  return <div className={cx("rounded-xl border border-line bg-white shadow-[0_1px_2px_rgba(35,34,39,0.04)]", className)}>{children}</div>;
}

export function PageHeader({ title, description, actions }: { title: string; description?: ReactNode; actions?: ReactNode }) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-ink">{title}</h1>
        {description && <p className="mt-1 text-sm text-muted">{description}</p>}
      </div>
      {actions && <div className="flex flex-wrap gap-2">{actions}</div>}
    </div>
  );
}

export function Field({
  label,
  hint,
  error,
  required,
  htmlFor,
  children,
}: {
  label: string;
  hint?: ReactNode;
  error?: string;
  required?: boolean;
  htmlFor?: string;
  children: ReactNode;
}) {
  return (
    <div className="space-y-1.5">
      <label htmlFor={htmlFor} className="block text-sm font-medium text-ink">
        {label}
        {required && <span className="ml-0.5 text-red-600">*</span>}
      </label>
      {children}
      {error ? <p className="text-xs text-red-700">{error}</p> : hint ? <p className="text-xs text-muted">{hint}</p> : null}
    </div>
  );
}

const INPUT =
  "block w-full rounded-lg border border-line bg-white px-3 py-2 text-sm text-ink placeholder:text-muted/70 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100 disabled:bg-paper";

export function Input({ className, invalid, ...props }: InputHTMLAttributes<HTMLInputElement> & { invalid?: boolean }) {
  return <input className={cx(INPUT, invalid && "border-red-400 focus:border-red-500 focus:ring-red-100", className)} {...props} />;
}

export function Textarea({ className, ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea className={cx(INPUT, "min-h-24", className)} {...props} />;
}

export function Spinner({ label = "Đang tải…" }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 py-10 text-sm text-muted" role="status">
      <Loader2 className="size-4 animate-spin" aria-hidden /> {label}
    </div>
  );
}

export function ErrorBox({ error, className }: { error: unknown; className?: string }) {
  if (!error) return null;
  const message = error instanceof Error ? error.message : String(error);
  return (
    <div role="alert" className={cx("rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800", className)}>
      {message}
    </div>
  );
}

export function EmptyState({ icon, title, description, action }: { icon?: ReactNode; title: string; description?: string; action?: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center px-6 py-14 text-center">
      {icon && <div className="mb-3 text-brand-500">{icon}</div>}
      <p className="font-semibold text-ink">{title}</p>
      {description && <p className="mt-1 max-w-sm text-sm text-muted">{description}</p>}
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}

const STATUS_STYLE: Record<string, string> = {
  generating: "bg-amber-50 text-amber-800 ring-amber-200",
  ready: "bg-emerald-50 text-emerald-800 ring-emerald-200",
  failed: "bg-red-50 text-red-800 ring-red-200",
  archived: "bg-stone-100 text-stone-600 ring-stone-200",
};

export function StatusBadge({ status }: { status: string }) {
  return (
    <span className={cx("inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset", STATUS_STYLE[status])}>
      {status === "generating" && <Loader2 className="size-3 animate-spin" aria-hidden />}
      {STATUS_LABEL[status] ?? status}
    </span>
  );
}

export function Badge({ children, tone = "brand" }: { children: ReactNode; tone?: "brand" | "gold" | "stone" }) {
  const tones = {
    brand: "bg-brand-50 text-brand-700 ring-brand-100",
    gold: "bg-gold-100 text-[#7a5516] ring-[#ecd9b2]",
    stone: "bg-stone-100 text-stone-700 ring-stone-200",
  };
  return <span className={cx("inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset", tones[tone])}>{children}</span>;
}

export function Checkbox({ checked, onChange, label, description, disabled }: {
  checked: boolean; onChange: (v: boolean) => void; label: ReactNode; description?: ReactNode; disabled?: boolean;
}) {
  return (
    <label className={cx("flex cursor-pointer items-start gap-3", disabled && "cursor-not-allowed opacity-60")}>
      <input type="checkbox" className="mt-0.5 size-4 rounded border-line accent-brand-500" checked={checked}
        disabled={disabled} onChange={(e) => onChange(e.target.checked)} />
      <span className="text-sm">
        <span className="font-medium text-ink">{label}</span>
        {description && <span className="mt-0.5 block text-xs text-muted">{description}</span>}
      </span>
    </label>
  );
}
