"use client";

import { useState } from "react";
import { STYLES } from "@/lib/game/content";
import {
  decisionName,
  energyLabel,
  paceLabel,
  trackGameEvent,
  type QuizResult,
} from "@/lib/game/engine";

export function Meter({
  label,
  left,
  right,
  value,
}: {
  label: string;
  left: string;
  right: string;
  value: number;
}) {
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

export function StyleCard({ result, compact }: { result: QuizResult; compact?: boolean }) {
  const style = STYLES[result.style];
  if (compact) {
    return (
      <div className="rounded-2xl border border-white/10 bg-white/5 p-5 text-center">
        <div className="text-5xl">{style.icon}</div>
        <div className="mt-1 text-xl font-black">{style.name}</div>
        <p className="mt-1 text-xs text-amber-200">{style.tagline}</p>
        <div className="mt-3 space-y-3 text-left">
          <Meter label={energyLabel(result.energy)} left="Theo đợt" right="Bền bỉ" value={result.energy} />
          <Meter label={paceLabel(result.pace)} left="Chờ thời" right="Lao ngay" value={result.pace} />
        </div>
      </div>
    );
  }
  return (
    <div className="space-y-4">
      <div className="rounded-3xl border border-amber-300/40 bg-gradient-to-b from-amber-300/15 to-white/5 p-6 text-center sm:p-8">
        <p className="text-xs font-bold uppercase tracking-widest text-amber-200">
          Thẻ phong cách của bạn
        </p>
        <div className="mt-2 text-5xl sm:text-6xl">{style.icon}</div>
        <h1 className="mt-2 text-2xl font-black sm:text-3xl">{style.name}</h1>
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
    </div>
  );
}

export function ShareRow({
  url,
  text,
  theme,
  label,
}: {
  url: string;
  text: string;
  theme: string;
  label?: string;
}) {
  const [copied, setCopied] = useState(false);
  const share = async () => {
    trackGameEvent("share_click", theme);
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
  return (
    <button
      type="button"
      onClick={share}
      className="flex-1 rounded-full border border-white/20 px-4 py-3 text-sm font-bold hover:bg-white/10"
    >
      {copied ? "✓ Đã chép link!" : (label ?? "↗ Thách bạn chơi")}
    </button>
  );
}
