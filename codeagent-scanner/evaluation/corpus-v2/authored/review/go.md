# go — authored corpus-v2 candidates

AI-authored, pending independent human review. Static validation is separate evidence, not approval. Source is quoted for inspection and must not be executed.

Review the corpus-level context and checklist in the [complete unsigned manifest](../unsigned-review-manifest.json) alongside each case.

## v2-go-safe-01 — allocation-change-bound-transaction

Proposed label: **safe**. Human review: **pending**.

Source hash: `ce96b1061eb2e47dbbef3dad056a8d4787ba007a048e30772225fa3f39e613f0`. Protocol-2.0 case hash: `9eb9461cac5b0a3f1504ed742690dd1991d9e0c7fa5726ed2b6455d6427f48f0`.

Both values are separated from query syntax. Result count and commit behavior preserve a real update contract, and the driver/placeholder compatibility is explicit.

### allocation.go

```go
package allocation
import (
    "context"
    "database/sql"
    "fmt"
)
func Rename(ctx context.Context, db *sql.DB, id int64, display string) error {
    if len(display)>100 { return fmt.Errorf("display too long") }
    tx, err := db.BeginTx(ctx,nil)
    if err!=nil { return err }
    defer tx.Rollback()
    result, err := tx.ExecContext(ctx,"UPDATE allocations SET display_name=$1 WHERE id=$2",display,id)
    if err!=nil { return err }
    count,err:=result.RowsAffected()
    if err!=nil { return err }; if count!=1 { return fmt.Errorf("unknown allocation") }
    return tx.Commit()
}
```

### Derivation

```json
{
  "group": "allocation-change-bound-transaction",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around rename exactly one authorized allocation atomically using a literal display string. Boundary: Untrusted name is bound using PostgreSQL-compatible placeholders; numeric ID is also bound. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Authorization is provided by handler and tenant-scoped view; this function does not infer ownership from the display text."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Rename exactly one authorized allocation atomically using a literal display string.",
  "trust_boundary": "Untrusted name is bound using PostgreSQL-compatible placeholders; numeric ID is also bound.",
  "legitimate_examples": [
    {
      "input": "display=Ops team's pool",
      "expected": "Exact display stored"
    },
    {
      "input": "Unknown authorized-view ID",
      "expected": "Error and rollback"
    }
  ],
  "permitted_changes": [
    "Retain bound parameters, rollback on errors and exactly-one-row semantics."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not strip punctuation, commit after failed updates, or treat zero changed rows as success."
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
    "https://go.dev/doc/database/execute-transactions"
  ]
}
```

### Regression traps

```json
[
  "Do not strip punctuation, commit after failed updates, or treat zero changed rows as success."
]
```

### Remediation constraints

```json
[
  "Rename exactly one authorized allocation atomically using a literal display string.",
  "Retain bound parameters, rollback on errors and exactly-one-row semantics.",
  "Do not strip punctuation, commit after failed updates, or treat zero changed rows as success."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-go-safe-01",
  "prior_case_id": "go-order-query-safe",
  "prior_source_sha256": "f77c19bd88a6c13a319119ec6fd83f16d7267b14985e07fb4972901f52d13433",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Go 1.24.2, Linux amd64",
  "libraries_platform_setup": "pgx/v5.7.2 database/sql driver, PostgreSQL16. Handler has authorized allocation id for the current tenant; database view enforces tenant ownership. Empty display labels are permitted."
}
```

### Split

```json
"held_out"
```

## v2-go-safe-02 — private-ca-metrics-client

Proposed label: **safe**. Human review: **pending**.

Source hash: `a247f97776e7472eab3e75e6d92e844495afb6e5485b8877f1f7c6bccb4d8c46`. Protocol-2.0 case hash: `2ed86e04ccbd2a5af09d40f64fc3b2129022b4a270160bdd8c4ef2e70b1000aa`.

A custom root store is not disabled validation. Standard hostname verification remains enabled and redirects are refused. Internal address use is an authorized fixed operation.

### metrics.go

```go
package metrics
import (
    "crypto/tls"
    "crypto/x509"
    "fmt"
    "io"
    "net/http"
    "time"
)
func Read(caPEM []byte) ([]byte,error) {
    roots:=x509.NewCertPool()
    if !roots.AppendCertsFromPEM(caPEM) { return nil,fmt.Errorf("invalid configured CA") }
    transport:=&http.Transport{TLSClientConfig:&tls.Config{RootCAs:roots,MinVersion:tls.VersionTLS12}}
    defer transport.CloseIdleConnections()
    client:=&http.Client{Transport:transport,Timeout:3*time.Second,
        CheckRedirect:func(_ *http.Request,_ []*http.Request) error { return http.ErrUseLastResponse }}
    response,err:=client.Get("https://metrics.internal.example.org/snapshot")
    if err!=nil { return nil,err }; defer response.Body.Close()
    if response.StatusCode!=200 { return nil,fmt.Errorf("metrics unavailable") }
    return io.ReadAll(io.LimitReader(response.Body,8192))
}
```

