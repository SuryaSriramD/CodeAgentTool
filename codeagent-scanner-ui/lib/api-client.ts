import type { AIConfig, AuthStatus, Capabilities, Comparison, Job, Page, Project, ProjectFinding, Provider, Report, ReportRow, Submission, Triage } from "./types";

export class APIError extends Error {
  constructor(message: string, public status: number) { super(message); this.name = "APIError"; }
}
export function errorMessage(value: unknown): string {
  if (typeof value === "string") return value;
  if (value instanceof Error) return value.message;
  if (value && typeof value === "object") {
    const record = value as Record<string, unknown>;
    return errorMessage(record.message ?? record.error ?? record.detail ?? "Request failed");
  }
  return "Request failed";
}
export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`/api/backend${path}`, {
    ...options, credentials: "same-origin", cache: "no-store",
    headers: { ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }), ...options.headers },
  });
  let payload: unknown;
  try { payload = await response.json(); } catch { payload = undefined; }
  if (!response.ok) {
    if (response.status === 401 && typeof window !== "undefined") window.dispatchEvent(new Event("scanner:unauthorized"));
    throw new APIError(payload ? errorMessage(payload) : `Request failed (${response.status})`, response.status);
  }
  return payload as T;
}
export const authStatus = () => api<AuthStatus>("/auth/status");
export const login = (password: string) => api<AuthStatus>("/auth/login", { method: "POST", body: JSON.stringify({ password }) });
export const logout = () => api<void>("/auth/logout", { method: "POST" });
export const capabilities = () => api<Capabilities>("/capabilities");
export const job = (id: string) => api<Job>(`/jobs/${encodeURIComponent(id)}`);
export const jobs = (page = 1, status = "", query = "") => {
  const params = new URLSearchParams({ page: String(page), limit: "20" });
  if (status) params.set("status", status);
  if (query) params.set("q", query);
  return api<Page<Job>>(`/jobs?${params}`);
};
export const submitScan = (data: FormData) => api<Submission>("/analyze-async", { method: "POST", body: data });
export const cancelJob = (id: string) => api<Job>(`/jobs/${encodeURIComponent(id)}`, { method: "DELETE" });
export const rerunJob = (id: string, latest = false) => api<{ job_id: string }>(`/jobs/${encodeURIComponent(id)}/rerun`, { method: "POST", body: JSON.stringify({ latest }) });
export const retryJob = (id: string) => api<{ job_id: string }>(`/jobs/${encodeURIComponent(id)}/retry`, { method: "POST" });
export const report = (id: string) => api<Report>(`/reports/${encodeURIComponent(id)}`);
export const reviewReport = (id: string) => api<Report>(`/reviews/${encodeURIComponent(id)}`);
export const enhancedReport = (id: string) => api<Report>(`/reports/${encodeURIComponent(id)}/enhanced`);
export const reports = (page = 1, severity = "", query = "") => {
  const params = new URLSearchParams({ page: String(page), limit: "20" });
  if (severity) params.set("severity", severity);
  if (query) params.set("repo", query);
  return api<Page<ReportRow>>(`/reports?${params}`);
};
export const startReview = (id: string, provider: Provider, model: string) => api<Submission>(`/reports/${encodeURIComponent(id)}/enhance`, { method: "POST", body: JSON.stringify({ provider, model, workflow_mode: "multi_agent" }) });
export function modelNames(data: Capabilities | undefined, provider: Provider): string[] {
  return (data?.providers?.[provider]?.models ?? []).map((model) => typeof model === "string" ? model : model.id || model.name || "").filter(Boolean);
}
export function sourceLabel(run: Job): string {
  const source = run.source ?? {};
  return String(source.url ?? source.github_url ?? source.filename ?? source.name ?? (run.kind === "review" ? `Review of ${run.parent_job_id?.slice(0, 8) ?? "scan"}` : "Uploaded source"));
}
export function pretty(value: unknown) { return typeof value === "string" ? value : JSON.stringify(value, null, 2); }

export const aiConfig = () => api<AIConfig>("/config/ai");
export const saveAIConfig = (config: AIConfig) => api<AIConfig>("/config/ai", { method: "PATCH", body: JSON.stringify(config) });
export const testAIConfig = (config: AIConfig) => api<Submission>("/config/ai/test", { method: "POST", body: JSON.stringify(config) });
export const projects = (page = 1) => api<Page<Project>>(`/projects?page=${page}&limit=100`);
export const createProject = (name: string) => api<Project>("/projects", { method: "POST", body: JSON.stringify({ name, kind: "zip" }) });
export const projectFindings = (id: string, page = 1) => api<Page<ProjectFinding>>(`/projects/${encodeURIComponent(id)}/findings?page=${page}&limit=20`);
export const updateTriage = (project: string, finding: string, data: { status: Triage["status"]; expected_revision: number; reason?: string; category?: string }) => api<ProjectFinding>(`/projects/${encodeURIComponent(project)}/findings/${encodeURIComponent(finding)}/triage`, { method: "PATCH", body: JSON.stringify(data) });
export const addFindingNote = (project: string, finding: string, body: string) => api<ProjectFinding>(`/projects/${encodeURIComponent(project)}/findings/${encodeURIComponent(finding)}/notes`, { method: "POST", body: JSON.stringify({ body }) });
export const compareReport = (id: string, baselineRun = "", baselineHash = "", hash = "") => {
  const params = new URLSearchParams(); if (baselineRun) params.set("baseline_run_id", baselineRun); if (baselineHash) params.set("baseline_hash", baselineHash); if (hash) params.set("report_hash", hash);
  return api<Comparison>(`/reports/${encodeURIComponent(id)}/comparison?${params}`);
};
export async function downloadAPI(path: string, filename: string, options: RequestInit = {}) {
  const response = await fetch(`/api/backend${path}`, { ...options, credentials: "same-origin", cache: "no-store", headers: { "Content-Type": "application/json", ...options.headers } });
  if (!response.ok) { let payload; try { payload = await response.json(); } catch {} throw new APIError(payload ? errorMessage(payload) : `Download failed (${response.status})`, response.status); }
  const blob = await response.blob(); const url = URL.createObjectURL(blob); const link = document.createElement("a"); link.href = url; link.download = filename; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
}
