import { ImageResponse } from "next/og";
import { STYLES, type StyleId } from "@/lib/game/content";

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
  const id = (searchParams.get("style") ?? "dan_duong") as StyleId;
  const style = STYLES[id] ?? STYLES.dan_duong;
  const font = await vietnameseFont();
  return new ImageResponse(
    (
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
