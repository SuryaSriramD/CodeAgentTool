# fsharp — authored corpus-v2 candidates

AI-authored, pending independent human review. Static validation is separate evidence, not approval. Source is quoted for inspection and must not be executed.

Review the corpus-level context and checklist in the [complete unsigned manifest](../unsigned-review-manifest.json) alongside each case.

## v2-fsharp-safe-01 — A retry policy rejects unknown mode names without evaluating configuration text

Proposed label: **safe**. Human review: **pending**.

Source hash: `3b702d3cd24767d734adc095898c3a6cbfe9f8573e99516914a5f0db60cfcb69`. Protocol-2.0 case hash: `e6bd7f779c07cedbe86897ddab240ad99e69356b4323863e4eeb5d9ceefef997`.

Configuration text is matched against two literal names, and the attempt bound makes the integer shift and multiplication safe. No expression parser or shell evaluates the mode.

### src/RetryPolicy.fs

```fsharp
module RetryPolicy
open System
let delays (mode: string) (attempts: int) =
    if attempts < 0 || attempts > 5 then invalidArg "attempts" "range"
    let initial =
        match mode with
        | "interactive" -> 100
        | "batch" -> 1000
        | _ -> invalidArg "mode" "unknown"
    [ for step in 0 .. attempts - 1 do
        yield TimeSpan.FromMilliseconds(float (initial * (1 <<< step))) ]
```

### Derivation

```json
{
  "group": "fsharp-closed-retry-policy",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "A small business configuration language is explicitly an enum with arithmetic bounds rather than arbitrary executable input. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "Dynamic-evaluation and arithmetic false-positive control in bounded policy selection.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Build a deterministic bounded exponential retry schedule.",
  "trust_boundary": "A user selects one of two modes and up to five attempts; arbitrary executable formulas are not accepted.",
  "legitimate_examples": [
    {
      "input": "interactive, 3",
      "expected": "Return delays of 100, 200 and 400 milliseconds."
    },
    {
      "input": "batch; command, 2",
      "expected": "Reject the mode rather than interpret it."
    }
  ],
  "permitted_changes": [
    "Preserve exact schedules and the attempt cap.",
    "Keep mode selection as a closed match."
  ],
  "forbidden_changes": [
    "Do not delete the demonstrated operation or replace its output with a constant.",
    "Do not change the documented ownership, return convention or accepted legitimate inputs without updating every included caller."
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
    "https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/functions/",
    "https://learn.microsoft.com/en-us/dotnet/api/system.xml.xmlreadersettings"
  ]
}
```

### Regression traps

```json
[
  "Changing the mode into an eval-based expression expands configuration into code.",
  "Lifting the attempt bound makes shift and delay overflow possible."
]
```

### Remediation constraints

```json
[
  "Preserve exact schedules and the attempt cap.",
  "Keep mode selection as a closed match."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-fsharp-safe-01",
  "prior_case_id": "fsharp-invoice-command-safe",
  "prior_source_sha256": "7e7132148f85da23c02174a6857223fbbd3f11d42ace01c643b8a2d4fa8d23e5",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; F# 8",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Linux x86-64",
  "setup": "Functions receive non-null values; configuration, executable paths and injected database connections are trusted. .NET 8 TimeSpan; zero attempts returns an empty list and no wait is performed by this helper."
}
```

### Split

```json
"held_out"
```

## v2-fsharp-safe-02 — Invitation tokens use operating-system randomness and a bounded lifetime

Proposed label: **safe**. Human review: **pending**.

Source hash: `3f445b85be11ebf3b90a72949d856f342c5da5021164deeeab9e91aa8183603c`. Protocol-2.0 case hash: `cddf7514d220f807af2abe44612442f60175c819faba2f4a4d63101f771dcfd9`.

The token contains 256 bits from the operating-system CSPRNG and the URL-safe encoding does not reduce entropy. Lifetime is bounded and computed from a caller-owned time source.

### src/InvitationToken.fs

```fsharp
module InvitationToken
open System
open System.Security.Cryptography
let issue (now: DateTimeOffset) (minutes: int) =
    if minutes < 1 || minutes > 60 then invalidArg "minutes" "range"
    let bytes = RandomNumberGenerator.GetBytes(32)
    let token =
        Convert.ToBase64String(bytes).TrimEnd('=').Replace('+', '-').Replace('/', '_')
    CryptographicOperations.ZeroMemory(Span<byte>(bytes))
    let expires = now.AddMinutes(float minutes)
    token, expires
```

### Derivation

```json
{
  "group": "fsharp-invitation-csprng-expiry",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "The operation generates a fresh bearer secret rather than verifying an HMAC, with randomness and expiry as its distinct invariants. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "Cryptographic random secret generation and bounded issuance metadata.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Issue an opaque invitation secret and its expiration timestamp.",
  "trust_boundary": "A user may request an allowed lifetime but cannot influence random bytes; the token is returned only to the authorized invitation issuer.",
  "legitimate_examples": [
    {
      "input": "now=2025-01-01T00:00:00Z, minutes=15",
      "expected": "Return a 43-character unpadded URL-safe token and expiry 00:15:00Z."
    },
    {
      "input": "minutes=61",
      "expected": "Reject without issuing a token."
    }
  ],
  "permitted_changes": [
    "Keep cryptographic randomness, 32 random bytes and bounded expiry.",
    "Do not derive the secret from names, timestamps or System.Random."
  ],
  "forbidden_changes": [
    "Do not delete the demonstrated operation or replace its output with a constant.",
    "Do not change the documented ownership, return convention or accepted legitimate inputs without updating every included caller."
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
    "https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/functions/",
    "https://learn.microsoft.com/en-us/dotnet/api/system.xml.xmlreadersettings"
  ]
}
```

### Regression traps

