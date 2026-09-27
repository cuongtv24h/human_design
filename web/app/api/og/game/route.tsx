import { ImageResponse } from "next/og";
import { STYLES, THEMES, type StyleId } from "@/lib/game/content";

export const runtime = "edge";

async function vietnameseFont(): Promise<ArrayBuffer | null> {
  try {
    const css = await (
      await fetch(
        "https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@700;900&display=swap",
        { headers: { "User-Agent": "Mozilla/5.0" } },
      )
    ).text();
    const block = css.split("/* vietnamese */")[1] ?? css;
    const url = block.match(/url\((https:[^)]+?\.woff2)\)/)?.[1];
    if (!url) return null;
    return await (await fetch(url)).arrayBuffer();
  } catch {
    return null;
  }
}

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const style = STYLES[(searchParams.get("style") ?? "dan_duong") as StyleId] ?? STYLES.dan_duong;
  const font = await vietnameseFont();
  const rankRaw = Number.parseInt(searchParams.get("rank") ?? "", 10);
  const rank =
    Number.isInteger(rankRaw) && rankRaw >= 1 && rankRaw <= 9999 ? rankRaw : null;
  const board = searchParams.get("board") === "1" && rank !== null;
  const themeName = THEMES[searchParams.get("theme") ?? ""]?.name ?? "Ngược Dòng";
  return new ImageResponse(
    board ? (
      <div
        style={{
          width: 1200,
          height: 630,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          background: "#14122b",
          color: "#fff",
          fontFamily: font ? "BeVietnam" : "sans-serif",
        }}
      >
        <div style={{ fontSize: 34, color: "#fcd34d", fontWeight: 700 }}>
          🏆 BẢNG VÀNG TUẦN NÀY · {themeName.toUpperCase()}
        </div>
        <div style={{ fontSize: 220, fontWeight: 900, lineHeight: 1 }}>#{rank}</div>
        <div style={{ display: "flex", alignItems: "center", gap: 16, marginTop: 8 }}>
          <div style={{ fontSize: 64 }}>{style.icon}</div>
          <div style={{ fontSize: 56, fontWeight: 700 }}>{style.name}</div>
        </div>
        <div style={{ marginTop: 24, fontSize: 30, color: "#fcd34d", fontWeight: 700 }}>
          Bạn có lọt top? Chơi 60 giây →
        </div>
      </div>
    ) : (
      <div
        style={{
          width: 1200,
          height: 630,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          padding: 80,
          background: "#14122b",
          color: "#fff",
          fontFamily: font ? "BeVietnam" : "sans-serif",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
          <div style={{ fontSize: 110 }}>{style.icon}</div>
          <div style={{ display: "flex", flexDirection: "column" }}>
            <div style={{ fontSize: 30, color: "#fcd34d", fontWeight: 700 }}>
              ĐÚNG THIẾT KẾ · THẺ PHONG CÁCH
            </div>
            <div style={{ fontSize: 84, fontWeight: 900, lineHeight: 1.1 }}>{style.name}</div>
          </div>
        </div>
        <div style={{ marginTop: 24, fontSize: 36, color: "rgba(255,255,255,0.75)" }}>
          {style.tagline}
        </div>
        <div style={{ marginTop: 32, fontSize: 28, color: "#fcd34d", fontWeight: 700 }}>
          Bạn thì sao? Chơi 60 giây →
        </div>
      </div>
    ),
    {
      width: 1200,
      height: 630,
      fonts: font ? [{ name: "BeVietnam", data: font, weight: 700 }] : undefined,
    },
  );
}
