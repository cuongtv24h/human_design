"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { BookOpen, Bot, FilePlus2, FileText, KeyRound, LayoutDashboard, LayoutTemplate, LogOut, Menu, MessagesSquare, UserCog, Users, X } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import { AssistantWidget } from "@/components/AssistantWidget";
import { Logo } from "@/components/Logo";
import { Button, ErrorBox, Field, Input, Modal, Spinner, cx } from "@/components/ui";
import { api, ApiError } from "@/lib/api";
import { useMe } from "@/lib/auth";
import { setSessionToken } from "@/lib/session";

const NAV = [
  { href: "/", label: "Tổng quan", icon: LayoutDashboard, exact: true },
  { href: "/clients", label: "Khách hàng", icon: Users },
  { href: "/reports", label: "Báo cáo", icon: FileText, exclude: "/reports/new" },
  { href: "/reports/new", label: "Tạo báo cáo", icon: FilePlus2 },
  { href: "/templates", label: "Mẫu báo cáo", icon: LayoutTemplate },
  { href: "/guide", label: "Hướng dẫn", icon: BookOpen },
];

function ChangePasswordModal({ onClose }: { onClose: () => void }) {
  const [form, setForm] = useState({ current_password: "", new_password: "", confirm: "" });
  const [done, setDone] = useState(false);
  const [mismatch, setMismatch] = useState(false);
  const change = useMutation({
    mutationFn: () => api.post<void>("/auth/password", {
      current_password: form.current_password,
      new_password: form.new_password,
    }),
    onSuccess: () => setDone(true),
  });
  const submit = (e: FormEvent) => {
    e.preventDefault();
    if (form.new_password !== form.confirm) {
      setMismatch(true);
      return;
    }
    setMismatch(false);
    change.mutate();
  };
  return (
    <Modal title="Đổi mật khẩu" onClose={onClose}>
      {done ? (
        <div className="space-y-4">
          <p className="text-sm text-muted">Đã đổi mật khẩu. Các thiết bị/phiên đăng nhập khác đã bị đăng xuất.</p>
          <Button onClick={onClose}>Đóng</Button>
        </div>
      ) : (
        <form onSubmit={submit} className="space-y-4">
          <Field label="Mật khẩu hiện tại" required htmlFor="pw-cur">
            <Input id="pw-cur" type="password" required value={form.current_password}
              onChange={(e) => setForm({ ...form, current_password: e.target.value })} />
          </Field>
          <Field label="Mật khẩu mới" required htmlFor="pw-new" hint="Tối thiểu 8 ký tự.">
            <Input id="pw-new" type="password" required minLength={8} value={form.new_password}
              onChange={(e) => setForm({ ...form, new_password: e.target.value })} />
          </Field>
          <Field label="Nhập lại mật khẩu mới" required htmlFor="pw-confirm"
            error={mismatch ? "Mật khẩu nhập lại chưa khớp." : undefined}>
            <Input id="pw-confirm" type="password" required minLength={8} value={form.confirm}
              onChange={(e) => setForm({ ...form, confirm: e.target.value })} />
          </Field>
          <ErrorBox error={change.error} />
          <div className="flex gap-2">
            <Button type="submit" loading={change.isPending}>Đổi mật khẩu</Button>
            <Button type="button" variant="secondary" onClick={onClose}>Hủy</Button>
          </div>
        </form>
      )}
    </Modal>
  );
}

export default function AdminLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const queryClient = useQueryClient();
  const me = useMe();
  const [open, setOpen] = useState(false);
  const [pwOpen, setPwOpen] = useState(false);

  useEffect(() => {
    if (me.error instanceof ApiError && me.error.status === 401) {
      router.replace(`/login?next=${encodeURIComponent(pathname)}`);
    }
  }, [me.error, pathname, router]);
  useEffect(() => setOpen(false), [pathname]);

  if (!me.data) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        {me.error && !(me.error instanceof ApiError && me.error.status === 401) ? (
          <p className="text-sm text-red-700">{(me.error as Error).message}</p>
        ) : (
          <Spinner label="Đang kiểm tra đăng nhập…" />
        )}
      </div>
    );
  }
  const user = me.data;
  const nav = user.role === "admin"
    ? [...NAV, { href: "/settings/users", label: "Tài khoản", icon: UserCog }, { href: "/settings/llm", label: "AI / LLM", icon: Bot }, { href: "/settings/assistant", label: "Trợ lý AI", icon: MessagesSquare }]
    : NAV;

  async function logout() {
    await api.post("/auth/logout").catch(() => undefined);
    setSessionToken(null);
    queryClient.clear();
    router.replace("/login");
  }

  const isActive = (item: (typeof nav)[number]) => {
    if ("exact" in item && item.exact) return pathname === item.href;
    if ("exclude" in item && item.exclude && pathname.startsWith(item.exclude)) return false;
    return pathname === item.href || pathname.startsWith(`${item.href}/`);
  };

  const sidebar = (
    <nav className="flex h-full flex-col">
      <Link href="/" className="flex items-center gap-3 px-5 py-5">
        <Logo />
        <div className="leading-tight">
          <div className="text-sm font-bold text-ink">Human Design</div>
          <div className="text-xs text-muted">{user.org_name || "Studio"}</div>
        </div>
      </Link>
      <ul className="flex-1 space-y-1 px-3">
        {nav.map((item) => {
          const Icon = item.icon;
          const active = isActive(item);
          return (
            <li key={item.href}>
              <Link href={item.href} aria-current={active ? "page" : undefined}
                className={cx("flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  active ? "bg-brand-50 text-brand-700" : "text-muted hover:bg-paper hover:text-ink")}>
                <Icon className="size-4" aria-hidden /> {item.label}
              </Link>
            </li>
          );
        })}
      </ul>
      <div className="border-t border-line p-4">
        <div className="mb-3 min-w-0">
          <div className="truncate text-sm font-medium text-ink">{user.full_name || user.email}</div>
          <div className="truncate text-xs text-muted">{user.role === "admin" ? "Quản trị viên" : "Chuyên viên tư vấn"} · {user.email}</div>
        </div>
        <button onClick={() => setPwOpen(true)} className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-muted hover:bg-paper hover:text-ink">
          <KeyRound className="size-4" aria-hidden /> Đổi mật khẩu
        </button>
        <button onClick={logout} className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-muted hover:bg-paper hover:text-ink">
          <LogOut className="size-4" aria-hidden /> Đăng xuất
        </button>
      </div>
    </nav>
  );

  return (
    <div className="min-h-screen lg:pl-64">
      {pwOpen && <ChangePasswordModal onClose={() => setPwOpen(false)} />}
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-line bg-white lg:block">{sidebar}</aside>
      {open && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="absolute inset-0 bg-ink/30" onClick={() => setOpen(false)} />
          <aside className="absolute inset-y-0 left-0 w-72 bg-white shadow-xl">
            <button className="absolute right-3 top-4 rounded-md p-1 text-muted hover:bg-paper" onClick={() => setOpen(false)} aria-label="Đóng menu">
              <X className="size-5" />
            </button>
            {sidebar}
          </aside>
        </div>
      )}
      <header className="sticky top-0 z-30 flex items-center gap-3 border-b border-line bg-white/90 px-4 py-3 backdrop-blur lg:hidden">
        <button onClick={() => setOpen(true)} className="rounded-md p-1 text-ink hover:bg-paper" aria-label="Mở menu">
          <Menu className="size-5" />
        </button>
        <Logo className="size-7" />
        <span className="text-sm font-semibold">Human Design Studio</span>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-10">{children}</main>
      <AssistantWidget />
    </div>
  );
}
