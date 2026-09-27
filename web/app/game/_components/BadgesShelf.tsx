"use client";

import { useEffect, useState } from "react";
import { BADGES, getBadges, peekFreshBadges, type BadgeDef } from "@/lib/game/engine";

export function FreshBadges({ badges }: { badges: BadgeDef[] }) {
  if (badges.length === 0) return null;
  return (
    <div className="rounded-2xl border border-amber-300/40 bg-amber-300/10 p-4 text-center">
      <div className="text-sm font-black text-amber-200">🎖 Huy hiệu mới mở khóa!</div>
      <div className="mt-2 flex flex-wrap justify-center gap-2">
        {badges.map((b) => (
          <span
            key={b.id}
            className="rounded-full border border-amber-300/40 bg-[#14122b] px-3 py-1.5 text-sm font-bold"
          >
            {b.icon} {b.name}
          </span>
        ))}
      </div>
    </div>
  );
}

export default function BadgesShelf() {
  const [unlocked, setUnlocked] = useState<string[]>([]);
  const [fresh, setFresh] = useState<string[]>([]);
  useEffect(() => {
    setUnlocked(getBadges());
    setFresh(peekFreshBadges());
  }, []);
  return (
    <div>
      <h2 className="text-center text-2xl font-black">🎖 Tủ huy hiệu</h2>
      <p className="mt-1 text-center text-sm text-white/60">
        {unlocked.length}/{BADGES.length} đã mở · lưu trên máy này
      </p>
      <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-4">
        {BADGES.map((b) => {
          const has = unlocked.includes(b.id);
          const isNew = has && fresh.includes(b.id);
          return (
            <div
              key={b.id}
              className={`relative rounded-2xl border p-3 text-center ${
                has ? "border-amber-300/40 bg-amber-300/10" : "border-white/10 bg-white/5 opacity-55"
              }`}
            >
              {isNew && (
                <span className="absolute right-2 top-2 rounded-full bg-amber-300 px-2 text-[10px] font-black text-[#14122b]">
                  MỚI
                </span>
              )}
              <div className={`text-3xl ${has ? "" : "grayscale"}`}>{has ? b.icon : "🔒"}</div>
              <div className="mt-1 text-sm font-bold">{b.name}</div>
              <div className="text-xs text-white/50">{b.desc}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
