# javascript — authored corpus-v2 candidates

AI-authored, pending independent human review. Static validation is separate evidence, not approval. Source is quoted for inspection and must not be executed.

Review the corpus-level context and checklist in the [complete unsigned manifest](../unsigned-review-manifest.json) alongside each case.

## v2-javascript-safe-01 — server-generated-png-dimensions

Proposed label: **safe**. Human review: **pending**.

Source hash: `a7254780712749faa3aaf84ad10e959d59f8c6459a7d7604a96e56f1ab2a0dab`. Protocol-2.0 case hash: `a93455896b784084c5e876d39d82eb5a6fa51e4be4667411882e0a22cdf418a8`.

The executable is fixed, shell=false, and the validated identifier forms an absolute filename that cannot be an option or an ImageMagick protocol specifier.

### dimensions.js

```javascript
const { execFile } = require('node:child_process');
const { promisify } = require('node:util');
const run = promisify(execFile);
async function dimensions(assetId) {
  if (typeof assetId !== 'string' || assetId.length !== 32 || !/^[a-f0-9]{32}$/.test(assetId)) throw new Error('asset ID');
  const filename = '/srv/rendered/' + assetId + '.png';
  const { stdout } = await run('/usr/bin/identify', ['-format', '%w %h', filename],
    { shell: false, timeout: 2000, maxBuffer: 1024 });
  const match = /^(\d+) (\d+)$/.exec(stdout);
  if (!match) throw new Error('invalid dimensions');
  return { width: Number(match[1]), height: Number(match[2]) };
}
module.exports = { dimensions };
```

### Derivation

```json
{
  "group": "server-generated-png-dimensions",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A user selects an owned 32-hex asset ID; file bytes are produced by a trusted renderer, not raw user image uploads. The operation is read pixel dimensions of a server-generated png selected by its opaque asset id.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for read pixel dimensions of a server-generated png selected by its opaque asset id. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Read pixel dimensions of a server-generated PNG selected by its opaque asset ID.",
  "trust_boundary": "A user selects an owned 32-hex asset ID; file bytes are produced by a trusted renderer, not raw user image uploads.",
  "legitimate_examples": [
    {
      "input": "assetId=0123456789abcdef0123456789abcdef for a 640x480 PNG",
      "expected": {
        "width": 640,
        "height": 480
      }
    }
  ],
  "permitted_changes": [
    "Internal validation and error handling may change while preserving documented legitimate behavior."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant result, or execute user input as code."
  ]
}
```

### Provenance

```json
{
  "origin": "original AI-authored evaluation candidate",
  "author": "Codex AI author",
  "generated": true,
  "license": "CC0-1.0",
  "references": [
    "https://nodejs.org/api/child_process.html#child_processexecfilefile-args-options-callback"
  ]
}
```

### Regression traps

```json
[
  "Do not replace execFile with a shell command or relax IDs into arbitrary filenames, URL protocols or coder specifications."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-javascript-safe-01",
  "prior_case_id": "javascript-log-command-safe",
  "prior_source_sha256": "112ce1671d2a529d8f5e4cf7e129a505df72a7ad6e39411560c3c57b5e695a68",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Node.js 22.14.0, CommonJS",
  "platform": "Linux x86_64",
  "setup": "ImageMagick 7.1.1 with PNG-only policy, root-owned binary; trusted renderer supplies bounded valid PNG files; authorization middleware verifies ownership before this function."
}
```

### Split

```json
"held_out"
```

## v2-javascript-safe-02 — content-addressed-public-blob-read

Proposed label: **safe**. Human review: **pending**.

Source hash: `700b0dca5dec18217026c1545aad761005680965fc90ca60b43fe9304240f6ea`. Protocol-2.0 case hash: `148d634448273f5c626ad388b00c2b0bc90ffaf4423ed48f198148067ccf47c4`.

An exact hex grammar fixes both path components and forbids separators, dot segments and absolute paths. The read-only public store has no attacker-created symlinks or private entries.

### blob-store.js

```javascript
const fs = require('node:fs/promises');
async function fetchPublicBlob(digest) {
  if (typeof digest !== 'string' || digest.length !== 64 || !/^[a-f0-9]{64}$/.test(digest)) {
    throw new Error('canonical SHA-256 digest required');
  }
  const path = '/srv/public-blobs/' + digest.slice(0, 2) + '/' + digest.slice(2);
  const buffer = await fs.readFile(path);
  return { digest, bytes: buffer };
}
async function route(req, res, next) {
  try { res.type('application/octet-stream').send((await fetchPublicBlob(req.params.digest)).bytes); }
  catch (error) { next(error); }
}
module.exports = { fetchPublicBlob, route };
```