### Derivation

```json
{
  "group": "private-ca-metrics-client",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around read a bounded metrics snapshot authenticated to the configured private ca. Boundary: Network peer must validate to the operator CA and requested hostname; callers do not choose destination or trust roots. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "This is not an arbitrary SSRF fetch: both origin and private trust anchor are deployment-controlled."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Read a bounded metrics snapshot authenticated to the configured private CA.",
  "trust_boundary": "Network peer must validate to the operator CA and requested hostname; callers do not choose destination or trust roots.",
  "legitimate_examples": [
    {
      "input": "Valid private-CA server",
      "expected": "Returns snapshot bytes"
    },
    {
      "input": "Different/self-signed certificate",
      "expected": "TLS error"
    }
  ],
  "permitted_changes": [
    "Retain hostname verification and fail closed on invalid CA configuration."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not set InsecureSkipVerify to accommodate a private CA or accept CA bytes from a request."
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
    "https://pkg.go.dev/crypto/tls#Config"
  ]
}
```

### Regression traps

```json
[
  "Do not set InsecureSkipVerify to accommodate a private CA or accept CA bytes from a request."
]
```

### Remediation constraints

```json
[
  "Read a bounded metrics snapshot authenticated to the configured private CA.",
  "Retain hostname verification and fail closed on invalid CA configuration.",
  "Do not set InsecureSkipVerify to accommodate a private CA or accept CA bytes from a request."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-go-safe-02",
  "prior_case_id": "go-custom-transport-safe",
  "prior_source_sha256": "b7b8ed3786ae324cf711b69cc4a4a8a841b77a3a4b70ecd63206ab39b35afb80",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Go 1.24.2, Linux amd64",
  "libraries_platform_setup": "Trusted deployment supplies a private CA PEM, not request data. Internal hostname has a certificate issued by that CA and matching SAN. This server is intentionally authorized to contact the internal metrics service."
}
```

### Split

```json
"held_out"
```

## v2-go-safe-03 — public-manual-rooted-file-reader

Proposed label: **safe**. Human review: **pending**.

Source hash: `f0be56d72ab8d55cd1969aa47d32a442ce1743e82df591caae6223d8b8135c18`. Protocol-2.0 case hash: `bc7202c216f8b28dfb2c3418037fc3deadc6f117d2925b4afc52e8cb7ab1feef`.

The root handle enforces containment during path traversal. This preserves a legitimate relative-file interface without inventing a one-item allow-list or relying on a racy prefix check.

### manual.go

```go
package manual
import (
    "io"
    "os"
)
func Read(rootDirectory string, relativeName string) ([]byte,error) {
    root,err:=os.OpenRoot(rootDirectory)
    if err!=nil { return nil,err }; defer root.Close()
    file,err:=root.Open(relativeName)
    if err!=nil { return nil,err }; defer file.Close()
    info,err:=file.Stat()
    if err!=nil { return nil,err }
    if !info.Mode().IsRegular() { return nil,os.ErrInvalid }
    return io.ReadAll(io.LimitReader(file,65536))
}
```

### Derivation

```json
{
  "group": "public-manual-rooted-file-reader",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around read a bounded relative manual file, including nested paths, under the configured public root. Boundary: Untrusted path resolution is constrained by os.Root, including parent/symlink escapes. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "The root is entirely public and immutable; directory authorization and filesystem mount ownership are stated prerequisites."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Read a bounded relative manual file, including nested paths, under the configured public root.",
  "trust_boundary": "Untrusted path resolution is constrained by os.Root, including parent/symlink escapes.",
  "legitimate_examples": [
    {
      "input": "guide/install.txt",
      "expected": "Bytes of that manual file"
    },
    {
      "input": "../private/key",
      "expected": "Path escape rejected"
    }
  ],
  "permitted_changes": [
    "Retain os.Root containment and regular-file checks."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not substitute lexical cleaning alone or allow absolute paths outside the manual tree."
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
    "https://go.dev/blog/osroot"
  ]
}
```

### Regression traps

```json
[
  "Do not substitute lexical cleaning alone or allow absolute paths outside the manual tree."
]
```

### Remediation constraints

```json
[
  "Read a bounded relative manual file, including nested paths, under the configured public root.",
  "Retain os.Root containment and regular-file checks.",
  "Do not substitute lexical cleaning alone or allow absolute paths outside the manual tree."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-go-safe-03",
  "prior_case_id": "go-url-fetcher-safe",
  "prior_source_sha256": "933e75d7c3d10d387e95294517e8843081adbe7b231e9cb78d2c2e016188c0bf",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Go 1.24.2, Linux amd64",
  "libraries_platform_setup": "Go1.24 os.Root API; rootDirectory is an immutable public manual tree selected by server configuration. Every file within it is public. Mount/device namespaces are trusted; no privileged special files exist inside it."
}
```

