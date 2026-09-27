import type { Metadata } from "next";
import LandingView from "./(game)/choi/_components/LandingView";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Đúng Thiết Kế — Bạn là ai khi trút bỏ mọi kỳ vọng?",
  description:
    "Trò chơi 60 giây: 3 tình huống đời thường bóc trần cách bạn đang vận hành, rồi đối chiếu với thiết kế gốc của chính bạn. Chưa cần ngày sinh.",
  openGraph: {
    title: "Đúng Thiết Kế — Bạn là ai khi trút bỏ mọi kỳ vọng?",
    description: "3 tình huống · 60 giây · Mở khóa thiết kế gốc của bạn — chưa cần ngày sinh.",
    images: ["/api/og/game"],
  },
};

export default function HomePage() {
  return <LandingView />;
}
