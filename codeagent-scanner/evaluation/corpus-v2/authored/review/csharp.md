# csharp — authored corpus-v2 candidates

AI-authored, pending independent human review. Static validation is separate evidence, not approval. Source is quoted for inspection and must not be executed.

Review the corpus-level context and checklist in the [complete unsigned manifest](../unsigned-review-manifest.json) alongside each case.

## v2-csharp-safe-01 — Password-change reauthentication derives a salted work-factor verifier

Proposed label: **safe**. Human review: **pending**.

Source hash: `33d6cc1675ed16b9002451c9193edafe95c570965839cbdd43549669f0d78690`. Protocol-2.0 case hash: `ff24bb8722f01fa084573821c9581852d27233b020d62c88e20f4e171b7f322d`.

A password is checked against a server-stored, per-account salted PBKDF2-HMAC-SHA256 verifier with a fixed work factor; the comparison is fixed-time and the temporary derived bytes are cleared. The candidate does not control salt, digest or iteration count.

### src/PasswordProof.cs

```csharp
using System;
using System.Security.Cryptography;
public sealed record StoredPassword(byte[] Salt, byte[] Digest);
public static class PasswordProof {
    public static bool Verify(StoredPassword stored, string candidate) {
        if (stored.Salt.Length != 16 || stored.Digest.Length != 32) throw new ArgumentException("stored verifier");
        if (candidate.Length < 1 || candidate.Length > 256) return false;
        byte[] derived = Rfc2898DeriveBytes.Pbkdf2(candidate, stored.Salt, 600000, HashAlgorithmName.SHA256, 32);
        try {
            return CryptographicOperations.FixedTimeEquals(derived, stored.Digest);
        } finally {
            CryptographicOperations.ZeroMemory(derived);
        }
    }
}
```

### src/PasswordChangeGate.cs

```csharp
using System;
public static class PasswordChangeGate {
    public static bool ConfirmCurrentPassword(StoredPassword authenticatedAccount, string formValue) {
        ArgumentNullException.ThrowIfNull(authenticatedAccount);
        ArgumentNullException.ThrowIfNull(formValue);
        return PasswordProof.Verify(authenticatedAccount, formValue);
    }
}
```

### Derivation

```json
{
  "group": "csharp-password-change-pbkdf2-verifier",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "This operation tests password work-factor derivation, stored salt ownership and exact password semantics rather than authentication of a network message with a reusable HMAC key. Conceptual independence remains subject to human review.",
  "retired_drafts": [
    {
      "reason": "Replaced before scanner exposure after cross-language audit identified a substantially shared operation/mechanism.",
      "overlap_case_ids": [
        "v2-kotlin-safe-02"
      ],
      "retired_before_scanner_exposure": true,
      "case_snapshot": {
        "id": "v2-csharp-safe-01",
        "language": "csharp",
        "vulnerable": false,
        "scenario": "Webhook authentication compares an HMAC over the exact request bytes",
        "files": {
          "src/WebhookSignature.cs": "using System;\nusing System.Security.Cryptography;\npublic static class WebhookSignature {\n    public static bool Verify(byte[] rawBody, byte[] signature, byte[] key) {\n        if (rawBody.Length > 1048576 || key.Length < 32 || signature.Length != 32) return false;\n        using var mac = new HMACSHA256(key);\n        byte[] expected = mac.ComputeHash(rawBody);\n        bool valid = CryptographicOperations.FixedTimeEquals(expected, signature);\n        CryptographicOperations.ZeroMemory(expected);\n        return valid;\n    }\n}\n"
        },
        "expected_findings": [],
        "rationale": "A secret HMAC authenticates exact request bytes, validates signature size and uses a fixed-time comparison. This is not an unkeyed digest mislabeled as authentication.",
        "remediation_constraints": [
          "Keep raw-byte authentication, secret key handling and fixed-time equality.",
          "Preserve the explicit body and signature limits."
        ],
        "runtime_assumptions": {
          "runtime": ".NET 8.0; C# 12",
          "libraries": [
            ".NET 8 BCL"
          ],
          "platform": "Linux x86-64 unless a case explicitly says Windows",
          "setup": "Methods are invoked by the described authenticated service ingress; service configuration and injected connections are trusted. Key is generated with at least 256 bits of entropy and isolated from request data; replay prevention is enforced by the authenticated event ID in the caller."
        },
        "operation_contract": {
          "purpose": "Authenticate a bounded webhook body without parsing or normalizing it first.",
          "trust_boundary": "A sender controls body and supplied signature; the service key is independently configured and secret.",
          "legitimate_examples": [
            {
              "input": "Correct HMAC-SHA256 for the exact body",
              "expected": "Return true."
            },
            {
              "input": "Same JSON meaning with different whitespace and old signature",
              "expected": "Return false because the authenticated bytes differ."
            }
          ],
          "permitted_changes": [
            "Keep raw-byte authentication, secret key handling and fixed-time equality.",
            "Preserve the explicit body and signature limits."
          ],
          "forbidden_changes": [
            "Do not delete the demonstrated operation or replace its output with a constant.",
            "Do not change the documented ownership, return convention or accepted legitimate inputs without updating every included caller."
          ]
        },
        "regression_traps": [
          "Replacing HMAC with SHA256(body) removes authenticity.",
          "Parsing and reserializing before verification changes the signed message."
        ],
        "ground_truth_scope": {
          "profile": "security-v2",
          "scope": "Cryptographic primitive and comparison safety; replay handling is explicitly a caller responsibility.",
          "reviewed_residual_risks": [
            "AI-authored candidate: labels, scope and independence require human review before freezing.",
            "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
          ]
        },
        "derivation": {
          "group": "csharp-webhook-keyed-authentication",
          "origin": "new AI-authored candidate",
          "related_case_ids": [],
          "independence_rationale": "This safe control specifies a keyed authenticity requirement and exact-byte semantics rather than merely choosing a stronger hash. Independence is a proposed classification pending human review; no effective sample size is claimed."
        },
        "provenance": {
          "origin": "original AI-authored evaluation candidate",
          "author": "Codex AI author",
          "generated": true,
          "license": "CC0-1.0",
          "references": [
            "https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo.argumentlist",
            "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca3075"
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
      "source_sha256": "333bed21f057d595f7c48cc17b390e36c428a2459d744fe5dae2b8c94e8c754c"
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
  "scope": "Password-specific key derivation and comparison; account sessions, enrollment storage access and request rate limits are explicit caller preconditions.",
  "reviewed_residual_risks": [
    "AI candidate: human review of labels, runtime assumptions and cross-corpus independence remains pending.",
    "Caller responsibilities are explicit assumptions, not a claim of whole-application security."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Reauthenticate the current account before allowing a password-change flow to proceed.",
  "trust_boundary": "An authenticated user submits the current password; the included caller receives that account’s credential record from trusted server storage, never from request fields.",
  "legitimate_examples": [
    {
      "input": "The exact password used when enrolling this salted record",
      "expected": "Return true."
    },
    {
      "input": "A different password or an empty string",
      "expected": "Return false without changing the stored credential record."
    }
  ],
  "permitted_changes": [
    "Keep a per-account random 16-byte salt, 600000 PBKDF2-HMAC-SHA256 iterations, a 32-byte verifier and fixed-time comparison.",
    "Preserve exact UTF-8 password semantics without trimming, normalization or truncation.",
    "Clear the temporary derived verifier and retain the 256-character ingress bound."
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
    "https://learn.microsoft.com/en-us/dotnet/api/system.security.cryptography.rfc2898derivebytes.pbkdf2",
    "https://learn.microsoft.com/en-us/dotnet/api/system.security.cryptography.cryptographicoperations.fixedtimeequals"
  ]
}
```

