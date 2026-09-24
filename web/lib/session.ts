// Session fallback for embedded previews.
//
// Normally the session lives only in the httpOnly cookie. When the admin runs inside a
// cross-site iframe (e.g. a hosted preview), browsers like Safari — or Chrome with
// third-party cookies blocked — drop that cookie, so login "succeeds" but every next
// request says "Bạn cần đăng nhập". In that case only, the token is kept in this tab's
// sessionStorage and sent as a Bearer header (and ?access_token= for <img>/<iframe>/links).

const KEY = "hd-session";

export function isEmbedded(): boolean {
  if (typeof window === "undefined") return false;
  try {
    return window.self !== window.top;
  } catch {
    return true; // cross-origin parent
  }
}

export function getSessionToken(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return sessionStorage.getItem(KEY);
  } catch {
    return null;
  }
}

export function setSessionToken(token: string | null | undefined): void {
  try {
    if (token) sessionStorage.setItem(KEY, token);
    else sessionStorage.removeItem(KEY);
  } catch {
    /* storage disabled: cookie-only */
  }
}
