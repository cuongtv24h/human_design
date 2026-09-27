"use client";

import { useState } from "react";
import type { GameTheme } from "@/lib/game/content";
import { pickVariants } from "@/lib/game/engine";

const LETTERS = ["A", "B", "C", "D"];

/** Luồng trả lời câu hỏi (dùng chung cho chơi thường và so bài). */
export default function PlayFlow({
  theme,
  onDone,
}: {
  theme: GameTheme;
  onDone: (answers: string[]) => void;
}) {
  const [picked] = useState(() => pickVariants(theme));
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<string[]>([]);
  const sc = picked[step];
  if (!sc) return null;

  const pick = (id: string) => {
    const next = [...answers];
    next[step] = id;
    setAnswers(next);
    if (step + 1 >= picked.length) onDone(next);
    else setStep(step + 1);
  };

  return (
    <div className="space-y-5">
      <div>
        <div className="mb-2 flex items-center justify-between text-sm">
          <span className="font-bold text-white/70">
            Tình huống {step + 1}/{picked.length}
          </span>
          {step > 0 && (
            <button
              type="button"
              onClick={() => setStep(step - 1)}
              className="text-white/50 hover:text-white"
            >
              ← Câu trước
            </button>
          )}
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-white/10">
          <div
            className="h-full rounded-full bg-amber-300 transition-all"
            style={{ width: `${Math.round(((step + 1) / picked.length) * 100)}%` }}
          />
        </div>
      </div>

      <div className="rounded-3xl border border-white/10 bg-white/5 p-6 sm:p-8">
        <h1 className="text-2xl font-black">{sc.title}</h1>
        <p className="mt-2 leading-relaxed text-white/80">{sc.situation}</p>
      </div>

      <div className="grid gap-2">
        {sc.options.map((o, i) => (
          <button
            key={o.id}
            type="button"
            onClick={() => pick(o.id)}
            className="flex items-start gap-3 rounded-2xl border border-white/10 bg-white/5 p-4 text-left hover:border-amber-300/60 hover:bg-white/10"
          >
            <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-white/10 text-sm font-black">
              {LETTERS[i] ?? i + 1}
            </span>
            <span className="text-[15px] leading-snug">{o.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
