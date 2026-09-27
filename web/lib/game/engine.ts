// Engine game "Đúng Thiết Kế" (G2): chấm điểm, xoay biến thể, mã hóa, đối chiếu,
// so bài bạn bè, analytics.

import { api } from "@/lib/api";
import {
  DECISIONS,
  STYLES,
  THEMES,
  type DecisionId,
  type GameTheme,
  type StyleId,
} from "./content";
import { BANKS, type BankQuestion } from "./bank";

export interface QuizResult {
  theme: string;
  /** option id đã chọn theo thứ tự câu hỏi */
  answers: string[];
  /** seed rút đề (v2) — so bài dùng chung để ra cùng 16 câu */
  seed?: string;
  style: StyleId;
  secondary: StyleId;
  /** -1..1 */
  energy: number;
  /** -1..1 */
  pace: number;
  decision: DecisionId;
}

export interface MiniChart {
  type: string;
  type_vn: string;
  strategy: string;
  authority: string;
  profile: string;
  definition: string;
  incarnation_cross: string;
  defined_centers: number;
}

export interface GameChartOut {
  summary: MiniChart;
  centers: string[];
  subject_display: string;
}

const STYLE_ORDER: StyleId[] = ["khoi_xuong", "kien_tao", "dan_duong", "tam_guong"];

interface ScoredOption {
  theme: string;
  points: Record<StyleId, number>;
  energy: number;
  pace: number;
  decision?: DecisionId;
}

/** Vector năng lượng/nhịp mặc định theo phong cách (cho đáp án kho mới). */
const STYLE_VECTORS: Record<StyleId, { energy: number; pace: number; decision: DecisionId }> = {
  khoi_xuong: { energy: 0, pace: 1, decision: "truc_giac" },
  kien_tao: { energy: 1, pace: 0, decision: "cam_xuc" },
  dan_duong: { energy: 0, pace: -1, decision: "logic" },
  tam_guong: { energy: -1, pace: -1, decision: "hoi_han" },
};

let optionMap: Map<string, ScoredOption> | null = null;

/** Map tra cứu đáp án: kho mới + scenario cũ (link ?d= đời cũ vẫn chấm y nguyên). */
function getOptionMap(): Map<string, ScoredOption> {
  if (optionMap) return optionMap;
  const map = new Map<string, ScoredOption>();
  for (const [slug, bank] of Object.entries(BANKS)) {
    for (const q of bank) {
      for (let oi = 0; oi < q.opts.length; oi++) {
        const [id, entry] = bankOptionEntry(slug, q, oi);
        map.set(id, entry);
      }
    }
  }
  for (const theme of Object.values(THEMES)) {
    for (const slot of theme.scenarios) {
      for (const v of slot.variants) {
        for (const o of v.options) {
          if (!map.has(o.id)) {
            map.set(o.id, {
              theme: theme.slug,
              points: { ...o.points },
              energy: o.energy,
              pace: o.pace,
              decision: o.decision,
            });
          }
        }
      }
    }
  }
  optionMap = map;
  return map;
}

function bankOptionEntry(slug: string, q: BankQuestion, oi: number): [string, ScoredOption] {
  const o = q.opts[oi];
  const id = `${q.id}${"abcd"[oi]}`;
  const v = STYLE_VECTORS[o.s];
  const je = ((hashSeed(id) % 31) / 100 - 0.15) * 2;
  const jp = ((hashSeed(`p${id}`) % 31) / 100 - 0.15) * 2;
  const points: Record<StyleId, number> = { khoi_xuong: 0, kien_tao: 0, dan_duong: 0, tam_guong: 0 };
  points[o.s] = 2;
  return [id, { theme: slug, points, energy: v.energy + je, pace: v.pace + jp, decision: v.decision }];
}

