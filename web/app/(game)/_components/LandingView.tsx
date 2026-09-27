import Link from "next/link";
import { STYLES } from "@/lib/game/content";
import { dailyLabel } from "@/lib/game/engine";
import {
  dailyRuntimeSlug,
  getRuntimeConcepts,
  type GameServerConfig,
} from "@/lib/game/runtime";
import BadgesShelf from "./BadgesShelf";
import ConceptGrid from "./ConceptGrid";
import DailyCard from "./DailyCard";
import Leaderboard from "./Leaderboard";
import PlayedProgress from "./PlayedProgress";

const STEPS = [
  {
    n: "1",
    title: "Chơi 3 phút",
    desc: "16 tình huống rút từ kho 300+ câu, chọn theo phản xạ đầu tiên. Không có đáp án đúng.",
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

const STATS = [
  { n: "300+", l: "tình huống trong kho" },
  { n: "16", l: "câu mỗi lượt chơi" },
  { n: "4", l: "phong cách hành xử" },
  { n: "100%", l: "ẩn danh" },
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
    q: "Mỗi lượt chơi bao nhiêu câu, có lặp lại không?",
    a: "16 câu rút ngẫu nhiên từ kho 300+ tình huống (mỗi concept 100 câu) nên gần như không bao giờ lặp lại. Đề hôm nay thì cả cộng đồng cùng 16 câu giống nhau.",
  },
  {
    q: "Mất bao lâu? Có tốn phí không?",
    a: "Khoảng 3–4 phút, miễn phí, không cần đăng ký.",
  },
  {
    q: "Thông tin của tôi có bị lộ không?",
    a: "Chơi ẩn danh hoàn toàn. Ngày sinh (nếu bạn nhập ở bước đối chiếu) chỉ dùng để tính bản đồ cho riêng bạn, không công khai.",
  },
];

/** Trang chủ game `/`. */
export default function LandingView({ config }: { config: GameServerConfig | null }) {
  const concepts = getRuntimeConcepts(config);
  const firstSlug = concepts.find((c) => c.enabled)?.slug ?? concepts[0]?.slug ?? "nguoc-dong";
  const dailySlug = dailyRuntimeSlug(concepts);
  const label = dailyLabel();
  const styles = Object.values(STYLES);
  return (
    <div className="space-y-12 pt-6 sm:space-y-16 sm:pt-10">
      {/* HERO */}
      <section className="relative">
        <div
          aria-hidden
          className="pointer-events-none absolute -top-24 left-1/2 h-72 w-[42rem] max-w-none -translate-x-1/2 rounded-full bg-amber-500/15 blur-3xl"
        />
        <div
          aria-hidden
          className="pointer-events-none absolute -left-32 top-40 size-72 rounded-full bg-violet-600/20 blur-3xl"
        />
        <div
          aria-hidden
          className="pointer-events-none absolute -right-32 top-24 size-72 rounded-full bg-amber-400/10 blur-3xl"
        />
        <div className="relative grid items-center gap-10 lg:grid-cols-[1.05fr_0.95fr]">
          <div className="text-center lg:text-left">
            <p className="mb-5 inline-block rounded-full border border-amber-300/40 bg-amber-300/10 px-4 py-1.5 text-xs font-bold tracking-widest text-amber-200">
              TRÒ CHƠI 3 PHÚT · CHƯA CẦN NGÀY SINH
            </p>
            <h1 className="mx-auto max-w-2xl text-4xl font-black leading-[1.1] sm:text-5xl lg:mx-0 lg:text-6xl">
              Bạn là ai khi{" "}
              <span className="bg-gradient-to-r from-amber-200 via-amber-300 to-orange-400 bg-clip-text text-transparent">
                trút bỏ mọi kỳ vọng?
              </span>
            </h1>
            <p className="mx-auto mt-5 max-w-xl text-white/70 lg:mx-0">
              16 tình huống đời thường bóc trần cách bạn đang vận hành — rồi đối chiếu với thiết kế
              gốc của chính bạn.
            </p>
            <div className="mt-8 flex flex-wrap justify-center gap-3 lg:justify-start">
              <Link
                href={`/${firstSlug}`}
                className="inline-block w-full rounded-full bg-amber-300 px-8 py-4 text-center text-lg font-black text-[#14122b] shadow-lg shadow-amber-300/25 transition hover:-translate-y-0.5 hover:bg-amber-200 sm:w-auto"
              >
                Khám phá thiết kế của tôi
              </Link>
              <Link
                href={`/${dailySlug}?daily=1`}
                className="inline-block w-full rounded-full border border-white/20 px-6 py-4 text-center text-sm font-bold transition hover:bg-white/10 sm:w-auto"
              >
                📅 Đề hôm nay · {label}
              </Link>
            </div>
            <p className="mt-3 text-xs text-white/50">Miễn phí · Không cần đăng ký · 3 phút</p>
          </div>
          <div className="grid grid-cols-2 gap-2 sm:gap-3" aria-hidden>
            {styles.map((s, i) => (
              <div
                key={s.id}
                className={`rounded-3xl border border-white/10 bg-white/[0.06] p-3 shadow-xl sm:p-5 shadow-black/30 backdrop-blur transition hover:border-amber-300/50 ${
                  i % 2 === 0 ? "-rotate-2" : "rotate-2 translate-y-3"
                }`}
              >
                <div className="text-3xl sm:text-4xl">{s.icon}</div>
                <div className="mt-2 text-sm font-black sm:text-base">{s.name}</div>
                <p className="mt-1 line-clamp-2 text-xs leading-relaxed text-amber-200/90">
                  {s.tagline}
                </p>
                <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-white/10">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-amber-300 to-orange-400"
                    style={{ width: `${72 - i * 9}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
        <dl className="relative mx-auto mt-12 grid max-w-3xl grid-cols-2 gap-y-6 rounded-3xl border border-white/10 bg-white/[0.04] px-6 py-6 backdrop-blur sm:grid-cols-4">
          {STATS.map((s) => (
            <div key={s.l} className="text-center">
              <dt className="order-2 mt-1 block text-xs text-white/50">{s.l}</dt>
              <dd className="text-2xl font-black text-amber-200 sm:text-3xl">{s.n}</dd>
            </div>
          ))}
        </dl>
      </section>

      <PlayedProgress />

      {/* CÁCH CHƠI */}
      <section>
        <p className="text-center text-xs font-bold uppercase tracking-widest text-amber-200">
          Cách chơi
        </p>
        <h2 className="mt-2 text-center text-2xl font-black sm:text-3xl">
          3 bước thấy rõ chính mình
        </h2>
        <div className="mt-6 grid gap-3 sm:grid-cols-3">
          {STEPS.map((s) => (
            <div
              key={s.n}
              className="group rounded-3xl border border-white/10 bg-white/[0.04] p-6 transition hover:-translate-y-1 hover:border-amber-300/40"
            >
              <div className="mb-3 flex size-10 items-center justify-center rounded-2xl bg-gradient-to-br from-amber-300 to-orange-400 text-lg font-black text-[#14122b]">
                {s.n}
              </div>
              <div className="font-bold">{s.title}</div>
              <p className="mt-1 text-sm leading-relaxed text-white/60">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ĐỀ HÔM NAY */}
      <section>
        <DailyCard initial={config} />
      </section>

      {/* CONCEPTS */}
      <section>
        <ConceptGrid initial={config} />
      </section>

      <section id="bang-vang" className="scroll-mt-24">
        <p className="text-center text-xs font-bold uppercase tracking-widest text-amber-200">
          Vinh danh
        </p>
        <div className="mt-2">
          <Leaderboard />
        </div>
      </section>

      <section id="huy-hieu" className="scroll-mt-24">
        <BadgesShelf />
      </section>

      {/* FAQ */}
      <section>
        <p className="text-center text-xs font-bold uppercase tracking-widest text-amber-200">
          Hỏi nhanh đáp gọn
        </p>
        <h2 className="mt-2 text-center text-2xl font-black sm:text-3xl">
          Thắc mắc thường gặp
        </h2>
        <div className="mx-auto mt-6 max-w-2xl space-y-2">
          {FAQS.map((f) => (
            <details
              key={f.q}
              className="rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-4 transition hover:border-amber-300/30"
            >
              <summary className="cursor-pointer font-bold">{f.q}</summary>
              <p className="mt-2 text-sm leading-relaxed text-white/60">{f.a}</p>
            </details>
          ))}
        </div>
      </section>

      {/* Final CTA */}
      <section className="relative overflow-hidden rounded-3xl border border-amber-300/30 bg-gradient-to-b from-amber-300/15 to-transparent p-10 text-center sm:p-14">
        <div
          aria-hidden
          className="pointer-events-none absolute -top-20 left-1/2 size-64 -translate-x-1/2 rounded-full bg-amber-400/20 blur-3xl"
        />
        <div className="relative">
          <div className="text-2xl font-black sm:text-3xl">Đừng đoán mò về chính mình nữa.</div>
          <p className="mt-2 text-sm text-white/60">
            3 phút — và bạn sẽ nhìn mình bằng con mắt khác.
          </p>
          <Link
            href={`/${firstSlug}`}
            className="mt-6 inline-block w-full rounded-full bg-amber-300 px-10 py-4 text-center text-lg font-black text-[#14122b] shadow-lg shadow-amber-300/25 transition hover:-translate-y-0.5 hover:bg-amber-200 sm:w-auto"
          >
            Chơi ngay
          </Link>
        </div>
      </section>
    </div>
  );
}
