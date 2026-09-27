"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useMemo, useRef, useState } from "react";
import { api } from "@/lib/api";
import { STYLES, THEMES } from "@/lib/game/content";
import {
  contrastFor,
  decodeResultParam,
  deviationPct,
  encodeResult,
  scoreQuiz,
  submitScore,
  trackGameEvent,
  unlockBadge,
  type GameChartOut,
} from "@/lib/game/engine";
import { ShareRow } from "../_components/cards";

const TIMEZONES = Array.from({ length: 27 }, (_, i) => {
  const h = i - 12;
  return `${h < 0 ? "-" : "+"}${String(Math.abs(h)).padStart(2, "0")}:00`;
});

function PageInner() {
  const params = useSearchParams();
  const decoded = useMemo(() => decodeResultParam(params.get("d")), [params]);
  const theme = decoded ? THEMES[decoded.theme] : undefined;
  const result = useMemo(
    () =>
      theme && decoded && decoded.answers.length > 0 ? scoreQuiz(theme, decoded.answers) : null,
    [theme, decoded],
  );

  const [birthDate, setBirthDate] = useState("");
  const [birthTime, setBirthTime] = useState("");
  const [birthPlace, setBirthPlace] = useState("");
  const [timezone, setTimezone] = useState("+07:00");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [chart, setChart] = useState<GameChartOut | null>(null);
  const [name, setName] = useState("");
  const [contact, setContact] = useState("");
  const [leadDone, setLeadDone] = useState(false);
  const [leadError, setLeadError] = useState("");
  const [rank, setRank] = useState<number | null>(null);
  const viewed = useRef(false);
  const scored = useRef(false);

  useEffect(() => {
    if (!viewed.current && result) {
      viewed.current = true;
      trackGameEvent("bridge_view", result.theme);
    }
  }, [result]);

  useEffect(() => {
    if (!scored.current && result && chart) {
      scored.current = true;
      unlockBadge("mirror");
      submitScore(result.theme, result.style, deviationPct(result, chart.summary.type)).then((rk) => {
        setRank(rk);
        if (rk !== null && rk <= 3) unlockBadge("top3");
      });
    }
  }, [result, chart]);

  if (!result || !theme) {
    return (
      <div className="rounded-3xl border border-white/10 bg-white/5 p-10 text-center">
        <div className="text-5xl">🎮</div>
        <h1 className="mt-4 text-2xl font-black">Chơi trước đã bạn ơi</h1>
        <p className="mt-2 text-white/60">
          Cần kết quả 16 câu trả lời mới đối chiếu được với thiết kế gốc.
        </p>
        <Link
          href="/choi"
          className="mt-6 inline-block rounded-full bg-amber-300 px-6 py-3 font-bold text-[#14122b]"
        >
          Chơi 3 phút
        </Link>
      </div>
    );
  }

  const submitChart = async () => {
    if (!birthDate || !birthTime) {
      setError("Vui lòng nhập đủ ngày và giờ sinh.");
      return;
    }
    setLoading(true);
    setError("");
    trackGameEvent("bridge_submit", result.theme);
    try {
      const out = await api.post<GameChartOut>("/public/game/chart", {
        birth_date: birthDate,
        birth_time: birthTime,
        birth_place: birthPlace.trim(),
        timezone,
      });
      setChart(out);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Không tính được, thử lại sau.");
    } finally {
      setLoading(false);
    }
  };

  const submitLead = async () => {
    if (!name.trim() || !contact.trim()) {
      setLeadError("Vui lòng nhập tên và số điện thoại/Zalo.");
      return;
    }
    setLeadError("");
    trackGameEvent("lead_submit", result.theme);
    try {
      await api.post("/public/game/leads", {
        name: name.trim(),
        contact: contact.trim(),
        birth_date: birthDate,
        birth_time: birthTime,
        birth_place: birthPlace.trim(),
        timezone,
        theme: result.theme,
        quiz: {
          style: result.style,
          secondary: result.secondary,
          decision: result.decision,
          deviation: deviation,
          answers: result.answers,
        },
      });
      setLeadDone(true);
    } catch (e) {
      setLeadError(e instanceof Error ? e.message : "Gửi thất bại, thử lại sau.");
    }
  };

  if (!chart) {
    return (
      <div className="mx-auto max-w-xl space-y-5">
        <div className="rounded-3xl border border-white/10 bg-white/5 p-8 text-center">
          <div className="text-5xl">🔗</div>
          <h1 className="mt-3 text-2xl font-black">Đồng bộ thiết kế gốc</h1>
          <p className="mt-2 text-sm text-white/70">{theme.bridge}</p>
        </div>
        <div className="grid gap-3 rounded-3xl border border-white/10 bg-white/5 p-6">
          <label className="block text-sm">
            <span className="mb-1 block font-bold">Ngày sinh *</span>
            <input
              type="date"
              value={birthDate}
              onChange={(e) => setBirthDate(e.target.value)}
              className="w-full rounded-xl border border-white/15 bg-[#14122b] px-3 py-2.5 text-white [color-scheme:dark]"
            />
          </label>
          <div className="grid grid-cols-2 gap-3">
            <label className="block text-sm">
              <span className="mb-1 block font-bold">Giờ sinh *</span>
              <input
                type="time"
                value={birthTime}
                onChange={(e) => setBirthTime(e.target.value)}
                className="w-full rounded-xl border border-white/15 bg-[#14122b] px-3 py-2.5 text-white [color-scheme:dark]"
              />
            </label>
            <label className="block text-sm">
              <span className="mb-1 block font-bold">Múi giờ</span>
              <select
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
                className="w-full rounded-xl border border-white/15 bg-[#14122b] px-3 py-2.5 text-white"
              >
                {TIMEZONES.map((tz) => (
                  <option key={tz} value={tz}>
                    UTC{tz}
                    {tz === "+07:00" ? " (VN)" : ""}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <label className="block text-sm">
            <span className="mb-1 block font-bold">Nơi sinh</span>
            <input
              type="text"
              value={birthPlace}
              onChange={(e) => setBirthPlace(e.target.value)}
              placeholder="Ví dụ: Hà Nội"
              maxLength={120}
              className="w-full rounded-xl border border-white/15 bg-[#14122b] px-3 py-2.5 text-white placeholder:text-white/30"
            />
          </label>
          {error && (
            <p className="rounded-xl bg-rose-500/15 px-3 py-2 text-sm text-rose-200">{error}</p>
          )}
          <button
            type="button"
            disabled={loading}
            onClick={submitChart}
            className="rounded-full bg-amber-300 px-6 py-3.5 font-black text-[#14122b] hover:bg-amber-200 disabled:opacity-60"
          >
            {loading ? "Đang tính toán…" : "Xem tôi lệch bao nhiêu % →"}
          </button>
          {loading && (
            <p className="text-center text-xs text-white/50">
              Đang tính 64 cổng · vẽ 9 trung tâm · so hai bản thiết kế…
            </p>
          )}
          <p className="text-center text-xs text-white/40">
            Ngày sinh chỉ dùng để tính bản đồ cho riêng bạn, không công khai.
          </p>
        </div>
      </div>
    );
  }

  const deviation = deviationPct(result, chart.summary.type);
  const contrast = contrastFor(result, chart.summary);
  const style = STYLES[result.style];
  const shareCode = encodeResult(result);
  const boardUrl =
    typeof window !== "undefined" && rank !== null
      ? `${window.location.origin}/choi/ket-qua?d=${shareCode}&rank=${rank}`
      : "";
  const facts = [
    ["Loại năng lượng", chart.summary.type_vn || chart.summary.type],
    ["Chiến lược", chart.summary.strategy],
    ["Thẩm quyền", chart.summary.authority],
    ["Profile", chart.summary.profile],
    ["Trung tâm xác định", `${chart.summary.defined_centers}/9`],
  ];

  return (
    <div className="space-y-4">
      <div className="rounded-3xl border border-amber-300/40 bg-gradient-to-b from-amber-300/15 to-white/5 p-8 text-center">
        <p className="text-xs font-bold uppercase tracking-widest text-amber-200">
          {style.icon} {style.name} · đối chiếu · {chart.summary.type_vn || chart.summary.type}
        </p>
        <div className="mx-auto mt-3 flex size-28 items-center justify-center rounded-full border-4 border-amber-300 bg-[#14122b]">
          <span className="text-3xl font-black">{deviation}%</span>
        </div>
        <p className="mt-1 text-xs text-white/50">độ lệch khỏi thiết kế gốc</p>
        {rank !== null && (
          <Link
            href="/choi#bang-vang"
            className="mt-2 inline-block rounded-full bg-amber-300/20 px-4 py-1 text-sm font-bold text-amber-200 hover:bg-amber-300/30"
          >
            🏆 Bạn đứng #{rank} bảng {theme.name} tuần này
          </Link>
        )}
        <h1 className="mx-auto mt-3 max-w-lg text-2xl font-black">{contrast.headline}</h1>
        <p className="mx-auto mt-2 max-w-lg text-sm text-white/70">{contrast.body}</p>
      </div>

      <div className="rounded-2xl border border-white/10 bg-white/5 p-5 text-[15px] leading-relaxed">
        <span className="font-bold text-amber-200">💡 Vì sao bạn thấy “sai sai”: </span>
        <span className="text-white/85">{contrast.insight}</span>
      </div>

      <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
        <div className="mb-3 text-sm font-bold text-white/70">
          Thiết kế gốc của bạn · {chart.subject_display}
        </div>
        <dl className="grid gap-2 sm:grid-cols-2">
          {facts.map(([k, v]) => (
            <div key={k} className="rounded-xl bg-white/5 px-3 py-2.5">
              <dt className="text-xs text-white/50">{k}</dt>
              <dd className="font-bold">{v || "—"}</dd>
            </div>
          ))}
        </dl>
      </div>

      <div className="rounded-3xl border border-amber-300/40 bg-gradient-to-b from-amber-300/10 to-transparent p-6 sm:p-8">
        {leadDone ? (
          <div className="text-center">
            <div className="text-5xl">🎉</div>
            <div className="mt-3 text-xl font-black">Đã nhận thông tin!</div>
            <p className="mt-1 text-sm text-white/70">
              Chuyên gia sẽ liên hệ trong 24h để gửi báo cáo đầy đủ của bạn.
            </p>
          </div>
        ) : (
          <>
            <div className="text-center text-xl font-black">Nhận bản đồ đầy đủ của chính bạn</div>
            <p className="mt-1 text-center text-sm text-white/60">
              Báo cáo đầy đủ giải mã chi tiết 9 trung tâm, kênh, cổng và cách áp dụng vào công
              việc + các mối quan hệ. Để lại liên hệ, chuyên gia gửi cho bạn.
            </p>
            <div className="mx-auto mt-4 grid max-w-md gap-2">
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Tên của bạn *"
                maxLength={80}
                className="rounded-xl border border-white/15 bg-[#14122b] px-3 py-2.5 text-white placeholder:text-white/30"
              />
              <input
                type="text"
                value={contact}
                onChange={(e) => setContact(e.target.value)}
                placeholder="SĐT / Zalo *"
                maxLength={120}
                className="rounded-xl border border-white/15 bg-[#14122b] px-3 py-2.5 text-white placeholder:text-white/30"
              />
              {leadError && (
                <p className="rounded-xl bg-rose-500/15 px-3 py-2 text-sm text-rose-200">{leadError}</p>
              )}
              <button
                type="button"
                onClick={() => {
                  trackGameEvent("cta_click", result.theme);
                  submitLead();
                }}
                className="rounded-full bg-amber-300 px-6 py-3 font-black text-[#14122b] hover:bg-amber-200"
              >
                Nhận báo cáo đầy đủ
              </button>
            </div>
          </>
        )}
      </div>

      <div className="flex flex-wrap gap-2">
        {rank !== null && (
          <ShareRow
            url={boardUrl}
            text={`Tôi đang đứng #${rank} bảng ${theme.name} tuần này — bạn có dám thách?`}
            theme={theme.slug}
            label={`🏆 Khoe hạng #${rank}`}
          />
        )}
        <Link
          href={`/choi/ket-qua?d=${shareCode}`}
          className="flex-1 rounded-full border border-white/20 px-4 py-3 text-center text-sm font-bold hover:bg-white/10"
        >
          ↗ Thách bạn chơi
        </Link>
        <Link
          href={`/choi/${theme.slug}`}
          className="flex-1 rounded-full border border-white/20 px-4 py-3 text-center text-sm font-bold hover:bg-white/10"
        >
          ↻ Chơi lại
        </Link>
      </div>
    </div>
  );
}

export default function DoiChieuPage() {
  return (
    <Suspense fallback={<p className="py-16 text-center text-white/60">Đang tải…</p>}>
      <PageInner />
    </Suspense>
  );
}
