# rust — authored corpus-v2 candidates

AI-authored, pending independent human review. Static validation is separate evidence, not approval. Source is quoted for inspection and must not be executed.

Review the corpus-level context and checklist in the [complete unsigned manifest](../unsigned-review-manifest.json) alongside each case.

## v2-rust-safe-01 — inventory-upsert-bound-sqlite

Proposed label: **safe**. Human review: **pending**.

Source hash: `fec9944aa9b8d7b801d27d47b152f310f0b09a29e4b8d8c1871cec191e4bbf8f`. Protocol-2.0 case hash: `09ea5d4fad41a60e9a90408cd0096213e18fe691d016806b50917a0bfaf67085`.

A nontrivial INSERT/ON CONFLICT statement remains safe because user data is bound. SQL keywords in the SKU cannot alter either insert or update behavior.

### inventory.rs

```rust
use rusqlite::{params, Connection, Result};
pub fn reserve(db: &Connection, sku: &str, amount: i64) -> Result<usize> {
    if !(1..=50).contains(&amount) || sku.len()>80 {
        return Err(rusqlite::Error::InvalidParameterName("invalid reservation".into()));
    }
    db.execute(
        "INSERT INTO reservations(sku,quantity) VALUES (?1,?2) ON CONFLICT(sku) DO UPDATE SET quantity=quantity+excluded.quantity",
        params![sku,amount],
    )
}
```

### Derivation

```json
{
  "group": "inventory-upsert-bound-sqlite",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around add a bounded reservation quantity for one exact sku using an atomic upsert. Boundary: Untrusted SKU is bound separately from a constant SQL program with a legitimate conflict-update clause. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
    "Authorization and stock accounting are separate explicit contracts; SQL execution does not concatenate SKU text."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Add a bounded reservation quantity for one exact SKU using an atomic upsert.",
  "trust_boundary": "Untrusted SKU is bound separately from a constant SQL program with a legitimate conflict-update clause.",
  "legitimate_examples": [
    {
      "input": "sku=artist's-kit, amount=2",
      "expected": "Exact SKU reservation increments by2"
    },
    {
      "input": "amount=0",
      "expected": "Error, no update"
    }
  ],
  "permitted_changes": [
    "Retain binding, atomic upsert and amount bounds."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not replace accumulation with assignment or split the operation into a racy read/write pair."
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
    "https://docs.rs/rusqlite/latest/rusqlite/struct.Connection.html#method.execute"
  ]
}
```

### Regression traps

```json
[
  "Do not replace accumulation with assignment or split the operation into a racy read/write pair."
]
```

### Remediation constraints

```json
[
  "Add a bounded reservation quantity for one exact SKU using an atomic upsert.",
  "Retain binding, atomic upsert and amount bounds.",
  "Do not replace accumulation with assignment or split the operation into a racy read/write pair."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-rust-safe-01",
  "prior_case_id": "rust-account-sqlx-safe",
  "prior_source_sha256": "440eb73c4f43c005a2fe7dc47a669bf0921e87d9b539066267a335a3cade6d15",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Rust1.83, edition2021; Linux amd64",
  "libraries_platform_setup": "rusqlite0.32.1; SQLite schema reservations(sku TEXT PRIMARY KEY,quantity INTEGER NOT NULL). Server has already authorized caller to reserve these public SKUs; this function has no payment or stock-depletion authority."
}
```

### Split

```json
"held_out"
```

## v2-rust-safe-02 — search-pagination-sqlx-bound-query

Proposed label: **safe**. Human review: **pending**.

Source hash: `a6ee78ec6c0a41083234ec50469aa36d1376e3f6a84a2d325432c676a54bba84`. Protocol-2.0 case hash: `71361d460d37a27a7576022c003b1a01940373c8dc449d0b16b6599f98ecf80f`.

The query is constant and both values are bound. Using strpos also preserves literal punctuation without a misleading wildcard-escaping contract.

### search.rs

```rust
use sqlx::{PgPool, Row};
pub async fn page(pool: &PgPool, term: &str, offset: i64) -> Result<Vec<String>, sqlx::Error> {
    if term.len()>100 || !(0..=1000).contains(&offset) { return Err(sqlx::Error::Protocol("invalid search".into())); }
    let rows=sqlx::query("SELECT title FROM public_notes WHERE strpos(title,$1)>0 ORDER BY id LIMIT 20 OFFSET $2")
        .bind(term).bind(offset).fetch_all(pool).await?;
    rows.into_iter().map(|row| row.try_get::<String,_>("title")).collect()
}
```

### Derivation

