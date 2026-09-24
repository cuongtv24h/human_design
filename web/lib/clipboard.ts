// Copy text; falls back to a hidden textarea when the async Clipboard API is blocked
// (e.g. inside an embedded preview iframe). Returns false if both fail.
export async function copyText(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    const area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    let ok = false;
    try {
      ok = document.execCommand("copy");
    } catch {
      ok = false;
    }
    area.remove();
    return ok;
  }
}

export const absoluteUrl = (path: string) => (typeof window === "undefined" ? path : new URL(path, window.location.origin).toString());
