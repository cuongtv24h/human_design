"use client";

import confetti from "canvas-confetti";
import { motion } from "framer-motion";
import Link from "next/link";
import { useParams, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
import { STYLES } from "@/lib/game/content";
import {
  checkPlayBadges,
  dailyLabel,
  dailySeed,
  encodeResult,
  QUESTIONS_PER_PLAY,
  randomSeed,
  recordPlayed,
  scoreQuiz,
  submitStreak,
  takeFreshBadges,
  toPlayQuestion,
  trackGameEvent,
  type BadgeDef,
} from "@/lib/game/engine";
import {
  getRuntimeBank,
  getRuntimeTheme,
  isBuiltinSlug,
  toGameTheme,
} from "@/lib/game/runtime";
import {
  BOSS_TIME_LIMIT_S,
  SPEED_TIME_LIMIT_S,
  buildNodes,
  completeNode,
  modeMeta,
  nodeBank,
  nodeCountFor,
  starsFor,
  type StageNode,
} from "@/lib/game/stages";
import { useGameConfig } from "@/lib/game/use-game-config";
import { FreshBadges } from "../_components/BadgesShelf";
import PlayFlow, { type PlayDoneInfo } from "../_components/PlayFlow";
import WorldMap from "../_components/WorldMap";
import { ShareRow, StyleCard } from "../_components/cards";

type Mode = { kind: "free"; daily: boolean } | { kind: "node"; node: StageNode };

export default function PlayPage() {
  const { theme: slug } = useParams<{ theme: string }>();
  const params = useSearchParams();
  const dailyParam = params.get("daily") === "1";
  const preview = params.get("preview") === "1";
  const { config, ready } = useGameConfig();
  const runtime = useMemo(() => getRuntimeTheme(slug, config), [slug, config]);
  const theme = useMemo(() => (runtime ? toGameTheme(runtime) : undefined), [runtime]);
  const bank = useMemo(() => getRuntimeBank(slug, config), [slug, config]);
  const totalNodes = useMemo(() => nodeCountFor(bank.length), [bank]);
  const nodes = useMemo(() => buildNodes(totalNodes), [totalNodes]);

  const [phase, setPhase] = useState<"map" | "playing" | "done">(dailyParam ? "playing" : "map");
  const [mode, setMode] = useState<Mode>({ kind: "free", daily: dailyParam });
  const [playSeed, setPlaySeed] = useState("");
  const [answers, setAnswers] = useState<string[]>([]);
  const [weights, setWeights] = useState<number[]>([]);
  const [info, setInfo] = useState<PlayDoneInfo>({ weights: [], maxCombo: 0, helpersUsed: 0 });
  const [stars, setStars] = useState(0);
  const [tick, setTick] = useState(0);
  const [streak, setStreak] = useState(0);
  const [fresh, setFresh] = useState<BadgeDef[]>([]);
  const started = useRef(false);

  const freeSeed = useMemo(
    () => (mode.kind === "free" && mode.daily ? `${dailySeed()}-${slug}` : playSeed),
    [mode, playSeed, slug],
  );
  const nodeQuestions = useMemo(() => {
    if (mode.kind !== "node" || !theme) return undefined;
    return nodeBank(bank, mode.node.index).map((q) =>
      toPlayQuestion(theme.slug, `${theme.slug}:node:${mode.node.index}`, q),
    );
  }, [mode, bank, theme]);

  useEffect(() => {
    if (dailyParam && theme && !started.current) {
      started.current = true;
      trackGameEvent("game_start", theme.slug);
    }
  }, [dailyParam, theme]);

  const result = useMemo(
    () => (theme && phase === "done" ? scoreQuiz(theme, answers, weights) : null),
    [theme, phase, answers, weights],
  );
  const code = useMemo(() => {
    if (!result) return "";
    const seed = mode.kind === "free" ? freeSeed || undefined : undefined;
    return encodeResult({ ...result, seed });
  }, [result, mode, freeSeed]);

  if (!runtime && !isBuiltinSlug(slug) && !ready) {
    return <p className="py-16 text-center text-white/60">Đang tải…</p>;
  }

  if (!theme || !runtime) {
    return (
      <div className="rounded-3xl border border-white/10 bg-white/5 p-10 text-center">
        <div className="text-5xl">🔒</div>
        <h1 className="mt-4 text-2xl font-black">Cửa này sắp mở</h1>
        <p className="mt-2 text-white/60">Theme này đang được soạn. Chơi theme khác trước nhé.</p>
        <Link
          href="/"
          className="mt-6 inline-block rounded-full bg-amber-300 px-6 py-3 font-bold text-[#14122b]"
        >
          ← Trang chủ
        </Link>
      </div>
    );
  }

  if (!preview && !runtime.enabled) {
    return (
      <div className="rounded-3xl border border-white/10 bg-white/5 p-10 text-center">
        <div className="text-5xl">🚧</div>
        <h1 className="mt-4 text-2xl font-black">{runtime.name} đang bảo trì</h1>
        <p className="mt-2 text-white/60">Concept này tạm đóng. Chơi concept khác trước nhé.</p>
        <Link
          href="/"
          className="mt-6 inline-block rounded-full bg-amber-300 px-6 py-3 font-bold text-[#14122b]"
        >
          ← Trang chủ
        </Link>
      </div>
    );
  }

  const startFree = (d: boolean) => {
    setMode({ kind: "free", daily: d });
    setPlaySeed(d ? `${dailySeed()}-${theme.slug}` : randomSeed());
    setAnswers([]);
    setWeights([]);
    trackGameEvent("game_start", theme.slug);
    setPhase("playing");
  };

  const startNode = (node: StageNode) => {
    setMode({ kind: "node", node });
    setAnswers([]);
    setWeights([]);
    trackGameEvent("game_start", theme.slug);
    setPhase("playing");
  };

  const handleDone = async (a: string[], inf: PlayDoneInfo) => {
    setAnswers(a);
    setWeights(inf.weights);
    setInfo(inf);
    const r = scoreQuiz(theme, a, inf.weights);
    recordPlayed(theme.slug, r.style);
    let n = 0;
    if (mode.kind === "free" && mode.daily) {
      const s = await submitStreak();
      n = s?.streak ?? 0;
      setStreak(n);
    }
    if (mode.kind === "node") {
      const st = starsFor(inf.maxCombo, inf.helpersUsed);
      setStars(st);
      const res = completeNode(runtime.slug, mode.node.index, st);
      setTick((t) => t + 1);
      if (res.newUnlock || st >= 3) {
        confetti({ particleCount: 90, spread: 75, origin: { y: 0.6 } });
      }
    }
    checkPlayBadges({ daily: mode.kind === "free" && mode.daily, streak: n });
    setFresh(takeFreshBadges());
    trackGameEvent("game_complete", theme.slug);
    setPhase("done");
  };

  if (phase === "map") {
    if (bank.length === 0) {
      return (
        <div className="rounded-3xl border border-white/10 bg-white/5 p-10 text-center">
          <div className="text-5xl">🚧</div>
          <h1 className="mt-4 text-2xl font-black">Kho câu hỏi đang cập nhật</h1>
          <p className="mt-2 text-white/60">Quay lại sau ít phút nhé.</p>
          <Link
            href="/"
            className="mt-6 inline-block rounded-full bg-amber-300 px-6 py-3 font-bold text-[#14122b]"
          >
            ← Trang chủ
          </Link>
        </div>
      );
    }
    return (
      <div className="space-y-6">
        <div className="rounded-3xl border border-white/10 bg-white/5 p-6 text-center sm:p-8">
          <div className="text-5xl sm:text-6xl">{theme.icon}</div>
          <p className="mt-3 text-xs font-bold uppercase tracking-widest text-amber-200">
            {theme.name}
          </p>
          <h1 className="mt-1 text-2xl font-black sm:text-3xl">{theme.entryLabel}</h1>
          <p className="mx-auto mt-2 max-w-md text-sm text-white/70">{theme.intro}</p>
          <div className="mx-auto mt-5 flex max-w-md flex-col gap-2 sm:flex-row">
            <button
              type="button"
              onClick={() => startFree(false)}
              className="flex-1 rounded-full bg-amber-300 px-6 py-3.5 font-black text-[#14122b] hover:bg-amber-200"
            >
              🎲 Chơi tự do · {QUESTIONS_PER_PLAY} câu
            </button>
            <button
              type="button"
              onClick={() => startFree(true)}
              className="flex-1 rounded-full border border-white/20 px-6 py-3.5 text-sm font-bold hover:bg-white/10"
            >
              📅 Đề hôm nay · {dailyLabel()}
            </button>
          </div>
        </div>
        <WorldMap concept={runtime} nodeCount={totalNodes} tick={tick} onPlay={startNode} />
        <p className="text-center">
          <Link href="/" className="text-sm font-bold text-white/60 hover:text-white">
            ← Trang chủ
          </Link>
        </p>
      </div>
    );
  }

  if (phase === "playing") {
    const isNode = mode.kind === "node";
    const node = isNode ? mode.node : null;
    const meta = node ? modeMeta(node.mode) : null;
    return (
      <PlayFlow
        key={isNode && node ? `n${node.index}` : `f${freeSeed}`}
        theme={theme}
        seed={isNode && node ? `${slug}:node:${node.index}` : freeSeed}
        bank={bank}
        questions={nodeQuestions}
        timeLimit={
          node?.mode === "boss" ? BOSS_TIME_LIMIT_S : node?.mode === "speed" ? SPEED_TIME_LIMIT_S : undefined
        }
        helpers={isNode}
        boss={node?.mode === "boss"}
        title={node && meta ? `Màn ${node.index + 1} · ${meta.icon} ${meta.label}` : "Chơi tự do"}
        onDone={handleDone}
      />
    );
  }

  if (!result) return null;

  /* --- xong màn: sao + mở khóa --- */
  if (mode.kind === "node") {
    const node = mode.node;
    const next = nodes[node.index + 1];
    const style = STYLES[result.style];
    return (
      <div className="space-y-4">
        <FreshBadges badges={fresh} />
        <div className="rounded-3xl border border-amber-300/40 bg-gradient-to-b from-amber-300/15 to-white/5 p-6 text-center sm:p-8">
          <p className="text-xs font-bold uppercase tracking-widest text-amber-200">
            Hoàn thành Màn {node.index + 1}
          </p>
          <div className="mt-2 flex items-center justify-center gap-1.5 text-5xl">
            {[0, 1, 2].map((i) => (
              <motion.span
                key={i}
                initial={{ scale: 0, rotate: -30 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ delay: 0.25 + i * 0.2, type: "spring", stiffness: 300, damping: 12 }}
                className={i < stars ? "" : "opacity-25 grayscale"}
              >
                ⭐
              </motion.span>
            ))}
          </div>
          <div className="mt-3 text-5xl">{style.icon}</div>
          <div className="mt-1 text-xl font-black">{style.name}</div>
          <p className="mt-0.5 text-sm text-amber-200">{style.tagline}</p>
          <p className="mt-2 text-xs text-white/55">
            🔥 Combo cao nhất ×{info.maxCombo} · 🃏 Đã dùng {info.helpersUsed} thẻ trợ giúp
          </p>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row">
          {next && (
            <button
              type="button"
              onClick={() => startNode(next)}
              className="flex-1 rounded-full bg-amber-300 px-6 py-3.5 font-black text-[#14122b] hover:bg-amber-200"
            >
              Màn {next.index + 1} {next.mode === "boss" ? "👹" : next.mode === "speed" ? "⚡" : ""} →
            </button>
          )}
          <button
            type="button"
            onClick={() => startNode(node)}
            className="flex-1 rounded-full border border-white/20 px-6 py-3.5 text-sm font-bold hover:bg-white/10"
          >
            ↻ Chơi lại
          </button>
          <button
            type="button"
            onClick={() => setPhase("map")}
            className="flex-1 rounded-full border border-white/20 px-6 py-3.5 text-sm font-bold hover:bg-white/10"
          >
            🗺️ Bản đồ
          </button>
        </div>
        <Link
          href={`/doi-chieu?d=${code}`}
          className="block rounded-2xl border border-white/10 bg-white/5 p-4 text-center text-sm font-bold hover:bg-white/10"
        >
          Đối chiếu với thiết kế gốc →
        </Link>
      </div>
    );
  }

  /* --- xong lượt tự do: flow cũ --- */
  const style = STYLES[result.style];
  const daily = mode.daily;
  const shareUrl =
    typeof window !== "undefined" ? `${window.location.origin}/ket-qua?d=${code}` : "";
  const shareText = daily
    ? `Đề hôm nay (${dailyLabel()}): tôi là “${style.name}” — bạn có dám thử?`
    : `Tôi vừa khám phá ra mình là “${style.name}” — bạn thì sao?`;
  return (
    <div className="space-y-4">
      {daily && streak > 0 && (
        <p className="rounded-2xl border border-amber-300/40 bg-amber-300/10 p-3 text-center text-sm font-bold text-amber-200">
          🔥 Streak {streak} ngày — mai quay lại giữ lửa nhé
        </p>
      )}
      <FreshBadges badges={fresh} />
      <StyleCard result={result} />

      <Link
        href={`/doi-chieu?d=${code}`}
        className="block rounded-2xl bg-amber-300 p-5 text-center font-black text-[#14122b] hover:bg-amber-200"
      >
        <span className="text-lg">Đối chiếu với thiết kế gốc →</span>
        <span className="mt-1 block text-sm font-bold opacity-70">
          Nhập ngày giờ sinh để xem bạn đang lệch bao nhiêu %
        </span>
      </Link>

      <div className="flex flex-col gap-2 sm:flex-row">
        <ShareRow url={shareUrl} text={shareText} theme={theme.slug} />
        <Link
          href={`/so-bai?d=${code}`}
          className="flex-1 rounded-full border border-white/20 px-4 py-3 text-center text-sm font-bold hover:bg-white/10"
        >
          ⚔️ So bài với bạn
        </Link>
        <button
          type="button"
          onClick={() => setPhase("map")}
          className="flex-1 rounded-full border border-white/20 px-4 py-3 text-sm font-bold hover:bg-white/10"
        >
          🗺️ Bản đồ
        </button>
      </div>

      <p className="text-center text-xs text-white/40">
        Đây là phong cách hành xử hiện tại — thiết kế gốc cần ngày giờ sinh mới tính được.
      </p>
    </div>
  );
}
