import type { Metadata } from "next";
import { Suspense } from "react";
import { STYLES } from "@/lib/game/content";
import {
  compatibility,
  decodeResultParam,
  registerCustomOptions,
  scoreQuiz,
  styleName,
} from "@/lib/game/engine";
import { customBankMap, getRuntimeTheme, toGameTheme } from "@/lib/game/runtime";
import { fetchServerConfig } from "@/lib/game/server-config";
import SoBaiFlow from "../_components/SoBaiFlow";

export async function generateMetadata({
  searchParams,
}: {
  searchParams: Promise<{ d?: string; e?: string }>;
}): Promise<Metadata> {
  const { d, e } = await searchParams;
  const da = decodeResultParam(d ?? null);
  const db = decodeResultParam(e ?? null);
  const config = await fetchServerConfig();
  registerCustomOptions(customBankMap(config));
  const themeOf = (slug: string | undefined) => {
    if (!slug) return undefined;
    const rc = getRuntimeTheme(slug, config);
    return rc ? toGameTheme(rc) : undefined;
  };
  const ta = themeOf(da?.theme);
  const tb = themeOf(db?.theme);
  if (ta && tb && da && db && da.answers.length > 0 && db.answers.length > 0) {
    const ra = scoreQuiz(ta, da.answers);
    const rb = scoreQuiz(tb, db.answers);
    const c = compatibility(ra, rb);
    const title = `${styleName(ra.style)} và ${styleName(rb.style)} hợp nhau ${c.score}% | Đúng Thiết Kế`;
    return {
      title,
      description: c.verdict,
      openGraph: {
        title,
        description: "So phong cách hành xử với bạn bè — không cần ngày sinh.",
        images: [`/api/og/game?style=${ra.style}`],
      },
    };
  }
  if (ta && da && da.answers.length > 0) {
    const style = STYLES[scoreQuiz(ta, da.answers).style];
    const title = `Bạn bè (${style.name}) thách bạn so bài | Đúng Thiết Kế`;
    return {
      title,
      description: "Chơi 3 phút để xem hai bạn hợp nhau bao nhiêu %.",
      openGraph: {
        title,
        description: "Chơi 3 phút để xem hai bạn hợp nhau bao nhiêu %.",
        images: [`/api/og/game?style=${style.id}`],
      },
    };
  }
  return { title: "So bài với bạn bè | Đúng Thiết Kế" };
}

export default function SoBaiPage() {
  return (
    <Suspense fallback={<p className="py-16 text-center text-white/60">Đang tải…</p>}>
      <SoBaiFlow />
    </Suspense>
  );
}
