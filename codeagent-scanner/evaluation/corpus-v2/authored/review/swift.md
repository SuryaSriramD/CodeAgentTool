# swift — authored corpus-v2 candidates

AI-authored, pending independent human review. Static validation is separate evidence, not approval. Source is quoted for inspection and must not be executed.

Review the corpus-level context and checklist in the [complete unsigned manifest](../unsigned-review-manifest.json) alongside each case.

## v2-swift-safe-01 — secure-note-title-keyed-decoding

Proposed label: **safe**. Human review: **pending**.

Source hash: `c219d079e9690e34abfc08ec74f134c93eba438a1254721cfc9ad0bac9436cdf`. Protocol-2.0 case hash: `ea3c349852bbaa32e75903208daaf8f5427e1e87961ee649fabdea04d4dff270`.

The allowed class is supplied to secure decoding before construction, and the returned value has a bounded length. There is no general decoder followed only by a cast.

### NoteTitle.swift

```swift
import Foundation
struct NoteTitle {
    enum DecodeError: Error { case tooLarge, invalid }
    static func read(_ attachment: Data) throws -> String {
        guard attachment.count <= 8192 else { throw DecodeError.tooLarge }
        guard let value = try NSKeyedUnarchiver.unarchivedObject(ofClass: NSString.self, from: attachment),
              value.length <= 200 else { throw DecodeError.invalid }
        return value as String
    }
}
```

### Derivation

```json
{
  "group": "secure-note-title-keyed-decoding",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around decode one bounded note title from a class-constrained archive. Boundary: Untrusted bytes may select only the explicitly permitted secure string class. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
    "The allowed string object is inert; malformed archive failure is propagated to the import UI."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Decode one bounded note title from a class-constrained archive.",
  "trust_boundary": "Untrusted bytes may select only the explicitly permitted secure string class.",
  "legitimate_examples": [
    {
      "input": "Secure archive of Meeting notes",
      "expected": "Meeting notes"
    },
    {
      "input": "Archive rooted in an unrelated class",
      "expected": "Rejected"
    }
  ],
  "permitted_changes": [
    "Retain pre-decode class restriction and format-specific length limits."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not add NSObject or arbitrary classes to the allowed set to silence errors."
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
    "https://developer.apple.com/documentation/foundation/nskeyedunarchiver/unarchivedobject(ofclass:from:)"
  ]
}
```

### Regression traps

```json
[
  "Do not add NSObject or arbitrary classes to the allowed set to silence errors."
]
```

### Remediation constraints

```json
[
  "Decode one bounded note title from a class-constrained archive.",
  "Retain pre-decode class restriction and format-specific length limits.",
  "Do not add NSObject or arbitrary classes to the allowed set to silence errors."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-swift-safe-01",
  "prior_case_id": "swift-server-trust-policy-safe",
  "prior_source_sha256": "b82d1ab8e892dcfc74c28c307a3b08af1dd9e4d6e9e3054ac12be08ae53b09a1",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Swift 5.9 language mode; macOS14 Foundation and Security frameworks",
  "libraries_platform_setup": "Title files are keyed archives containing a single NSString, generated using requiringSecureCoding=true; other graph shapes were never part of the format. Foundation NSString conforms to NSSecureCoding."
}
```

### Split

```json
"held_out"
```

## v2-swift-safe-02 — typed-shortcut-property-list

Proposed label: **safe**. Human review: **pending**.

Source hash: `8987d3b89d17f8f4df38bbacf1462a3eeb360cfe9bc7b8eee016612d72fee58b`. Protocol-2.0 case hash: `1570a17389d650d079c27c31c534d21a092c7622bb9f4b56baf405361f1a324c`.

PropertyListDecoder targets a fixed data model and validates bounded fields. Serialized input by itself does not imply unsafe object deserialization.

### ShortcutPreferences.swift

```swift
import Foundation
struct ShortcutPreferences: Decodable {
    let title: String
    let repeatCount: Int
}
struct ShortcutImport {
    enum ImportError: Error { case invalid }
    static func load(_ data: Data) throws -> ShortcutPreferences {
        guard data.count <= 4096 else { throw ImportError.invalid }
        let value = try PropertyListDecoder().decode(ShortcutPreferences.self, from: data)
        guard value.title.count <= 80, (1...5).contains(value.repeatCount) else { throw ImportError.invalid }
        return value
    }
}
```

### Derivation

```json
{
  "group": "typed-shortcut-property-list",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around import display-only repeated-title preferences from a typed property list. Boundary: Untrusted plist fields populate a fixed Decodable struct without runtime class activation. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
    "The document is presentation data; no arbitrary URL, filesystem path or privileged action is derived from it."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Import display-only repeated-title preferences from a typed property list.",
  "trust_boundary": "Untrusted plist fields populate a fixed Decodable struct without runtime class activation.",
  "legitimate_examples": [
    {
      "input": "title=Hello, repeatCount=2",
      "expected": "Model for two Hello displays"
    },
    {
      "input": "repeatCount=1000000",
      "expected": "Rejected"
    }
  ],
  "permitted_changes": [
    "Retain typed decoding and value bounds."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not infer executable classes/commands from title or accept unbounded repeat counts."
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
    "https://developer.apple.com/documentation/foundation/propertylistdecoder"
  ]
}
```