```json
[
  "Base64 encoding is transport representation, not encryption or entropy generation.",
  "The caller must store only a suitable token verifier and enforce single use; this helper does not claim to implement redemption."
]
```

### Remediation constraints

```json
[
  "Keep cryptographic randomness, 32 random bytes and bounded expiry.",
  "Do not derive the secret from names, timestamps or System.Random."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-fsharp-safe-02",
  "prior_case_id": "fsharp-support-process-safe",
  "prior_source_sha256": "28914a708b283fbdd7efb4eae69caf5873f87ccf8c2cc6bbcfb95f34aa2851dd",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; F# 8",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Linux x86-64",
  "setup": "Functions receive non-null values; configuration, executable paths and injected database connections are trusted. .NET 8 RandomNumberGenerator; trusted now is far enough from DateTimeOffset.MaxValue for the lifetime; the caller stores and redeems tokens with single-use expiry enforcement."
}
```

### Split

```json
"held_out"
```

## v2-fsharp-safe-03 — A database paging request binds numeric bounds and keeps ordering fixed

Proposed label: **safe**. Human review: **pending**.

Source hash: `db20abb42b7b5e4147a72da0f0ff4da35b11267d705f51c17308cb6a5763df44`. Protocol-2.0 case hash: `2cd85acf72f00f34545f60fe0894f828858bd6d791105b25a7a0772358d22ef7`.

Both numeric values are bound with explicit SQL types; the ordering and query structure are fixed. The page bound also limits result volume.

### src/RecentEvents.fs

```fsharp
module RecentEvents
open System
open System.Data
open Microsoft.Data.SqlClient
let read (connection: SqlConnection) (afterId: int64) (count: int) =
    if afterId < 0L || count < 1 || count > 100 then invalidArg "paging" "range"
    use command = connection.CreateCommand()
    command.CommandText <- "SELECT TOP (@count) Id FROM Events WHERE Id > @after ORDER BY Id ASC"
    command.Parameters.Add("@count", SqlDbType.Int).Value <- count
    command.Parameters.Add("@after", SqlDbType.BigInt).Value <- afterId
    use reader = command.ExecuteReader()
    [ while reader.Read() do yield reader.GetInt64(0) ]
```

### Derivation

```json
{
  "group": "fsharp-numeric-event-cursor",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "A safe paged query has cursor ordering and result-count invariants distinct from scalar string lookup or IN-list assembly. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "Fixed SQL structure and typed paging values.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return the next ascending event IDs after an exclusive cursor.",
  "trust_boundary": "A client chooses a cursor and page count but cannot select SQL structure or arbitrary order expressions.",
  "legitimate_examples": [
    {
      "input": "afterId=10, count=2 with rows 10,11,15",
      "expected": "Return [11;15]."
    },
    {
      "input": "count=101",
      "expected": "Reject before executing the query."
    }
  ],
  "permitted_changes": [
    "Keep typed parameters, exclusive cursor and ascending order.",
    "Maintain the page-size bound."
  ],
  "forbidden_changes": [
    "Do not delete the demonstrated operation or replace its output with a constant.",
    "Do not change the documented ownership, return convention or accepted legitimate inputs without updating every included caller."
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
    "https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/functions/",
    "https://learn.microsoft.com/en-us/dotnet/api/system.xml.xmlreadersettings"
  ]
}
```

### Regression traps

```json
[
  "Replacing > with >= repeats the cursor event.",
  "Interpolating even validated numbers obscures the explicit parameter contract."
]
```

### Remediation constraints

```json
[
  "Keep typed parameters, exclusive cursor and ascending order.",
  "Maintain the page-size bound."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-fsharp-safe-03",
  "prior_case_id": "fsharp-http-callback-safe",
  "prior_source_sha256": "544143fb30d416a52becfbef15a6336dff0818a749d48c317485d74c8f0e86ec",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; F# 8",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Linux x86-64",
  "setup": "Functions receive non-null values; configuration, executable paths and injected database connections are trusted. SQL Server 2022; Microsoft.Data.SqlClient 5.2.2; Id is unique BIGINT; connection visibility is authorized by the caller."
}
```

### Split

```json
"held_out"
```

## v2-fsharp-safe-04 — A bounded binary export is compressed without interpreting its content

Proposed label: **safe**. Human review: **pending**.

Source hash: `decdcc3265d072022b96a08d054094763af43db4fb1974fecddd4c3f26c66d78`. Protocol-2.0 case hash: `32403bbd553bb9c43342a7ee2949a0477870e49e9f8639220020d2e68d41fcde`.

The bounded byte array is passed to a trusted compression writer without parsing, executing or formatting its contents. Disposing the compressor before reading the destination completes the gzip trailer.

### src/ExportCompression.fs

```fsharp
module ExportCompression
open System
open System.IO
open System.IO.Compression
let pack (payload: byte[]) =
    if payload.Length > 65536 then invalidArg "payload" "size"
    use destination = new MemoryStream()
    do
        use compressor = new GZipStream(destination, CompressionLevel.Fastest, true)
        compressor.Write(payload, 0, payload.Length)
    let complete = destination.ToArray()
    if complete.Length = 0 then failwith "empty gzip output"
    complete
```

### Derivation