```json
{
  "group": "search-pagination-sqlx-bound-query",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around page public notes containing an exact literal substring. Boundary: User search text and offset enter PostgreSQL bound parameters, not query grammar or LIKE patterns. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
    "Only public note titles are returned and later serialized as JSON; HTML escaping belongs to the UI consumer."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Page public notes containing an exact literal substring.",
  "trust_boundary": "User search text and offset enter PostgreSQL bound parameters, not query grammar or LIKE patterns.",
  "legitimate_examples": [
    {
      "input": "term=50%_done",
      "expected": "Matches that literal substring"
    },
    {
      "input": "term=author's note",
      "expected": "Apostrophe retained as data"
    }
  ],
  "permitted_changes": [
    "Keep literal substring semantics, bounded offset and stable ID order."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not switch to wildcard LIKE matching or interpolate pagination text."
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
    "https://docs.rs/sqlx/latest/sqlx/fn.query.html"
  ]
}
```

### Regression traps

```json
[
  "Do not switch to wildcard LIKE matching or interpolate pagination text."
]
```

### Remediation constraints

```json
[
  "Page public notes containing an exact literal substring.",
  "Keep literal substring semantics, bounded offset and stable ID order.",
  "Do not switch to wildcard LIKE matching or interpolate pagination text."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-rust-safe-02",
  "prior_case_id": "rust-reqwest-certificates-safe",
  "prior_source_sha256": "6b2670e341b76874eb77d557288e8d98445c1fc69b2847f93e7d1e93c22b4420",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Rust1.83, edition2021; Linux amd64",
  "libraries_platform_setup": "sqlx0.8.3 features postgres,runtime-tokio-rustls, PostgreSQL16; public_notes(id,title) contains public text only. strpos provides literal substring matching, including percent/underscore."
}
```

### Split

```json
"held_out"
```

## v2-rust-safe-03 — bookmark-origin-display-without-fetch

Proposed label: **safe**. Human review: **pending**.

Source hash: `9c32ab32fc20384a65a779b4d792cab1da6cd3125ff86bcebc01c8a18a67e721`. Protocol-2.0 case hash: `e13441b624c94d2bb0a21251eb55948325be0761e3df44cd268fccf6acee2089`.

URL parsing is not fetching. This operation intentionally permits arbitrary HTTP bookmark origins for display, with no privileged networking sink or HTML interpretation.

### bookmark.rs

```rust
use url::Url;
pub struct BookmarkSummary { pub host:String, pub port:Option<u16>, pub path:String }
pub fn summarize(untrusted_url:&str) -> Result<BookmarkSummary,String> {
    if untrusted_url.len()>2048 { return Err("bookmark too long".into()); }
    let url=Url::parse(untrusted_url).map_err(|_|"invalid URL")?;
    if !matches!(url.scheme(),"https"|"http") { return Err("unsupported bookmark scheme".into()); }
    let host=url.host_str().ok_or("host required")?.to_owned();
    Ok(BookmarkSummary{host,port:url.port(),path:url.path().to_owned()})
}
```

### panel.rs

```rust
mod bookmark;
pub fn origin_label(text:&str) -> Result<String,String> {
    let summary=bookmark::summarize(text)?;
    Ok(match summary.port {
        Some(port)=>format!("{}:{}",summary.host,port),
        None=>summary.host,
    })
}
```

### Derivation

```json
{
  "group": "bookmark-origin-display-without-fetch",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around display the parsed origin of a user bookmark without contacting it. Boundary: Untrusted URL syntax is parsed into inert display fields and never becomes an outbound request. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
    "A separate explicit user navigation action would have its own trust model; it is absent from this panel and must not be invented by the reviewer."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Display the parsed origin of a user bookmark without contacting it.",
  "trust_boundary": "Untrusted URL syntax is parsed into inert display fields and never becomes an outbound request.",
  "legitimate_examples": [
    {
      "input": "https://notes.example.org:8443/a",
      "expected": "notes.example.org:8443"
    },
    {
      "input": "http://127.0.0.1:8080/admin",
      "expected": "127.0.0.1:8080 displayed; no connection"
    }
  ],
  "permitted_changes": [
    "Keep the operation free of implicit fetch/navigation and render origin text literally."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not add background health checks or reject local bookmarks as though displaying one performs SSRF."
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
    "https://docs.rs/url/latest/url/struct.Url.html"
  ]
}
```

### Regression traps

```json
[
  "Do not add background health checks or reject local bookmarks as though displaying one performs SSRF."
]
```

### Remediation constraints

```json
[
  "Display the parsed origin of a user bookmark without contacting it.",
  "Keep the operation free of implicit fetch/navigation and render origin text literally.",
  "Do not add background health checks or reject local bookmarks as though displaying one performs SSRF."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-rust-safe-03",
  "prior_case_id": "rust-shell-maintenance-safe",
  "prior_source_sha256": "30d8b25e83cab522264ff9e04db69a29f5692c3c1137350b37ddeb9554557624",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Rust1.83, edition2021; Linux amd64",
  "libraries_platform_setup": "url2.5.4; the bookmark panel renders returned strings as text and performs no network I/O, DNS resolution, automatic navigation or filesystem access. Internal/loopback bookmarks are intentionally allowed as display data."
}
```

