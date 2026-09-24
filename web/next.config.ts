import type { NextConfig } from "next";

// The browser only talks to this Next.js server; /api/* is proxied to FastAPI
// (hd-api). Same origin => the httpOnly session cookie works without CORS.
const API_INTERNAL_URL = process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8001";

const nextConfig: NextConfig = {
  poweredByHeader: false,
  // "AI biên tập phần này" waits for the LLM (up to ~2 min) through the /api proxy.
  experimental: { proxyTimeout: 180_000 },
  // Dev previews are served through proxied hosts (e.g. *.e2b.app).
  allowedDevOrigins: ["*.e2b.app", "localhost", "127.0.0.1"],
  async rewrites() {
    // afterFiles: route handler nội bộ (vd proxy stream SSE ở app/api/...)
    // được ưu tiên trước rewrite, còn lại vẫn proxy sang FastAPI như cũ.
    return { afterFiles: [{ source: "/api/:path*", destination: `${API_INTERNAL_URL}/api/:path*` }] };
  },
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "same-origin" },
        ],
      },
    ];
  },
};

export default nextConfig;
