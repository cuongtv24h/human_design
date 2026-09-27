import type { ReactNode } from "react";
import Link from "next/link";
import { dailyRuntimeSlug, getRuntimeConcepts } from "@/lib/game/runtime";
import { fetchServerConfig } from "@/lib/game/server-config";
import FxBackground from "./_components/FxBackground";
import SoundToggle from "./_components/SoundToggle";

export default async function GameLayout({ children }: { children: ReactNode }) {
  const config = await fetchServerConfig();
  const dailySlug = dailyRuntimeSlug(getRuntimeConcepts(config));
  return (
    <div className="relative min-h-screen overflow-x-clip bg-[#14122b] text-white">
      <FxBackground />
      <header className="mx-auto flex max-w-3xl items-center justify-between px-4 py-4">
        <Link href="/" className="text-lg font-bold tracking-tight">
          🧭 Đúng Thiết Kế
        </Link>
        <nav className="hidden items-center gap-5 text-sm font-bold text-white/70 sm:flex">
          <Link href="/#bang-vang" className="transition hover:text-white">
            Bảng vàng
          </Link>
          <Link href="/#huy-hieu" className="transition hover:text-white">
            Huy hiệu
          </Link>
        </nav>
        <div className="flex items-center gap-2">
          <SoundToggle />
          <Link
            href={`/${dailySlug}?daily=1`}
            className="rounded-full bg-amber-300 px-4 py-2 text-sm font-bold text-[#14122b] hover:bg-amber-200"
          >
            Chơi ngay
          </Link>
        </div>
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
