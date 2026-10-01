# typescript — authored corpus-v2 candidates

AI-authored, pending independent human review. Static validation is separate evidence, not approval. Source is quoted for inspection and must not be executed.

Review the corpus-level context and checklist in the [complete unsigned manifest](../unsigned-review-manifest.json) alongside each case.

## v2-typescript-safe-01 — streaming-artifact-checksum-in-process

Proposed label: **safe**. Human review: **pending**.

Source hash: `57cbb049146eff1e76e5a22a788ef3a382db73af0ecc0d33b65df6b1a98d1630`. Protocol-2.0 case hash: `ce7747a8fe5064e702c480e49fc4ee01a85fbd0bd5859e4eb41a4bafc2080208`.

The legacy shellChecksum name is misleading: the implementation uses crypto and streams without spawning a process. Numeric IDs prevent path syntax.

### checksum.ts

```typescript
import { createHash } from 'node:crypto';
import { createReadStream } from 'node:fs';
export async function shellChecksumForArtifact(storageId: number): Promise<string> {
  if (!Number.isSafeInteger(storageId) || storageId < 1) throw new Error('artifact ID');
  const hash = createHash('sha256');
  const stream = createReadStream(`/srv/artifacts/${storageId}.bin`);
  for await (const chunk of stream) hash.update(chunk);
  return hash.digest('hex');
}
export async function artifactResponse(ownedArtifact: { storageId: number }) {
  return { sha256: await shellChecksumForArtifact(ownedArtifact.storageId) };
}
```

### Derivation

```json
{
  "group": "streaming-artifact-checksum-in-process",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around The caller supplies an authorized numeric artifact record; artifact bytes are hashed as data and never form a command. The operation is compute the sha-256 digest of an owned stored artifact using a streaming in-process hash.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
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
  "scope": "Candidate whole-snippet source-security judgment for compute the sha-256 digest of an owned stored artifact using a streaming in-process hash. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Compute the SHA-256 digest of an owned stored artifact using a streaming in-process hash.",
  "trust_boundary": "The caller supplies an authorized numeric artifact record; artifact bytes are hashed as data and never form a command.",
  "legitimate_examples": [
    {
      "input": "storageId=6 storing UTF-8 bytes abc",
      "expected": "Return ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad."
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
    "https://nodejs.org/api/crypto.html#class-hash"
  ]
}
```

### Regression traps

```json
[
  "Replacing the streaming hash with exec of a command string is unnecessary and would add a boundary; SHA-256 is a content digest, not an authentication MAC here."
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
  "slot_id": "v2-typescript-safe-01",
  "prior_case_id": "typescript-backup-process-safe",
  "prior_source_sha256": "354754d22e7829e9f90ae4ffb7f1aa2a9648f4b5900a1ebf6a2ec47fe2ead99a",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "TypeScript 5.7.3; Node.js 22.14.0; strict mode; @types/node 22.13.10",
  "platform": "Linux x86_64",
  "setup": "Root-owned storage tree with no symlinks; artifact access checked by the caller; blobs at most 8 MiB; SHA-256 used only as an integrity/content identifier."
}
```

### Split

```json
"held_out"
```

## v2-typescript-safe-02 — virtual-zip-member-download

Proposed label: **safe**. Human review: **pending**.

Source hash: `d2a3885045ad001622ef95d9711413aa0b2b3fec350552d62d2a534a97257360`. Protocol-2.0 case hash: `5c785f3130c3fb74cdb3e9842f39a76b47f1ca4928ad46332cff1561971189ef`.

getEntry looks up archive metadata and getData decompresses its contents into memory. A ../-looking key cannot traverse the host filesystem because no path-based write or read consumes it.

### archive-member.ts

```typescript
import AdmZip from 'adm-zip';
export function downloadMember(trustedArchiveBytes: Buffer, memberName: string): Buffer {
  if (memberName.length > 200) throw new Error('member name');
  const archive = new AdmZip(trustedArchiveBytes);
  const member = archive.getEntry(memberName);
  if (!member || member.isDirectory || member.header.size > 65536) {
    throw new Error('missing or oversized member');
  }
  // Member names are virtual keys: nothing is extracted to the filesystem.
  return member.getData();
}
export function responseForMember(archive: Buffer, query: { name: string }) {
  return { mime: 'application/octet-stream', body: downloadMember(archive, query.name) };
}
```

### Derivation