### Split

```json
"held_out"
```

## v2-rust-safe-04 — pdf-metadata-direct-process

Proposed label: **safe**. Human review: **pending**.

Source hash: `6294b4fe21ab185dc24696fb99ee09af8bed19db022a811fc55501b800b74575`. Protocol-2.0 case hash: `c3bbfaee18ce879eff72a52a9a6f4bb27abc9c7af67e2afca820503224f22234`.

Command uses a fixed binary and one literal argument, with no shell. Absolute server-assigned paths cannot be mistaken for a leading option. Returning Output preserves error evidence.

### pdf_metadata.rs

```rust
use std::io;
use std::path::Path;
use std::process::{Command, Output};
pub fn metadata(owned_pdf: &Path) -> io::Result<Output> {
    if !owned_pdf.is_absolute() { return Err(io::Error::new(io::ErrorKind::InvalidInput,"absolute owned path required")); }
    Command::new("/usr/bin/pdfinfo").arg(owned_pdf).env_clear().env("LC_ALL","C").output()
}
```

### Derivation

```json
{
  "group": "pdf-metadata-direct-process",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around collect metadata for an accepted owned pdf and preserve stdout/stderr/status. Boundary: The server-assigned absolute file path is one process argument, not shell source or an option. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
    "PDF implementation bugs are outside source ground truth; ingestion and process resource limits are deployment prerequisites."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Collect metadata for an accepted owned PDF and preserve stdout/stderr/status.",
  "trust_boundary": "The server-assigned absolute file path is one process argument, not shell source or an option.",
  "legitimate_examples": [
    {
      "input": "Owned path containing spaces",
      "expected": "Metadata for that one PDF"
    },
    {
      "input": "Owned path containing semicolon",
      "expected": "No extra command is executed"
    }
  ],
  "permitted_changes": [
    "Keep fixed executable, literal argv and full process result."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not invoke sh -c, drop stderr/status, or narrow accepted filenames by deleting spaces."
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
    "https://doc.rust-lang.org/std/process/struct.Command.html"
  ]
}
```

### Regression traps

```json
[
  "Do not invoke sh -c, drop stderr/status, or narrow accepted filenames by deleting spaces."
]
```

### Remediation constraints

```json
[
  "Collect metadata for an accepted owned PDF and preserve stdout/stderr/status.",
  "Keep fixed executable, literal argv and full process result.",
  "Do not invoke sh -c, drop stderr/status, or narrow accepted filenames by deleting spaces."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-rust-safe-04",
  "prior_case_id": "rust-sqlite-update-safe",
  "prior_source_sha256": "cecd64722fe2d3c7ba33483edf65efecde67a2a1a08c8e9dab37082e20645d8d",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Rust1.83, edition2021; Linux amd64",
  "libraries_platform_setup": "Poppler24.02 pdfinfo; ingestion assigns an absolute path inside a private directory and has bounded/prevalidated the PDF. Caller cannot choose an arbitrary host file. Executable and file are immutable for the operation."
}
```

### Split

```json
"held_out"
```

## v2-rust-safe-05 — typed-json-device-screen-config

Proposed label: **safe**. Human review: **pending**.

Source hash: `773f5b66c39b021b1e743f0bd83f180cb8fb7a35c669ebedab156308c7b34e7f`. Protocol-2.0 case hash: `45b4f586d6f55f4dd42ac6f1d4c2a40818ebe5dbdc4325fadaede7afc4c94861`.

Serde decodes a fixed data model; no dynamic object activation is present. Unknown fields and out-of-range dimensions are rejected, preserving a data-only import.

### screen.rs

```rust
use serde::Deserialize;
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Screen { pub title:String, pub columns:u8 }
pub fn import(bytes:&[u8]) -> Result<Screen,String> {
    if bytes.len()>4096 { return Err("config too large".into()); }
    let screen:Screen=serde_json::from_slice(bytes).map_err(|_| "invalid config")?;
    if screen.title.len()>100 || !(1..=4).contains(&screen.columns) { return Err("invalid screen layout".into()); }
    Ok(screen)
}
```

### Derivation