### Derivation

```json
{
  "group": "content-addressed-public-blob-read",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A visitor controls only a canonical lowercase digest, not any filesystem path component or storage entry. The operation is retrieve an immutable public blob by its canonical sha-256 address.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for retrieve an immutable public blob by its canonical sha-256 address. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Retrieve an immutable public blob by its canonical SHA-256 address.",
  "trust_boundary": "A visitor controls only a canonical lowercase digest, not any filesystem path component or storage entry.",
  "legitimate_examples": [
    {
      "input": "digest=64 lowercase hex digits of a published blob",
      "expected": "Return exactly that public blob’s bytes."
    }
  ],
  "permitted_changes": [
    "Internal validation and error handling may change while preserving documented legitimate behavior."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant result, or execute user input as code."
  ]
}
```

### Provenance

```json
{
  "origin": "original AI-authored evaluation candidate",
  "author": "Codex AI author",
  "generated": true,
  "license": "CC0-1.0",
  "references": [
    "https://nodejs.org/api/fs.html#fspromisesreadfilepath-options"
  ]
}
```

### Regression traps

```json
[
  "Using a prefix-only hex regex would let a trailing slash or newline escape the intended identifier grammar; retain full-string validation."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-javascript-safe-02",
  "prior_case_id": "javascript-template-load-safe",
  "prior_source_sha256": "289115f3c913e0b27d1c6606a4027a3e55bddc8270b52d80de978c6c06ef7c49",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Node.js 22.14.0, CommonJS",
  "platform": "Linux x86_64",
  "setup": "Store populated by trusted publishing service; root-owned immutable entries without symlinks; all blobs public and at most 1 MiB. Exact digest length plus regex excludes JavaScript end-anchor newline behavior."
}
```

### Split

```json
"held_out"
```

## v2-javascript-safe-03 — offline-link-inspection-card

Proposed label: **safe**. Human review: **pending**.

Source hash: `44b8f12ecb51fdcbe9df3aaa92de65b343fbe80f1e26f5bef3fb7ffe7fca8eee`. Protocol-2.0 case hash: `4d395cc6a11c5b0b8d68d60b2e50e9cdba7e95a09889bad5e94254fc2e0f081a`.

Despite the function name fetchLinkPreview, the code only uses the URL parser. No network request or background fetch is scheduled, including for private-address strings.

### link-card.js

```javascript
function fetchLinkPreview(input) {
  // This editor preview is deliberately offline: it computes URL metadata.
  if (typeof input !== 'string' || input.length > 2048) throw new Error('link');
  const parsed = new URL(input);
  if (!['http:', 'https:'].includes(parsed.protocol)) throw new Error('web links only');
  return { host: parsed.hostname, path: parsed.pathname,
    encryptedScheme: parsed.protocol === 'https:' };
}
function route(req, res) {
  res.json(fetchLinkPreview(req.body.url));
}
module.exports = { fetchLinkPreview, route };
```

### Derivation

```json
{
  "group": "offline-link-inspection-card",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around An editor supplies arbitrary URL text which is parsed into JSON display fields, never sent to a network client. The operation is display host, path and scheme metadata for a pasted web link without contacting it.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for display host, path and scheme metadata for a pasted web link without contacting it. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Display host, path and scheme metadata for a pasted web link without contacting it.",
  "trust_boundary": "An editor supplies arbitrary URL text which is parsed into JSON display fields, never sent to a network client.",
  "legitimate_examples": [
    {
      "input": "url=http://127.0.0.1/admin",
      "expected": {
        "host": "127.0.0.1",
        "path": "/admin",
        "encryptedScheme": false
      }
    }
  ],
  "permitted_changes": [
    "Internal validation and error handling may change while preserving documented legitimate behavior."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant result, or execute user input as code."
  ]
}
```

### Provenance

```json
{
  "origin": "original AI-authored evaluation candidate",
  "author": "Codex AI author",
  "generated": true,
  "license": "CC0-1.0",
  "references": [
    "https://nodejs.org/api/url.html#the-whatwg-url-api"
  ]
}
```

### Regression traps

```json
[
  "Adding an automatic title-fetch request would change this intentionally offline operation and introduce a new security boundary."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-javascript-safe-03",
  "prior_case_id": "javascript-webhook-preview-safe",
  "prior_source_sha256": "d50ebb71a5ac25baf886d6165e1404961b7dbdd99935b1416b0b895ab5c31fe3",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Node.js 22.14.0, CommonJS",
  "platform": "Linux x86_64",
  "setup": "Express 4.21.2 supplies bounded JSON body and renders JSON as data. The client displays text nodes; no raw HTML injection or downstream fetch consumer exists."
}
```