```json
{
  "group": "fsharp-bounded-gzip-export",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "The safe operation is a binary compression writer with explicit disposal ordering, wholly separate from XML feed parsing. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "Bounded binary transformation with no executable or parser language.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return a complete gzip member representing exactly one bounded binary export.",
  "trust_boundary": "A tenant controls export bytes; it cannot select executable code, filesystem paths or compression plugins.",
  "legitimate_examples": [
    {
      "input": "Payload containing NUL and percent bytes",
      "expected": "Decompression by the recipient recovers every original byte."
    },
    {
      "input": "Empty payload",
      "expected": "Return a complete gzip representation of zero bytes, not an empty output file."
    }
  ],
  "permitted_changes": [
    "Keep the input bound and dispose the compressor before taking destination bytes.",
    "Preserve binary transparency and ownership of the returned byte array."
  ],
  "forbidden_changes": [
    "Do not delete the demonstrated operation or replace its output with a constant.",
    "Do not change the documented ownership, return convention or accepted legitimate inputs without updating every included caller."
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
    "https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/functions/",
    "https://learn.microsoft.com/en-us/dotnet/api/system.xml.xmlreadersettings"
  ]
}
```

### Regression traps

```json
[
  "Reading MemoryStream before compressor disposal can omit the gzip trailer.",
  "Converting the payload to a string loses binary data and is unnecessary."
]
```

### Remediation constraints

```json
[
  "Keep the input bound and dispose the compressor before taking destination bytes.",
  "Preserve binary transparency and ownership of the returned byte array."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-fsharp-safe-04",
  "prior_case_id": "fsharp-binary-state-safe",
  "prior_source_sha256": "e42a5fb4c3240e3138e5561a14a6027a212561f717ef3b16ce323d486bc7ea09",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; F# 8",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Linux x86-64",
  "setup": "Functions receive non-null values; configuration, executable paths and injected database connections are trusted. .NET 8 built-in GZipStream; payload storage is stable for the call; compression is not combined with secret data or exposed through a chosen-input length oracle."
}
```

### Split

```json
"held_out"
```

## v2-fsharp-safe-05 — A diagnostic bundle escapes control characters without formatting evaluation

Proposed label: **safe**. Human review: **pending**.

Source hash: `245c863861451e2a862d6240b485cdf0b5870066aed4e8b4e086d0c286d8e3e3`. Protocol-2.0 case hash: `b4657f99ae4175360bc782126872283b55f8e2d6615863879cc902c14e938d88`.

The input is appended as characters after escaping record separators and backslashes. Percent sequences and braces are never evaluated by a formatting engine.

### src/DiagnosticLine.fs

```fsharp
module DiagnosticLine
open System
open System.Text
let render (field: string) =
    if field.Length > 256 then invalidArg "field" "size"
    let builder = StringBuilder("field=")
    for ch in field do
        match ch with
        | '\n' -> builder.Append("\\n") |> ignore
        | '\r' -> builder.Append("\\r") |> ignore
        | '\\' -> builder.Append("\\\\") |> ignore
        | value -> builder.Append(value) |> ignore
    builder.Append('\n').ToString()
```

### Derivation

```json
{
  "group": "fsharp-reversible-diagnostic-escaping",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "The safe case has reversible record-boundary encoding rather than simply a fixed printf format. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "Format and log-boundary false-positive control with explicit escaping.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Render one reversible diagnostic field on one physical line.",
  "trust_boundary": "A remote client controls field text; the service owns the log prefix and line boundaries.",
  "legitimate_examples": [
    {
      "input": "Field a followed by newline then b",
      "expected": "Return field=a\\nb followed by one real newline."
    },
    {
      "input": "Field %s {0}",
      "expected": "Preserve both sequences literally."
    }
  ],
  "permitted_changes": [
    "Keep backslash and newline escaping unambiguous and preserve all accepted text.",
    "Retain the bounded field length."
  ],
  "forbidden_changes": [
    "Do not delete the demonstrated operation or replace its output with a constant.",
    "Do not change the documented ownership, return convention or accepted legitimate inputs without updating every included caller."
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
    "https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/functions/",
    "https://learn.microsoft.com/en-us/dotnet/api/system.xml.xmlreadersettings"
  ]
}
```

### Regression traps

```json
[
  "Escaping newlines without escaping backslashes makes decoding ambiguous.",
  "Changing Append to an input-controlled format string introduces new semantics."
]
```

### Remediation constraints

```json
[
  "Keep backslash and newline escaping unambiguous and preserve all accepted text.",
  "Retain the bounded field length."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-fsharp-safe-05",
  "prior_case_id": "fsharp-digest-scope-safe",
  "prior_source_sha256": "cee489ed5dbf634cab9455784f1cbce30463a650aff4f464dd0f1c8969f5a211",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; F# 8",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Linux x86-64",
  "setup": "Functions receive non-null values; configuration, executable paths and injected database connections are trusted. .NET UTF-16 strings; downstream decoder recognizes only the documented escapes and never evaluates code."
}
```

### Split

```json
"held_out"
```

## v2-fsharp-safe-06 — Request completion logs only an explicit nonsecret audit projection

Proposed label: **safe**. Human review: **pending**.

Source hash: `0d846afe28b9f4c8eab90827cd3fa3545003613e8fd7b0af10b582412d8615b9`. Protocol-2.0 case hash: `704f3e7bda01847b024528fde9942de7d73c15535450564d6ba2db3da764e0b4`.

The serializer receives a newly constructed allow-listed audit record, not the incoming request object. Authorization and body fields can contain secrets but are never copied into the persisted JSON or used as a format program.

### src/RequestAudit.fs

```fsharp
module RequestAudit
open System
open System.Text.Json
type Incoming = { Method: string; RequestId: Guid; Authorization: string; Body: string }
type Entry = { Method: string; Route: string; RequestId: string; Status: int }
let serialize (routeName: string) (request: Incoming) (status: int) =
    if status < 100 || status > 599 then invalidArg "status" "range"
    if routeName.Length > 80 then invalidArg "routeName" "length"
    let methodName =
        match request.Method with
        | "GET" | "POST" | "PUT" | "PATCH" | "DELETE" -> request.Method
        | _ -> "OTHER"
    let entry = { Method = methodName; Route = routeName;
                  RequestId = request.RequestId.ToString("D"); Status = status }
    JsonSerializer.Serialize(entry)
```

