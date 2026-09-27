"use client";

import Link from "next/link";
import { useState } from "react";
import type { BankQuestion } from "@/lib/game/bank";
import type { GameTheme } from "@/lib/game/content";
import { QUESTIONS_PER_PLAY, sampleQuestions } from "@/lib/game/engine";

const LETTERS = ["A", "B", "C", "D"];

/** Luồng trả lời 16 câu rút từ kho (dùng chung cho chơi thường, đề hôm nay và so bài). */
export default function PlayFlow({
  theme,
  seed,
  bank,
  onDone,
}: {
  theme: GameTheme;
  seed: string;
  /** Kho runtime (built-in đã lọc + custom) — thiếu thì dùng kho TS. */
  bank?: BankQuestion[];
  onDone: (answers: string[]) => void;
}) {
  const [picked] = useState(() => sampleQuestions(theme.slug, seed, QUESTIONS_PER_PLAY, bank));
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<string[]>([]);

  if (picked.length === 0) {
    return (
      <div className="rounded-3xl border border-white/10 bg-white/5 p-10 text-center">
        <div className="text-5xl">🚧</div>
        <h1 className="mt-4 text-2xl font-black">Kho câu hỏi đang cập nhật</h1>
        <p className="mt-2 text-white/60">Quay lại sau ít phút nhé.</p>
        <Link
          href="/"
          className="mt-6 inline-block rounded-full bg-amber-300 px-6 py-3 font-bold text-[#14122b]"
        >
          ← Chọn cửa khác
        </Link>
      </div>
    );
  }

  const sc = picked[step];
  if (!sc) return null;
  const half = Math.floor(picked.length / 2);

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
            Câu {step + 1}/{picked.length}
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
        {step === half && (
          <p className="mt-2 text-center text-sm font-bold text-amber-200">
            Được nửa đường rồi — cứ theo phản xạ đầu tiên nhé 💪
          </p>
        )}
      </div>

      <div className="rounded-3xl border border-white/10 bg-white/5 p-6 sm:p-8">
        <h1 className="text-xl font-black sm:text-2xl">{sc.title}</h1>
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
