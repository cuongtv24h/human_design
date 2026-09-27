"use client";

import { useEffect, useState } from "react";
import {
  NODES_PER_CHAPTER,
  buildNodes,
  getChapters,
  getProgress,
  modeMeta,
  type StageNode,
  type WorldProgress,
} from "@/lib/game/stages";
import type { RuntimeConcept } from "@/lib/game/runtime";

function Stars({ n }: { n: number }) {
  return (
    <span className="text-[11px] leading-none tracking-tight" aria-label={`${n}/3 sao`}>
      {[0, 1, 2].map((i) => (
        <span key={i} className={i < n ? "" : "opacity-25 grayscale"}>
          ⭐
        </span>
      ))}
    </span>
  );
}

/** Bản đồ thế giới kiểu Mario: chương → màn, màn khóa/mở theo tiến trình. */
export default function WorldMap({
  concept,
  nodeCount,
  tick,
  onPlay,
}: {
  concept: RuntimeConcept;
  nodeCount: number;
  /** tăng mỗi khi xong 1 màn để vẽ lại tiến trình */
  tick: number;
  onPlay: (node: StageNode) => void;
}) {
  const [progress, setProgress] = useState<WorldProgress>({ unlocked: 0, stars: {} });
  useEffect(() => {
    setProgress(getProgress(concept.slug));
  }, [concept.slug, tick]);
  if (nodeCount <= 0) return null;

  const chapters = getChapters(concept.slug);
  const nodes = buildNodes(nodeCount);
  const total = Object.values(progress.stars).reduce((a, b) => a + b, 0);

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-black sm:text-2xl">🗺️ Bản đồ {concept.name}</h2>
        <span className="rounded-full bg-amber-300/15 px-3 py-1 text-xs font-black text-amber-200">
          ⭐ {total}/{nodeCount * 3}
        </span>
      </div>
      {chapters.map((ch, ci) => {
        const ns = nodes.filter((n) => n.chapter === ci);
        if (ns.length === 0) return null;
        return (
          <section key={ci} className="rounded-3xl border border-white/10 bg-white/[0.03] p-4 sm:p-5">
            <div className="flex items-center gap-3">
              <span className="flex size-11 shrink-0 items-center justify-center rounded-2xl bg-white/10 text-2xl">
                {ch.icon}
              </span>
              <div className="min-w-0">
                <div className="text-xs font-bold uppercase tracking-widest text-amber-200">
                  Chương {ci + 1}
                </div>
                <div className="font-black">{ch.name}</div>
              </div>
            </div>
            <p className="mt-1.5 text-xs text-white/55">{ch.desc}</p>
            <div className="mt-3 flex items-stretch gap-1.5">
              {ns.map((n, k) => {
                const locked = n.index > progress.unlocked;
                const stars = progress.stars[String(n.index)] ?? 0;
                const isCurrent = n.index === progress.unlocked;
                const meta = modeMeta(n.mode);
                return (
                  <div key={n.index} className="flex min-w-0 flex-1 items-center gap-1.5">
                    {k > 0 && (
                      <span
                        aria-hidden
                        className={`h-0.5 min-w-2 flex-1 rounded-full sm:min-w-4 ${
                          n.index <= progress.unlocked ? "bg-amber-300/70" : "bg-white/10"
                        }`}
                      />
                    )}
                    <button
                      type="button"
                      disabled={locked}
                      onClick={() => onPlay(n)}
                      title={locked ? `Hoàn thành Màn ${n.index} để mở` : `${meta.label} · Màn ${n.index + 1}`}
                      className={`flex min-w-0 flex-1 flex-col items-center gap-1 rounded-2xl border px-1 py-3 transition ${
                        locked
                          ? "border-white/10 bg-white/[0.02] opacity-50"
                          : n.mode === "boss"
                            ? "border-rose-400/50 bg-rose-500/10 hover:-translate-y-0.5 hover:bg-rose-500/20"
                            : "border-white/15 bg-white/5 hover:-translate-y-0.5 hover:border-amber-300/50"
                      } ${isCurrent && stars === 0 ? "animate-pulse border-amber-300/60" : ""}`}
                    >
                      <span className="text-2xl">
                        {locked ? "🔒" : n.mode === "normal" ? `${n.index + 1}️⃣` : meta.icon}
                      </span>
                      <span className="text-[11px] font-black">
                        {n.mode === "boss" ? "TRÙM" : n.mode === "speed" ? "⚡ Màn " + (n.index + 1) : "Màn " + (n.index + 1)}
                      </span>
                      {!locked && <Stars n={stars} />}
                    </button>
                  </div>
                );
              })}
              {Array.from({ length: NODES_PER_CHAPTER - ns.length }).map((_, k) => (
                <span key={`pad-${k}`} aria-hidden className="min-w-0 flex-1" />
              ))}
            </div>
          </section>
        );
      })}
    </div>
  );
}
