"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { cancelJob, errorMessage, jobs, pretty, rerunJob, retryJob, sourceLabel } from "@/lib/api-client";
import { useRun, useRunEvents } from "@/lib/hooks";
import { TERMINAL, type AgentStep, type Job } from "@/lib/types";
import { Empty, ErrorNotice, Loading, Pagination, Shell, Status, Time } from "./shared";

export function RunList({ compact = false }: { compact?: boolean }) {
  const [page, setPage] = useState(1); const [status, setStatus] = useState("");
  const query = useQuery({ queryKey: ["jobs", page, status], queryFn: () => jobs(page, status), refetchInterval: 5000 });
  return <section className="panel"><div className="section-heading"><h2>{compact ? "Recent runs" : "All runs"}</h2>{compact ? <Link className="text-link" href="/jobs">View all runs →</Link> : <div><label className="sr-only" htmlFor="run-status">Filter runs by status</label><select id="run-status" value={status} onChange={(event) => { setStatus(event.target.value); setPage(1); }}><option value="">All statuses</option>{["queued", "running", "completed", "partial", "failed", "canceled", "interrupted"].map((value) => <option key={value} value={value}>{value}</option>)}</select></div>}</div>
    {query.isPending ? <Loading text="Loading runs…" /> : query.error ? <ErrorNotice message={errorMessage(query.error)} retry={() => void query.refetch()} /> : !query.data?.items.length ? <Empty title="No runs yet"><Link className="text-link" href="/dashboard#new-scan">Start a scan</Link> to see progress here.</Empty> : <><div className="table-scroll"><table><thead><tr><th>Source / run</th><th>Kind</th><th>Status</th><th>Stage</th><th>Submitted</th></tr></thead><tbody>{query.data.items.slice(0, compact ? 5 : undefined).map((run) => <tr key={run.job_id}><td><Link className="row-link" href={`/jobs/${run.job_id}`}>{sourceLabel(run)}</Link><small className="mono muted">{run.job_id.slice(0, 12)}</small></td><td>{run.kind || "scan"}</td><td><Status value={run.status} /></td><td>{run.progress?.phase?.replaceAll("_", " ") || "Waiting"}</td><td className="muted"><Time value={run.submitted_at} /></td></tr>)}</tbody></table></div>{!compact && <Pagination page={page} total={query.data.total} onPage={setPage} />}</>}
  </section>;
}
function Steps({ steps, scanId }: { steps?: AgentStep[]; scanId: string }) {
  if (!steps?.length) return <p className="muted">Stage details will appear when the worker starts.</p>;
  return <ol className="stage-list">{steps.map((step, index) => <li key={`${step.key}-${index}`}><div className="stage-marker">{index + 1}</div><div className="stage-content"><div className="section-heading"><h3>{step.role || step.key.replaceAll("_", " ")}</h3><Status value={step.status} /></div>{step.key.startsWith("finding:") && <Link className="text-link" href={`/reports/${scanId}#finding-${encodeURIComponent(step.key.split(":")[1])}`}>Related source finding →</Link>}{Boolean(step.usage?.effective_model || step.model || step.usage?.model) && <p className="field-help">{step.status === "completed" ? "Model used" : "Selected model"}: <span className="mono">{String(step.usage?.effective_model || step.model || step.usage?.model)}</span></p>}{Boolean(step.error) && <p className="notice error">{errorMessage(step.error)}</p>}{step.usage && Object.keys(step.usage).length > 0 && <details><summary>Usage</summary><pre className="output">{pretty(step.usage)}</pre></details>}{step.output !== undefined && step.output !== null && <details><summary>Stage output</summary><pre className="output">{pretty(step.output)}</pre></details>}</div></li>)}</ol>;
}
function RunCard({ run, title, detailLink = false }: { run: Job; title: string; detailLink?: boolean }) {
  const percentage = Math.max(0, Math.min(100, run.progress?.percent ?? 0));
  return <section className="panel"><div className="section-heading"><div><p className="eyebrow">{run.kind === "provider_check" ? "MODEL CONNECTION" : run.kind === "review" ? "AI ANALYSIS" : "SOURCE ANALYSIS"}</p><h2>{title}</h2></div><div className="actions"><Status value={run.status} />{detailLink && <Link className="text-link" href={`/jobs/${run.job_id}`}>Open review run →</Link>}</div></div>{["partial", "failed", "interrupted"].includes(run.status) && run.steps?.some((step) => step.output != null) && <p className="notice warning">Completed stage outputs are retained below. Explicitly retry incomplete stages to continue this run; no provider call is retried automatically.</p>}<div className="progress-label"><span>{run.progress?.phase?.replaceAll("_", " ") || "Waiting"}</span><span>{percentage}%</span></div><progress aria-label={`${title} progress`} value={percentage} max={100} />{run.error && <ErrorNotice message={run.error} />}<Steps steps={run.steps} scanId={run.parent_job_id || run.job_id} />{run.kind === "review" && <p className="notice neutral">Agent review and static validation assess proposals. Repository builds and runtime tests are not run.</p>}</section>;
}
export function RunDetail({ id }: { id: string }) {
  const query = useRun(id); const run = query.data;
  const reviewQuery = useRun(run?.kind !== "review" ? run?.latest_review_id : null);
  const finished = Boolean(run && TERMINAL.includes(run.status) && (!run.latest_review_id || (reviewQuery.data && TERMINAL.includes(reviewQuery.data.status))));
  const live = useRunEvents(id, Boolean(run), finished);
  const [busy, setBusy] = useState(false); const [actionError, setActionError] = useState("");
  const client = useQueryClient(); const router = useRouter();
  async function act(kind: "cancel" | "rerun" | "latest" | "retry") {
    setBusy(true); setActionError("");
    try {
      if (kind === "cancel") { await cancelJob(id); await client.invalidateQueries({ queryKey: ["job"] }); }
      else { const result = kind === "retry" ? await retryJob(id) : await rerunJob(id, kind === "latest"); await client.invalidateQueries({ queryKey: ["jobs"] }); await client.invalidateQueries({ queryKey: ["job"] }); router.push(`/jobs/${result.job_id}`); }
    } catch (error) { setActionError(errorMessage(error)); } finally { setBusy(false); }
  }
  const scanId = run?.kind === "review" ? run.parent_job_id : id;
  return <Shell title="Run details" description={run ? sourceLabel(run) : "A durable record of source analysis and agent review."} action={<Link className="button secondary" href="/jobs">All runs</Link>}>
    {query.isPending ? <Loading /> : query.error ? <ErrorNotice message={errorMessage(query.error)} retry={() => void query.refetch()} /> : run && <div className="stack">
      <div className="run-toolbar"><div><span className="mono muted">{run.job_id}</span><p className="field-help">{finished ? "Run finished · event history available" : live.connected ? "Live updates connected" : "Refreshing status · reconnecting live updates"}</p></div><div className="actions">{!TERMINAL.includes(run.status) ? <button className="button danger" disabled={busy} onClick={() => void act("cancel")}>{busy ? "Working…" : "Cancel run"}</button> : <>{["failed", "partial", "interrupted"].includes(run.status) && <button className="button secondary" disabled={busy} onClick={() => void act("retry")}>Retry incomplete stages</button>}{run.kind === "scan" && <><button className="button secondary" disabled={busy} onClick={() => void act("rerun")}>Rerun same snapshot</button>{(run.source?.url || run.source?.github_url) && <button className="button secondary" disabled={busy} onClick={() => void act("latest")}>Scan latest ref</button>}</>}</>}{run.kind !== "provider_check" && scanId && (TERMINAL.includes(run.status) || run.kind === "review") && <Link className="button primary" href={`/reports/${scanId}${run.kind === "review" ? `?review=${run.job_id}` : ""}`}>View report</Link>}</div></div>
      {actionError && <ErrorNotice message={actionError} />}
      <RunCard run={run} title={run.kind === "provider_check" ? "Model connection check" : run.kind === "review" ? "Multi-agent review" : "Static scan"} />
      {run.latest_review_id && run.kind !== "review" && (reviewQuery.data ? <RunCard run={reviewQuery.data} title="Multi-agent review" detailLink /> : reviewQuery.error ? <ErrorNotice message={errorMessage(reviewQuery.error)} retry={() => void reviewQuery.refetch()} /> : <Loading text="Loading agent review…" />)}
      <section className="panel"><h2>Run record</h2><dl className="metadata-grid"><div><dt>Submitted</dt><dd><Time value={run.submitted_at} /></dd></div><div><dt>Started</dt><dd><Time value={run.started_at} /></dd></div><div><dt>Finished</dt><dd><Time value={run.finished_at} /></dd></div><div><dt>Provider / model</dt><dd>{run.config?.provider ? `${run.config.provider} / ${run.config.model || "—"}` : "Static analysis"}</dd></div></dl><details><summary>Effective configuration and source</summary><pre className="output">{pretty({ config: run.config, source: run.source })}</pre></details></section>
      <section className="panel"><div className="section-heading"><h2>Event history</h2><span className="muted">Latest 200 events</span></div>{live.events.length ? <ol className="event-list">{live.events.map((event) => <li key={`${event.job_id}-${event.seq}`}><span className="mono muted">#{event.seq}</span><details><summary>{event.event.replaceAll("_", " ")}</summary><pre className="output">{pretty(event.data)}</pre></details></li>)}</ol> : <p className="muted">Waiting for events. The run record above is refreshed independently.</p>}</section>
    </div>}
  </Shell>;
}
