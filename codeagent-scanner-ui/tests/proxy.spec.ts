import { test, expect } from '@playwright/test';
import { NextRequest } from 'next/server';
import { proxy } from '../lib/server-proxy';

test('backend proxy forwards session, event cursor and streaming response', async () => {
  const original = globalThis.fetch; let captured: { url?: string; headers?: Headers } = {};
  globalThis.fetch = async (input, init) => {
    captured = { url: String(input), headers: new Headers(init?.headers) };
    return new Response('id: 9\nevent: update\ndata: {"seq":9}\n\n', { headers: { 'content-type': 'text/event-stream', 'set-cookie': 'codeagent_session=test; HttpOnly; Path=/; SameSite=Strict' } });
  };
  try {
    const request = new NextRequest('http://localhost:3000/api/backend/events/job?after=5', { headers: { cookie: 'codeagent_session=test', 'last-event-id': '8' } });
    const response = await proxy(request, ['events', 'job']);
    expect(captured.url).toMatch(/\/events\/job\?after=5$/);
    expect(captured.headers?.get('cookie')).toBe('codeagent_session=test');
    expect(captured.headers?.get('last-event-id')).toBe('8');
    expect(response.headers.get('content-type')).toBe('text/event-stream');
    expect(response.headers.get('set-cookie')).toContain('HttpOnly');
    expect(await response.text()).toContain('id: 9');
  } finally { globalThis.fetch = original; }
});

test('backend proxy refuses cross-origin writes and invalid segments', async () => {
  const request = new NextRequest('http://localhost:3000/api/backend/auth/login', { method: 'POST', headers: { origin: 'https://other.example' }, body: '{}' });
  expect((await proxy(request, ['auth', 'login'])).status).toBe(403);
  expect((await proxy(new NextRequest('http://localhost:3000/api/backend/health'), ['..', 'health'])).status).toBe(400);
});

test('standalone proxy accepts configured browser origins despite an internal NextRequest host', async () => {
  const original = globalThis.fetch; const configured = process.env.PUBLIC_ORIGIN;
  let calls = 0;
  process.env.PUBLIC_ORIGIN = 'http://localhost:3000, https://scanner.example/';
  globalThis.fetch = async () => { calls += 1; return Response.json({ job_id: 'scan', status: 'queued' }, { status: 202 }); };
  try {
    for (const origin of ['http://localhost:3000', 'https://scanner.example']) {
      const request = new NextRequest('http://0.0.0.0:3000/api/backend/analyze-async', {
        method: 'POST', headers: { origin, host: 'frontend:3000', 'x-forwarded-host': 'spoof.example' }, body: 'source',
      });
      expect((await proxy(request, ['analyze-async'])).status).toBe(202);
    }
    const spoof = new NextRequest('http://0.0.0.0:3000/api/backend/auth/login', {
      method: 'POST', headers: { origin: 'https://spoof.example', host: 'spoof.example', 'x-forwarded-host': 'spoof.example' }, body: '{}',
    });
    expect((await proxy(spoof, ['auth', 'login'])).status).toBe(403);
    expect(calls).toBe(2);
  } finally {
    globalThis.fetch = original;
    if (configured === undefined) delete process.env.PUBLIC_ORIGIN; else process.env.PUBLIC_ORIGIN = configured;
  }
});
