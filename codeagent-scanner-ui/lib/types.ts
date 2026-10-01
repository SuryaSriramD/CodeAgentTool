import type { components } from "./generated/api";
type Schemas = components["schemas"];
export type Provider = "openai" | "ollama";
export type JobStatus = Schemas["Job"]["status"];
export type Severity = Schemas["Issue"]["severity"];
export interface Page<T> { items: T[]; page: number; limit: number; total: number }
export interface AgentStep {
  key: string; role?: string; provider?: string; model?: string; status: string; error?: unknown;
  output?: unknown; usage?: Record<string, unknown>; input_hash?: string;
}
export type Job = Pick<Schemas["Job"], "job_id" | "parent_job_id" | "status" | "progress" | "submitted_at" | "started_at" | "finished_at" | "error" | "config" | "source" | "latest_review_id"> & { kind: "scan" | "review" | "provider_check"; steps?: AgentStep[] };
export interface Coverage {
  tool: string; status: string; files_discovered?: number; files_scanned?: number;
  files_skipped?: number; errors?: string[]; version?: string; languages?: string[];
  rule_set?: string | string[];
}
export type Finding = Pick<Schemas["Issue"], "id" | "tool" | "type" | "message" | "severity" | "file" | "line" | "rule_id" | "suggestion" | "source_hash"> & {
  logical_id?: string; fingerprint?: string; end_line?: number; cwe?: string | string[];
  vulnerability_family?: string; analysis_kind?: string; rule_revision?: string; evidence?: unknown;
  triage?: Triage; dependency?: unknown;
};
export type Submission = Schemas["Submission"];
export interface Proposal {
  id: string; finding_ids: string[]; related_finding_ids?: string[]; group_id?: string; diff: string; explanation: string;
  checks?: unknown; review?: { decision: string; comments?: unknown } | null;
  status: string; edits?: unknown; validation?: ProposalValidation; conflicts?: string[];
}
export interface Report extends Pick<Schemas["ScanReport"], "job_id" | "schema_version"> {
  review_run_id?: string; report_hash?: string; project_id?: string; stream?: string; baseline?: unknown;
  meta: {
    repo: { source: string; url?: string; ref?: string; commit?: string };
    generated_at: string; project_id?: string; stream?: string; report_hash?: string; profile?: string; duration_ms?: number; tools?: string[]; labels?: string[];
    snapshot?: { digest?: string; files?: Record<string, string>; warnings?: string[] };
  };
  summary: Record<Severity, number>;
  files: { path: string; issues: Finding[] }[];
  coverage?: Coverage[];
  ai_analysis?: { status: string; triage?: unknown; proposals?: Proposal[]; errors?: unknown };
}
export interface ReportRow {
  job_id: string; repo_url?: string; generated_at: string; summary: Record<Severity, number>;
  tools?: string[]; labels?: string[];
}
export interface Capabilities {
  ready: boolean; worker_online: boolean; auth_required?: boolean;
  private_github?: boolean; max_upload_size?: number; proposal_only?: boolean;
  analyzers: { name: string; available: boolean; version?: string; languages?: string[]; advisory_database?: { updated_at?: string; age_hours?: number; error?: string }; database_age?: string; [key: string]: unknown }[];
  providers: Record<Provider, { available: boolean; configured?: boolean; reachable?: boolean | null; models?: (string | { id?: string; name?: string })[]; error?: string; last_test?: ProviderCheck }>;
  languages: (string | { name?: string; language?: string; available?: boolean; tools?: string[] })[];
}
export interface AuthStatus { required: boolean; authenticated: boolean }
export interface RunEvent { seq: number; event: string; job_id: string; data: unknown; timestamp?: string }
export const TERMINAL: JobStatus[] = ["completed", "partial", "failed", "canceled", "interrupted"];
export const SEVERITIES: Severity[] = ["critical", "high", "medium", "low"];

export interface AIConfig { provider: Provider; model: string; min_severity: Severity; max_model_calls: number; max_total_tokens: number; timeout_sec: number; max_findings: number; max_context_chars: number; max_output_tokens: number }
export interface ProviderCheck { configured?: boolean; reachable?: boolean; schema_test_passed?: boolean; schema_tested?: boolean; model?: string; provider?: Provider; error?: string; tested_at?: string; [key: string]: unknown }
export interface ProposalValidation { status: string; syntax?: unknown; targeted_findings_remaining?: unknown; new_findings?: unknown; errors?: unknown; coverage?: unknown; elapsed_ms?: number; [key: string]: unknown }
export interface Project { id: string; project_id?: string; name: string; kind: string; created_at?: string; repository?: string; [key: string]: unknown }
export interface Triage { status: "open" | "confirmed" | "dismissed"; revision: number; reason?: string; category?: string; previous_status?: string; requires_reconfirmation?: boolean }
export interface FindingAssessment { classification: "existing" | "resolved" | "not_assessed" | "ambiguous"; reason?: string | null; stream?: string; job_id?: string; report_hash?: string }
export interface ProjectFinding { assessment?: FindingAssessment; id: string; logical_id?: string; fingerprint: string; file: string; rule_id: string; message: string; severity: Severity; triage: Triage; notes?: { body: string; created_at?: string; [key: string]: unknown }[]; latest_occurrence?: unknown; [key: string]: unknown }
export interface Comparison { has_baseline: boolean; baseline?: unknown; current?: unknown; status?: string; counts?: Record<string, number>; comparability_reasons?: string[]; items: { classification: "new" | "existing" | "resolved" | "not_assessed" | "ambiguous"; finding?: Partial<Finding>; baseline_finding?: Partial<Finding>; reason?: string }[] }
