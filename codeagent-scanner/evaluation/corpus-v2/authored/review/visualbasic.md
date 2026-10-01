# visualbasic — authored corpus-v2 candidates

AI-authored, pending independent human review. Static validation is separate evidence, not approval. Source is quoted for inspection and must not be executed.

Review the corpus-level context and checklist in the [complete unsigned manifest](../unsigned-review-manifest.json) alongside each case.

## v2-visualbasic-safe-01 — Hourly alert count binds a timestamp and returns a scalar

Proposed label: **safe**. Human review: **pending**.

Source hash: `f4ef64eba480ffef13d4e9598523fa6b9eae40c3ab405299e55fdc14a11d5130`. Protocol-2.0 case hash: `8116ef7939a5b9e3d191f4ca7a0054a143b6bb64292c00ef6b446bf6a23d46d3`.

A fixed query receives a typed UTC timestamp parameter. No request text becomes SQL grammar or a locale-formatted date literal.

### src/AlertCount.vb

```visualbasic
Option Strict On
Imports System
Imports System.Data
Imports Microsoft.Data.SqlClient
Public Module AlertCount
    Public Function Since(connection As SqlConnection, afterUtc As DateTime) As Integer
        If afterUtc.Kind <> DateTimeKind.Utc Then Throw New ArgumentException("UTC required")
        Using command As New SqlCommand("SELECT COUNT(*) FROM Alerts WHERE CreatedAt >= @after", connection)
            command.Parameters.Add("@after", SqlDbType.DateTime2).Value = afterUtc
            Dim result = command.ExecuteScalar()
            Return Convert.ToInt32(result)
        End Using
    End Function
End Module
```

### Derivation

```json
{
  "group": "vb-alert-time-typed-parameter",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "This safe query exercises a typed temporal value and boundary comparison, not a sanitized text-search sibling. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "SQL parameterization and timestamp boundary semantics.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Count alerts at or after a precise UTC instant.",
  "trust_boundary": "A user selects the instant through a validated datetime API; the connection is service-owned.",
  "legitimate_examples": [
    {
      "input": "UTC 2025-01-01T00:00:00",
      "expected": "Count rows at or later than that exact instant."
    },
    {
      "input": "A DateTime with Kind=Local",
      "expected": "Reject instead of silently reinterpreting the timezone."
    }
  ],
  "permitted_changes": [
    "Keep typed DateTime2 binding and UTC validation.",
    "Preserve inclusive timestamp comparison."
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
    "https://learn.microsoft.com/en-us/dotnet/framework/data/adonet/configuring-parameters-and-parameter-data-types",
    "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca5359"
  ]
}
```

### Regression traps

```json
[
  "Formatting dates into SQL strings introduces locale and injection hazards.",
  "Changing >= to > loses boundary events."
]
```

### Remediation constraints

```json
[
  "Keep typed DateTime2 binding and UTC validation.",
  "Preserve inclusive timestamp comparison."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-visualbasic-safe-01",
  "prior_case_id": "visualbasic-order-command-safe",
  "prior_source_sha256": "fd5456e0f251d8a49b67c46455b0f77a0cd6f3666b8324589dd561389040d32a",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; Visual Basic 16.9; Option Strict On",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Windows Server 2022",
  "setup": "Methods are invoked with non-null values from the described ingress; the service configuration and database connection are trusted. SQL Server 2022; Microsoft.Data.SqlClient 5.2.2; CreatedAt is UTC DATETIME2 NOT NULL; the open connection is authorized for the alert collection."
}
```

### Split

```json
"held_out"
```

## v2-visualbasic-safe-02 — Legacy label XML allows bounded internal entities but no external resolver

Proposed label: **safe**. Human review: **pending**.

Source hash: `769cacfcc754a935d542880b6e4199f943791cd76348abd4848bd437fc7ce77b`. Protocol-2.0 case hash: `ef374a1eb21d8f58127e10d48bf739e77c2ae626c522b579bc513ec66eafa89b`.

DTD parsing is required for a legacy internal-entity label format, but the consuming reader has no external resolver and strict expansion/document limits. DtdProcessing.Parse alone is insufficient to label this an external-entity vulnerability.

### src/LabelText.vb

```visualbasic
Option Strict On
Imports System
Imports System.IO
Imports System.Xml
Public Module LabelText
    Public Function Read(xml As String) As String
        If xml.Length > 8192 Then Throw New ArgumentException("label")
        Dim settings As New XmlReaderSettings With {.DtdProcessing = DtdProcessing.Parse, .XmlResolver = Nothing, .MaxCharactersFromEntities = 256, .MaxCharactersInDocument = 8192}
        Using input As New StringReader(xml)
            Using reader = XmlReader.Create(input, settings)
                reader.MoveToContent()
                If reader.Name <> "label" Then Throw New FormatException("label root")
                Return reader.ReadElementContentAsString()
            End Using
        End Using
    End Function
End Module
```

### Derivation