### Regression traps

```json
[
  "Replacing PBKDF2 with one fast SHA-256 hash removes the password work factor.",
  "Taking the stored salt/digest or iteration count from the submitted form would bypass server-owned verification.",
  "Do not erase or mutate the persisted verifier while clearing temporary bytes."
]
```

### Remediation constraints

```json
[
  "Keep a per-account random 16-byte salt, 600000 PBKDF2-HMAC-SHA256 iterations, a 32-byte verifier and fixed-time comparison.",
  "Preserve exact UTF-8 password semantics without trimming, normalization or truncation.",
  "Clear the temporary derived verifier and retain the 256-character ingress bound."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-csharp-safe-01",
  "prior_case_id": "csharp-account-command-safe",
  "prior_source_sha256": "3c792be4cf2a6595f70c20aab3f7865960f17ebef5542e7003ad118f2913671e",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; C# 12",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Linux x86-64 unless a case explicitly says Windows",
  "setup": ".NET 8; C#12. Enrollment uses the identical PBKDF2 parameters and a fresh cryptographic 16-byte salt per account. The caller is an already authenticated password-change flow and loads only that account’s record from immutable server storage. Requests are rate-limited before this CPU-expensive check; all strings and byte arrays are non-null."
}
```

### Split

```json
"held_out"
```

## v2-csharp-safe-02 — A stored procedure receives a postcode as a typed input parameter

Proposed label: **safe**. Human review: **pending**.

Source hash: `1e7bb940255a975afa7a16ad0df53c53d6f54633440329b318ba927d81b72c04`. Protocol-2.0 case hash: `283a954c8bb982b122cd53a7ecc42f37d59ad334675f01e4a4e8efa0f0c9fce1`.

The client selects a fixed stored procedure and binds the full postcode as data. The included procedure performs a static equality query and contains no dynamic EXEC.

### src/DeliveryZones.cs

```csharp
using System;
using System.Data;
using Microsoft.Data.SqlClient;
public static class DeliveryZones {
    public static int Lookup(SqlConnection connection, string postcode) {
        if (postcode.Length > 16) throw new ArgumentException("postcode");
        using var command = new SqlCommand("dbo.LookupDeliveryZone", connection);
        command.CommandType = CommandType.StoredProcedure;
        command.Parameters.Add("@postcode", SqlDbType.NVarChar, 16).Value = postcode;
        object value = command.ExecuteScalar();
        return value == null || value == DBNull.Value ? -1 : Convert.ToInt32(value);
    }
}
```

### db/LookupDeliveryZone.sql

```csharp
CREATE PROCEDURE dbo.LookupDeliveryZone @postcode NVARCHAR(16)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT ZoneId FROM dbo.DeliveryZones WHERE Postcode = @postcode;
END;
```

### Derivation

```json
{
  "group": "csharp-fixed-delivery-procedure",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "A safe procedure call includes the downstream SQL body to make the trust boundary reviewable rather than assuming parameterization across unknown server code. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "SQL execution, including the included static stored procedure; no source-only assumption about hidden dynamic SQL.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return the zone for an exact postcode or -1 when absent.",
  "trust_boundary": "An end user controls postcode; procedure identity and database schema are trusted.",
  "legitimate_examples": [
    {
      "input": "Postcode O'NEIL",
      "expected": "Treat the apostrophe literally and return the stored mapping if present."
    },
    {
      "input": "Unknown postcode",
      "expected": "Return -1."
    }
  ],
  "permitted_changes": [
    "Preserve the fixed procedure and typed binding.",
    "Keep the no-result convention and static procedure body."
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
    "https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo.argumentlist",
    "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca3075"
  ]
}
```

