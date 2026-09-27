import type { Metadata } from "next";
import Link from "next/link";
import { STYLES, THEMES } from "@/lib/game/content";
import { decodeResultParam, scoreQuiz } from "@/lib/game/engine";

function parseRank(v: string | undefined): number | null {
  const n = Number.parseInt(v ?? "", 10);
  return Number.isInteger(n) && n >= 1 && n <= 9999 ? n : null;
}

export async function generateMetadata({
  searchParams,
}: {
  searchParams: Promise<{ d?: string; rank?: string }>;
}): Promise<Metadata> {
  const { d, rank: rankRaw } = await searchParams;
  const decoded = decodeResultParam(d ?? null);
  const theme = decoded ? THEMES[decoded.theme] : undefined;
  if (!theme || !decoded) {
    return { title: "Đúng Thiết Kế — Kết quả trò chơi" };
  }
  const result = scoreQuiz(theme, decoded.answers);
  const style = STYLES[result.style];
  const rank = parseRank(rankRaw);
  if (rank !== null) {
    const title = `Hạng #${rank} bảng vàng ${theme.name} — Bạn có dám thách? | Đúng Thiết Kế`;
    return {
      title,
      description: `${style.icon} ${style.name} đang giữ hạng #${rank} tuần này. Chơi 3 phút để vượt qua.`,
      openGraph: {
        title,
        description: "Bảng vàng tuần · ẩn danh · reset mỗi thứ Hai.",
        images: [`/api/og/game?board=1&theme=${theme.slug}&rank=${rank}&style=${result.style}`],
      },
    };
  }
  const title = `Tôi là “${style.name}” — Bạn thì sao? | Đúng Thiết Kế`;
  return {
    title,
    description: `${style.tagline} Chơi 3 phút để biết phong cách của bạn.`,
    openGraph: {
      title,
      description: "Trò chơi 3 phút khám phá thiết kế gốc của bạn — chưa cần ngày sinh.",
      images: [`/api/og/game?style=${result.style}`],
    },
  };
}

export default async function SharedResultPage({
  searchParams,
}: {
  searchParams: Promise<{ d?: string; rank?: string }>;
}) {
  const { d, rank: rankRaw } = await searchParams;
  const decoded = decodeResultParam(d ?? null);
  const theme = decoded ? THEMES[decoded.theme] : undefined;
  if (!theme || !decoded || decoded.answers.length === 0) {
    return (
      <div className="rounded-3xl border border-white/10 bg-white/5 p-10 text-center">
        <div className="text-5xl">🧭</div>
        <h1 className="mt-4 text-2xl font-black">Link này hết hạn hoặc không hợp lệ</h1>
        <p className="mt-2 text-white/60">Chơi một ván mới chỉ mất 3 phút.</p>
        <Link
          href="/choi"
          className="mt-6 inline-block rounded-full bg-amber-300 px-6 py-3 font-bold text-[#14122b]"
        >
          Chơi ngay
        </Link>
      </div>
    );
  }
  const result = scoreQuiz(theme, decoded.answers);
  const style = STYLES[result.style];
  const rank = parseRank(rankRaw);
  return (
    <div className="space-y-4">
      <div className="rounded-3xl border border-amber-300/40 bg-gradient-to-b from-amber-300/15 to-white/5 p-8 text-center">
        <p className="text-xs font-bold uppercase tracking-widest text-amber-200">
          Bạn bè vừa khám phá ra
        </p>
        <div className="mt-2 text-6xl">{style.icon}</div>
        <h1 className="mt-2 text-3xl font-black">{style.name}</h1>
        <p className="mt-1 font-bold text-amber-200">{style.tagline}</p>
        <p className="mx-auto mt-3 max-w-md text-sm text-white/70">{style.desc}</p>
        <p className="mt-2 text-xs text-white/40">Theme: {theme.name}</p>
      </div>
      {rank !== null && (
        <div className="rounded-2xl border border-amber-300/40 bg-amber-300/10 p-4 text-center text-sm font-bold text-amber-200">
          🏆 Người chơi này đang đứng #{rank} bảng {theme.name} tuần này — vượt qua không?
        </div>
      )}
      <div className="rounded-3xl border border-white/10 bg-white/5 p-8 text-center">
        <div className="text-xl font-black">Còn bạn là ai?</div>
        <p className="mt-1 text-sm text-white/60">
          16 tình huống · 3 phút · Không cần đăng ký, chưa cần ngày sinh.
        </p>
        <div className="mt-5 flex flex-wrap justify-center gap-2">
          <Link
            href={`/choi/${theme.slug}`}
            className="rounded-full bg-amber-300 px-8 py-3 font-black text-[#14122b] hover:bg-amber-200"
          >
            Tôi cũng muốn biết
          </Link>
          <Link
            href="/choi"
            className="rounded-full border border-white/20 px-6 py-3 font-bold hover:bg-white/10"
          >
            Xem tất cả
          </Link>
        </div>
      </div>
    </div>
  );
}
