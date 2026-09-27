"use client";

import { useEffect, useState } from "react";
import { isMuted, setMuted, sfx } from "@/lib/game/sound";

export default function SoundToggle() {
  const [muted, setM] = useState(false);
  useEffect(() => {
    setM(isMuted());
  }, []);
  return (
    <button
      type="button"
      aria-label={muted ? "Bật tiếng" : "Tắt tiếng"}
      onClick={() => {
        const m = !muted;
        setM(m);
        setMuted(m);
        if (!m) sfx.click();
      }}
      className="flex size-9 items-center justify-center rounded-full border border-white/20 text-base transition hover:bg-white/10"
    >
      {muted ? "🔇" : "🔊"}
    </button>
  );
}
