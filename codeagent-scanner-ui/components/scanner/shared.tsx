"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, FileSearch, FolderOpen, LayoutDashboard, LogOut, Settings, ShieldCheck } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";
import { logout, errorMessage } from "@/lib/api-client";
import { useState } from "react";

export function Shell({ title, description, children, action }: { title: string; description?: string; children: React.ReactNode; action?: React.ReactNode }) {
  const pathname = usePathname();
  const client = useQueryClient();
  const [error, setError] = useState("");
  const auth = client.getQueryData<{ required: boolean }>(["auth"]);
  return <div className="scanner-shell">
    <aside className="scanner-sidebar">
      <Link href="/dashboard" className="scanner-brand"><ShieldCheck aria-hidden="true" /><span>CodeAgent<small>Security workspace</small></span></Link>
      <nav aria-label="Main navigation">{[
        { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
        { href: "/jobs", label: "Runs", icon: Activity },
        { href: "/projects", label: "Projects", icon: FolderOpen },
        { href: "/reports", label: "Reports", icon: FileSearch },
        { href: "/setup", label: "Setup", icon: Settings },
      ].map(({ href, label, icon: Icon }) => <Link key={href} href={href} aria-current={pathname.startsWith(href) ? "page" : undefined}><Icon size={18} aria-hidden="true" />{label}</Link>)}</nav>
      <div className="sidebar-note"><span className="eyebrow">Review before you change</span><p>Source analysis and reviewed patch proposals. Proposals remain unapplied. Static validation runs in disposable copies.</p></div>
      {auth?.required && <button className="button secondary" onClick={async () => { try { await logout(); client.clear(); window.location.assign("/dashboard"); } catch (e) { setError(errorMessage(e)); } }}><LogOut size={16} />Sign out</button>}
    </aside>
    <main className="scanner-main"><header className="page-header"><div><p className="eyebrow">CODEAGENT / {title.toUpperCase()}</p><h1>{title}</h1>{description && <p className="muted">{description}</p>}</div>{action}</header>{error && <ErrorNotice message={error} />}{children}</main>
  </div>;
}
export function ErrorNotice({ message, retry }: { message: string; retry?: () => void }) {
  return <div className="notice error" role="alert"><span>{message}</span>{retry && <button className="button secondary compact" onClick={retry}>Try again</button>}</div>;
}
export function Loading({ text = "Loading…" }: { text?: string }) { return <p className="loading" role="status"><span className="loading-dot" />{text}</p>; }
export function Status({ value }: { value: string }) { return <span className={`status status-${value.replace(/[^a-z_-]/gi, "")}`}>{value.replaceAll("_", " ")}</span>; }
export function Time({ value }: { value?: string | null }) {
  if (!value) return <span>—</span>;
  const parsed = new Date(value);
  return <time dateTime={value}>{Number.isNaN(parsed.valueOf()) ? value : parsed.toLocaleString()}</time>;
}
export function Pagination({ page, total, onPage, limit = 20 }: { page: number; total: number; onPage: (page: number) => void; limit?: number }) {
  const count = Math.max(1, Math.ceil(total / limit));
  return <div className="pagination"><span className="muted">Page {page} of {count} · {total} results</span><div className="actions"><button className="button secondary compact" disabled={page <= 1} onClick={() => onPage(page - 1)}>Previous</button><button className="button secondary compact" disabled={page >= count} onClick={() => onPage(page + 1)}>Next</button></div></div>;
}
export function Empty({ title, children }: { title: string; children?: React.ReactNode }) { return <div className="empty"><FileSearch aria-hidden="true" /><h3>{title}</h3><div className="muted">{children}</div></div>; }