### Split

```json
"held_out"
```

## v2-javascript-safe-04 — literal-code-sample-html-view

Proposed label: **safe**. Human review: **pending**.

Source hash: `9e388e689781ac75a6715e1930585b4f88b46f28599671a6d9548234d3d72120`. Protocol-2.0 case hash: `78b8bca860f4ec934e6b512b5f72d3fd969d5781102f207aceecaffc756765ef`.

The evaluation-sounding name does not execute code. Every HTML metacharacter is escaped and the only consumer is a static code element.

### code-view.js

```javascript
const ESCAPES = new Map([['&', '&amp;'], ['<', '&lt;'], ['>', '&gt;'],
  ['"', '&quot;'], ["'", '&#39;']]);
function evaluateSnippetForDisplay(source) {
  if (typeof source !== 'string' || source.length > 4096) throw new Error('snippet');
  const escaped = source.replace(/[&<>"']/g, character => ESCAPES.get(character));
  return '<pre><code>' + escaped + '</code></pre>';
}
function route(req, res) {
  res.type('text/html').send(evaluateSnippetForDisplay(req.body.source));
}
module.exports = { evaluateSnippetForDisplay, route };
```

### Derivation

```json
{
  "group": "literal-code-sample-html-view",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A student submits program text, including eval-like syntax, but has no authority to execute it on the server or browser. The operation is render a submitted program excerpt as literal code inside an html preformatted block.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for render a submitted program excerpt as literal code inside an html preformatted block. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Render a submitted program excerpt as literal code inside an HTML preformatted block.",
  "trust_boundary": "A student submits program text, including eval-like syntax, but has no authority to execute it on the server or browser.",
  "legitimate_examples": [
    {
      "input": "source=<script>eval(\"x\")</script>",
      "expected": "Display the exact characters as code text, with markup escaped."
    }
  ],
  "permitted_changes": [
    "Internal validation and error handling may change while preserving documented legitimate behavior."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant result, or execute user input as code."
  ]
}
```

### Provenance

```json
{
  "origin": "original AI-authored evaluation candidate",
  "author": "Codex AI author",
  "generated": true,
  "license": "CC0-1.0",
  "references": [
    "https://tc39.es/ecma262/#sec-string.prototype.replace"
  ]
}
```

### Regression traps

```json
[
  "Stripping script tags changes the displayed source; decoding entities after escaping would reintroduce markup."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-javascript-safe-04",
  "prior_case_id": "javascript-calculator-safe",
  "prior_source_sha256": "e9719ed81dff33eeaa52a40a0c88cf7c1827cc566b830537d515f92cae3bb28f",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Node.js 22.14.0, CommonJS",
  "platform": "Linux x86_64",
  "setup": "Express 4.21.2; response is displayed as HTML exactly once, with no second templating pass or client-side execution of code text."
}
```

### Split

```json
"held_out"
```

## v2-javascript-safe-05 — validated-integer-stock-threshold

Proposed label: **safe**. Human review: **pending**.

Source hash: `15c1c2b0053d4944a6727a516a7290beb63735e705d7451d4ce05af05d03283d`. Protocol-2.0 case hash: `f21402b822829fb46d397d8f15c20e961243b6a4ea6e68097bacddbef52d2359`.

Only a Number that is a finite safe integer in 0..1000 is concatenated. Its decimal string representation cannot contain SQL syntax; the original untrusted text never reaches query.

### inventory-count.js

```javascript
async function lowStockCount(pool, rawThreshold) {
  const threshold = Number(rawThreshold);
  if (!Number.isSafeInteger(threshold) || threshold < 0 || threshold > 1000) {
    throw new Error('threshold must be an integer in 0..1000');
  }
  // Only a checked numeric value, never the original string, becomes SQL.
  const [rows] = await pool.query('SELECT COUNT(*) AS count FROM inventory WHERE units < ' + threshold);
  return Number(rows[0].count);
}
module.exports = { lowStockCount };
```

### schema.sql

```javascript
CREATE TABLE inventory(id INTEGER PRIMARY KEY, units INTEGER NOT NULL);
INSERT INTO inventory VALUES(1, 3), (2, 12), (3, 0);
```

### Derivation

```json
{
  "group": "validated-integer-stock-threshold",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A visitor supplies threshold text; the raw string is converted to a safe integer and range-checked before SQL construction. The operation is count public inventory rows below a bounded integer quantity threshold.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for count public inventory rows below a bounded integer quantity threshold. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Count public inventory rows below a bounded integer quantity threshold.",
  "trust_boundary": "A visitor supplies threshold text; the raw string is converted to a safe integer and range-checked before SQL construction.",
  "legitimate_examples": [
    {
      "input": "rawThreshold=10",
      "expected": 2
    }
  ],
  "permitted_changes": [
    "Internal validation and error handling may change while preserving documented legitimate behavior."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant result, or execute user input as code."
  ]
}
```

