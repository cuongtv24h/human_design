/** Game runtime: hợp nhất nội dung built-in (TS) với cấu hình Game Manager (server).
 *
 * - Concept built-in: nội dung lấy từ TS, riêng bật/tắt + thứ tự lấy từ server.
 * - Concept custom: toàn bộ nội dung từ server.
 * - Kho câu hỏi = built-in (trừ câu bị ẩn) + câu custom đang bật.
 * - Server lỗi/offline: dùng nguyên TS, không chặn người chơi.
 */
import { BANKS, type BankQuestion } from "./bank";
import { THEMES, type GameTheme } from "./content";

/** 1 dòng concept từ GET /api/v1/public/game/config. */
export interface ServerConcept {
  slug: string;
  name: string;
  entry_label: string;
  entry_desc: string;
  icon: string;
  intro: string;
  bridge: string;
  enabled: boolean;
  is_builtin: boolean;
  sort_order: number;
}

export interface ServerCustomQuestion {
  id: number;
  concept_slug: string;
  qid: string;
  title: string;
  sit: string;
  options: { t: string; s: string }[];
  enabled: boolean;
}

export interface ServerNode {
  id: number;
  chapter_id: number;
  idx: number;
  mode: string;
  question_count: number;
  /** 0 = auto theo mode */
  time_limit: number;
  question_ids: string[];
  auto: boolean;
}

export interface ServerChapter {
  id: number;
  concept_slug: string;
  idx: number;
  name: string;
  icon: string;
  desc: string;
  nodes: ServerNode[];
}

export interface GameServerConfig {
  concepts: ServerConcept[];
  custom_questions: Record<string, ServerCustomQuestion[]>;
  disabled_builtin: Record<string, string[]>;
  structures: Record<string, ServerChapter[]>;
}

/** Concept sau khi hợp nhất — UI chỉ dùng kiểu này, không đọc THEMES trực tiếp. */
export interface RuntimeConcept {
  slug: string;
  name: string;
  entryLabel: string;
  entryDesc: string;
  icon: string;
  intro: string;
  bridge: string;
  enabled: boolean;
  isBuiltin: boolean;
  sort: number;
  questionCount: number;
}

const STYLE_IDS = ["khoi_xuong", "kien_tao", "dan_duong", "tam_guong"] as const;

/** Câu custom từ server -> BankQuestion (null nếu dữ liệu thiếu). */
export function customToBank(q: ServerCustomQuestion): BankQuestion | null {
  if (!q.qid || q.options.length !== 4) return null;
  const opts = [];
  for (const o of q.options) {
    if (!o.t || !(STYLE_IDS as readonly string[]).includes(o.s)) return null;
    opts.push({ t: o.t, s: o.s as (typeof STYLE_IDS)[number] });
  }
  return { id: q.qid, title: q.title, sit: q.sit, opts: opts as BankQuestion["opts"] };
}

/** Toàn bộ câu custom (đang bật) theo concept — để đăng ký vào map chấm điểm. */
export function customBankMap(config: GameServerConfig | null): Record<string, BankQuestion[]> {
  const out: Record<string, BankQuestion[]> = {};
  if (!config) return out;
  for (const [slug, list] of Object.entries(config.custom_questions)) {
    const bank = list.filter((q) => q.enabled).map(customToBank).filter((q) => q !== null);
    if (bank.length > 0) out[slug] = bank;
  }
  return out;
}

/** Kho câu hỏi thực tế của 1 concept: built-in (trừ câu bị ẩn) + custom đang bật. */
export function getRuntimeBank(slug: string, config: GameServerConfig | null): BankQuestion[] {
  const disabled = new Set(config?.disabled_builtin[slug] ?? []);
  const builtin = (BANKS[slug] ?? []).filter((q) => !disabled.has(q.id));
  const custom = (config?.custom_questions[slug] ?? [])
    .filter((q) => q.enabled)
    .map(customToBank)
    .filter((q) => q !== null);
  return [...builtin, ...custom];
}

/** Danh sách concept sau hợp nhất, đã sắp xếp (gồm cả concept đang tắt). */
export function getRuntimeConcepts(config: GameServerConfig | null): RuntimeConcept[] {
  const list: RuntimeConcept[] = [];
  const seen = new Set<string>();
  const push = (slug: string, override?: ServerConcept, sortFallback = 999) => {
    if (seen.has(slug)) return;
    seen.add(slug);
    const base = THEMES[slug];
    if (!base && !override) return;
    list.push({
      slug,
      name: base?.name ?? override?.name ?? slug,
      entryLabel: base?.entryLabel ?? override?.entry_label ?? "",
      entryDesc: base?.entryDesc ?? override?.entry_desc ?? "",
      icon: base?.icon ?? override?.icon ?? "🎮",
      intro: base?.intro ?? override?.intro ?? "",
      bridge: base?.bridge ?? override?.bridge ?? "",
      enabled: override?.enabled ?? true,
      isBuiltin: override?.is_builtin ?? true,
      sort: override?.sort_order ?? sortFallback,
      questionCount: getRuntimeBank(slug, config).length,
    });
  };
  if (config) {
    const sorted = [...config.concepts].sort(
      (a, b) => a.sort_order - b.sort_order || a.slug.localeCompare(b.slug),
    );
    for (const c of sorted) push(c.slug, c);
    for (const slug of Object.keys(THEMES)) push(slug);
  } else {
    Object.keys(THEMES).forEach((slug, i) => push(slug, undefined, i * 10));
  }
  return list.sort((a, b) => a.sort - b.sort || a.slug.localeCompare(b.slug));
}

/** Tìm 1 concept (kể cả đang tắt) — null nếu slug không tồn tại. */
export function getRuntimeTheme(
  slug: string,
  config: GameServerConfig | null,
): RuntimeConcept | null {
  return getRuntimeConcepts(config).find((c) => c.slug === slug) ?? null;
}

/** RuntimeConcept -> GameTheme cho PlayFlow/scoreQuiz (custom không có scenarios cũ). */
export function toGameTheme(rc: RuntimeConcept): GameTheme {
  return {
    slug: rc.slug,
    name: rc.name,
    entryLabel: rc.entryLabel,
    entryDesc: rc.entryDesc,
    icon: rc.icon,
    intro: rc.intro,
    bridge: rc.bridge,
    scenarios: THEMES[rc.slug]?.scenarios ?? [],
  };
}

/** Slug đề hôm nay: xoay vòng trên concept đang bật (fallback: tất cả). */
export function dailyRuntimeSlug(concepts: RuntimeConcept[], date = new Date()): string {
  const pool = concepts.filter((c) => c.enabled);
  const slugs = (pool.length > 0 ? pool : concepts).map((c) => c.slug);
  if (slugs.length === 0) return "nguoc-dong";
  const start = new Date(date.getFullYear(), 0, 0);
  const day = Math.floor((date.getTime() - start.getTime()) / 86400000);
  return slugs[day % slugs.length];
}

export function isBuiltinSlug(slug: string): boolean {
  return slug in THEMES;
}
