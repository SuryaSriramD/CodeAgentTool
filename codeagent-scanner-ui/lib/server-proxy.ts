import type { NextRequest } from "next/server";

export async function proxy(request: NextRequest, segments: string[]) {
  if (segments.some((segment) => !segment || segment === "." || segment === ".." || segment.includes("/") || segment.includes("\\"))) {
    return Response.json({ error: { message: "Invalid API path" } }, { status: 400 });
  }
  // Origin comes exclusively from server configuration; callers cannot choose
  // an upstream host or escape the API path through an absolute URL.
  const base = (process.env.API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
  const url = `${base}/${segments.map(encodeURIComponent).join("/")}${request.nextUrl.search}`;
  const headers = new Headers();
  for (const name of ["content-type", "accept", "cookie", "last-event-id", "authorization"]) {
    const value = request.headers.get(name); if (value) headers.set(name, value);
  }
  // Standalone/reverse-proxy NextRequest URLs may contain an internal bind host.
  // Trust only operator-configured public origins, never forwarded Host headers.
  const allowedOrigins = new Set((process.env.PUBLIC_ORIGIN || "http://localhost:3000,http://127.0.0.1:3000")
    .split(",").map((value) => value.trim().replace(/\/+$/, "")).filter(Boolean));
  const origin = request.headers.get("origin");
  if (!["GET", "HEAD", "OPTIONS"].includes(request.method) && origin && !allowedOrigins.has(origin)) {
    return Response.json({ error: { message: "Cross-origin requests are not allowed" } }, { status: 403 });
  }
  try {
    const upstream = await fetch(url, {
      method: request.method, headers, cache: "no-store", redirect: "manual",
      body: ["GET", "HEAD"].includes(request.method) ? undefined : request.body,
      signal: request.signal, duplex: "half",
    } as RequestInit & { duplex: "half" });
    const responseHeaders = new Headers();
    for (const name of ["content-type", "content-disposition", "cache-control", "retry-after"]) {
      const value = upstream.headers.get(name); if (value) responseHeaders.set(name, value);
    }
    for (const cookie of upstream.headers.getSetCookie()) responseHeaders.append("set-cookie", cookie);
    responseHeaders.set("Cache-Control", "no-store");
    responseHeaders.set("X-Accel-Buffering", "no");
    return new Response(upstream.body, { status: upstream.status, headers: responseHeaders });
  } catch {
    return Response.json({ error: { message: "The scanner API is unavailable. Check the backend address and service." } }, { status: 502 });
  }
}