```json
{
  "group": "virtual-zip-member-download",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A user controls only a virtual member key; the server provides an immutable validated archive and performs no filesystem extraction. The operation is return one named entry from an already-authorized, trusted zip archive as download bytes.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
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
  "scope": "Candidate whole-snippet source-security judgment for return one named entry from an already-authorized, trusted zip archive as download bytes. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return one named entry from an already-authorized, trusted ZIP archive as download bytes.",
  "trust_boundary": "A user controls only a virtual member key; the server provides an immutable validated archive and performs no filesystem extraction.",
  "legitimate_examples": [
    {
      "input": "name=manuals/intro.txt in an authorized archive",
      "expected": "Return that archive entry’s bytes, not a host filesystem file."
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
    "https://github.com/cthackers/adm-zip/blob/v0.5.16/README.md"
  ]
}
```

### Regression traps

```json
[
  "Adding extraction to a temporary directory would require a separate containment policy; do not mistake virtual archive paths for host paths."
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
  "slot_id": "v2-typescript-safe-02",
  "prior_case_id": "typescript-document-load-safe",
  "prior_source_sha256": "6e527914bed97473d34a968098f4fb9c51f24d5255d5fe22da291ef926846a9c",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "TypeScript 5.7.3; Node.js 22.14.0; strict mode; @types/node 22.13.10",
  "platform": "Linux x86_64",
  "setup": "adm-zip 0.5.16; @types/adm-zip 0.5.7; esModuleInterop. Archives created by trusted publishing, bounded total uncompressed size 1 MiB, correct headers, no attacker-controlled decompression bombs. All entries of the selected archive are authorized."
}
```

### Split

```json
"held_out"
```

## v2-typescript-safe-03 — mail-api-fixed-origin-recipient-data

Proposed label: **safe**. Human review: **pending**.

Source hash: `4c8a03f0a0f01b18b12e49e5f11815d25699ecfddc17886e2fddc259894a4cb7`. Protocol-2.0 case hash: `29f688d01b7580eca52582d566a7e78aa5e478b4b522d34a6543033707aa5344`.

URL-looking text lives in a JSON request body, not the request destination. The constant HTTPS origin and redirect:error prevent a recipient-controlled second network target.

### mail-api.ts

```typescript
export async function deliverMessage(recipientId: string, text: string, secret: string) {
  if (!/^[a-z0-9-]{1,40}$/.test(recipientId) || text.length > 1000) throw new Error('message');
  const response = await fetch('https://mailer.example.net/v2/send', {
    method: 'POST', redirect: 'error', signal: AbortSignal.timeout(3000),
    headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + secret },
    body: JSON.stringify({ recipientId, text })
  });
  if (response.status !== 202) throw new Error('message rejected');
  return { accepted: true };
}
```

### Derivation

```json
{
  "group": "mail-api-fixed-origin-recipient-data",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A user supplies message data and an authorized recipient identifier; endpoint, token and redirect policy are server-owned. The operation is send a plain-text message to a verified internal account through the configured mail api.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
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
  "scope": "Candidate whole-snippet source-security judgment for send a plain-text message to a verified internal account through the configured mail api. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Send a plain-text message to a verified internal account through the configured mail API.",
  "trust_boundary": "A user supplies message data and an authorized recipient identifier; endpoint, token and redirect policy are server-owned.",
  "legitimate_examples": [
    {
      "input": "recipientId=member-7; text=Visit http://127.0.0.1",
      "expected": "POST literal message text to the fixed mail API and report accepted=true on 202."
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
    "https://fetch.spec.whatwg.org/#request-redirect-mode"
  ]
}
```

### Regression traps

```json
[
  "Do not promote message text or recipient ID into a URL; preserve newlines and Unicode as JSON data without converting them to email headers."
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
  "slot_id": "v2-typescript-safe-03",
  "prior_case_id": "typescript-feed-preview-safe",
  "prior_source_sha256": "3e87072299485e772ba8ec9e96cf8ffdfcbdc68cd6581e58e6cfaa15b465cb28",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "TypeScript 5.7.3; Node.js 22.14.0; strict mode; @types/node 22.13.10",
  "platform": "Linux x86_64",
  "setup": "Mailer resolves recipientId to verified account addresses and sends plain text; it does not fetch URLs in text. Node CA/environment configuration trusted; no custom unverified dispatcher or proxy."
}
```

### Split

```json
"held_out"
```

## v2-typescript-safe-04 — workflow-action-map-dispatch

Proposed label: **safe**. Human review: **pending**.

Source hash: `527ed576da608d62a87bef987e305c11218d77e9982f11d67a87211635944689`. Protocol-2.0 case hash: `34415115b18d7b0c7914d46066b089a1c4b18c82df7db0f0dc092ea8e538d273`.

The action name selects a predeclared function through Map; it is never evaluated as source and names such as constructor or __proto__ are absent.

### workflow.ts

