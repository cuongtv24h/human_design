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
  async redirects() {
    // URL game cũ (/choi, /game) -> URL gốc mới, giữ nguyên query (?d=...).
    // URL admin cũ (trước khi gom về /admin/*) -> tiền tố mới, giữ nguyên query.
    return [
      { source: "/choi/:path*", destination: "/:path*", permanent: true },
      { source: "/game/:path*", destination: "/:path*", permanent: true },
      { source: "/login", destination: "/admin/login", permanent: true },
      { source: "/reports/:path*", destination: "/admin/reports/:path*", permanent: true },
      { source: "/clients/:path*", destination: "/admin/clients/:path*", permanent: true },
      { source: "/settings/:path*", destination: "/admin/settings/:path*", permanent: true },
    ];
  },
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
          // HSTS: trình duyệt chỉ áp dụng khi truy cập qua HTTPS (bỏ qua khi là HTTP).
          { key: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains" },
          // Không dùng quyền trình duyệt không cần thiết.
          { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=(), payment=()" },
          // Chống clickjacking nhưng vẫn cho phép iframe preview (e2b) nhúng trang admin.
          // CSP full (script-src nonce) cần middleware nonce của Next — làm riêng để không vỡ App Router.
          { key: "Content-Security-Policy", value: "frame-ancestors 'self' *.e2b.app" },
        ],
      },
    ];
  },
};

export default nextConfig;