```json
{
  "group": "vb-internal-entity-no-resolution",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "This safe XML case intentionally needs internal DTD entities, making it different from a simple Prohibit counterpart and testing policy precision. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "External entity access and bounded internal expansion.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Read small label text, including a limited set of inline internal entity abbreviations.",
  "trust_boundary": "A partner controls the XML; it cannot resolve external files or network entities.",
  "legitimate_examples": [
    {
      "input": "<!DOCTYPE label [<!ENTITY unit \"kg\">]><label>12 &unit;</label>",
      "expected": "Return 12 kg."
    },
    {
      "input": "Internal entity expansion exceeding 256 characters",
      "expected": "Reject with a parser error."
    }
  ],
  "permitted_changes": [
    "Retain null external resolver and expansion/document limits.",
    "Preserve legitimate internal-entity text rather than prohibiting the required format without migration."
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
    "https://learn.microsoft.com/en-us/dotnet/framework/data/adonet/configuring-parameters-and-parameter-data-types",
    "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca5359"
  ]
}
```

### Regression traps

```json
[
  "A blanket ban on DtdProcessing.Parse would report an overbroad finding for this contract.",
  "Increasing entity limits without a business bound broadens denial-of-service exposure."
]
```

### Remediation constraints

```json
[
  "Retain null external resolver and expansion/document limits.",
  "Preserve legitimate internal-entity text rather than prohibiting the required format without migration."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-visualbasic-safe-02",
  "prior_case_id": "visualbasic-diagnostic-shell-safe",
  "prior_source_sha256": "df1953f26552003f00ff68ca464aaa3e62b8e3927141a90cff29fd413bc63362",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; Visual Basic 16.9; Option Strict On",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Windows Server 2022",
  "setup": "Methods are invoked with non-null values from the described ingress; the service configuration and database connection are trusted. .NET 8 XmlReaderSettings; XmlResolver=Nothing prevents external retrieval; external-entity documents need not yield successful output and are never trusted as external content."
}
```

### Split

```json
"held_out"
```

## v2-visualbasic-safe-03 — A compact session envelope uses authenticated AES-GCM with fresh nonce

Proposed label: **safe**. Human review: **pending**.

Source hash: `f9f1e2def2f65e7b77059e86d7d7c57cf09a7a3f526c78c424ce32570708111a`. Protocol-2.0 case hash: `2f5e30b9665b375b3eb433905f85451b5fa21b7f678c8e2eda53abeabdb9fea0`.

AES-GCM authenticates ciphertext using a freshly generated 96-bit nonce and a 128-bit tag. The key is supplied from trusted configuration and must be 256 bits.

### src/SessionEnvelope.vb

```visualbasic
Option Strict On
Imports System
Imports System.Security.Cryptography
Public Module SessionEnvelope
    Public Function Seal(payload As Byte(), key As Byte()) As Byte()
        If payload.Length > 4096 OrElse key.Length <> 32 Then Throw New ArgumentException("envelope")
        Dim nonce = RandomNumberGenerator.GetBytes(12)
        Dim ciphertext(payload.Length - 1) As Byte
        Dim tag(15) As Byte
        Using cipher As New AesGcm(key, 16)
            cipher.Encrypt(nonce, payload, ciphertext, tag)
        End Using
        Dim output(12 + 16 + ciphertext.Length - 1) As Byte
        Buffer.BlockCopy(nonce, 0, output, 0, 12)
        Buffer.BlockCopy(tag, 0, output, 12, 16)
        Buffer.BlockCopy(ciphertext, 0, output, 28, ciphertext.Length)
        Return output
    End Function
End Module
```

### Derivation

```json
{
  "group": "vb-session-aead-envelope",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "The safe cryptographic case has a defined wire layout and authenticated receiver contract, independent from legacy cipher migrations. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "Modern authenticated encryption with explicit nonce and envelope contracts.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Seal a bounded nonempty session payload into nonce, tag and ciphertext bytes.",
  "trust_boundary": "The client may observe or modify envelopes but never receives the server key; the receiver verifies the GCM tag before exposing plaintext.",
  "legitimate_examples": [
    {
      "input": "One-byte payload 41 with a valid key",
      "expected": "Return 29 bytes: 12 nonce, 16 tag and one ciphertext byte."
    },
    {
      "input": "Key length 16",
      "expected": "Reject because the protocol requires a 32-byte key."
    }
  ],
  "permitted_changes": [
    "Keep authenticated encryption, fresh nonces and the exact envelope layout.",
    "Reject invalid keys and preserve the receiver requirement to verify tags."
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
    "https://learn.microsoft.com/en-us/dotnet/framework/data/adonet/configuring-parameters-and-parameter-data-types",
    "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca5359"
  ]
}
```

### Regression traps

```json
[
  "A fixed nonce would destroy the stated guarantee.",
  "Dropping the tag changes authenticated encryption into an incomplete envelope."
]
```

### Remediation constraints

