"use client";
import { useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { authStatus, errorMessage, login } from "@/lib/api-client";
import { ErrorNotice, Loading } from "./shared";
import { ShieldCheck } from "lucide-react";

export function AuthGate({ children }: { children: React.ReactNode }) {
  const client = useQueryClient();
  const auth = useQuery({ queryKey: ["auth"], queryFn: authStatus, retry: false });
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    const refresh = () => void client.invalidateQueries({ queryKey: ["auth"] });
    window.addEventListener("scanner:unauthorized", refresh);
    return () => window.removeEventListener("scanner:unauthorized", refresh);
  }, [client]);
  if (auth.isPending) return <div className="auth-screen"><Loading text="Connecting to your scanner…" /></div>;
  if (auth.error) return <div className="auth-screen"><section className="panel auth-panel"><ShieldCheck size={36} /><h1>Scanner unavailable</h1><p className="muted">Start the backend and check the server’s API_URL setting. Your browser connects through this workspace.</p><ErrorNotice message={errorMessage(auth.error)} retry={() => void auth.refetch()} /></section></div>;
  if (!auth.data?.required || auth.data.authenticated) return children;
  return <div className="auth-screen"><section className="panel auth-panel"><ShieldCheck size={36} /><p className="eyebrow">CODEAGENT WORKSPACE</p><h1>Sign in to your scanner</h1><p className="muted">Use the workspace password configured by the server administrator.</p><form onSubmit={async (event) => {
    event.preventDefault(); setBusy(true); setError("");
    try { await login(password); setPassword(""); client.clear(); await client.invalidateQueries({ queryKey: ["auth"] }); window.location.reload(); }
    catch (e) { setError(errorMessage(e)); }
    finally { setBusy(false); }
  }}><label htmlFor="workspace-password">Workspace password</label><input id="workspace-password" type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} required />{error && <ErrorNotice message={error} />}<button className="button primary" disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button></form></section></div>;
}