```json
{
  "group": "typed-json-device-screen-config",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around import a bounded device-screen layout into a fixed struct. Boundary: Network JSON is decoded into explicit scalar fields with no class/type dispatch. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
    "Template rendering uses plain text per consumer contract; parser depth and input limits are bounded by the stated small schema."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Import a bounded device-screen layout into a fixed struct.",
  "trust_boundary": "Network JSON is decoded into explicit scalar fields with no class/type dispatch.",
  "legitimate_examples": [
    {
      "input": "{title:Night shift,columns:2}",
      "expected": "Two-column Night shift model"
    },
    {
      "input": "Additional class or command field",
      "expected": "Rejected unknown field"
    }
  ],
  "permitted_changes": [
    "Keep the typed schema and layout bounds."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not turn title into an executable action or ignore validation on decode errors."
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
    "https://serde.rs/attributes.html",
    "https://docs.rs/serde_json/latest/serde_json/fn.from_slice.html"
  ]
}
```

### Regression traps

```json
[
  "Do not turn title into an executable action or ignore validation on decode errors."
]
```

### Remediation constraints

```json
[
  "Import a bounded device-screen layout into a fixed struct.",
  "Keep the typed schema and layout bounds.",
  "Do not turn title into an executable action or ignore validation on decode errors."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-rust-safe-05",
  "prior_case_id": "rust-hostname-acceptance-safe",
  "prior_source_sha256": "19b753ca36818bca14e2f8f64001bdbc2de2e54e9750ef2e4f3846846cc0815a",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Rust1.83, edition2021; Linux amd64",
  "libraries_platform_setup": "serde1.0.217 derive, serde_json1.0.138. Parsed configuration controls display text and column count only; title is rendered as text and does not select commands, classes or HTML."
}
```

### Split

```json
"held_out"
```

## v2-rust-safe-06 — immutable-build-record-sha256-address

Proposed label: **safe**. Human review: **pending**.

Source hash: `c0b894c944b272daab77fdad4160bd66cb89eafe8798386c3188c870633e08d4`. Protocol-2.0 case hash: `f277c08a54a9738e67742256b0c3684003931bb8d68a57b7b2299fd156cc514d`.

SHA-256 is appropriate for bounded content addressing, and the returned bytes are exactly those hashed. Predictability of a public digest is not an authentication weakness when it grants no access.

### build_record.rs

```rust
use sha2::{Digest,Sha256};
use std::fmt::Write;
pub struct Record { pub id:String, pub bytes:Vec<u8> }
pub fn identify(public_manifest:&[u8]) -> Result<Record,&'static str> {
    if public_manifest.len()>65536 { return Err("manifest too large"); }
    let digest=Sha256::digest(public_manifest);
    let mut id=String::with_capacity(64);
    for byte in digest { write!(&mut id,"{:02x}",byte).map_err(|_|"format failure")?; }
    Ok(Record{id,bytes:public_manifest.to_vec()})
}
```

### Derivation

```json
{
  "group": "immutable-build-record-sha256-address",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around create a full sha-256 content address paired with the exact public manifest bytes. Boundary: Untrusted manifest bytes affect a collision-resistant public identifier, not a bearer secret. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
    "The content address is not a signature; public-store authenticity is not claimed by this function."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Create a full SHA-256 content address paired with the exact public manifest bytes.",
  "trust_boundary": "Untrusted manifest bytes affect a collision-resistant public identifier, not a bearer secret.",
  "legitimate_examples": [
    {
      "input": "Same manifest twice",
      "expected": "Same64-hex ID and identical bytes"
    },
    {
      "input": "Manifest with changed byte",
      "expected": "Different content address except negligible collision probability"
    }
  ],
  "permitted_changes": [
    "Preserve full digest and exact-byte association."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not truncate identifiers into security tokens or canonicalize bytes after hashing."
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
    "https://docs.rs/sha2/latest/sha2/"
  ]
}
```

### Regression traps

```json
[
  "Do not truncate identifiers into security tokens or canonicalize bytes after hashing."
]
```

### Remediation constraints

```json
[
  "Create a full SHA-256 content address paired with the exact public manifest bytes.",
  "Preserve full digest and exact-byte association.",
  "Do not truncate identifiers into security tokens or canonicalize bytes after hashing."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-rust-safe-06",
  "prior_case_id": "rust-artifact-file-safe",
  "prior_source_sha256": "738190f95338fcbba24cbf2c7300990aef8658efc56703bea2c67e76a820c7cb",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Rust1.83, edition2021; Linux amd64",
  "libraries_platform_setup": "sha2 0.10.8; records are public immutable build manifests. A trusted append-only store uses the full digest as content address and compares stored bytes before treating duplicate IDs as the same record. No authentication/authorization decision relies on public IDs."
}
```

### Split

```json
"held_out"
```

## v2-rust-vulnerable-01 — offline-journal-rusqlite-batch-prune

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `5407ec56384a224a18f45c1f04bbaf61128a48c64ccfe6326da5f600a1a34e94`. Protocol-2.0 case hash: `ab1f850a220e934adc09f648ad690c693fd187661b436d512d7fcca84d2cda62`.

