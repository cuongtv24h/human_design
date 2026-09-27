"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
import { STYLES, THEMES } from "@/lib/game/content";
import {
  compatibility,
  decodeResultParam,
  encodeResult,
  recordPlayed,
  scoreQuiz,
  styleName,
  trackGameEvent,
} from "@/lib/game/engine";
import PlayFlow from "./PlayFlow";
import { ShareRow, StyleCard } from "./cards";

export default function SoBaiFlow() {
  const params = useSearchParams();
  const router = useRouter();
  const d = params.get("d");
  const e = params.get("e");

  const challenger = useMemo(() => {
    const decoded = decodeResultParam(d);
    if (!decoded) return null;
    const theme = THEMES[decoded.theme];
    if (!theme || decoded.answers.length === 0) return null;
    return { theme, result: scoreQuiz(theme, decoded.answers) };
  }, [d]);

  const [mine, setMine] = useState<string[] | null>(() => {
    const decoded = decodeResultParam(e);
    if (!decoded || decoded.answers.length === 0) return null;
    const theme = decoded.theme ? THEMES[decoded.theme] : undefined;
    if (!theme) return null;
    return decoded.answers;
  });
  const viewed = useRef(false);

  useEffect(() => {
    if (!viewed.current && challenger) {
      viewed.current = true;
      trackGameEvent("compare_view", challenger.theme.slug);
    }
  }, [challenger]);

  if (!challenger) {
    return (
      <div className="rounded-3xl border border-white/10 bg-white/5 p-10 text-center">
        <div className="text-5xl">⚔️</div>
        <h1 className="mt-4 text-2xl font-black">Thiếu bài để so</h1>
        <p className="mt-2 text-white/60">Link này không có kết quả của bạn bè. Chơi một ván rồi thách lại nhé.</p>
        <Link
          href="/choi"
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
            Chơi theme “{challenger.theme.name}” để xem hai bạn hợp nhau bao nhiêu %
          </p>
        </div>
        <PlayFlow
          theme={challenger.theme}
          onDone={(answers) => {
            setMine(answers);
            const myResult = scoreQuiz(challenger.theme, answers);
            recordPlayed(challenger.theme.slug, myResult.style);
            trackGameEvent("compare_done", challenger.theme.slug);
            router.replace(`/choi/so-bai?d=${d}&e=${encodeResult(myResult)}`);
          }}
        />
      </div>
    );
  }

  const myResult = scoreQuiz(challenger.theme, mine);
  const c = compatibility(challenger.result, myResult);
  const myCode = encodeResult(myResult);
  const compareUrl =
    typeof window !== "undefined" ? `${window.location.origin}/choi/so-bai?d=${d}&e=${myCode}` : "";

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
          href={`/choi/doi-chieu?d=${myCode}`}
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