### Provenance

```json
{
  "origin": "original AI-authored evaluation candidate",
  "author": "Codex AI author",
  "generated": true,
  "license": "CC0-1.0",
  "references": [
    "https://tc39.es/ecma262/#sec-number.issafeinteger",
    "https://dev.mysql.com/doc/refman/8.4/en/select.html"
  ]
}
```

### Regression traps

```json
[
  "A fix that validates threshold but interpolates rawThreshold would defeat the current safety property; NaN and Infinity must remain rejected."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-javascript-safe-05",
  "prior_case_id": "javascript-account-lookup-safe",
  "prior_source_sha256": "f1364945f7c60505bb02c9677f149350478c58f183da8ff5f67efb11cb2483d7",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Node.js 22.14.0, CommonJS",
  "platform": "Linux x86_64",
  "setup": "mysql2 3.12.0; MySQL 8.4; fixed initialized schema.sql; aggregate uses a read-only account and has no tenant-private inventory."
}
```

### Split

```json
"held_out"
```

## v2-javascript-safe-06 — verified-https-release-events

Proposed label: **safe**. Human review: **pending**.

Source hash: `b6a0932f2d856e80371a49440b1159cf6ade4cf17e0be5a466e0805f75cb2ffe`. Protocol-2.0 case hash: `0b3658ac69a10f8202402821a7f3df78fbc55ca33f650efb559be5a208ffc41e`.

Explicit certificate rejection is enabled and Node HTTPS applies its default hostname check. Status redirects are rejected rather than followed; errors do not produce a fabricated event.

### release-event.js

```javascript
const https = require('node:https');
function latestReleaseEvent() {
  return new Promise((resolve, reject) => {
    const request = https.get('https://releases.example.org/event', {
      rejectUnauthorized: true, timeout: 3000
    }, response => {
      let body = '';
      response.setEncoding('utf8');
      response.on('data', chunk => {
        body += chunk;
        if (body.length > 8192) response.destroy(new Error('event too large'));
      });
      response.on('error', reject);
      response.on('end', () => {
        if (response.statusCode !== 200) return reject(new Error('event unavailable'));
        try { resolve(JSON.parse(body)); } catch (error) { reject(error); }
      });
    });
    request.on('timeout', () => request.destroy(new Error('deadline')));
    request.on('error', reject);
  });
}
module.exports = { latestReleaseEvent };
```

### Derivation

```json
{
  "group": "verified-https-release-events",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around The network may be intercepted; the hostname, Node trust roots and process environment are deployment-owned. The operation is read one bounded json release event from a public https service.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for read one bounded json release event from a public https service. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Read one bounded JSON release event from a public HTTPS service.",
  "trust_boundary": "The network may be intercepted; the hostname, Node trust roots and process environment are deployment-owned.",
  "legitimate_examples": [
    {
      "input": "Valid peer certificate and HTTP 200 body {\"tag\":\"v7\"}",
      "expected": {
        "tag": "v7"
      }
    }
  ],
  "permitted_changes": [
    "Internal validation and error handling may change while preserving documented legitimate behavior."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant result, or execute user input as code."
  ]
}
```

### Provenance

```json
{
  "origin": "original AI-authored evaluation candidate",
  "author": "Codex AI author",
  "generated": true,
  "license": "CC0-1.0",
  "references": [
    "https://nodejs.org/api/https.html#httpsgeturl-options-callback"
  ]
}
```

### Regression traps

```json
[
  "Replacing checkServerIdentity with an empty callback would silently defeat hostname checks even if rejectUnauthorized stays true."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-javascript-safe-06",
  "prior_case_id": "javascript-payment-client-safe",
  "prior_source_sha256": "6330621fb6bc3626f6753ab57e124b1ef10c5b8932ea371e8003f20f984d2e17",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Node.js 22.14.0, CommonJS",
  "platform": "Linux x86_64",
  "setup": "Default Node HTTPS agent and trust roots; NODE_TLS_REJECT_UNAUTHORIZED is not set to 0; no monkey-patched TLS callbacks; endpoint has a publicly trusted matching certificate."
}
```

### Split

```json
"held_out"
```