### Split

```json
"held_out"
```

## v2-go-safe-04 — literal-lines-sort-process-input

Proposed label: **safe**. Human review: **pending**.

Source hash: `44508fed2673169c851caf1363c434c17149e8669d8e083271963fc0e522e198`. Protocol-2.0 case hash: `c15ba851250a3f8524c60b3254a8339141a00a815010304ef053517c83a7b3e7`.

Input punctuation cannot become options or shell grammar because it is process data on stdin. Timeout and bounds also apply to the actual process.

### sort.go

```go
package display
import (
    "bytes"
    "context"
    "fmt"
    "os/exec"
    "strings"
    "time"
)
func Sort(lines []string) ([]byte,error) {
    if len(lines)>50 { return nil,fmt.Errorf("too many lines") }
    for _,line:=range lines { if len(line)>80 || strings.ContainsAny(line,"\x00\n") { return nil,fmt.Errorf("invalid line") } }
    ctx,cancel:=context.WithTimeout(context.Background(),time.Second); defer cancel()
    command:=exec.CommandContext(ctx,"/usr/bin/sort")
    command.Env=[]string{"LC_ALL=C"}
    payload:=strings.Join(lines,"\n")
    if len(lines)>0 { payload+="\n" }
    command.Stdin=bytes.NewBufferString(payload)
    return command.Output()
}
```

### Derivation

```json
{
  "group": "literal-lines-sort-process-input",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around sort literal user labels in byte order and return newline-delimited output. Boundary: Labels flow only to child stdin; no user-controlled executable, option or shell source exists. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Control characters are explicitly rejected; line text is displayed as text by the caller."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Sort literal user labels in byte order and return newline-delimited output.",
  "trust_boundary": "Labels flow only to child stdin; no user-controlled executable, option or shell source exists.",
  "legitimate_examples": [
    {
      "input": "[-r, beta, alpha]",
      "expected": "-r\nalpha\nbeta\n"
    },
    {
      "input": "Empty list",
      "expected": "Empty output"
    }
  ],
  "permitted_changes": [
    "Preserve C-locale sort order, duplicates and exit errors."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not treat a leading dash as an option, deduplicate labels, or switch to locale-dependent collation."
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
    "https://pkg.go.dev/os/exec"
  ]
}
```

### Regression traps

```json
[
  "Do not treat a leading dash as an option, deduplicate labels, or switch to locale-dependent collation."
]
```

### Remediation constraints

```json
[
  "Sort literal user labels in byte order and return newline-delimited output.",
  "Preserve C-locale sort order, duplicates and exit errors.",
  "Do not treat a leading dash as an option, deduplicate labels, or switch to locale-dependent collation."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-go-safe-04",
  "prior_case_id": "go-diagnostic-command-safe",
  "prior_source_sha256": "777188587952c275e6f790b049acf0e2311c32c3edaac5dcbd952841ceebded1",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Go 1.24.2, Linux amd64",
  "libraries_platform_setup": "GNU coreutils9.5 sort; trusted executable; input is a bounded list of lines with no NUL/newlines. Locale is deliberately C for stable byte ordering."
}
```

### Split

```json
"held_out"
```

## v2-go-safe-05 — typed-public-feed-xml-decoder

Proposed label: **safe**. Human review: **pending**.

Source hash: `2717a29d619fbf47da7908314a7da4f49f2c63829cd48c0e76de25ee904eb01b`. Protocol-2.0 case hash: `4f060941bc5446a31c67e8aa0f38b9d605620aca45fbaf744368f4392e23db93`.

Standard encoding/xml decoding into fixed fields does not activate arbitrary classes or resolve external resources. XML use alone does not imply Java-style XXE behavior.

### feed.go

```go
package feed
import (
    "encoding/xml"
    "fmt"
)
type Announcement struct { Title string `xml:"title"`; Category string `xml:"category"` }
type Feed struct { Items []Announcement `xml:"item"` }
func Read(data []byte) ([]Announcement,error) {
    if len(data)>32768 { return nil,fmt.Errorf("feed too large") }
    var value Feed
    if err:=xml.Unmarshal(data,&value); err!=nil { return nil,err }
    if len(value.Items)>30 { return nil,fmt.Errorf("too many items") }
    for _,item:=range value.Items { if len(item.Title)>200 { return nil,fmt.Errorf("title too long") } }
    return value.Items,nil
}
```

### Derivation

