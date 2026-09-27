"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { STYLES, THEMES } from "@/lib/game/content";
import type { GameScoreOut } from "@/lib/types";

const MEDALS = ["🥇", "🥈", "🥉"];

export default function Leaderboard() {
  const slugs = Object.keys(THEMES);
  const [tab, setTab] = useState(slugs[0] ?? "");
  const [rows, setRows] = useState<GameScoreOut[] | null>(null);

  useEffect(() => {
    let alive = true;
    setRows(null);
    api
      .get<GameScoreOut[]>(`/public/game/scores?theme=${tab}&limit=5`)
      .then(
        (r) => {
          if (alive) setRows(r);
        },
        () => {
          if (alive) setRows([]);
        },
      );
    return () => {
      alive = false;
    };
  }, [tab]);

  return (
    <div>
      <h2 className="text-center text-2xl font-black">🏆 Bảng vàng tuần này</h2>
      <p className="mt-1 text-center text-sm text-white/60">
        Độ lệch càng thấp, sống càng đúng thiết kế — ẩn danh hoàn toàn
      </p>
      <div className="mt-4 flex flex-wrap justify-center gap-2">
        {Object.values(THEMES).map((t) => (
          <button
            key={t.slug}
            type="button"
            onClick={() => setTab(t.slug)}
            className={`rounded-full px-4 py-2 text-sm font-bold ${
              tab === t.slug ? "bg-amber-300 text-[#14122b]" : "border border-white/20 hover:bg-white/10"
            }`}
          >
            {t.icon} {t.name}
          </button>
        ))}
      </div>
      <div className="mx-auto mt-3 max-w-md space-y-1.5">
        {rows === null ? (
          <p className="rounded-2xl border border-white/10 bg-white/5 p-5 text-center text-sm text-white/50">
            Đang tải bảng vàng…
          </p>
        ) : rows.length === 0 ? (
          <p className="rounded-2xl border border-white/10 bg-white/5 p-5 text-center text-sm text-white/60">
            Chưa có ai ghi danh — đối chiếu xong, bạn có thể là người đầu tiên.
          </p>
        ) : (
          rows.map((r, i) => {
            const st = (STYLES as Record<string, { icon: string; name: string }>)[r.style];
            return (
              <div
                key={`${r.created_at}-${i}`}
                className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-2.5"
              >
                <span className="w-7 text-center font-black">{MEDALS[i] ?? `#${i + 1}`}</span>
                <span className="text-2xl">{st?.icon ?? "✨"}</span>
                <span className="flex-1 text-sm font-bold">{st?.name ?? "Ẩn danh"}</span>
                <span className="text-sm font-black text-amber-200">lệch {r.deviation}%</span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