/** Đăng ký đáp án custom từ Game Manager vào map chấm điểm (gọi khi config về). */
export function registerCustomOptions(custom: Record<string, BankQuestion[]>): void {
  const map = getOptionMap();
  for (const [slug, bank] of Object.entries(custom)) {
    for (const q of bank) {
      for (let oi = 0; oi < q.opts.length; oi++) {
        const [id, entry] = bankOptionEntry(slug, q, oi);
        if (!map.has(id)) map.set(id, entry);
      }
    }
  }
}

export function scoreQuiz(theme: GameTheme, answers: string[], weights?: number[]): QuizResult {
  const map = getOptionMap();
  const totals: Record<StyleId, number> = { khoi_xuong: 0, kien_tao: 0, dan_duong: 0, tam_guong: 0 };
  let energy = 0;
  let pace = 0;
  let matched = 0;
  let weightSum = 0;
  const votes: Record<DecisionId, number> = { truc_giac: 0, cam_xuc: 0, logic: 0, hoi_han: 0 };
  const firstSeen: DecisionId[] = [];
  for (let ai = 0; ai < answers.length; ai++) {
    const opt = map.get(answers[ai]);
    if (!opt || opt.theme !== theme.slug) continue;
    const w = weights?.[ai] ?? 1;
    matched += 1;
    weightSum += w;
    for (const st of STYLE_ORDER) totals[st] += (opt.points[st] ?? 0) * w;
    energy += opt.energy * w;
    pace += opt.pace * w;
    if (opt.decision) {
      votes[opt.decision] += w;
      if (!firstSeen.includes(opt.decision)) firstSeen.push(opt.decision);
    }
  }
  const ranked = [...STYLE_ORDER].sort((a, b) => totals[b] - totals[a]);
  const n = Math.max(1, weightSum);
  let decision: DecisionId = "truc_giac";
  let best = 0;
  for (const d of firstSeen) {
    if (votes[d] > best) {
      best = votes[d];
      decision = d;
    }
  }
  return {
    theme: theme.slug,
    answers,
    style: ranked[0],
    secondary: ranked[1],
    energy: Math.max(-1, Math.min(1, energy / n)),
    pace: Math.max(-1, Math.min(1, pace / n)),
    decision,
  };
}

export const QUESTIONS_PER_PLAY = 16;

export interface PlayOption {
  id: string;
  label: string;
}

export interface PlayQuestion {
  qid: string;
  title: string;
  situation: string;
  options: PlayOption[];
}

function shuffled<T>(arr: T[], rand: () => number): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

/** 1 câu kho -> câu chơi (xáo đáp án theo seed) — màn nào seed nấy, đề cố định. */
export function toPlayQuestion(themeSlug: string, seed: string, q: BankQuestion): PlayQuestion {
  const order = shuffled([0, 1, 2, 3], mulberry32(hashSeed(`o:${seed}:${q.id}`)));
  return {
    qid: q.id,
    title: q.title,
    situation: q.sit,
    options: order.map((oi) => ({ id: `${q.id}${"abcd"[oi]}`, label: q.opts[oi].t })),
  };
}

/** Rút n câu khác nhau từ kho + xáo thứ tự đáp án — cùng seed ra cùng đề. */
export function sampleQuestions(
  themeSlug: string,
  seed: string,
  n = QUESTIONS_PER_PLAY,
  bankOverride?: BankQuestion[],
): PlayQuestion[] {
  const bank = bankOverride ?? BANKS[themeSlug] ?? [];
  const picked = shuffled(bank, mulberry32(hashSeed(`q:${seed}:${themeSlug}`))).slice(
    0,
    Math.min(n, bank.length),
  );
  return picked.map((q) => toPlayQuestion(themeSlug, seed, q));
}

export function randomSeed(): string {
  return `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 10)}`;
}