### src/RequestCompletion.fs

```fsharp
module RequestCompletion
open System.IO
let recordPasswordChange (audit: TextWriter) (request: RequestAudit.Incoming) (status: int) =
    let encoded = RequestAudit.serialize "account.password-change" request status
    audit.WriteLine(encoded)
    audit.Flush()
```

### Derivation

```json
{
  "group": "fsharp-request-audit-allowlisted-projection",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "This operation enforces nonsecret field selection at an audit boundary using typed projection and a visible fixed-route caller. It does not launch a tool or inspect archive contents. Conceptual independence remains subject to human review.",
  "retired_drafts": [
    {
      "reason": "Replaced before scanner exposure after cross-language audit identified a substantially shared operation/mechanism.",
      "overlap_case_ids": [
        "v2-scala-safe-04"
      ],
      "retired_before_scanner_exposure": true,
      "case_snapshot": {
        "id": "v2-fsharp-safe-06",
        "language": "fsharp",
        "vulnerable": false,
        "scenario": "A preflight worker uses a closed executable argument vector",
        "files": {
          "src/ArchivePreflight.fs": "module ArchivePreflight\nopen System\nopen System.Diagnostics\nlet inspect () =\n    let start = ProcessStartInfo(\"/usr/bin/unzip\")\n    start.UseShellExecute <- false\n    start.RedirectStandardOutput <- true\n    start.ArgumentList.Add \"-Z1\"\n    start.ArgumentList.Add \"/srv/jobs/staged.zip\"\n    use child = Process.Start start\n    if isNull child then failwith \"spawn\"\n    let listing = child.StandardOutput.ReadToEnd()\n    child.WaitForExit()\n    if child.ExitCode <> 0 then failwith \"invalid archive\"\n    listing\n"
        },
        "expected_findings": [],
        "rationale": "The inspection command and path are fixed and launched without a shell. Archive entry names appear only in captured output; this helper does not extract them.",
        "remediation_constraints": [
          "Keep listing-only behavior, fixed paths and non-shell invocation.",
          "Do not treat successful listing as permission to extract unsafe member paths."
        ],
        "runtime_assumptions": {
          "runtime": ".NET 8.0; F# 8",
          "libraries": [
            ".NET 8 BCL"
          ],
          "platform": "Linux x86-64",
          "setup": "Functions receive non-null values; configuration, executable paths and injected database connections are trusted. Info-ZIP unzip 6.0 is a trusted system installation; caller enforces an archive-size limit, output cap and deadline; staged.zip is a private immutable file."
        },
        "operation_contract": {
          "purpose": "Return the member-name listing of one staged archive for later policy checks.",
          "trust_boundary": "An uploader controls archive bytes but not the executable path, arguments or staging filename.",
          "legitimate_examples": [
            {
              "input": "Archive containing a member named ../note",
              "expected": "Return the literal member name for policy review without extracting it."
            },
            {
              "input": "Invalid archive",
              "expected": "Report helper failure after child cleanup."
            }
          ],
          "permitted_changes": [
            "Keep listing-only behavior, fixed paths and non-shell invocation.",
            "Do not treat successful listing as permission to extract unsafe member paths."
          ],
          "forbidden_changes": [
            "Do not delete the demonstrated operation or replace its output with a constant.",
            "Do not change the documented ownership, return convention or accepted legitimate inputs without updating every included caller."
          ]
        },
        "regression_traps": [
          "Listing an unsafe-looking member is not itself filesystem traversal.",
          "A later extractor must separately enforce containment and is not implied safe here."
        ],
        "ground_truth_scope": {
          "profile": "security-v2",
          "scope": "Process construction and nonextracting archive inspection; trusted tool defects are outside this source evaluation.",
          "reviewed_residual_risks": [
            "AI-authored candidate: labels, scope and independence require human review before freezing.",
            "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
          ]
        },
        "derivation": {
          "group": "fsharp-fixed-archive-listing-only",
          "origin": "new AI-authored candidate",
          "related_case_ids": [],
          "independence_rationale": "An attacker controls a data file consumed by a fixed utility, while path traversal is deliberately a later policy boundary rather than this operation. Independence is a proposed classification pending human review; no effective sample size is claimed."
        },
        "provenance": {
          "origin": "original AI-authored evaluation candidate",
          "author": "Codex AI author",
          "generated": true,
          "license": "CC0-1.0",
          "references": [
            "https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/functions/",
            "https://learn.microsoft.com/en-us/dotnet/api/system.xml.xmlreadersettings"
          ]
        },
        "split": "held_out",
        "human_review": {
          "status": "pending",
          "reviewer_kind": null,
          "reviewer": null,
          "reviewed_at": null,
          "notes": null,
          "review_schema_version": "2.0",
          "reviewed_content_sha256": null,
          "reviewed_case_sha256": null
        }
      },
      "source_sha256": "6674f9eaab630c13eab225e6777a69cc09e61642cf4d961bd77b9c2f8015b0c5"
    }
  ]
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
  "scope": "Data minimization in structured audit output and prevention of format/log injection. This case does not claim to implement authentication, authorization or password changes themselves.",
  "reviewed_residual_risks": [
    "AI candidate: human review of labels, runtime assumptions and cross-corpus independence remains pending.",
    "Caller responsibilities are explicit assumptions, not a claim of whole-application security."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Write one structured password-change completion event containing method, a fixed route name, a correlation ID and status, while excluding submitted credentials.",
  "trust_boundary": "The client controls authorization/body text and method input. The service generates the request GUID and the included completion caller chooses the fixed route label and actual response status.",
  "legitimate_examples": [
    {
      "input": "POST request with Authorization=Bearer secret and Body containing an old/new password, status=204",
      "expected": "Write one JSON event containing POST, account.password-change, the request GUID and 204; neither secret field nor its value appears."
    },
    {
      "input": "An unknown method spelling, status=400",
      "expected": "Write Method=OTHER and the remaining approved fields, without serializing the raw method."
    }
  ],
  "permitted_changes": [
    "Keep the explicit audit projection and never serialize the Incoming record or arbitrary headers/body.",
    "Retain a fixed service route label, GUID correlation, validated status and one JSON record per line.",
    "Preserve operator diagnostics without logging password or authorization values."
  ],
  "forbidden_changes": [
    "Do not delete the operation or replace its result with a constant.",
    "Do not expose credentials or change the documented input/output contract."
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
    "https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/how-to",
    "https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/records"
  ]
}
```

