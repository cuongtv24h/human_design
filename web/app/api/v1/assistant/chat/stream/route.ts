// POST /api/v1/assistant/chat/stream — proxy stream SSE thẳng tới FastAPI.
//
// Route handler được ưu tiên trước rewrite /api/* (xem afterFiles trong
// next.config.ts), nên luồng token pipe trực tiếp về trình duyệt, loại trừ
// mọi tầng trung gian dồn response (buffer) của Next.
import { NextRequest } from "next/server";

const API = process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8001";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  const headers: Record<string, string> = {
    "content-type": "application/json",
    accept: "text/event-stream",
  };
  for (const key of ["cookie", "authorization", "x-hd-request", "x-hd-embedded", "x-forwarded-for"] as const) {
    const value = req.headers.get(key);
    if (value) headers[key] = value;
  }
  let upstream: Response;
  try {
    upstream = await fetch(`${API}/api/v1/assistant/chat/stream`, {
      method: "POST",
      headers,
      body: await req.text(),
      signal: AbortSignal.timeout(290_000),
    });
  } catch {
    return Response.json({ detail: "AI phản hồi quá lâu, thử lại sau." }, { status: 504 });
  }
  if (!upstream.ok || !upstream.body) {
    const text = await upstream.text().catch(() => "");
    return new Response(text || `{"detail":"Lỗi máy chủ (${upstream.status})."}`, {
      status: upstream.status,
      headers: { "content-type": "application/json" },
    });
  }
  return new Response(upstream.body, {
    status: 200,
    headers: {
      "content-type": "text/event-stream; charset=utf-8",
      "cache-control": "no-cache, no-transform",
      "x-accel-buffering": "no",
    },
  });
}
