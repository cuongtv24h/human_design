/** Chặng game kiểu Mario: Thế giới (concept) → Chương → Màn (node).
 *
 * Mỗi màn = 8 câu hỏi CỐ ĐỊNH (cắt từ kho runtime theo thứ tự qid) nên mọi
 * người chơi cùng đi một bản đồ giống nhau. Hoàn thành màn mở khóa màn tiếp theo.
 */
import type { BankQuestion } from "./bank";
import { hashSeed, mulberry32 } from "./engine";
import type { GameServerConfig } from "./runtime";

export type NodeMode = "normal" | "speed" | "boss";

export interface StageChapter {
  name: string;
  icon: string;
  desc: string;
}

export interface StageNode {
  index: number;
  chapter: number;
  nodeInChapter: number;
  mode: NodeMode;
}

export const QUESTIONS_PER_NODE = 8;
export const NODES_PER_CHAPTER = 3;
export const CHAPTERS_PER_WORLD = 4;
/** 12 màn × 8 câu = 96 câu, vừa khít kho 100 câu (dư cho tự do + đề hôm nay). */
export const MAX_NODES = NODES_PER_CHAPTER * CHAPTERS_PER_WORLD;
export const COMBO_THRESHOLD_S = 5;
export const SPEED_TIME_LIMIT_S = 10;
export const BOSS_TIME_LIMIT_S = 8;
export const HELPERS_PER_NODE = 2;
export const COMBO_STAR_GOAL = 4;

const CHAPTER_COPY: Record<string, StageChapter[]> = {
  "nguoc-dong": [
    { name: "Thức Tỉnh", icon: "🌅", desc: "Nhận ra mình đang sống theo kỳ vọng của người khác." },
    { name: "Va Chạm", icon: "💥", desc: "Những tình huống đầu tiên thử phản xạ thật của bạn." },
    { name: "Soi Gương", icon: "🪞", desc: "Nhìn thẳng vào cách mình ra quyết định mỗi ngày." },
    { name: "Bứt Phá", icon: "🚀", desc: "Trùm cuối: sống đúng thiết kế, hay quay về lối cũ?" },
  ],
  "thuong-vu": [
    { name: "Nhận Dự Án", icon: "📋", desc: "Dự án mới, sếp mới, áp lực mới." },
    { name: "Deadline Dí", icon: "⏰", desc: "Mọi thứ cháy cùng lúc — bạn ưu tiên gì?" },
    { name: "Đàm Phán", icon: "🤝", desc: "Bàn đàm phán là nơi lộ rõ bản chất nhất." },
    { name: "Chốt Deal", icon: "🏆", desc: "Trùm cuối: thương vụ sinh tử quyết định tất cả." },
  ],
  "linh-thu": [
    { name: "Vào Rừng", icon: "🌲", desc: "Bước vào khu rừng nơi linh thú soi thấu lòng người." },
    { name: "Dấu Vết", icon: "🐾", desc: "Mỗi lựa chọn để lại một dấu vết trong rừng." },
    { name: "Đối Mặt", icon: "🦁", desc: "Linh thú hiện thân từ chính phản xạ của bạn." },
    { name: "Linh Thú Vương", icon: "👑", desc: "Trùm cuối: thuần hóa được nó, hay bị nó nuốt?" },
  ],
};

const GENERIC_CHAPTERS: StageChapter[] = [
  { name: "Chương 1", icon: "🗺️", desc: "Bắt đầu hành trình." },
  { name: "Chương 2", icon: "🧭", desc: "Đi sâu hơn vào thế giới này." },
  { name: "Chương 3", icon: "⚔️", desc: "Thử thách tăng dần." },
  { name: "Chương 4", icon: "👑", desc: "Trùm cuối đang chờ." },
];

export function getChapters(slug: string): StageChapter[] {
  return CHAPTER_COPY[slug] ?? GENERIC_CHAPTERS;
}