### Regression traps

```json
[
  "A parameterized call would not by itself prove a dynamic SQL procedure safe; the body is included here.",
  "Do not truncate postcodes silently."
]
```

### Remediation constraints

```json
[
  "Preserve the fixed procedure and typed binding.",
  "Keep the no-result convention and static procedure body."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-csharp-safe-02",
  "prior_case_id": "csharp-shell-command-safe",
  "prior_source_sha256": "c1d8ec5474a5bd1c9c49bd29fd279da97bceb871c95e683deba70df2fa52b77f",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; C# 12",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Linux x86-64 unless a case explicitly says Windows",
  "setup": "Methods are invoked by the described authenticated service ingress; service configuration and injected connections are trusted. Microsoft.Data.SqlClient 5.2.2; SQL Server 2022; open connection; Postcode is unique NVARCHAR(16)."
}
```

### Split

```json
"held_out"
```

## v2-csharp-safe-03 — Model service health request keeps platform certificate verification

Proposed label: **safe**. Human review: **pending**.

Source hash: `170749b73b1e4bf249b12b67e135eb299c36950c987a39be30363b1dd044eb56`. Protocol-2.0 case hash: `0595d16171391d8a06beaed671799e95b4510bc3d790ed637c5fb24263d76fef`.

The request uses default platform chain and hostname verification, a fixed HTTPS origin, no redirects and no response body consumption.

### src/ModelHealth.cs

```csharp
using System;
using System.Net.Http;
using System.Threading.Tasks;
public static class ModelHealth {
    public static async Task<bool> ReadyAsync() {
        using var handler = new HttpClientHandler { AllowAutoRedirect = false };
        using var client = new HttpClient(handler) { Timeout = TimeSpan.FromSeconds(3) };
        using var request = new HttpRequestMessage(HttpMethod.Head, "https://models.example.org/health");
        using var response = await client.SendAsync(request, HttpCompletionOption.ResponseHeadersRead);
        return response.IsSuccessStatusCode;
    }
}
```

### Derivation

```json
{
  "group": "csharp-model-head-health",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "A headers-only health check has a distinct output and transport contract from downloading update metadata. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "TLS authentication and fixed-destination request policy.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Check whether the configured model service returns a successful health status.",
  "trust_boundary": "The network is untrusted; users cannot change the destination or request headers.",
  "legitimate_examples": [
    {
      "input": "Valid certificate and HTTP 204",
      "expected": "Return true."
    },
    {
      "input": "Wrong-host certificate",
      "expected": "Raise a transport error rather than returning readiness."
    }
  ],
  "permitted_changes": [
    "Retain default TLS verification and redirect refusal.",
    "Preserve the short deadline and HEAD semantics."
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
    "https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo.argumentlist",
    "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca3075"
  ]
}
```

### Regression traps

```json
[
  "A readiness check still needs authenticated transport.",
  "Swallowing all transport errors as a successful health response changes the meaning."
]
```

### Remediation constraints

```json
[
  "Retain default TLS verification and redirect refusal.",
  "Preserve the short deadline and HEAD semantics."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-csharp-safe-03",
  "prior_case_id": "csharp-tls-handler-safe",
  "prior_source_sha256": "06c00d5a72f45920ba59989a97e664a0743f69d11605309a6ad8ed8d1799eb16",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; C# 12",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Linux x86-64 unless a case explicitly says Windows",
  "setup": "Methods are invoked by the described authenticated service ingress; service configuration and injected connections are trusted. Linux OS trust store is maintained; the destination is a fixed operator-managed host."
}
```

### Split

```json
"held_out"
```

## v2-csharp-safe-04 — Tenant preferences use a sealed JSON DTO with bounded fields

Proposed label: **safe**. Human review: **pending**.

Source hash: `5cba468c290b4badc69605f4f7998ae5c4e3e99cb02002ab2e986d417f86cdb9`. Protocol-2.0 case hash: `00917dc6e9e2edea8dae78df65a6ffdb3decf445f5b8bc5b4f668e9ad44e4203`.

The JSON deserializer targets one sealed data record with no polymorphic resolver or arbitrary runtime type metadata, and validates both accepted fields.

### src/Preferences.cs

```csharp
using System;
using System.Text.Json;
public sealed record Preferences(string Theme, int PageSize);
public static class PreferenceImport {
    public static Preferences Read(string json) {
        if (json.Length > 4096) throw new ArgumentException("json");
        var options = new JsonSerializerOptions { MaxDepth = 8, PropertyNameCaseInsensitive = false };
        var value = JsonSerializer.Deserialize<Preferences>(json, options) ?? throw new FormatException("preferences");
        if (value.Theme != "light" && value.Theme != "dark") throw new FormatException("theme");
        if (value.PageSize < 10 || value.PageSize > 100) throw new FormatException("page size");
        return value;
    }
}
```

### Derivation

```json
{
  "group": "csharp-sealed-preferences-json",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "This safe data import has explicit primitive fields and validation and is not a byte-for-byte safe twin of an object-graph import. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "Deserialization and bounded settings validation.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Import a theme and page-size preference from a small JSON document.",
  "trust_boundary": "The tenant controls JSON bytes but may select only documented preference values.",
  "legitimate_examples": [
    {
      "input": "{\"Theme\":\"dark\",\"PageSize\":25}",
      "expected": "Return those exact values."
    },
    {
      "input": "{\"Theme\":\"dark\",\"PageSize\":100000}",
      "expected": "Reject the page size."
    }
  ],
  "permitted_changes": [
    "Keep explicit DTO selection, depth bound and field validation.",
    "Do not enable arbitrary type-name resolution to support extra metadata."
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
    "https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo.argumentlist",
    "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca3075"
  ]
}
```