### Regression traps

```json
[
  "Do not infer executable classes/commands from title or accept unbounded repeat counts."
]
```

### Remediation constraints

```json
[
  "Import display-only repeated-title preferences from a typed property list.",
  "Retain typed decoding and value bounds.",
  "Do not infer executable classes/commands from title or accept unbounded repeat counts."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-swift-safe-02",
  "prior_case_id": "swift-archive-import-safe",
  "prior_source_sha256": "deb807259279d429bb057e5f9f98ac40ead6ce8c30f202ab54515a4027d31432",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Swift 5.9 language mode; macOS14 Foundation and Security frameworks",
  "libraries_platform_setup": "XML or binary plist accepted; the typed model contains only String and Int. Import consumer displays title repeatCount times, with text rendering, and never executes named shortcuts or shell commands."
}
```

### Split

```json
"held_out"
```

## v2-swift-safe-03 — literal-document-search-regex-escaping

Proposed label: **safe**. Human review: **pending**.

Source hash: `a5f0ceacffd08816c5f74a6d7db70e7c9dfe375859b2d3f7e680697ab441d6bc`. Protocol-2.0 case hash: `fa1b249096a30bfd1e761288b56ec95ef5e649f9aabdfcbdffd46f38f0ff1166`.

Escaping converts regex metacharacters to literal data, and input bounds constrain the search. Unicode range conversion uses Foundation string indexing rather than byte offsets.

### DocumentSearch.swift

```swift
import Foundation
struct DocumentSearch {
    enum SearchError: Error { case tooLarge }
    static func first(needle: String, in document: String) throws -> NSRange? {
        guard needle.utf8.count <= 80, document.utf8.count <= 65536 else { throw SearchError.tooLarge }
        if needle.isEmpty { return nil }
        let literal = NSRegularExpression.escapedPattern(for: needle)
        let expression = try NSRegularExpression(pattern: literal)
        let whole = NSRange(document.startIndex..<document.endIndex, in: document)
        return expression.firstMatch(in: document, range: whole)?.range
    }
}
```

### SearchSelection.swift

```swift
import Foundation
struct SearchSelection {
    static func highlight(query: String, loadedText: String) throws -> NSRange? {
        try DocumentSearch.first(needle: query, in: loadedText)
    }
}
```

### Derivation

```json
{
  "group": "literal-document-search-regex-escaping",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around find the first exact literal phrase in a bounded document for highlighting. Boundary: User text is escaped before it becomes regular-expression syntax; no raw regex is accepted. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
    "General regex denial-of-service is not inferred from a fixed escaped literal; empty query intentionally yields no highlight."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Find the first exact literal phrase in a bounded document for highlighting.",
  "trust_boundary": "User text is escaped before it becomes regular-expression syntax; no raw regex is accepted.",
  "legitimate_examples": [
    {
      "input": "needle=a.*b, document=try a.*b now",
      "expected": "Highlights literal a.*b"
    },
    {
      "input": "needle=🍎, document=x🍎y",
      "expected": "Correct UTF-16 range for the emoji"
    }
  ],
  "permitted_changes": [
    "Retain literal escaping, bounded lengths and UTF-16-compatible result ranges."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not enable user regexes, remove punctuation from the phrase, or compute ranges from UTF-8 bytes."
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
    "https://developer.apple.com/documentation/foundation/nsregularexpression/escapedpattern(for:)"
  ]
}
```

### Regression traps

```json
[
  "Do not enable user regexes, remove punctuation from the phrase, or compute ranges from UTF-8 bytes."
]
```

### Remediation constraints

```json
[
  "Find the first exact literal phrase in a bounded document for highlighting.",
  "Retain literal escaping, bounded lengths and UTF-16-compatible result ranges.",
  "Do not enable user regexes, remove punctuation from the phrase, or compute ranges from UTF-8 bytes."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-swift-safe-03",
  "prior_case_id": "swift-session-challenge-safe",
  "prior_source_sha256": "ee7c86704a9bcc3560ffd8d41df2e5becd9f8cd43199fc599e44580519da2876",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Swift 5.9 language mode; macOS14 Foundation and Security frameworks",
  "libraries_platform_setup": "Foundation ICU regular-expression engine; output range is consumed by a text view using UTF-16 NSRange. Both search string and document are plain text, not patterns or executable templates."
}
```

### Split

```json
"held_out"
```

## v2-swift-safe-04 — public-calendar-default-urlsession

Proposed label: **safe**. Human review: **pending**.

Source hash: `b5e113d4544cc5dae2cc12780ef7fc8c8ee480a2d981be7537645f2564132a5a`. Protocol-2.0 case hash: `58990a7d2834bd0db74986d06da4cad64251b2a86137cab2779fd0dc780ff59a`.

No certificate/hostname checks are disabled, and the fixed URL carries no secrets. Final origin and size are validated before data is used.

### HolidayCalendar.swift

