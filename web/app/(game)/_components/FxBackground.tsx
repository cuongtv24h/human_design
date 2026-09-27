"use client";

import { useEffect, useRef } from "react";

/** Nền hạt sao trôi — canvas nhẹ, tự tắt khi máy yêu cầu giảm chuyển động. */
export default function FxBackground() {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const DPR = Math.min(2, window.devicePixelRatio || 1);
    let w = 0;
    let h = 0;
    let raf = 0;
    const N = 70;
    const ps = Array.from({ length: N }, () => ({
      x: Math.random(),
      y: Math.random(),
      r: 0.6 + Math.random() * 1.8,
      s: 0.05 + Math.random() * 0.25,
      o: 0.15 + Math.random() * 0.5,
      ph: Math.random() * Math.PI * 2,
      gold: Math.random() < 0.35,
    }));
    const resize = () => {
      w = canvas.clientWidth;
      h = canvas.clientHeight;
      canvas.width = Math.max(1, w * DPR);
      canvas.height = Math.max(1, h * DPR);
    };
    resize();
    window.addEventListener("resize", resize);
    let t = 0;
    const loop = () => {
      t += 0.016;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      for (const p of ps) {
        p.y -= p.s * 0.0016;
        if (p.y < -0.02) {
          p.y = 1.02;
          p.x = Math.random();
        }
        const tw = p.o * (0.6 + 0.4 * Math.sin(t * 2 + p.ph));
        ctx.beginPath();
        ctx.arc(p.x * w * DPR, p.y * h * DPR, p.r * DPR, 0, 7);
        ctx.fillStyle = p.gold ? `rgba(251,191,36,${tw})` : `rgba(167,139,250,${tw})`;
        ctx.fill();
      }
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
    };
  }, []);
  return (
    <canvas
      ref={ref}
      aria-hidden
      className="pointer-events-none absolute inset-0 h-full w-full opacity-60"
    />
  );
}