## v2-javascript-vulnerable-01 — dns-support-diagnostic-command

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `5544e08fb9c531e313f5af53106dd8113fada498ca6111cf193c5aafe58aaf5c`. Protocol-2.0 case hash: `02d1c83bbed3c131eaf5eb5e711633549c8839e45d92ee2ad132460dbd733d95`.

child_process.exec invokes a shell; the domain enters the shell command without separation or DNS-name validation.

### dns-route.js

```javascript
const express = require('express');
const { exec } = require('node:child_process');
const { promisify } = require('node:util');
const run = promisify(exec);
const app = express();
app.get('/support/txt', async (req, res, next) => {
  try {
    const domain = String(req.query.domain || '');
    if (domain.length > 253) return res.sendStatus(400);
    const { stdout } = await run('/usr/bin/dig +short TXT ' + domain,
      { timeout: 2500, maxBuffer: 65536 });
    res.type('text/plain').send(stdout);
  } catch (err) { next(err); }
});
module.exports = app;
```

### Derivation

```json
{
  "group": "dns-support-diagnostic-command",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A support-account holder controls the domain string while the service owns the executable and host privileges. The operation is show dns txt answers for a domain supplied by an authenticated support user.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "shell-injection",
    "cwe": "CWE-78",
    "path": "dns-route.js"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for show dns txt answers for a domain supplied by an authenticated support user. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Show DNS TXT answers for a domain supplied by an authenticated support user.",
  "trust_boundary": "A support-account holder controls the domain string while the service owns the executable and host privileges.",
  "legitimate_examples": [
    {
      "input": "domain=example.org",
      "expected": "Return dig TXT answer text, including quoted spaces, for example.org."
    }
  ],
  "permitted_changes": [
    "Use a direct executable argument list and validate/normalize a DNS hostname before invoking dig."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant result, or execute user input as code."
  ]
}
```

### Provenance

```json
{
  "origin": "original AI-authored evaluation candidate",
  "author": "Codex AI author",
  "generated": true,
  "license": "CC0-1.0",
  "references": [
    "https://nodejs.org/api/child_process.html#child_processexeccommand-options-callback"
  ]
}
```

### Regression traps

```json
[
  "The fix must preserve TXT answers and support valid internationalized domains through a defined IDNA conversion; shell quoting alone must not allow dig option injection."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Use a direct executable argument list and validate/normalize a DNS hostname before invoking dig."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-javascript-vulnerable-01",
  "prior_case_id": "javascript-log-command-vulnerable",
  "prior_source_sha256": "a44bfd3876ba4a943fbb93290449886da8579918e32deb3bdab3d72f6b384c29",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Node.js 22.14.0, CommonJS",
  "platform": "Linux x86_64",
  "setup": "Express 4.21.2; BIND dig 9.18 at /usr/bin/dig; support authentication and rate limits are deployment middleware, output bounded by maxBuffer."
}
```

### Split

```json
"held_out"
```

## v2-javascript-vulnerable-02 — published-theme-css-file

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `b850530238c856a1ebd747eed0174dbd649beff349507f49d7e5a6fba54eee4f`. Protocol-2.0 case hash: `2c6357c3dceaa14e59976dfe1c104240b9060b7f913002714951a4790ee97323`.

path.normalize collapses parent components but does not enforce the resulting path beneath the authorized theme; a relative escape can read sibling files.

### theme-files.js

```javascript
const fs = require('node:fs/promises');
const path = require('node:path');
async function stylesheet(theme, asset) {
  const directory = path.join('/srv/themes', theme.storageId);
  const candidate = path.normalize(path.join(directory, asset));
  // Normalization alone does not confine the file to the published theme.
  return fs.readFile(candidate, 'utf8');
}
async function route(req, res, next) {
  try {
    const text = await stylesheet(req.publishedTheme, String(req.query.asset));
    res.type('text/plain').send(text);
  } catch (err) { next(err); }
}
module.exports = { route, stylesheet };
```

### Derivation

```json
{
  "group": "published-theme-css-file",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around The server selects a published theme object; a visitor controls the asset path beneath it. The operation is serve a named stylesheet from the already-authorized published theme, including nested vendor css.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "path-traversal",
    "cwe": "CWE-22",
    "path": "theme-files.js"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for serve a named stylesheet from the already-authorized published theme, including nested vendor css. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Serve a named stylesheet from the already-authorized published theme, including nested vendor CSS.",
  "trust_boundary": "The server selects a published theme object; a visitor controls the asset path beneath it.",
  "legitimate_examples": [
    {
      "input": "theme.storageId=t17; asset=vendor/reset.css",
      "expected": "Text from /srv/themes/t17/vendor/reset.css."
    }
  ],
  "permitted_changes": [
    "Enforce canonical directory containment and preserve per-theme authorization and nested assets."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant result, or execute user input as code."
  ]
}
```