```swift
import Foundation
struct HolidayCalendar {
    enum CalendarError: Error { case response }
    static func fetch() async throws -> Data {
        let configuration = URLSessionConfiguration.ephemeral
        configuration.timeoutIntervalForRequest = 4
        let session = URLSession(configuration: configuration)
        defer { session.invalidateAndCancel() }
        let url = URL(string: "https://calendar.example.org/holidays.json")!
        let (data, response) = try await session.data(from: url)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200,
              response.url?.scheme == "https", response.url?.host == "calendar.example.org",
              data.count <= 65536 else { throw CalendarError.response }
        return data
    }
}
```

### Derivation

```json
{
  "group": "public-calendar-default-urlsession",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around download a bounded public holiday calendar over default platform-authenticated https. Boundary: Network response is untrusted until URLSession certificate checks and response validation complete. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
    "The public endpoint and system trust store are deployment assumptions. Redirect requests carry no credentials and do not represent arbitrary user-directed SSRF."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Download a bounded public holiday calendar over default platform-authenticated HTTPS.",
  "trust_boundary": "Network response is untrusted until URLSession certificate checks and response validation complete.",
  "legitimate_examples": [
    {
      "input": "200 JSON from calendar host",
      "expected": "Returns bytes"
    },
    {
      "input": "Bad certificate or final different host",
      "expected": "Throws"
    }
  ],
  "permitted_changes": [
    "Preserve platform authentication and validate successful response metadata."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not add permissive challenge handling or return failed-response bytes as a calendar."
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
    "https://developer.apple.com/documentation/foundation/urlsession"
  ]
}
```

### Regression traps

```json
[
  "Do not add permissive challenge handling or return failed-response bytes as a calendar."
]
```

### Remediation constraints

```json
[
  "Download a bounded public holiday calendar over default platform-authenticated HTTPS.",
  "Preserve platform authentication and validate successful response metadata.",
  "Do not add permissive challenge handling or return failed-response bytes as a calendar."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-swift-safe-04",
  "prior_case_id": "swift-archive-file-safe",
  "prior_source_sha256": "73fdbd2c7e66b586f77d636073c86107f426fe098816bba4055ab6819ae123ca",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Swift 5.9 language mode; macOS14 Foundation and Security frameworks",
  "libraries_platform_setup": "Default ATS enabled with no exceptions, no custom trust delegate or global protocol overrides. Endpoint is public and operator-controlled; authenticated HTTPS redirects only within the same final host are accepted. No credentials are sent."
}
```

### Split

```json
"held_out"
```

## v2-swift-safe-05 — filesystem-image-literal-name-stat

Proposed label: **safe**. Human review: **pending**.

Source hash: `520006b774e94b50ca7fcf649f33630676e427dcd1f8d89fa3a9f69acb6580c0`. Protocol-2.0 case hash: `a95344d5971156058b7f3c74795c0dd9ae3d5bd477fd7367e52d11f3e396d23f`.

An arbitrary user-authorized filesystem selection is the intended desktop operation. A pathname alone does not establish traversal, and FileManager does not interpret shell punctuation.

### ImageMetadata.swift

```swift
import Foundation
struct ImageMetadata {
    static func byteCount(of selectedFile: URL) throws -> UInt64 {
        guard selectedFile.isFileURL else { throw CocoaError(.fileReadUnsupportedScheme) }
        let attributes = try FileManager.default.attributesOfItem(atPath: selectedFile.path)
        guard let size = attributes[.size] as? NSNumber else { throw CocoaError(.fileReadUnknown) }
        return size.uint64Value
    }
}
```

### OpenPanelAction.swift

```swift
import Foundation
struct OpenPanelAction {
    func inspect(userSelectedAuthorizedURL: URL) throws -> String {
        "Size: \(try ImageMetadata.byteCount(of: userSelectedAuthorizedURL)) bytes"
    }
}
```

### Derivation

```json
{
  "group": "filesystem-image-literal-name-stat",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around display byte size of a user-selected authorized local file. Boundary: A selected filename is passed to a filesystem metadata API, never to a shell or app-root traversal boundary. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
    "The selection/entitlement boundary is trusted UI infrastructure; attacker access to unrelated files is not granted by this function."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Display byte size of a user-selected authorized local file.",
  "trust_boundary": "A selected filename is passed to a filesystem metadata API, never to a shell or app-root traversal boundary.",
  "legitimate_examples": [
    {
      "input": "Selected filename --help.png",
      "expected": "Its actual byte count"
    },
    {
      "input": "Selected filename photo;notes.jpg",
      "expected": "Its actual byte count"
    }
  ],
  "permitted_changes": [
    "Retain the explicit file-URL check and user-selected sandbox authorization."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not narrow legitimate selections to invented resource IDs or invoke shell stat with interpolation."
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
    "https://developer.apple.com/documentation/foundation/filemanager/attributesofitem(atpath:)"
  ]
}
```

### Regression traps

```json
[
  "Do not narrow legitimate selections to invented resource IDs or invoke shell stat with interpolation."
]
```

### Remediation constraints

```json
[
  "Display byte size of a user-selected authorized local file.",
  "Retain the explicit file-URL check and user-selected sandbox authorization.",
  "Do not narrow legitimate selections to invented resource IDs or invoke shell stat with interpolation."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-swift-safe-05",
  "prior_case_id": "swift-format-log-safe",
  "prior_source_sha256": "a49f04dacabe3dbda9281d18d46b33ab364cebd0ba001cff46a121561352557d",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Swift 5.9 language mode; macOS14 Foundation and Security frameworks",
  "libraries_platform_setup": "User explicitly selects a file through the macOS open panel; sandbox grants access to that selected URL only. Operation intentionally accepts any user-authorized local filename, including spaces and leading dashes."
}
```