```json
{
  "group": "typed-public-feed-xml-decoder",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around decode bounded public announcement titles/categories into a fixed go struct. Boundary: Network XML is data for the standard decoder, with no user-selected types or external entity resolver. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Unknown fields may be ignored by this documented feed format; the consumer does not derive privileged actions from them."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Decode bounded public announcement titles/categories into a fixed Go struct.",
  "trust_boundary": "Network XML is data for the standard decoder, with no user-selected types or external entity resolver.",
  "legitimate_examples": [
    {
      "input": "<feed><item><title>A&amp;B</title></item></feed>",
      "expected": "One title A&B"
    },
    {
      "input": "Unrecognized external entity reference",
      "expected": "Decode error; no resource fetch"
    }
  ],
  "permitted_changes": [
    "Retain fixed data types, bounded input and no custom external-resource callbacks."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not add an unrestricted entity resolver to make unsupported feeds parse."
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
    "https://pkg.go.dev/encoding/xml"
  ]
}
```

### Regression traps

```json
[
  "Do not add an unrestricted entity resolver to make unsupported feeds parse."
]
```

### Remediation constraints

```json
[
  "Decode bounded public announcement titles/categories into a fixed Go struct.",
  "Retain fixed data types, bounded input and no custom external-resource callbacks.",
  "Do not add an unrestricted entity resolver to make unsupported feeds parse."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-go-safe-05",
  "prior_case_id": "go-artifact-reader-safe",
  "prior_source_sha256": "9b280ff86df54d27396abb204fe6f381a14a9b551e17cfaea587994a38e8e653",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Go 1.24.2, Linux amd64",
  "libraries_platform_setup": "encoding/xml standard implementation, no custom Entity map, CharsetReader or unmarshaler. Feed text is public and displayed with escaping; unknown entities cause decoding error, and the parser does not fetch external DTDs."
}
```

### Split

```json
"held_out"
```

## v2-go-safe-06 — avatar-html-template-autoescaping

Proposed label: **safe**. Human review: **pending**.

Source hash: `e76c9720a3c313e98ab6f32a64df7bf14dfdc6381337b0aa4acc597b81ca35e3`. Protocol-2.0 case hash: `6a9853144fae6eab54c4248fb5cdd04d6c43815204b73452dd0d5a603f74b244`.

The template structure is trusted and html/template escapes ordinary strings. There is no evaluation of user template syntax or safe-type override.

### card.go

```go
package cards
import (
    "bytes"
    "fmt"
    "html/template"
)
var card=template.Must(template.New("card").Parse(`<article><h2>{{.Name}}</h2><p>{{.Bio}}</p></article>`))
type Person struct { Name string; Bio string }
func Render(person Person) (string,error) {
    if len(person.Name)>100 || len(person.Bio)>500 { return "",fmt.Errorf("profile too large") }
    var output bytes.Buffer
    if err:=card.Execute(&output,person); err!=nil { return "",err }
    return output.String(),nil
}
```

### Derivation

```json
{
  "group": "avatar-html-template-autoescaping",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around render a public profile card while treating name and bio as text. Boundary: User profile content enters template text positions with contextual automatic escaping. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "No dynamic URL/JavaScript/CSS context exists; browser delivery must preserve the stated text/html semantics."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Render a public profile card while treating name and bio as text.",
  "trust_boundary": "User profile content enters template text positions with contextual automatic escaping.",
  "legitimate_examples": [
    {
      "input": "Name <admin>",
      "expected": "Visible literal <admin>, no element creation"
    },
    {
      "input": "Bio containing a script tag",
      "expected": "Escaped text, no script execution"
    }
  ],
  "permitted_changes": [
    "Preserve automatic escaping and fixed template structure."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not cast user content to template.HTML, switch to text/template, or pre-escape into double-encoded output."
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
    "https://pkg.go.dev/html/template"
  ]
}
```

### Regression traps

```json
[
  "Do not cast user content to template.HTML, switch to text/template, or pre-escape into double-encoded output."
]
```

### Remediation constraints

```json
[
  "Render a public profile card while treating name and bio as text.",
  "Preserve automatic escaping and fixed template structure.",
  "Do not cast user content to template.HTML, switch to text/template, or pre-escape into double-encoded output."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-go-safe-06",
  "prior_case_id": "go-checksum-authentication-safe",
  "prior_source_sha256": "79c3561efd454f080b8f90fa74d3892ba857513e2b7323d7a31b9266701fe71a",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Go 1.24.2, Linux amd64",
  "libraries_platform_setup": "Fixed application-owned html/template; user strings stay ordinary string values, never template.HTML. HTTP caller serves the resulting document as text/html with UTF-8."
}
```

### Split

```json
"held_out"
```

## v2-go-vulnerable-01 — tenant-search-json-array-sql-fragments

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `650d789b4553555f4015bb5e1cce198cd2b91496e4e2eb662a47fc1cb62d8f64`. Protocol-2.0 case hash: `235dc681ebd5b9ae29f14ea82c33321b5a666256f1ef9f1b4809db190fd1ec76`.

JSON decoding and wrapping values in single quotes do not escape SQL syntax. A malicious array member can change the IN predicate even when the list length and request size are bounded.

### search.go