A second-order label reaches an API that executes SQL text, including multiple statements. User confirmation of cleanup does not authorize label-supplied SQL.

### prune.rs

```rust
use rusqlite::{Connection, Result};
pub fn prune_source(db: &Connection, imported_source: &str) -> Result<()> {
    let sql = format!("DELETE FROM journal_entries WHERE source = '{}';", imported_source);
    db.execute_batch(&sql)
}
pub fn confirm_cleanup(db: &Connection, selected_import_source: &str) -> Result<()> {
    if selected_import_source.len() > 100 { return Err(rusqlite::Error::InvalidParameterName("source too long".into())); }
    prune_source(db, selected_import_source)
}
```

### Derivation

```json
{
  "group": "offline-journal-rusqlite-batch-prune",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around prune entries from exactly the selected imported journal source. Boundary: A stored untrusted import label is interpolated into execute_batch at a later cleanup action. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "sql-injection",
    "cwe": "CWE-89",
    "path": "prune.rs"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "The database is local and trusted; importing arbitrary label text does not grant execution authority."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Prune entries from exactly the selected imported journal source.",
  "trust_boundary": "A stored untrusted import label is interpolated into execute_batch at a later cleanup action.",
  "legitimate_examples": [
    {
      "input": "source=travel-journal",
      "expected": "Delete only travel-journal entries"
    },
    {
      "input": "source=editor's notebook",
      "expected": "Exact apostrophe-containing source can be pruned"
    }
  ],
  "permitted_changes": [
    "Execute one prepared DELETE with a bound source parameter and retain failure reporting."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not clear the entire journal, reject all punctuation, or replace cleanup with a no-op."
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
    "https://docs.rs/rusqlite/latest/rusqlite/struct.Connection.html#method.execute_batch"
  ]
}
```

### Regression traps

```json
[
  "Do not clear the entire journal, reject all punctuation, or replace cleanup with a no-op."
]
```

### Remediation constraints

```json
[
  "Prune entries from exactly the selected imported journal source.",
  "Execute one prepared DELETE with a bound source parameter and retain failure reporting.",
  "Do not clear the entire journal, reject all punctuation, or replace cleanup with a no-op."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-rust-vulnerable-01",
  "prior_case_id": "rust-account-sqlx-vulnerable",
  "prior_source_sha256": "7c7e547c1c5b305305a60f47ca393910b1f3b24045dd82a9a7da02009a217acd",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Rust1.83, edition2021; Linux amd64",
  "libraries_platform_setup": "rusqlite0.32.1 with bundled SQLite; journal_entries(id,source,body) in a local app-owned database. Imported source labels are untrusted; user explicitly confirms pruning one source, not all journal entries."
}
```

### Split

```json
"held_out"
```

## v2-rust-vulnerable-02 — work-queue-sqlx-sort-expression

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `5c6dca6a9786169bbfee4b20c158dadd4a143e451c05c895c504377113ba1f38`. Protocol-2.0 case hash: `ed3e6f3db47722b4c49bade75473935cfe52b44a8ab3a33b985995c116fc6eb8`.

Binding owner does not protect the interpolated ORDER BY grammar. The user can supply arbitrary SQL expressions rather than one published sort key; prepared query execution does not parameterize that fragment.

### queue.rs

```rust
use sqlx::{PgPool, Row};
pub async fn page(pool: &PgPool, owner: i64, sort_from_query: &str) -> Result<Vec<i64>, sqlx::Error> {
    let sql = format!("SELECT id FROM tasks WHERE owner=$1 ORDER BY {}, id LIMIT 50", sort_from_query);
    let rows = sqlx::query(&sql).bind(owner).fetch_all(pool).await?;
    rows.into_iter().map(|row| row.try_get::<i64,_>("id")).collect()
}
```

### handler.rs

```rust
use sqlx::PgPool;
mod queue;
pub async fn list(pool: &PgPool, authenticated_owner: i64, sort: Option<&str>) -> Result<Vec<i64>, sqlx::Error> {
    queue::page(pool, authenticated_owner, sort.unwrap_or("created_at")).await
}
```

### Derivation

```json
{
  "group": "work-queue-sqlx-sort-expression",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around list an authenticated user work queue in one of two published orders. Boundary: Untrusted sort text becomes an SQL expression even though the owner value is bound correctly. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "sql-injection",
    "cwe": "CWE-89",
    "path": "queue.rs"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Multiple-statement execution is not assumed under the PostgreSQL extended protocol; arbitrary expressions within one statement are sufficient for the injection label."
  ]
}
```

### Operation contract

