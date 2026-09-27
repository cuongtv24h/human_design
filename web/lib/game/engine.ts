// Engine game "Đúng Thiết Kế" (G2): chấm điểm, xoay biến thể, mã hóa, đối chiếu,
// so bài bạn bè, analytics.

import { api } from "@/lib/api";
import {
  DECISIONS,
  STYLES,
  type DecisionId,
  type GameScenario,
  type GameTheme,
  type StyleId,
} from "./content";

export interface QuizResult {
  theme: string;
  /** option id đã chọn theo thứ tự slot */
  answers: string[];
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

export function scoreQuiz(theme: GameTheme, answers: string[]): QuizResult {
  const totals: Record<StyleId, number> = { khoi_xuong: 0, kien_tao: 0, dan_duong: 0, tam_guong: 0 };
  let energy = 0;
  let pace = 0;
  const decisions: DecisionId[] = [];
  theme.scenarios.forEach((slot, i) => {
    const opt = slot.variants.flatMap((v) => v.options).find((o) => o.id === answers[i]);
    if (!opt) return;
    for (const s of STYLE_ORDER) totals[s] += opt.points[s] ?? 0;
    energy += opt.energy;
    pace += opt.pace;
    if (opt.decision) decisions.push(opt.decision);
  });
  const ranked = [...STYLE_ORDER].sort((a, b) => totals[b] - totals[a]);
  const n = Math.max(1, theme.scenarios.length);
  return {
    theme: theme.slug,
    answers,
    style: ranked[0],
    secondary: ranked[1],
    energy: Math.max(-1, Math.min(1, energy / n)),
    pace: Math.max(-1, Math.min(1, pace / n)),
    decision: decisions[0] ?? "truc_giac",
  };
}

/** Chọn ngẫu nhiên 1 biến thể cho mỗi slot (mỗi lượt chơi khác nhau). */
export function pickVariants(theme: GameTheme): GameScenario[] {
  return theme.scenarios.map((slot) => {
    const vs = slot.variants.length > 0 ? slot.variants : [];
    return vs[Math.floor(Math.random() * vs.length)];
  });
}

/** Mã hóa kết quả vào URL (?d=...) để share không cần DB. */
export function encodeResult(result: QuizResult): string {
  const raw = JSON.stringify({ t: result.theme, a: result.answers, v: 1 });
  return btoa(unescape(encodeURIComponent(raw))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

export function decodeResultParam(param: string | null): { theme: string; answers: string[] } | null {
  if (!param) return null;
  try {
    const b64 = param.replace(/-/g, "+").replace(/_/g, "/");
    const raw = decodeURIComponent(escape(atob(b64)));
    const data = JSON.parse(raw) as { t?: unknown; a?: unknown };
    if (typeof data.t !== "string" || !Array.isArray(data.a)) return null;
    const answers = data.a.filter((x): x is string => typeof x === "string").slice(0, 10);
    return { theme: data.t, answers };
  } catch {
    return null;
  }
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

/** Phong cách hành xử "giống như" Type nào — chỉ dùng để đối chiếu, không phải kết luận. */
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

/** % lệch giữa hành xử và thiết kế — chỉ số vui, ổn định theo đáp án. */
export function deviationPct(result: QuizResult, chartType: string): number {
  const like = STYLE_LIKE_TYPE[result.style];
  const match = like === chartType || (like === "Generator" && chartType === "Manifesting Generator");
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
  const match = like === chart.type || (like === "Generator" && chart.type === "Manifesting Generator");
  const typeVn = chart.type_vn || chart.type;
  if (match) {
    return {
      match: true,
      headline: `Khớp ${100 - deviationPct(result, chart.type)}% — bạn đang sống đúng thiết kế.`,
      body: `Cách bạn hành xử ngoài đời (${style.name.toLowerCase()}) trùng với thiết kế gốc (${typeVn}). Đây là trạng thái mà nhiều người phải mất năm mới tìm lại được — giữ vững nó.`,
      insight: `Chiến lược của bạn là “${chart.strategy}”. Càng tuân thủ nó, mọi thứ càng trôi. Báo cáo đầy đủ sẽ chỉ bạn áp dụng chiến lược này vào công việc, tiền bạc và các mối quan hệ.`,
    };
  }
  const key = `${result.style}__${chart.type}`;
  const insights: Record<string, string> = {
    khoi_xuong__Projector:
      "Bạn liên tục lao ra khởi xướng, trong khi thiết kế của bạn phát huy mạnh nhất khi được mời đúng chỗ. Càng gồng, càng gặp tường và cay đắng — không phải vì bạn kém, mà vì sai cách dùng lực.",
    khoi_xuong__Reflector:
      "Bạn hành động như người mở đường, nhưng thiết kế của bạn cần thời gian thấm và môi trường đúng. Vội vàng khiến bạn quyết sai rồi đổ lỗi cho bản thân.",
    dan_duong__Generator:
      "Bạn đứng ngoài quan sát và chờ đợi, trong khi động cơ của bạn sinh ra để phản hồi và cày. Nhàn quá lâu khiến bạn bức bối — không phải vì thiếu việc, mà vì thiếu việc đáng làm.",
    dan_duong__Manifesting_Generator:
      "Bạn đứng ngoài quan sát và chờ đợi, trong khi động cơ của bạn sinh ra để phản hồi và cày. Nhàn quá lâu khiến bạn bức bối — không phải vì thiếu việc, mà vì thiếu việc đáng làm.",
    tam_guong__Manifestor:
      "Bạn hòa theo cảm xúc và tiêu chuẩn của người xung quanh, trong khi thiết kế của bạn cần không gian riêng để khởi xướng. Càng chiều lòng tất cả, bạn càng mất tiếng nói của mình.",
    tam_guong__Generator:
      "Bạn gật đầu với kỳ vọng của người khác, trong khi pin của bạn chỉ sạc khi làm việc mình thật sự muốn. Kiệt sức của bạn không đến từ việc nhiều — mà từ việc sai.",
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
