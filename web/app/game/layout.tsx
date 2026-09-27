import type { ReactNode } from "react";
import Link from "next/link";

export default function GameLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-[#14122b] text-white">
      <header className="mx-auto flex max-w-3xl items-center justify-between px-4 py-4">
        <Link href="/game" className="text-lg font-bold tracking-tight">
          🧭 Đúng Thiết Kế
        </Link>
        <nav className="hidden items-center gap-5 text-sm font-bold text-white/70 sm:flex">
          <Link href="/game#bang-vang" className="transition hover:text-white">
            Bảng vàng
          </Link>
          <Link href="/game" className="transition hover:text-white">
            Huy hiệu
          </Link>
        </nav>
        <Link
          href="/game"
          className="rounded-full bg-amber-300 px-4 py-2 text-sm font-bold text-[#14122b] hover:bg-amber-200"
        >
          Chơi ngay
        </Link>
      </header>
      <main className="mx-auto max-w-3xl px-4 pb-16">{children}</main>
      <footer className="border-t border-white/10 px-4 py-6 text-center text-xs leading-relaxed text-white/50">
        Trò chơi mô phỏng phong cách hành xử — không phải luận giải Human Design chính thức.
        <br />
        Thiết kế gốc của bạn chỉ được tính từ ngày giờ nơi sinh.
      </footer>
    </div>
  );
}