### Provenance

```json
{
  "origin": "original AI-authored evaluation candidate",
  "author": "Codex AI author",
  "generated": true,
  "license": "CC0-1.0",
  "references": [
    "https://nodejs.org/api/path.html#pathnormalizepath"
  ]
}
```

### Regression traps

```json
[
  "Do not mistake a normalized absolute string for an authorization check; legitimate vendor subdirectories must continue to work."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Enforce canonical directory containment and preserve per-theme authorization and nested assets."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-javascript-vulnerable-02",
  "prior_case_id": "javascript-template-load-vulnerable",
  "prior_source_sha256": "cdd6a9f09314264c8386cd7959dfeea2cfa46cb20c6d6ab7f659aeb97285a728",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Node.js 22.14.0, CommonJS",
  "platform": "Linux x86_64",
  "setup": "Express 4.21.2 route mounting supplies a root-owned theme record whose storageId is alphanumeric. Theme deployment is immutable during reads, paths are Linux. CSS is served as text/plain in this preview endpoint."
}
```

### Split

```json
"held_out"
```

## v2-javascript-vulnerable-03 — customer-health-probe-redirect

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `e5cafa39a8d2402a2eb0449aab5d9ce51e60d44d2ab8bd07e5fbd09cbdd03821`. Protocol-2.0 case hash: `32dfbde92c64c58c25e97f70e6d64cb73c5980c4d1219c406bccf603afff8243`.

HTTPS-only parsing does not establish public reachability. Direct private destinations and redirects into private services remain reachable from the privileged probe.

### probe.js

```javascript
async function probeRegistration(body) {
  const endpoint = new URL(body.endpoint);
  if (endpoint.protocol !== 'https:') throw new Error('HTTPS required');
  const response = await fetch(endpoint, {
    signal: AbortSignal.timeout(3000), redirect: 'follow'
  });
  await response.body?.cancel();
  return { endpoint: endpoint.toString(), healthy: response.status < 500 };
}
async function route(req, res, next) {
  try { res.json(await probeRegistration(req.body)); }
  catch (error) { next(error); }
}
module.exports = { route, probeRegistration };
```

### Derivation

```json
{
  "group": "customer-health-probe-redirect",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A customer supplies an endpoint; the probe runs inside a network that also reaches private HTTPS services. The operation is check whether a customer-registered public https service responds without a server error.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "ssrf",
    "cwe": "CWE-918",
    "path": "probe.js"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for check whether a customer-registered public https service responds without a server error. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Check whether a customer-registered public HTTPS service responds without a server error.",
  "trust_boundary": "A customer supplies an endpoint; the probe runs inside a network that also reaches private HTTPS services.",
  "legitimate_examples": [
    {
      "input": "endpoint=https://status.example.org/ready",
      "expected": "Return the original endpoint and healthy=true for HTTP 204."
    }
  ],
  "permitted_changes": [
    "Keep public HTTPS probes with bounded deadline; reject private/reserved destinations and redirects that leave the approved policy."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant result, or execute user input as code."
  ]
}
```

### Provenance

```json
{
  "origin": "original AI-authored evaluation candidate",
  "author": "Codex AI author",
  "generated": true,
  "license": "CC0-1.0",
  "references": [
    "https://nodejs.org/api/globals.html#fetch"
  ]
}
```

### Regression traps

```json
[
  "A fix must inspect redirect destinations and connection addresses, not merely ban the literal string localhost or require a URL suffix."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Keep public HTTPS probes with bounded deadline; reject private/reserved destinations and redirects that leave the approved policy."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-javascript-vulnerable-03",
  "prior_case_id": "javascript-webhook-preview-vulnerable",
  "prior_source_sha256": "57febf93f7f060cb7d96c5fae6e65b98cce8d66b3afab4a928a0af3f64b2155b",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Node.js 22.14.0, CommonJS",
  "platform": "Linux x86_64",
  "setup": "Node built-in fetch/Undici from Node 22.14; internal service uses a trusted certificate; requests limited to one per customer per minute by trusted middleware. Body is canceled, not rendered."
}
```

### Split

```json
"held_out"
```

## v2-javascript-vulnerable-04 — stored-notification-interpolation-source

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `1f23731d30a731ef9a9661b36ce806f53105985de69607706d41be2bb6ed23a4`. Protocol-2.0 case hash: `3ba04dd132c9a348227f9be854f0c2a5664e4a3622d37183a6bef906f4ac1bcf`.

Stored text becomes JavaScript template-literal source in a new Function. Template expressions and closing backticks can execute code with the worker process privileges.

### notification.js

