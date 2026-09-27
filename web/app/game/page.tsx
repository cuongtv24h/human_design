import type { Metadata } from "next";
import { fetchServerConfig } from "@/lib/game/server-config";
import LandingView from "./_components/LandingView";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Đúng Thiết Kế — Bạn là ai khi trút bỏ mọi kỳ vọng?",
  description:
    "Trò chơi 3 phút: 16 tình huống đời thường bóc trần cách bạn đang vận hành, rồi đối chiếu với thiết kế gốc của chính bạn. Chưa cần ngày sinh.",
  openGraph: {
    title: "Đúng Thiết Kế — Bạn là ai khi trút bỏ mọi kỳ vọng?",
    description: "16 tình huống · 3 phút · Mở khóa thiết kế gốc của bạn — chưa cần ngày sinh.",
    images: ["/api/og/game"],
  },
};

export default async function GameLandingPage() {
  const config = await fetchServerConfig();
  return <LandingView config={config} />;
}
