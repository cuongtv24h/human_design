"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useMemo, useState } from "react";
import { STYLES, THEMES } from "@/lib/game/content";
import {
  decisionName,
  encodeResult,
  energyLabel,
  paceLabel,
  scoreQuiz,
  trackGameEvent,
} from "@/lib/game/engine";

const LETTERS = ["A", "B", "C", "D"];

function Meter({ label, left, right, value }: { label: string; left: string; right: string; value: number }) {
  const pct = Math.round(((value + 1) / 2) * 100);
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-xs">
        <span className="text-white/50">{left}</span>
        <span className="font-bold text-white">{label}</span>
        <span className="text-white/50">{right}</span>
      </div>
      <div className="relative h-2 rounded-full bg-white/10">
        <div
          className="absolute top-1/2 size-4 -translate-x-1/2 -translate-y-1/2 rounded-full bg-amber-300 shadow"
          style={{ left: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export default function PlayPage() {
  const { theme: slug } = useParams<{ theme: string }>();
  const theme = THEMES[slug];
  const [step, setStep] = useState(-1);
  const [answers, setAnswers] = useState<string[]>([]);
  const [copied, setCopied] = useState(false);

  const result = useMemo(
    () => (theme && step >= theme.scenarios.length ? scoreQuiz(theme, answers) : null),
    [theme, step, answers],
  );
  const code = useMemo(() => (result ? encodeResult(result) : ""), [result]);

  if (!theme) {
    return (
      <div className="rounded-3xl border border-white/10 bg-white/5 p-10 text-center">
        <div className="text-5xl">🔒</div>
        <h1 className="mt-4 text-2xl font-black">Cửa này sắp mở</h1>
        <p className="mt-2 text-white/60">Theme này đang được soạn. Chơi theme mở màn trước nhé.</p>
        <Link
          href="/choi"
          className="mt-6 inline-block rounded-full bg-amber-300 px-6 py-3 font-bold text-[#14122b]"
        >
          ← Chọn cửa khác
        </Link>
      </div>
    );
  }

  const share = async () => {
    if (!code) return;
    trackGameEvent("share_click", theme.slug);
    const url = `${window.location.origin}/choi/ket-qua?d=${code}`;
    const text = `Tôi vừa khám phá ra mình là “${result ? STYLES[result.style].name : ""}” — bạn thì sao?`;
    try {
      if (navigator.share) {
        await navigator.share({ title: "Đúng Thiết Kế", text, url });
        return;
      }
      throw new Error("no-share");
    } catch {
      /* rớt xuống chép link */
    }
    try {
      await navigator.clipboard.writeText(`${text} ${url}`);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch {
      prompt("Chép link này để chia sẻ:", url);
    }
  };

  if (step === -1) {
    return (
      <div className="rounded-3xl border border-white/10 bg-white/5 p-8 text-center sm:p-12">
        <div className="text-6xl">{theme.icon}</div>
        <p className="mt-4 text-xs font-bold uppercase tracking-widest text-amber-200">{theme.name}</p>
        <h1 className="mt-1 text-3xl font-black">{theme.entryLabel}</h1>
        <p className="mx-auto mt-3 max-w-md text-white/70">{theme.intro}</p>
        <button
          type="button"
          onClick={() => {
            trackGameEvent("game_start", theme.slug);
            setStep(0);
          }}
          className="mt-8 rounded-full bg-amber-300 px-10 py-4 text-lg font-black text-[#14122b] hover:bg-amber-200"
        >
          Bắt đầu →
        </button>
        <p className="mt-3 text-xs text-white/50">{theme.scenarios.length} tình huống · khoảng 1 phút</p>
      </div>
    );
  }

  if (result) {
    const style = STYLES[result.style];
    return (
      <div className="space-y-4">
        <div className="rounded-3xl border border-amber-300/40 bg-gradient-to-b from-amber-300/15 to-white/5 p-8 text-center">
          <p className="text-xs font-bold uppercase tracking-widest text-amber-200">
            Thẻ phong cách của bạn
          </p>
          <div className="mt-2 text-6xl">{style.icon}</div>
          <h1 className="mt-2 text-3xl font-black">{style.name}</h1>
          <p className="mt-1 font-bold text-amber-200">{style.tagline}</p>
          <p className="mx-auto mt-3 max-w-md text-sm text-white/70">{style.desc}</p>
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm">
            <span className="font-bold text-emerald-300">💪 Điểm mạnh: </span>
            <span className="text-white/80">{style.strength}</span>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm">
            <span className="font-bold text-rose-300">⚠️ Điểm mù: </span>
            <span className="text-white/80">{style.blindspot}</span>
          </div>
        </div>

        <div className="space-y-4 rounded-2xl border border-white/10 bg-white/5 p-5">
          <Meter label={energyLabel(result.energy)} left="Theo đợt" right="Bền bỉ" value={result.energy} />
          <Meter label={paceLabel(result.pace)} left="Chờ thời" right="Lao ngay" value={result.pace} />
          <p className="text-center text-sm text-white/70">
            Cách quyết định: <strong className="text-white">{decisionName(result.decision)}</strong>
          </p>
        </div>

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
          <button
            type="button"
            onClick={share}
            className="flex-1 rounded-full border border-white/20 px-4 py-3 text-sm font-bold hover:bg-white/10"
          >
            {copied ? "✓ Đã chép link!" : "↗ Thách bạn chơi"}
          </button>
          <button
            type="button"
            onClick={() => {
              setAnswers([]);
              setStep(-1);
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

  const sc = theme.scenarios[step];
  const done = step >= theme.scenarios.length;
  if (!sc || done) return null;
  const pick = (id: string) => {
    const next = [...answers];
    next[step] = id;
    setAnswers(next);
    if (step + 1 >= theme.scenarios.length) trackGameEvent("game_complete", theme.slug);
    setStep(step + 1);
  };
  return (
    <div className="space-y-5">
      <div>
        <div className="mb-2 flex items-center justify-between text-sm">
          <span className="font-bold text-white/70">
            Tình huống {step + 1}/{theme.scenarios.length}
          </span>
          {step > 0 && (
            <button
              type="button"
              onClick={() => setStep(step - 1)}
              className="text-white/50 hover:text-white"
            >
              ← Câu trước
            </button>
          )}
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-white/10">
          <div
            className="h-full rounded-full bg-amber-300 transition-all"
            style={{ width: `${Math.round(((step + 1) / theme.scenarios.length) * 100)}%` }}
          />
        </div>
      </div>

      <div className="rounded-3xl border border-white/10 bg-white/5 p-6 sm:p-8">
        <h1 className="text-2xl font-black">{sc.title}</h1>
        <p className="mt-2 leading-relaxed text-white/80">{sc.situation}</p>
      </div>

      <div className="grid gap-2">
        {sc.options.map((o, i) => (
          <button
            key={o.id}
            type="button"
            onClick={() => pick(o.id)}
            className="flex items-start gap-3 rounded-2xl border border-white/10 bg-white/5 p-4 text-left hover:border-amber-300/60 hover:bg-white/10"
          >
            <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-white/10 text-sm font-black">
              {LETTERS[i] ?? i + 1}
            </span>
            <span className="text-[15px] leading-snug">{o.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