```javascript
function renderNotification(template, recipient) {
  if (template.length > 500 || recipient.length > 80) throw new Error('too long');
  // Editors may write ordinary text and ${recipient}; never arbitrary JS.
  const render = new Function('recipient', 'return `' + template + '`;');
  return render(recipient);
}
async function deliverSavedNotification(notificationId, recipient, store, mailer) {
  const saved = await store.get(notificationId);
  const text = renderNotification(saved.editorText, recipient);
  await mailer.sendPlainText(recipient, text);
  return { delivered: true, text };
}
module.exports = { renderNotification, deliverSavedNotification };
```

### Derivation

```json
{
  "group": "stored-notification-interpolation-source",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around An editor can save notification text but is not permitted to execute JavaScript in the delivery worker. The operation is render editor-authored plain-text notifications with only the literal recipient placeholder, then deliver them.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "dynamic-evaluation",
    "cwe": "CWE-95",
    "path": "notification.js"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for render editor-authored plain-text notifications with only the literal recipient placeholder, then deliver them. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Render editor-authored plain-text notifications with only the literal recipient placeholder, then deliver them.",
  "trust_boundary": "An editor can save notification text but is not permitted to execute JavaScript in the delivery worker.",
  "legitimate_examples": [
    {
      "input": "editorText=Hello ${recipient}!; recipient=Pat",
      "expected": "Deliver plain text Hello Pat! to the trusted recipient identity."
    }
  ],
  "permitted_changes": [
    "Implement literal ${recipient} substitution without code evaluation; reject unsupported placeholder syntax or treat it as literal documented text."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant result, or execute user input as code."
  ]
}
```

### Provenance

```json
{
  "origin": "original AI-authored evaluation candidate",
  "author": "Codex AI author",
  "generated": true,
  "license": "CC0-1.0",
  "references": [
    "https://tc39.es/ecma262/#sec-function-constructor"
  ]
}
```

### Regression traps

```json
[
  "A replacement that prints ${recipient} unchanged or applies HTML escaping instead of placeholder expansion violates the plain-text operation."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Implement literal ${recipient} substitution without code evaluation; reject unsupported placeholder syntax or treat it as literal documented text."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-javascript-vulnerable-04",
  "prior_case_id": "javascript-calculator-vulnerable",
  "prior_source_sha256": "4c0df99f048d58ea6afccd1d2b9836e20932d862bc679e4cc08a85e4ab569381",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Node.js 22.14.0, CommonJS",
  "platform": "Linux x86_64",
  "setup": "The store is trusted to enforce notification ownership but intentionally preserves editor text verbatim. mailer accepts a trusted account identifier, not raw email headers. recipient is supplied by the server account directory."
}
```

### Split

```json
"held_out"
```

## v2-javascript-vulnerable-05 — warehouse-batch-code-selection

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `311ab569329c72273b6ce74003939ab88811d07dfa954dc746dee6f3ec46c631`. Protocol-2.0 case hash: `4f7d5be5b4fd5bd8e2a329514d4807c45d58149d486f138de3e88112c0bad3ed`.

Wrapping each code in quotes does not bind or escape it. An element can alter the IN expression and the rest of the SELECT even with multipleStatements disabled.

### batch-query.js

```javascript
async function selectBatch(pool, body) {
  if (!Array.isArray(body.codes) || body.codes.length > 20 ||
      body.codes.some(code => typeof code !== 'string' || code.length > 60)) {
    throw new Error('codes must be a bounded string list');
  }
  if (body.codes.length === 0) return [];
  const values = body.codes.map(code => "'" + code + "'").join(',');
  const [rows] = await pool.query('SELECT code, units FROM stock WHERE code IN (' + values + ') ORDER BY code');
  return rows;
}
module.exports = { selectBatch };
```

### schema.sql

```javascript
CREATE TABLE stock(code VARCHAR(60) PRIMARY KEY, units INTEGER NOT NULL, internal_cost DECIMAL(8,2));
INSERT INTO stock VALUES ('A-20', 7, 29.50), ('B-10', 3, 88.10);
```

### Derivation

```json
{
  "group": "warehouse-batch-code-selection",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A partner submits a JSON list of stock codes; only code and units are authorized output columns. The operation is return stock quantities for a bounded set of exact warehouse codes, ordered by code.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "sql-injection",
    "cwe": "CWE-89",
    "path": "batch-query.js"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for return stock quantities for a bounded set of exact warehouse codes, ordered by code. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return stock quantities for a bounded set of exact warehouse codes, ordered by code.",
  "trust_boundary": "A partner submits a JSON list of stock codes; only code and units are authorized output columns.",
  "legitimate_examples": [
    {
      "input": {
        "codes": [
          "B-10",
          "A-20"
        ]
      },
      "expected": [
        {
          "code": "A-20",
          "units": 7
        },
        {
          "code": "B-10",
          "units": 3
        }
      ]
    }
  ],
  "permitted_changes": [
    "Build only the placeholder count dynamically and bind each string value with mysql2 execute."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant result, or execute user input as code."
  ]
}
```

