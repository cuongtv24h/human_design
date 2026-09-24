// Thin fetch wrapper: same-origin cookie session + CSRF header + RFC 9457 errors.

export class ApiError extends Error {
  constructor(public status: number, message: string, public errors?: { field: string; message: string }[]) {
    super(message);
  }
}

const BASE = "/api/v1";

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const headers: Record<string, string> = { Accept: "application/json" };
  if (method !== "GET") headers["X-HD-Request"] = "1";
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
  del: (path: string) => request<void>("DELETE", path),
};

export const fileUrl = (reportId: string, kind: "markdown" | "infographic.html" | "bodygraph.svg", download = false) =>
  `${BASE}/reports/${reportId}/${kind}?download=${download}`;

export function qs(params: Record<string, string | number | undefined | null>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") search.set(key, String(value));
  }
  const s = search.toString();
  return s ? `?${s}` : "";
}