### Regression traps

```json
[
  "The mere word Deserialize does not make data-only JSON parsing equivalent to BinaryFormatter.",
  "Removing validation while changing serializers broadens allowed settings."
]
```

### Remediation constraints

```json
[
  "Keep explicit DTO selection, depth bound and field validation.",
  "Do not enable arbitrary type-name resolution to support extra metadata."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-csharp-safe-04",
  "prior_case_id": "csharp-state-formatter-safe",
  "prior_source_sha256": "331fb6b9f1961f2bccd5cbd6575743d5dd7136905fd6591c9483641e17da36f4",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; C# 12",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Linux x86-64 unless a case explicitly says Windows",
  "setup": "Methods are invoked by the described authenticated service ingress; service configuration and injected connections are trusted. System.Text.Json shipped with .NET 8; no custom converters or polymorphic configuration are registered. Unknown JSON members are intentionally ignored."
}
```

### Split

```json
"held_out"
```

## v2-csharp-safe-05 — Support diagnostics launch a fixed binary without accepting executable text

Proposed label: **safe**. Human review: **pending**.

Source hash: `6baf0c544566793f606b1455d321b4981da96f7423fcb2734eed80a9f11770e9`. Protocol-2.0 case hash: `9e756a7b6bb6540ec737931230688a11a7fe52eef4b9f74a8f2b9c79cc870f7e`.

The executable and sole argument are fixed application code, and no shell or user string reaches process construction.

### src/RuntimeReport.cs

```csharp
using System;
using System.Diagnostics;
public static class RuntimeReport {
    public static string Read() {
        var start = new ProcessStartInfo("/usr/bin/dotnet") { UseShellExecute = false, RedirectStandardOutput = true };
        start.ArgumentList.Add("--info");
        using var process = Process.Start(start) ?? throw new InvalidOperationException("spawn");
        string result = process.StandardOutput.ReadToEnd();
        process.WaitForExit();
        if (process.ExitCode != 0) throw new InvalidOperationException("runtime report");
        return result;
    }
}
```

### Derivation

```json
{
  "group": "csharp-fixed-runtime-inventory",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "This process operation has no attacker-controlled command components and an explicit operator-only observation contract. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "Process-injection false-positive control for a zero-input diagnostic command.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return the installed runtime diagnostic report to an authenticated operator.",
  "trust_boundary": "Users may request the report but cannot choose its command, arguments, environment or executable location.",
  "legitimate_examples": [
    {
      "input": "Authorized report request",
      "expected": "Return the trusted dotnet --info output."
    },
    {
      "input": "Tool exits unsuccessfully",
      "expected": "Throw rather than returning success."
    }
  ],
  "permitted_changes": [
    "Keep the fixed executable/argument pair and capture/reap behavior.",
    "Restrict report access to operators."
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
    "https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo.argumentlist",
    "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca3075"
  ]
}
```

### Regression traps

```json
[
  "A process API alone is not command injection.",
  "Adding a user-provided suffix to a shell command would change the trust model."
]
```

### Remediation constraints

```json
[
  "Keep the fixed executable/argument pair and capture/reap behavior.",
  "Restrict report access to operators."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-csharp-safe-05",
  "prior_case_id": "csharp-integrity-alias-safe",
  "prior_source_sha256": "7733ce10e1c098ca7f69f5d33bf5dee2389a1513cb681382465ae6e8322ceac9",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; C# 12",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Linux x86-64 unless a case explicitly says Windows",
  "setup": "Methods are invoked by the described authenticated service ingress; service configuration and injected connections are trusted. /usr/bin/dotnet is an administrator-owned installation; environment and working directory are sanitized; caller enforces a deadline and small output bound."
}
```

### Split

```json
"held_out"
```

## v2-csharp-safe-06 — An outgoing contact record uses XML text APIs for untrusted values

Proposed label: **safe**. Human review: **pending**.

Source hash: `3a29c6960cb7ed6aad0f0be497939e1a63278f86b42001d5bd0a2b4715020528`. Protocol-2.0 case hash: `1b553ff899f55def2dde0f52cfd9de8445352761f8e757a73b9143a4a75f16ca`.

Untrusted contact values are written through WriteElementString, which treats them as XML text and escapes markup characters. No parser or external resolver consumes user input in this operation.

### src/ContactXml.cs

```csharp
using System;
using System.Text;
using System.Xml;
public static class ContactXml {
    public static string Write(string name, string city) {
        if (name.Length > 120 || city.Length > 80) throw new ArgumentException("contact");
        var text = new StringBuilder();
        var settings = new XmlWriterSettings { OmitXmlDeclaration = true, ConformanceLevel = ConformanceLevel.Document };
        using (var writer = XmlWriter.Create(text, settings)) {
            writer.WriteStartElement("contact");
            writer.WriteElementString("name", name);
            writer.WriteElementString("city", city);
            writer.WriteEndElement();
        }
        return text.ToString();
    }
}
```

### Derivation

