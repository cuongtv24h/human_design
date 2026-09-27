import type { Metadata } from "next";
import Link from "next/link";
import { LOCKED_THEMES, THEMES } from "@/lib/game/content";

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

const STEPS = [
  {
    n: "1",
    title: "Chơi 60 giây",
    desc: "3 tình huống, chọn theo phản xạ đầu tiên. Không có đáp án đúng.",
  },
  {
    n: "2",
    title: "Nhận thẻ phong cách",
    desc: "Biết mình đang vận hành kiểu gì: Khởi Xướng, Kiến Tạo, Dẫn Đường hay Tấm Gương.",
  },
  {
    n: "3",
    title: "Đối chiếu thiết kế gốc",
    desc: "Nhập ngày giờ sinh để xem bản vẽ gốc — và bạn đang lệch bao nhiêu %.",
  },
];

const FAQS = [
  {
    q: "Có cần ngày sinh mới chơi được không?",
    a: "Không. Chơi xong cả game mới cần — và chỉ khi bạn muốn đối chiếu với thiết kế gốc của mình.",
  },
  {
    q: "Kết quả có phải luận giải Human Design không?",
    a: "Không. Đó là phong cách hành xử hiện tại của bạn. Thiết kế gốc (loại năng lượng, chiến lược, thẩm quyền) chỉ tính được từ ngày giờ nơi sinh — và đó mới là phần hay nhất.",
  },
  {
    q: "Mất bao lâu? Có tốn phí không?",
    a: "Khoảng 1 phút, miễn phí, không cần đăng ký.",
  },
  {
    q: "Thông tin của tôi có bị lộ không?",
    a: "Chơi ẩn danh hoàn toàn. Ngày sinh (nếu bạn nhập ở bước đối chiếu) chỉ dùng để tính bản đồ cho riêng bạn, không công khai.",
  },
];

export default function GameLandingPage() {
  const first = Object.values(THEMES)[0];
  return (
    <div className="space-y-12 pt-8">
      <section className="text-center">
        <p className="mb-4 inline-block rounded-full border border-amber-300/40 bg-amber-300/10 px-4 py-1 text-xs font-bold tracking-widest text-amber-200">
          TRÒ CHƠI 60 GIÂY · CHƯA CẦN NGÀY SINH
        </p>
        <h1 className="mx-auto max-w-2xl text-4xl font-black leading-tight sm:text-5xl">
          Bạn là ai khi trút bỏ mọi kỳ vọng?
        </h1>
        <p className="mx-auto mt-4 max-w-xl text-white/70">
          3 tình huống đời thường bóc trần cách bạn đang vận hành — rồi đối chiếu với thiết kế gốc
          của chính bạn.
        </p>
        <div className="mt-8">
          <Link
            href={`/choi/${first.slug}`}
            className="inline-block rounded-full bg-amber-300 px-8 py-4 text-lg font-black text-[#14122b] shadow-lg shadow-amber-300/20 hover:bg-amber-200"
          >
            Khám phá thiết kế của tôi
          </Link>
          <p className="mt-3 text-xs text-white/50">Miễn phí · Không cần đăng ký · 1 phút</p>
        </div>
      </section>

      <section className="grid gap-3 sm:grid-cols-3">
        {STEPS.map((s) => (
          <div key={s.n} className="rounded-2xl border border-white/10 bg-white/5 p-5">
            <div className="mb-2 flex size-8 items-center justify-center rounded-full bg-amber-300 font-black text-[#14122b]">
              {s.n}
            </div>
            <div className="font-bold">{s.title}</div>
            <p className="mt-1 text-sm text-white/60">{s.desc}</p>
          </div>
        ))}
      </section>

      <section>
        <h2 className="mb-4 text-center text-2xl font-black">Chọn cửa vào</h2>
        <div className="grid gap-3">
          {Object.values(THEMES).map((t) => (
            <Link
              key={t.slug}
              href={`/choi/${t.slug}`}
              className="group rounded-2xl border border-amber-300/40 bg-gradient-to-r from-amber-300/15 to-transparent p-5 hover:border-amber-300"
            >
              <div className="flex items-center gap-4">
                <span className="text-4xl">{t.icon}</span>
                <div className="min-w-0 flex-1">
                  <div className="text-xs font-bold uppercase tracking-widest text-amber-200">
                    {t.name}
                  </div>
                  <div className="text-lg font-bold">{t.entryLabel}</div>
                  <p className="text-sm text-white/60">{t.entryDesc}</p>
                </div>
                <span className="shrink-0 rounded-full bg-amber-300 px-4 py-2 text-sm font-bold text-[#14122b]">
                  Chơi →
                </span>
              </div>
            </Link>
          ))}
          {LOCKED_THEMES.map((t) => (
            <div
              key={t.name}
              className="rounded-2xl border border-white/10 bg-white/[0.03] p-5 opacity-60"
            >
              <div className="flex items-center gap-4">
                <span className="text-4xl grayscale">{t.icon}</span>
                <div className="min-w-0 flex-1">
                  <div className="text-xs font-bold uppercase tracking-widest text-white/40">
                    {t.name}
                  </div>
                  <p className="text-sm text-white/50">{t.desc}</p>
                </div>
                <span className="shrink-0 rounded-full border border-white/20 px-4 py-2 text-sm text-white/50">
                  🔒 Sắp ra mắt
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-4 text-center text-2xl font-black">Hỏi nhanh đáp gọn</h2>
        <div className="space-y-2">
          {FAQS.map((f) => (
            <details key={f.q} className="rounded-2xl border border-white/10 bg-white/5 px-5 py-4">
              <summary className="cursor-pointer font-bold">{f.q}</summary>
              <p className="mt-2 text-sm text-white/60">{f.a}</p>
            </details>
          ))}
        </div>
      </section>

      <section className="rounded-3xl border border-amber-300/30 bg-gradient-to-b from-amber-300/15 to-transparent p-8 text-center">
        <div className="text-xl font-black">Đừng đoán mò về chính mình nữa.</div>
        <p className="mt-1 text-sm text-white/60">60 giây — và bạn sẽ nhìn mình bằng con mắt khác.</p>
        <Link
          href={`/choi/${first.slug}`}
          className="mt-5 inline-block rounded-full bg-amber-300 px-8 py-3 font-black text-[#14122b] hover:bg-amber-200"
        >
          Chơi ngay
        </Link>
      </section>
    </div>
  );
}