```json
[
  "Keep authenticated encryption, fresh nonces and the exact envelope layout.",
  "Reject invalid keys and preserve the receiver requirement to verify tags."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-visualbasic-safe-03",
  "prior_case_id": "visualbasic-certificate-callback-safe",
  "prior_source_sha256": "7559de36fa8935341599b1c11b1793293154daa670a748f8af5f2d5872d47a43",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; Visual Basic 16.9; Option Strict On",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Windows Server 2022",
  "setup": "Methods are invoked with non-null values from the described ingress; the service configuration and database connection are trusted. .NET 8 AesGcm; payload length is 1..4096 at ingress; key is random and rotated before nonce collision risk becomes material; receiver already implements this layout."
}
```

### Split

```json
"held_out"
```

## v2-visualbasic-safe-04 — A Windows service restart accepts only enumerated internal service names

Proposed label: **safe**. Human review: **pending**.

Source hash: `d054db683810c4382595f453c87f6c67c51eba6139acf23e6b4476087e3bd852`. Protocol-2.0 case hash: `6e5fe539daa4257754c8343986d3a6994aad332057b78f48d14aaf624223deca`.

The public choice maps to one of two fixed service names passed directly to sc.exe without cmd. No caller value is accepted as an executable, command line or arbitrary service selector.

### src/RestartService.vb

```visualbasic
Option Strict On
Imports System
Imports System.Diagnostics
Public Module RestartService
    Public Function StopOne(kind As String) As Integer
        Dim service As String
        Select Case kind
            Case "collector" : service = "ContosoCollector"
            Case "exporter" : service = "ContosoExporter"
            Case Else : Throw New ArgumentException("service")
        End Select
        Dim start As New ProcessStartInfo("C:\Windows\System32\sc.exe") With {.UseShellExecute = False}
        start.ArgumentList.Add("stop")
        start.ArgumentList.Add(service)
        Using child = Process.Start(start)
            If child Is Nothing Then Throw New InvalidOperationException("spawn")
            child.WaitForExit()
            Return child.ExitCode
        End Using
    End Function
End Module
```

### Derivation

```json
{
  "group": "vb-allowlisted-service-control",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "A limited administrative operation is authorized while arbitrary command and service-name selection remain forbidden. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "Process-injection boundary for an intentionally privileged fixed utility.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Request a stop for one of two administrator-approved services and return sc.exe status.",
  "trust_boundary": "An authorized operator chooses collector or exporter; the operation itself is privileged but explicitly permitted.",
  "legitimate_examples": [
    {
      "input": "kind collector",
      "expected": "Request sc.exe stop ContosoCollector and return its exit code."
    },
    {
      "input": "kind collector & whoami",
      "expected": "Reject before starting a process."
    }
  ],
  "permitted_changes": [
    "Keep the allow-list and direct executable launch.",
    "Preserve the asynchronous service-state semantics: a successful stop request does not claim the service is already stopped."
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
    "https://learn.microsoft.com/en-us/dotnet/framework/data/adonet/configuring-parameters-and-parameter-data-types",
    "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca5359"
  ]
}
```

### Regression traps

```json
[
  "Do not interpret this authorized fixed administrative operation as injection solely because it is privileged.",
  "Returning success without checking the child code hides operational failure."
]
```

### Remediation constraints

```json
[
  "Keep the allow-list and direct executable launch.",
  "Preserve the asynchronous service-state semantics: a successful stop request does not claim the service is already stopped."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-visualbasic-safe-04",
  "prior_case_id": "visualbasic-import-formatter-safe",
  "prior_source_sha256": "5313b9b76071e08717d0bd291ee19948bf57d3ff93888629e3370b490e49bb63",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; Visual Basic 16.9; Option Strict On",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Windows Server 2022",
  "setup": "Methods are invoked with non-null values from the described ingress; the service configuration and database connection are trusted. Windows Server 2022; sc.exe and service registration are administrator-owned; caller authenticates and authorizes the two stop operations."
}
```

### Split

```json
"held_out"
```

## v2-visualbasic-safe-05 — A SQL-like saved-search label is stored only in memory

Proposed label: **safe**. Human review: **pending**.

Source hash: `7cc7cbba28acbb9d1ffb938ff4247da2d650a9872b08af873cc0a469ce873c32`. Protocol-2.0 case hash: `4e6406d2a383b23a25d86c34177a6c125f11cbab4aa0ca8e3fc12612d096bbe0`.

The saved-search label is a bounded string in a dictionary. Neither SQL syntax nor shell syntax is interpreted anywhere in this operation.

### src/SearchLabels.vb

```visualbasic
Option Strict On
Imports System
Imports System.Collections.Generic
Public Class SearchLabels
    Private ReadOnly labels As New Dictionary(Of Guid, String)()
    Public Sub Rename(id As Guid, label As String)
        If label.Length > 120 Then Throw New ArgumentException("label")
        If Not labels.ContainsKey(id) Then Throw New KeyNotFoundException()
        labels(id) = label
    End Sub
    Public Sub Add(id As Guid, label As String)
        If label.Length > 120 Then Throw New ArgumentException("label")
        labels.Add(id, label)
    End Sub
    Public Function Display(id As Guid) As String
        Return labels(id)
    End Function
End Class
```

### Derivation