/** Chương 1–3: thường, thường, tốc độ. Chương 4: thường, tốc độ, trùm. */
export function nodeMode(chapter: number, nodeInChapter: number): NodeMode {
  if (chapter === CHAPTERS_PER_WORLD - 1 && nodeInChapter === NODES_PER_CHAPTER - 1) return "boss";
  if (nodeInChapter === NODES_PER_CHAPTER - 1) return "speed";
  if (chapter === CHAPTERS_PER_WORLD - 1 && nodeInChapter === NODES_PER_CHAPTER - 2) return "speed";
  return "normal";
}

export function buildNodes(count: number): StageNode[] {
  return Array.from({ length: Math.max(0, count) }, (_, index) => {
    const chapter = Math.floor(index / NODES_PER_CHAPTER);
    const nodeInChapter = index % NODES_PER_CHAPTER;
    return { index, chapter, nodeInChapter, mode: nodeMode(chapter, nodeInChapter) };
  });
}

export function nodeCountFor(bankLen: number): number {
  if (bankLen <= 0) return 0;
  return Math.min(MAX_NODES, Math.max(1, Math.ceil(bankLen / QUESTIONS_PER_NODE)));
}

/** Cắt 1 khúc `count` câu từ vị trí start; thiếu thì rút bù (seeded, cố định). */
function fillChunk(sorted: BankQuestion[], start: number, count: number, salt: string): BankQuestion[] {
  const chunk = sorted.slice(start, start + count);
  if (chunk.length === 0 || chunk.length >= count) return chunk;
  const ids = new Set(chunk.map((q) => q.id));
  const pool = sorted.filter((q) => !ids.has(q.id));
  const rand = mulberry32(hashSeed(salt));
  const p = [...pool];
  for (let i = p.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [p[i], p[j]] = [p[j], p[i]];
  }
  return [...chunk, ...p.slice(0, count - chunk.length)];
}

function sortBank(bank: BankQuestion[]): BankQuestion[] {
  return [...bank].sort((a, b) => (a.id < b.id ? -1 : a.id > b.id ? 1 : 0));
}

/** 8 câu cố định của màn: cắt kho (sort theo qid) thành từng khúc 8. */
export function nodeBank(bank: BankQuestion[], nodeIndex: number): BankQuestion[] {
  return fillChunk(sortBank(bank), nodeIndex * QUESTIONS_PER_NODE, QUESTIONS_PER_NODE, `fill:${nodeIndex}`);
}

export function modeFromString(m: string): NodeMode {
  return m === "boss" || m === "speed" ? m : "normal";
}

export function defaultTimeLimit(mode: NodeMode): number | undefined {
  if (mode === "boss") return BOSS_TIME_LIMIT_S;
  if (mode === "speed") return SPEED_TIME_LIMIT_S;
  return undefined;
}

/* --- thế giới sau hợp nhất (server thắng, thiếu thì fallback TS) --- */

export interface ResolvedNode {
  index: number;
  chapter: number;
  nodeInChapter: number;
  mode: NodeMode;
  questions: BankQuestion[];
  timeLimit?: number;
  manual: boolean;
}

export interface ResolvedChapter {
  name: string;
  icon: string;
  desc: string;
  nodes: ResolvedNode[];
}

export interface ResolvedWorld {
  chapters: ResolvedChapter[];
  flat: ResolvedNode[];
  totalNodes: number;
  /** true = cấu trúc riêng từ Game Manager */
  custom: boolean;
}