```json
{
  "purpose": "List an authenticated user work queue in one of two published orders.",
  "trust_boundary": "Untrusted sort text becomes an SQL expression even though the owner value is bound correctly.",
  "legitimate_examples": [
    {
      "input": "sort=priority",
      "expected": "At most50 task IDs ordered by priority then id"
    },
    {
      "input": "sort=created_at",
      "expected": "At most50 task IDs ordered by creation time then id"
    }
  ],
  "permitted_changes": [
    "Select trusted sort-expression literals from the two supported keys and include the documented id tie-break."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not bind a column name as a string constant, drop owner filtering, or return every user queue."
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
    "https://docs.rs/sqlx/latest/sqlx/fn.query.html"
  ]
}
```

### Regression traps

```json
[
  "Do not bind a column name as a string constant, drop owner filtering, or return every user queue."
]
```

### Remediation constraints

```json
[
  "List an authenticated user work queue in one of two published orders.",
  "Select trusted sort-expression literals from the two supported keys and include the documented id tie-break.",
  "Do not bind a column name as a string constant, drop owner filtering, or return every user queue."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-rust-vulnerable-02",
  "prior_case_id": "rust-reqwest-certificates-vulnerable",
  "prior_source_sha256": "959459b934ce0dd213bf15147ed92d8b65052baddf0967da8320c4283ef40f28",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Rust1.83, edition2021; Linux amd64",
  "libraries_platform_setup": "sqlx0.8.3 features postgres,runtime-tokio-rustls; Tokio1.42; PostgreSQL16 tasks(id bigint,owner bigint,created_at timestamptz,priority integer). Public API promises sort keys created_at or priority, ascending with stable id tie-break."
}
```

### Split

```json
"held_out"
```

## v2-rust-vulnerable-03 — update-channel-reqwest-invalid-certs

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `85c86a1f969dd835c260f4ac25125360075e309ee1a70dc36e558d824371d099`. Protocol-2.0 case hash: `027e000b562dc3afc48c0902d6be787a192e5b6f75564d33a176446fab6cb8eb`.

The builder disables chain validation on the actual client used by the channel consumer. Refusing redirects does not authenticate the initial TLS peer.

### channel.rs

```rust
use reqwest::blocking::Client;
use reqwest::redirect::Policy;
use std::time::Duration;
pub fn latest_version() -> Result<String, reqwest::Error> {
    let client = Client::builder()
        .danger_accept_invalid_certs(true)
        .redirect(Policy::none())
        .timeout(Duration::from_secs(4))
        .build()?;
    client.get("https://updates.example.org/channel/stable")
        .send()?.error_for_status()?.text()
}
pub fn displayed_update() -> Result<String, reqwest::Error> {
    Ok(format!("Available version: {}", latest_version()?.trim()))
}
```

### Derivation

```json
{
  "group": "update-channel-reqwest-invalid-certs",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around fetch an authenticated stable-channel version label for the update ui. Boundary: An on-path attacker can supply an arbitrary certificate and body to a client configured to accept invalid certificates. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "tls-validation",
    "cwe": "CWE-295",
    "path": "channel.rs"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Deployment bounds the channel body through its reverse proxy; this case labels transport authenticity rather than guaranteeing protection against malicious authenticated update servers."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Fetch an authenticated stable-channel version label for the update UI.",
  "trust_boundary": "An on-path attacker can supply an arbitrary certificate and body to a client configured to accept invalid certificates.",
  "legitimate_examples": [
    {
      "input": "Trusted channel returns2.4.0",
      "expected": "Available version: 2.4.0"
    },
    {
      "input": "Untrusted peer certificate",
      "expected": "Must fail after remediation"
    }
  ],
  "permitted_changes": [
    "Use normal validation or a correctly configured private root store without insecure fallback."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not fabricate a current version, silently ignore TLS failures, or switch to HTTP."
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
    "https://docs.rs/reqwest/latest/reqwest/struct.ClientBuilder.html"
  ]
}
```

### Regression traps

```json
[
  "Do not fabricate a current version, silently ignore TLS failures, or switch to HTTP."
]
```

### Remediation constraints

```json
[
  "Fetch an authenticated stable-channel version label for the update UI.",
  "Use normal validation or a correctly configured private root store without insecure fallback.",
  "Do not fabricate a current version, silently ignore TLS failures, or switch to HTTP."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-rust-vulnerable-03",
  "prior_case_id": "rust-shell-maintenance-vulnerable",
  "prior_source_sha256": "cb69f602244af353bc45fafa60134cfc3b3c916012623b1acc495798a58e47d7",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Rust1.83, edition2021; Linux amd64",
  "libraries_platform_setup": "reqwest0.12.12 features blocking,rustls-tls with default-features=false. The application trusts channel metadata to select an update offered to the user; no separate signature authenticates channel labels."
}
```

### Split

```json
"held_out"
```