```json
{
  "group": "vb-literal-saved-search-label",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "The user controls text that resembles a query but the implementation only stores and retrieves a label in a per-user object. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "Injection false-positive control in bounded in-memory state.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Maintain literal labels for caller-owned saved-search identifiers.",
  "trust_boundary": "A user controls a label for identifiers already authorized by the caller; labels do not contain query definitions.",
  "legitimate_examples": [
    {
      "input": "Label SELECT * FROM reports;",
      "expected": "Store and return that exact literal label."
    },
    {
      "input": "Rename an unknown identifier",
      "expected": "Throw without creating a new record."
    }
  ],
  "permitted_changes": [
    "Keep labels distinct from executable query definitions.",
    "Preserve exact text and unknown-ID behavior."
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
    "https://learn.microsoft.com/en-us/dotnet/framework/data/adonet/configuring-parameters-and-parameter-data-types",
    "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca5359"
  ]
}
```

### Regression traps

```json
[
  "Names containing Search or SQL-like content do not establish an execution sink.",
  "Silently creating records during rename changes the ownership model."
]
```

### Remediation constraints

```json
[
  "Keep labels distinct from executable query definitions.",
  "Preserve exact text and unknown-ID behavior."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-visualbasic-safe-05",
  "prior_case_id": "visualbasic-digest-import-safe",
  "prior_source_sha256": "04fb71c0beb8be53782e0c3e9c232542a7f8b1b1a22bced0bcf67b9a9559714f",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; Visual Basic 16.9; Option Strict On",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Windows Server 2022",
  "setup": "Methods are invoked with non-null values from the described ingress; the service configuration and database connection are trusted. A single-threaded caller owns one SearchLabels instance per user and authorizes IDs; display is plain text or output-encoded by the UI."
}
```

### Split

```json
"held_out"
```

## v2-visualbasic-safe-06 — Certificate audit evaluates errors but never overrides TLS decisions

Proposed label: **safe**. Human review: **pending**.

Source hash: `9be003b4afe1eda3dd1461dd36a88bae31b3e14ba76fd1e6946f3331278cc015`. Protocol-2.0 case hash: `cc8a97c50d01e8456269a46e4e88253cd30b0c512536040956f4d85f9f849703`.

This is a string-returning diagnostic formatter for an already determined validation result. It is not installed as a certificate validation callback and cannot accept a peer.

### src/CertificateAudit.vb

```visualbasic
Option Strict On
Imports System
Imports System.Net.Security
Public Module CertificateAudit
    Public Function Describe(errors As SslPolicyErrors) As String
        If errors = SslPolicyErrors.None Then Return "verified"
        Dim parts As New System.Collections.Generic.List(Of String)()
        If (errors And SslPolicyErrors.RemoteCertificateNotAvailable) <> 0 Then parts.Add("missing")
        If (errors And SslPolicyErrors.RemoteCertificateNameMismatch) <> 0 Then parts.Add("name")
        If (errors And SslPolicyErrors.RemoteCertificateChainErrors) <> 0 Then parts.Add("chain")
        Return String.Join(",", parts)
    End Function
End Module
```

### Derivation

```json
{
  "group": "vb-certificate-errors-diagnostic-only",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "A certificate-related helper is deliberately nonauthoritative and has a string type rather than a trust-policy result. Independence is a proposed classification pending human review; no effective sample size is claimed."
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
  "scope": "TLS-validation false-positive control; no networking or callback registration is present.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Render TLS policy error flags for operator diagnostics.",
  "trust_boundary": "The runtime supplies error flags; the returned string is displayed only and never converted to an accept/reject decision.",
  "legitimate_examples": [
    {
      "input": "SslPolicyErrors.None",
      "expected": "Return verified."
    },
    {
      "input": "NameMismatch Or ChainErrors",
      "expected": "Return name,chain."
    }
  ],
  "permitted_changes": [
    "Keep the return value diagnostic-only.",
    "Preserve combinations of flags rather than reporting only one."
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
    "https://learn.microsoft.com/en-us/dotnet/framework/data/adonet/configuring-parameters-and-parameter-data-types",
    "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca5359"
  ]
}
```

### Regression traps

```json
[
  "A comparison to SslPolicyErrors.None is not automatically a TLS bypass.",
  "Do not turn this formatter into an always-true boolean callback."
]
```

### Remediation constraints

```json
[
  "Keep the return value diagnostic-only.",
  "Preserve combinations of flags rather than reporting only one."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-visualbasic-safe-06",
  "prior_case_id": "visualbasic-xml-settings-safe",
  "prior_source_sha256": "3a38efa463ceb246d8c3426cc7d6e7164506c42760c62ec7f7e437e300b92cf3",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; Visual Basic 16.9; Option Strict On",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Windows Server 2022",
  "setup": "Methods are invoked with non-null values from the described ingress; the service configuration and database connection are trusted. The call site uses normal platform TLS validation and invokes this helper only after a failure or for logging."
}
```

### Split

```json
"held_out"
```

## v2-visualbasic-vulnerable-01 — Inventory grid accepts a sort expression as SQL syntax

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `bf68f23316b646a57abf23b5a1d1f794cba3dc838de3bfecee5a1f6ec2d52d3b`. Protocol-2.0 case hash: `c628c38ea9ec8b8fdfe09ca6b10d5a62475056392d7e1a1558e52b6fdcb96b49`.