### Regression traps

```json
[
  "Serializing the full incoming record and removing a few known secret substrings is not equivalent to the allow-list.",
  "Adding the raw request URL could expose query-string credentials; the current route label is deliberately service-owned.",
  "Writing an unencoded user object through string concatenation can break log record boundaries."
]
```

### Remediation constraints

```json
[
  "Keep the explicit audit projection and never serialize the Incoming record or arbitrary headers/body.",
  "Retain a fixed service route label, GUID correlation, validated status and one JSON record per line.",
  "Preserve operator diagnostics without logging password or authorization values."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-fsharp-safe-06",
  "prior_case_id": "fsharp-xml-configuration-safe",
  "prior_source_sha256": "9146a7e3ea465fcdc808c00c5043e71e3b5532d6baaa10a37f0476ad8a044eb6",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; F# 8",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Linux x86-64",
  "setup": ".NET 8; F#8; compile RequestAudit.fs before RequestCompletion.fs. System.Text.Json serializes public F# record properties with default encoding. Ingress bounds method and body size, all strings are non-null, the server generates RequestId, and a serialized caller owns the TextWriter. The body may contain credentials and must never be logged."
}
```

### Split

```json
"held_out"
```

## v2-fsharp-vulnerable-01 — SKU lookup lets a decoded route segment alter a SQL literal

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `2fd736115a94ed6031c3071c664948718caaa994e9d606d842f800f30453db88`. Protocol-2.0 case hash: `7fd5846d6c4743a8ee05da59c6837f58173e36e6b306491b683af39cfde6fa88`.

The route adapter decodes percent escapes into the SKU and the lookup inserts the result into SQL. URL decoding does not make an apostrophe safe for a SQL string literal.

### src/PriceLookup.fs

```fsharp
module PriceLookup
open System
open Microsoft.Data.SqlClient
let price (connection: SqlConnection) (sku: string) =
    if sku.Length > 64 then invalidArg "sku" "too long"
    use command = connection.CreateCommand()
    command.CommandText <- "SELECT UnitPrice FROM Prices WHERE Sku='" + sku + "'"
    let value = command.ExecuteScalar()
    if isNull value || value = box DBNull.Value then
        None
    else
        Some (Convert.ToDecimal(value))
```

### src/PriceRoute.fs

```fsharp
module PriceRoute
open System
open Microsoft.Data.SqlClient
let handle (connection: SqlConnection) (encodedSegment: string) =
    let sku = Uri.UnescapeDataString encodedSegment
    PriceLookup.price connection sku
```

### Derivation

```json
{
  "group": "fsharp-route-decode-sku-query",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "A source-visible route decoding step feeds an option-returning lookup, with exact encoding and absence behavior as remediation constraints. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "sql-injection",
    "cwe": "CWE-89",
    "path": "src/PriceLookup.fs",
    "line_start": 7,
    "line_end": 7
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "SQL injection through a visible decoding handoff.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return the price of the exact decoded SKU or None if absent.",
  "trust_boundary": "A public route segment is decoded by the included adapter; it remains untrusted when passed into database lookup.",
  "legitimate_examples": [
    {
      "input": "Encoded SKU O%27RING",
      "expected": "Look up the literal SKU O'RING."
    },
    {
      "input": "Unknown decoded SKU",
      "expected": "Return None without selecting another product."
    }
  ],
  "permitted_changes": [
    "Bind the decoded SKU as an NVARCHAR parameter and preserve absent-result handling.",
    "Keep exactly one URL-decoding pass at the route boundary."
  ],
  "forbidden_changes": [
    "Do not delete the demonstrated operation or replace its output with a constant.",
    "Do not change the documented ownership, return convention or accepted legitimate inputs without updating every included caller."
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
    "https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/functions/",
    "https://learn.microsoft.com/en-us/dotnet/api/system.xml.xmlreadersettings"
  ]
}
```

### Regression traps

```json
[
  "Escaping before URL decoding fails to constrain the final SQL value.",
  "Double decoding changes legitimate percent-containing SKUs."
]
```

### Remediation constraints

```json
[
  "Bind the decoded SKU as an NVARCHAR parameter and preserve absent-result handling.",
  "Keep exactly one URL-decoding pass at the route boundary."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-fsharp-vulnerable-01",
  "prior_case_id": "fsharp-invoice-command-vulnerable",
  "prior_source_sha256": "66f6bab5c8dc4411bff6928508dbe8c49ad87be2785906a6b9adf7cb3a36ea1c",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; F# 8",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Linux x86-64",
  "setup": "Functions receive non-null values; configuration, executable paths and injected database connections are trusted. Microsoft.Data.SqlClient 5.2.2; SQL Server 2022; Sku is unique NVARCHAR(64), UnitPrice DECIMAL(12,2); compile PriceLookup.fs before PriceRoute.fs."
}
```

### Split

```json
"held_out"
```

