import type { NextRequest } from "next/server";
import { proxy } from "@/lib/server-proxy";
export const runtime = "nodejs";
export const dynamic = "force-dynamic";
type Context = { params: Promise<{ path: string[] }> };
async function handler(request: NextRequest, context: Context) { return proxy(request, (await context.params).path); }
export { handler as GET, handler as POST, handler as PATCH, handler as DELETE, handler as PUT };
