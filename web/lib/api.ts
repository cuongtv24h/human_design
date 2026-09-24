// Thin fetch wrapper: same-origin cookie session + CSRF header + RFC 9457 errors.
import { getSessionToken, isEmbedded, setSessionToken } from "./session";
import type { ChatMessage } from "./types";

export class ApiError extends Error {
  constructor(public status: number, message: string, public errors?: { field: string; message: string }[]) {
    super(message);
  }
}

const BASE = "/api/v1";

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const headers: Record<string, string> = { Accept: "application/json" };
  if (method !== "GET") headers["X-HD-Request"] = "1";
  const token = getSessionToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (isEmbedded()) headers["X-HD-Embedded"] = "1";
  if (body !== undefined) headers["Content-Type"] = "application/json";
  let res: Response;
  try {
    res = await fetch(`${BASE}${path}`, {
      method,
      headers,
      credentials: "same-origin",
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError(0, "Không kết nối được máy chủ. Kiểm tra mạng rồi thử lại.");
  }
  if (res.status === 204) return undefined as T;
  const text = await res.text();
  let data: any = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = null;
  }
  if (res.status === 401 && token) setSessionToken(null);
  if (!res.ok) {
    const detail = (data && typeof data.detail === "string" && data.detail) || `Lỗi máy chủ (${res.status}).`;
    throw new ApiError(res.status, detail, data?.errors);
  }
  return data as T;
}

export const api = {
  get: <T>(path: string) => request<T>("GET", path),
  post: <T>(path: string, body?: unknown) => request<T>("POST", path, body ?? {}),
  patch: <T>(path: string, body: unknown) => request<T>("PATCH", path, body),
  put: <T>(path: string, body: unknown) => request<T>("PUT", path, body),
  del: (path: string) => request<void>("DELETE", path),
};

export const fileUrl = (reportId: string, kind: "markdown" | "infographic.html" | "bodygraph.svg" | "pdf" | "docx", download = false) => {
  const token = getSessionToken();
  return `${BASE}/reports/${reportId}/${kind}?download=${download}${token ? `&access_token=${encodeURIComponent(token)}` : ""}`;
};

export interface ChatStreamHandlers {
  onMeta?: (meta: { session_id: string; provider: string; model: string }) => void;
  onToken?: (text: string) => void;
  onTool?: (info: { phase: string; tool: string; source?: string }) => void;
  onDone?: (message: ChatMessage) => void;
}

/** POST SSE stream (trợ lý chat): đọc từng event meta/token/tool/done, ném ApiError khi lỗi. */
export async function postChatStream(path: string, body: unknown, h: ChatStreamHandlers, signal?: AbortSignal): Promise<void> {
  const headers: Record<string, string> = { Accept: "text/event-stream", "X-HD-Request": "1", "Content-Type": "application/json" };
  const token = getSessionToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (isEmbedded()) headers["X-HD-Embedded"] = "1";
  let res: Response;
  try {
    res = await fetch(`${BASE}${path}`, { method: "POST", headers, credentials: "same-origin", body: JSON.stringify(body), signal });
  } catch (e) {
    if ((e as Error).name === "AbortError") return;
    throw new ApiError(0, "Không kết nối được máy chủ. Kiểm tra mạng rồi thử lại.");
  }
  if (!res.ok || !res.body) {
    const text = await res.text().catch(() => "");
    let detail = `Lỗi máy chủ (${res.status}).`;
    try {
      const data = text ? JSON.parse(text) : null;
      if (data && typeof data.detail === "string") detail = data.detail;
    } catch { /* giữ nguyên */ }
    if (res.status === 401 && token) setSessionToken(null);
    throw new ApiError(res.status, detail);
  }
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  const pump = async (): Promise<void> => {
    const { done, value } = await reader.read();
    if (done) return;
    buf += decoder.decode(value, { stream: true });
    let idx: number;
    while ((idx = buf.indexOf("\n\n")) >= 0) {
      const block = buf.slice(0, idx);
      buf = buf.slice(idx + 2);
      let name = "";
      let data: any = null;
      for (const line of block.split("\n")) {
        if (line.startsWith("event:")) name = line.slice(6).trim();
        else if (line.startsWith("data:")) {
          try {
            data = JSON.parse(line.slice(5).trim());
          } catch { data = null; }
        }
      }
      if (name === "meta") h.onMeta?.(data);
      else if (name === "token") h.onToken?.(data?.text ?? "");
      else if (name === "tool") h.onTool?.(data);
      else if (name === "done") {
        h.onDone?.(data?.message);
        return;
      } else if (name === "error") {
        throw new ApiError(503, data?.message || "AI đang bận, thử lại sau.");
      }
    }
    return pump();
  };
  try {
    await pump();
  } finally {
    reader.releaseLock();
  }
}

export function qs(params: Record<string, string | number | undefined | null>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") search.set(key, String(value));
  }
  const s = search.toString();
  return s ? `?${s}` : "";
}
