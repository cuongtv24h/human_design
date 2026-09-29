"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { BookOpen, Bot, FilePlus2, FileText, Gamepad, KeyRound, LayoutDashboard, LayoutTemplate, Library, LogOut, Menu, MessagesSquare, PanelLeftClose, PanelLeftOpen, Search, UserCog, UserPlus, Users, X, type LucideIcon } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import { AssistantWidget } from "@/components/AssistantWidget";
import { CommandPalette } from "@/components/CommandPalette";
import { Logo } from "@/components/Logo";
import { Button, ErrorBox, Field, Input, Modal, Spinner, cx } from "@/components/ui";
import { api, ApiError } from "@/lib/api";
import { useMe } from "@/lib/auth";
import { setSessionToken } from "@/lib/session";

// Sidebar gom nhóm theo chủ đề (thay vì11 mục phẳng). Mục đánh dấu adminOnly
// chỉ hiện cho role admin — với coach nhóm tương ứng tự rỗng và bị ẩn.
type NavItem = {
  href: string;
  label: string;
  icon: LucideIcon;
  exact?: boolean;
  exclude?: string;
  adminOnly?: boolean;
};
type NavGroup = { title?: string; adminOnly?: boolean; items: NavItem[] };

const GROUPS: NavGroup[] = [
  {
    // Mục đầu không có tiêu đề nhóm — giữ cảm giác "trang chủ" như trước.
    items: [{ href: "/admin", label: "Tổng quan", icon: LayoutDashboard, exact: true }],
  },
  {
    title: "Khách hàng",
    items: [
      { href: "/admin/clients", label: "Khách hàng", icon: Users },
      { href: "/admin/leads", label: "Khách tiềm năng", icon: UserPlus, adminOnly: true },
    ],
  },
  {
    title: "Báo cáo",
    items: [
      { href: "/admin/reports", label: "Báo cáo", icon: FileText, exclude: "/admin/reports/new" },
      { href: "/admin/reports/new", label: "Tạo báo cáo", icon: FilePlus2 },
      { href: "/admin/templates", label: "Mẫu báo cáo", icon: LayoutTemplate },
      { href: "/admin/guide", label: "Hướng dẫn", icon: BookOpen },
    ],
  },
  {
    title: "Công cụ",
    items: [
      { href: "/admin/knowledge", label: "Tra cứu tri thức", icon: Search },
      { href: "/admin/docs", label: "Đọc tài liệu", icon: Library, adminOnly: true },
      { href: "/admin/game", label: "Game", icon: Gamepad, adminOnly: true },
    ],
  },
  {
    title: "Hệ thống",
    adminOnly: true,
    items: [
      { href: "/admin/settings/users", label: "Tài khoản", icon: UserCog },
      { href: "/admin/settings/llm", label: "AI / LLM", icon: Bot },
      { href: "/admin/settings/assistant", label: "Trợ lý AI", icon: MessagesSquare },
    ],
  },
];