```typescript
type Job = { state: 'held' | 'released'; audit: string[] };
const actions = new Map<string, (job: Job) => void>([
  ['release', job => { job.state = 'released'; job.audit.push('released'); }],
  ['hold', job => { job.state = 'held'; job.audit.push('held'); }]
]);
export function evaluateAction(job: Job, suppliedName: string): Job {
  const action = actions.get(suppliedName);
  if (!action) throw new Error('unknown action');
  action(job);
  return job;
}
export function applyRequest(ownedJob: Job, body: { action: string }) {
  return evaluateAction(ownedJob, body.action);
}
```

### Derivation

```json
{
  "group": "workflow-action-map-dispatch",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A user selects a literal action name; executable handlers are fixed server code and Map lookups have no inherited properties. The operation is apply one of two authorized workflow state transitions and append an audit entry.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
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
  "scope": "Candidate whole-snippet source-security judgment for apply one of two authorized workflow state transitions and append an audit entry. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Apply one of two authorized workflow state transitions and append an audit entry.",
  "trust_boundary": "A user selects a literal action name; executable handlers are fixed server code and Map lookups have no inherited properties.",
  "legitimate_examples": [
    {
      "input": "held job with empty audit; action=release",
      "expected": {
        "state": "released",
        "audit": [
          "released"
        ]
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
    "https://tc39.es/ecma262/#sec-map-objects"
  ]
}
```

### Regression traps

```json
[
  "Converting the Map to a plain object with unchecked property lookup would change behavior for inherited names; returning only a status without updating audit is a regression."
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
  "slot_id": "v2-typescript-safe-04",
  "prior_case_id": "typescript-formula-parser-safe",
  "prior_source_sha256": "27c55c39e5a48cc65f043fa0e919b076f38b4fe807e6d5eb0ccc6d2642a98e28",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "TypeScript 5.7.3; Node.js 22.14.0; strict mode; @types/node 22.13.10",
  "platform": "Linux x86_64",
  "setup": "The caller confirms ownership and permission to perform either action; job is a server-created object, not a request-controlled prototype. The returned object is serialized as JSON."
}
```

### Split

```json
"held_out"
```

## v2-typescript-safe-05 — prepared-audit-message-insertion

Proposed label: **safe**. Human review: **pending**.

Source hash: `aef51ea263ffa7388043064865baaa96235a473633c1add74f882e04d80e6647`. Protocol-2.0 case hash: `cae5b64716f31dae3e76f5260ea19f821f4aa4a24d9b5853abae72d69be1fa0b`.

The SQL structure is constant and better-sqlite3 run binds both values. SQL-looking note text remains data and is not reconstructed as a later query.

### audit-store.ts

```typescript
import Database from 'better-sqlite3';
export function appendAudit(db: Database.Database, account: number, message: string) {
  if (!Number.isSafeInteger(account) || account < 1 || message.length > 1000) throw new Error('audit');
  const statement = db.prepare('INSERT INTO audit(account_id, message) VALUES (?, ?)');
  const result = statement.run(account, message);
  return Number(result.lastInsertRowid);
}
export function saveUserNote(db: Database.Database, accountId: number, body: { note: string }) {
  return { id: appendAudit(db, accountId, body.note) };
}
```

### schema.sql

```typescript
CREATE TABLE audit(id INTEGER PRIMARY KEY, account_id INTEGER NOT NULL, message TEXT NOT NULL);
```

### Derivation

```json
{
  "group": "prepared-audit-message-insertion",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A user supplies the message; the account identifier comes from trusted authentication and both are bound values. The operation is append an exact user note to the authenticated account’s audit table and return its new row id.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
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
  "scope": "Candidate whole-snippet source-security judgment for append an exact user note to the authenticated account’s audit table and return its new row id. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Append an exact user note to the authenticated account’s audit table and return its new row ID.",
  "trust_boundary": "A user supplies the message; the account identifier comes from trusted authentication and both are bound values.",
  "legitimate_examples": [
    {
      "input": "accountId=9; note=Sam's \"DROP TABLE\" reminder",
      "expected": "Insert that exact text once under account 9 and return the inserted ID."
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
    "https://github.com/WiseLibs/better-sqlite3/blob/v11.8.1/docs/api.md"
  ]
}
```

### Regression traps

```json
[
  "Manual quote stripping or replacing INSERT with a read-only operation violates exact message storage; retain the inserted row ID."
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
  "slot_id": "v2-typescript-safe-05",
  "prior_case_id": "typescript-invoice-lookup-safe",
  "prior_source_sha256": "422282a2a7033f62de1a9a891242c6394855c0800f4d2b96eda48eb13e80f403",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "TypeScript 5.7.3; Node.js 22.14.0; strict mode; @types/node 22.13.10",
  "platform": "Linux x86_64",
  "setup": "better-sqlite3 11.8.1; SQLite 3.48; @types/better-sqlite3 7.6.12 and esModuleInterop; trusted schema initialization; audit displayed as escaped text."
}
```