```go
package catalog
import (
    "database/sql"
    "encoding/json"
    "net/http"
    "strings"
)
type Search struct { DB *sql.DB }
func (s Search) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    var request struct { Codes []string `json:"codes"` }
    r.Body = http.MaxBytesReader(w, r.Body, 4096)
    if json.NewDecoder(r.Body).Decode(&request) != nil || len(request.Codes) > 20 {
        http.Error(w, "invalid request", 400); return
    }
    quoted := make([]string, 0, len(request.Codes))
    for _, code := range request.Codes { quoted = append(quoted, "'"+code+"'") }
    if len(quoted) == 0 { w.WriteHeader(204); return }
    query := "SELECT name FROM catalog WHERE code IN (" + strings.Join(quoted, ",") + ") ORDER BY code"
    rows, err := s.DB.QueryContext(r.Context(), query)
    if err != nil { http.Error(w, "query failed", 500); return }
    defer rows.Close()
    names := []string{}
    for rows.Next() { var name string; if rows.Scan(&name) != nil { http.Error(w,"read failed",500);return }; names=append(names,name) }
    if rows.Err()!=nil { http.Error(w,"read failed",500);return }
    w.Header().Set("Content-Type","application/json")
    json.NewEncoder(w).Encode(names)
}
```

### Derivation

```json
{
  "group": "tenant-search-json-array-sql-fragments",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around resolve a bounded json list of catalog codes to names ordered by code. Boundary: Decoded JSON array members become quoted SQL fragments without binding. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "sql-injection",
    "cwe": "CWE-89",
    "path": "search.go"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Tenant isolation is in the view; incorrect membership remains a source vulnerability even under a read-only role."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Resolve a bounded JSON list of catalog codes to names ordered by code.",
  "trust_boundary": "Decoded JSON array members become quoted SQL fragments without binding.",
  "legitimate_examples": [
    {
      "input": "{codes:[A-7,B-2]}",
      "expected": "Matching names in code order"
    },
    {
      "input": "{codes:[author's-kit]}",
      "expected": "Exact apostrophe-containing code supported"
    }
  ],
  "permitted_changes": [
    "Construct placeholders for the bounded list and bind every code using the configured PostgreSQL driver."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not flatten all codes into one parameter, discard apostrophes, or change the empty-list204 behavior."
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
    "https://go.dev/doc/database/sql-injection"
  ]
}
```

### Regression traps

```json
[
  "Do not flatten all codes into one parameter, discard apostrophes, or change the empty-list204 behavior."
]
```

### Remediation constraints

```json
[
  "Resolve a bounded JSON list of catalog codes to names ordered by code.",
  "Construct placeholders for the bounded list and bind every code using the configured PostgreSQL driver.",
  "Do not flatten all codes into one parameter, discard apostrophes, or change the empty-list204 behavior."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-go-vulnerable-01",
  "prior_case_id": "go-order-query-vulnerable",
  "prior_source_sha256": "1e162f40ede1f3310ee6f660c3bc00696a942b54b5f548b6e368ff268f517075",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Go 1.24.2, Linux amd64",
  "libraries_platform_setup": "database/sql with pgx/v5.7.2 stdlib driver and PostgreSQL16. catalog(code text,name text) is a tenant-scoped read-only view. HTTP routing attaches this handler to POST /lookup."
}
```

### Split

```json
"held_out"
```

## v2-go-vulnerable-02 — maintenance-api-optional-client-certificate

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `0e3c1bd7699fd3328bbd9dcdfffab7b77bbac0e5a79fe19d08a57999ef666f7d`. Protocol-2.0 case hash: `5dfc39743244d8f5a2f7befcf43a347426c9c55ef25febb4a1bfdbc7b0ea2a86`.

RequestClientCert requests a certificate but does not authenticate its chain. PeerCertificates presence is not equivalent to a verified client identity, so a self-signed certificate passes the handler check.

### server.go

```go
package maintenance
import (
    "crypto/tls"
    "crypto/x509"
    "fmt"
    "net/http"
)
func Server(cert tls.Certificate, clientCA *x509.CertPool) *http.Server {
    handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        if r.TLS == nil || len(r.TLS.PeerCertificates) == 0 {
            http.Error(w, "client certificate required", http.StatusUnauthorized); return
        }
        fmt.Fprint(w, "maintenance-authorized")
    })
    return &http.Server{
        Addr: ":8443", Handler: handler,
        TLSConfig: &tls.Config{
            MinVersion: tls.VersionTLS12,
            Certificates: []tls.Certificate{cert}, ClientCAs: clientCA,
            ClientAuth: tls.RequestClientCert,
        },
    }
}
func Serve(cert tls.Certificate, roots *x509.CertPool) error {
    return Server(cert, roots).ListenAndServeTLS("", "")
}
```

### Derivation

