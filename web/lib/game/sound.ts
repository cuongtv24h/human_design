/** Hiệu ứng âm thanh tổng hợp bằng WebAudio — không cần file asset. */

let ctx: AudioContext | null = null;
const MUTE_KEY = "ddtk-muted";

export function isMuted(): boolean {
  try {
    return window.localStorage.getItem(MUTE_KEY) === "1";
  } catch {
    return false;
  }
}

export function setMuted(m: boolean): void {
  try {
    window.localStorage.setItem(MUTE_KEY, m ? "1" : "0");
  } catch {
    /* bỏ qua */
  }
}

function ac(): AudioContext | null {
  try {
    if (typeof window === "undefined") return null;
    const AC =
      window.AudioContext ??
      (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
    if (!AC) return null;
    ctx ??= new AC();
    if (ctx.state === "suspended") void ctx.resume();
    return ctx.state === "running" ? ctx : null;
  } catch {
    return null;
  }
}

function tone(
  freq: number,
  dur = 0.12,
  type: OscillatorType = "sine",
  gain = 0.08,
  delay = 0,
  slideTo?: number,
): void {
  const c = ac();
  if (!c || isMuted()) return;
  try {
    const t0 = c.currentTime + delay;
    const o = c.createOscillator();
    const g = c.createGain();
    o.type = type;
    o.frequency.setValueAtTime(freq, t0);
    if (slideTo) o.frequency.exponentialRampToValueAtTime(slideTo, t0 + dur);
    g.gain.setValueAtTime(0.0001, t0);
    g.gain.exponentialRampToValueAtTime(gain, t0 + 0.015);
    g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
    o.connect(g);
    g.connect(c.destination);
    o.start(t0);
    o.stop(t0 + dur + 0.05);
  } catch {
    /* bỏ qua */
  }
}

const PENTA = [0, 2, 4, 7, 9];

export const sfx = {
  click() {
    tone(760, 0.05, "triangle", 0.06);
  },
  flip() {
    tone(280, 0.1, "triangle", 0.045, 0, 640);
  },
  deal(i: number) {
    tone(420 + i * 60, 0.06, "triangle", 0.04);
  },
  /** Cao độ tăng dần theo combo — nghe là biết đang "vào cầu". */
  pick(combo: number) {
    const c = Math.min(Math.max(combo, 0), 8);
    const semis = PENTA[c % PENTA.length] + 12 * Math.floor(c / PENTA.length);
    const f = 523.25 * Math.pow(2, semis / 12);
    tone(f, 0.14, "sine", 0.09);
    tone(f * 1.5, 0.12, "sine", 0.05, 0.05);
  },
  timeout() {
    tone(180, 0.22, "sawtooth", 0.05, 0, 90);
  },
  star(i: number) {
    tone(880 + i * 240, 0.16, "sine", 0.08);
  },
  win() {
    [523.25, 659.25, 783.99, 1046.5].forEach((f, i) => tone(f, 0.18, "triangle", 0.07, i * 0.09));
  },
  unlock() {
    [392, 523.25, 659.25].forEach((f, i) => tone(f, 0.2, "triangle", 0.07, i * 0.1));
    tone(1318.5, 0.3, "sine", 0.04, 0.32);
  },
};