```json
{
  "group": "csharp-contact-xml-text-writer",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "This safe case constructs an outgoing document using text APIs, rather than toggling resolver settings on a vulnerable reader sibling. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "Structured XML output and injection false-positive control; no external entity parsing occurs.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Create an XML contact record for a downstream data-only CRM API.",
  "trust_boundary": "A user controls name and city strings but may not add elements, attributes or entity declarations.",
  "legitimate_examples": [
    {
      "input": "name=A & B, city=<Paris>",
      "expected": "Produce contact XML whose decoded name is A & B and city is <Paris>, with both values escaped as text."
    },
    {
      "input": "A string containing an XML closing-tag sequence",
      "expected": "Keep the sequence in element text rather than changing document structure."
    }
  ],
  "permitted_changes": [
    "Retain structured writer APIs and exact decoded string values.",
    "Do not replace text writes with WriteRaw or manual markup concatenation."
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
    "https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo.argumentlist",
    "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca3075"
  ]
}
```

### Regression traps

```json
[
  "XML-related code is not inherently an entity-resolution sink; this code only writes text.",
  "Discarding punctuation to avoid escaping changes legitimate contact data."
]
```

### Remediation constraints

```json
[
  "Retain structured writer APIs and exact decoded string values.",
  "Do not replace text writes with WriteRaw or manual markup concatenation."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-csharp-safe-06",
  "prior_case_id": "csharp-xml-resolver-safe",
  "prior_source_sha256": "5b4524246acc63ccbada5ff08df8b87bd243ed3c3f3f3fbdfa70cb0dce81305c",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; C# 12",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Linux x86-64 unless a case explicitly says Windows",
  "setup": "Methods are invoked by the described authenticated service ingress; service configuration and injected connections are trusted. .NET 8 XmlWriter; inputs contain only valid XML 1.0 characters, enforced at ingress; the downstream CRM consumes a fixed contact schema without interpreting element text as code."
}
```

### Split

```json
"held_out"
```

## v2-csharp-vulnerable-01 — Tenant-bound customer search splices a free-text predicate into SQL

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `67db58c36597c0c103404592f919059a2811b7a051b98255c0fb43bdb1a98632`. Protocol-2.0 case hash: `a9e315911bc65da4e39567990f06eebc00474ecb55e50fc01bb2d80bc6581218`.

TenantId is parameterized but City is inserted into the query grammar, allowing input to change the predicate despite one correctly bound parameter.

### src/CustomerSearch.cs

```csharp
using System;
using System.Data;
using System.Collections.Generic;
using Microsoft.Data.SqlClient;
public static class CustomerSearch {
    public static List<string> Find(SqlConnection connection, int tenant, string city) {
        if (city.Length > 80) throw new ArgumentException("city");
        using var command = connection.CreateCommand();
        command.CommandText = "SELECT Name FROM Customers WHERE TenantId=@tenant AND City='" + city + "'";
        command.Parameters.Add("@tenant", SqlDbType.Int).Value = tenant;
        var names = new List<string>();
        using var reader = command.ExecuteReader();
        while (reader.Read()) names.Add(reader.GetString(0));
        return names;
    }
}
```

### src/CustomerRoute.cs

```csharp
using System;
using System.Collections.Generic;
using System.Security.Claims;
using Microsoft.Data.SqlClient;
public static class CustomerRoute {
    public static List<string> Handle(SqlConnection connection, ClaimsPrincipal user,
                                       IReadOnlyDictionary<string, string> query) {
        if (user.Identity?.IsAuthenticated != true) throw new UnauthorizedAccessException();
        var tenantClaim = user.FindFirst("tenant") ?? throw new UnauthorizedAccessException();
        if (!int.TryParse(tenantClaim.Value, out int tenant) || tenant < 1) throw new UnauthorizedAccessException();
        if (!query.TryGetValue("city", out string city)) throw new ArgumentException("city required");
        return CustomerSearch.Find(connection, tenant, city);
    }
}
```

### Derivation

```json
{
  "group": "csharp-mixed-bound-unbound-tenant-query",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "The query already contains one security-sensitive bound filter, so repair must preserve isolation while binding another field. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "sql-injection",
    "cwe": "CWE-89",
    "path": "src/CustomerSearch.cs",
    "line_start": 9,
    "line_end": 9
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "SQL construction and tenant predicate preservation.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return customer names in the authorized tenant whose city exactly equals the requested string.",
  "trust_boundary": "The caller derives tenant from authenticated identity; the user supplies city and must not alter SQL syntax or tenant scope.",
  "legitimate_examples": [
    {
      "input": "Tenant 7, city O'Fallon",
      "expected": "Return only tenant 7 customers with that literal city."
    },
    {
      "input": "City with SQL punctuation",
      "expected": "Treat the entire value as a string predicate value."
    }
  ],
  "permitted_changes": [
    "Bind city with a typed parameter while retaining the tenant predicate.",
    "Preserve the result list and database nullability contract."
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
    "https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo.argumentlist",
    "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca3075"
  ]
}
```

### Regression traps

```json
[
  "Parameterizing one part of a query does not sanitize concatenated parts.",
  "Removing the tenant predicate to simplify a fix exposes other tenants."
]
```

### Remediation constraints

```json
[
  "Bind city with a typed parameter while retaining the tenant predicate.",
  "Preserve the result list and database nullability contract."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-csharp-vulnerable-01",
  "prior_case_id": "csharp-account-command-vulnerable",
  "prior_source_sha256": "d46f47a585a71793ebb6aaefa8d92e9fac94dffa211292ce1e2e66fbe4959d33",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; C# 12",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Linux x86-64 unless a case explicitly says Windows",
  "setup": "Methods are invoked by the described authenticated service ingress; service configuration and injected connections are trusted. Microsoft.Data.SqlClient 5.2.2; SQL Server 2022; open connection; Name and City are NOT NULL NVARCHAR, City length 80. ClaimsPrincipal is created by a trusted authenticated middleware; client input cannot add or alter tenant claims."
}
```