The grid accepts a free-form expression in the ORDER BY grammar. Quoting a value parameter is not sufficient for an SQL identifier or ordering expression.

### src/InventoryGrid.vb

```visualbasic
Option Strict On
Imports System
Imports System.Data
Imports Microsoft.Data.SqlClient
Public Module InventoryGrid
    Public Function Load(connection As SqlConnection, sort As String) As DataTable
        If sort.Length > 64 Then Throw New ArgumentException("sort")
        Dim sql = "SELECT Sku, Quantity FROM Inventory ORDER BY " & sort
        Using command As New SqlCommand(sql, connection)
            Using adapter As New SqlDataAdapter(command)
                Dim table As New DataTable()
                adapter.Fill(table)
                Return table
            End Using
        End Using
    End Function
End Module
```

### Derivation

```json
{
  "group": "vb-inventory-sort-grammar",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Repair must map a finite UI ordering language to SQL structure rather than merely parameterize a scalar value. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "sql-injection",
    "cwe": "CWE-89",
    "path": "src/InventoryGrid.vb",
    "line_start": 8,
    "line_end": 8
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "SQL structure selection at an identifier/expression boundary.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return inventory rows ordered by one of the product sort modes sku, quantity-asc or quantity-desc.",
  "trust_boundary": "A dashboard user controls the requested sort mode and must not submit arbitrary SQL expressions.",
  "legitimate_examples": [
    {
      "input": "Sort quantity-desc",
      "expected": "Return rows ordered by Quantity DESC, then Sku ASC for ties."
    },
    {
      "input": "Sort sku",
      "expected": "Return rows ordered by Sku ASC."
    }
  ],
  "permitted_changes": [
    "Map public sort modes to fixed SQL fragments and reject unknown modes.",
    "Keep the selected columns and deterministic tie ordering."
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
    "https://learn.microsoft.com/en-us/dotnet/framework/data/adonet/configuring-parameters-and-parameter-data-types",
    "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca5359"
  ]
}
```

### Regression traps

```json
[
  "Binding the sort name as @sort does not select an SQL column.",
  "Escaping apostrophes does not constrain an unquoted expression."
]
```

### Remediation constraints

```json
[
  "Map public sort modes to fixed SQL fragments and reject unknown modes.",
  "Keep the selected columns and deterministic tie ordering."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-visualbasic-vulnerable-01",
  "prior_case_id": "visualbasic-order-command-vulnerable",
  "prior_source_sha256": "62bc8cf8a4aabdbbc10527463b30cf274777a81eea5fcd56e3c217e809bdc114",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; Visual Basic 16.9; Option Strict On",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Windows Server 2022",
  "setup": "Methods are invoked with non-null values from the described ingress; the service configuration and database connection are trusted. Microsoft.Data.SqlClient 5.2.2; SQL Server 2022; Sku is a unique non-null NVARCHAR field. The source currently misinterprets documented public sort modes."
}
```

### Split

```json
"held_out"
```

## v2-visualbasic-vulnerable-02 — Contact prefix filter concatenates quoted text into a LIKE expression

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `3959113874867f53587f0c0bc2c62fd55b6a8a7654cfc5f288cd5e1da01b4690`. Protocol-2.0 case hash: `f46e10128fbea2a9b6400c396afae980ca323ad0783e16842799bbb7a9eb8e12`.

An apostrophe in the prefix escapes the LIKE literal and changes SQL. A correct repair must also preserve literal-prefix semantics for wildcard characters.

### src/ContactPrefix.vb

```visualbasic
Option Strict On
Imports System
Imports Microsoft.Data.SqlClient
Public Module ContactPrefix
    Public Function Count(connection As SqlConnection, prefix As String) As Integer
        If prefix.Length > 40 Then Throw New ArgumentException("prefix")
        Dim pattern = prefix & "%"
        Using command As New SqlCommand()
            command.Connection = connection
            command.CommandText = "SELECT COUNT(*) FROM Contacts WHERE DisplayName LIKE '" & pattern & "'"
            Return Convert.ToInt32(command.ExecuteScalar())
        End Using
    End Function
End Module
```

### Derivation

```json
{
  "group": "vb-contact-prefix-pattern-language",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "The case distinguishes query syntax from a second embedded wildcard language that a complete fix must handle. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "sql-injection",
    "cwe": "CWE-89",
    "path": "src/ContactPrefix.vb",
    "line_start": 10,
    "line_end": 10
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "SQL injection and LIKE-pattern semantic preservation.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Count contacts whose display name begins with the exact user-supplied prefix.",
  "trust_boundary": "A user supplies arbitrary bounded display-name text, including apostrophes, percent and underscore.",
  "legitimate_examples": [
    {
      "input": "Prefix O'",
      "expected": "Count names beginning with the literal characters O followed by apostrophe."
    },
    {
      "input": "Prefix 10%",
      "expected": "Count names beginning with literal 10%, not all 10-prefixed names."
    }
  ],
  "permitted_changes": [
    "Bind the pattern and escape LIKE metacharacters using an explicit ESCAPE character.",
    "Keep the exact prefix semantics and integer count result."
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
    "https://learn.microsoft.com/en-us/dotnet/framework/data/adonet/configuring-parameters-and-parameter-data-types",
    "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca5359"
  ]
}
```