### Split

```json
"held_out"
```

## v2-typescript-safe-06 — smtp-implicit-tls-system-ca

Proposed label: **safe**. Human review: **pending**.

Source hash: `2d98d3f0b882074074e65ad95e5e23f0ccd7a3f00bef6016449d456abf2fafa2`. Protocol-2.0 case hash: `8fa1db5f6b9431dcd9ec38d9b308f0f8c1dc9a4fe39432b175a8ed771aad7b01`.

The TLS client explicitly verifies peer certificates, supplies SNI for hostname checks and does not override checkServerIdentity. Data is delivered only after the TLS handshake succeeds.

### smtp-greeting.ts

```typescript
import * as tls from 'node:tls';
export function readSmtpGreeting(): Promise<string> {
  return new Promise((resolve, reject) => {
    const socket = tls.connect({ host: 'smtp.example.org', port: 465,
      servername: 'smtp.example.org', rejectUnauthorized: true,
      minVersion: 'TLSv1.2' });
    let response = '';
    socket.setTimeout(3000, () => socket.destroy(new Error('deadline')));
    socket.on('data', chunk => {
      response += chunk.toString('utf8');
      if (response.length > 4096) socket.destroy(new Error('greeting too large'));
      else if (response.includes('\r\n')) { socket.end(); resolve(response.split('\r\n')[0]); }
    });
    socket.once('error', reject);
  });
}
```

### Derivation

```json
{
  "group": "smtp-implicit-tls-system-ca",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around Network traffic is untrusted while hostname and Node certificate roots are trusted deployment configuration. The operation is read the first smtp greeting line over implicit tls from the configured mail server.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
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
  "scope": "Candidate whole-snippet source-security judgment for read the first smtp greeting line over implicit tls from the configured mail server. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Read the first SMTP greeting line over implicit TLS from the configured mail server.",
  "trust_boundary": "Network traffic is untrusted while hostname and Node certificate roots are trusted deployment configuration.",
  "legitimate_examples": [
    {
      "input": "Valid matching SMTP server certificate and greeting 220 ready\r\n",
      "expected": "Return 220 ready; reject invalid certificates."
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
    "https://nodejs.org/api/tls.html#tlsconnectoptions-callback"
  ]
}
```

### Regression traps

```json
[
  "A matching SNI string is not itself verification; retain rejectUnauthorized and the default hostname checker."
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
  "slot_id": "v2-typescript-safe-06",
  "prior_case_id": "typescript-metadata-client-safe",
  "prior_source_sha256": "22cd98b81ccb66e023ea9bfe1d575d1a05bedb5831c58ac7883fd353a9eedb1f",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "TypeScript 5.7.3; Node.js 22.14.0; strict mode; @types/node 22.13.10",
  "platform": "Linux x86_64",
  "setup": "SMTP server offers a publicly trusted certificate for smtp.example.org and closes idle connections; no process-level TLS bypass or custom global trust hooks."
}
```

### Split

```json
"held_out"
```

## v2-typescript-vulnerable-01 — tenant-printer-queue-routing

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `b709cb9e925cc01b6cc9180c04370cf77e6c85cc12cf215c97999b7696381d18`. Protocol-2.0 case hash: `eaaa4fd2f0677cc71969d54d880f9c455f1d05e358ca264065d1ef0a4cdcb53a`.

Numeric job validation does not protect the persisted printer name. The name is interpolated into a shell command when the worker executes lpr.

### print.ts

