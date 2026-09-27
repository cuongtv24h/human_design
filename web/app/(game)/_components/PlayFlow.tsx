"use client";

import {
  AnimatePresence,
  motion,
  useMotionValue,
  useSpring,
  useTransform,
} from "framer-motion";
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
  type PlayOption,
  type PlayQuestion,
} from "@/lib/game/engine";
import { sfx } from "@/lib/game/sound";
import { COMBO_THRESHOLD_S, HELPERS_PER_NODE } from "@/lib/game/stages";

const LETTERS = ["A", "B", "C", "D"];

export interface PlayDoneInfo {
  weights: number[];
  maxCombo: number;
  helpersUsed: number;
}

const DOT_PATTERN = "radial-gradient(rgba(251,191,36,0.28) 1px, transparent 1.6px)";

/** 1 lá đáp án: phát bài 3D → lơ lửng → nghiêng theo tay → lật úp khi chọn. */
function AnswerCard({
  o,
  i,
  dim,
  isPicked,
  revealedStyle,
  onPick,
}: {
  o: PlayOption;
  i: number;
  dim: boolean;
  isPicked: boolean;
  revealedStyle: string | null;
  onPick: () => void;
}) {
  const mx = useMotionValue(0.5);
  const my = useMotionValue(0.5);
  const tiltX = useSpring(useTransform(my, [0, 1], [6, -6]), { stiffness: 260, damping: 18 });
  const tiltY = useSpring(useTransform(mx, [0, 1], [-8, 8]), { stiffness: 260, damping: 18 });
  return (
    <motion.button
      type="button"
      initial={{ opacity: 0, y: 110, rotateX: 55 }}
      animate={{
        opacity: dim ? 0.2 : 1,
        y: 0,
        rotateX: 0,
        rotateY: isPicked ? 180 : 0,
        scale: isPicked ? 1.03 : 1,
      }}
      transition={{
        rotateY: { duration: 0.45, ease: [0.3, 1.4, 0.5, 1] },
        default: { delay: 0.06 + i * 0.08, type: "spring", stiffness: 300, damping: 25 },
      }}
      whileTap={{ scale: 0.96 }}
      onPointerMove={(e) => {
        const r = e.currentTarget.getBoundingClientRect();
        mx.set((e.clientX - r.left) / r.width);
        my.set((e.clientY - r.top) / r.height);
      }}
      onPointerLeave={() => {
        mx.set(0.5);
        my.set(0.5);
      }}
      onClick={onPick}
      style={{ transformStyle: "preserve-3d", perspective: 900 }}
      className="relative block w-full text-left"
      aria-label={`Đáp án ${LETTERS[i] ?? i + 1}: ${o.label}`}
    >
      <motion.span
        animate={{ y: isPicked ? 0 : [0, -4, 0] }}
        transition={isPicked ? { duration: 0.2 } : { repeat: Infinity, duration: 2.6, delay: i * 0.35 }}
        style={{ rotateX: tiltX, rotateY: tiltY, transformStyle: "preserve-3d" }}
        className="relative block"
      >
        {/* mặt trước */}
        <span
          style={{ backfaceVisibility: "hidden" }}
          className="relative flex items-start gap-3 overflow-hidden rounded-2xl border border-amber-200/30 bg-gradient-to-br from-violet-900/90 via-[#232052] to-[#14122b] p-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.14),0_12px_32px_rgba(0,0,0,0.5)]"
        >
          <span
            aria-hidden
            style={{ backgroundImage: DOT_PATTERN, backgroundSize: "14px 14px" }}
            className="pointer-events-none absolute inset-0 opacity-25"
          />
          <span className="relative flex size-7 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-amber-200 to-amber-500 text-sm font-black text-[#14122b] shadow">
            {LETTERS[i] ?? i + 1}
          </span>
          <span className="relative min-w-0 flex-1">
            <span className="block text-[15px] font-medium leading-snug text-white">{o.label}</span>
            {revealedStyle && (
              <span className="mt-1.5 inline-block rounded-full bg-amber-300/20 px-2.5 py-0.5 text-xs font-bold text-amber-200">
                {revealedStyle}
              </span>
            )}
          </span>
        </span>
        {/* mặt sau: đã chọn */}
        <span
          style={{ backfaceVisibility: "hidden", transform: "rotateY(180deg)" }}
          className="absolute inset-0 flex items-center justify-center gap-2 overflow-hidden rounded-2xl border border-amber-300 bg-gradient-to-br from-amber-300 via-amber-400 to-orange-500 shadow-[0_0_36px_rgba(251,191,36,0.45)]"
        >
          <span
            aria-hidden
            style={{ backgroundImage: DOT_PATTERN, backgroundSize: "12px 12px" }}
            className="pointer-events-none absolute inset-0 opacity-30"
          />
          <span className="relative text-2xl font-black text-[#14122b]">✓ ĐÃ CHỌN</span>
        </span>
      </motion.span>
    </motion.button>
  );
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
  const expiredRef = useRef(false);

  useEffect(() => {
    qStart.current = Date.now();
    expiredRef.current = false;
    setDoubled(false);
    setRevealed(false);
    setPickedId(null);
    sfx.flip();
    if (!timeLimit) return;
    setLeft(timeLimit);
    const t0 = Date.now();
    const t = setInterval(() => {
      const remain = timeLimit - (Date.now() - t0) / 1000;
      if (remain <= 0) {
        setLeft(0);
        setCombo(0);
        if (!expiredRef.current) {
          expiredRef.current = true;
          sfx.timeout();
        }
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
    sfx.pick(nc);
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
    }, 480);
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
    sfx.click();
    setUsesLeft((u) => u - 1);
    setUsedCount((c) => c + 1);
  };

  const ring = timeLimit ? Math.max(0, left / timeLimit) : 0;
  const danger = !!timeLimit && left <= 3;
  const hot = combo >= 4;

  return (
    <div className="space-y-5">
      <div>
        <div className="mb-2 flex items-center justify-between gap-2 text-sm">
          <span className="font-bold text-white/70">
            {title ? `${title} · ` : ""}Câu {step + 1}/{queue.length}
          </span>
          <span className="flex items-center gap-2">
            <AnimatePresence mode="popLayout">
              {combo >= 2 && (
                <motion.span
                  key={combo}
                  initial={{ scale: 0.3, rotate: -10, opacity: 0 }}
                  animate={{ scale: 1, rotate: 0, opacity: 1 }}
                  exit={{ opacity: 0, scale: 0.5 }}
                  transition={{ type: "spring", stiffness: 500, damping: 16 }}
                  className={`rounded-full px-3 py-1 text-xs font-black ${
                    hot
                      ? "bg-gradient-to-r from-orange-500 to-amber-400 text-[#14122b] shadow-[0_0_20px_rgba(251,146,60,0.6)]"
                      : "bg-orange-500/25 text-orange-200"
                  }`}
                >
                  🔥 Combo ×{combo}
                </motion.span>
              )}
            </AnimatePresence>
            {timeLimit ? (
              <span
                className={`flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-black ${
                  danger ? "animate-shake bg-rose-500/30 text-rose-100" : "bg-white/10 text-white/80"
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
          className={`rounded-3xl border bg-white/5 p-6 sm:p-8 ${
            boss
              ? "border-rose-400/40"
              : hot
                ? "border-amber-300/60 shadow-[0_0_32px_rgba(251,191,36,0.25)]"
                : "border-white/10"
          }`}
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

      <div className="grid gap-3">
        {sc.options.map((o, i) => {
          const st = revealed ? optionStyle(o.id) : null;
          return (
            <AnswerCard
              key={o.id}
              o={o}
              i={i}
              dim={pickedId !== null && pickedId !== o.id}
              isPicked={pickedId === o.id}
              revealedStyle={st ? `${STYLES[st].icon} ${styleName(st)}` : null}
              onPick={() => pick(o.id)}
            />
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