```json
{
  "group": "maintenance-api-optional-client-certificate",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around serve a maintenance authorization response only to clients certified by the configured client ca. Boundary: Handler trusts certificate presence, while RequestClientCert does not require verification to ClientCAs. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "tls-validation",
    "cwe": "CWE-295",
    "path": "server.go"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "This is inbound mutual-TLS authorization, not an outbound InsecureSkipVerify template. Server certificate verification by legitimate clients remains intact."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Serve a maintenance authorization response only to clients certified by the configured client CA.",
  "trust_boundary": "Handler trusts certificate presence, while RequestClientCert does not require verification to ClientCAs.",
  "legitimate_examples": [
    {
      "input": "Valid configured-CA client",
      "expected": "maintenance-authorized"
    },
    {
      "input": "No client certificate",
      "expected": "Rejected"
    }
  ],
  "permitted_changes": [
    "Require and verify client certificates against the configured CA before the handler authorizes them."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not replace mTLS with presence checks, authorize empty chains, or accidentally require the server CA to equal the client CA."
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
    "https://pkg.go.dev/crypto/tls#ClientAuthType"
  ]
}
```

### Regression traps

```json
[
  "Do not replace mTLS with presence checks, authorize empty chains, or accidentally require the server CA to equal the client CA."
]
```

### Remediation constraints

```json
[
  "Serve a maintenance authorization response only to clients certified by the configured client CA.",
  "Require and verify client certificates against the configured CA before the handler authorizes them.",
  "Do not replace mTLS with presence checks, authorize empty chains, or accidentally require the server CA to equal the client CA."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-go-vulnerable-02",
  "prior_case_id": "go-custom-transport-vulnerable",
  "prior_source_sha256": "ce6058eb4f6de90e053c36e6d288b28f06df5a4c3ce74802d3d38b36fb5bb6ba",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Go 1.24.2, Linux amd64",
  "libraries_platform_setup": "Trusted server TLS certificate and intended client CA are supplied by deployment. An attacker can reach port8443 and present an arbitrary self-signed client certificate. All CA-issued clients are authorized; no additional identity ACL is required."
}
```

### Split

```json
"held_out"
```

## v2-go-vulnerable-03 — trusted-image-origin-redirect-following

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `45005fe52f11b17999afe020c15096b90790ed3384670f20b7fed8fbea92bb87`. Protocol-2.0 case hash: `5427bf48b966ff996057ca68b2f2a4abab47cf1a8e6ad2d4fb62a31c2732f5ad`.

The default client follows redirects after the initial validation. The declared image redirect endpoint permits a tenant to pivot the privileged fetch to a private HTTP URL; initial TLS does not constrain the next hop.

### preview.go

```go
package preview
import (
    "fmt"
    "io"
    "net/http"
    "net/url"
    "time"
)
func Fetch(raw string) ([]byte, error) {
    target, err := url.Parse(raw)
    if err != nil || target.Scheme != "https" || target.Host != "images.example.org" || target.User != nil {
        return nil, fmt.Errorf("image origin required")
    }
    client := &http.Client{Timeout: 3*time.Second}
    response, err := client.Get(target.String())
    if err != nil { return nil, err }
    defer response.Body.Close()
    if response.StatusCode != 200 { return nil, fmt.Errorf("unexpected status") }
    return io.ReadAll(io.LimitReader(response.Body, 65536))
}
```

### Derivation

```json
{
  "group": "trusted-image-origin-redirect-following",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around return a bounded preview from the configured image origin. Boundary: The initial URL is host-checked, but the standard HTTP client follows redirects to unchecked destinations. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "ssrf",
    "cwe": "CWE-918",
    "path": "preview.go"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Trusted DNS for the initial configured host is assumed; this candidate isolates the redirect trust transition rather than prefix matching."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Return a bounded preview from the configured image origin.",
  "trust_boundary": "The initial URL is host-checked, but the standard HTTP client follows redirects to unchecked destinations.",
  "legitimate_examples": [
    {
      "input": "https://images.example.org/a.png",
      "expected": "Preview bytes from image service"
    },
    {
      "input": "Same-origin relative redirect",
      "expected": "Preview remains supported if destination policy allows"
    }
  ],
  "permitted_changes": [
    "Disable redirects or revalidate every hop against the approved destination policy, including scheme and resolved address behavior."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not simply recheck the original URL or return the URL string instead of preview bytes."
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
    "https://pkg.go.dev/net/http#Client"
  ]
}
```

### Regression traps

```json
[
  "Do not simply recheck the original URL or return the URL string instead of preview bytes."
]
```

### Remediation constraints

```json
[
  "Return a bounded preview from the configured image origin.",
  "Disable redirects or revalidate every hop against the approved destination policy, including scheme and resolved address behavior.",
  "Do not simply recheck the original URL or return the URL string instead of preview bytes."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-go-vulnerable-03",
  "prior_case_id": "go-url-fetcher-vulnerable",
  "prior_source_sha256": "0f0fa57bbd6d6e4fbd34ea12e2b175af138c55fb24bc0ad81c78e80c393ce4e6",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Go 1.24.2, Linux amd64",
  "libraries_platform_setup": "The public image service supports /redirect?to=... with an arbitrary Location for legacy delivery. Server network can reach private HTTP management addresses. Users may preview images from the published origin but may not access private services."
}
```

