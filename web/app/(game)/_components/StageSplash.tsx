"use client";

import { motion } from "framer-motion";
import { useEffect, useRef } from "react";
import type { NodeMode } from "@/lib/game/stages";

/** Màn chào vào trận: CHƯƠNG × — MÀN Y (tự tắt sau 2s, chạm để qua ngay). */
export default function StageSplash({
  icon,
  chapterLabel,
  chapterName,
  nodeIndex,
  mode,
  onDone,
}: {
  icon: string;
  chapterLabel: string;
  chapterName: string;
  nodeIndex: number;
  mode: NodeMode;
  onDone: () => void;
}) {
  const cb = useRef(onDone);
  cb.current = onDone;
  useEffect(() => {
    const t = setTimeout(() => cb.current(), 2000);
    return () => clearTimeout(t);
  }, []);
  const boss = mode === "boss";
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, scale: 1.12 }}
      onClick={onDone}
      className={`fixed inset-0 z-50 flex items-center justify-center px-6 backdrop-blur-sm ${
        boss ? "bg-red-950/85" : "bg-[#0b0a1d]/90"
      }`}
    >
      <motion.div
        initial={{ scale: 0.6, y: 30 }}
        animate={{ scale: 1, y: 0 }}
        transition={{ type: "spring", stiffness: 260, damping: 18 }}
        className="text-center"
      >
        <motion.div
          animate={boss ? { rotate: [0, -6, 6, 0], scale: [1, 1.12, 1] } : { y: [0, -10, 0] }}
          transition={boss ? { repeat: Infinity, duration: 0.9 } : { repeat: Infinity, duration: 1.6 }}
          className="text-7xl sm:text-8xl"
        >
          {boss ? "👹" : mode === "speed" ? "⚡" : icon}
        </motion.div>
        <p className="mt-4 text-xs font-bold uppercase tracking-[0.3em] text-amber-200">
          {chapterLabel} · {chapterName}
        </p>
        <h2
          className={`mt-1 text-5xl font-black tracking-tight sm:text-6xl ${
            boss ? "text-rose-300" : "text-white"
          }`}
        >
          MÀN {nodeIndex + 1}
        </h2>
        {boss && (
          <p className="mt-2 inline-block rounded-full border border-rose-400/50 bg-rose-500/20 px-4 py-1 text-sm font-black text-rose-200">
            TRÙM CUỐI CHƯƠNG — 8 GIÂY MỖI CÂU
          </p>
        )}
        {mode === "speed" && (
          <p className="mt-2 inline-block rounded-full border border-amber-300/50 bg-amber-300/15 px-4 py-1 text-sm font-black text-amber-200">
            MÀN TỐC ĐỘ — 10 GIÂY MỖI CÂU
          </p>
        )}
        <p className="mt-4 animate-pulse text-xs text-white/50">chạm để bắt đầu</p>
      </motion.div>
    </motion.div>
  );
}
