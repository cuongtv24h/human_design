"use client";

import { AnimatePresence, motion } from "framer-motion";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { BANKS, type BankQuestion } from "@/lib/game/bank";
import { STYLES, type GameTheme } from "@/lib/game/content";
import {
  QUESTIONS_PER_PLAY,
  optionStyle,
  sampleQuestions,
  styleName,
  toPlayQuestion,
  type PlayQuestion,
} from "@/lib/game/engine";
import { COMBO_THRESHOLD_S, HELPERS_PER_NODE } from "@/lib/game/stages";

const LETTERS = ["A", "B", "C", "D"];

export interface PlayDoneInfo {
  weights: number[];
  maxCombo: number;
  helpersUsed: number;
}

/** Luồng trả lời dạng lá bài — dùng chung cho màn, chơi tự do, đề hôm nay và so bài. */
export default function PlayFlow({
  theme,
  seed,
  bank,
  questions,
  count = QUESTIONS_PER_PLAY,
  timeLimit,
  helpers = false,
  helperUses = HELPERS_PER_NODE,
  boss = false,
  title,
  onDone,
}: {
  theme: GameTheme;
  seed: string;
  /** Kho runtime (built-in đã lọc + custom) — thiếu thì dùng kho TS. */
  bank?: BankQuestion[];
  /** Set câu cố định của màn — có thì bỏ qua sampling. */
  questions?: PlayQuestion[];
  count?: number;
  /** Giây/câu (màn tốc độ/trùm) — hết giờ chỉ đứt combo, không ép đáp án. */
  timeLimit?: number;
  helpers?: boolean;
  helperUses?: number;
  boss?: boolean;
  title?: string;
  onDone: (answers: string[], info: PlayDoneInfo) => void;
}) {
  const fullBank = bank ?? BANKS[theme.slug] ?? [];
  const asked = useRef<Set<string>>(new Set());
  const [queue, setQueue] = useState<PlayQuestion[]>(() => {
    const q = questions ?? sampleQuestions(theme.slug, seed, count, bank);
    asked.current = new Set(q.map((x) => x.qid));
    return q;
  });
  const [step, setStep] = useState(0);
  const [round, setRound] = useState(0);
  const [answers, setAnswers] = useState<string[]>([]);
  const [weights, setWeights] = useState<number[]>([]);
  const [combo, setCombo] = useState(0);
  const [maxCombo, setMaxCombo] = useState(0);
  const [left, setLeft] = useState(timeLimit ?? 0);
  const [usesLeft, setUsesLeft] = useState(helperUses);
  const [usedCount, setUsedCount] = useState(0);
  const [doubled, setDoubled] = useState(false);
  const [revealed, setRevealed] = useState(false);
  const [pickedId, setPickedId] = useState<string | null>(null);
  const qStart = useRef(0);
  const doneRef = useRef(false);

  useEffect(() => {
    qStart.current = Date.now();
    setDoubled(false);
    setRevealed(false);
    setPickedId(null);
    if (!timeLimit) return;
    setLeft(timeLimit);
    const t0 = Date.now();
    const t = setInterval(() => {
      const remain = timeLimit - (Date.now() - t0) / 1000;
      if (remain <= 0) {
        setLeft(0);
        setCombo(0);
        clearInterval(t);
      } else {
        setLeft(remain);
      }
    }, 100);
    return () => clearInterval(t);
  }, [step, round, timeLimit]);

  if (queue.length === 0) {
    return (
      <div className="rounded-3xl border border-white/10 bg-white/5 p-10 text-center">
        <div className="text-5xl">🚧</div>
        <h1 className="mt-4 text-2xl font-black">Kho câu hỏi đang cập nhật</h1>
        <p className="mt-2 text-white/60">Quay lại sau ít phút nhé.</p>
        <Link
          href="/"
          className="mt-6 inline-block rounded-full bg-amber-300 px-6 py-3 font-bold text-[#14122b]"
        >
          ← Về trang chủ
        </Link>
      </div>
    );
  }

  const sc = queue[step];
  if (!sc) return null;

  const pick = (id: string) => {
    if (pickedId) return;
    setPickedId(id);
    const elapsed = (Date.now() - qStart.current) / 1000;
    const nc = elapsed < COMBO_THRESHOLD_S ? combo + 1 : 0;
    setCombo(nc);
    const nm = Math.max(maxCombo, nc);
    setMaxCombo(nm);
    const w = doubled ? 2 : 1;
    setTimeout(() => {
      const nextA = [...answers, id];
      const nextW = [...weights, w];
      setAnswers(nextA);
      setWeights(nextW);
      if (step + 1 >= queue.length) {
        if (!doneRef.current) {
          doneRef.current = true;
          onDone(nextA, { weights: nextW, maxCombo: nm, helpersUsed: usedCount });
        }
      } else {
        setStep(step + 1);
      }
    }, 280);
  };

  const useHelper = (kind: "swap" | "reveal" | "double") => {
    if (usesLeft <= 0 || pickedId) return;
    if (kind === "double") {
      if (doubled) return;
      setDoubled(true);
    } else if (kind === "reveal") {
      if (revealed) return;
      setRevealed(true);
    } else {
      const fresh = fullBank.filter((q) => !asked.current.has(q.id));
      if (fresh.length === 0) return;
      const nq = fresh[Math.floor(Math.random() * fresh.length)];
      asked.current.add(nq.id);
      const pq = toPlayQuestion(theme.slug, `${seed}:swap:${step}:${nq.id}`, nq);
      setQueue((qq) => qq.map((x, i) => (i === step ? pq : x)));
      setRound((r) => r + 1);
    }
    setUsesLeft((u) => u - 1);
    setUsedCount((c) => c + 1);
  };

  const ring = timeLimit ? Math.max(0, left / timeLimit) : 0;
  const danger = !!timeLimit && left <= 3;

  return (
    <div className="space-y-5">
      <div>
        <div className="mb-2 flex items-center justify-between gap-2 text-sm">
          <span className="font-bold text-white/70">
            {title ? `${title} · ` : ""}Câu {step + 1}/{queue.length}
          </span>
          <span className="flex items-center gap-2">
            <AnimatePresence>
              {combo >= 2 && (
                <motion.span
                  key={combo}
                  initial={{ scale: 0.4, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="rounded-full bg-orange-500/25 px-3 py-1 text-xs font-black text-orange-200"
                >
                  🔥 Combo ×{combo}
                </motion.span>
              )}
            </AnimatePresence>
            {timeLimit ? (
              <span
                className={`flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-black ${
                  danger ? "bg-rose-500/25 text-rose-200" : "bg-white/10 text-white/80"
                }`}
              >
                <svg viewBox="0 0 20 20" className="size-4 -rotate-90">
                  <circle cx="10" cy="10" r="8" fill="none" stroke="currentColor" strokeOpacity="0.25" strokeWidth="3" />
                  <circle
                    cx="10"
                    cy="10"
                    r="8"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeDasharray={2 * Math.PI * 8}
                    strokeDashoffset={2 * Math.PI * 8 * (1 - ring)}
                  />
                </svg>
                {Math.ceil(left)}s
              </span>
            ) : null}
          </span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-white/10">
          <div
            className={`h-full rounded-full transition-all ${boss ? "bg-gradient-to-r from-rose-400 to-amber-300" : "bg-amber-300"}`}
            style={{ width: `${Math.round(((step + 1) / queue.length) * 100)}%` }}
          />
        </div>
      </div>

      {boss && (
        <p className="rounded-2xl border border-rose-400/40 bg-rose-500/10 p-3 text-center text-sm font-black text-rose-200">
          👹 TRÙM CUỐI CHƯƠNG — {timeLimit}s mỗi câu, giữ combo để hạ nó!
        </p>
      )}

      <AnimatePresence mode="wait">
        <motion.div
          key={`${step}-${round}`}
          initial={{ opacity: 0, x: 48 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -48 }}
          transition={{ duration: 0.22 }}
          className="rounded-3xl border border-white/10 bg-white/5 p-6 sm:p-8"
        >
          <div className="flex items-start justify-between gap-2">
            <h1 className="text-xl font-black sm:text-2xl">{sc.title}</h1>
            {doubled && (
              <span className="shrink-0 rounded-full bg-amber-300 px-2.5 py-1 text-xs font-black text-[#14122b]">
                ×2 điểm
              </span>
            )}
          </div>
          <p className="mt-2 leading-relaxed text-white/80">{sc.situation}</p>
        </motion.div>
      </AnimatePresence>

      <div className="grid gap-2 [perspective:900px]">
        {sc.options.map((o, i) => {
          const st = revealed ? optionStyle(o.id) : null;
          const isPicked = pickedId === o.id;
          const dim = pickedId !== null && !isPicked;
          return (
            <motion.button
              key={o.id}
              type="button"
              initial={{ opacity: 0, y: 20, rotateX: 50 }}
              animate={{
                opacity: dim ? 0.35 : 1,
                y: 0,
                rotateX: 0,
                scale: isPicked ? 1.03 : 1,
              }}
              transition={{ delay: 0.05 + i * 0.06, type: "spring", stiffness: 320, damping: 24 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => pick(o.id)}
              style={{ transformStyle: "preserve-3d" }}
              className={`flex items-start gap-3 rounded-2xl border bg-white/5 p-4 text-left ${
                isPicked
                  ? "border-amber-300 bg-amber-300/15 shadow-lg shadow-amber-300/20"
                  : "border-white/10 hover:border-amber-300/60 hover:bg-white/10"
              }`}
            >
              <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-white/10 text-sm font-black">
                {LETTERS[i] ?? i + 1}
              </span>
              <span className="min-w-0 flex-1">
                <span className="block text-[15px] leading-snug">{o.label}</span>
                {st && (
                  <span className="mt-1.5 inline-block rounded-full bg-white/10 px-2.5 py-0.5 text-xs font-bold text-amber-200">
                    {STYLES[st].icon} {styleName(st)}
                  </span>
                )}
              </span>
            </motion.button>
          );
        })}
      </div>

      {helpers && (
        <div className="flex flex-wrap items-center gap-2 rounded-2xl border border-white/10 bg-white/[0.03] p-3">
          <span className="mr-auto text-xs font-bold text-white/50">
            🃏 Thẻ trợ giúp · còn {usesLeft} lượt
          </span>
          <button
            type="button"
            disabled={usesLeft <= 0 || !!pickedId}
            onClick={() => useHelper("swap")}
            title="Đổi sang câu khác"
            className="rounded-full border border-white/15 px-3.5 py-2 text-xs font-bold hover:bg-white/10 disabled:opacity-40"
          >
            🔄 Đổi câu
          </button>
          <button
            type="button"
            disabled={usesLeft <= 0 || revealed || !!pickedId}
            onClick={() => useHelper("reveal")}
            title="Tiết lộ phong cách của 4 đáp án"
            className="rounded-full border border-white/15 px-3.5 py-2 text-xs font-bold hover:bg-white/10 disabled:opacity-40"
          >
            🪞 Soi gương
          </button>
          <button
            type="button"
            disabled={usesLeft <= 0 || doubled || !!pickedId}
            onClick={() => useHelper("double")}
            title="Câu này nhân đôi điểm"
            className="rounded-full border border-white/15 px-3.5 py-2 text-xs font-bold hover:bg-white/10 disabled:opacity-40"
          >
            ✖️2 Nhân đôi
          </button>
        </div>
      )}
    </div>
  );
}