const NAV_COLLAPSED_KEY = "hd.admin.nav.collapsed";

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
  // Thu nhỏ sidebar (chỉ desktop; nhớ qua localStorage). Khởi tại false để
  // SSR/client render khớp nhau — đọc storage trong useEffect sau hydration.
  const [collapsed, setCollapsed] = useState(false);
  const [palOpen, setPalOpen] = useState(false);
  // Trang login nằm trong /admin nên phải thoát khỏi guard — không thì máy chưa
  // đăng nhập sẽ kẹt ở "Đang kiểm tra đăng nhập…" vì form login không bao giờ render.
  const isLoginPage = pathname === "/admin/login" || pathname.startsWith("/admin/login/");

  useEffect(() => {
    if (!isLoginPage && me.error instanceof ApiError && me.error.status === 401) {
      router.replace(`/admin/login?next=${encodeURIComponent(pathname)}`);
    }
  }, [me.error, pathname, router, isLoginPage]);
  useEffect(() => setOpen(false), [pathname]);
  useEffect(() => {
    try {
      setCollapsed(localStorage.getItem(NAV_COLLAPSED_KEY) === "1");
    } catch {
      /* localStorage không sẵn sàng — để mở rộng */
    }
  }, []);
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setPalOpen((v) => !v);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const toggleCollapsed = () =>
    setCollapsed((c) => {
      const next = !c;
      try {
        localStorage.setItem(NAV_COLLAPSED_KEY, next ? "1" : "0");
      } catch {
        /* bỏ qua */
      }
      return next;
    });

  if (isLoginPage) return <>{children}</>;

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
  const isAdmin = user.role === "admin";
  const groups = GROUPS.filter((g) => !g.adminOnly || isAdmin)
    .map((g) => ({ ...g, items: g.items.filter((it) => !it.adminOnly || isAdmin) }))
    .filter((g) => g.items.length > 0);

  async function logout() {
    await api.post("/auth/logout").catch(() => undefined);
    setSessionToken(null);
    queryClient.clear();
    router.replace("/admin/login");
  }

  const isActive = (item: NavItem) => {
    if (item.exact) return pathname === item.href;
    if (item.exclude && pathname.startsWith(item.exclude)) return false;
    return pathname === item.href || pathname.startsWith(`${item.href}/`);
  };

  // desktop=true chỉ dùng cho sidebar cố định (lg+); drawer mobile luôn mở
  // đầy đủ nhãn vì người dùng mở nó theo hành động bấm.
  const renderSidebar = (desktop: boolean) => {
    const mini = desktop && collapsed;
    const iconBtn =
      "flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-muted hover:bg-paper hover:text-ink";
    const iconBtnMini = "justify-center px-0";
    return (
      <nav className="flex h-full flex-col">
        <Link
          href="/admin"
          className={cx("flex items-center gap-3 px-5 py-5", mini && "justify-center px-0")}
          title={mini ? "Human Design Studio" : undefined}
        >
          <Logo className={mini ? "size-7" : undefined} />
          {!mini && (
            <div className="min-w-0 leading-tight">
              <div className="text-sm font-bold text-ink">Human Design</div>
              <div className="text-xs text-muted">{user.org_name || "Studio"}</div>
            </div>
          )}
        </Link>

        <div className="flex-1 overflow-y-auto px-3">
          <button
            onClick={() => setPalOpen(true)}
            title={mini ? "Tìm kiếm (⌘K)" : undefined}
            className={cx(
              "mb-1 mt-1 flex w-full items-center gap-2 rounded-lg border border-line bg-paper/60 px-3 py-2 text-sm text-muted hover:text-ink",
              mini && "justify-center px-0",
            )}
          >
            <Search className="size-4 shrink-0" aria-hidden />
            {!mini && (
              <>
                <span className="flex-1 text-left">Tìm kiếm…</span>
                <kbd className="rounded border border-line bg-white px-1.5 py-0.5 text-[10px] font-sans">
                  ⌘K
                </kbd>
              </>
            )}
          </button>
          {groups.map((group) => (
            <div key={group.title ?? "main"}>
              {group.title && !mini && (
                <div className="px-3 pb-1 pt-4 text-[11px] font-semibold uppercase tracking-wider text-muted">
                  {group.title}
                </div>
              )}
              {group.title && mini && <div className="mx-2 my-2 border-t border-line" />}
              <ul className="space-y-1">
                {group.items.map((item) => {
                  const Icon = item.icon;
                  const active = isActive(item);
                  return (
                    <li key={item.href}>
                      <Link
                        href={item.href}
                        aria-current={active ? "page" : undefined}
                        title={mini ? item.label : undefined}
                        className={cx(
                          "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                          mini && iconBtnMini,
                          active ? "bg-brand-50 text-brand-700" : "text-muted hover:bg-paper hover:text-ink",
                        )}
                      >
                        <Icon className="size-4 shrink-0" aria-hidden />
                        {!mini && item.label}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </div>

        <div className="border-t border-line p-4">
          {!mini && (
            <div className="mb-3 min-w-0">
              <div className="truncate text-sm font-medium text-ink">{user.full_name || user.email}</div>
              <div className="truncate text-xs text-muted">
                {isAdmin ? "Quản trị viên" : "Chuyên viên tư vấn"} · {user.email}
              </div>
            </div>
          )}
          {desktop && (
            <button
              onClick={toggleCollapsed}
              aria-expanded={!collapsed}
              title={mini ? "Mở rộng menu" : "Thu nhỏ menu"}
              className={cx(iconBtn, mini && iconBtnMini)}
            >
              {mini ? <PanelLeftOpen className="size-4" aria-hidden /> : <PanelLeftClose className="size-4" aria-hidden />}
              {!mini && "Thu nhỏ menu"}
            </button>
          )}
          <button
            onClick={() => setPwOpen(true)}
            title={mini ? "Đổi mật khẩu" : undefined}
            className={cx(iconBtn, mini && iconBtnMini)}
          >
            <KeyRound className="size-4" aria-hidden /> {!mini && "Đổi mật khẩu"}
          </button>
          <button onClick={logout} title={mini ? "Đăng xuất" : undefined} className={cx(iconBtn, mini && iconBtnMini)}>
            <LogOut className="size-4" aria-hidden /> {!mini && "Đăng xuất"}
          </button>
        </div>
      </nav>
    );
  };

  return (
    <div className={cx("min-h-screen", collapsed ? "lg:pl-16" : "lg:pl-64")}>
      {pwOpen && <ChangePasswordModal onClose={() => setPwOpen(false)} />}
      {palOpen && <CommandPalette onClose={() => setPalOpen(false)} />}
      <aside
        className={cx(
          "fixed inset-y-0 left-0 hidden border-r border-line bg-white lg:block",
          collapsed ? "w-16" : "w-64",
        )}
      >
        {renderSidebar(true)}
      </aside>
      {open && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="absolute inset-0 bg-ink/30" onClick={() => setOpen(false)} />
          <aside className="absolute inset-y-0 left-0 w-72 bg-white shadow-xl">
            <button className="absolute right-3 top-4 rounded-md p-1 text-muted hover:bg-paper" onClick={() => setOpen(false)} aria-label="Đóng menu">
              <X className="size-5" />
            </button>
            {renderSidebar(false)}
          </aside>
        </div>
      )}
      <header className="sticky top-0 z-30 flex items-center gap-3 border-b border-line bg-white/90 px-4 py-3 backdrop-blur lg:hidden">
        <button onClick={() => setOpen(true)} className="rounded-md p-1 text-ink hover:bg-paper" aria-label="Mở menu">
          <Menu className="size-5" />
        </button>
        <button
          onClick={() => setPalOpen(true)}
          className="ml-auto rounded-md p-1 text-ink hover:bg-paper"
          aria-label="Tìm kiếm (⌘K)"
        >
          <Search className="size-5" />
        </button>
        <Logo className="size-7" />
        <span className="text-sm font-semibold">Human Design Studio</span>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-10">{children}</main>
      <AssistantWidget />
    </div>
  );
}