### Split

```json
"held_out"
```

## v2-csharp-vulnerable-02 — Image worker uses ArgumentList but deliberately launches a shell

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `c003ad3ec75e3b9948f599ce782dd4afa8e68f7f61ffb60f9824376ed236caf3`. Protocol-2.0 case hash: `e39be7f7d76c32bfa88a9304cd96e7d0bd7dcfadba80f79f7fb1b789e883ecb3`.

ArgumentList separates the shell arguments but the -c argument remains a program assembled from an uploaded path. UseShellExecute=false does not disable an explicitly selected shell.

### src/ImageSummary.cs

```csharp
using System;
using System.Diagnostics;
public static class ImageSummary {
    public static string Summarize(string uploadPath) {
        if (uploadPath.Length > 180) throw new ArgumentException("path");
        var start = new ProcessStartInfo("/bin/sh") { UseShellExecute = false, RedirectStandardOutput = true };
        start.ArgumentList.Add("-c");
        start.ArgumentList.Add("/usr/bin/identify -format '%wx%h' " + uploadPath);
        using var child = Process.Start(start) ?? throw new InvalidOperationException("spawn");
        string summary = child.StandardOutput.ReadToEnd();
        child.WaitForExit();
        if (child.ExitCode != 0) throw new InvalidOperationException("identify");
        return summary;
    }
}
```

### Derivation

```json
{
  "group": "csharp-shell-inside-argumentlist",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "A normally safer process API is misused by selecting a shell and feeding it one constructed program string. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "shell-injection",
    "cwe": "CWE-78",
    "path": "src/ImageSummary.cs",
    "line_start": 8,
    "line_end": 8
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Explicit shell interpretation of an authorized path; image parser vulnerabilities are outside this source case.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return the dimensions of one authorized uploaded image as widthxheight.",
  "trust_boundary": "A user controls a basename already placed under an authorized private upload root; the complete path may contain shell metacharacters.",
  "legitimate_examples": [
    {
      "input": "Path /srv/uploads/7/family photo.png",
      "expected": "Return dimensions for that exact file."
    },
    {
      "input": "Invalid image",
      "expected": "Throw after reaping the child; do not manufacture dimensions."
    }
  ],
  "permitted_changes": [
    "Launch identify directly with separate arguments, a fixed format, and its option terminator.",
    "Preserve captured output and exit failure handling; keep authorization of the upload path."
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
    "https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo.argumentlist",
    "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca3075"
  ]
}
```

### Regression traps

```json
[
  "ArgumentList is not a sanitizer for a string passed to sh -c.",
  "Do not replace the worker process or drop captured dimensions."
]
```

### Remediation constraints

```json
[
  "Launch identify directly with separate arguments, a fixed format, and its option terminator.",
  "Preserve captured output and exit failure handling; keep authorization of the upload path."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-csharp-vulnerable-02",
  "prior_case_id": "csharp-shell-command-vulnerable",
  "prior_source_sha256": "85a022c8c2bfe815c981777d1e5464491798874a292030c25182f50da82c2f0e",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; C# 12",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Linux x86-64 unless a case explicitly says Windows",
  "setup": "Methods are invoked by the described authenticated service ingress; service configuration and injected connections are trusted. ImageMagick 6.9 identify at /usr/bin/identify; caller supplies a stable regular image inside a private directory, caps output and enforces a deadline."
}
```

### Split

```json
"held_out"
```

## v2-csharp-vulnerable-03 — Release metadata client disables verification on the handler it actually uses

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `dbc031a8afa8468a21940a78b51a8781b628aaadec2625a8ade2666372170264`. Protocol-2.0 case hash: `4469d322304a328828614e274a5f169262d32b74d8e1c2eae3576be2c70d7421`.

The live HttpClient uses a handler that accepts any certificate, so an active network attacker can impersonate the fixed release host. A fixed URL and disabled redirects do not restore TLS authentication.

### src/ReleaseMetadata.cs

```csharp
using System;
using System.Net.Http;
using System.Threading.Tasks;
public static class ReleaseMetadata {
    public static async Task<string> CurrentAsync() {
        using var handler = new HttpClientHandler();
        handler.AllowAutoRedirect = false;
        handler.ServerCertificateCustomValidationCallback = HttpClientHandler.DangerousAcceptAnyServerCertificateValidator;
        using var client = new HttpClient(handler) { Timeout = TimeSpan.FromSeconds(10) };
        using var response = await client.GetAsync("https://releases.example.org/current.json");
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadAsStringAsync();
    }
}
```

### Derivation

```json
{
  "group": "csharp-release-handler-consumer",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "The vulnerable policy is connected to a real request and has a defined integrity consequence rather than being an unused configuration snippet. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "tls-validation",
    "cwe": "CWE-295",
    "path": "src/ReleaseMetadata.cs",
    "line_start": 8,
    "line_end": 8
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "TLS server authentication with explicit consumer wiring.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return authenticated release metadata from a fixed HTTPS endpoint.",
  "trust_boundary": "The network is untrusted and release metadata influences the version displayed to operators; the endpoint configuration is trusted.",
  "legitimate_examples": [
    {
      "input": "Valid publicly trusted endpoint certificate",
      "expected": "Return response body on a successful status."
    },
    {
      "input": "Untrusted or wrong-host certificate",
      "expected": "Fail before accepting metadata."
    }
  ],
  "permitted_changes": [
    "Use platform hostname and chain verification, or a documented narrow trust policy.",
    "Keep HTTPS, redirect refusal, timeout and non-success errors."
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
    "https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo.argumentlist",
    "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca3075"
  ]
}
```

