"use client";

import Link from "next/link";
import { useParams, useSearchParams } from "next/navigation";
import { useMemo, useState } from "react";
import { STYLES, THEMES } from "@/lib/game/content";
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
  trackGameEvent,
  type BadgeDef,
} from "@/lib/game/engine";
import { FreshBadges } from "../_components/BadgesShelf";
import PlayFlow from "../_components/PlayFlow";
import { ShareRow, StyleCard } from "../_components/cards";

export default function PlayPage() {
  const { theme: slug } = useParams<{ theme: string }>();
  const params = useSearchParams();
  const daily = params.get("daily") === "1";
  const theme = THEMES[slug];
  const [phase, setPhase] = useState<"intro" | "playing" | "done">("intro");
  const [answers, setAnswers] = useState<string[]>([]);
  const [playSeed, setPlaySeed] = useState("");
  const [streak, setStreak] = useState(0);
  const [fresh, setFresh] = useState<BadgeDef[]>([]);

  const result = useMemo(
    () => (theme && phase === "done" ? scoreQuiz(theme, answers) : null),
    [theme, phase, answers],
  );
  const code = useMemo(
    () => (result ? encodeResult({ ...result, seed: playSeed || undefined }) : ""),
    [result, playSeed],
  );

  if (!theme) {
    return (
      <div className="rounded-3xl border border-white/10 bg-white/5 p-10 text-center">
        <div className="text-5xl">🔒</div>
        <h1 className="mt-4 text-2xl font-black">Cửa này sắp mở</h1>
        <p className="mt-2 text-white/60">Theme này đang được soạn. Chơi theme khác trước nhé.</p>
        <Link
          href="/choi"
          className="mt-6 inline-block rounded-full bg-amber-300 px-6 py-3 font-bold text-[#14122b]"
        >
          ← Chọn cửa khác
        </Link>
      </div>
    );
  }

  if (phase === "intro") {
    return (
      <div className="rounded-3xl border border-white/10 bg-white/5 p-8 text-center sm:p-12">
        {daily && (
          <p className="mb-4 inline-block rounded-full border border-amber-300/40 bg-amber-300/10 px-4 py-1 text-xs font-bold tracking-widest text-amber-200">
            📅 ĐỀ HÔM NAY · {dailyLabel()} · CẢ CỘNG ĐỒNG CÙNG 1 ĐỀ
          </p>
        )}
        <div className="text-6xl">{theme.icon}</div>
        <p className="mt-4 text-xs font-bold uppercase tracking-widest text-amber-200">{theme.name}</p>
        <h1 className="mt-1 text-3xl font-black">{theme.entryLabel}</h1>
        <p className="mx-auto mt-3 max-w-md text-white/70">{theme.intro}</p>
        <button
          type="button"
          onClick={() => {
            setPlaySeed(daily ? `${dailySeed()}-${theme.slug}` : randomSeed());
            trackGameEvent("game_start", theme.slug);
            setPhase("playing");
          }}
          className="mt-8 rounded-full bg-amber-300 px-10 py-4 text-lg font-black text-[#14122b] hover:bg-amber-200"
        >
          Bắt đầu →
        </button>
        <p className="mt-3 text-xs text-white/50">
          {QUESTIONS_PER_PLAY} tình huống · khoảng 3 phút
          {daily ? " · đề chung cả cộng đồng" : " · mỗi lượt rút đề khác nhau"}
        </p>
      </div>
    );
  }

  if (phase === "playing") {
    return (
      <PlayFlow
        theme={theme}
        seed={playSeed}
        onDone={async (a) => {
          setAnswers(a);
          const r = scoreQuiz(theme, a);
          recordPlayed(theme.slug, r.style);
          let n = 0;
          if (daily) {
            const s = await submitStreak();
            n = s?.streak ?? 0;
            setStreak(n);
          }
          checkPlayBadges({ daily, streak: n });
          setFresh(takeFreshBadges());
          trackGameEvent("game_complete", theme.slug);
          setPhase("done");
        }}
      />
    );
  }

  if (!result) return null;
  const style = STYLES[result.style];
  const shareUrl =
    typeof window !== "undefined" ? `${window.location.origin}/choi/ket-qua?d=${code}` : "";
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
        href={`/choi/doi-chieu?d=${code}`}
        className="block rounded-2xl bg-amber-300 p-5 text-center font-black text-[#14122b] hover:bg-amber-200"
      >
        <span className="text-lg">Đối chiếu với thiết kế gốc →</span>
        <span className="mt-1 block text-sm font-bold opacity-70">
          Nhập ngày giờ sinh để xem bạn đang lệch bao nhiêu %
        </span>
      </Link>

      <div className="flex flex-wrap gap-2">
        <ShareRow url={shareUrl} text={shareText} theme={theme.slug} />
        <Link
          href={`/choi/so-bai?d=${code}`}
          className="flex-1 rounded-full border border-white/20 px-4 py-3 text-center text-sm font-bold hover:bg-white/10"
        >
          ⚔️ So bài với bạn
        </Link>
        <button
          type="button"
          onClick={() => {
            setAnswers([]);
            setPhase("intro");
          }}
          className="flex-1 rounded-full border border-white/20 px-4 py-3 text-sm font-bold hover:bg-white/10"
        >
          ↻ Chơi lại
        </button>
      </div>

      <p className="text-center text-xs text-white/40">
        Đây là phong cách hành xử hiện tại — thiết kế gốc cần ngày giờ sinh mới tính được.
      </p>
    </div>
  );
}