## v2-fsharp-vulnerable-02 — A queued media job turns a human track title into shell code

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `620b0a23c77b7d0647246b0222808663bc2c55f4b8093a60a4084b467b4f53dd`. Protocol-2.0 case hash: `9c0c1992221023d37db8ea08f8e11f2b02ad681e21cc883c0bd8f72d62294258`.

Apostrophes in the title terminate shell quoting. The fixed executable and paths do not prevent the metadata value from changing the shell program.

### src/TrackMetadata.fs

```fsharp
module TrackMetadata
open System
open System.Diagnostics
let writeTitle (title: string) =
    if title.Length > 100 then invalidArg "title" "too long"
    let start = ProcessStartInfo("/bin/sh")
    start.UseShellExecute <- false
    start.ArgumentList.Add "-c"
    start.ArgumentList.Add ("/usr/bin/ffmpeg -y -i /srv/jobs/input.wav -metadata title='" + title + "' /srv/jobs/output.wav")
    use child = Process.Start start
    if isNull child then failwith "spawn failed"
    child.WaitForExit()
    if child.ExitCode <> 0 then failwith "metadata write failed"
```

### Derivation

```json
{
  "group": "fsharp-audio-metadata-shell-quote",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "The input is metadata, not a filename or command selector; a correct repair must preserve literal media metadata through a trusted tool. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "shell-injection",
    "cwe": "CWE-78",
    "path": "src/TrackMetadata.fs",
    "line_start": 9,
    "line_end": 9
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Shell injection in an explicit media metadata operation; decoder internals are outside this source case.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Write a literal track title into a service-owned audio conversion output.",
  "trust_boundary": "A user supplies a title; input/output paths and the transcode operation are fixed by the queue worker.",
  "legitimate_examples": [
    {
      "input": "Title Bird's Song",
      "expected": "Store the apostrophe literally in title metadata."
    },
    {
      "input": "Title containing $ and semicolon",
      "expected": "Treat all characters as metadata, without launching additional commands."
    }
  ],
  "permitted_changes": [
    "Start ffmpeg directly with one metadata argument and fixed input/output paths.",
    "Preserve audio processing, metadata content and nonzero-exit failure handling."
  ],
  "forbidden_changes": [
    "Do not delete the demonstrated operation or replace its output with a constant.",
    "Do not change the documented ownership, return convention or accepted legitimate inputs without updating every included caller."
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
    "https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/functions/",
    "https://learn.microsoft.com/en-us/dotnet/api/system.xml.xmlreadersettings"
  ]
}
```

### Regression traps

```json
[
  "Single quotes are not safe when the value itself contains apostrophes.",
  "Dropping title metadata removes the intended operation."
]
```

### Remediation constraints

```json
[
  "Start ffmpeg directly with one metadata argument and fixed input/output paths.",
  "Preserve audio processing, metadata content and nonzero-exit failure handling."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-fsharp-vulnerable-02",
  "prior_case_id": "fsharp-support-process-vulnerable",
  "prior_source_sha256": "d85010770055de91caab1c26818a9d838c8466edccac53d4ce6e4f7538f74c6e",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; F# 8",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Linux x86-64",
  "setup": "Functions receive non-null values; configuration, executable paths and injected database connections are trusted. FFmpeg 6.1 is installed at /usr/bin/ffmpeg; a caller owns stable input/output files, bounds stderr and imposes a deadline; title contains no NUL."
}
```

### Split

```json
"held_out"
```

## v2-fsharp-vulnerable-03 — A content-addressed legal archive relies on SHA-1 as collision resistance

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `0052aafdb28e88aa47ced25abb648cfcfab0dcdfe8fc047416eeaf3774d9a130`. Protocol-2.0 case hash: `3b5422ff144a1b5ef709773b2b2ce237c4fdb71415dab00b0b38f1ec8c54f8c4`.

The archive treats a SHA-1 collision as document identity and skips storage when an existing digest matches. Collision resistance is a security property here, not merely an incidental checksum.

### src/ArchiveIdentity.fs

```fsharp
module ArchiveIdentity
open System
open System.Security.Cryptography
open System.Collections.Generic
let remember (index: IDictionary<string, byte[]>) (document: byte[]) =
    if document.Length > 1048576 then invalidArg "document" "too large"
    use digest = SHA1.Create()
    let identity = Convert.ToHexString(digest.ComputeHash document)
    if index.ContainsKey identity then
        identity
    else
        index.Add(identity, Array.copy document)
        identity
```

### Derivation

```json
{
  "group": "fsharp-legal-content-address-collision",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "The digest controls de-duplication of chosen content, providing a concrete collision consequence and persisted-key migration requirement. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "weak-cryptography",
    "cwe": "CWE-328",
    "path": "src/ArchiveIdentity.fs",
    "line_start": 7,
    "line_end": 7
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Weak digest in an explicitly collision-sensitive deduplication decision.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Assign stable content identities while ensuring distinct legal documents are not silently treated as the same object.",
  "trust_boundary": "An uploader may choose document bytes and request repeated insertions; the archive index is service-owned.",
  "legitimate_examples": [
    {
      "input": "Upload exactly the same document twice",
      "expected": "Return the same versioned identity without duplicating content."
    },
    {
      "input": "Upload distinct documents",
      "expected": "Do not silently alias them solely because a legacy digest matches."
    }
  ],
  "permitted_changes": [
    "Use a collision-resistant versioned digest and compare stored bytes before treating a hit as identical.",
    "Document index migration; retain existing document accessibility."
  ],
  "forbidden_changes": [
    "Do not delete the demonstrated operation or replace its output with a constant.",
    "Do not change the documented ownership, return convention or accepted legitimate inputs without updating every included caller."
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
    "https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/functions/",
    "https://learn.microsoft.com/en-us/dotnet/api/system.xml.xmlreadersettings"
  ]
}
```

### Regression traps