### Regression traps

```json
[
  "Accepting certificates only when the subject text matches is not chain validation.",
  "Changing the URL to HTTP makes the original security requirement impossible."
]
```

### Remediation constraints

```json
[
  "Use platform hostname and chain verification, or a documented narrow trust policy.",
  "Keep HTTPS, redirect refusal, timeout and non-success errors."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-csharp-vulnerable-03",
  "prior_case_id": "csharp-tls-handler-vulnerable",
  "prior_source_sha256": "d954764fc18f905c7bc50b4d61009cb532804966232fd9b5457e04c0e1f322fb",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; C# 12",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Linux x86-64 unless a case explicitly says Windows",
  "setup": "Methods are invoked by the described authenticated service ingress; service configuration and injected connections are trusted. .NET 8 HttpClientHandler on Linux with a maintained OS trust store; caller enforces a 64 KiB response cap at ingress."
}
```

### Split

```json
"held_out"
```

## v2-csharp-vulnerable-04 — Invoice importer resolves external XML entities before extracting a name

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `9ec3b324c3f56f0309c215ca22056b54c4061ee21a20b1a339893339bc320033`. Protocol-2.0 case hash: `34d4524daf6d52a4e822eeab06170512d925bdf334d126aef502e35aa75bc539`.

External entity resolution is explicitly enabled for tenant-uploaded XML. A finite entity expansion limit limits volume but still permits file or network content to enter the returned customer field.

### src/InvoiceName.cs

```csharp
using System;
using System.IO;
using System.Xml;
using System.Xml.Linq;
public static class InvoiceName {
    public static string Read(string xml) {
        if (xml.Length > 65536) throw new ArgumentException("invoice");
        var settings = new XmlReaderSettings { DtdProcessing = DtdProcessing.Parse, XmlResolver = new XmlUrlResolver(), MaxCharactersFromEntities = 4096 };
        using var text = new StringReader(xml);
        using var reader = XmlReader.Create(text, settings);
        var document = XDocument.Load(reader);
        return document.Root?.Element("customer")?.Value ?? throw new FormatException("customer");
    }
}
```

### Derivation

```json
{
  "group": "csharp-invoice-reader-entity-access",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "A bounded import requires actual XML text extraction, making external resolution observable in an application field. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "unsafe-xml",
    "cwe": "CWE-611",
    "path": "src/InvoiceName.cs",
    "line_start": 8,
    "line_end": 8
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "External XML entity access; ordinary XML parsing and text extraction are required.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Read the customer text from a small invoice XML document.",
  "trust_boundary": "A tenant supplies the entire XML, including any DOCTYPE; service files and internal network resources are not tenant-readable.",
  "legitimate_examples": [
    {
      "input": "<invoice><customer>A &amp; B</customer></invoice>",
      "expected": "Return A & B."
    },
    {
      "input": "An invoice with an external entity declaration",
      "expected": "Reject it without opening any external resource."
    }
  ],
  "permitted_changes": [
    "Prohibit DTDs and external resolution while preserving built-in XML entities and ordinary customer text.",
    "Keep input size and required-customer validation."
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
    "https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo.argumentlist",
    "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca3075"
  ]
}
```

### Regression traps

```json
[
  "Lowering MaxCharactersFromEntities does not prohibit external reads.",
  "Returning escaped raw XML instead of the customer value changes the operation."
]
```

### Remediation constraints

```json
[
  "Prohibit DTDs and external resolution while preserving built-in XML entities and ordinary customer text.",
  "Keep input size and required-customer validation."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-csharp-vulnerable-04",
  "prior_case_id": "csharp-state-formatter-vulnerable",
  "prior_source_sha256": "ccc3b2a2949775339c4f65be636a51e451e0207bed7300178b49dd287ffe88e4",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; C# 12",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Linux x86-64 unless a case explicitly says Windows",
  "setup": "Methods are invoked by the described authenticated service ingress; service configuration and injected connections are trusted. No application DTD is required; the service account can access nonpublic local configuration files."
}
```

### Split

```json
"held_out"
```

## v2-csharp-vulnerable-05 — Legacy offline badge encryption uses DES with a random IV

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `deb08d9cd2f9e7f025221fbd3e269f08c945419f6c6e6b2806d42cc8483e0ff0`. Protocol-2.0 case hash: `33d3716a419a4a23dcd88d2f6db499249fa0070288b4e33d222df774e03e6ab3`.

DES has an inadequate effective key length for confidentiality. Random IVs do not repair the primitive; unauthenticated CBC also requires an integrity-aware migration rather than an in-place constant substitution.

### src/BadgeCipher.cs

```csharp
using System;
using System.Security.Cryptography;
public static class BadgeCipher {
    public static byte[] Encrypt(byte[] employeeId, byte[] key) {
        if (employeeId.Length > 128 || key.Length != 8) throw new ArgumentException("badge");
        using var algorithm = DES.Create();
        algorithm.Key = key;
        algorithm.GenerateIV();
        using var transform = algorithm.CreateEncryptor();
        byte[] ciphertext = transform.TransformFinalBlock(employeeId, 0, employeeId.Length);
        byte[] envelope = new byte[algorithm.IV.Length + ciphertext.Length];
        Buffer.BlockCopy(algorithm.IV, 0, envelope, 0, algorithm.IV.Length);
        Buffer.BlockCopy(ciphertext, 0, envelope, algorithm.IV.Length, ciphertext.Length);
        return envelope;
    }
}
```

### Derivation