### Provenance

```json
{
  "origin": "original AI-authored evaluation candidate",
  "author": "Codex AI author",
  "generated": true,
  "license": "CC0-1.0",
  "references": [
    "https://sidorares.github.io/node-mysql2/docs/examples/queries/prepared-statements"
  ]
}
```

### Regression traps

```json
[
  "A single ? bound to an array is driver-dependent; use an explicit placeholder per element and preserve the empty-list result."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Build only the placeholder count dynamically and bind each string value with mysql2 execute."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-javascript-vulnerable-05",
  "prior_case_id": "javascript-account-lookup-vulnerable",
  "prior_source_sha256": "c3ef1a5e47556f280ffb27b4832435606f00ef37ed19521e9054335e9366fcfb",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Node.js 22.14.0, CommonJS",
  "platform": "Linux x86_64",
  "setup": "mysql2 3.12.0 promise pool; MySQL 8.4, multipleStatements=false and utf8mb4; trusted schema.sql initialization and read-only service DB account."
}
```

### Split

```json
"held_out"
```

## v2-javascript-vulnerable-06 — wss-notification-bridge-peer-trust

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `9a394ff32bd4192c36a32b465fd06b81711e8d7e47b1f1ed5c97e7557e225d94`. Protocol-2.0 case hash: `c4ce88df97e9e3b123b7e435113a88f72e8b6521d78db5c325adaa3c005929f2`.

rejectUnauthorized=false disables certificate rejection for the secure WebSocket connection; an impostor can capture the token and forge account notifications.

### bridge.js

```javascript
const WebSocket = require('ws');
function firstNotification(accountToken) {
  return new Promise((resolve, reject) => {
    const socket = new WebSocket('wss://events.example.net/account', {
      rejectUnauthorized: false,
      headers: { Authorization: 'Bearer ' + accountToken },
      handshakeTimeout: 3000, maxPayload: 16384
    });
    socket.once('error', reject);
    socket.once('message', data => {
      socket.close();
      resolve(JSON.parse(data.toString('utf8')));
    });
  });
}
module.exports = { firstNotification };
```

### Derivation

```json
{
  "group": "wss-notification-bridge-peer-trust",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around The network is adversarial; service hostname and token are trusted but the peer certificate must authenticate the destination. The operation is return the first account notification from a tls-protected websocket service using a server-held token.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "tls-validation",
    "cwe": "CWE-295",
    "path": "bridge.js"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for return the first account notification from a tls-protected websocket service using a server-held token. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return the first account notification from a TLS-protected WebSocket service using a server-held token.",
  "trust_boundary": "The network is adversarial; service hostname and token are trusted but the peer certificate must authenticate the destination.",
  "legitimate_examples": [
    {
      "input": "Trusted account token and a valid notification {\"type\":\"ready\"}",
      "expected": "Return the notification object only from the authenticated events service."
    }
  ],
  "permitted_changes": [
    "Enable peer verification and configure the enterprise CA explicitly if needed."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant result, or execute user input as code."
  ]
}
```

### Provenance

```json
{
  "origin": "original AI-authored evaluation candidate",
  "author": "Codex AI author",
  "generated": true,
  "license": "CC0-1.0",
  "references": [
    "https://github.com/websockets/ws/blob/8.18.0/doc/ws.md#new-websocketaddress-protocols-options",
    "https://nodejs.org/api/tls.html#tlsconnectoptions-callback"
  ]
}
```

### Regression traps

```json
[
  "Switching to ws:// or deleting the Authorization header breaks the contract; trust the deployed CA while retaining WSS and token authentication."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Enable peer verification and configure the enterprise CA explicitly if needed."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-javascript-vulnerable-06",
  "prior_case_id": "javascript-payment-client-vulnerable",
  "prior_source_sha256": "aab9911825b401f9fb3823300e52b1c09a09607c02597e944ed5e3d79b0d8fc6",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Node.js 22.14.0, CommonJS",
  "platform": "Linux x86_64",
  "setup": "ws 8.18.0, enterprise certificate authority at /run/secrets/events-ca.pem; service emits its first message within three seconds. Caller enforces a total-operation deadline and handles rejected promises."
}
```

### Split

```json
"held_out"
```

