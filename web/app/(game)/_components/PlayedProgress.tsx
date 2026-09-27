"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { STYLES } from "@/lib/game/content";
import { fetchStreak, getPlayed, type PlayedState, type StreakOut } from "@/lib/game/engine";
import { dailyRuntimeSlug, getRuntimeConcepts } from "@/lib/game/runtime";
import { useGameConfig } from "@/lib/game/use-game-config";

export default function PlayedProgress() {
  const { config } = useGameConfig();
  const [played, setPlayed] = useState<PlayedState | null>(null);
  const [streak, setStreak] = useState<StreakOut | null>(null);
  useEffect(() => {
    setPlayed(getPlayed());
    fetchStreak().then((s) => {
      if (s && s.streak > 0) setStreak(s);
    });
  }, []);
  const concepts = getRuntimeConcepts(config);
  const all = concepts.filter((c) => c.enabled);
  if (!played || played.themes.length === 0 || all.length === 0) return null;

  const next = all.find((t) => !played.themes.includes(t.slug));
  const last = played.lastStyle ? STYLES[played.lastStyle] : null;
  const dailySlug = dailyRuntimeSlug(concepts);

  return (
    <section className="space-y-2 rounded-2xl border border-amber-300/40 bg-gradient-to-r from-amber-300/15 to-transparent p-5">
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
            href={`/${next.slug}`}
            className="w-full rounded-full bg-amber-300 px-4 py-2 text-center text-sm font-bold text-[#14122b] hover:bg-amber-200 sm:w-auto sm:ml-auto"
          >
            Chơi tiếp: {next.entryLabel} →
          </Link>
        ) : (
          <Link
            href={`/${dailySlug}?daily=1`}
            className="w-full rounded-full bg-amber-300 px-4 py-2 text-center text-sm font-bold text-[#14122b] hover:bg-amber-200 sm:w-auto sm:ml-auto"
          >
            Cả {all.length} cửa xong 🎉 Luyện đề hôm nay →
          </Link>
        )}
      </div>
      {streak && (
        <div>
          <span className="rounded-full bg-amber-300/15 px-3 py-1 text-xs font-bold text-amber-200">
            🔥 Streak {streak.streak} ngày{!streak.today_done ? " · chơi đề hôm nay để giữ lửa" : ""}
          </span>
        </div>
      )}
    </section>
  );
}