### Regression traps

```json
[
  "Parameterization alone removes SQL syntax injection but leaves unintended wildcard expansion.",
  "Replacing the prefix filter with equality loses prefix search."
]
```

### Remediation constraints

```json
[
  "Bind the pattern and escape LIKE metacharacters using an explicit ESCAPE character.",
  "Keep the exact prefix semantics and integer count result."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-visualbasic-vulnerable-02",
  "prior_case_id": "visualbasic-diagnostic-shell-vulnerable",
  "prior_source_sha256": "8b3c8dd715da6e9c59f56c81fb8a10250c70f7d3298e424f061129ee8d568929",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; Visual Basic 16.9; Option Strict On",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Windows Server 2022",
  "setup": "Methods are invoked with non-null values from the described ingress; the service configuration and database connection are trusted. SQL Server 2022; Microsoft.Data.SqlClient 5.2.2; DisplayName is NVARCHAR(200) NOT NULL; collation-defined case sensitivity is intentional."
}
```

### Split

```json
"held_out"
```

## v2-visualbasic-vulnerable-03 — Dispatch logger puts an operator message into cmd redirection

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `2f977fce07e33a9ebd2459dfb7a6b09b52c13c485a684e8bb4a74b8e165e0c0d`. Protocol-2.0 case hash: `fcca7ec4cb0acab75c9f3cb9aad6172281b5ffe8db601bc1e250d268caea8b5d`.

Newline rejection does not neutralize cmd metacharacters. A limited operator role can inject additional commands through a message intended only for a log.

### src/DispatchLog.vb

```visualbasic
Option Strict On
Imports System
Imports System.Diagnostics
Public Module DispatchLog
    Public Function Append(message As String) As Integer
        If message.Length > 200 OrElse message.Contains(vbCr) OrElse message.Contains(vbLf) Then Throw New ArgumentException("message")
        Dim start As New ProcessStartInfo("C:\Windows\System32\cmd.exe")
        start.UseShellExecute = False
        start.ArgumentList.Add("/d")
        start.ArgumentList.Add("/c")
        start.ArgumentList.Add("echo " & message & " >> C:\Service\dispatch.log")
        Using child = Process.Start(start)
            If child Is Nothing Then Throw New InvalidOperationException("spawn")
            child.WaitForExit()
            Return child.ExitCode
        End Using
    End Function
End Module
```

### Derivation

```json
{
  "group": "vb-dispatch-log-command-redirection",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "A restricted append-only operator permission accidentally becomes process execution through shell redirection. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "shell-injection",
    "cwe": "CWE-78",
    "path": "src/DispatchLog.vb",
    "line_start": 11,
    "line_end": 11
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Windows shell interpretation of a bounded single-line log message.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Append the literal operator message and one Windows newline to a service-owned UTF-8 dispatch log.",
  "trust_boundary": "Help-desk operators may append notes but cannot execute commands under the service account.",
  "legitimate_examples": [
    {
      "input": "Message Ready & waiting",
      "expected": "Append the literal ampersand text followed by CRLF."
    },
    {
      "input": "Message containing a newline",
      "expected": "Reject without appending or launching a process."
    }
  ],
  "permitted_changes": [
    "Use a direct file append API with explicit UTF-8 encoding and serialization.",
    "Keep literal messages, one newline and error reporting."
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
    "https://learn.microsoft.com/en-us/dotnet/framework/data/adonet/configuring-parameters-and-parameter-data-types",
    "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca5359"
  ]
}
```

### Regression traps

```json
[
  "Escaping spaces does not protect cmd operators.",
  "Do not grant file path selection while removing the shell."
]
```

### Remediation constraints

```json
[
  "Use a direct file append API with explicit UTF-8 encoding and serialization.",
  "Keep literal messages, one newline and error reporting."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-visualbasic-vulnerable-03",
  "prior_case_id": "visualbasic-certificate-callback-vulnerable",
  "prior_source_sha256": "cfaa7fe4623f1c46fa5f4438f94f77095dff3e050f7d42ebaea4e650f17ab5f7",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; Visual Basic 16.9; Option Strict On",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Windows Server 2022",
  "setup": "Methods are invoked with non-null values from the described ingress; the service configuration and database connection are trusted. Windows Server 2022; C:\\Service is not writable by operators; a caller lock serializes log writes. The desired file encoding is UTF-8 without BOM."
}
```

### Split

```json
"held_out"
```

## v2-visualbasic-vulnerable-04 — A PowerShell event query embeds an untrusted application name

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `f2c5817a6c0288fbcca522c70dcc763fc32ed13605823bb8d3f0acd67ad645d5`. Protocol-2.0 case hash: `020abcd25ce48f50332025a157408cf5e1dabbee271eceb2341e2ddf7504d483`.

