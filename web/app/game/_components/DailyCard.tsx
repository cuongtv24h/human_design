"use client";

import Link from "next/link";
import { dailyLabel } from "@/lib/game/engine";
import {
  dailyRuntimeSlug,
  getRuntimeConcepts,
  type GameServerConfig,
} from "@/lib/game/runtime";
import { useGameConfig } from "@/lib/game/use-game-config";

/** Thẻ đề hôm nay — xoay vòng trên concept đang bật theo Game Manager. */
export default function DailyCard({ initial }: { initial: GameServerConfig | null }) {
  const { config } = useGameConfig();
  const concepts = getRuntimeConcepts(config ?? initial);
  const slug = dailyRuntimeSlug(concepts);
  const daily = concepts.find((c) => c.slug === slug) ?? concepts[0];
  if (!daily) return null;
  const label = dailyLabel();
  return (
    <Link
      href={`/game/${daily.slug}?daily=1`}
      className="group block overflow-hidden rounded-3xl border border-amber-300/40 bg-gradient-to-r from-amber-300/20 via-amber-300/10 to-transparent p-6 transition hover:-translate-y-0.5 hover:border-amber-300 sm:p-7"
    >
      <div className="flex items-center gap-4">
        <span className="flex size-14 shrink-0 items-center justify-center rounded-2xl bg-amber-300 text-3xl shadow-lg shadow-amber-300/25">
          📅
        </span>
        <div className="min-w-0 flex-1">
          <div className="text-xs font-bold uppercase tracking-widest text-amber-200">
            Đề hôm nay · {label} · cả cộng đồng cùng 16 câu
          </div>
          <div className="mt-0.5 text-lg font-black sm:text-xl">
            {daily.icon} {daily.name}: {daily.entryLabel}
          </div>
          <p className="mt-0.5 text-sm text-white/60">
            Chơi xong đối chiếu để ghi tên lên bảng vàng và giữ streak.
          </p>
        </div>
        <span className="hidden shrink-0 rounded-full bg-amber-300 px-5 py-2.5 text-sm font-bold text-[#14122b] transition group-hover:bg-amber-200 sm:block">
          Chơi →
        </span>
      </div>
    </Link>
  );
}