```typescript
import { exec } from 'node:child_process';
import { promisify } from 'node:util';
const run = promisify(exec);
type PrintJob = { serverFileId: number; copies: number };
export async function printJob(job: PrintJob, settings: { queueName: string }) {
  if (!Number.isSafeInteger(job.serverFileId) || job.serverFileId < 1 ||
      !Number.isInteger(job.copies) || job.copies < 1 || job.copies > 5) {
    throw new Error('invalid server print job');
  }
  const file = `/srv/print/${job.serverFileId}.pdf`;
  const command = `/usr/bin/lpr -P ${settings.queueName} -# ${job.copies} ${file}`;
  await run(command, { timeout: 5000, maxBuffer: 4096 });
  return { submitted: true, copies: job.copies };
}
```

### settings.ts

```typescript
export function savePrinter(body: unknown, store: { setQueue(value: string): void }) {
  const candidate = body as { queueName?: unknown };
  if (typeof candidate.queueName !== 'string' || candidate.queueName.length > 80) {
    throw new Error('queue name');
  }
  store.setQueue(candidate.queueName);
}
```

### Derivation

```json
{
  "group": "tenant-printer-queue-routing",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A tenant administrator stores a printer queue name that later reaches a more privileged print worker. The operation is submit the requested number of copies of a server-rendered pdf to the tenant’s selected printer.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "shell-injection",
    "cwe": "CWE-78",
    "path": "print.ts"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for submit the requested number of copies of a server-rendered pdf to the tenant’s selected printer. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Submit the requested number of copies of a server-rendered PDF to the tenant’s selected printer.",
  "trust_boundary": "A tenant administrator stores a printer queue name that later reaches a more privileged print worker.",
  "legitimate_examples": [
    {
      "input": "serverFileId=31; copies=2; queueName=west-wing",
      "expected": "Submit two copies of /srv/print/31.pdf to west-wing and return submitted=true."
    }
  ],
  "permitted_changes": [
    "Use direct execFile arguments and enforce the deployment’s documented queue-name grammar or trusted queue-ID mapping."
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
  "Retain the copy count and wait for successful submission; a fix that only validates the live job payload misses the stored queue setting."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Use direct execFile arguments and enforce the deployment’s documented queue-name grammar or trusted queue-ID mapping."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-typescript-vulnerable-01",
  "prior_case_id": "typescript-backup-process-vulnerable",
  "prior_source_sha256": "bbd3d1816488c4fa2ab9b78caf8425b4ea5552c3f62983c5170908d98d186246",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "TypeScript 5.7.3; Node.js 22.14.0; strict mode; @types/node 22.13.10",
  "platform": "Linux x86_64",
  "setup": "CUPS 2.4.10 /usr/bin/lpr; printer names approved for this tenant by trusted ownership middleware; tenant may edit the text setting but not execute worker commands. PDFs are server-rendered and IDs trusted."
}
```

### Split

```json
"held_out"
```

## v2-typescript-vulnerable-02 — saved-mail-attachment-path

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `7fc4d6f0d956ac2ea3ba6a53736dc7ea946ac4ab8e0c8de4a62a7f4bb24d5b3f`. Protocol-2.0 case hash: `ccac11bf14defbc9950a29873a63de2eba28064d0ad396f911ea2aec36c75b81`.

A stored filename crosses into a later mail worker without containment validation, allowing parent traversal into another account or service-readable file.

### mail-digest.ts

```typescript
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
type Subscription = { accountId: number; attachmentName: string; recipient: string };
export async function sendDigest(subscription: Subscription,
    send: (recipient: string, bytes: Buffer) => Promise<void>) {
  const root = `/srv/account-reports/${subscription.accountId}`;
  const attachment = await readFile(join(root, subscription.attachmentName));
  await send(subscription.recipient, attachment);
  return { sentBytes: attachment.length };
}
```

### subscription.ts

```typescript
export function savedSubscription(accountId: number, accountEmail: string, body: { file: unknown }) {
  if (typeof body.file !== 'string' || body.file.length > 200) throw new Error('file');
  // The digest worker reads this record after the HTTP request has ended.
  return { accountId, recipient: accountEmail, attachmentName: body.file };
}
```

### Derivation

```json
{
  "group": "saved-mail-attachment-path",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A subscriber controls a saved relative attachment name; account ID and verified recipient are server-owned. The operation is email an owned account report, including nested monthly reports, to the account’s verified email.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "path-traversal",
    "cwe": "CWE-22",
    "path": "mail-digest.ts"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for email an owned account report, including nested monthly reports, to the account’s verified email. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Email an owned account report, including nested monthly reports, to the account’s verified email.",
  "trust_boundary": "A subscriber controls a saved relative attachment name; account ID and verified recipient are server-owned.",
  "legitimate_examples": [
    {
      "input": "accountId=5; file=2025/summary.pdf",
      "expected": "Email the bytes of /srv/account-reports/5/2025/summary.pdf to account 5’s verified address."
    }
  ],
  "permitted_changes": [
    "Validate canonical containment under the account root when the worker reads the attachment."
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
    "https://nodejs.org/api/path.html#pathjoinpaths"
  ]
}
```

### Regression traps

```json
[
  "Checking only the live subscription request is insufficient if historical rows remain unsafe; validate at the read boundary and preserve nested reports."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Validate canonical containment under the account root when the worker reads the attachment."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-typescript-vulnerable-02",
  "prior_case_id": "typescript-document-load-vulnerable",
  "prior_source_sha256": "5ee56c3d58023993730d0cb0c5814c0aeff00ca48ff3769bae79c8d10e6bd7ad",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "TypeScript 5.7.3; Node.js 22.14.0; strict mode; @types/node 22.13.10",
  "platform": "Linux x86_64",
  "setup": "Read-only report tree during each job; account IDs numeric, recipients verified server values; subscriber cannot create symlinks. send transmits bytes as an attachment and never treats file content as commands."
}
```

### Split

```json
"held_out"
```

## v2-typescript-vulnerable-03 — opengraph-image-second-hop

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `02f8f3c6f6397f69799d1be16b59dc2f46eca52d0426bfa00a3a563a9e6043b3`. Protocol-2.0 case hash: `16ade0e5aca1b62cd0ea578b857d2585aa1a2e1b6b97d1bffa99bc2336407936`.

Validation of the initial page URL does not cover its image URL. A page author can select an internal absolute URL or public URL that redirects internally.

### open-graph.ts

```typescript
import * as cheerio from 'cheerio';
export async function previewImage(publicPageHtml: string, publicPageUrl: string) {
  // An upstream service already verified and downloaded the public page.
  const $ = cheerio.load(publicPageHtml);
  const imageValue = $('meta[property="og:image"]').attr('content');
  if (!imageValue) return null;
  const imageUrl = new URL(imageValue, publicPageUrl);
  if (!['http:', 'https:'].includes(imageUrl.protocol)) throw new Error('image scheme');
  const response = await fetch(imageUrl, { redirect: 'follow', signal: AbortSignal.timeout(2500) });
  if (!response.ok) throw new Error('image unavailable');
  await response.body?.cancel();
  return { source: imageUrl.toString(), mime: response.headers.get('content-type') };
}
```

### Derivation

```json
{
  "group": "opengraph-image-second-hop",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A public-page author controls og:image metadata, which becomes a second network destination inside the preview service. The operation is inspect the advertised image of a verified public web page and return its media type.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "ssrf",
    "cwe": "CWE-918",
    "path": "open-graph.ts"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for inspect the advertised image of a verified public web page and return its media type. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Inspect the advertised image of a verified public web page and return its media type.",
  "trust_boundary": "A public-page author controls og:image metadata, which becomes a second network destination inside the preview service.",
  "legitimate_examples": [
    {
      "input": "Public page at https://blog.example.org/a with og:image=/photo.png",
      "expected": "Fetch https://blog.example.org/photo.png and return its media type."
    }
  ],
  "permitted_changes": [
    "Apply public-destination and redirect policy independently to the resolved image URL and the actual connection address."
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
    "https://cheerio.js.org/docs/api/classes/Cheerio#attr",
    "https://nodejs.org/api/globals.html#fetch"
  ]
}
```

### Regression traps

```json
[
  "Preserve relative image resolution against the page URL; approving the original page host is not approval for every resource referenced by its HTML."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Apply public-destination and redirect policy independently to the resolved image URL and the actual connection address."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-typescript-vulnerable-03",
  "prior_case_id": "typescript-feed-preview-vulnerable",
  "prior_source_sha256": "05244b4f37ec10ec4caa7e87cc144582d6e192b98f510256b4406ffe8e8e31d8",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "TypeScript 5.7.3; Node.js 22.14.0; strict mode; @types/node 22.13.10",
  "platform": "Linux x86_64",
  "setup": "cheerio 1.0.0; Node fetch; trusted upstream provides bounded public HTML and canonical final page URL. Preview worker can reach private HTTP services; no HTML scripts execute."
}
```

### Split

```json
"held_out"
```

## v2-typescript-vulnerable-04 — queued-transform-worker-source

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `95551ffc736ac8b55e041915788c566794082cd64ef99540e75d5880cedf7816`. Protocol-2.0 case hash: `78500693362269cbee8e0bf0f9ae04bd3b394eba3c47ca1830fd8d4e46180d44`.

Worker eval executes supplied JavaScript with Node capabilities; a separate thread and a time limit do not sandbox filesystem or network access.

### transform.ts

```typescript
import { Worker } from 'node:worker_threads';
type TransformRequest = { javascript: string; rows: Array<Record<string, string>> };
export function transformRows(request: TransformRequest): Promise<unknown> {
  if (request.javascript.length > 2048 || request.rows.length > 20) throw new Error('size');
  const source = "const {parentPort,workerData}=require('node:worker_threads');" +
    'const transform=' + request.javascript + ';parentPort.postMessage(workerData.map(transform));';
  return new Promise((resolve, reject) => {
    const worker = new Worker(source, { eval: true, workerData: request.rows });
    const timer = setTimeout(() => { void worker.terminate(); reject(new Error('deadline')); }, 1000);
    worker.once('message', value => { clearTimeout(timer); void worker.terminate(); resolve(value); });
    worker.once('error', error => { clearTimeout(timer); reject(error); });
  });
}
```

### Derivation

```json
{
  "group": "queued-transform-worker-source",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A low-privilege analyst supplies transformation text; worker threads retain the server’s filesystem/network/process authority. The operation is apply user-selected field projection and renaming to a small batch of tabular string rows.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "dynamic-evaluation",
    "cwe": "CWE-95",
    "path": "transform.ts"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for apply user-selected field projection and renaming to a small batch of tabular string rows. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Apply user-selected field projection and renaming to a small batch of tabular string rows.",
  "trust_boundary": "A low-privilege analyst supplies transformation text; worker threads retain the server’s filesystem/network/process authority.",
  "legitimate_examples": [
    {
      "input": "javascript=(row)=>({city:row.town}); rows=[{town:\"Oslo\",note:\"x\"}]",
      "expected": "Return [{city:\"Oslo\"}] without granting arbitrary server execution."
    }
  ],
  "permitted_changes": [
    "Migrate accepted transforms to a bounded data-only field map with explicit versioning; reject legacy executable transforms."
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
    "https://nodejs.org/api/worker_threads.html#new-workerfilename-options"
  ]
}
```

### Regression traps

```json
[
  "A fix must preserve projection/renaming behavior through a declared data-only transformation schema; moving the same code to another worker does not remove authority."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Migrate accepted transforms to a bounded data-only field map with explicit versioning; reject legacy executable transforms."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-typescript-vulnerable-04",
  "prior_case_id": "typescript-formula-parser-vulnerable",
  "prior_source_sha256": "7db75ab11c3a2c6bd86c844c1f0b3f55b11cda2bcc0930486663978b4d194bc0",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "TypeScript 5.7.3; Node.js 22.14.0; strict mode; @types/node 22.13.10",
  "platform": "Linux x86_64",
  "setup": "No permission sandbox is configured; worker_threads shares process permissions. The public feature promises only field projection/renaming, not arbitrary user programs. Request is size-limited and authenticated."
}
```

### Split

```json
"held_out"
```

## v2-typescript-vulnerable-05 — sqlite-user-selected-order-expression

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `5d91c0efa917a99933f0cf8fa7b9d5052f733582df5a745ceb13179b74cb6f73`. Protocol-2.0 case hash: `c279ff136acb66a829aceda935307d72d74e2893a6095295e571501215514868`.

The owner value is bound, but ORDER BY contains uncontrolled SQL structure. SQLite can evaluate attacker-selected expressions or subqueries in that position without multiple statements.

### case-list.ts

```typescript
import Database from 'better-sqlite3';
export function listCases(db: Database.Database, owner: number, sort: string) {
  if (sort.length > 200) throw new Error('sort length');
  const statement = db.prepare('SELECT id, created_at FROM cases WHERE owner = ? ORDER BY ' + sort + ' LIMIT 20');
  return statement.all(owner);
}
export function handleList(db: Database.Database, accountId: number, query: { sort?: string }) {
  return listCases(db, accountId, query.sort ?? 'created_at DESC');
}
```

### schema.sql

```typescript
CREATE TABLE cases(id INTEGER PRIMARY KEY, owner INTEGER NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE private_flags(name TEXT PRIMARY KEY, enabled INTEGER NOT NULL);
INSERT INTO cases VALUES(1, 4, '2025-01-01'), (2, 4, '2025-03-01');
INSERT INTO private_flags VALUES('billing-migration', 1);
```

### Derivation

```json
{
  "group": "sqlite-user-selected-order-expression",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around A user controls a sort expression but is authorized only for two documented orderings, not arbitrary SQL expressions. The operation is list an owner’s first twenty cases using either chronological or reverse chronological ordering.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "sql-injection",
    "cwe": "CWE-89",
    "path": "case-list.ts"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for list an owner’s first twenty cases using either chronological or reverse chronological ordering. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "List an owner’s first twenty cases using either chronological or reverse chronological ordering.",
  "trust_boundary": "A user controls a sort expression but is authorized only for two documented orderings, not arbitrary SQL expressions.",
  "legitimate_examples": [
    {
      "input": "accountId=4; sort=created_at DESC",
      "expected": "Return case 2 before case 1."
    }
  ],
  "permitted_changes": [
    "Use an explicit map for created_at ASC and created_at DESC; retain owner binding and limit."
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
    "https://github.com/WiseLibs/better-sqlite3/blob/v11.8.1/docs/api.md",
    "https://www.sqlite.org/lang_select.html#orderby"
  ]
}
```

### Regression traps

```json
[
  "Binding the string \"created_at DESC\" as a value yields constant ordering; map the two supported sort choices to trusted SQL fragments instead."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Use an explicit map for created_at ASC and created_at DESC; retain owner binding and limit."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-typescript-vulnerable-05",
  "prior_case_id": "typescript-invoice-lookup-vulnerable",
  "prior_source_sha256": "ddcb0a268d1a17fb2121d5d232872d40ed1a7cb3dccd7df1a8928bcbbeb7c5b3",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "TypeScript 5.7.3; Node.js 22.14.0; strict mode; @types/node 22.13.10",
  "platform": "Linux x86_64",
  "setup": "better-sqlite3 11.8.1 and SQLite 3.48; @types/better-sqlite3 7.6.12, esModuleInterop enabled. schema.sql installed; accountId trusted; private_flags is intentionally not accessible through this endpoint."
}
```

### Split

```json
"held_out"
```

## v2-typescript-vulnerable-06 — line-protocol-token-before-peer-auth

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `5e72faa416657802200f3e248376f50316fb48f18c971af45ed08d618f0c7c42`. Protocol-2.0 case hash: `a37645810d3705a45a307d88f6fa01ca574d5fb6ca5c8b9f6cbfa90a49b930fc`.

rejectUnauthorized=false allows the secure-connect callback even when the peer certificate is untrusted, exposing the token before any authorization check.

### token-client.ts

```typescript
import * as tls from 'node:tls';
export function authenticate(token: string): Promise<string> {
  if (!/^[A-Za-z0-9_-]{16,100}$/.test(token)) throw new Error('token format');
  return new Promise((resolve, reject) => {
    const socket = tls.connect({ host: 'relay.example.net', port: 7443,
      servername: 'relay.example.net', rejectUnauthorized: false }, () => {
      socket.write('AUTH ' + token + '\r\n');
    });
    socket.setTimeout(3000, () => socket.destroy(new Error('deadline')));
    socket.once('data', bytes => { socket.end(); resolve(bytes.toString('utf8')); });
    socket.once('error', reject);
  });
}
```

### Derivation

```json
{
  "group": "line-protocol-token-before-peer-auth",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around An active network attacker can impersonate the relay unless its certificate is validated before the server token is transmitted. The operation is authenticate to a private line-protocol relay and return its acknowledgment.; this candidate is not a paired safe/vulnerable rewrite. Scenario independence across the full corpus requires human judgment and is not established by its distinct identifier."
}
```

### Expected findings

```json
[
  {
    "family": "tls-validation",
    "cwe": "CWE-295",
    "path": "token-client.ts"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Candidate whole-snippet source-security judgment for authenticate to a private line-protocol relay and return its acknowledgment. under the declared deployment; not a claim about absent middleware or third-party package CVEs.",
  "reviewed_residual_risks": [
    "The caller enforces the stated authentication, resource limits and ownership before this bounded operation; that integration must be confirmed by human review.",
    "Availability and vulnerability of pinned third-party packages require separate dependency evidence; no dependency install or execution was performed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Authenticate to a private line-protocol relay and return its acknowledgment.",
  "trust_boundary": "An active network attacker can impersonate the relay unless its certificate is validated before the server token is transmitted.",
  "legitimate_examples": [
    {
      "input": "A server-issued token and authentic relay reply OK",
      "expected": "Transmit AUTH over an authenticated TLS channel and return OK."
    }
  ],
  "permitted_changes": [
    "Enable certificate rejection and use the correct CA plus hostname/SNI before writing AUTH."
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
    "https://nodejs.org/api/tls.html#tlsconnectoptions-callback"
  ]
}
```

### Regression traps

```json
[
  "Checking socket.authorized only after writing AUTH is too late; preserve SNI and reject before sending secrets."
]
```

### Remediation constraints

```json
[
  "Preserve the operation and legitimate input/output examples in operation_contract.",
  "Enable certificate rejection and use the correct CA plus hostname/SNI before writing AUTH."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-typescript-vulnerable-06",
  "prior_case_id": "typescript-metadata-client-vulnerable",
  "prior_source_sha256": "c74a21f8e8d3fca91d446ffc2d39451ed89b6aac45dca2af8fc6bca9b946ca5c",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "TypeScript 5.7.3; Node.js 22.14.0; strict mode; @types/node 22.13.10",
  "platform": "Linux x86_64",
  "setup": "Trusted relay responds with one bounded acknowledgment chunk; token supplied from trusted secret storage, no CR/LF; relay certificate issued by deployed enterprise CA."
}
```

### Split

```json
"held_out"
```