```json
[
  "Changing the digest length without migrating persisted keys loses existing records.",
  "An unkeyed hash is suitable for content identity here, but must not be repurposed as sender authentication."
]
```

### Remediation constraints

```json
[
  "Use a collision-resistant versioned digest and compare stored bytes before treating a hit as identical.",
  "Document index migration; retain existing document accessibility."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-fsharp-vulnerable-03",
  "prior_case_id": "fsharp-http-callback-vulnerable",
  "prior_source_sha256": "ab955dff29fd4cfcb1b7d57669fd3c4173f78433135bf28ad2d21d0b6509eb47",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; F# 8",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Linux x86-64",
  "setup": "Functions receive non-null values; configuration, executable paths and injected database connections are trusted. .NET 8; the IDictionary is accessed under a caller lock; documents are private immutable byte arrays after copying; archive identities are persisted externally."
}
```

### Split

```json
"held_out"
```

## v2-fsharp-vulnerable-04 — External XML entities enter an import record through aliased reader settings

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `c7fe71a798db489b4cf17d74e011380eb3cf8c59a0b923b9499f9b717aefcc92`. Protocol-2.0 case hash: `6c130812f3b9999acf5f279e64e89853dda5aafb19b2ac0a3e6d37c021766421`.

The alias and original refer to the same mutable settings object. Enabling the resolver through parserPolicy affects the reader created with settings and permits external entity content in the returned title.

### src/FeedRecord.fs

```fsharp
module FeedRecord
open System
open System.IO
open System.Xml
open System.Xml.Linq
let read (xml: string) =
    if xml.Length > 16384 then invalidArg "xml" "too large"
    let settings = XmlReaderSettings()
    let parserPolicy = settings
    parserPolicy.DtdProcessing <- DtdProcessing.Parse
    parserPolicy.XmlResolver <- XmlUrlResolver()
    parserPolicy.MaxCharactersFromEntities <- 1024L
    use input = new StringReader(xml)
    use reader = XmlReader.Create(input, settings)
    let document = XDocument.Load reader
    let title = document.Root.Element(XName.Get "title")
    if isNull title then failwith "title missing"
    title.Value
```

### Derivation

```json
{
  "group": "fsharp-xml-settings-object-alias",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "The case requires object alias reasoning inside one lexical scope and a concrete reader consumption path rather than a detached configuration assignment. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "unsafe-xml",
    "cwe": "CWE-611",
    "path": "src/FeedRecord.fs",
    "line_start": 11,
    "line_end": 11
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "XML resolver alias tracking and live-reader policy.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Extract the title of a bounded partner feed record.",
  "trust_boundary": "A partner controls the XML; the service does not grant access to local files or internal network resources.",
  "legitimate_examples": [
    {
      "input": "<record><title>Morning &amp; Evening</title></record>",
      "expected": "Return Morning & Evening."
    },
    {
      "input": "An external entity used inside title",
      "expected": "Reject without resolving it."
    }
  ],
  "permitted_changes": [
    "Disable external resolution and prohibit DTDs on the actual settings object.",
    "Keep ordinary XML entity decoding and the required title check."
  ],
  "forbidden_changes": [
    "Do not delete the demonstrated operation or replace its output with a constant.",
    "Do not change the documented ownership, return convention or accepted legitimate inputs without updating every included caller."
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
    "https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/functions/",
    "https://learn.microsoft.com/en-us/dotnet/api/system.xml.xmlreadersettings"
  ]
}
```

### Regression traps

```json
[
  "Treating aliases as unrelated objects misses the effective parser policy.",
  "Mutating a new unused settings object does not protect this reader."
]
```

### Remediation constraints

```json
[
  "Disable external resolution and prohibit DTDs on the actual settings object.",
  "Keep ordinary XML entity decoding and the required title check."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-fsharp-vulnerable-04",
  "prior_case_id": "fsharp-binary-state-vulnerable",
  "prior_source_sha256": "930b5a6fd5ad0a46fee1367b2e225edfdf6b471c4d1cd76923a5bc235680fd43",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; F# 8",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Linux x86-64",
  "setup": "Functions receive non-null values; configuration, executable paths and injected database connections are trusted. Feed ingress requires a record root and rejects missing root; no DTD is part of the protocol. Document input and entity expansion are bounded."
}
```

### Split

```json
"held_out"
```

## v2-fsharp-vulnerable-05 — Batch billing selection joins client IDs into an unquoted IN list

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `140aa38acd1175c9ef6b1cf61c488878e9ed832f7e022c06fcaef4a4a3933920`. Protocol-2.0 case hash: `58b6586e1ff813034c2abc6ab385a9adb4c4b13bfb177a6351e0427c05d360bb`.

A size-limited list still contains unvalidated SQL fragments. Joining textual IDs into an unquoted IN clause permits expression and statement syntax rather than integer values.

### src/BillingBatch.fs

```fsharp
module BillingBatch
open System
open Microsoft.Data.SqlClient
let total (connection: SqlConnection) (invoiceIds: string list) =
    if List.isEmpty invoiceIds || List.length invoiceIds > 20 then invalidArg "invoiceIds" "count"
    if invoiceIds |> List.exists (fun id -> id.Length > 40) then invalidArg "invoiceIds" "length"
    let selected = String.concat "," invoiceIds
    use command = connection.CreateCommand()
    command.CommandText <- "SELECT SUM(Amount) FROM Invoices WHERE InvoiceId IN (" + selected + ")"
    let result = command.ExecuteScalar()
    if isNull result || result = box DBNull.Value then 0M
    else Convert.ToDecimal result
```

### Derivation