### Split

```json
"held_out"
```

## v2-swift-safe-06 — preferences-sqlite-bound-update

Proposed label: **safe**. Human review: **pending**.

Source hash: `8be60124ee9096b6ba5ab764e0ce54a4278647aca48bf0ac9defe1fee6d32857`. Protocol-2.0 case hash: `98ae057b1dbd4372c27b4119a6c8170233ee9ac3c9d09e63903a171c5b5d56bc`.

The prepared UPDATE binds a copied string value with correct lifetime, handles errors and finalizes the statement. A misleading unsafeBitCast is the documented SQLITE_TRANSIENT sentinel conversion rather than input-derived pointer arithmetic.

### ColorPreference.swift

```swift
import Foundation
import SQLite3
struct ColorPreference {
    enum DBError: Error { case failure }
    static func save(label: String, database: OpaquePointer) throws {
        guard label.utf8.count <= 80 else { throw DBError.failure }
        var statement: OpaquePointer?
        guard sqlite3_prepare_v2(database, "UPDATE preferences SET color_label=?1 WHERE id=1", -1, &statement, nil) == SQLITE_OK else {
            throw DBError.failure
        }
        defer { sqlite3_finalize(statement) }
        let transient = unsafeBitCast(-1, to: sqlite3_destructor_type.self)
        let bound = label.withCString { sqlite3_bind_text(statement, 1, $0, -1, transient) }
        guard bound == SQLITE_OK, sqlite3_step(statement) == SQLITE_DONE else { throw DBError.failure }
    }
}
```

### Derivation

```json
{
  "group": "preferences-sqlite-bound-update",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around save the exact user color label into one fixed preferences row. Boundary: Untrusted label is bound after statement preparation and never contributes to SQL syntax. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
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
    "Embedded NUL is excluded by the stated input contract; the case tests binding and lifetime rather than silent C-string truncation."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Save the exact user color label into one fixed preferences row.",
  "trust_boundary": "Untrusted label is bound after statement preparation and never contributes to SQL syntax.",
  "legitimate_examples": [
    {
      "input": "label=artist's blue",
      "expected": "Exact label saved"
    },
    {
      "input": "label=red; DELETE",
      "expected": "Punctuation remains label data"
    }
  ],
  "permitted_changes": [
    "Retain prepared binding and correct SQLite buffer ownership."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not remove apostrophes, expand the UPDATE to every row, or replace SQLITE_TRANSIENT with an invalid buffer lifetime."
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
    "https://www.sqlite.org/c3ref/bind_blob.html"
  ]
}
```

### Regression traps

```json
[
  "Do not remove apostrophes, expand the UPDATE to every row, or replace SQLITE_TRANSIENT with an invalid buffer lifetime."
]
```

### Remediation constraints

```json
[
  "Save the exact user color label into one fixed preferences row.",
  "Retain prepared binding and correct SQLite buffer ownership.",
  "Do not remove apostrophes, expand the UPDATE to every row, or replace SQLITE_TRANSIENT with an invalid buffer lifetime."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-swift-safe-06",
  "prior_case_id": "swift-path-selection-safe",
  "prior_source_sha256": "aaffdd4b669528e5cbc72461b6252fce62f91e2ba2cc5cb2c86ccf47822f6e5a",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Swift 5.9 language mode; macOS14 Foundation and Security frameworks",
  "libraries_platform_setup": "SQLite3.45; one app-owned preferences row id1 exists. UI labels disallow embedded NUL before this API and contain arbitrary other Unicode. SQLITE_TRANSIENT makes SQLite copy temporary UTF-8 buffer data."
}
```

### Split

```json
"held_out"
```

## v2-swift-vulnerable-01 — desktop-license-session-trust-override

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `51e009c5ae43785ee21eb6dadd4394d35ebb682a40bc53c7f9fcb7fbae05cb78`. Protocol-2.0 case hash: `fce10ad23944ff543cf2bdad685264f3b5fd5c51f1a10793b754f7d42f662609`.

The application both relaxes ATS and returns a trust credential without evaluating the peer. Fixed URL selection does not authenticate its TLS responder.

### LicenseService.swift

```swift
import Foundation
import Security
final class LicenseService: NSObject, URLSessionDelegate {
    private lazy var session = URLSession(configuration: .ephemeral, delegate: self, delegateQueue: nil)
    func licensed() async throws -> Bool {
        let url = URL(string: "https://license.example.org/desktop/status")!
        let (data, _) = try await session.data(from: url)
        return data == Data("licensed".utf8)
    }
    func urlSession(_ session: URLSession, didReceive challenge: URLAuthenticationChallenge,
                    completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
        if challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust,
           let trust = challenge.protectionSpace.serverTrust {
            completionHandler(.useCredential, URLCredential(trust: trust))
        } else { completionHandler(.performDefaultHandling, nil) }
    }
}
```

### Info.plist

```swift
<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0"><dict>
<key>NSAppTransportSecurity</key><dict><key>NSAllowsArbitraryLoads</key><true/></dict>
</dict></plist>
```