## v2-rust-vulnerable-04 — billing-api-native-tls-hostname-bypass

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `0079526445ffbc1e2b3d459e3c48452bf86c2883cfec6af251383793ea76bf4c`. Protocol-2.0 case hash: `d5360e25b6878df4c1b7dd6c10e37e24d0252aa92013e07f819bf6e842d2d823`.

The native-TLS hostname bypass accepts another domain identity even when the certificate chain is valid. The protected asset is an outbound private body, not merely public fetched text.

### billing.rs

```rust
use reqwest::blocking::Client;
use std::time::Duration;
pub fn send_receipt(receipt: Vec<u8>) -> Result<u16, reqwest::Error> {
    let client = Client::builder()
        .danger_accept_invalid_hostnames(true)
        .redirect(reqwest::redirect::Policy::none())
        .timeout(Duration::from_secs(3))
        .build()?;
    let response = client.post("https://billing.example.org/receipts")
        .body(receipt).send()?;
    Ok(response.status().as_u16())
}
```

### Derivation

```json
{
  "group": "billing-api-native-tls-hostname-bypass",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around send a receipt only to the authenticated billing origin and return http status. Boundary: Chain validation remains active but the requested DNS identity is ignored before transmitting private receipt bytes. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "tls-validation",
    "cwe": "CWE-295",
    "path": "billing.rs"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Native-tls is explicitly selected because backend support affects reachability of this option; a generic rustls assumption would be insufficient."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Send a receipt only to the authenticated billing origin and return HTTP status.",
  "trust_boundary": "Chain validation remains active but the requested DNS identity is ignored before transmitting private receipt bytes.",
  "legitimate_examples": [
    {
      "input": "Trusted billing host returns201",
      "expected": 201
    },
    {
      "input": "CA-valid certificate for unrelated.example",
      "expected": "Must not receive receipt after remediation"
    }
  ],
  "permitted_changes": [
    "Restore hostname checks while preserving trusted CA validation and exact billing destination."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not suppress failures, remove receipt upload, or send the body before authenticating the host."
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
    "https://docs.rs/reqwest/latest/reqwest/struct.ClientBuilder.html#method.danger_accept_invalid_hostnames"
  ]
}
```

### Regression traps

```json
[
  "Do not suppress failures, remove receipt upload, or send the body before authenticating the host."
]
```

### Remediation constraints

```json
[
  "Send a receipt only to the authenticated billing origin and return HTTP status.",
  "Restore hostname checks while preserving trusted CA validation and exact billing destination.",
  "Do not suppress failures, remove receipt upload, or send the body before authenticating the host."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-rust-vulnerable-04",
  "prior_case_id": "rust-sqlite-update-vulnerable",
  "prior_source_sha256": "f84f88d5137c1d2b0d501e73fe3d003975e997ac2dffa8145b34d6cbcfc8fdde",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Rust1.83, edition2021; Linux amd64",
  "libraries_platform_setup": "reqwest0.12.12 features blocking,native-tls with default-features=false; OpenSSL-backed native-tls on Linux. Caller supplies an authorized bounded receipt containing private billing details. Network attacker owns a certificate valid for another hostname."
}
```

### Split

```json
"held_out"
```

## v2-rust-vulnerable-05 — document-count-shell-glob-selector

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `c0811739bcaa073a70884936157779be314d786d0824603494072214c401df50`. Protocol-2.0 case hash: `b997fd186a0ec622e0456b33da41acacc50bfadd341b76fa44b4115f4795991b`.

Length restriction does not stop a quote escaping the shell word. In addition, find wildcard semantics must not replace the declared literal-suffix contract during a repair.

### count.rs

```rust
use std::io;
use std::process::{Command, Output};
pub fn count_documents(extension: &str) -> io::Result<Output> {
    if extension.len() > 20 { return Err(io::Error::new(io::ErrorKind::InvalidInput,"extension too long")); }
    let command = format!("find /srv/public/docs -type f -name '*.{}' | wc -l", extension);
    Command::new("/bin/sh").arg("-c").arg(command).output()
}
```

### endpoint.rs

```rust
use std::io;
mod count;
pub fn count_for_form(extension: &str) -> io::Result<String> {
    let output = count::count_documents(extension)?;
    if !output.status.success() { return Err(io::Error::other("count failed")); }
    Ok(String::from_utf8_lossy(&output.stdout).trim().to_owned())
}
```

### Derivation