The provider name can close a PowerShell string in a constructed program. Passing that program with ArgumentList does not turn its embedded data into literal script arguments.

### src/EventCount.vb

```visualbasic
Option Strict On
Imports System
Imports System.Diagnostics
Public Module EventCount
    Public Function Read(application As String) As String
        If application.Length > 80 Then Throw New ArgumentException("application")
        Dim script = "(Get-WinEvent -FilterHashtable @{LogName='Application';ProviderName='" & application & "'} -ErrorAction Stop | Measure-Object).Count"
        Dim start As New ProcessStartInfo("C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe")
        start.UseShellExecute = False
        start.RedirectStandardOutput = True
        start.ArgumentList.Add("-NoProfile")
        start.ArgumentList.Add("-Command")
        start.ArgumentList.Add(script)
        Using child = Process.Start(start)
            If child Is Nothing Then Throw New InvalidOperationException("spawn")
            Dim output = child.StandardOutput.ReadToEnd()
            child.WaitForExit()
            If child.ExitCode <> 0 Then Throw New InvalidOperationException("events")
            Return output.Trim()
        End Using
    End Function
End Module
```

### Derivation

```json
{
  "group": "vb-powershell-event-filter",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "The embedded language is PowerShell hashtable syntax and pipeline evaluation, with an exact event-filter semantic requirement. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "shell-injection",
    "cwe": "CWE-78",
    "path": "src/EventCount.vb",
    "line_start": 7,
    "line_end": 7
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "PowerShell program construction with provider-name data; Windows event authorization is an external service policy.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return the count of Application-log events for one exact provider name.",
  "trust_boundary": "A support UI user controls a provider-name filter, not executable PowerShell code.",
  "legitimate_examples": [
    {
      "input": "Application Contoso Agent",
      "expected": "Count only that exact provider."
    },
    {
      "input": "Application O'Brien Worker",
      "expected": "Treat the apostrophe as provider-name data."
    }
  ],
  "permitted_changes": [
    "Use a trusted parameterized script or direct Windows event-log API, retaining exact provider matching.",
    "Preserve capture, process failure handling and a caller deadline."
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
    "https://learn.microsoft.com/en-us/dotnet/framework/data/adonet/configuring-parameters-and-parameter-data-types",
    "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca5359"
  ]
}
```

### Regression traps

```json
[
  "Replacing quotes without respecting PowerShell syntax is not a complete injection defense.",
  "Do not expand the query to all providers when parsing a difficult name."
]
```

### Remediation constraints

```json
[
  "Use a trusted parameterized script or direct Windows event-log API, retaining exact provider matching.",
  "Preserve capture, process failure handling and a caller deadline."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-visualbasic-vulnerable-04",
  "prior_case_id": "visualbasic-import-formatter-vulnerable",
  "prior_source_sha256": "8dc8a8315e17f2b25d880c62763fb59edf4441642daa4960292f3efeb058a590",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; Visual Basic 16.9; Option Strict On",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Windows Server 2022",
  "setup": "Methods are invoked with non-null values from the described ingress; the service configuration and database connection are trusted. Windows PowerShell 5.1; the service can read Application events; output is one integer and bounded by the caller."
}
```

### Split

```json
"held_out"
```

## v2-visualbasic-vulnerable-05 — TLS telemetry stream accepts every presented peer certificate

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `e3b8190f2f99e490ea39bee9ee895c7be19eca827e06270ca860705faf3945c2`. Protocol-2.0 case hash: `f087a1d39b7d881cec2fccc340ae39e70a79fa0e38e540fdbae220267041c6bc`.

The certificate callback ignores both chain and hostname errors on the SslStream actually sending telemetry. An encrypted stream is not authenticated when every certificate is accepted.

### src/TelemetryChannel.vb

```visualbasic
Option Strict On
Imports System
Imports System.Net.Sockets
Imports System.Net.Security
Imports System.Text
Public Module TelemetryChannel
    Public Sub Send(payload As String)
        If payload.Length > 2048 Then Throw New ArgumentException("payload")
        Using tcp As New TcpClient("telemetry.example.org", 443)
            Using tls As New SslStream(tcp.GetStream(), False, Function(sender, certificate, chain, errors) True)
                tls.AuthenticateAsClient("telemetry.example.org")
                Dim bytes = Encoding.UTF8.GetBytes(payload & vbLf)
                tls.Write(bytes, 0, bytes.Length)
                tls.Flush()
            End Using
        End Using
    End Sub
End Module
```

### Derivation