```json
{
  "group": "fsharp-invoice-collection-sql-list",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "A collection-to-query conversion introduces cardinality, duplicate and type-conversion requirements absent from a scalar lookup. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "sql-injection",
    "cwe": "CWE-89",
    "path": "src/BillingBatch.fs",
    "line_start": 9,
    "line_end": 9
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "SQL syntax construction from a collection, with duplicate and absent-value semantics.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Sum the amounts of a bounded nonempty set of authorized integer invoice IDs.",
  "trust_boundary": "The API receives IDs as JSON strings; authorization establishes account access but does not validate the numeric grammar.",
  "legitimate_examples": [
    {
      "input": "IDs [\"12\",\"31\"]",
      "expected": "Sum invoices 12 and 31 once according to IN semantics."
    },
    {
      "input": "ID containing SQL punctuation",
      "expected": "Reject as a noninteger or bind a validated integer; never execute it as syntax."
    }
  ],
  "permitted_changes": [
    "Parse each ID into the documented integer range and bind each value or a table-valued parameter.",
    "Retain empty-list rejection, duplicate-as-set semantics and null-sum behavior."
  ],
  "forbidden_changes": [
    "Do not delete the demonstrated operation or replace its output with a constant.",
    "Do not change the documented ownership, return convention or accepted legitimate inputs without updating every included caller."
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
    "https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/functions/",
    "https://learn.microsoft.com/en-us/dotnet/api/system.xml.xmlreadersettings"
  ]
}
```

### Regression traps

```json
[
  "Quoting joined IDs instead of parameterizing preserves a second injection boundary.",
  "Changing IN to a join that counts duplicate IDs alters totals."
]
```

### Remediation constraints

```json
[
  "Parse each ID into the documented integer range and bind each value or a table-valued parameter.",
  "Retain empty-list rejection, duplicate-as-set semantics and null-sum behavior."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-fsharp-vulnerable-05",
  "prior_case_id": "fsharp-digest-scope-vulnerable",
  "prior_source_sha256": "b105bd3726d34a36238ba02d38423da8b49c1dfbc81cac1d1884d2442c5751b3",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; F# 8",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Linux x86-64",
  "setup": "Functions receive non-null values; configuration, executable paths and injected database connections are trusted. SQL Server 2022; Microsoft.Data.SqlClient 5.2.2; authorized connection is scoped to one account view; InvoiceId is INT and Amount DECIMAL."
}
```

### Split

```json
"held_out"
```

## v2-fsharp-vulnerable-06 — A literal log search term is interpolated into a shell pipeline

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `528ea82dcab725aafd8d22fd0dcb81772b0ac6fc5850a59f477c87e23665fa8b`. Protocol-2.0 case hash: `8dab3a5fee275b4c069e7ff6af3c24f0bf082fe1cdcbd2ad927babe2315a6a53`.

grep -F makes its pattern literal only after shell parsing. Dollar substitutions and quote characters in the term are still interpreted by sh before grep sees them.

### src/JobLogSearch.fs

```fsharp
module JobLogSearch
open System
open System.Diagnostics
let search (term: string) =
    if term.Length = 0 || term.Length > 60 then invalidArg "term" "length"
    let start = ProcessStartInfo("/bin/sh")
    start.UseShellExecute <- false
    start.RedirectStandardOutput <- true
    start.ArgumentList.Add "-c"
    start.ArgumentList.Add ("/usr/bin/grep -F -- \"" + term + "\" /srv/jobs/current.log | /usr/bin/head -n 20")
    use child = Process.Start start
    if isNull child then failwith "spawn"
    let output = child.StandardOutput.ReadToEnd()
    child.WaitForExit()
    if child.ExitCode <> 0 then failwith "search"
    output
```

### Derivation

```json
{
  "group": "fsharp-log-search-literal-pipeline",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "This case separates literal matcher flags from shell expansion and makes empty search results an explicit regression trap. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "shell-injection",
    "cwe": "CWE-78",
    "path": "src/JobLogSearch.fs",
    "line_start": 10,
    "line_end": 10
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Shell injection with downstream literal matching and pipeline exit semantics.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return at most the first twenty log lines containing a literal user search term.",
  "trust_boundary": "A support user may search a preauthorized fixed log but may not run worker commands or select paths.",
  "legitimate_examples": [
    {
      "input": "Term costs $5",
      "expected": "Match that literal text."
    },
    {
      "input": "No matching lines",
      "expected": "Return an empty string as a successful search."
    }
  ],
  "permitted_changes": [
    "Use a bounded direct line-reading literal search, or separate child arguments without a shell pipeline.",
    "Preserve first-twenty ordering, empty-result success and the caller output limit."
  ],
  "forbidden_changes": [
    "Do not delete the demonstrated operation or replace its output with a constant.",
    "Do not change the documented ownership, return convention or accepted legitimate inputs without updating every included caller."
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
    "https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/functions/",
    "https://learn.microsoft.com/en-us/dotnet/api/system.xml.xmlreadersettings"
  ]
}
```

### Regression traps

```json
[
  "Removing -F changes a literal search into a regular-expression language.",
  "A grep exit code of 1 means no matches, not an operational failure."
]
```

### Remediation constraints

```json
[
  "Use a bounded direct line-reading literal search, or separate child arguments without a shell pipeline.",
  "Preserve first-twenty ordering, empty-result success and the caller output limit."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-fsharp-vulnerable-06",
  "prior_case_id": "fsharp-xml-configuration-vulnerable",
  "prior_source_sha256": "68087dc60c14e04663ce03fc3767bd565296676abcbc68940760a9f388513e3d",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; F# 8",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Linux x86-64",
  "setup": "Functions receive non-null values; configuration, executable paths and injected database connections are trusted. GNU grep/coreutils 9.4; the fixed log is at most 2 MiB, uses UTF-8 lines of at most 4096 bytes and is a stable snapshot during search."
}
```

### Split

```json
"held_out"
```