### Split

```json
"held_out"
```

## v2-go-vulnerable-04 — support-bundle-journal-shell-window

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `6d56cb9bffd5e986c23babcf57d31b30dbfa26622534878f3a0db93aac72886c`. Protocol-2.0 case hash: `8b88abdeea18dd853df325e2a7f069efccaf573701878c370cbfbf70cb77a903`.

The shell parses a concatenated command before the trusted journal tool can interpret the time expression. A request timeout limits duration, not injected command execution.

### journal.go

```go
package support
import (
    "context"
    "fmt"
    "os/exec"
    "time"
)
func Collect(since string) ([]byte, error) {
    if len(since)>80 { return nil, fmt.Errorf("time expression too long") }
    ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
    defer cancel()
    command := "journalctl --no-pager --unit=myapp --since='"+since+"'"
    return exec.CommandContext(ctx, "/bin/sh", "-c", command).Output()
}
```

### Derivation

```json
{
  "group": "support-bundle-journal-shell-window",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around collect the application journal since a requested time expression. Boundary: Support form text becomes a shell single-quoted argument before journalctl processes it. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "shell-injection",
    "cwe": "CWE-78",
    "path": "journal.go"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Journal output has a deployment retention/size bound; process timeout is explicit. Time-expression validation is distinct from shell escaping."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Collect the application journal since a requested time expression.",
  "trust_boundary": "Support form text becomes a shell single-quoted argument before journalctl processes it.",
  "legitimate_examples": [
    {
      "input": "since=2026-09-01 09:30:00",
      "expected": "Journal records since that instant"
    },
    {
      "input": "since=2 hours ago",
      "expected": "Preserve supported natural-language time syntax"
    }
  ],
  "permitted_changes": [
    "Invoke journalctl directly with separate argv entries and keep timeout/cancellation."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not remove spaces from supported date expressions, lose command errors, or broaden the journal unit."
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
    "https://pkg.go.dev/os/exec"
  ]
}
```

### Regression traps

```json
[
  "Do not remove spaces from supported date expressions, lose command errors, or broaden the journal unit."
]
```

### Remediation constraints

```json
[
  "Collect the application journal since a requested time expression.",
  "Invoke journalctl directly with separate argv entries and keep timeout/cancellation.",
  "Do not remove spaces from supported date expressions, lose command errors, or broaden the journal unit."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-go-vulnerable-04",
  "prior_case_id": "go-diagnostic-command-vulnerable",
  "prior_source_sha256": "af601c9d9d0e3a1e7854db5a6703707bd5cf25a500a3870e3c1ed5a0d46e4b46",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Go 1.24.2, Linux amd64",
  "libraries_platform_setup": "systemd255 journalctl; service account can read only the application journal but also has writable application state. Support users may request natural-language journal start times, never shell programs."
}
```

### Split

```json
"held_out"
```

## v2-go-vulnerable-05 — theme-asset-write-relative-manifest

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `d07fe69f48bf4c3b3a843b8bc602f8f5dc96599890c8a1bedc0c79ddccde0ef9`. Protocol-2.0 case hash: `1869fd6fc52c43c65f5ab1f132a79fe82522236a161b027cff3fa3650b7235e4`.

filepath.Join cleans parent components but does not establish authorization to the resulting path. A traversal name can overwrite outside the fresh theme directory.

### assets.go

```go
package themes
import (
    "fmt"
    "os"
    "path/filepath"
)
type Asset struct { Name string; Bytes []byte }
func Install(root string, assets []Asset) error {
    if len(assets)>20 { return fmt.Errorf("too many assets") }
    for _, asset := range assets {
        if len(asset.Bytes)>32768 { return fmt.Errorf("asset too large") }
        target := filepath.Join(root, asset.Name)
        if err := os.MkdirAll(filepath.Dir(target), 0700); err != nil { return err }
        if err := os.WriteFile(target, asset.Bytes, 0600); err != nil { return err }
    }
    return nil
}
```

### Derivation

```json
{
  "group": "theme-asset-write-relative-manifest",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around install bounded named theme assets while preserving subdirectories. Boundary: Manifest-relative paths are normalized but not checked for containment before filesystem writes. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "path-traversal",
    "cwe": "CWE-22",
    "path": "assets.go"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Fresh private root excludes a pre-existing symlink attacker; concurrent writable ancestors are not part of the trusted deployment."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Install bounded named theme assets while preserving subdirectories.",
  "trust_boundary": "Manifest-relative paths are normalized but not checked for containment before filesystem writes.",
  "legitimate_examples": [
    {
      "input": "css/theme.css",
      "expected": "Written under the selected theme root"
    },
    {
      "input": "fonts/large print.woff",
      "expected": "Nested spaces preserved"
    }
  ],
  "permitted_changes": [
    "Use a root-constrained filesystem API or verified containment with safe symlink handling and reject the entire invalid import."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not flatten nested assets or remove all parent-component substrings and assume containment."
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
    "https://pkg.go.dev/os#OpenRoot",
    "https://pkg.go.dev/path/filepath#Join"
  ]
}
```

