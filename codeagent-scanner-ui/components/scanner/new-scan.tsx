"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowRight, Github, Upload } from "lucide-react";
import { aiConfig, errorMessage, modelNames, submitScan } from "@/lib/api-client";
import { useCapabilities } from "@/lib/hooks";
import type { Provider } from "@/lib/types";
import { ErrorNotice } from "./shared";
import { ProviderPicker } from "./provider-picker";
import { ProjectPicker } from "./projects";

const MAX_BYTES = 50 * 1024 * 1024;
export function NewScan() {
  const { data: capabilities } = useCapabilities();
  const router = useRouter(); const client = useQueryClient();
  const [source, setSource] = useState<"github" | "zip">("github");
  const [file, setFile] = useState<File | null>(null);
  const [mode, setMode] = useState<"static" | "multi_agent">("static");
  const [provider, setProvider] = useState<Provider>("ollama");
  const [model, setModel] = useState("");
  const [projectId, setProjectId] = useState(""); const [profile, setProfile] = useState("security-v1");
  const defaults = useQuery({ queryKey: ["ai-config"], queryFn: aiConfig });
  const [defaultsLoaded, setDefaultsLoaded] = useState(false);
  useEffect(() => { if (defaults.data && !defaultsLoaded) { setProvider(defaults.data.provider); setModel(defaults.data.model); setDefaultsLoaded(true); } }, [defaults.data, defaultsLoaded]);
  const [busy, setBusy] = useState(false); const [error, setError] = useState("");
  const maxBytes = capabilities?.max_upload_size ?? MAX_BYTES;
  useEffect(() => { if (!model) setModel(modelNames(capabilities, provider)[0] ?? ""); }, [capabilities, model, provider]);
  const pickFile = (candidate?: File) => {
    setError("");
    if (!candidate) { setFile(null); return; }
    if (!candidate.name.toLowerCase().endsWith(".zip")) { setError("Choose a ZIP archive (.zip)."); setFile(null); return; }
    if (candidate.size > maxBytes) { setError(`The ZIP archive must be ${Math.floor(maxBytes / 1024 / 1024)} MB or smaller.`); setFile(null); return; }
    if (!candidate.size) { setError("The ZIP archive is empty."); setFile(null); return; }
    setFile(candidate);
  };
  return <section className="panel" id="new-scan"><div className="section-heading"><div><p className="eyebrow">START WITH YOUR SOURCE</p><h2>New security scan</h2></div><span className="pill">Read-only source</span></div>
    <form onSubmit={async (event) => {
      event.preventDefault(); setError("");
      if (source === "zip" && (!file || !projectId)) { setError("Choose a ZIP archive before starting."); return; }
      if (mode === "multi_agent" && (!capabilities?.providers[provider]?.available || !model)) { setError("Choose a ready provider and model, or select static analysis."); return; }
      const form = new FormData(event.currentTarget); const payload = new FormData();
      if (source === "github") {
        const url = String(form.get("github_url") ?? "").trim();
        try { const parsed = new URL(url); if (parsed.protocol !== "https:" || parsed.hostname !== "github.com" || parsed.username || parsed.password || parsed.pathname.split("/").filter(Boolean).length !== 2) throw new Error(); }
        catch { setError("Use an HTTPS GitHub repository URL, such as https://github.com/owner/repo. Do not put credentials in the URL."); return; }
        payload.set("github_url", url);
        if (form.get("ref")) payload.set("ref", String(form.get("ref")));
        if (form.get("commit")) payload.set("commit", String(form.get("commit")));
      } else { if (!projectId) { setError("Select or create a named project for this ZIP."); return; } payload.set("file", file!); payload.set("project_id", projectId); }
      payload.set("profile", profile);
      for (const key of ["include", "exclude", "labels"]) { const value = String(form.get(key) ?? "").trim(); if (value) payload.set(key, value); }
      payload.set("mode", mode); if (mode === "multi_agent") { payload.set("provider", provider); payload.set("model", model); }
      setBusy(true);
      try { const result = await submitScan(payload); await client.invalidateQueries({ queryKey: ["jobs"] }); router.push(`/jobs/${result.job_id}`); }
      catch (e) { setError(errorMessage(e)); }
      finally { setBusy(false); }
    }}>
      <div className="segmented" role="group" aria-label="Source type"><button type="button" aria-pressed={source === "github"} onClick={() => setSource("github")}><Github size={17} />GitHub repository</button><button type="button" aria-pressed={source === "zip"} onClick={() => setSource("zip")}><Upload size={17} />ZIP archive</button></div>
      {source === "github" ? <div className="stack"><div><label htmlFor="github-url">Repository URL</label><input id="github-url" name="github_url" type="url" placeholder="https://github.com/owner/repository" required /><p className="field-help">Private repositories use the administrator’s server-side GitHub token.</p></div><div className="field-grid"><div><label htmlFor="ref">Branch or tag <span className="muted">(optional)</span></label><input id="ref" name="ref" placeholder="Repository default branch" /></div><div><label htmlFor="commit">Commit <span className="muted">(optional)</span></label><input id="commit" name="commit" placeholder="Immutable commit SHA" /></div></div></div> : <div className="dropzone" onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); pickFile(event.dataTransfer.files[0]); }}><Upload size={24} aria-hidden="true" /><label htmlFor="source-file">{file ? file.name : "Drop a ZIP archive here, or choose a file"}</label><input id="source-file" type="file" accept=".zip,application/zip" onChange={(event) => pickFile(event.target.files?.[0])} /><p className="field-help">Up to {Math.floor(maxBytes / 1024 / 1024)} MB compressed. Exclude dependencies, build outputs, and secrets.</p></div>}
      {source === "zip" && <ProjectPicker value={projectId} onChange={setProjectId} />}
      <div className="profile-picker"><label htmlFor="scan-profile">Security rule profile</label><select id="scan-profile" value={profile} onChange={(e) => setProfile(e.target.value)}><option value="security-v1">Stable · security-v1</option><option value="security-v2">Candidate · security-v2 (expanded checks)</option></select><p className="field-help">The candidate profile is opt-in while comparative quality gates are pending. Saved runs retain their selected profile.</p></div>
      <fieldset className="mode-options"><legend>Analysis</legend><label><input type="radio" name="mode-choice" checked={mode === "static"} onChange={() => setMode("static")} /><span><strong>Static analysis</strong><small>Source and dependency findings. No model required.</small></span></label><label><input type="radio" name="mode-choice" checked={mode === "multi_agent"} onChange={() => setMode("multi_agent")} /><span><strong>Multi-agent review</strong><small>Static analysis, security triage, patch proposal, and independent review.</small></span></label></fieldset>
      {mode === "multi_agent" && <ProviderPicker capabilities={capabilities} provider={provider} model={model} onProvider={setProvider} onModel={setModel} id="new-scan" />}
      <details className="advanced"><summary>File filters and labels</summary><div className="stack"><div className="field-grid"><div><label htmlFor="include">Include patterns</label><input id="include" name="include" placeholder="src/**,app/**" /></div><div><label htmlFor="exclude">Exclude patterns</label><input id="exclude" name="exclude" placeholder="tests/**,generated/**" /></div></div><div><label htmlFor="labels">Labels</label><input id="labels" name="labels" placeholder="team:backend,release" /><p className="field-help">Separate multiple values with commas.</p></div></div></details>
      {error && <ErrorNotice message={error} />}
      {capabilities && !capabilities.worker_online && <p className="notice warning">The worker is offline. Start it before submitting a scan.</p>}
      <div className="form-footer"><p className="muted">Patches are proposals only.<br />Nothing is applied or executed.</p><button className="button primary" disabled={busy || (source === "zip" && (!file || !projectId)) || !capabilities?.worker_online || (mode === "multi_agent" && (!capabilities.providers[provider]?.available || !model))}>{busy ? "Submitting…" : "Start scan"}<ArrowRight size={17} /></button></div>
    </form>
  </section>;
}