```json
{
  "group": "csharp-offline-badge-envelope-migration",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "The fix crosses an external binary format and key-size contract, so primitive replacement alone is not a valid remediation. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "weak-cryptography",
    "cwe": "CWE-327",
    "path": "src/BadgeCipher.cs",
    "line_start": 6,
    "line_end": 6
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Weak cipher selection and secure envelope migration; this candidate requires human validation of compatibility constraints.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Produce a versioned encrypted employee identifier for an offline badge reader.",
  "trust_boundary": "Attackers can obtain badge ciphertexts but not the encryption key; the reader must recover the original identifier after migration.",
  "legitimate_examples": [
    {
      "input": "Employee identifier bytes for E-204",
      "expected": "A compatible reader recovers exactly E-204."
    },
    {
      "input": "Two encryptions of the same identifier",
      "expected": "Use independent randomness; do not reuse a fixed IV."
    }
  ],
  "permitted_changes": [
    "Migrate to authenticated encryption with a new explicit envelope version and appropriately sized fresh keys.",
    "Document reader migration and reject malformed envelopes; do not silently reinterpret old bytes."
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
    "https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo.argumentlist",
    "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca3075"
  ]
}
```

### Regression traps

```json
[
  "Replacing DES with AES while retaining an eight-byte key is invalid.",
  "Keeping old unauthenticated envelopes without a migration boundary leaves tampering unresolved."
]
```

### Remediation constraints

```json
[
  "Migrate to authenticated encryption with a new explicit envelope version and appropriately sized fresh keys.",
  "Document reader migration and reject malformed envelopes; do not silently reinterpret old bytes."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-csharp-vulnerable-05",
  "prior_case_id": "csharp-integrity-alias-vulnerable",
  "prior_source_sha256": "19cb8cf0d80349ac18356be2f31641b0e6594dcc54f2689769ea470bcf47d87a",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; C# 12",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Linux x86-64 unless a case explicitly says Windows",
  "setup": "Methods are invoked by the described authenticated service ingress; service configuration and injected connections are trusted. The eight-byte input key is a service-generated non-weak DES key; an external versioned badge-reader interface may be revised but must be documented."
}
```

### Split

```json
"held_out"
```

## v2-csharp-vulnerable-06 — A legacy desktop bridge restores untrusted object graphs from an upload

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `ee6d4cbcac5a9a52106f88fe50ddc019c0355a7cf608aebf4f3124901c29df7f`. Protocol-2.0 case hash: `958b9454ec2b680913905ac73662cf91d774e435be00e94cd34ff98b32c724dc`.

BinaryFormatter instantiates an attacker-controlled object graph before the result is cast and validated. A post-deserialization type check does not make that operation safe.

### src/LayoutImport.cs

```csharp
using System;
using System.IO;
using System.Runtime.Serialization.Formatters.Binary;
[Serializable]
public sealed class Layout { public string Name = ""; public int Columns; }
public static class LayoutImport {
    public static Layout Import(byte[] upload) {
        if (upload.Length > 65536) throw new ArgumentException("upload");
        using (var input = new MemoryStream(upload, false)) {
            var formatter = new BinaryFormatter();
            object value = formatter.Deserialize(input);
            var layout = value as Layout;
            if (layout == null || layout.Columns < 1 || layout.Columns > 12) throw new FormatException("layout");
            return layout;
        }
    }
}
```

### Derivation

```json
{
  "group": "csharp-legacy-layout-object-graph",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "The case pins an actually enabled legacy runtime and includes post-load checks that cannot undo arbitrary object construction. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "unsafe-deserialization",
    "cwe": "CWE-502",
    "path": "src/LayoutImport.cs",
    "line_start": 11,
    "line_end": 11
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Unsafe object graph construction on an explicitly supported legacy runtime.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Import a bounded layout containing a name and column count from a partner upload.",
  "trust_boundary": "The partner controls bytes and cannot run code in the desktop bridge; signed application code runs with user privileges.",
  "legitimate_examples": [
    {
      "input": "Approved layout named Overview with three columns",
      "expected": "Return those two values."
    },
    {
      "input": "An object graph naming arbitrary runtime types",
      "expected": "Reject without instantiating arbitrary types."
    }
  ],
  "permitted_changes": [
    "Replace object-graph deserialization with an explicit data-only schema and validate fields.",
    "Allow a documented format migration; do not claim to safely deserialize arbitrary legacy BinaryFormatter uploads."
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
    "https://learn.microsoft.com/en-us/dotnet/standard/serialization/binaryformatter-security-guide"
  ]
}
```

### Regression traps

```json
[
  "Casting to Layout after Deserialize is too late.",
  "A new runtime that disables BinaryFormatter would make this original example non-reachable and must not be substituted silently."
]
```

### Remediation constraints

```json
[
  "Replace object-graph deserialization with an explicit data-only schema and validate fields.",
  "Allow a documented format migration; do not claim to safely deserialize arbitrary legacy BinaryFormatter uploads."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-csharp-vulnerable-06",
  "prior_case_id": "csharp-xml-resolver-vulnerable",
  "prior_source_sha256": "3345837c0d7f817d61fd7269ed66f7536c1ec3205bd5dbe45d38ef560eaa6b35",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET Framework 4.8; C# 7.3",
  "libraries": [
    ".NET Framework 4.8 BCL"
  ],
  "platform": "Windows Server 2022",
  "setup": "Methods are invoked by the described authenticated service ingress; service configuration and injected connections are trusted. This case specifically targets .NET Framework 4.8 on Windows 10/Server 2022, where BinaryFormatter.Deserialize remains enabled; it does not target .NET 9+."
}
```

### Split

```json
"held_out"
```

