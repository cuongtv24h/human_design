"use client";

import Link from "next/link";
import { getRuntimeConcepts, type GameServerConfig } from "@/lib/game/runtime";
import { useGameConfig } from "@/lib/game/use-game-config";

/** Lưới chọn concept — theo Game Manager (server), fallback TS khi offline. */
export default function ConceptGrid({ initial }: { initial: GameServerConfig | null }) {
  const { config } = useGameConfig();
  const concepts = getRuntimeConcepts(config ?? initial);
  const visible = concepts.filter((c) => c.enabled);
  const hidden = concepts.filter((c) => !c.enabled);

  return (
    <div>
      <p className="text-center text-xs font-bold uppercase tracking-widest text-amber-200">
        Chọn concept
      </p>
      <h2 className="mt-2 text-center text-2xl font-black sm:text-3xl">
        {visible.length > 1 ? `${visible.length} cánh cửa, ${visible.length} thế giới` : "Chọn thế giới của bạn"}
      </h2>
      <p className="mt-2 text-center text-sm text-white/60">
        Mỗi lượt rút ngẫu nhiên 16 câu từ kho của concept.
      </p>
      {visible.length === 0 && (
        <div className="mt-6 rounded-3xl border border-white/10 bg-white/[0.04] p-8 text-center">
          <div className="text-4xl">🚧</div>
          <p className="mt-2 font-bold">Game đang bảo trì, quay lại sau ít phút nhé.</p>
        </div>
      )}
      <div className="mt-6 grid gap-3">
        {visible.map((t) => (
          <Link
            key={t.slug}
            href={`/game/${t.slug}`}
            className="group rounded-3xl border border-white/10 bg-white/[0.04] p-6 transition hover:-translate-y-1 hover:border-amber-300/50 hover:bg-white/[0.06] sm:p-7"
          >
            <div className="flex items-center gap-5">
              <span className="flex size-16 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-white/15 to-white/5 text-4xl shadow-inner">
                {t.icon}
              </span>
              <div className="min-w-0 flex-1">
                <div className="text-xs font-bold uppercase tracking-widest text-amber-200">
                  {t.name} · {t.questionCount} tình huống
                </div>
                <div className="mt-0.5 text-xl font-black">{t.entryLabel}</div>
                <p className="mt-0.5 text-sm text-white/60">{t.entryDesc}</p>
              </div>
              <span className="shrink-0 rounded-full bg-amber-300 px-5 py-2.5 text-sm font-bold text-[#14122b] transition group-hover:bg-amber-200">
                Chơi →
              </span>
            </div>
          </Link>
        ))}
        {hidden.map((t) => (
          <div
            key={t.slug}
            className="rounded-3xl border border-white/10 bg-white/[0.02] p-6 opacity-60 sm:p-7"
          >
            <div className="flex items-center gap-5">
              <span className="text-4xl grayscale">{t.icon}</span>
              <div className="min-w-0 flex-1">
                <div className="text-xs font-bold uppercase tracking-widest text-white/40">
                  {t.name}
                </div>
                <p className="text-sm text-white/50">{t.entryDesc || "Concept này đang tạm đóng."}</p>
              </div>
              <span className="shrink-0 rounded-full border border-white/20 px-4 py-2 text-sm text-white/50">
                🔒 Tạm đóng
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
