import type { GameServerConfig } from "./runtime";

const API_BASE = process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8001";

/** Đọc config Game Manager phía server (landing/metadata render đúng ngay lần đầu). */
export async function fetchServerConfig(): Promise<GameServerConfig | null> {
  try {
    const r = await fetch(`${API_BASE}/api/v1/public/game/config`, {
      next: { revalidate: 300 },
    });
    if (!r.ok) return null;
    return (await r.json()) as GameServerConfig;
  } catch {
    return null;
  }
}