### Derivation

```json
{
  "group": "desktop-license-session-trust-override",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around authenticate the licensing service before using its licensed response to unlock desktop features. Boundary: The network response controls a licensing decision while every server trust challenge is accepted. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "tls-validation",
    "cwe": "CWE-295",
    "path": "LicenseService.swift"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "License protocol freshness and offline grace policy are separately controlled; the candidate isolates reachable transport authentication."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Authenticate the licensing service before using its licensed response to unlock desktop features.",
  "trust_boundary": "The network response controls a licensing decision while every server trust challenge is accepted.",
  "legitimate_examples": [
    {
      "input": "Authenticated service sends licensed",
      "expected": true
    },
    {
      "input": "Authenticated service sends expired",
      "expected": false
    }
  ],
  "permitted_changes": [
    "Restore platform trust/hostname evaluation and remove unnecessary ATS exceptions without eliminating the license request."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not always return licensed, silently allow TLS errors, or replace network status with a local constant."
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
    "https://developer.apple.com/library/archive/documentation/NetworkingInternet/Conceptual/NetworkingTopics/Articles/OverridingSSLChainValidationCorrectly.html"
  ]
}
```

### Regression traps

```json
[
  "Do not always return licensed, silently allow TLS errors, or replace network status with a local constant."
]
```

### Remediation constraints

```json
[
  "Authenticate the licensing service before using its licensed response to unlock desktop features.",
  "Restore platform trust/hostname evaluation and remove unnecessary ATS exceptions without eliminating the license request.",
  "Do not always return licensed, silently allow TLS errors, or replace network status with a local constant."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-swift-vulnerable-01",
  "prior_case_id": "swift-server-trust-policy-vulnerable",
  "prior_source_sha256": "b887375addf8c4931fce9639431b446c7f302b4d3b50131ae5f2dba19ba88c2c",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Swift 5.9 language mode; macOS14 Foundation and Security frameworks",
  "libraries_platform_setup": "Application bundle includes the supplied ATS exception. Developer mode is disabled; the shown delegate is used in production. An active network attacker can present an untrusted certificate matching the fixed hostname."
}
```

### Split

```json
"held_out"
```

## v2-swift-vulnerable-02 — mobile-support-alamofire-upload-trust

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `5b3418a32393ab21714e601cdaa3af4ce99299392ab27be0482cb2d2f628b001`. Protocol-2.0 case hash: `0bdb6988acbcd9cebd461b980881a503f7ae00a11e7f5a0c1db1125c10e62e99`.

DisabledTrustEvaluator removes server authentication on the exact production host used by Session.upload. HTTP status validation occurs after the private body has crossed the untrusted connection.

### SupportUpload.swift

```swift
import Foundation
import Alamofire
final class SupportUpload {
    private let session: Session
    init() {
        let manager = ServerTrustManager(evaluators: ["support.example.org": DisabledTrustEvaluator()])
        session = Session(serverTrustManager: manager)
    }
    func send(redactedLog: Data, completion: @escaping (Bool) -> Void) {
        session.upload(redactedLog, to: "https://support.example.org/logs", method: .post)
            .validate(statusCode: 200..<300)
            .response { result in completion(result.error == nil) }
    }
}
```

### Info.plist

```swift
<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0"><dict>
<key>NSAppTransportSecurity</key><dict><key>NSAllowsArbitraryLoads</key><true/></dict>
</dict></plist>
```

### Derivation

```json
{
  "group": "mobile-support-alamofire-upload-trust",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around upload private support diagnostics only to the authenticated support origin. Boundary: A network attacker can receive the uploaded body because trust evaluation for the production host is disabled. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "tls-validation",
    "cwe": "CWE-295",
    "path": "SupportUpload.swift"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Redaction does not make diagnostic content public. Request size is capped by the trusted diagnostic collector before this method."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Upload private support diagnostics only to the authenticated support origin.",
  "trust_boundary": "A network attacker can receive the uploaded body because trust evaluation for the production host is disabled.",
  "legitimate_examples": [
    {
      "input": "Successful trusted upload",
      "expected": "Completion true"
    },
    {
      "input": "Rejected HTTP response",
      "expected": "Completion false"
    }
  ],
  "permitted_changes": [
    "Use default or correctly pinned trust evaluation for the support domain."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not replace the upload with a success callback, leak logs to a fallback HTTP endpoint, or suppress transport errors."
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
    "https://alamofire.github.io/Alamofire/Classes/DisabledTrustEvaluator.html"
  ]
}
```

### Regression traps

```json
[
  "Do not replace the upload with a success callback, leak logs to a fallback HTTP endpoint, or suppress transport errors."
]
```

### Remediation constraints

```json
[
  "Upload private support diagnostics only to the authenticated support origin.",
  "Use default or correctly pinned trust evaluation for the support domain.",
  "Do not replace the upload with a success callback, leak logs to a fallback HTTP endpoint, or suppress transport errors."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-swift-vulnerable-02",
  "prior_case_id": "swift-archive-import-vulnerable",
  "prior_source_sha256": "1116ee7d141614c17ec58c9e6181e23360d8e99f22c348e7380b948459453c9d",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Swift 5.9 language mode; macOS14 Foundation and Security frameworks",
  "libraries_platform_setup": "Alamofire5.9.1; supplied ATS exception is active. Logs are redacted of credentials but contain private user diagnostics. Uploader instance remains alive until completion; URL is operator-controlled."
}
```