### Regression traps

```json
[
  "Do not flatten nested assets or remove all parent-component substrings and assume containment."
]
```

### Remediation constraints

```json
[
  "Install bounded named theme assets while preserving subdirectories.",
  "Use a root-constrained filesystem API or verified containment with safe symlink handling and reject the entire invalid import.",
  "Do not flatten nested assets or remove all parent-component substrings and assume containment."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-go-vulnerable-05",
  "prior_case_id": "go-artifact-reader-vulnerable",
  "prior_source_sha256": "5486b33d2316a3ab3b0e22de017977f3c27c8f9e34ead290643f880c4cdeb5dd",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Go 1.24.2, Linux amd64",
  "libraries_platform_setup": "root is a fresh server-owned theme directory under /srv/themes; an untrusted theme publisher supplies decoded manifest names/content. No pre-existing symlinks inside root, but sibling themes and server state must remain protected."
}
```

### Split

```json
"held_out"
```

## v2-go-vulnerable-06 — password-reset-predictable-prng

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `e51b38c4c381ba25bf0bf1107194e8df1f29d81dc13b2f72a53a39d66ed25ea7`. Protocol-2.0 case hash: `ab40eff0f3f5a4b37be22e9e2f717b8523aa8040e1e4115d49af6783b09f1bd3`.

The fixed seed produces a reproducible sequence, permitting prediction without controlling email. Mutexes and one-time deletion do not provide unpredictability.

### reset.go

```go
package accounts
import (
    "fmt"
    "math/rand"
    "sync"
)
type ResetTokens struct { mu sync.Mutex; random *rand.Rand; owners map[string]string }
func NewResetTokens() *ResetTokens {
    return &ResetTokens{random: rand.New(rand.NewSource(42)), owners: make(map[string]string)}
}
func (s *ResetTokens) Issue(account string) string {
    s.mu.Lock(); defer s.mu.Unlock()
    token := fmt.Sprintf("%016x", s.random.Uint64())
    s.owners[token] = account
    return token
}
func (s *ResetTokens) Redeem(token string) (string, bool) {
    s.mu.Lock(); defer s.mu.Unlock()
    owner, ok := s.owners[token]
    if ok { delete(s.owners,token) }
    return owner,ok
}
```

### Derivation

```json
{
  "group": "password-reset-predictable-prng",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around issue unguessable one-time password-reset tokens mapped to an account. Boundary: A public bearer token derives from a deterministic fixed-seed non-cryptographic generator. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "insecure-randomness",
    "cwe": "CWE-338",
    "path": "reset.go"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Account lookup and email delivery are trusted; the defect is bearer-token entropy, not delivery-channel compromise."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Issue unguessable one-time password-reset tokens mapped to an account.",
  "trust_boundary": "A public bearer token derives from a deterministic fixed-seed non-cryptographic generator.",
  "legitimate_examples": [
    {
      "input": "Issue for account alice, redeem emitted token",
      "expected": "Returns alice once"
    },
    {
      "input": "Second redemption of same token",
      "expected": "Returns false"
    }
  ],
  "permitted_changes": [
    "Use sufficient crypto/rand entropy, retain atomic one-time redemption and propagate entropy failures."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not replace tokens with sequential IDs, weaken expiry, or allow a token to redeem twice."
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
    "https://pkg.go.dev/math/rand",
    "https://pkg.go.dev/crypto/rand"
  ]
}
```

### Regression traps

```json
[
  "Do not replace tokens with sequential IDs, weaken expiry, or allow a token to redeem twice."
]
```

### Remediation constraints

```json
[
  "Issue unguessable one-time password-reset tokens mapped to an account.",
  "Use sufficient crypto/rand entropy, retain atomic one-time redemption and propagate entropy failures.",
  "Do not replace tokens with sequential IDs, weaken expiry, or allow a token to redeem twice."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-go-vulnerable-06",
  "prior_case_id": "go-checksum-authentication-vulnerable",
  "prior_source_sha256": "af1c595202bf676e0dc79028c1d938c6f50bb3d0639a3cd4892525c68621113e",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Go 1.24.2, Linux amd64",
  "libraries_platform_setup": "Service creates one store with NewResetTokens on startup and sends issued tokens to account email addresses. Redeem success authorizes password reset. Trusted routing expires records after15minutes; attacker knows implementation and can observe its own issued token."
}
```

### Split

```json
"held_out"
```

