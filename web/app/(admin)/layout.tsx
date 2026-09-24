"use client";

import { useQueryClient } from "@tanstack/react-query";
import { Bot, FilePlus2, FileText, LayoutDashboard, LogOut, Menu, UserCog, Users, X } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";
import { Logo } from "@/components/Logo";
import { Spinner, cx } from "@/components/ui";
import { api, ApiError } from "@/lib/api";
import { useMe } from "@/lib/auth";
import { setSessionToken } from "@/lib/session";

const NAV = [
  { href: "/", label: "Tổng quan", icon: LayoutDashboard, exact: true },
  { href: "/clients", label: "Khách hàng", icon: Users },
  { href: "/reports", label: "Báo cáo", icon: FileText, exclude: "/reports/new" },
  { href: "/reports/new", label: "Tạo báo cáo", icon: FilePlus2 },
];

export default function AdminLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const queryClient = useQueryClient();
  const me = useMe();
  const [open, setOpen] = useState(false);

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
    ? [...NAV, { href: "/settings/users", label: "Tài khoản", icon: UserCog }, { href: "/settings/llm", label: "AI / LLM", icon: Bot }]
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
        <button onClick={logout} className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-muted hover:bg-paper hover:text-ink">
          <LogOut className="size-4" aria-hidden /> Đăng xuất
        </button>
      </div>
    </nav>
  );

  return (
    <div className="min-h-screen lg:pl-64">
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
    </div>
  );
}