### Split

```json
"held_out"
```

## v2-swift-vulnerable-03 — shared-sketch-legacy-object-archive

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `48bb4b0d7f48d36f78823f73bd87df61bb3598a7e223a2113bca78e444001835`. Protocol-2.0 case hash: `083266e95bd274bacc90c43b6d7ff9b357bf47c43b427f88ff515ea4ce7f3899`.

An unrestricted unarchiver constructs the object graph before the shape check. A post-decode cast cannot prevent decoding an unintended NSCoding class; arbitrary-code execution is not presumed for every class.

### SketchImport.swift

```swift
import Foundation
struct SketchImport {
    static func labels(from sharedAttachment: Data) throws -> [String] {
        guard sharedAttachment.count <= 65536 else { throw ImportError.tooLarge }
        let object = try NSKeyedUnarchiver.unarchiveTopLevelObjectWithData(sharedAttachment)
        guard let labels = object as? [String], labels.count <= 20 else {
            throw ImportError.invalidShape
        }
        return labels
    }
    enum ImportError: Error { case tooLarge, invalidShape }
}
```

### SketchViewModel.swift

```swift
import Foundation
final class SketchViewModel {
    private(set) var labels: [String] = []
    func openSharedAttachment(_ data: Data) throws {
        labels = try SketchImport.labels(from: data)
    }
}
```

### Derivation

```json
{
  "group": "shared-sketch-legacy-object-archive",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around import up to20 text labels from a shared sketch attachment. Boundary: Archive class metadata is interpreted before an array-of-strings cast is performed. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "unsafe-deserialization",
    "cwe": "CWE-502",
    "path": "SketchImport.swift"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "The candidate concerns object activation; specific installed gadgets and their side effects require human runtime review rather than an invented exploit claim."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Import up to20 text labels from a shared sketch attachment.",
  "trust_boundary": "Archive class metadata is interpreted before an array-of-strings cast is performed.",
  "legitimate_examples": [
    {
      "input": "Legacy archive of [north, south]",
      "expected": [
        "north",
        "south"
      ]
    },
    {
      "input": "Legacy archive of Unicode labels",
      "expected": "Same Unicode strings in order"
    }
  ],
  "permitted_changes": [
    "Use secure class-constrained decoding of the documented array/string graph, preserving legacy supported label archives where safe."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not return archive bytes as text, accept arbitrary NSCoding classes, or clear every imported label."
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
    "https://developer.apple.com/videos/play/wwdc2020/10189/"
  ]
}
```

### Regression traps

```json
[
  "Do not return archive bytes as text, accept arbitrary NSCoding classes, or clear every imported label."
]
```

### Remediation constraints

```json
[
  "Import up to20 text labels from a shared sketch attachment.",
  "Use secure class-constrained decoding of the documented array/string graph, preserving legacy supported label archives where safe.",
  "Do not return archive bytes as text, accept arbitrary NSCoding classes, or clear every imported label."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-swift-vulnerable-03",
  "prior_case_id": "swift-session-challenge-vulnerable",
  "prior_source_sha256": "5bc6051eef49b0f389dd1764f47153c03de80bc97d6a618a68299f777410fb47",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Swift 5.9 language mode; macOS14 Foundation and Security frameworks",
  "libraries_platform_setup": "Legacy NSKeyedArchiver document format; desktop app links AppKit/Foundation NSCoding classes. Coworker attachments are untrusted even when their extension matches. Legacy APIs remain available in this runtime."
}
```

### Split

```json
"held_out"
```

## v2-swift-vulnerable-04 — local-receipt-tag-deletion-sql

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `a0662d70b57508f47c9dfdd44c3a20f2b7eb9574afaabda2e8554d69d4e494d0`. Protocol-2.0 case hash: `702cc222d7a4089de8aa02f9fbec8ca991a85d5ababd3179b90e9c4b010c70ae`.

String concatenation allows tag content to close the quoted predicate or add statements. The database handle is trusted, but imported labels are not SQL syntax.

### ReceiptTags.swift

```swift
import Foundation
import SQLite3
struct ReceiptTags {
    enum StoreError: Error { case sql(Int32) }
    static func removeTag(_ name: String, database: OpaquePointer) throws {
        guard name.utf8.count <= 100 else { throw StoreError.sql(SQLITE_TOOBIG) }
        let statement = "DELETE FROM receipt_tags WHERE tag = '" + name + "'"
        let result = sqlite3_exec(database, statement, nil, nil, nil)
        guard result == SQLITE_OK else { throw StoreError.sql(result) }
    }
}
```

### TagAction.swift

```swift
import Foundation
struct TagAction {
    let database: OpaquePointer
    func remove(importedTag: String) throws {
        try ReceiptTags.removeTag(importedTag, database: database)
    }
}
```

### Derivation