```json
{
  "group": "vb-raw-telemetry-stream-certificate",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Unlike HTTP examples, a directly authenticated TLS stream sends sensitive records and exposes the callback-to-write dataflow. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "tls-validation",
    "cwe": "CWE-295",
    "path": "src/TelemetryChannel.vb",
    "line_start": 10,
    "line_end": 10
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Raw TLS peer authentication with a consuming stream.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Send one bounded telemetry record to the authenticated fixed collector.",
  "trust_boundary": "The network can be intercepted; payload is service data and must not be disclosed to an impersonated collector.",
  "legitimate_examples": [
    {
      "input": "Trusted certificate for telemetry.example.org",
      "expected": "Write one UTF-8 line."
    },
    {
      "input": "Wrong-host certificate",
      "expected": "Fail authentication before writing the payload."
    }
  ],
  "permitted_changes": [
    "Use the platform validation result without bypass or remove the permissive callback.",
    "Keep the fixed hostname, encoding, record boundary and disposal."
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
    "https://learn.microsoft.com/en-us/dotnet/framework/data/adonet/configuring-parameters-and-parameter-data-types",
    "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca5359"
  ]
}
```

### Regression traps

```json
[
  "Checking certificate IsNot Nothing still accepts attacker certificates.",
  "Changing only TLS protocol version does not restore peer identity checks."
]
```

### Remediation constraints

```json
[
  "Use the platform validation result without bypass or remove the permissive callback.",
  "Keep the fixed hostname, encoding, record boundary and disposal."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-visualbasic-vulnerable-05",
  "prior_case_id": "visualbasic-digest-import-vulnerable",
  "prior_source_sha256": "bbd06bcd7ae589097afc2112046ef61fb7bcbd8e77e9583db72195f381d17bc2",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; Visual Basic 16.9; Option Strict On",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Windows Server 2022",
  "setup": "Methods are invoked with non-null values from the described ingress; the service configuration and database connection are trusted. The collector accepts a raw newline-delimited application protocol over TLS on port 443; ingress payload contains no newline. Caller enforces connect/read deadlines."
}
```

### Split

```json
"held_out"
```

## v2-visualbasic-vulnerable-06 — Partner order DOM enables a URL resolver on untrusted XML

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `fd11372227f0eead297dc947f70b8672fc577fc48a054de6bc972528bfa19bcc`. Protocol-2.0 case hash: `89b7bccc4a6ce4f8b334956141a0a6dbfc50951dd4c0827482159d9d218db27f`.

The DOM is configured to resolve external entities while loading a partner-controlled document. Validating the selected text length afterward cannot prevent the resource access.

### src/PartnerOrder.vb

```visualbasic
Option Strict On
Imports System
Imports System.Xml
Public Module PartnerOrder
    Public Function Reference(xml As String) As String
        If xml.Length > 32768 Then Throw New ArgumentException("order")
        Dim document As New XmlDocument()
        document.XmlResolver = New XmlUrlResolver()
        document.LoadXml(xml)
        Dim node = document.SelectSingleNode("/order/reference")
        If node Is Nothing Then Throw New FormatException("reference")
        If node.InnerText.Length > 128 Then Throw New FormatException("reference length")
        Return node.InnerText
    End Function
End Module
```

### Derivation

```json
{
  "group": "vb-partner-dom-postvalidation",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "The case focuses on validation order after DOM expansion and the difference between configuring an unused reader and the parser actually used. Independence is a proposed classification pending human review; no effective sample size is claimed."
}
```

### Expected findings

```json
[
  {
    "family": "unsafe-xml",
    "cwe": "CWE-611",
    "path": "src/PartnerOrder.vb",
    "line_start": 8,
    "line_end": 8
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "External entity resolution on the actual DOM parser.",
  "reviewed_residual_risks": [
    "AI-authored candidate: labels, scope and independence require human review before freezing.",
    "Resource-exhaustion and caller authorization outside the stated bounded ingress are not claimed safe."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return the reference text from a bounded partner order document.",
  "trust_boundary": "A partner controls XML and may not read service-local files or request arbitrary internal URLs.",
  "legitimate_examples": [
    {
      "input": "<order><reference>PO-31</reference></order>",
      "expected": "Return PO-31."
    },
    {
      "input": "Order defining a SYSTEM entity",
      "expected": "Reject without resolving it."
    }
  ],
  "permitted_changes": [
    "Load through a reader with DTD prohibition and a null resolver.",
    "Retain required-reference and output-length validation."
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
    "https://learn.microsoft.com/en-us/dotnet/framework/data/adonet/configuring-parameters-and-parameter-data-types",
    "https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca5359"
  ]
}
```

### Regression traps

```json
[
  "Post-load validation happens after entity resolution.",
  "Removing the resolver on a different unused reader does not protect the DOM load."
]
```

### Remediation constraints

```json
[
  "Load through a reader with DTD prohibition and a null resolver.",
  "Retain required-reference and output-length validation."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-visualbasic-vulnerable-06",
  "prior_case_id": "visualbasic-xml-settings-vulnerable",
  "prior_source_sha256": "854597e8800cc46eee41080cf7abd9490e08b0c5e3a18b230a5bb194e08ab155",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": ".NET 8.0; Visual Basic 16.9; Option Strict On",
  "libraries": [
    ".NET 8 BCL"
  ],
  "platform": "Windows Server 2022",
  "setup": "Methods are invoked with non-null values from the described ingress; the service configuration and database connection are trusted. .NET 8 XmlDocument; no DTD is required by the order protocol; the service may reach private network resources."
}
```

### Split

```json
"held_out"
```