```json
{
  "group": "document-count-shell-glob-selector",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around count public documents whose filenames end in the selected literal suffix. Boundary: Form suffix is interpolated inside shell quotes, then interpreted by sh -c before find receives its pattern. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "shell-injection",
    "cwe": "CWE-78",
    "path": "count.rs"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "The trusted finite document tree constrains work. Command output status and literal suffix interpretation are behavior requirements beyond merely removing the shell."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Count public documents whose filenames end in the selected literal suffix.",
  "trust_boundary": "Form suffix is interpolated inside shell quotes, then interpreted by sh -c before find receives its pattern.",
  "legitimate_examples": [
    {
      "input": "extension=pdf",
      "expected": "Count .pdf files"
    },
    {
      "input": "extension=notes'old",
      "expected": "Count literal .notes'old suffix"
    }
  ],
  "permitted_changes": [
    "Use directory iteration with literal suffix matching, or a safely escaped direct find invocation and explicit pipe handling."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not count every file, replace the response with command text, or allow wildcard expansion to alter literal suffix meaning."
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
    "https://doc.rust-lang.org/std/process/struct.Command.html"
  ]
}
```

### Regression traps

```json
[
  "Do not count every file, replace the response with command text, or allow wildcard expansion to alter literal suffix meaning."
]
```

### Remediation constraints

```json
[
  "Count public documents whose filenames end in the selected literal suffix.",
  "Use directory iteration with literal suffix matching, or a safely escaped direct find invocation and explicit pipe handling.",
  "Do not count every file, replace the response with command text, or allow wildcard expansion to alter literal suffix meaning."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-rust-vulnerable-05",
  "prior_case_id": "rust-hostname-acceptance-vulnerable",
  "prior_source_sha256": "e63b9bfaa63f368118037c58a9ca5ce35d7bf375e0c9bc7602d777644713bcdc",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Rust1.83, edition2021; Linux amd64",
  "libraries_platform_setup": "Linux POSIX shell, GNU findutils/coreutils in trusted PATH. Public document tree is immutable and bounded. API accepts literal filename suffixes, including punctuation, not shell programs or arbitrary find expressions."
}
```

### Split

```json
"held_out"
```

## v2-rust-vulnerable-06 — support-export-world-readable-permissions

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `05e88b79161c0eaec4a7a1534f0cdc0c10702792b7e1eda5fda25a1952847746`. Protocol-2.0 case hash: `9b24bf6042e1892816eefa26d60b55a101616bc273970842b1bb0a9b8381929f`.

The final chmod defeats the restrictive create mode and exposes private contents to unrelated local users. The containing directory is explicitly traversable so this is reachable rather than masked by a0700 parent.

### export.rs

```rust
use std::fs::{self, OpenOptions, Permissions};
use std::io::{self, Write};
use std::os::unix::fs::{OpenOptionsExt, PermissionsExt};
use std::path::Path;
pub fn private_export(path: &Path, customer_csv: &[u8]) -> io::Result<()> {
    let mut file = OpenOptions::new().write(true).create_new(true).mode(0o600).open(path)?;
    file.write_all(customer_csv)?;
    file.sync_all()?;
    fs::set_permissions(path, Permissions::from_mode(0o666))?;
    Ok(())
}
```

### Derivation

```json
{
  "group": "support-export-world-readable-permissions",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around write a new private support export readable only by its service account. Boundary: After securely creating the file, the code grants read/write permissions to every local user. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "insecure-permissions",
    "cwe": "CWE-732",
    "path": "export.rs"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Path generation and parent ownership are trusted. Cross-user confidentiality/integrity, not a generic chmod occurrence, establishes the label."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Write a new private support export readable only by its service account.",
  "trust_boundary": "After securely creating the file, the code grants read/write permissions to every local user.",
  "legitimate_examples": [
    {
      "input": "New trusted export path",
      "expected": "CSV stored, readable by owner"
    },
    {
      "input": "Existing export path",
      "expected": "Creation fails without overwrite"
    }
  ],
  "permitted_changes": [
    "Keep owner-only permissions and avoid broadening them after creation; preserve exclusive creation and durable-write errors."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not make the parent world-writable, omit the CSV, or overwrite existing exports."
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
    "https://doc.rust-lang.org/std/os/unix/fs/trait.PermissionsExt.html"
  ]
}
```

### Regression traps

```json
[
  "Do not make the parent world-writable, omit the CSV, or overwrite existing exports."
]
```

### Remediation constraints

```json
[
  "Write a new private support export readable only by its service account.",
  "Keep owner-only permissions and avoid broadening them after creation; preserve exclusive creation and durable-write errors.",
  "Do not make the parent world-writable, omit the CSV, or overwrite existing exports."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-rust-vulnerable-06",
  "prior_case_id": "rust-artifact-file-vulnerable",
  "prior_source_sha256": "9b426afde88ac7d5af0bc4ca2085d9906a6dd874dd42331f6fde1558bf00b99a",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Rust1.83, edition2021; Linux amd64",
  "libraries_platform_setup": "Unix filesystem; path is server-generated beneath an application-owned directory with mode0755, traversable by other local users. Source CSV contains private customer records; intended reader is the service account only. No symlink/path attacker controls the destination."
}
```

### Split

```json
"held_out"
```