```json
{
  "group": "local-receipt-tag-deletion-sql",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around delete exactly the selected tag from local receipts. Boundary: Untrusted imported tag names become SQLite statement text, including multiple-statement execution through sqlite3_exec. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "sql-injection",
    "cwe": "CWE-89",
    "path": "ReceiptTags.swift"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "Database ownership is local; the attacker controls imported metadata and can influence a later legitimate removal action."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Delete exactly the selected tag from local receipts.",
  "trust_boundary": "Untrusted imported tag names become SQLite statement text, including multiple-statement execution through sqlite3_exec.",
  "legitimate_examples": [
    {
      "input": "tag=travel",
      "expected": "Only travel tag rows are deleted"
    },
    {
      "input": "tag=client's copy",
      "expected": "Apostrophe-containing tag can be removed"
    }
  ],
  "permitted_changes": [
    "Use a prepared DELETE with one bound text parameter and preserve error propagation."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not delete all tags, strip apostrophes from names, or silently ignore SQL errors."
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
    "https://www.sqlite.org/c3ref/exec.html"
  ]
}
```

### Regression traps

```json
[
  "Do not delete all tags, strip apostrophes from names, or silently ignore SQL errors."
]
```

### Remediation constraints

```json
[
  "Delete exactly the selected tag from local receipts.",
  "Use a prepared DELETE with one bound text parameter and preserve error propagation.",
  "Do not delete all tags, strip apostrophes from names, or silently ignore SQL errors."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-swift-vulnerable-04",
  "prior_case_id": "swift-archive-file-vulnerable",
  "prior_source_sha256": "cfd7701d00b4c85e87f1112e74c837e2fb5436ad125a79bf21dc872eeed9987e",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Swift 5.9 language mode; macOS14 Foundation and Security frameworks",
  "libraries_platform_setup": "SQLite3.45; open database handle is app-owned. receipt_tags(receipt_id INTEGER,tag TEXT) is populated by imported receipts. User may remove a selected imported tag, not unrelated receipts/tags."
}
```

### Split

```json
"held_out"
```

## v2-swift-vulnerable-05 — signed-design-manifest-md5-binding

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `0d908f8b3ed63c8b9d3aa7a69da51d6de3816b49884c50035eca3a16de788421`. Protocol-2.0 case hash: `e284cf2f4e4b615d2cde7d45e27b16b2afee42248fc02e3efdad831dacd34d7c`.

A collision-capable supplier can substitute a different file with the same MD5 after one file is approved. Authenticating the manifest does not repair a collision-weak content binding.

### DesignGate.swift

```swift
import Foundation
import CryptoKit
struct ApprovedDesign { let md5: String }
struct DesignGate {
    static func accept(download: Data, trustedEntry: ApprovedDesign) throws -> Data {
        guard download.count <= 1048576 else { throw GateError.size }
        let digest = Insecure.MD5.hash(data: download)
        let hex = digest.map { String(format: "%02x", $0) }.joined()
        guard hex == trustedEntry.md5 else { throw GateError.digest }
        return download
    }
    enum GateError: Error { case size, digest }
}
```

### DesignDisplay.swift

```swift
import Foundation
struct DesignDisplay {
    static func approvedBytes(untrustedDownload: Data, verifiedManifestEntry: ApprovedDesign) throws -> Data {
        try DesignGate.accept(download: untrustedDownload, trustedEntry: verifiedManifestEntry)
    }
}
```

### Derivation

```json
{
  "group": "signed-design-manifest-md5-binding",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around bind approved design artwork to the signed manifest before display. Boundary: Supplier-controlled artwork is identified by collision-broken MD5 in an otherwise authenticated manifest. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "weak-cryptography",
    "cwe": "CWE-328",
    "path": "DesignGate.swift"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "The threat requires supplier control before approval and a suitable colliding file pair; arbitrary second-preimage attacks are not claimed."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Bind approved design artwork to the signed manifest before display.",
  "trust_boundary": "Supplier-controlled artwork is identified by collision-broken MD5 in an otherwise authenticated manifest.",
  "legitimate_examples": [
    {
      "input": "Bytes of the approved artwork",
      "expected": "Returns identical approved bytes"
    },
    {
      "input": "Ordinary changed artwork",
      "expected": "Rejects mismatched digest"
    }
  ],
  "permitted_changes": [
    "Version the manifest to a collision-resistant content digest and migrate trust records through the approval workflow."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not remove digest checking, treat the unsigned download digest as authoritative, or silently accept all old/new algorithms."
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
    "https://developer.apple.com/documentation/cryptokit/insecure/md5"
  ]
}
```

### Regression traps

```json
[
  "Do not remove digest checking, treat the unsigned download digest as authoritative, or silently accept all old/new algorithms."
]
```

### Remediation constraints

```json
[
  "Bind approved design artwork to the signed manifest before display.",
  "Version the manifest to a collision-resistant content digest and migrate trust records through the approval workflow.",
  "Do not remove digest checking, treat the unsigned download digest as authoritative, or silently accept all old/new algorithms."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-swift-vulnerable-05",
  "prior_case_id": "swift-format-log-vulnerable",
  "prior_source_sha256": "760c322b7040f17d73c9043d579053df0fc21a9916e44c0c3ef2ba48cecad060",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Swift 5.9 language mode; macOS14 Foundation and Security frameworks",
  "libraries_platform_setup": "Manifest signature is verified upstream with a trusted key. A malicious supplier can choose a pair of colliding design files before submitting one for approval, then serve the other. Accepted bytes are displayed as approved regulatory artwork."
}
```

