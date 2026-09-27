"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
import { STYLES } from "@/lib/game/content";
import {
  checkPlayBadges,
  compatibility,
  decodeResultParam,
  encodeResult,
  randomSeed,
  recordPlayed,
  scoreQuiz,
  styleName,
  takeFreshBadges,
  trackGameEvent,
  type BadgeDef,
} from "@/lib/game/engine";
import { getRuntimeBank, getRuntimeTheme, toGameTheme } from "@/lib/game/runtime";
import { useGameConfig } from "@/lib/game/use-game-config";
import { FreshBadges } from "./BadgesShelf";
import PlayFlow from "./PlayFlow";
import { ShareRow, StyleCard } from "./cards";

export default function SoBaiFlow() {
  const params = useSearchParams();
  const router = useRouter();
  const d = params.get("d");
  const e = params.get("e");
  const { config, ready } = useGameConfig();

  const challenger = useMemo(() => {
    const decoded = decodeResultParam(d);
    if (!decoded) return null;
    const rc = getRuntimeTheme(decoded.theme, config);
    if (!rc || decoded.answers.length === 0) return null;
    const theme = toGameTheme(rc);
    return { theme, result: scoreQuiz(theme, decoded.answers), seed: decoded.seed };
  }, [d, config]);

  // Bạn chơi cùng seed với người thách → cả hai ra cùng 16 câu.
  const friendSeed = useMemo(() => challenger?.seed ?? randomSeed(), [challenger]);
  const bank = useMemo(
    () => (challenger ? getRuntimeBank(challenger.theme.slug, config) : []),
    [challenger, config],
  );

  const [mine, setMine] = useState<string[] | null>(() => {
    const decoded = decodeResultParam(e);
    if (!decoded || decoded.answers.length === 0) return null;
    return decoded.answers;
  });
  const [fresh, setFresh] = useState<BadgeDef[]>([]);
  const viewed = useRef(false);

  useEffect(() => {
    if (!viewed.current && challenger) {
      viewed.current = true;
      trackGameEvent("compare_view", challenger.theme.slug);
    }
  }, [challenger]);

  if (!ready) {
    return <p className="py-16 text-center text-white/60">Đang tải…</p>;
  }

  if (!challenger) {
    return (
      <div className="rounded-3xl border border-white/10 bg-white/5 p-10 text-center">
        <div className="text-5xl">⚔️</div>
        <h1 className="mt-4 text-2xl font-black">Thiếu bài để so</h1>
        <p className="mt-2 text-white/60">Link này không có kết quả của bạn bè. Chơi một ván rồi thách lại nhé.</p>
        <Link
          href="/game"
          className="mt-6 inline-block rounded-full bg-amber-300 px-6 py-3 font-bold text-[#14122b]"
        >
          Chơi ngay
        </Link>
      </div>
    );
  }

  if (!mine) {
    return (
      <div className="space-y-4">
        <div className="rounded-3xl border border-amber-300/40 bg-gradient-to-b from-amber-300/15 to-white/5 p-6 text-center">
          <p className="text-xs font-bold uppercase tracking-widest text-amber-200">
            Bạn bè thách đấu
          </p>
          <div className="mt-2 text-5xl">{STYLES[challenger.result.style].icon}</div>
          <div className="mt-1 text-2xl font-black">{styleName(challenger.result.style)}</div>
          <p className="mt-1 text-sm text-white/60">
            Chơi cùng 16 câu của theme “{challenger.theme.name}” để xem hai bạn hợp nhau bao nhiêu %
          </p>
        </div>
        <PlayFlow
          theme={challenger.theme}
          seed={friendSeed}
          bank={bank}
          onDone={(answers) => {
            setMine(answers);
            const myResult = scoreQuiz(challenger.theme, answers);
            recordPlayed(challenger.theme.slug, myResult.style);
            checkPlayBadges({ compare: true });
            setFresh(takeFreshBadges());
            trackGameEvent("compare_done", challenger.theme.slug);
            router.replace(
              `/game/so-bai?d=${d}&e=${encodeResult({ ...myResult, seed: friendSeed })}`,
            );
          }}
        />
      </div>
    );
  }

  const myResult = scoreQuiz(challenger.theme, mine);
  const c = compatibility(challenger.result, myResult);
  const myCode = encodeResult({ ...myResult, seed: friendSeed });
  const compareUrl =
    typeof window !== "undefined" ? `${window.location.origin}/game/so-bai?d=${d}&e=${myCode}` : "";

  return (
    <div className="space-y-4">
      <div className="rounded-3xl border border-amber-300/40 bg-gradient-to-b from-amber-300/15 to-white/5 p-8 text-center">
        <p className="text-xs font-bold uppercase tracking-widest text-amber-200">Độ hợp của hai bạn</p>
        <div className="mx-auto mt-3 flex size-28 items-center justify-center rounded-full border-4 border-amber-300 bg-[#14122b]">
          <span className="text-3xl font-black">{c.score}%</span>
        </div>
        <h1 className="mx-auto mt-3 max-w-lg text-xl font-black">{c.verdict}</h1>
        <p className="mx-auto mt-2 max-w-lg text-sm text-white/70">{c.note}</p>
      </div>

      <FreshBadges badges={fresh} />

      <div className="grid gap-3 sm:grid-cols-2">
        <div>
          <p className="mb-1 text-center text-xs font-bold uppercase tracking-widest text-white/50">
            Bạn bè
          </p>
          <StyleCard result={challenger.result} compact />
        </div>
        <div>
          <p className="mb-1 text-center text-xs font-bold uppercase tracking-widest text-white/50">Bạn</p>
          <StyleCard result={myResult} compact />
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        <ShareRow
          url={compareUrl}
          text={`Tôi và bạn hợp nhau ${c.score}% — bạn có dám so bài?`}
          theme={challenger.theme.slug}
          label="↗ Khoe độ hợp"
        />
        <Link
          href={`/game/doi-chieu?d=${myCode}`}
          className="flex-1 rounded-full bg-amber-300 px-4 py-3 text-center text-sm font-black text-[#14122b] hover:bg-amber-200"
        >
          Đối chiếu thiết kế gốc →
        </Link>
      </div>
      <p className="text-center text-xs text-white/40">
        So theo phong cách hành xử (không cần ngày sinh) — muốn sâu hơn thì đối chiếu thiết kế gốc.
      </p>
    </div>
  );
}
