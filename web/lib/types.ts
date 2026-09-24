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
}

export interface CatalogOption { value: string; label: string; description: string }
export interface CatalogSection { id: string; title: string }

export interface Catalog {
  tiers: CatalogOption[];
  templates: CatalogOption[];
  content_modes: CatalogOption[];
  domains: CatalogOption[];
  sections_by_tier: Record<string, CatalogSection[]>;
  llm_available: boolean;
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