### Split

```json
"held_out"
```

## v2-swift-vulnerable-06 — report-renderer-manifest-executable-selection

Proposed label: **vulnerable**. Human review: **pending**.

Source hash: `08257e0b882bf0370cecb682515da7644782b2888314384f83ffd0843c600d9f`. Protocol-2.0 case hash: `3a9b20f922b769cae8c98cd3a928caa6eb3a237d590ad9c98f40b5609acc1958`.

This does not require a shell: parent components in the renderer ID can select an attacker-owned executable outside the trusted helper directory. Direct argv prevents shell expansion but does not authorize the executable itself.

### ReportRenderer.swift

```swift
import Foundation
struct ReportRenderer {
    enum RenderError: Error { case invalid }
    static func render(kindFromManifest: String, ownedInput: URL) throws -> Int32 {
        guard kindFromManifest.count <= 200 else { throw RenderError.invalid }
        let helperPath = "/Applications/Reports.app/Contents/Helpers/" + kindFromManifest
        let child = Process()
        child.executableURL = URL(fileURLWithPath: helperPath)
        child.arguments = [ownedInput.path]
        child.standardOutput = FileHandle.nullDevice
        child.standardError = FileHandle.nullDevice
        try child.run()
        child.waitUntilExit()
        return child.terminationStatus
    }
}
```

### ReportManifest.swift

```swift
import Foundation
struct ReportManifest: Decodable { let renderer: String }
struct ReportAction {
    static func generate(manifest: Data, serverOwnedInput: URL) throws -> Int32 {
        guard manifest.count <= 4096 else { throw ReportRenderer.RenderError.invalid }
        let value = try JSONDecoder().decode(ReportManifest.self, from: manifest)
        return try ReportRenderer.render(kindFromManifest: value.renderer, ownedInput: serverOwnedInput)
    }
}
```

### Derivation

```json
{
  "group": "report-renderer-manifest-executable-selection",
  "origin": "new AI-authored candidate",
  "related_case_ids": [],
  "independence_rationale": "Conceived around render an owned report using one of the two published helper ids and return its exit code. Boundary: A declarative manifest field selects an executable path with unchecked parent traversal, crossing into service-account code execution. No source was copied from development fixtures or corpus-v1; conceptual independence remains subject to cross-corpus human assessment."
}
```

### Expected findings

```json
[
  {
    "family": "command-injection",
    "cwe": "CWE-78",
    "path": "ReportRenderer.swift"
  }
]
```

### Ground truth scope

```json
{
  "profile": "security-v2",
  "scope": "Source security under the stated runtime and trust boundary; no dependency advisory ground truth is implied.",
  "reviewed_residual_risks": [
    "The attacker must have an executable reachable through the service filesystem; that prerequisite is explicit. Trusted input/report paths avoid conflating this with arbitrary document reads."
  ]
}
```

### Operation contract

```json
{
  "purpose": "Render an owned report using one of the two published helper IDs and return its exit code.",
  "trust_boundary": "A declarative manifest field selects an executable path with unchecked parent traversal, crossing into service-account code execution.",
  "legitimate_examples": [
    {
      "input": "renderer=pdf",
      "expected": "Run the bundled pdf helper with the owned input"
    },
    {
      "input": "renderer=svg",
      "expected": "Run the bundled svg helper with the owned input"
    }
  ],
  "permitted_changes": [
    "Map the two renderer IDs to fixed trusted executable URLs and reject all other IDs before launch."
  ],
  "forbidden_changes": [
    "Do not remove the operation, return a constant, or bypass its caller.",
    "Do not accept arbitrary executable paths, lose the selected output format, or claim argument separation alone secures executable selection."
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
    "https://developer.apple.com/documentation/foundation/process"
  ]
}
```

### Regression traps

```json
[
  "Do not accept arbitrary executable paths, lose the selected output format, or claim argument separation alone secures executable selection."
]
```

### Remediation constraints

```json
[
  "Render an owned report using one of the two published helper IDs and return its exit code.",
  "Map the two renderer IDs to fixed trusted executable URLs and reject all other IDs before launch.",
  "Do not accept arbitrary executable paths, lose the selected output format, or claim argument separation alone secures executable selection."
]
```

### Replacement trace

```json
{
  "register_version": "2.0.0-plan.1",
  "slot_id": "v2-swift-vulnerable-06",
  "prior_case_id": "swift-path-selection-vulnerable",
  "prior_source_sha256": "306292695447d73cccb2ac51fcf7bae873f30d1027859ea5929b60fed3b70aeb",
  "relationship": "replacement coverage slot; not a reference fix or source template"
}
```

### Runtime assumptions

```json
{
  "runtime": "Swift 5.9 language mode; macOS14 Foundation and Security frameworks",
  "libraries_platform_setup": "Non-sandboxed desktop rendering service. Two supported renderer IDs, pdf and svg, correspond to owned helper executables. An untrusted local theme author can submit a manifest and place an executable in its own filesystem area, but is not authorized to run code as the rendering service. Process accepts the resulting filesystem path without additional policy."
}
```

### Split

```json
"held_out"
```

