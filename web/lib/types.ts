// Mirrors backend/api/schemas.py (source of truth: /api/v1/openapi.json).

export type Role = "admin" | "coach";
export type ReportStatus = "generating" | "ready" | "failed" | "archived";

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: Role;
  is_active: boolean;
  org_name: string;
  created_at: string;
  last_login_at: string | null;
}

export interface CatalogOption { value: string; label: string; description: string; badge?: string; meta?: string; has_style?: boolean }
export interface CatalogSection { id: string; title: string }

export interface Catalog {
  tiers: CatalogOption[];
  templates: CatalogOption[];
  content_modes: CatalogOption[];
  domains: CatalogOption[];
  sections_by_tier: Record<string, CatalogSection[]>;
  llm_available: boolean;
  llm_providers: { name: string; model: string }[];
  timezone_default: string;
  timezone_label: string;
}

export interface ClientInput {
  full_name: string;
  email: string;
  phone: string;
  birth_date: string; // YYYY-MM-DD
  birth_time: string; // HH:MM (giờ Việt Nam khai báo)
  birth_time_known: boolean;
  birth_place: string;
  timezone: string;
  notes: string;
  consent?: boolean;
}

export interface Client extends Omit<ClientInput, "consent"> {
  id: number;
  birth_display: string;
  owner_id: number;
  owner_name: string;
  report_count: number;
  consent_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Paged<T> { items: T[]; total: number }

export interface ChartSummary {
  type: string;
  type_vn: string;
  strategy: string;
  authority: string;
  profile: string;
  definition: string;
  incarnation_cross: string;
  defined_centers: number;
}

export interface ReportOptions {
  tier: string;
  template: string;
  domains: string[];
}

export interface ReportSummary extends ReportOptions {
  id: string;
  client_id: number;
  client_name: string;
  template_name: string;
  content_mode: string;
  status: ReportStatus;
  editor: string;
  warnings_count: number;
  version: number;
  error: string;
  created_at: string;
  updated_at: string;
}

export interface Section { id: string; title: string; status: string; warnings: string[] }

export interface ReportDetail extends ReportSummary {
  subject_display: string;
  summary: ChartSummary | null;
  sections: Section[];
  warnings: string[];
  markdown: string;
  llm_provider: string;
  llm_cost_usd: number | null;
  style_used: boolean;
  style_rating: number | null;
  style_version: number | null;
}

export interface Preview {
  subject_display: string;
  summary: ChartSummary;
  sections: CatalogSection[];
  markdown: string;
  bodygraph_svg: string;
}

export interface Dashboard {
  clients: number;
  reports_total: number;
  reports_by_status: Record<string, number>;
  recent_reports: ReportSummary[];
}

// --- editor (P2) ---
export interface GlossaryGroup { title: string; terms: { source: string; term: string }[] }

export interface EditorSection {
  id: string;
  title: string;
  kind: string;
  order: number;
  content_markdown: string;
  data: Record<string, unknown>;
  warnings: string[];
  knowledge_refs: string[];
}

export interface EditorData {
  report: ReportSummary;
  subject_display: string;
  sections: EditorSection[];
  llm_available: boolean;
  glossary: GlossaryGroup[];
}

export interface SectionSave { version: number; section: EditorSection; missing_facts: string[] }
export interface Revision { version: number; author: string; change_type: string; warnings_count: number; created_at: string }
export interface LlmProposal { draft: string; missing_facts: string[] }

// --- sharing / links / LLM settings ---
export type ShareFormat = "pdf" | "docx" | "markdown";
export interface Share {
  id: number;
  report_id: string;
  label: string;
  formats: ShareFormat[];
  expires_at: string;
  revoked_at: string | null;
  view_count: number;
  last_viewed_at: string | null;
  created_at: string;
  status: "active" | "expired" | "revoked";
}
export interface ShareCreated { share: Share; url: string }
export interface DownloadLink { url: string; expires_at: string }

export interface LlmProvider {
  index: number;
  name: string;
  base_url: string;
  model: string;
  temperature: number;
  timeout: number;
  enabled: boolean;
  has_key: boolean;
  key_hint: string;
  key_unreadable: boolean;
  input_price: number;
  output_price: number;
}
export interface LlmSettings {
  providers: LlmProvider[];
  key_source: "database" | "environment" | "none";
  updated_by: string;
  updated_at: string | null;
}
export interface LlmTestItem {
  index: number;
  name: string;
  model: string;
  ok: boolean;
  latency_ms: number;
  detail: string;
}
export interface LlmTest { results: LlmTestItem[] }

export interface LlmUsageTotals {
  requests: number;
  errors: number;
  prompt_tokens: number;
  completion_tokens: number;
  cost_usd: number;
  unpriced_requests: number;
}
export interface LlmProviderStat extends LlmUsageTotals {
  provider: string;
  model: string;
}
export interface LlmUsageRow {
  id: number;
  created_at: string;
  report_id: string | null;
  purpose: string;
  provider: string;
  model: string;
  prompt_tokens: number;
  completion_tokens: number;
  cost_usd: number | null;
  ok: boolean;
  error: string;
  latency_ms: number;
}
export interface LlmUsage {
  days: number;
  totals: LlmUsageTotals;
  by_provider: LlmProviderStat[];
  recent: LlmUsageRow[];
}

export interface AssistantModel { index: number; name: string; model: string }

export interface ChatSession {
  id: string;
  title: string;
  provider: string;
  model: string;
  message_count: number;
  total_cost_usd: number;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: number;
  role: string;
  content: string;
  tools_used: string[];
  sources: string[];
  prompt_tokens: number;
  completion_tokens: number;
  cost_usd: number | null;
  latency_ms: number;
  rating: number | null;
  created_at: string;
}

export interface ChatSend { session: ChatSession; message: ChatMessage; provider: string; model: string }
export interface ChatDetail { session: ChatSession; messages: ChatMessage[] }

export interface ChatUserStat {
  user_id: number;
  email: string;
  full_name: string;
  sessions: number;
  messages: number;
  cost_usd: number;
}

export interface ChatAdminStats {
  days: number;
  sessions: number;
  messages: number;
  prompt_tokens: number;
  completion_tokens: number;
  cost_usd: number;
  likes: number;
  dislikes: number;
  by_user: ChatUserStat[];
}

export interface ChatAdminSession extends ChatSession {
  user_email: string;
  user_name: string;
}

export interface PublicReport {
  client_name: string;
  subject_display: string;
  title: string;
  generated_at: string;
  summary: ChartSummary;
  formats: ShareFormat[];
  sections: { id: string; title: string; content_markdown: string }[];
  org_name: string;
}


// --- mẫu báo cáo (P1) ---
export type TemplateStatus = "draft" | "pending" | "active" | "rejected" | "archived";

export interface TemplateSummary {
  id: number;
  key: string;
  name: string;
  description: string;
  badge: string;
  visibility: "private" | "shared";
  status: TemplateStatus;
  version: number;
  sections_count: number;
  samples_count: number;
  reports_count: number;
  origin_label: string;
  import_count: number;
  created_by_name: string;
  style_status: string;
  created_at: string;
  updated_at: string;
}

export interface ResolvedSection {
  type: string;
  ref: string;
  block_id: number | null;
  title: string;
  title_default: string;
  kind: string;
  name: string;
  body: string;
}

export interface TemplateSample { id: number; title: string; body: string; sort: number }

export interface TemplateDetail extends TemplateSummary {
  review_note: string;
  style_profile: StyleProfile;
  sections: ResolvedSection[];
  samples: TemplateSample[];
}

export interface TemplateBlock {
  id: number;
  name: string;
  kind: string;
  body: string;
  variables: string[];
  used_in: string[];
}

export interface BlockVariable { path: string; label: string; example: string }
export interface BuiltinSection { id: string; title: string; kind: string }
export interface OrgVar { key: string; label: string; value: string }
export interface OrgVars { vars: OrgVar[] }
export interface PreviewSection { id: string; title: string; markdown: string }
export interface TemplatePreview { title: string; sections: PreviewSection[]; warnings: string[] }

export interface StyleProfile {
  tone: string;
  rhythm: string;
  vocabulary: string;
  structure: string;
  do: string[];
  dont: string[];
  excerpt: string;
  sample_count: number;
}

export interface StylePreviewOut {
  preview: string;
  topic: string;
  style_status: string;
  provider: string;
}

export interface StyleCompareOut {
  topic: string;
  default_text: string;
  styled_text: string;
  style_status: string;
  provider: string;
}

export interface StyleRatedReport {
  report_id: string;
  client_name: string;
  rating: number;
  created_at: string;
}

export interface StyleVersionStat {
  version: number;
  up: number;
  down: number;
}

export interface StyleStatsOut {
  up: number;
  down: number;
  reports: StyleRatedReport[];
  by_version: StyleVersionStat[];
}

export interface StyleHistoryOut {
  version_no: number;
  source: string;
  created_by_name: string;
  created_at: string;
  tone: string;
  excerpt: string;
  sample_count: number;
}

export interface GameLeadOut {
  id: number;
  name: string;
  contact: string;
  birth_date: string;
  birth_time: string;
  birth_place: string;
  timezone: string;
  theme: string;
  quiz: { style?: string; deviation?: number; theme?: string };
  note: string;
  status: string;
  created_at: string;
}

export interface GameFunnelStat {
  theme: string;
  name: string;
  count: number;
}

export interface GameScoreOut {
  theme: string;
  style: string;
  deviation: number;
  created_at: string;
}

export interface GameStreakOut {
  streak: number;
  today_done: boolean;
}