/** Mã hóa kết quả vào URL (?d=...) để share không cần DB. v2 kèm seed rút đề. */
export function encodeResult(result: QuizResult): string {
  const raw = JSON.stringify({ t: result.theme, a: result.answers, v: 2, s: result.seed ?? "" });
  return btoa(unescape(encodeURIComponent(raw))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

export function decodeResultParam(
  param: string | null,
): { theme: string; answers: string[]; seed?: string } | null {
  if (!param) return null;
  try {
    const b64 = param.replace(/-/g, "+").replace(/_/g, "/");
    const raw = decodeURIComponent(escape(atob(b64)));
    const data = JSON.parse(raw) as { t?: unknown; a?: unknown; s?: unknown };
    if (typeof data.t !== "string" || !Array.isArray(data.a)) return null;
    const answers = data.a.filter((x): x is string => typeof x === "string").slice(0, 25);
    const seed = typeof data.s === "string" && data.s ? data.s : undefined;
    return { theme: data.t, answers, seed };
  } catch {
    return null;
  }
}

/** Phong cách của 1 đáp án (thẻ Soi Gương) — đáp án bank luôn thuộc đúng 1 style. */
export function optionStyle(id: string): StyleId | null {
  const opt = getOptionMap().get(id);
  if (!opt) return null;
  let best: StyleId = STYLE_ORDER[0];
  let bestV = -Infinity;
  for (const st of STYLE_ORDER) {
    const v = opt.points[st] ?? 0;
    if (v > bestV) {
      bestV = v;
      best = st;
    }
  }
  return best;
}

export function styleName(id: StyleId): string {
  return STYLES[id]?.name ?? id;
}

export function decisionName(id: DecisionId): string {
  return DECISIONS[id]?.name ?? id;
}

export function energyLabel(v: number): string {
  if (v > 0.33) return "Pin bền bỉ";
  if (v < -0.33) return "Năng lượng theo đợt";
  return "Năng lượng linh hoạt";
}

export function paceLabel(v: number): string {
  if (v > 0.33) return "Thích lao ngay";
  if (v < -0.33) return "Thích chờ thời";
  return "Tùy tình huống";
}

/** Phong cách hành xử "giống như" Type nào — chỉ dùng để đối chiếu, không phải kết luận.
 * Game có 4 phong cách; MG (Manifesting Generator) thuộc họ Generator (cùng pin Sacral)
 * nên khớp với phong cách Kiến Tạo — xem typeMatches. */
const STYLE_LIKE_TYPE: Record<StyleId, string> = {
  khoi_xuong: "Manifestor",
  kien_tao: "Generator",
  dan_duong: "Projector",
  tam_guong: "Reflector",
};

function hashAnswers(answers: string[]): number {
  const s = answers.join("|");
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
  return h;
}

/** MG thuộc họ Generator (cùng pin Sacral) nên khớp với phong cách Kiến Tạo. */
function typeMatches(like: string, chartType: string): boolean {
  return like === chartType || (like === "Generator" && chartType === "Manifesting Generator");
}

/** % lệch giữa hành xử và thiết kế — chỉ số vui, ổn định theo đáp án. */
export function deviationPct(result: QuizResult, chartType: string): number {
  const like = STYLE_LIKE_TYPE[result.style];
  const match = typeMatches(like, chartType);
  const h = hashAnswers(result.answers) % 100;
  return match ? 12 + (h % 18) : 52 + (h % 33);
}

export interface Contrast {
  match: boolean;
  headline: string;
  body: string;
  insight: string;
}

export function contrastFor(result: QuizResult, chart: MiniChart): Contrast {
  const style = STYLES[result.style];
  const like = STYLE_LIKE_TYPE[result.style];
  const match = typeMatches(like, chart.type);
  const typeVn = chart.type_vn || chart.type;
  if (match) {
    return {
      match: true,
      headline: `Khớp ${100 - deviationPct(result, chart.type)}% — bạn đang sống đúng thiết kế.`,
      body: `Cách bạn hành xử ngoài đời (${style.name.toLowerCase()}) trùng với thiết kế gốc (${typeVn}). Đây là trạng thái mà nhiều người phải mất năm mới tìm lại được — giữ vững nó.`,
      insight:
        chart.type === "Manifesting Generator"
          ? "Bạn thuộc nhóm MG — dòng Generator đa hướng, nhanh nhất trong 5 Type. Chiến lược của bạn là “đáp ứng rồi thông báo”: chờ việc gọi, bung sức làm, và nhớ báo cho người xung quanh mỗi khi bạn bẻ lái. Báo cáo đầy đủ sẽ chỉ bạn dùng tốc độ này mà không đốt cháy mình và người khác."
          : `Chiến lược của bạn là “${chart.strategy}”. Càng tuân thủ nó, mọi thứ càng trôi. Báo cáo đầy đủ sẽ chỉ bạn áp dụng chiến lược này vào công việc, tiền bạc và các mối quan hệ.`,
    };
  }
  const key = `${result.style}__${chart.type}`;
  const insights: Record<string, string> = {
    khoi_xuong__Projector:
      "Bạn liên tục lao ra khởi xướng, trong khi thiết kế của bạn phát huy mạnh nhất khi được mời đúng chỗ. Càng gồng, càng gặp tường và cay đắng — không phải vì bạn kém, mà vì sai cách dùng lực.",
    khoi_xuong__Reflector:
      "Bạn hành động như người mở đường, nhưng thiết kế của bạn cần thời gian thấm và môi trường đúng. Vội vàng khiến bạn quyết sai rồi đổ lỗi cho bản thân.",
    khoi_xuong__Manifesting_Generator:
      "Bạn lao ra mở đường như Manifestor, nhưng pin Sacral của MG cần “đáp ứng” trước khi bung. Khởi xướng đúng việc thì bạn nhanh gấp đôi người thường; khởi xướng bừa thì vừa giận (vì bị cản) vừa kiệt (vì sai việc) — combo mệt nhất trong 5 Type.",
    dan_duong__Generator:
      "Bạn đứng ngoài quan sát và chờ đợi, trong khi động cơ của bạn sinh ra để phản hồi và cày. Nhàn quá lâu khiến bạn bức bối — không phải vì thiếu việc, mà vì thiếu việc đáng làm.",
    dan_duong__Manifesting_Generator:
      "Bạn đứng ngoài quan sát và chờ đợi, trong khi động cơ của bạn sinh ra để phản hồi và cày. Nhàn quá lâu khiến bạn bức bối — không phải vì thiếu việc, mà vì thiếu việc đáng làm.",
    tam_guong__Manifestor:
      "Bạn hòa theo cảm xúc và tiêu chuẩn của người xung quanh, trong khi thiết kế của bạn cần không gian riêng để khởi xướng. Càng chiều lòng tất cả, bạn càng mất tiếng nói của mình.",
    tam_guong__Generator:
      "Bạn gật đầu với kỳ vọng của người khác, trong khi pin của bạn chỉ sạc khi làm việc mình thật sự muốn. Kiệt sức của bạn không đến từ việc nhiều — mà từ việc sai.",
    tam_guong__Manifesting_Generator:
      "Bạn gật theo kỳ vọng của người khác, trong khi MG sinh ra để đáp ứng rồi bẻ lái theo ý mình. Càng “ngoan”, bạn càng kiệt: pin Sacral chỉ sạc khi bạn được làm thứ mình thật sự muốn, theo cách của mình.",
    kien_tao__Projector:
      "Bạn cày như máy để chứng minh giá trị, trong khi thiết kế của bạn không có pin cày — sức mạnh của bạn nằm ở tầm nhìn. Sập nguồn rồi đổ tại lười là vòng lặp cần phá vỡ đầu tiên.",
    kien_tao__Manifestor:
      "Bạn vùi đầu cày cuốc và chờ ai đó công nhận, trong khi thiết kế của bạn cần tự mở đường và thông báo cho người khác biết. Báo cáo đầy đủ sẽ chỉ bạn chuyển từ “làm thuê cho kỳ vọng” sang “làm chủ cuộc chơi”.",
  };
  const insight =
    insights[key.replace(/ /g, "_")] ??
    `Bạn đang hành xử như ${style.name.toLowerCase()}, nhưng thiết kế gốc của bạn là ${typeVn} với chiến lược “${chart.strategy}”. Khoảng cách này chính là nguồn cơn của cảm giác “sai sai” mà bạn mang bấy lâu.`;
  return {
    match: false,
    headline: `Lệch ${deviationPct(result, chart.type)}% — bạn đang gồng theo một khuôn không phải của mình.`,
    body: `Phản xạ ngoài đời của bạn giống ${style.name.toLowerCase()}, nhưng bản thiết kế nguyên bản ghi bạn là ${typeVn}. Tin tốt: chỉ cần biết mình lệch ở đâu, bạn đã đi được nửa đường trở về.`,
    insight,
  };
}

// --- so bài bạn bè (G2, không cần ngày sinh) ---

const PAIR_VERDICTS: Record<string, string> = {
  "khoi_xuong|khoi_xuong": "Hai ngọn lửa — bùng nổ hoặc cháy nhà. Phân vai rõ thì bất khả chiến bại.",
  "kien_tao|kien_tao": "Hai cỗ máy — êm và bền, miễn là đừng cùng kiệt pin một lúc.",
  "dan_duong|dan_duong": "Hai nhà chiến lược — nhìn ra mọi thứ, trừ việc ai sẽ làm.",
  "tam_guong|tam_guong": "Hai tấm gương — thấu hiểu nhau sâu, nhưng cần neo ngoài để khỏi trôi.",
  "khoi_xuong|kien_tao": "Lửa + động cơ: một người mở đường, một người cày — combo kinh điển.",
  "dan_duong|khoi_xuong": "Người mở đường + người chỉ hướng: đi nhanh mà không lạc.",
  "khoi_xuong|tam_guong": "Lửa mạnh gặp gương nhạy — truyền cảm hứng hoặc thiêu rụi, tùy tiết chế.",
  "dan_duong|kien_tao": "Động cơ + hoa tiêu: cày khỏe, đi đúng — cặp bài trùng công việc.",
  "kien_tao|tam_guong": "Cỗ máy + tấm gương: một bên làm, một bên cảm — cần nói ra nhu cầu.",
  "dan_duong|tam_guong": "Mắt quan sát + lòng thấu cảm: hiểu nhau không cần nói, nhưng cần người hành động.",
};

function pairKey(a: StyleId, b: StyleId): string {
  return [a, b].sort().join("|");
}

export interface Compatibility {
  score: number;
  verdict: string;
  note: string;
}

export function compatibility(a: QuizResult, b: QuizResult): Compatibility {
  const energyFit = 1 - Math.abs(a.energy - b.energy) / 2;
  const paceFit = 1 - Math.abs(a.pace - b.pace) / 2;
  let bonus = 2;
  if (a.style === b.style) bonus = 10;
  else if (
    pairKey(a.style, b.style) === "dan_duong|khoi_xuong" ||
    pairKey(a.style, b.style) === "dan_duong|kien_tao"
  )
    bonus = 6;
  const jitter = hashAnswers([...a.answers, ...b.answers]) % 7;
  const score = Math.max(38, Math.min(97, Math.round(52 + 18 * energyFit + 14 * paceFit + bonus + jitter - 3)));
  const verdict = PAIR_VERDICTS[pairKey(a.style, b.style)] ?? "Hai tần số khác nhau — càng hiểu nhau càng mạnh.";
  const note =
    a.decision === b.decision
      ? `Cùng kiểu quyết định (${decisionName(a.decision).toLowerCase()}) nên hai bạn ít cãi vặt, nhưng cũng dễ cùng mù một hướng.`
      : "Khác kiểu quyết định: một bên muốn chốt nhanh, một bên cần thời gian — chốt deadline chung trước khi bàn tiếp.";
  return { score, verdict, note };
}

// --- analytics ẩn danh (fire-and-forget) ---

export function gameSessionId(): string {
  try {
    const k = "hd_game_sid";
    let sid = localStorage.getItem(k);
    if (!sid) {
      sid = `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 10)}`;
      localStorage.setItem(k, sid);
    }
    return sid;
  } catch {
    return "nosession";
  }
}

export type GameEventName =
  | "game_start"
  | "game_complete"
  | "bridge_view"
  | "bridge_submit"
  | "share_click"
  | "cta_click"
  | "lead_submit"
  | "compare_view"
  | "compare_done";

export function trackGameEvent(name: GameEventName, theme = ""): void {
  try {
    void api
      .post("/public/game/events", { name, theme, session_id: gameSessionId() })
      .catch(() => undefined);
  } catch {
    /* bỏ qua — analytics không được làm hỏng trải nghiệm */
  }
}

/* G3: đề hôm nay + bảng vàng + nhắc chơi lại */

export function hashSeed(str: string): number {
  let h = 2166136261;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

export function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function dailySeed(date = new Date()): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

/** Mỗi ngày 1 theme, xoay vòng — đề hôm nay của cả cộng đồng. */
export function dailyTheme(date = new Date()): GameTheme {
  const slugs = Object.keys(THEMES);
  const start = new Date(date.getFullYear(), 0, 0);
  const day = Math.floor((date.getTime() - start.getTime()) / 86400000);
  return THEMES[slugs[day % slugs.length]];
}

export function dailyLabel(date = new Date()): string {
  return `${String(date.getDate()).padStart(2, "0")}/${String(date.getMonth() + 1).padStart(2, "0")}`;
}

const PLAYED_KEY = "ddtk-played";

export interface PlayedState {
  themes: string[];
  styles: StyleId[];
  lastStyle: StyleId | null;
}

export function getPlayed(): PlayedState {
  const empty: PlayedState = { themes: [], styles: [], lastStyle: null };
  if (typeof window === "undefined") return empty;
  try {
    const raw = window.localStorage.getItem(PLAYED_KEY);
    if (!raw) return empty;
    const parsed = JSON.parse(raw) as Partial<PlayedState>;
    return {
      themes: Array.isArray(parsed.themes) ? parsed.themes.filter((t) => typeof t === "string") : [],
      styles: Array.isArray(parsed.styles)
        ? parsed.styles.filter((t): t is StyleId => typeof t === "string")
        : [],
      lastStyle: typeof parsed.lastStyle === "string" ? (parsed.lastStyle as StyleId) : null,
    };
  } catch {
    return empty;
  }
}

export function recordPlayed(theme: string, style: StyleId): void {
  if (typeof window === "undefined") return;
  const cur = getPlayed();
  const themes = cur.themes.includes(theme) ? cur.themes : [...cur.themes, theme];
  const styles = cur.styles.includes(style) ? cur.styles : [...cur.styles, style];
  try {
    window.localStorage.setItem(PLAYED_KEY, JSON.stringify({ themes, styles, lastStyle: style }));
  } catch {
    /* đầy bộ nhớ thì bỏ qua */
  }
}

/** Ghi điểm lên bảng vàng tuần, trả về thứ hạng (null nếu lỗi mạng). */
export async function submitScore(
  theme: string,
  style: StyleId,
  deviation: number,
): Promise<number | null> {
  try {
    const out = await api.post<{ ok: boolean; rank: number }>("/public/game/scores", {
      theme,
      style,
      deviation,
      session_id: gameSessionId(),
    });
    return typeof out.rank === "number" ? out.rank : null;
  } catch {
    return null;
  }
}

/* G4: huy hiệu + streak điểm danh */

export interface BadgeDef {
  id: string;
  icon: string;
  name: string;
  desc: string;
}

export const BADGES: BadgeDef[] = [
  { id: "explorer", icon: "🧭", name: "Nhà Thám Hiểm", desc: "Chơi đủ 3 cửa" },
  { id: "chameleon", icon: "🦎", name: "Tắc Kè Hoa", desc: "Ra đủ 4 phong cách" },
  { id: "daily", icon: "📅", name: "Đúng Giờ", desc: "Hoàn thành đề hôm nay" },
  { id: "streak3", icon: "🔥", name: "Lửa Bền", desc: "Streak 3 ngày liên tiếp" },
  { id: "streak7", icon: "🌋", name: "Bất Diệt", desc: "Streak 7 ngày liên tiếp" },
  { id: "challenger", icon: "⚔️", name: "Thách Đấu", desc: "So bài với bạn bè" },
  { id: "mirror", icon: "🪞", name: "Soi Gương", desc: "Đối chiếu thiết kế gốc" },
  { id: "top3", icon: "🏆", name: "Top Vàng", desc: "Lọt top 3 bảng tuần" },
];

const BADGE_KEY = "ddtk-badges";

function readBadges(): { unlocked: string[]; fresh: string[] } {
  if (typeof window === "undefined") return { unlocked: [], fresh: [] };
  try {
    const parsed = JSON.parse(window.localStorage.getItem(BADGE_KEY) ?? "{}") as {
      unlocked?: unknown;
      fresh?: unknown;
    };
    const clean = (v: unknown) => (Array.isArray(v) ? v.filter((t) => typeof t === "string") : []);
    return { unlocked: clean(parsed.unlocked), fresh: clean(parsed.fresh) };
  } catch {
    return { unlocked: [], fresh: [] };
  }
}

export function getBadges(): string[] {
  return readBadges().unlocked;
}

export function peekFreshBadges(): string[] {
  return readBadges().fresh;
}

/** Mở huy hiệu, trả true nếu vừa mở mới (để khoe). */
export function unlockBadge(id: string): boolean {
  if (typeof window === "undefined") return false;
  const cur = readBadges();
  if (cur.unlocked.includes(id)) return false;
  try {
    window.localStorage.setItem(
      BADGE_KEY,
      JSON.stringify({ unlocked: [...cur.unlocked, id], fresh: [...cur.fresh, id] }),
    );
  } catch {
    /* đầy bộ nhớ thì bỏ qua */
  }
  return true;
}

/** Lấy + xóa danh sách vừa mở (để hiện 1 lần trên màn hình done). */
export function takeFreshBadges(): BadgeDef[] {
  const cur = readBadges();
  if (typeof window !== "undefined") {
    try {
      window.localStorage.setItem(BADGE_KEY, JSON.stringify({ unlocked: cur.unlocked, fresh: [] }));
    } catch {
      /* bỏ qua */
    }
  }
  return BADGES.filter((b) => cur.fresh.includes(b.id));
}

/** Gọi sau recordPlayed khi xong 1 ván chơi/so bài. */
export function checkPlayBadges(opts: { daily?: boolean; streak?: number; compare?: boolean }): void {
  const p = getPlayed();
  if (p.themes.length >= Object.keys(THEMES).length) unlockBadge("explorer");
  if (p.styles.length >= Object.keys(STYLES).length) unlockBadge("chameleon");
  if (opts.daily) unlockBadge("daily");
  const streak = opts.streak ?? 0;
  if (streak >= 7) unlockBadge("streak7");
  else if (streak >= 3) unlockBadge("streak3");
  if (opts.compare) unlockBadge("challenger");
}

export interface StreakOut {
  streak: number;
  today_done: boolean;
}

/** Điểm danh đề hôm nay (null nếu lỗi mạng). */
export async function submitStreak(): Promise<StreakOut | null> {
  try {
    return await api.post<StreakOut>("/public/game/streak", { session_id: gameSessionId() });
  } catch {
    return null;
  }
}

/** Xem streak mà không điểm danh (null nếu lỗi mạng). */
export async function fetchStreak(): Promise<StreakOut | null> {
  try {
    return await api.get<StreakOut>(
      `/public/game/streak?session_id=${encodeURIComponent(gameSessionId())}`,
    );
  } catch {
    return null;
  }
}
