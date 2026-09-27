"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { STYLES, THEMES } from "@/lib/game/content";
import { dailyTheme, getPlayed, type PlayedState } from "@/lib/game/engine";

export default function PlayedProgress() {
  const [played, setPlayed] = useState<PlayedState | null>(null);
  useEffect(() => {
    setPlayed(getPlayed());
  }, []);
  if (!played || played.themes.length === 0) return null;

  const all = Object.values(THEMES);
  const next = all.find((t) => !played.themes.includes(t.slug));
  const last = played.lastStyle ? STYLES[played.lastStyle] : null;
  const daily = dailyTheme();

  return (
    <section className="rounded-2xl border border-amber-300/40 bg-gradient-to-r from-amber-300/15 to-transparent p-5">
      <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
        <div className="text-sm">
          <span className="font-black">
            Đã chơi {played.themes.length}/{all.length} cửa
          </span>
          {last && <span className="text-white/60"> · lần trước bạn là {last.icon} {last.name}</span>}
        </div>
        <div className="flex gap-1.5">
          {all.map((t) => (
            <span
              key={t.slug}
              title={t.name}
              className={`text-2xl ${played.themes.includes(t.slug) ? "" : "opacity-25 grayscale"}`}
            >
              {t.icon}
            </span>
          ))}
        </div>
        {next ? (
          <Link
            href={`/choi/${next.slug}`}
            className="ml-auto rounded-full bg-amber-300 px-4 py-2 text-sm font-bold text-[#14122b] hover:bg-amber-200"
          >
            Chơi tiếp: {next.entryLabel} →
          </Link>
        ) : (
          <Link
            href={`/choi/${daily.slug}?daily=1`}
            className="ml-auto rounded-full bg-amber-300 px-4 py-2 text-sm font-bold text-[#14122b] hover:bg-amber-200"
          >
            Cả 3 cửa xong 🎉 Luyện đề hôm nay →
          </Link>
        )}
      </div>
    </section>
  );
}