export function resolveWorld(
  slug: string,
  bank: BankQuestion[],
  config: GameServerConfig | null,
): ResolvedWorld {
  const sorted = sortBank(bank);
  const byId = new Map(sorted.map((q) => [q.id, q]));
  const custom = config?.structures?.[slug];
  if (custom && custom.length > 0) {
    const chapters = [...custom].sort((a, b) => a.idx - b.idx || a.id - b.id);
    const out: ResolvedChapter[] = [];
    let gi = 0;
    let cursor = 0;
    for (const c of chapters) {
      const nodes = [...c.nodes].sort((a, b) => a.idx - b.idx || a.id - b.id);
      const rn: ResolvedNode[] = nodes.map((n, nic) => {
        const mode = modeFromString(n.mode);
        let questions: BankQuestion[] = [];
        let manual = false;
        if (n.question_ids.length > 0) {
          questions = n.question_ids
            .map((id) => byId.get(id))
            .filter((q): q is BankQuestion => q !== undefined);
          manual = questions.length > 0;
        }
        if (!manual) {
          const count = Math.min(Math.max(1, n.question_count || QUESTIONS_PER_NODE), 25);
          questions = fillChunk(sorted, cursor, count, `auto:${slug}:${gi}`);
          cursor += count;
        }
        const timeLimit = n.time_limit > 0 ? n.time_limit : defaultTimeLimit(mode);
        return { index: gi++, chapter: out.length, nodeInChapter: nic, mode, questions, timeLimit, manual };
      });
      out.push({ name: c.name || `Chương ${out.length + 1}`, icon: c.icon || "🗺️", desc: c.desc, nodes: rn });
    }
    const flat = out.flatMap((c) => c.nodes);
    return { chapters: out, flat, totalNodes: flat.length, custom: true };
  }
  const count = nodeCountFor(bank.length);
  const nodes = buildNodes(count);
  const chapters = getChapters(slug);
  const out: ResolvedChapter[] = [];
  for (const n of nodes) {
    while (out.length <= n.chapter) {
      const c = chapters[out.length] ?? { name: `Chương ${out.length + 1}`, icon: "🗺️", desc: "" };
      out.push({ ...c, nodes: [] });
    }
    out[n.chapter].nodes.push({
      index: n.index,
      chapter: n.chapter,
      nodeInChapter: n.nodeInChapter,
      mode: n.mode,
      questions: nodeBank(bank, n.index),
      timeLimit: defaultTimeLimit(n.mode),
      manual: false,
    });
  }
  return { chapters: out, flat: out.flatMap((c) => c.nodes), totalNodes: nodes.length, custom: false };
}

export function modeMeta(mode: NodeMode): { icon: string; label: string } {
  if (mode === "boss") return { icon: "👹", label: "Trùm cuối chương" };
  if (mode === "speed") return { icon: "⚡", label: `Tốc độ (${SPEED_TIME_LIMIT_S}s/câu)` };
  return { icon: "🗺️", label: "Màn thường" };
}

/* --- tiến trình bản đồ (lưu trên máy) --- */

const KEY = "ddtk-stages-v1";

export interface WorldProgress {
  /** màn đang mở cao nhất (màn 0 luôn mở) */
  unlocked: number;
  stars: Record<string, number>;
}

function readAll(): Record<string, WorldProgress> {
  if (typeof window === "undefined") return {};
  try {
    const raw = window.localStorage.getItem(KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw) as Record<string, WorldProgress>;
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

export function getProgress(slug: string): WorldProgress {
  return readAll()[slug] ?? { unlocked: 0, stars: {} };
}

export function completeNode(
  slug: string,
  nodeIndex: number,
  stars: number,
): { unlocked: number; newBest: boolean; newUnlock: boolean } {
  const all = readAll();
  const cur = all[slug] ?? { unlocked: 0, stars: {} };
  const prev = cur.stars[String(nodeIndex)] ?? 0;
  const newBest = stars > prev;
  if (newBest) cur.stars[String(nodeIndex)] = stars;
  const newUnlock = nodeIndex + 1 > cur.unlocked;
  cur.unlocked = Math.max(cur.unlocked, nodeIndex + 1);
  all[slug] = cur;
  try {
    window.localStorage.setItem(KEY, JSON.stringify(all));
  } catch {
    /* đầy bộ nhớ thì bỏ qua */
  }
  return { unlocked: cur.unlocked, newBest, newUnlock };
}

/** ★ hoàn thành · ★ combo ≥4 · ★ không dùng thẻ trợ giúp. */
export function starsFor(maxCombo: number, helpersUsed: number): number {
  let s = 1;
  if (maxCombo >= COMBO_STAR_GOAL) s += 1;
  if (helpersUsed === 0) s += 1;
  return s;
}

export function totalStars(slug: string): number {
  return Object.values(getProgress(slug).stars).reduce((a, b) => a + b, 0);
}
